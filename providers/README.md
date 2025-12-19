# LLM Provider Integration System

A comprehensive, modular provider system for integrating multiple LLM backends into your AI Router application.

## Overview

This provider system offers a unified interface to interact with various LLM providers, both local and cloud-based. All providers implement a common abstract base class, ensuring consistent behavior across different backends.

## Available Providers

### 1. Llama.cpp Provider (Local)
Execute local GGUF models via llama.cpp in WSL or native Linux.

**Features:**
- Full GPU offload support
- Flash Attention optimization
- KV cache quantization
- System prompts
- Streaming responses
- WSL auto-detection

**Configuration:**
```python
from providers import create_provider

provider = create_provider('llama-cpp', {
    'llama_cpp_path': '~/llama.cpp/build/bin/llama-cli',
    'models_dir': '/mnt/d/models/organized',
    'default_threads': 24,
    'default_gpu_layers': 999
})
```

**Usage:**
```python
response = provider.execute(
    model='qwen3-coder-30b',
    prompt='Write a Python function to sort a list',
    system_prompt='You are an expert Python developer',
    parameters={
        'temperature': 0.7,
        'top_p': 0.9,
        'max_tokens': 2048,
        'special_flags': ['--jinja']
    }
)
```

### 2. Ollama Provider (Local)
Connect to local or remote Ollama instance.

**Features:**
- Model discovery via ollama list
- Model pull/download
- Model deletion
- Chat completions
- Streaming responses
- System prompts

**Configuration:**
```python
provider = create_provider('ollama', {
    'base_url': 'http://localhost:11434',
    'timeout': 300
})
```

**Usage:**
```python
# List available models
models = provider.list_models()

# Execute model
response = provider.execute(
    model='mistral',
    prompt='Explain quantum computing',
    parameters={'temperature': 0.7}
)

# Pull a new model
provider.pull_model('llama2')

# Chat completion
response = provider.chat_execute(
    model='mistral',
    messages=[
        {"role": "system", "content": "You are helpful"},
        {"role": "user", "content": "Hello!"}
    ],
    stream=False
)
```

### 3. OpenRouter Provider (Cloud)
Access multiple providers through OpenRouter API.

**Features:**
- Unified access to 100+ models
- OpenAI, Anthropic, Google, Meta models
- Cost tracking
- Model search
- Credit management
- Streaming responses

**Configuration:**
```python
provider = create_provider('openrouter', {
    'api_key': 'your-openrouter-key',
    'app_name': 'AI-Router',
    'app_url': 'https://github.com/yourusername/ai-router'
})
```

**Usage:**
```python
# List all models with pricing
models = provider.list_models()

# Execute model
response = provider.execute(
    model='openai/gpt-4',
    prompt='Explain machine learning',
    parameters={'temperature': 0.7, 'max_tokens': 1000}
)

# Search for models
coding_models = provider.search_models(query='coding', provider='openai')

# Check credits
credits = provider.get_credits()
print(f"Remaining credits: {credits['credits']}")
```

### 4. OpenAI Provider (Cloud)
Direct OpenAI API integration.

**Features:**
- GPT-4 and GPT-3.5 models
- Function calling
- Vision (GPT-4V)
- Image generation (DALL-E)
- Embeddings
- Content moderation
- JSON mode

**Configuration:**
```python
provider = create_provider('openai', {
    'api_key': 'sk-...',
    'organization': 'org-...',  # Optional
    'timeout': 300
})
```

**Usage:**
```python
# Chat completion
response = provider.execute(
    model='gpt-4',
    prompt='Write a story about AI',
    system_prompt='You are a creative writer',
    parameters={'temperature': 0.9, 'max_tokens': 2000}
)

# Create embedding
embedding = provider.create_embedding('Hello world')

# Generate image
image_urls = provider.create_image(
    prompt='A cat wearing a space suit',
    model='dall-e-3',
    size='1024x1024'
)

# Moderate content
result = provider.moderate_content('Some text to check')
```

### 5. Claude Provider (Cloud)
Anthropic Claude API integration.

**Features:**
- Claude 3 models (Opus, Sonnet, Haiku)
- 200K context window
- Vision capabilities
- System prompts
- Streaming responses
- Constitutional AI

**Configuration:**
```python
provider = create_provider('claude', {
    'api_key': 'sk-ant-...',
    'api_version': '2023-06-01'
})
```

**Usage:**
```python
# Chat completion
response = provider.execute(
    model='claude-3-opus-20240229',
    prompt='Analyze this code for security issues',
    system_prompt='You are a security expert',
    parameters={'temperature': 0.7, 'max_tokens': 4096}
)

# Vision
response = provider.execute_with_vision(
    model='claude-3-sonnet-20240229',
    prompt='What is in this image?',
    image_url='https://example.com/image.jpg'
)

# Estimate tokens
token_count = provider.count_tokens('Some text')
```

