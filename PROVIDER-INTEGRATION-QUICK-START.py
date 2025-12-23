"""
Quick Start: Provider Error Classification & Fallback Chains
Complete working examples showing integration
"""

# ============================================================================
# EXAMPLE 1: Using Enhanced OpenRouter with Error Handling
# ============================================================================

def example_1_enhanced_openrouter():
    """Basic usage with error handling"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Enhanced OpenRouter with Error Handling")
    print("="*70 + "\n")

    from providers import (
        OpenRouterProviderEnhanced,
        AuthenticationError,
        TimeoutError,
        InvalidParameterError
    )

    try:
        # Initialize enhanced provider
        provider = OpenRouterProviderEnhanced({
            'api_key': 'your-openrouter-key',
            'app_name': 'MyApp',
            'timeout': 30
        })

        # Execute with specific error handling
        response = provider.execute(
            model='openai/gpt-4',
            prompt='What is 2+2?',
            system_prompt='You are a helpful assistant',
            parameters={
                'temperature': 0.7,
                'max_tokens': 100
            }
        )

        print(f"Success: {response}")

    except AuthenticationError as e:
        print(f"Authentication failed: {e}")
        print("  → Update your API key in configuration")

    except TimeoutError as e:
        print(f"Request timed out: {e}")
        print("  → Try again with longer timeout")

    except InvalidParameterError as e:
        print(f"Invalid parameters: {e}")
        print("  → Check your parameter names")

    except Exception as e:
        print(f"Provider error: {e}")


# ============================================================================
# EXAMPLE 2: Fallback Chain - Primary with Secondary Backup
# ============================================================================

def example_2_fallback_chain():
    """Use fallback chain for graceful degradation"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Fallback Chain (Primary → Secondary)")
    print("="*70 + "\n")

    from providers import (
        OpenRouterProviderEnhanced,
        OllamaProvider,
        FallbackProvider,
        AuthenticationError,
        TimeoutError
    )

    # Primary: OpenRouter (API-based)
    primary = OpenRouterProviderEnhanced({
        'api_key': 'your-openrouter-key',
        'timeout': 30
    })

    # Secondary: Ollama (Local fallback)
    secondary = OllamaProvider({
        'base_url': 'http://localhost:11434',
        'timeout': 300
    })

    # Create fallback chain
    chain = FallbackProvider(primary, secondary)

    try:
        # This tries primary first
        # If primary times out/errors → tries secondary
        # If primary auth fails → fails immediately (don't try secondary)
        response = chain.execute(
            model='gpt-4',
            prompt='Explain quantum computing',
            parameters={'temperature': 0.8}
        )

        print(f"Success: {response[:100]}...")
        print("  → Response from whichever provider succeeded first")

    except AuthenticationError:
        print("Authentication failed on all providers")
        print("  → Update your API credentials")

    except Exception as e:
        print(f"All providers failed: {e}")


# ============================================================================
# EXAMPLE 3: Three-Provider Fallback Chain
# ============================================================================

def example_3_three_provider_chain():
    """Ultimate fallback: Primary → Secondary → Tertiary"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Three-Provider Fallback Chain")
    print("="*70 + "\n")

    from providers import (
        create_provider,
        FallbackProvider
    )

    try:
        # Provider 1: Cloud API (best quality, may fail)
        primary = create_provider('openrouter', {
            'api_key': 'your-key'
        })

        # Provider 2: Local Ollama (good quality, medium latency)
        secondary = create_provider('ollama', {
            'base_url': 'http://localhost:11434'
        })

        # Provider 3: Local llama.cpp (always available, may be slower)
        tertiary = create_provider('llama-cpp', {
            'models_dir': '/path/to/models'
        })

        # Chain all three
        chain = FallbackProvider(primary, secondary, tertiary)

        # Get info about the chain
        info = chain.get_info()
        print(f"Chain configured with {info['provider_count']} providers:")
        for p in info['providers']:
            print(f"  [{p['position']}] {p['name']}")

        # Execute with complete fallback
        response = chain.execute(
            model='gpt-4',
            prompt='Your prompt here'
        )

        print(f"\nSuccess: Executed successfully on one of the providers")

    except Exception as e:
        print(f"All providers failed: {e}")


# ============================================================================
# EXAMPLE 4: Error Classification for Custom Retry Logic
# ============================================================================

def example_4_custom_retry_logic():
    """Implement custom retry logic based on error classification"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Custom Retry Logic Based on Error Type")
    print("="*70 + "\n")

    import time
    from providers import (
        OpenRouterProviderEnhanced,
        TimeoutError,
        RateLimitError,
        AuthenticationError,
        ServerError
    )

    provider = OpenRouterProviderEnhanced({'api_key': 'your-key'})

    def execute_with_retries(model, prompt, max_retries=3):
        """Execute with smart retry based on error type"""
        for attempt in range(max_retries):
            try:
                return provider.execute(model, prompt)

            except TimeoutError as e:
                if attempt < max_retries - 1:
                    wait = 2 ** attempt  # exponential backoff
                    print(f"Attempt {attempt+1} failed: Timeout")
                    print(f"  → Retrying in {wait}s...")
                    time.sleep(wait)
                else:
                    print(f"Failed after {max_retries} attempts: {e}")
                    raise

            except RateLimitError as e:
                print(f"Rate limited, waiting {e.retry_after}s...")
                time.sleep(e.retry_after)
                # Automatically retry

            except (AuthenticationError, InvalidParameterError):
                # Don't retry non-retryable errors
                print(f"Fatal error: {e}")
                raise

            except ServerError as e:
                if attempt < max_retries - 1:
                    print(f"Server error on attempt {attempt+1}")
                    print(f"  → Retrying...")
                    time.sleep(1)
                else:
                    raise

    try:
        response = execute_with_retries('gpt-4', 'Hello!')
        print(f"Success: {response}")
    except Exception as e:
        print(f"Failed: {e}")


