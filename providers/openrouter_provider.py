"""
OpenRouter Provider
Connect to OpenRouter API for access to multiple LLM providers
"""

import requests
import json
from typing import Dict, List, Optional, Any, Generator
from urllib.parse import urljoin

from .base_provider import LLMProvider, logger


class OpenRouterProvider(LLMProvider):
    """
    Provider for OpenRouter API.

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
    """

    API_BASE = "https://openrouter.ai/api/v1/"

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize OpenRouter provider.

        Config keys:
            - api_key: OpenRouter API key (REQUIRED)
            - app_name: Your app name for tracking (optional)
            - app_url: Your app URL (optional)
            - timeout: Request timeout in seconds (default: 300)
        """
        super().__init__(config)

        self.api_key = config.get('api_key')
        if not self.api_key:
            raise ValueError("OpenRouter API key is required")

        self.app_name = config.get('app_name', 'AI-Router')
        self.app_url = config.get('app_url', 'https://github.com/yourusername/ai-router')
        self.timeout = config.get('timeout', 300)

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": self.app_url,
            "X-Title": self.app_name,
            "Content-Type": "application/json"
        }

        logger.info(f"OpenRouter provider initialized: app={self.app_name}")

    def list_models(self) -> List[Dict[str, Any]]:
        """
        List all available models from OpenRouter.

        Returns:
            List of model dictionaries with pricing info
        """
        try:
            url = urljoin(self.API_BASE, 'models')
            response = requests.get(
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

        except requests.RequestException as e:
            logger.error(f"Failed to list OpenRouter models: {e}")
            return []

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
        """
        try:
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

            # Make request
            response = requests.post(
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

        except requests.RequestException as e:
            error_msg = f"OpenRouter API request failed: {str(e)}"
            logger.error(error_msg)
            if hasattr(e.response, 'text'):
                logger.error(f"Response: {e.response.text}")
            raise RuntimeError(error_msg)

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
        """
        try:
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

            # Make streaming request
            response = requests.post(
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

        except requests.RequestException as e:
            error_msg = f"OpenRouter streaming request failed: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def validate_config(self) -> bool:
        """
        Validate OpenRouter API key and connectivity.

        Returns:
            True if API key is valid and server is accessible
        """
        try:
            # Test API key by listing models
            url = urljoin(self.API_BASE, 'models')
            response = requests.get(
                url,
                headers=self.headers,
                timeout=10
            )

            if response.status_code == 401:
                logger.error("Invalid OpenRouter API key")
                return False

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
                "cost_tracking"
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

    def get_credits(self) -> Dict[str, Any]:
        """
        Get current credit balance and usage.

        Returns:
            Dictionary with credit information
        """
        try:
            url = urljoin(self.API_BASE, 'auth/key')
            response = requests.get(
                url,
                headers=self.headers,
                timeout=10
            )
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
            response = requests.get(
                url,
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()

            return response.json()

        except requests.RequestException as e:
            logger.error(f"Failed to get generation stats: {e}")
            return {}