## Provider Factory

The provider factory simplifies provider creation and management.

### Creating Providers

```python
from providers import create_provider

# Simple creation
provider = create_provider('openai', {'api_key': 'sk-...'})

# With aliases
provider = create_provider('gpt', {'api_key': 'sk-...'})  # Creates OpenAI

# List available providers
from providers import list_providers
providers = list_providers()
for p in providers:
    print(f"{p['name']}: {p['description']}")
```

### Provider Manager

Manage multiple providers simultaneously:

```python
from providers import ProviderManager

# Create manager
manager = ProviderManager()

# Add providers
manager.add_provider('openai', {'api_key': 'sk-...'})
manager.add_provider('claude', {'api_key': 'sk-ant-...'})
manager.add_provider('ollama', {'base_url': 'http://localhost:11434'})

# Execute on specific provider
response = manager.execute('openai', 'gpt-4', 'Hello!')

# Auto-select provider based on model name
response = manager.auto_execute('claude-3-opus-20240229', 'Hello!')

# List all models from all providers
all_models = manager.list_all_models()
for provider_name, models in all_models.items():
    print(f"{provider_name}: {len(models)} models")

# Get info from all providers
all_info = manager.get_all_info()
```

## Common Interface

All providers implement the same base interface:

### Core Methods

```python
# List available models
models = provider.list_models()

# Execute model (non-streaming)
response = provider.execute(
    model='model-name',
    prompt='Your prompt',
    system_prompt='Optional system prompt',
    parameters={'temperature': 0.7}
)

# Execute with streaming
for chunk in provider.stream_execute(
    model='model-name',
    prompt='Your prompt',
    parameters={'temperature': 0.7}
):
    print(chunk, end='', flush=True)

# Validate configuration
is_valid = provider.validate_config()

# Get provider info
info = provider.get_info()
print(f"Status: {info['status']}")
print(f"Capabilities: {info['capabilities']}")
```

### Parameter Normalization

Each provider automatically normalizes common parameters:

```python
# These are all equivalent
parameters = {
    'temperature': 0.7,      # Standard
    'temp': 0.7,            # Alias

    'top_p': 0.9,           # Standard
    'nucleus_sampling': 0.9, # Alias

    'max_tokens': 2000,     # Standard
    'max_length': 2000,     # Alias

    'context': 32768,       # Standard
    'context_length': 32768, # Alias
    'ctx_size': 32768       # Alias
}
```

## Error Handling

All providers use consistent error handling:

```python
from providers import create_provider

try:
    provider = create_provider('openai', {'api_key': 'invalid'})
    response = provider.execute('gpt-4', 'Hello!')
except ValueError as e:
    print(f"Configuration error: {e}")
except RuntimeError as e:
    print(f"Execution error: {e}")
```

## Examples

### Example 1: Multi-Provider Comparison

```python
from providers import ProviderManager

manager = ProviderManager()
manager.add_provider('openai', {'api_key': 'sk-...'})
manager.add_provider('claude', {'api_key': 'sk-ant-...'})

prompt = "Explain quantum entanglement"

# Compare responses
openai_response = manager.execute('openai', 'gpt-4', prompt)
claude_response = manager.execute('claude', 'claude-3-opus-20240229', prompt)

print("OpenAI:", openai_response)
print("\nClaude:", claude_response)
```

### Example 2: Streaming Response

```python
from providers import create_provider

provider = create_provider('openai', {'api_key': 'sk-...'})

print("Response: ", end='', flush=True)
for chunk in provider.stream_execute('gpt-4', 'Write a haiku about AI'):
    print(chunk, end='', flush=True)
print()
```

### Example 3: Local + Cloud Hybrid

```python
from providers import ProviderManager

manager = ProviderManager()

# Add local provider for fast tasks
manager.add_provider('ollama', {'base_url': 'http://localhost:11434'})

# Add cloud provider for complex tasks
manager.add_provider('openai', {'api_key': 'sk-...'})

# Use local for simple query
simple_response = manager.execute('ollama', 'mistral', 'What is 2+2?')

# Use cloud for complex reasoning
complex_response = manager.execute('openai', 'gpt-4',
    'Explain the philosophical implications of AI consciousness')
```

### Example 4: Model Search and Selection

```python
from providers import create_provider

provider = create_provider('openrouter', {'api_key': 'your-key'})

# Search for coding models
coding_models = provider.search_models(query='coding', provider='openai')

# Find cheapest model
cheapest = min(coding_models, key=lambda m: m['pricing']['prompt'])
print(f"Cheapest coding model: {cheapest['name']}")

# Use the selected model
response = provider.execute(cheapest['id'], 'Write a sorting algorithm')
```

## Configuration Best Practices

### 1. Use Environment Variables

