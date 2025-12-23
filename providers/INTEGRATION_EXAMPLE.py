"""
Complete Integration Example: Provider Error Classification & Fallback Chains

This file demonstrates the complete integration of the provider error
classification and fallback chain system into a production application.
"""

import logging
from typing import Optional, Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import everything we need
from providers import (
    # Error classes
    ProviderError,
    AuthenticationError,
    TimeoutError,
    RateLimitError,
    InvalidParameterError,
    ServerError,
    ConnectionError,
    NotFoundError,
    # Providers
    OpenRouterProviderEnhanced,
    OllamaProvider,
    FallbackProvider,
    # Utilities
    classify_error
)


class AIRouterWithFallback:
    """
    AI Router with automatic fallback and intelligent error handling.

    This router demonstrates how to integrate:
    1. Enhanced provider with error classification
    2. Fallback chains for resilience
    3. Custom retry logic
    4. Error-specific handling
    """

    def __init__(
        self,
        openrouter_config: Dict[str, Any],
        ollama_config: Optional[Dict[str, Any]] = None,
        enable_fallback: bool = True
    ):
        """
        Initialize router with providers.

        Args:
            openrouter_config: OpenRouter API configuration
            ollama_config: Ollama server configuration (optional)
            enable_fallback: Enable fallback chain (default: True)
        """
        # Create primary provider
        self.primary = OpenRouterProviderEnhanced(openrouter_config)

        # Create fallback chain if enabled
        if enable_fallback and ollama_config:
            self.secondary = OllamaProvider(ollama_config)
            self.provider = FallbackProvider(self.primary, self.secondary)
            logger.info("Fallback chain enabled: OpenRouter -> Ollama")
        else:
            self.provider = self.primary
            logger.info("Single provider mode: OpenRouter only")

    def execute(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        max_retries: int = 1
    ) -> str:
        """
        Execute model with error handling and optional retries.

        Args:
            model: Model identifier
            prompt: User prompt
            system_prompt: Optional system prompt
            parameters: Model parameters
            max_retries: Number of retries for retryable errors

        Returns:
            Model response

        Raises:
            AuthenticationError: Invalid credentials
            InvalidParameterError: Invalid parameters
            ProviderError: All providers failed
        """
        attempt = 0

        while attempt <= max_retries:
            try:
                logger.info(f"Executing on provider (attempt {attempt + 1})")

                response = self.provider.execute(
                    model=model,
                    prompt=prompt,
                    system_prompt=system_prompt,
                    parameters=parameters
                )

                logger.info("Execution successful")
                return response

            except (AuthenticationError, InvalidParameterError, NotFoundError) as e:
                # Non-retryable errors - fail immediately
                logger.error(f"Non-retryable error: {e}")
                raise

            except TimeoutError as e:
                # Timeout - can retry
                if attempt < max_retries:
                    logger.warning(f"Timeout on attempt {attempt + 1}, retrying...")
                    import time
                    time.sleep(2 ** attempt)  # exponential backoff
                    attempt += 1
                else:
                    logger.error(f"Timeout after {max_retries} retries")
                    raise

            except RateLimitError as e:
                # Rate limited - wait and retry
                if attempt < max_retries:
                    wait_time = e.retry_after or 60
                    logger.warning(f"Rate limited, waiting {wait_time}s...")
                    import time
                    time.sleep(wait_time)
                    attempt += 1
                else:
                    logger.error(f"Rate limit exceeded after {max_retries} retries")
                    raise

            except (ServerError, ConnectionError) as e:
                # Server/connection error - can retry
                if attempt < max_retries:
                    logger.warning(f"Retryable error: {e}, retrying...")
                    import time
                    time.sleep(2 ** attempt)
                    attempt += 1
                else:
                    logger.error(f"Provider error after {max_retries} retries")
                    raise

            except ProviderError as e:
                # Other provider errors
                logger.error(f"Provider error: {e}")
                if "All" in str(e):
                    # Fallback chain exhausted
                    raise
                elif attempt < max_retries:
                    attempt += 1
                else:
                    raise

            except Exception as e:
                # Unexpected error
                logger.error(f"Unexpected error: {e}")
                raise

    def stream_execute(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ):
        """
        Stream model response with fallback.

        Args:
            model: Model identifier
            prompt: User prompt
            system_prompt: Optional system prompt
            parameters: Model parameters

        Yields:
            Response chunks

        Raises:
            ProviderError: All providers failed
        """
        try:
            logger.info("Starting stream execution")

            for chunk in self.provider.stream_execute(
                model=model,
                prompt=prompt,
                system_prompt=system_prompt,
                parameters=parameters
            ):
                yield chunk

            logger.info("Stream execution completed")

        except (AuthenticationError, InvalidParameterError) as e:
            logger.error(f"Non-retryable error: {e}")
            raise

        except ProviderError as e:
            logger.error(f"Provider error: {e}")
            raise

    def get_status(self) -> Dict[str, Any]:
        """
        Get status of all providers in chain.

        Returns:
            Status information
        """
        info = self.provider.get_info()
        return {
            "provider_type": type(self.provider).__name__,
            "fallback_enabled": isinstance(self.provider, FallbackProvider),
            "details": info
        }


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

