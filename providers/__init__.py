"""
Provider Factory and Utilities

This module provides a unified interface for creating and managing
LLM providers across multiple backends.

Available Providers:
- LlamaCppProvider: Execute local GGUF models via llama.cpp
- OllamaProvider: Connect to Ollama for local model execution
- OpenRouterProvider: Access multiple providers via OpenRouter
- OpenAIProvider: Use OpenAI GPT models
- ClaudeProvider: Use Anthropic Claude models

Usage:
    from providers import create_provider, list_providers

    # Create provider
    provider = create_provider('openai', {'api_key': 'your-key'})

    # List available providers
    providers = list_providers()

    # Execute model
    response = provider.execute('gpt-4', 'Hello, world!')
"""

from typing import Dict, Any, Optional, List
import logging

# Import all providers
from .base_provider import LLMProvider
from .llama_cpp_provider import LlamaCppProvider
from .ollama_provider import OllamaProvider
from .openrouter_provider import OpenRouterProvider
from .openai_provider import OpenAIProvider
from .claude_provider import ClaudeProvider

# Configure logging
logger = logging.getLogger(__name__)

# Provider registry
PROVIDERS = {
    'llama-cpp': LlamaCppProvider,
    'llama.cpp': LlamaCppProvider,
    'llamacpp': LlamaCppProvider,
    'ollama': OllamaProvider,
    'openrouter': OpenRouterProvider,
    'openai': OpenAIProvider,
    'claude': ClaudeProvider,
    'anthropic': ClaudeProvider
}

# Provider aliases for convenience
PROVIDER_ALIASES = {
    'local': 'llama-cpp',
    'gguf': 'llama-cpp',
    'gpt': 'openai',
    'gpt-4': 'openai',
    'gpt-3.5': 'openai',
    'claude-3': 'claude',
    'sonnet': 'claude',
    'opus': 'claude',
    'haiku': 'claude'
}


def create_provider(
    provider_name: str,
    config: Optional[Dict[str, Any]] = None
) -> LLMProvider:
    """
    Create and initialize a provider.

    Args:
        provider_name: Name of the provider to create
        config: Provider configuration dictionary

    Returns:
        Initialized provider instance

    Raises:
        ValueError: If provider name is invalid

    Examples:
        # Create OpenAI provider
        provider = create_provider('openai', {'api_key': 'sk-...'})

        # Create local llama.cpp provider
        provider = create_provider('llama-cpp', {
            'models_dir': '/path/to/models'
        })

        # Create Ollama provider
        provider = create_provider('ollama', {
            'base_url': 'http://localhost:11434'
        })
    """
    if config is None:
        config = {}

    # Normalize provider name
    provider_key = provider_name.lower().strip()

    # Check aliases
    if provider_key in PROVIDER_ALIASES:
        provider_key = PROVIDER_ALIASES[provider_key]

    # Get provider class
    if provider_key not in PROVIDERS:
        available = ', '.join(sorted(set(list(PROVIDERS.keys()) + list(PROVIDER_ALIASES.keys()))))
        raise ValueError(
            f"Unknown provider: {provider_name}. "
            f"Available providers: {available}"
        )

    provider_class = PROVIDERS[provider_key]

    # Create and return provider
    logger.info(f"Creating provider: {provider_key}")
    return provider_class(config)


def list_providers() -> List[Dict[str, Any]]:
    """
    List all available providers with metadata.

    Returns:
        List of provider information dictionaries

    Example:
        [
            {
                "name": "llama-cpp",
                "class": "LlamaCppProvider",
                "description": "Execute local GGUF models",
                "aliases": ["local", "gguf"]
            },
            ...
        ]
    """
    providers = []

    # Get unique provider classes
    seen = set()
    for name, provider_class in PROVIDERS.items():
        if provider_class in seen:
            continue
        seen.add(provider_class)

        # Find aliases
        aliases = [
            alias for alias, target in PROVIDER_ALIASES.items()
            if target == name
        ]

        providers.append({
            "name": name,
            "class": provider_class.__name__,
            "description": provider_class.__doc__.split('\n')[1].strip() if provider_class.__doc__ else "",
            "aliases": aliases
        })

    return sorted(providers, key=lambda x: x['name'])


def get_provider_info(provider_name: str) -> Optional[Dict[str, Any]]:
    """
    Get detailed information about a specific provider.

    Args:
        provider_name: Name of the provider

    Returns:
        Provider information dictionary or None if not found

    Example:
        info = get_provider_info('openai')
        print(info['description'])
    """
    provider_key = provider_name.lower().strip()

    # Check aliases
    if provider_key in PROVIDER_ALIASES:
        provider_key = PROVIDER_ALIASES[provider_key]

    if provider_key not in PROVIDERS:
        return None

    provider_class = PROVIDERS[provider_key]

    # Find aliases
    aliases = [
        alias for alias, target in PROVIDER_ALIASES.items()
        if target == provider_key
    ]

    return {
        "name": provider_key,
        "class": provider_class.__name__,
        "description": provider_class.__doc__.split('\n')[1].strip() if provider_class.__doc__ else "",
        "aliases": aliases,
        "module": provider_class.__module__
    }