```python
import os
from providers import create_provider

provider = create_provider('openai', {
    'api_key': os.getenv('OPENAI_API_KEY'),
    'organization': os.getenv('OPENAI_ORG_ID')
})
```

### 2. Validate Configuration

```python
from providers import validate_provider_config

config = {'api_key': 'sk-...'}
valid, error = validate_provider_config('openai', config)

if not valid:
    print(f"Invalid config: {error}")
```

### 3. Use Config Files

```python
import json
from providers import create_provider

# Load config from file
with open('providers.json', 'r') as f:
    configs = json.load(f)

# Create providers
openai_provider = create_provider('openai', configs['openai'])
claude_provider = create_provider('claude', configs['claude'])
```

Example `providers.json`:
```json
{
  "openai": {
    "api_key": "sk-...",
    "timeout": 300
  },
  "claude": {
    "api_key": "sk-ant-...",
    "timeout": 300
  },
  "ollama": {
    "base_url": "http://localhost:11434"
  },
  "llama-cpp": {
    "models_dir": "/mnt/d/models/organized",
    "default_threads": 24,
    "default_gpu_layers": 999
  }
}
```

## Logging

All providers use Python's logging module:

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Or configure per-provider
logger = logging.getLogger('providers.openai_provider')
logger.setLevel(logging.INFO)
```

## Testing

Test provider connectivity:

```python
from providers import create_provider

provider = create_provider('openai', {'api_key': 'sk-...'})

# Validate configuration
if provider.validate_config():
    print("Provider is ready!")

    # Get info
    info = provider.get_info()
    print(f"Status: {info['status']}")
    print(f"Available models: {info['available_models']}")
else:
    print("Provider validation failed")
```

## Advanced Features

### Custom Headers (OpenAI/Claude)

```python
provider = create_provider('openai', {
    'api_key': 'sk-...',
    'custom_headers': {
        'X-Custom-Header': 'value'
    }
})
```

### Timeout Configuration

```python
provider = create_provider('claude', {
    'api_key': 'sk-ant-...',
    'timeout': 600  # 10 minutes for long responses
})
```

### SSL Verification (Ollama)

```python
provider = create_provider('ollama', {
    'base_url': 'https://remote-ollama:11434',
    'verify_ssl': False  # Disable for self-signed certs
})
```

## Troubleshooting

### Common Issues

1. **API Key Invalid**
   - Verify key is correct
   - Check environment variables
   - Use `validate_config()` to test

2. **Model Not Found**
   - Use `list_models()` to see available models
   - Check model name spelling
   - Ensure provider supports the model

3. **Timeout Errors**
   - Increase timeout in config
   - Check network connectivity
   - Try smaller max_tokens

4. **WSL Path Issues (llama.cpp)**
   - Ensure paths use WSL format: `/mnt/d/...`
   - Check llama.cpp binary is executable
   - Verify model files exist

### Debug Mode

Enable verbose logging:

```python
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## Integration with AI Router

The providers integrate seamlessly with the AI Router:

```python
from providers import create_provider, ProviderManager

class AIRouter:
    def __init__(self):
        self.provider_manager = ProviderManager()

        # Add providers
        self.provider_manager.add_provider('llama-cpp', {
            'models_dir': '/mnt/d/models/organized'
        })
        self.provider_manager.add_provider('openai', {
            'api_key': os.getenv('OPENAI_API_KEY')
        })

    def route_request(self, prompt, use_case):
        if use_case == 'coding':
            # Use local model for coding
            return self.provider_manager.execute(
                'llama-cpp',
                'qwen3-coder-30b',
                prompt
            )
        else:
            # Use cloud for general tasks
            return self.provider_manager.execute(
                'openai',
                'gpt-4',
                prompt
            )
```

## License

This provider system is part of the AI Router project.

## Support

For issues, questions, or contributions, please see the main AI Router documentation.

---

**Quick Reference:**

- **Local Models**: Use `llama-cpp` or `ollama`
- **Cloud APIs**: Use `openai`, `claude`, or `openrouter`
- **Multi-Provider Access**: Use `openrouter`
- **Cost Tracking**: Use `openrouter` or check individual provider usage
- **Vision**: Use `claude` (Claude 3) or `openai` (GPT-4V)
- **Function Calling**: Use `openai`
- **Extended Context**: Use `claude` (200K) or local models

**Provider Comparison:**

| Provider | Type | Cost | Context | Speed | Capabilities |
|----------|------|------|---------|-------|--------------|
| llama-cpp | Local | Free | Up to 256K | Fast | Local execution, GPU offload |
| ollama | Local | Free | Varies | Fast | Easy model management |
| openai | Cloud | $$$ | 128K | Fast | Function calling, vision, images |
| claude | Cloud | $$$ | 200K | Fast | Extended context, vision |
| openrouter | Cloud | $ | Varies | Varies | Access to 100+ models |
