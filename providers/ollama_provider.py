"""
Ollama Provider
Connect to local or remote Ollama instance for model execution
"""

import requests
import json
from typing import Dict, List, Optional, Any, Generator
from urllib.parse import urljoin

from .base_provider import LLMProvider, logger


class OllamaProvider(LLMProvider):
    """
    Provider for Ollama API.

    Supports:
    - Local Ollama instance (default: http://localhost:11434)
    - Remote Ollama servers
    - Model discovery via ollama list
    - Streaming responses
    - Full parameter support
    - System prompts
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Ollama provider.

        Config keys:
            - base_url: Ollama server URL (default: http://localhost:11434)
            - timeout: Request timeout in seconds (default: 300)
            - verify_ssl: Verify SSL certificates (default: True)
        """
        super().__init__(config)

        self.base_url = config.get('base_url', 'http://localhost:11434')
        self.timeout = config.get('timeout', 300)
        self.verify_ssl = config.get('verify_ssl', True)

        # Ensure base_url ends with /
        if not self.base_url.endswith('/'):
            self.base_url += '/'

        logger.info(f"Ollama provider initialized: base_url={self.base_url}")

    def list_models(self) -> List[Dict[str, Any]]:
        """
        List all available models from Ollama.

        Returns:
            List of model dictionaries
        """
        try:
            url = urljoin(self.base_url, 'api/tags')
            response = requests.get(
                url,
                timeout=10,
                verify=self.verify_ssl
            )
            response.raise_for_status()

            data = response.json()
            models = []

            for model in data.get('models', []):
                # Extract model info
                name = model.get('name', 'unknown')
                size = model.get('size', 0)
                size_gb = size / (1024**3)

                models.append({
                    "id": name,
                    "name": name,
                    "description": f"Ollama model: {name}",
                    "size": f"{size_gb:.1f}GB",
                    "size_bytes": size,
                    "modified_at": model.get('modified_at', ''),
                    "digest": model.get('digest', ''),
                    "context_length": 4096,  # Default, can be overridden
                    "framework": "ollama"
                })

            logger.info(f"Found {len(models)} Ollama models")
            return models

        except requests.RequestException as e:
            logger.error(f"Failed to list Ollama models: {e}")
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
            model: Model identifier
            prompt: User prompt
            system_prompt: Optional system prompt
            parameters: Model parameters

        Returns:
            Complete model response
        """
        try:
            url = urljoin(self.base_url, 'api/generate')

            # Build request payload
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False
            }

            # Add system prompt if provided
            if system_prompt:
                payload["system"] = system_prompt

            # Add parameters
            if parameters:
                options = self.normalize_parameters(parameters)
                payload["options"] = options

            # Make request
            response = requests.post(
                url,
                json=payload,
                timeout=self.timeout,
                verify=self.verify_ssl
            )
            response.raise_for_status()

            # Parse response
            data = response.json()
            return data.get('response', '')

        except requests.RequestException as e:
            error_msg = f"Ollama API request failed: {str(e)}"
            logger.error(error_msg)
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
            url = urljoin(self.base_url, 'api/generate')

            # Build request payload
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": True
            }

            # Add system prompt if provided
            if system_prompt:
                payload["system"] = system_prompt

            # Add parameters
            if parameters:
                options = self.normalize_parameters(parameters)
                payload["options"] = options

            # Make streaming request
            response = requests.post(
                url,
                json=payload,
                timeout=self.timeout,
                verify=self.verify_ssl,
                stream=True
            )
            response.raise_for_status()

            # Stream response line by line
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        chunk = data.get('response', '')
                        if chunk:
                            yield chunk

                        # Check if done
                        if data.get('done', False):
                            break

                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse JSON line: {line}")
                        continue

        except requests.RequestException as e:
            error_msg = f"Ollama streaming request failed: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def chat_execute(
        self,
        model: str,
        messages: List[Dict[str, str]],
        parameters: Optional[Dict[str, Any]] = None,
        stream: bool = False
    ) -> Any:
        """
        Execute chat completion request.

        Args:
            model: Model identifier
            messages: List of message dictionaries with 'role' and 'content'
            parameters: Model parameters
            stream: Enable streaming

        Returns:
            Response string or generator if streaming
        """
        try:
            url = urljoin(self.base_url, 'api/chat')

            # Build request payload
            payload = {
                "model": model,
                "messages": messages,
                "stream": stream
            }

            # Add parameters
            if parameters:
                options = self.normalize_parameters(parameters)
                payload["options"] = options

            if stream:
                # Streaming response
                response = requests.post(
                    url,
                    json=payload,
                    timeout=self.timeout,
                    verify=self.verify_ssl,
                    stream=True
                )
                response.raise_for_status()

                def stream_generator():
                    for line in response.iter_lines():
                        if line:
                            try:
                                data = json.loads(line)
                                chunk = data.get('message', {}).get('content', '')
                                if chunk:
                                    yield chunk

                                if data.get('done', False):
                                    break

                            except json.JSONDecodeError:
                                continue

                return stream_generator()

            else:
                # Non-streaming response
                response = requests.post(
                    url,
                    json=payload,
                    timeout=self.timeout,
                    verify=self.verify_ssl
                )
                response.raise_for_status()

                data = response.json()
                return data.get('message', {}).get('content', '')

        except requests.RequestException as e:
            error_msg = f"Ollama chat request failed: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def validate_config(self) -> bool:
        """
        Validate Ollama configuration and connectivity.

        Returns:
            True if Ollama server is accessible
        """
        try:
            url = urljoin(self.base_url, 'api/version')
            response = requests.get(
                url,
                timeout=5,
                verify=self.verify_ssl
            )
            response.raise_for_status()

            logger.info("Ollama server is accessible")
            return True

        except requests.RequestException as e:
            logger.error(f"Ollama server not accessible: {e}")
            return False

    def get_info(self) -> Dict[str, Any]:
        """
        Get Ollama provider information.

        Returns:
            Provider metadata and status
        """
        info = {
            "name": "Ollama",
            "version": "unknown",
            "status": "offline",
            "base_url": self.base_url,
            "capabilities": [
                "streaming",
                "system_prompts",
                "chat_completions",
                "model_discovery"
            ],
            "available_models": 0
        }

        try:
            # Get version
            url = urljoin(self.base_url, 'api/version')
            response = requests.get(url, timeout=5, verify=self.verify_ssl)
            if response.status_code == 200:
                data = response.json()
                info["version"] = data.get('version', 'unknown')
                info["status"] = "online"

            # Count models
            models = self.list_models()
            info["available_models"] = len(models)

        except Exception as e:
            logger.warning(f"Failed to get Ollama info: {e}")

        return info

    def normalize_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize parameters for Ollama.

        Ollama uses 'options' dict with specific parameter names.
        """
        options = {}

        # Map common parameters to Ollama names
        param_mapping = {
            'temperature': 'temperature',
            'temp': 'temperature',
            'top_p': 'top_p',
            'top_k': 'top_k',
            'max_tokens': 'num_predict',
            'max_length': 'num_predict',
            'repeat_penalty': 'repeat_penalty',
            'seed': 'seed',
            'context': 'num_ctx',
            'context_length': 'num_ctx',
        }

        for key, value in parameters.items():
            if key in param_mapping:
                options[param_mapping[key]] = value
            else:
                # Pass through unknown parameters
                options[key] = value

        return options

    def pull_model(self, model: str) -> bool:
        """
        Pull/download a model from Ollama library.

        Args:
            model: Model name to pull (e.g., 'llama2', 'mistral')

        Returns:
            True if successful
        """
        try:
            url = urljoin(self.base_url, 'api/pull')
            payload = {"name": model}

            logger.info(f"Pulling Ollama model: {model}")

            response = requests.post(
                url,
                json=payload,
                timeout=3600,  # 1 hour for large models
                verify=self.verify_ssl,
                stream=True
            )
            response.raise_for_status()

            # Monitor progress
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        status = data.get('status', '')
                        if status:
                            logger.info(f"Pull status: {status}")

                        if data.get('error'):
                            logger.error(f"Pull error: {data['error']}")
                            return False

                    except json.JSONDecodeError:
                        continue

            logger.info(f"Successfully pulled model: {model}")
            return True

        except requests.RequestException as e:
            logger.error(f"Failed to pull model: {e}")
            return False

    def delete_model(self, model: str) -> bool:
        """
        Delete a model from Ollama.

        Args:
            model: Model name to delete

        Returns:
            True if successful
        """
        try:
            url = urljoin(self.base_url, 'api/delete')
            payload = {"name": model}

            response = requests.delete(
                url,
                json=payload,
                timeout=30,
                verify=self.verify_ssl
            )
            response.raise_for_status()

            logger.info(f"Successfully deleted model: {model}")
            return True

        except requests.RequestException as e:
            logger.error(f"Failed to delete model: {e}")
            return False
