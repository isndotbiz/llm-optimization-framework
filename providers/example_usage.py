#!/usr/bin/env python3
"""
Provider Integration Examples

Demonstrates how to use the LLM provider system with various backends.
"""

import os
import sys
from pathlib import Path

# Add providers directory to path
sys.path.insert(0, str(Path(__file__).parent))

from providers import (
    create_provider,
    list_providers,
    ProviderManager,
    validate_provider_config
)


def example_1_list_providers():
    """Example 1: List all available providers"""
    print("=" * 70)
    print("EXAMPLE 1: List Available Providers")
    print("=" * 70)

    providers = list_providers()
    for provider in providers:
        print(f"\nProvider: {provider['name']}")
        print(f"  Class: {provider['class']}")
        print(f"  Description: {provider['description']}")
        if provider['aliases']:
            print(f"  Aliases: {', '.join(provider['aliases'])}")


def example_2_llama_cpp():
    """Example 2: Use llama.cpp provider for local models"""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Llama.cpp Provider (Local Models)")
    print("=" * 70)

    try:
        provider = create_provider('llama-cpp', {
            'models_dir': '/mnt/d/models/organized',
            'default_threads': 24,
            'default_gpu_layers': 999
        })

        print("\nProvider Info:")
        info = provider.get_info()
        for key, value in info.items():
            print(f"  {key}: {value}")

        print("\nAvailable Models:")
        models = provider.list_models()
        for model in models[:5]:  # Show first 5 models
            print(f"  - {model['name']} ({model['size']})")

        # Example execution (commented out to avoid actually running)
        # response = provider.execute(
        #     model='qwen3-coder-30b',
        #     prompt='Write a hello world function in Python',
        #     parameters={'temperature': 0.7, 'max_tokens': 100}
        # )
        # print(f"\nResponse: {response}")

    except Exception as e:
        print(f"Error: {e}")


def example_3_ollama():
    """Example 3: Use Ollama provider"""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Ollama Provider")
    print("=" * 70)

    try:
        provider = create_provider('ollama', {
            'base_url': 'http://localhost:11434'
        })

        # Validate configuration
        if provider.validate_config():
            print("Ollama server is accessible!")

            info = provider.get_info()
            print(f"Status: {info['status']}")
            print(f"Available models: {info['available_models']}")

            # List models
            models = provider.list_models()
            if models:
                print("\nModels:")
                for model in models[:5]:
                    print(f"  - {model['name']} ({model['size']})")
        else:
            print("Ollama server is not accessible")
            print("Make sure Ollama is running: ollama serve")

    except Exception as e:
        print(f"Error: {e}")


def example_4_openai():
    """Example 4: Use OpenAI provider"""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: OpenAI Provider")
    print("=" * 70)

    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("OPENAI_API_KEY environment variable not set")
        print("Set it with: export OPENAI_API_KEY='sk-...'")
        return

    try:
        provider = create_provider('openai', {
            'api_key': api_key
        })

        if provider.validate_config():
            print("OpenAI API key is valid!")

            info = provider.get_info()
            print(f"Status: {info['status']}")

            # Example execution (commented to avoid API charges)
            # response = provider.execute(
            #     model='gpt-3.5-turbo',
            #     prompt='Say hello in 5 words or less',
            #     parameters={'temperature': 0.7, 'max_tokens': 20}
            # )
            # print(f"\nResponse: {response}")
        else:
            print("Invalid OpenAI API key")

    except Exception as e:
        print(f"Error: {e}")


def example_5_claude():
    """Example 5: Use Claude provider"""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Claude Provider")
    print("=" * 70)

    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("ANTHROPIC_API_KEY environment variable not set")
        print("Set it with: export ANTHROPIC_API_KEY='sk-ant-...'")
        return

    try:
        provider = create_provider('claude', {
            'api_key': api_key
        })

        print("Available Claude models:")
        models = provider.list_models()
        for model in models:
            print(f"  - {model['name']}")
            print(f"    Context: {model['context_length']:,} tokens")

        # Example execution (commented to avoid API charges)
        # response = provider.execute(
        #     model='claude-3-haiku-20240307',
        #     prompt='Say hello in 5 words or less',
        #     parameters={'temperature': 0.7, 'max_tokens': 20}
        # )
        # print(f"\nResponse: {response}")

    except Exception as e:
        print(f"Error: {e}")