def example_basic_usage():
    """Basic usage example"""
    print("\n=== Example 1: Basic Usage ===\n")

    router = AIRouterWithFallback(
        openrouter_config={'api_key': 'your-key'},
        ollama_config={'base_url': 'http://localhost:11434'},
        enable_fallback=True
    )

    try:
        response = router.execute(
            model='gpt-4',
            prompt='What is 2+2?',
            parameters={'temperature': 0.7}
        )
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error: {e}")


def example_with_retry_logic():
    """Example with explicit retry logic"""
    print("\n=== Example 2: With Retry Logic ===\n")

    router = AIRouterWithFallback(
        openrouter_config={'api_key': 'your-key'},
        enable_fallback=False
    )

    try:
        response = router.execute(
            model='gpt-4',
            prompt='Analyze this code',
            max_retries=3  # Retry up to 3 times
        )
        print(f"Response: {response}")
    except TimeoutError:
        print("All retries exhausted: Timeout")
    except Exception as e:
        print(f"Error: {e}")


def example_streaming():
    """Example with streaming"""
    print("\n=== Example 3: Streaming Response ===\n")

    router = AIRouterWithFallback(
        openrouter_config={'api_key': 'your-key'},
        ollama_config={'base_url': 'http://localhost:11434'}
    )

    try:
        print("Streaming response: ", end='', flush=True)
        for chunk in router.stream_execute(
            model='gpt-4',
            prompt='Write a haiku'
        ):
            print(chunk, end='', flush=True)
        print()
    except ProviderError as e:
        print(f"\nProvider error: {e}")


def example_error_handling():
    """Example showing different error handling"""
    print("\n=== Example 4: Error Handling ===\n")

    router = AIRouterWithFallback(
        openrouter_config={'api_key': 'invalid-key'},
        enable_fallback=False
    )

    try:
        response = router.execute(
            model='gpt-4',
            prompt='Hello'
        )
    except AuthenticationError as e:
        print(f"Auth Error: {e}")
        print("  -> Update your API key")
    except TimeoutError as e:
        print(f"Timeout Error: {e}")
        print("  -> Retry with backoff")
    except InvalidParameterError as e:
        print(f"Parameter Error: {e}")
        print("  -> Check parameter names")
    except RateLimitError as e:
        print(f"Rate Limit: {e}")
        print(f"  -> Wait {e.retry_after} seconds")
    except ServerError as e:
        print(f"Server Error: {e}")
        print("  -> Provider may be down, retry later")
    except Exception as e:
        print(f"Unknown Error: {e}")


def example_status_check():
    """Example checking provider status"""
    print("\n=== Example 5: Provider Status ===\n")

    router = AIRouterWithFallback(
        openrouter_config={'api_key': 'your-key'},
        ollama_config={'base_url': 'http://localhost:11434'}
    )

    status = router.get_status()
    print(f"Router Type: {status['provider_type']}")
    print(f"Fallback Enabled: {status['fallback_enabled']}")
    print(f"Provider Details: {status['details']}")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Provider Error Classification & Fallback Chains Integration Examples")
    print("=" * 70)

    print("""
This example shows how to integrate the provider error classification
and fallback system into your application.

Key features:
1. Specific error types instead of generic RuntimeError
2. Automatic fallback to secondary provider
3. Intelligent retry logic based on error type
4. Non-retryable errors fail immediately
5. Streaming support with fallback

See the example functions above for integration patterns.
    """)

    print("\nNote: Examples require valid API configuration to run.")
    print("Update openrouter_config and ollama_config with your settings.")

    # Uncomment to run examples (requires configuration):
    # example_basic_usage()
    # example_with_retry_logic()
    # example_streaming()
    # example_error_handling()
    # example_status_check()
