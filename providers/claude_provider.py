"""
Claude Provider
Connect to Anthropic Claude API
"""

import requests
import json
from typing import Dict, List, Optional, Any, Generator
from urllib.parse import urljoin

from .base_provider import LLMProvider, logger


class ClaudeProvider(LLMProvider):
    """
    Provider for Anthropic Claude API.

    Supports:
    - Claude 3 models (Opus, Sonnet, Haiku)
    - Claude 2.1 and 2.0
    - Streaming responses
    - System prompts
    - Vision capabilities (Claude 3)
    - Extended context (200K tokens)
    """

    API_BASE = "https://api.anthropic.com/v1/"
    API_VERSION = "2023-06-01"

    # Known models with metadata
    KNOWN_MODELS = {
        "claude-3-opus-20240229": {
            "name": "Claude 3 Opus",
            "description": "Most powerful Claude model",
            "context_length": 200000,
            "capabilities": ["text", "vision"]
        },
        "claude-3-5-sonnet-20241022": {
            "name": "Claude 3.5 Sonnet",
            "description": "Best balance of intelligence and speed",
            "context_length": 200000,
            "capabilities": ["text", "vision"]
        },
        "claude-3-sonnet-20240229": {
            "name": "Claude 3 Sonnet",
            "description": "Balanced performance and speed",
            "context_length": 200000,
            "capabilities": ["text", "vision"]
        },
        "claude-3-haiku-20240307": {
            "name": "Claude 3 Haiku",
            "description": "Fastest and most compact",
            "context_length": 200000,
            "capabilities": ["text", "vision"]
        },
        "claude-2.1": {
            "name": "Claude 2.1",
            "description": "Previous generation model",
            "context_length": 200000,
            "capabilities": ["text"]
        },
        "claude-2.0": {
            "name": "Claude 2.0",
            "description": "Previous generation model",
            "context_length": 100000,
            "capabilities": ["text"]
        }
    }

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Claude provider.

        Config keys:
            - api_key: Anthropic API key (REQUIRED)
            - api_version: API version (default: 2023-06-01)
            - timeout: Request timeout in seconds (default: 300)
        """
        super().__init__(config)

        self.api_key = config.get('api_key')
        if not self.api_key:
            raise ValueError("Anthropic API key is required")

        self.api_version = config.get('api_version', self.API_VERSION)
        self.timeout = config.get('timeout', 300)

        # Build headers
        self.headers = {
            "x-api-key": self.api_key,
            "anthropic-version": self.api_version,
            "Content-Type": "application/json"
        }

        logger.info(f"Claude provider initialized: api_version={self.api_version}")

    def list_models(self) -> List[Dict[str, Any]]:
        """
        List all available Claude models.

        Note: Anthropic doesn't provide a models endpoint,
        so we return the known models list.

        Returns:
            List of model dictionaries
        """
        models = []

        for model_id, info in self.KNOWN_MODELS.items():
            models.append({
                "id": model_id,
                "name": info["name"],
                "description": info["description"],
                "context_length": info["context_length"],
                "capabilities": info["capabilities"],
                "framework": "claude"
            })

        logger.info(f"Returning {len(models)} known Claude models")
        return models

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
            model: Model identifier (e.g., 'claude-3-opus-20240229')
            prompt: User prompt
            system_prompt: Optional system prompt
            parameters: Model parameters

        Returns:
            Complete model response
        """
        try:
            url = urljoin(self.API_BASE, 'messages')

            # Build messages (Claude uses different format)
            messages = [{"role": "user", "content": prompt}]

            # Build request payload
            payload = {
                "model": model,
                "messages": messages,
                "max_tokens": 4096  # Required parameter for Claude
            }

            # Add system prompt if provided
            if system_prompt:
                payload["system"] = system_prompt

            # Add parameters
            if parameters:
                params = self.normalize_parameters(parameters)
                payload.update(params)

            # Ensure max_tokens is set
            if 'max_tokens' not in payload:
                payload['max_tokens'] = parameters.get('max_tokens', 4096) if parameters else 4096

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
            content = data['content'][0]['text']

            # Log usage for cost tracking
            usage = data.get('usage', {})
            logger.info(f"Claude usage - input: {usage.get('input_tokens', 0)}, "
                       f"output: {usage.get('output_tokens', 0)}")

            return content

        except requests.RequestException as e:
            error_msg = f"Claude API request failed: {str(e)}"
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
            url = urljoin(self.API_BASE, 'messages')

            # Build messages
            messages = [{"role": "user", "content": prompt}]

            # Build request payload
            payload = {
                "model": model,
                "messages": messages,
                "max_tokens": 4096,
                "stream": True
            }

            # Add system prompt if provided
            if system_prompt:
                payload["system"] = system_prompt

            # Add parameters
            if parameters:
                params = self.normalize_parameters(parameters)
                payload.update(params)

            # Ensure max_tokens is set
            if 'max_tokens' not in payload:
                payload['max_tokens'] = parameters.get('max_tokens', 4096) if parameters else 4096

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

                        try:
                            data = json.loads(line)
                            event_type = data.get('type')

                            # Handle different event types
                            if event_type == 'content_block_delta':
                                delta = data.get('delta', {})
                                if delta.get('type') == 'text_delta':
                                    text = delta.get('text', '')
                                    if text:
                                        yield text

                            elif event_type == 'message_stop':
                                break

                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse JSON line: {line}")
                            continue
                        except (KeyError, IndexError) as e:
                            logger.warning(f"Unexpected response format: {e}")
                            continue

        except requests.RequestException as e:
            error_msg = f"Claude streaming request failed: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def validate_config(self) -> bool:
        """
        Validate Claude API key and connectivity.

        Returns:
            True if API key is valid and server is accessible
        """
        try:
            # Test API key with minimal request
            url = urljoin(self.API_BASE, 'messages')

            payload = {
                "model": "claude-3-haiku-20240307",  # Use fastest model for testing
                "messages": [{"role": "user", "content": "Hi"}],
                "max_tokens": 10
            }

            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 401:
                logger.error("Invalid Claude API key")
                return False

            response.raise_for_status()
            logger.info("Claude API key validated successfully")
            return True

        except requests.RequestException as e:
            logger.error(f"Claude validation failed: {e}")
            return False

    def get_info(self) -> Dict[str, Any]:
        """
        Get Claude provider information.

        Returns:
            Provider metadata and status
        """
        info = {
            "name": "Claude (Anthropic)",
            "version": self.api_version,
            "status": "offline",
            "api_base": self.API_BASE,
            "capabilities": [
                "streaming",
                "system_prompts",
                "extended_context",
                "vision",
                "constitutional_ai"
            ],
            "available_models": len(self.KNOWN_MODELS)
        }

        try:
            # Validate connectivity
            if self.validate_config():
                info["status"] = "online"

        except Exception as e:
            logger.warning(f"Failed to get Claude info: {e}")

        return info

    def normalize_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize parameters for Claude.

        Claude uses specific parameter names that differ from OpenAI.
        """
        normalized = {}

        # Map common parameters
        param_mapping = {
            'temperature': 'temperature',
            'temp': 'temperature',
            'top_p': 'top_p',
            'top_k': 'top_k',
            'max_tokens': 'max_tokens',
            'max_length': 'max_tokens',
            'stop_sequences': 'stop_sequences',
            'stop': 'stop_sequences'
        }

        for key, value in parameters.items():
            if key in param_mapping:
                normalized[param_mapping[key]] = value

        return normalized

    def count_tokens(self, text: str) -> int:
        """
        Estimate token count for text.

        This is a rough approximation. For accurate counts,
        use Anthropic's tokenization library.

        Args:
            text: Text to count tokens for

        Returns:
            Estimated token count
        """
        # Rough estimate: ~4 characters per token
        return len(text) // 4

    def format_messages_for_claude(
        self,
        messages: List[Dict[str, str]]
    ) -> tuple[Optional[str], List[Dict[str, str]]]:
        """
        Format messages for Claude API.

        Claude separates system messages from user/assistant messages.

        Args:
            messages: List of message dictionaries

        Returns:
            Tuple of (system_prompt, user_messages)
        """
        system_prompt = None
        user_messages = []

        for msg in messages:
            role = msg.get('role')
            content = msg.get('content')

            if role == 'system':
                # Claude uses a separate system parameter
                if system_prompt:
                    system_prompt += "\n\n" + content
                else:
                    system_prompt = content
            else:
                user_messages.append(msg)

        return system_prompt, user_messages

    def execute_with_vision(
        self,
        model: str,
        prompt: str,
        image_url: str,
        system_prompt: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Execute model with vision capability.

        Args:
            model: Model identifier (must be Claude 3)
            prompt: User prompt
            image_url: URL or base64 encoded image
            system_prompt: Optional system prompt
            parameters: Model parameters

        Returns:
            Complete model response
        """
        try:
            url = urljoin(self.API_BASE, 'messages')

            # Build vision message
            content = [
                {
                    "type": "image",
                    "source": {
                        "type": "url",
                        "url": image_url
                    }
                },
                {
                    "type": "text",
                    "text": prompt
                }
            ]

            messages = [{"role": "user", "content": content}]

            # Build request payload
            payload = {
                "model": model,
                "messages": messages,
                "max_tokens": 4096
            }

            # Add system prompt if provided
            if system_prompt:
                payload["system"] = system_prompt

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
            return data['content'][0]['text']

        except requests.RequestException as e:
            error_msg = f"Claude vision request failed: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
