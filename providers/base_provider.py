"""
Base Provider Abstract Class
Defines the interface that all LLM providers must implement
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Generator
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """
    Abstract base class for all LLM providers.

    All providers must implement these core methods to ensure
    consistent behavior across different LLM backends.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize provider with configuration.

        Args:
            config: Provider-specific configuration dictionary
                   Common keys: api_key, base_url, timeout, etc.
        """
        self.config = config
        self.name = self.__class__.__name__
        logger.info(f"Initializing {self.name} with config: {self._safe_config()}")

    def _safe_config(self) -> Dict[str, Any]:
        """
        Return config with sensitive data masked for logging.

        Returns:
            Config dictionary with API keys and secrets masked
        """
        safe = self.config.copy()
        if 'api_key' in safe:
            safe['api_key'] = '***REDACTED***'
        if 'oauth_token' in safe:
            safe['oauth_token'] = '***REDACTED***'
        return safe

    @abstractmethod
    def list_models(self) -> List[Dict[str, Any]]:
        """
        Return available models for this provider.

        Returns:
            List of model dictionaries with keys:
                - id: Model identifier
                - name: Human-readable name
                - description: Model description
                - context_length: Maximum context window
                - pricing: Pricing information (optional)

        Example:
            [
                {
                    "id": "gpt-4",
                    "name": "GPT-4",
                    "description": "Most capable GPT-4 model",
                    "context_length": 8192,
                    "pricing": {"input": 0.03, "output": 0.06}
                }
            ]
        """
        pass

    @abstractmethod
    def execute(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Execute model with given parameters and return response.

        Args:
            model: Model identifier to use
            prompt: User prompt/message
            system_prompt: Optional system prompt for behavior control
            parameters: Model parameters (temperature, top_p, max_tokens, etc.)

        Returns:
            Model response as string

        Raises:
            ValueError: If model not found or parameters invalid
            RuntimeError: If API call fails
        """
        pass

    @abstractmethod
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
            model: Model identifier to use
            prompt: User prompt/message
            system_prompt: Optional system prompt for behavior control
            parameters: Model parameters (temperature, top_p, max_tokens, etc.)

        Yields:
            Response chunks as they become available

        Raises:
            ValueError: If model not found or parameters invalid
            RuntimeError: If API call fails
        """
        pass

    @abstractmethod
    def validate_config(self) -> bool:
        """
        Validate provider configuration.

        Returns:
            True if configuration is valid and provider is accessible
            False otherwise

        Example:
            Checks API key validity, network connectivity, etc.
        """
        pass

    @abstractmethod
    def get_info(self) -> Dict[str, Any]:
        """
        Get provider information and status.

        Returns:
            Dictionary with provider metadata:
                - name: Provider name
                - version: API version
                - status: Current status (online/offline/degraded)
                - capabilities: List of supported features
                - limits: Rate limits and quotas

        Example:
            {
                "name": "OpenAI",
                "version": "v1",
                "status": "online",
                "capabilities": ["streaming", "function_calling"],
                "limits": {"rpm": 3500, "tpm": 90000}
            }
        """
        pass

    def normalize_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize parameters to provider-specific format.

        Different providers use different parameter names:
        - temperature vs temp
        - max_tokens vs max_length
        - top_p vs nucleus_sampling

        Args:
            parameters: Standard parameter dictionary

        Returns:
            Provider-specific parameter dictionary
        """
        return parameters.copy()

    def format_messages(
        self,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Format prompt and system prompt into message list.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt

        Returns:
            List of message dictionaries with 'role' and 'content' keys
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return messages

    def handle_error(self, error: Exception) -> str:
        """
        Handle and format error messages.

        Args:
            error: Exception that occurred

        Returns:
            Formatted error message
        """
        error_msg = f"{self.name} Error: {str(error)}"
        logger.error(error_msg)
        return error_msg

    def __repr__(self) -> str:
        """String representation of provider."""
        return f"{self.name}(config={self._safe_config()})"
