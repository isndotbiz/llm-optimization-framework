"""
Fallback Provider Chain
Manages multiple providers with intelligent fallback for error handling
"""

from typing import Dict, List, Optional, Any, Generator
import logging

from .base_provider import LLMProvider
from .provider_errors import (
    ProviderError, AuthenticationError, TimeoutError, RateLimitError,
    InvalidParameterError, ServerError, ConnectionError, NotFoundError,
    QuotaExceededError
)

logger = logging.getLogger(__name__)


class FallbackProvider(LLMProvider):
    """
    Manages multiple providers with intelligent fallback chains.

    Usage:
        primary = OpenRouterProvider(config1)
        secondary = OllamaProvider(config2)
        tertiary = LlamaCppProvider(config3)

        fallback = FallbackProvider(primary, secondary, tertiary)
        response = fallback.execute('gpt-4', 'Hello!')  # Tries each in order

    Fallback Strategy:
    - Retryable errors (timeout, server error, rate limit):
      Try next provider
    - Non-retryable errors (auth, invalid params, quota):
      Don't try next provider, raise immediately
    - Connection errors:
      Try next provider with backoff
    """

    def __init__(
        self,
        primary: LLMProvider,
        secondary: Optional[LLMProvider] = None,
        tertiary: Optional[LLMProvider] = None
    ):
        """
        Initialize fallback provider chain.

        Args:
            primary: Primary provider to try first
            secondary: Secondary provider to fall back to
            tertiary: Tertiary provider as last resort

        Raises:
            ValueError: If no providers are provided
        """
        if not primary:
            raise ValueError("At least primary provider is required")

        self.providers = [primary]
        if secondary:
            self.providers.append(secondary)
        if tertiary:
            self.providers.append(tertiary)

        # Use primary provider's config as fallback
        super().__init__(primary.config)

        logger.info(f"FallbackProvider initialized with {len(self.providers)} provider(s)")

    def list_models(self) -> List[Dict[str, Any]]:
        """
        List all available models from all providers.

        Returns:
            Combined list of models from all providers
        """
        all_models = []
        errors = []

        for i, provider in enumerate(self.providers):
            try:
                logger.debug(f"Listing models from provider {i}: {provider.name}")
                models = provider.list_models()
                all_models.extend(models)
            except Exception as e:
                error_msg = f"{provider.name}: {str(e)}"
                logger.warning(f"Failed to list models: {error_msg}")
                errors.append(error_msg)

        if all_models:
            logger.info(f"Found {len(all_models)} total models from {len(self.providers)} provider(s)")
        else:
            logger.error(f"Failed to list models from any provider: {errors}")

        return all_models

    def execute(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Execute model with fallback chain.

        Tries providers in order. Falls back on retryable errors,
        but fails immediately on non-retryable errors.

        Args:
            model: Model identifier
            prompt: User prompt
            system_prompt: Optional system prompt
            parameters: Model parameters

        Returns:
            Model response from first successful provider

        Raises:
            AuthenticationError: Authentication failed (non-retryable)
            InvalidParameterError: Invalid parameters (non-retryable)
            QuotaExceededError: Quota exceeded (non-retryable)
            ProviderError: All providers failed
        """
        last_error = None

        for i, provider in enumerate(self.providers):
            try:
                logger.info(f"Attempting execute on provider {i + 1}/{len(self.providers)}: {provider.name}")
                response = provider.execute(model, prompt, system_prompt, parameters)
                logger.info(f"Success on provider {i}: {provider.name}")
                return response

            except (AuthenticationError, InvalidParameterError, QuotaExceededError, NotFoundError) as e:
                # Non-retryable errors - fail immediately
                logger.error(f"Non-retryable error on provider {i} ({provider.name}): {e}")
                raise

            except (TimeoutError, ServerError, ConnectionError, RateLimitError) as e:
                # Retryable errors - try next provider
                last_error = e
                logger.warning(
                    f"Retryable error on provider {i} ({provider.name}): {e}. "
                    f"Trying next provider..." if i < len(self.providers) - 1 else
                    f"Retryable error on provider {i} ({provider.name}): {e}. "
                    f"No more providers to try."
                )

                if i == len(self.providers) - 1:
                    # Last provider failed
                    break

            except ProviderError as e:
                # Generic provider error - try next if available
                last_error = e
                logger.warning(f"Provider error on {provider.name}: {e}. Trying next provider...")

                if i == len(self.providers) - 1:
                    break

            except Exception as e:
                # Unexpected error - log but don't stop chain
                last_error = e
                logger.error(f"Unexpected error on {provider.name}: {e}. Trying next provider...")

                if i == len(self.providers) - 1:
                    break

        # All providers failed
        error_msg = f"All {len(self.providers)} provider(s) failed"
        if last_error:
            error_msg += f". Last error: {str(last_error)}"
        logger.error(error_msg)

        raise ProviderError(error_msg)

    def stream_execute(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Generator[str, None, None]:
        """
        Execute model with streaming and fallback chain.

        Tries providers in order. Falls back on retryable errors.

        Args:
            model: Model identifier
            prompt: User prompt
            system_prompt: Optional system prompt
            parameters: Model parameters

        Yields:
            Response chunks from first successful provider

        Raises:
            AuthenticationError: Authentication failed
            InvalidParameterError: Invalid parameters
            ProviderError: All providers failed
        """
        last_error = None

        for i, provider in enumerate(self.providers):
            try:
                logger.info(f"Attempting stream execute on provider {i + 1}/{len(self.providers)}: {provider.name}")

                # Create generator from provider
                generator = provider.stream_execute(model, prompt, system_prompt, parameters)

                # Yield from successful provider
                for chunk in generator:
                    yield chunk

                logger.info(f"Stream success on provider {i}: {provider.name}")
                return

            except (AuthenticationError, InvalidParameterError, QuotaExceededError, NotFoundError) as e:
                # Non-retryable errors - fail immediately
                logger.error(f"Non-retryable error on provider {i} ({provider.name}): {e}")
                raise

            except (TimeoutError, ServerError, ConnectionError, RateLimitError) as e:
                # Retryable errors - try next provider
                last_error = e
                logger.warning(
                    f"Retryable error on provider {i} ({provider.name}): {e}. "
                    f"Trying next provider..."
                )

                if i == len(self.providers) - 1:
                    break

            except ProviderError as e:
                # Generic provider error - try next if available
                last_error = e
                logger.warning(f"Provider error on {provider.name}: {e}. Trying next provider...")

                if i == len(self.providers) - 1:
                    break

            except Exception as e:
                # Unexpected error - log but don't stop chain
                last_error = e
                logger.error(f"Unexpected error on {provider.name}: {e}. Trying next provider...")

                if i == len(self.providers) - 1:
                    break

        # All providers failed for streaming
        error_msg = f"All {len(self.providers)} provider(s) failed for streaming"
        if last_error:
            error_msg += f". Last error: {str(last_error)}"
        logger.error(error_msg)

        raise ProviderError(error_msg)

    def validate_config(self) -> bool:
        """
        Validate that at least one provider is properly configured.

        Returns:
            True if at least one provider is valid
        """
        valid_providers = []

        for i, provider in enumerate(self.providers):
            try:
                if provider.validate_config():
                    valid_providers.append(provider.name)
                    logger.info(f"Provider {i} ({provider.name}) is valid")
                else:
                    logger.warning(f"Provider {i} ({provider.name}) validation failed")
            except Exception as e:
                logger.warning(f"Provider {i} ({provider.name}) validation error: {e}")

        is_valid = len(valid_providers) > 0
        if is_valid:
            logger.info(f"At least one provider is valid: {valid_providers}")
        else:
            logger.error("No valid providers in fallback chain")

        return is_valid

    def get_info(self) -> Dict[str, Any]:
        """
        Get information about fallback chain and all providers.

        Returns:
            Dictionary with chain and provider information
        """
        provider_infos = []

        for i, provider in enumerate(self.providers):
            try:
                info = provider.get_info()
                info['position'] = i
                provider_infos.append(info)
            except Exception as e:
                logger.warning(f"Failed to get info for provider {i}: {e}")
                provider_infos.append({
                    'name': provider.name,
                    'position': i,
                    'status': 'error',
                    'error': str(e)
                })

        return {
            "name": "FallbackProvider",
            "type": "fallback_chain",
            "description": "Manages multiple providers with intelligent error handling",
            "provider_count": len(self.providers),
            "providers": provider_infos,
            "fallback_strategy": {
                "non_retryable": ["AuthenticationError", "InvalidParameterError", "QuotaExceededError"],
                "retryable": ["TimeoutError", "ServerError", "ConnectionError", "RateLimitError"]
            }
        }

    def get_provider(self, index: int) -> Optional[LLMProvider]:
        """
        Get a specific provider by index.

        Args:
            index: Provider index (0 = primary, 1 = secondary, etc.)

        Returns:
            Provider instance or None if index out of range
        """
        if 0 <= index < len(self.providers):
            return self.providers[index]
        return None

    def add_provider(self, provider: LLMProvider) -> None:
        """
        Add a provider to the fallback chain.

        Args:
            provider: Provider to add
        """
        if not provider:
            raise ValueError("Provider cannot be None")

        self.providers.append(provider)
        logger.info(f"Added provider to fallback chain: {provider.name}")

    def get_provider_count(self) -> int:
        """
        Get the number of providers in the chain.

        Returns:
            Number of providers
        """
        return len(self.providers)

    def normalize_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize parameters using primary provider's method.

        Args:
            parameters: Parameters to normalize

        Returns:
            Normalized parameters
        """
        return self.providers[0].normalize_parameters(parameters)