def example_6_provider_manager():
    """Example 6: Use ProviderManager for multiple providers"""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Provider Manager")
    print("=" * 70)

    manager = ProviderManager()

    # Add llama.cpp provider
    if manager.add_provider('llama-cpp', {
        'models_dir': '/mnt/d/models/organized'
    }):
        print("Added llama-cpp provider")

    # Add Ollama provider
    if manager.add_provider('ollama', {
        'base_url': 'http://localhost:11434'
    }):
        print("Added Ollama provider")

    # Add OpenAI if API key available
    if os.getenv('OPENAI_API_KEY'):
        if manager.add_provider('openai', {
            'api_key': os.getenv('OPENAI_API_KEY')
        }):
            print("Added OpenAI provider")

    # List registered providers
    print(f"\nRegistered providers: {', '.join(manager.list_providers())}")

    # Get info from all providers
    print("\nProvider Status:")
    all_info = manager.get_all_info()
    for name, info in all_info.items():
        status = info.get('status', 'unknown')
        models = info.get('available_models', 0)
        print(f"  {name}: {status} ({models} models)")


def example_7_streaming():
    """Example 7: Streaming responses"""
    print("\n" + "=" * 70)
    print("EXAMPLE 7: Streaming Responses")
    print("=" * 70)

    print("Streaming is supported by all providers.")
    print("\nExample code:")
    print("""
    provider = create_provider('openai', {'api_key': 'sk-...'})

    print("Response: ", end='', flush=True)
    for chunk in provider.stream_execute('gpt-3.5-turbo', 'Tell me a joke'):
        print(chunk, end='', flush=True)
    print()
    """)


def example_8_parameter_normalization():
    """Example 8: Parameter normalization"""
    print("\n" + "=" * 70)
    print("EXAMPLE 8: Parameter Normalization")
    print("=" * 70)

    print("All providers normalize common parameter names:")
    print("\nEquivalent parameter names:")
    print("  temperature = temp")
    print("  top_p = nucleus_sampling")
    print("  max_tokens = max_length")
    print("  context = context_length = ctx_size")

    print("\nExample:")
    print("""
    # These are all equivalent:
    parameters1 = {'temperature': 0.7, 'max_tokens': 2000}
    parameters2 = {'temp': 0.7, 'max_length': 2000}

    # Both work with any provider
    response1 = provider.execute(model, prompt, parameters=parameters1)
    response2 = provider.execute(model, prompt, parameters=parameters2)
    """)


def example_9_validation():
    """Example 9: Configuration validation"""
    print("\n" + "=" * 70)
    print("EXAMPLE 9: Configuration Validation")
    print("=" * 70)

    # Test invalid config
    print("Testing invalid OpenAI config...")
    valid, error = validate_provider_config('openai', {
        'api_key': 'invalid-key'
    })
    print(f"  Valid: {valid}")
    if error:
        print(f"  Error: {error}")

    # Test Ollama config
    print("\nTesting Ollama config...")
    valid, error = validate_provider_config('ollama', {
        'base_url': 'http://localhost:11434'
    })
    print(f"  Valid: {valid}")
    if error:
        print(f"  Error: {error}")


def main():
    """Run all examples"""
    print("\n" + "=" * 70)
    print("LLM PROVIDER INTEGRATION EXAMPLES")
    print("=" * 70)

    examples = [
        example_1_list_providers,
        example_2_llama_cpp,
        example_3_ollama,
        example_4_openai,
        example_5_claude,
        example_6_provider_manager,
        example_7_streaming,
        example_8_parameter_normalization,
        example_9_validation
    ]

    for example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"\nError in {example_func.__name__}: {e}")

    print("\n" + "=" * 70)
    print("Examples completed!")
    print("=" * 70)
    print("\nTo use these providers:")
    print("  1. Install dependencies: pip install requests")
    print("  2. Set API keys as environment variables")
    print("  3. Ensure local services (Ollama, llama.cpp) are running")
    print("  4. Import and use providers in your code")
    print("\nSee README.md for detailed documentation.")


if __name__ == "__main__":
    main()