# ============================================================================
# EXAMPLE 5: Parameter Validation
# ============================================================================

def example_5_parameter_validation():
    """Learn about parameter validation"""
    print("\n" + "="*70)
    print("EXAMPLE 5: Parameter Validation")
    print("="*70 + "\n")

    from providers import (
        OpenRouterProviderEnhanced,
        InvalidParameterError
    )

    provider = OpenRouterProviderEnhanced({'api_key': 'your-key'})

    # CORRECT: Valid parameters
    print("1. CORRECT: Valid parameters")
    try:
        response = provider.execute(
            'gpt-4',
            'Hello',
            parameters={
                'temperature': 0.7,
                'max_tokens': 100,
                'top_p': 0.9
            }
        )
        print("  ✓ Accepted")
    except Exception as e:
        print(f"  ✗ Error: {e}")

    # INCORRECT: Unknown parameter
    print("\n2. INCORRECT: Unknown parameter")
    try:
        response = provider.execute(
            'gpt-4',
            'Hello',
            parameters={
                'invalid_param': 123  # ← WRONG!
            }
        )
        print("  ✓ Accepted")
    except InvalidParameterError as e:
        print(f"  ✗ Error: {e}")
        print(f"  → Shows valid parameters in error message")

    # Show valid parameters
    print("\n3. Valid parameters for OpenRouter:")
    valid_params = [
        'temperature', 'temp',
        'top_p', 'max_tokens', 'max_length',
        'frequency_penalty', 'presence_penalty',
        'stop', 'n', 'seed'
    ]
    for param in valid_params:
        print(f"  • {param}")


# ============================================================================
# EXAMPLE 6: Provider Chain Information
# ============================================================================

def example_6_chain_information():
    """Get detailed information about a provider chain"""
    print("\n" + "="*70)
    print("EXAMPLE 6: Provider Chain Information")
    print("="*70 + "\n")

    from providers import (
        create_provider,
        FallbackProvider
    )

    primary = create_provider('openrouter', {'api_key': 'key'})
    secondary = create_provider('ollama', {'base_url': 'http://localhost:11434'})

    chain = FallbackProvider(primary, secondary)

    # Get detailed chain info
    info = chain.get_info()

    print(f"Chain Type: {info['type']}")
    print(f"Providers: {info['provider_count']}")
    print(f"\nFallback Strategy:")
    print(f"  Non-retryable: {info['fallback_strategy']['non_retryable']}")
    print(f"  Retryable: {info['fallback_strategy']['retryable']}")

    print(f"\nProviders in chain:")
    for p in info['providers']:
        print(f"  [{p['position']}] {p['name']}: {p.get('status', 'unknown')}")


# ============================================================================
# EXAMPLE 7: Streaming with Fallback
# ============================================================================

def example_7_streaming_with_fallback():
    """Use fallback chain with streaming responses"""
    print("\n" + "="*70)
    print("EXAMPLE 7: Streaming with Fallback Chain")
    print("="*70 + "\n")

    from providers import (
        create_provider,
        FallbackProvider,
        ProviderError
    )

    primary = create_provider('openrouter', {'api_key': 'key'})
    secondary = create_provider('ollama', {'base_url': 'http://localhost:11434'})

    chain = FallbackProvider(primary, secondary)

    try:
        print("Streaming response (falls back if primary fails):\n")

        # Stream from primary, fallback to secondary if needed
        for chunk in chain.stream_execute(
            'gpt-4',
            'Write a haiku about AI'
        ):
            print(chunk, end='', flush=True)

        print("\n\n✓ Stream completed successfully")

    except ProviderError as e:
        print(f"\n\n✗ Stream failed: {e}")


# ============================================================================
# RUN ALL EXAMPLES
# ============================================================================

def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("PROVIDER INTEGRATION: QUICK START EXAMPLES")
    print("="*70)

    examples = [
        ("1. Enhanced OpenRouter", example_1_enhanced_openrouter),
        ("2. Fallback Chain", example_2_fallback_chain),
        ("3. Three-Provider Chain", example_3_three_provider_chain),
        ("4. Custom Retry Logic", example_4_custom_retry_logic),
        ("5. Parameter Validation", example_5_parameter_validation),
        ("6. Chain Information", example_6_chain_information),
        ("7. Streaming with Fallback", example_7_streaming_with_fallback),
    ]

    print("\nAvailable examples:")
    for name, _ in examples:
        print(f"  • {name}")

    print("\nRunning examples...\n")

    for name, example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"\nNote: Example requires configuration")
            print(f"  → Update API keys and endpoints as needed")


if __name__ == "__main__":
    main()
    print("\n" + "="*70)
    print("For more information, see: PROVIDER-INTEGRATION-EXAMPLES.md")
    print("="*70 + "\n")
