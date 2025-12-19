"""
OpenAI Provider
Connect to OpenAI API for GPT models
"""

import requests
import json
from typing import Dict, List, Optional, Any, Generator
from urllib.parse import urljoin

from .base_provider import LLMProvider, logger


class OpenAIProvider(LLMProvider):
    """
    Provider for OpenAI API.

    Supports:
    - GPT-4 models (gpt-4, gpt-4-turbo, gpt-4o)
    - GPT-3.5 models (gpt-3.5-turbo)
    - Streaming responses
    - Function calling
    - Vision capabilities (GPT-4V)
    - JSON mode
    - System prompts
    """

    API_BASE = "https://api.openai.com/v1/"

    # Popular models with metadata
    KNOWN_MODELS = {
        "gpt-4o": {
            "name": "GPT-4o",
            "description": "Most advanced multimodal model",
            "context_length": 128000,
            "capabilities": ["text", "vision", "function_calling"]
        },
        "gpt-4-turbo": {
            "name": "GPT-4 Turbo",
            "description": "Fast and capable GPT-4 variant",
            "context_length": 128000,
            "capabilities": ["text", "vision", "function_calling"]
        },
        "gpt-4": {
            "name": "GPT-4",
            "description": "Most capable GPT-4 model",
            "context_length": 8192,
            "capabilities": ["text", "function_calling"]
        },
        "gpt-3.5-turbo": {
            "name": "GPT-3.5 Turbo",
            "description": "Fast and cost-effective",
            "context_length": 16385,
            "capabilities": ["text", "function_calling"]
        }
    }

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize OpenAI provider.

        Config keys:
            - api_key: OpenAI API key (REQUIRED)
            - organization: OpenAI organization ID (optional)
            - base_url: Custom API base URL (optional, for Azure OpenAI)
            - timeout: Request timeout in seconds (default: 300)
        """
        super().__init__(config)

        self.api_key = config.get('api_key')
        if not self.api_key:
            raise ValueError("OpenAI API key is required")

        self.organization = config.get('organization')
        self.base_url = config.get('base_url', self.API_BASE)
        self.timeout = config.get('timeout', 300)

        # Build headers
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        if self.organization:
            self.headers["OpenAI-Organization"] = self.organization

        logger.info(f"OpenAI provider initialized: base_url={self.base_url}")

    def list_models(self) -> List[Dict[str, Any]]:
        """
        List all available models from OpenAI.

        Returns:
            List of model dictionaries
        """
        try:
            url = urljoin(self.base_url, 'models')
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

                # Only include chat models
                if not any(x in model_id for x in ['gpt-3.5', 'gpt-4']):
                    continue

                # Get known model info or use defaults
                known = self.KNOWN_MODELS.get(model_id, {})

                models.append({
                    "id": model_id,
                    "name": known.get("name", model_id),
                    "description": known.get("description", f"OpenAI model: {model_id}"),
                    "context_length": known.get("context_length", 4096),
                    "capabilities": known.get("capabilities", ["text"]),
                    "owned_by": model.get('owned_by', 'openai'),
                    "created": model.get('created', 0),
                    "framework": "openai"
                })

            logger.info(f"Found {len(models)} OpenAI models")
            return sorted(models, key=lambda x: x['created'], reverse=True)

        except requests.RequestException as e:
            logger.error(f"Failed to list OpenAI models: {e}")
            # Return known models as fallback
            return [
                {
                    "id": model_id,
                    "name": info["name"],
                    "description": info["description"],
                    "context_length": info["context_length"],
                    "capabilities": info["capabilities"],
                    "framework": "openai"
                }
                for model_id, info in self.KNOWN_MODELS.items()
            ]

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
            model: Model identifier (e.g., 'gpt-4', 'gpt-3.5-turbo')
            prompt: User prompt
            system_prompt: Optional system prompt
            parameters: Model parameters

        Returns:
            Complete model response
        """
        try:
            url = urljoin(self.base_url, 'chat/completions')

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
            logger.info(f"OpenAI usage - prompt: {usage.get('prompt_tokens', 0)}, "
                       f"completion: {usage.get('completion_tokens', 0)}, "
                       f"total: {usage.get('total_tokens', 0)}")

            return content

        except requests.RequestException as e:
            error_msg = f"OpenAI API request failed: {str(e)}"
            logger.error(error_msg)
            if hasattr(e, 'response') and e.response is not None:
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
            url = urljoin(self.base_url, 'chat/completions')

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
                        except (KeyError, IndexError) as e:
                            logger.warning(f"Unexpected response format: {e}")
                            continue

        except requests.RequestException as e:
            error_msg = f"OpenAI streaming request failed: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def validate_config(self) -> bool:
        """
        Validate OpenAI API key and connectivity.

        Returns:
            True if API key is valid and server is accessible
        """
        try:
            # Test API key by listing models
            url = urljoin(self.base_url, 'models')
            response = requests.get(
                url,
                headers=self.headers,
                timeout=10
            )

            if response.status_code == 401:
                logger.error("Invalid OpenAI API key")
                return False

            response.raise_for_status()
            logger.info("OpenAI API key validated successfully")
            return True

        except requests.RequestException as e:
            logger.error(f"OpenAI validation failed: {e}")
            return False

    def get_info(self) -> Dict[str, Any]:
        """
        Get OpenAI provider information.

        Returns:
            Provider metadata and status
        """
        info = {
            "name": "OpenAI",
            "version": "v1",
            "status": "offline",
            "api_base": self.base_url,
            "capabilities": [
                "streaming",
                "system_prompts",
                "chat_completions",
                "function_calling",
                "vision",
                "json_mode"
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
            logger.warning(f"Failed to get OpenAI info: {e}")

        return info

    def normalize_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize parameters for OpenAI.

        OpenAI uses specific parameter names.
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
            'seed': 'seed',
            'response_format': 'response_format',
            'tools': 'tools',
            'tool_choice': 'tool_choice'
        }

        for key, value in parameters.items():
            if key in param_mapping:
                normalized[param_mapping[key]] = value

        return normalized

    def create_embedding(
        self,
        text: str,
        model: str = "text-embedding-3-small"
    ) -> List[float]:
        """
        Create text embedding.

        Args:
            text: Text to embed
            model: Embedding model (default: text-embedding-3-small)

        Returns:
            Embedding vector as list of floats
        """
        try:
            url = urljoin(self.base_url, 'embeddings')

            payload = {
                "model": model,
                "input": text
            }

            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()

            data = response.json()
            return data['data'][0]['embedding']

        except requests.RequestException as e:
            logger.error(f"Failed to create embedding: {e}")
            raise RuntimeError(f"Embedding creation failed: {str(e)}")

    def moderate_content(self, text: str) -> Dict[str, Any]:
        """
        Check content for policy violations.

        Args:
            text: Text to moderate

        Returns:
            Moderation results
        """
        try:
            url = urljoin(self.base_url, 'moderations')

            payload = {"input": text}

            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()

            data = response.json()
            return data['results'][0]

        except requests.RequestException as e:
            logger.error(f"Failed to moderate content: {e}")
            raise RuntimeError(f"Moderation failed: {str(e)}")

    def create_image(
        self,
        prompt: str,
        model: str = "dall-e-3",
        size: str = "1024x1024",
        quality: str = "standard",
        n: int = 1
    ) -> List[str]:
        """
        Generate images with DALL-E.

        Args:
            prompt: Image description
            model: Model to use (dall-e-2, dall-e-3)
            size: Image size (256x256, 512x512, 1024x1024, etc.)
            quality: Image quality (standard, hd)
            n: Number of images to generate

        Returns:
            List of image URLs
        """
        try:
            url = urljoin(self.base_url, 'images/generations')

            payload = {
                "model": model,
                "prompt": prompt,
                "size": size,
                "quality": quality,
                "n": n
            }

            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=120
            )
            response.raise_for_status()

            data = response.json()
            return [img['url'] for img in data['data']]

        except requests.RequestException as e:
            logger.error(f"Failed to generate image: {e}")
            raise RuntimeError(f"Image generation failed: {str(e)}")