def validate_provider_config(
    provider_name: str,
    config: Dict[str, Any]
) -> tuple[bool, Optional[str]]:
    """
    Validate provider configuration without creating the provider.

    Args:
        provider_name: Name of the provider
        config: Configuration to validate

    Returns:
        Tuple of (is_valid, error_message)

    Example:
        valid, error = validate_provider_config('openai', {'api_key': 'sk-...'})
        if not valid:
            print(f"Config error: {error}")
    """
    try:
        provider = create_provider(provider_name, config)
        is_valid = provider.validate_config()

        if is_valid:
            return True, None
        else:
            return False, "Provider validation failed"

    except Exception as e:
        return False, str(e)


class ProviderManager:
    """
    Manages multiple providers and provides unified interface.

    Usage:
        manager = ProviderManager()

        # Add providers
        manager.add_provider('openai', {'api_key': 'sk-...'})
        manager.add_provider('claude', {'api_key': 'sk-ant-...'})
        manager.add_provider('ollama', {'base_url': 'http://localhost:11434'})

        # Execute on specific provider
        response = manager.execute('openai', 'gpt-4', 'Hello!')

        # Auto-select provider
        response = manager.auto_execute('gpt-4', 'Hello!')

        # List all available models across all providers
        models = manager.list_all_models()
    """

    def __init__(self):
        """Initialize provider manager."""
        self.providers: Dict[str, LLMProvider] = {}
        logger.info("ProviderManager initialized")

    def add_provider(
        self,
        name: str,
        config: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add a provider to the manager.

        Args:
            name: Provider name
            config: Provider configuration

        Returns:
            True if successful
        """
        try:
            provider = create_provider(name, config)
            self.providers[name] = provider
            logger.info(f"Added provider: {name}")
            return True

        except Exception as e:
            logger.error(f"Failed to add provider {name}: {e}")
            return False

    def remove_provider(self, name: str) -> bool:
        """
        Remove a provider from the manager.

        Args:
            name: Provider name

        Returns:
            True if successful
        """
        if name in self.providers:
            del self.providers[name]
            logger.info(f"Removed provider: {name}")
            return True
        return False

    def get_provider(self, name: str) -> Optional[LLMProvider]:
        """
        Get a provider by name.

        Args:
            name: Provider name

        Returns:
            Provider instance or None
        """
        return self.providers.get(name)

    def list_providers(self) -> List[str]:
        """
        List all registered provider names.

        Returns:
            List of provider names
        """
        return list(self.providers.keys())

    def execute(
        self,
        provider_name: str,
        model: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Execute on a specific provider.

        Args:
            provider_name: Provider to use
            model: Model identifier
            prompt: User prompt
            system_prompt: Optional system prompt
            parameters: Model parameters

        Returns:
            Model response
        """
        provider = self.get_provider(provider_name)
        if not provider:
            raise ValueError(f"Provider not found: {provider_name}")

        return provider.execute(model, prompt, system_prompt, parameters)

    def auto_execute(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Automatically select provider based on model name.

        Args:
            model: Model identifier
            prompt: User prompt
            system_prompt: Optional system prompt
            parameters: Model parameters

        Returns:
            Model response
        """
        # Detect provider from model name
        model_lower = model.lower()

        if 'gpt' in model_lower or 'openai' in model_lower:
            provider_name = 'openai'
        elif 'claude' in model_lower or 'anthropic' in model_lower:
            provider_name = 'claude'
        elif 'ollama' in model_lower:
            provider_name = 'ollama'
        else:
            # Default to first available provider
            if not self.providers:
                raise ValueError("No providers available")
            provider_name = list(self.providers.keys())[0]

        return self.execute(provider_name, model, prompt, system_prompt, parameters)

    def list_all_models(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        List all models from all providers.

        Returns:
            Dictionary mapping provider names to model lists
        """
        all_models = {}

        for name, provider in self.providers.items():
            try:
                models = provider.list_models()
                all_models[name] = models
            except Exception as e:
                logger.error(f"Failed to list models for {name}: {e}")
                all_models[name] = []

        return all_models

    def get_all_info(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information for all providers.

        Returns:
            Dictionary mapping provider names to info
        """
        all_info = {}

        for name, provider in self.providers.items():
            try:
                info = provider.get_info()
                all_info[name] = info
            except Exception as e:
                logger.error(f"Failed to get info for {name}: {e}")
                all_info[name] = {"status": "error", "error": str(e)}

        return all_info


# Convenience exports
__all__ = [
    'LLMProvider',
    'LlamaCppProvider',
    'OllamaProvider',
    'OpenRouterProvider',
    'OpenAIProvider',
    'ClaudeProvider',
    'create_provider',
    'list_providers',
    'get_provider_info',
    'validate_provider_config',
    'ProviderManager',
    'PROVIDERS',
    'PROVIDER_ALIASES'
]
