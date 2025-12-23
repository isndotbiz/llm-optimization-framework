"""
Enhanced OpenRouter Provider with Error Classification
Connect to OpenRouter API with intelligent error handling and fallback support
"""

import requests
import json
from typing import Dict, List, Optional, Any, Generator
from urllib.parse import urljoin
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .base_provider import LLMProvider, logger
from .provider_errors import (
    ProviderError, AuthenticationError, TimeoutError, RateLimitError,
    InvalidParameterError, ServerError, ConnectionError, classify_error
)


class OpenRouterProviderEnhanced(LLMProvider):
    """
    Enhanced Provider for OpenRouter API with error classification.

    OpenRouter provides unified access to:
    - OpenAI models (GPT-4, GPT-3.5, etc.)
    - Anthropic models (Claude)
    - Google models (PaLM, Gemini)
    - Meta models (Llama)
    - Many open-source models

    Supports:
    - Unified API for multiple providers
    - Model discovery from catalog
    - Streaming responses
    - Full parameter support
    - Cost tracking
    - Intelligent error classification for fallback chains
    """

    API_BASE = "https://openrouter.ai/api/v1/"

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize enhanced OpenRouter provider.

        Config keys:
            - api_key: OpenRouter API key (REQUIRED)
            - app_name: Your app name for tracking (optional)
            - app_url: Your app URL (optional)
            - timeout: Request timeout in seconds (default: 300)
        """
        super().__init__(config)

        self.api_key = config.get('api_key')
        if not self.api_key:
            raise InvalidParameterError("OpenRouter API key is required")

        self.app_name = config.get('app_name', 'AI-Router')
        self.app_url = config.get('app_url', 'https://github.com/yourusername/ai-router')
        self.timeout = config.get('timeout', 300)

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": self.app_url,
            "X-Title": self.app_name,
            "Content-Type": "application/json"
        }

        # Initialize session with connection pooling for better performance
        self.session = self._create_session()

        logger.info(f"OpenRouter enhanced provider initialized: app={self.app_name}")

    def _create_session(self) -> requests.Session:
        """
        Create a requests Session with connection pooling and retry strategy.

        This significantly improves performance by reusing TCP connections
        across multiple requests instead of creating a new connection per request.

        Returns:
            Configured requests.Session with pooling
        """
        session = requests.Session()

        # Configure retry strategy with exponential backoff
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
        )

        # Create HTTP adapter with connection pooling
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=10,
            pool_block=False
        )

        # Mount for both HTTP and HTTPS
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def list_models(self) -> List[Dict[str, Any]]:
        """
        List all available models from OpenRouter.

        Returns:
            List of model dictionaries with pricing info

        Raises:
            ProviderError: If API request fails
        """
        try:
            url = urljoin(self.API_BASE, 'models')
            response = self.session.get(
                url,
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()

            data = response.json()
            models = []

            for model in data.get('data', []):
                model_id = model.get('id', '')
                name = model.get('name', model_id)
                description = model.get('description', '')
                context_length = model.get('context_length', 4096)

                # Pricing info
                pricing = model.get('pricing', {})
                prompt_price = float(pricing.get('prompt', 0))
                completion_price = float(pricing.get('completion', 0))

                models.append({
                    "id": model_id,
                    "name": name,
                    "description": description,
                    "context_length": context_length,
                    "pricing": {
                        "prompt": prompt_price,
                        "completion": completion_price,
                        "unit": "per 1M tokens"
                    },
                    "top_provider": model.get('top_provider', {}),
                    "framework": "openrouter"
                })

            logger.info(f"Found {len(models)} OpenRouter models")
            return models

        except requests.exceptions.Timeout:
            raise TimeoutError("List models request timed out")
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(f"Failed to connect to OpenRouter: {str(e)}")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Invalid OpenRouter API key", 401)
            elif e.response.status_code == 429:
                raise RateLimitError("Rate limit exceeded", 429)
            elif e.response.status_code >= 500:
                raise ServerError(f"OpenRouter server error", e.response.status_code)
            raise ProviderError(f"HTTP error: {str(e)}")
        except requests.RequestException as e:
            raise ProviderError(f"Failed to list OpenRouter models: {str(e)}")

    def execute(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Execute model and return complete response.

        Args:
            model: Model identifier (e.g., 'openai/gpt-4', 'anthropic/claude-3-opus')
            prompt: User prompt
            system_prompt: Optional system prompt
            parameters: Model parameters

        Returns:
            Complete model response

        Raises:
            AuthenticationError: Invalid credentials
            TimeoutError: Request timed out
            RateLimitError: Rate limit exceeded
            ServerError: Provider server error
            InvalidParameterError: Invalid parameters
        """
        try:
            # Validate parameters
            self._validate_parameters(parameters)

            url = urljoin(self.API_BASE, 'chat/completions')

            # Build messages
            messages = self.format_messages(prompt, system_prompt)

            # Build request payload
            payload = {
                "model": model,
                "messages": messages
            }

            # Add parameters
            if parameters:
                params = self.normalize_parameters(parameters)
                payload.update(params)

            # Make request (uses connection pool from session)
            response = self.session.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()

            # Parse response
            data = response.json()
            content = data['choices'][0]['message']['content']

            # Log usage for cost tracking
            usage = data.get('usage', {})
            logger.info(f"OpenRouter usage - prompt: {usage.get('prompt_tokens', 0)}, "
                       f"completion: {usage.get('completion_tokens', 0)}")

            return content

        except requests.exceptions.Timeout:
            raise TimeoutError("Execute request timed out")
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(f"Failed to connect to OpenRouter: {str(e)}")
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if hasattr(e, 'response') else None
            if status_code == 401:
                raise AuthenticationError("Invalid or expired API key", 401)
            elif status_code == 403:
                raise AuthenticationError("Access forbidden", 403)
            elif status_code == 404:
                raise ProviderError(f"Model not found: {model}", 404)
            elif status_code == 429:
                raise RateLimitError("Rate limit exceeded", 429)
            elif status_code == 400:
                error_detail = str(e.response.text) if hasattr(e, 'response') else str(e)
                raise InvalidParameterError(f"Invalid request: {error_detail}", 400)
            elif status_code and status_code >= 500:
                raise ServerError(f"Server error: {str(e)}", status_code)
            raise ProviderError(f"HTTP error {status_code}: {str(e)}")
        except requests.RequestException as e:
            raise ProviderError(f"OpenRouter API request failed: {str(e)}")

    def stream_execute(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Generator[str, None, None]:
        """
        Execute model with streaming response.

        Args:
            model: Model identifier
            prompt: User prompt
            system_prompt: Optional system prompt
            parameters: Model parameters

        Yields:
            Response chunks as they are generated

        Raises:
            AuthenticationError: Invalid credentials
            TimeoutError: Request timed out
            ServerError: Provider server error
        """
        try:
            # Validate parameters
            self._validate_parameters(parameters)

            url = urljoin(self.API_BASE, 'chat/completions')

            # Build messages
            messages = self.format_messages(prompt, system_prompt)

            # Build request payload
            payload = {
                "model": model,
                "messages": messages,
                "stream": True
            }

            # Add parameters
            if parameters:
                params = self.normalize_parameters(parameters)
                payload.update(params)

            # Make streaming request (uses connection pool from session)
            response = self.session.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=self.timeout,
                stream=True
            )
            response.raise_for_status()

            # Stream response
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        line = line[6:]  # Remove 'data: ' prefix

                        if line == '[DONE]':
                            break

                        try:
                            data = json.loads(line)
                            delta = data['choices'][0]['delta']
                            content = delta.get('content', '')
                            if content:
                                yield content

                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse JSON line: {line}")
                            continue

        except requests.exceptions.Timeout:
            raise TimeoutError("Stream request timed out")
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(f"Stream connection failed: {str(e)}")
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if hasattr(e, 'response') else None
            if status_code == 401:
                raise AuthenticationError("Invalid or expired API key", 401)
            elif status_code == 429:
                raise RateLimitError("Rate limit exceeded", 429)
            elif status_code and status_code >= 500:
                raise ServerError(f"Server error", status_code)
            raise ProviderError(f"Stream HTTP error: {str(e)}")
        except requests.RequestException as e:
            raise ProviderError(f"OpenRouter streaming request failed: {str(e)}")

    def validate_config(self) -> bool:
        """
        Validate OpenRouter API key and connectivity.

        Returns:
            True if API key is valid and server is accessible

        Raises:
            AuthenticationError: If API key is invalid
        """
        try:
            # Test API key by listing models
            url = urljoin(self.API_BASE, 'models')
            response = self.session.get(
                url,
                headers=self.headers,
                timeout=10
            )

            if response.status_code == 401:
                logger.error("Invalid OpenRouter API key")
                raise AuthenticationError("Invalid API key", 401)

            response.raise_for_status()
            logger.info("OpenRouter API key validated successfully")
            return True

        except requests.RequestException as e:
            logger.error(f"OpenRouter validation failed: {e}")
            return False

    def get_info(self) -> Dict[str, Any]:
        """
        Get OpenRouter provider information.

        Returns:
            Provider metadata and status
        """
        info = {
            "name": "OpenRouter",
            "version": "v1",
            "status": "offline",
            "api_base": self.API_BASE,
            "app_name": self.app_name,
            "capabilities": [
                "streaming",
                "system_prompts",
                "chat_completions",
                "multi_provider",
                "cost_tracking",
                "error_classification"
            ],
            "available_models": 0
        }

        try:
            # Validate and count models
            if self.validate_config():
                info["status"] = "online"
                models = self.list_models()
                info["available_models"] = len(models)

        except Exception as e:
            logger.warning(f"Failed to get OpenRouter info: {e}")

        return info

    def normalize_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize parameters for OpenRouter.

        OpenRouter uses OpenAI-compatible parameter names.
        """
        normalized = {}

        # Map common parameters
        param_mapping = {
            'temperature': 'temperature',
            'temp': 'temperature',
            'top_p': 'top_p',
            'max_tokens': 'max_tokens',
            'max_length': 'max_tokens',
            'frequency_penalty': 'frequency_penalty',
            'presence_penalty': 'presence_penalty',
            'stop': 'stop',
            'n': 'n',
            'seed': 'seed'
        }

        for key, value in parameters.items():
            if key in param_mapping:
                normalized[param_mapping[key]] = value

        return normalized

    def _validate_parameters(self, parameters: Optional[Dict[str, Any]]) -> None:
        """
        Validate request parameters against known parameters.

        Args:
            parameters: Parameters to validate

        Raises:
            InvalidParameterError: If unknown parameters are provided
        """
        if not parameters:
            return

        # Known valid parameters for OpenRouter
        known_params = {
            'temperature', 'temp', 'top_p', 'max_tokens', 'max_length',
            'frequency_penalty', 'presence_penalty', 'stop', 'n', 'seed',
            'provider', 'models', 'top_k', 'min_p'
        }

        unknown_params = set(parameters.keys()) - known_params
        if unknown_params:
            logger.warning(f"Unknown parameters provided: {unknown_params}")
            raise InvalidParameterError(
                f"Unknown parameters: {', '.join(unknown_params)}. "
                f"Valid parameters: {', '.join(sorted(known_params))}"
            )

    def get_credits(self) -> Dict[str, Any]:
        """
        Get current credit balance and usage.

        Returns:
            Dictionary with credit information

        Raises:
            AuthenticationError: If API key is invalid
            ProviderError: If request fails
        """
        try:
            url = urljoin(self.API_BASE, 'auth/key')
            response = self.session.get(
                url,
                headers=self.headers,
                timeout=10
            )

            if response.status_code == 401:
                raise AuthenticationError("Invalid API key", 401)

            response.raise_for_status()

            data = response.json()
            return {
                "credits": data.get('data', {}).get('credit_limit', 0),
                "usage": data.get('data', {}).get('usage', 0),
                "label": data.get('data', {}).get('label', ''),
                "rate_limit": data.get('data', {}).get('rate_limit', {})
            }

        except requests.RequestException as e:
            logger.error(f"Failed to get credits: {e}")
            return {}

    def search_models(
        self,
        query: str = "",
        provider: Optional[str] = None,
        modality: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for models by criteria.

        Args:
            query: Search query (model name, description)
            provider: Filter by provider (e.g., 'openai', 'anthropic')
            modality: Filter by modality (e.g., 'text', 'image')

        Returns:
            Filtered list of models
        """
        models = self.list_models()

        # Apply filters
        filtered = models

        if query:
            query_lower = query.lower()
            filtered = [
                m for m in filtered
                if query_lower in m['id'].lower() or
                   query_lower in m['name'].lower() or
                   query_lower in m.get('description', '').lower()
            ]

        if provider:
            provider_lower = provider.lower()
            filtered = [
                m for m in filtered
                if provider_lower in m['id'].lower()
            ]

        if modality:
            # This would require additional metadata from OpenRouter
            # For now, just return filtered list
            pass

        return filtered

    def get_generation_stats(self, generation_id: str) -> Dict[str, Any]:
        """
        Get statistics for a specific generation.

        Args:
            generation_id: Generation ID from response

        Returns:
            Statistics dictionary
        """
        try:
            url = urljoin(self.API_BASE, f'generation?id={generation_id}')
            response = self.session.get(
                url,
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()

            return response.json()

        except requests.RequestException as e:
            logger.error(f"Failed to get generation stats: {e}")
            return {}
