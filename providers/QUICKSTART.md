# Provider Integration - Quick Start Guide

Get started with the LLM provider system in 5 minutes!

## Installation

```bash
# Install dependencies
pip install requests

# Or use requirements file
cd D:\models\providers
pip install -r requirements.txt
```

## Quick Examples

### 1. Local Models (llama.cpp)

```python
from providers import create_provider

# Create provider
provider = create_provider('llama-cpp', {
    'models_dir': '/mnt/d/models/organized'
})

# List available models
models = provider.list_models()
print(f"Found {len(models)} models")

# Execute
response = provider.execute(
    model='qwen3-coder-30b',
    prompt='Write a hello world function',
    parameters={'temperature': 0.7}
)
print(response)
```

### 2. Ollama

```bash
# First, start Ollama server
ollama serve
```

```python
from providers import create_provider

provider = create_provider('ollama')

# Pull a model (if needed)
provider.pull_model('mistral')

# Execute
response = provider.execute(
    model='mistral',
    prompt='Explain Python in one sentence'
)
print(response)
```

### 3. OpenAI

```bash
# Set API key
export OPENAI_API_KEY="sk-..."
```

```python
import os
from providers import create_provider

provider = create_provider('openai', {
    'api_key': os.getenv('OPENAI_API_KEY')
})

# Execute
response = provider.execute(
    model='gpt-3.5-turbo',
    prompt='Say hello in 5 words',
    parameters={'max_tokens': 20}
)
print(response)

# Streaming
for chunk in provider.stream_execute('gpt-3.5-turbo', 'Count to 5'):
    print(chunk, end='', flush=True)
```

### 4. Claude

```bash
# Set API key
export ANTHROPIC_API_KEY="sk-ant-..."
```

```python
import os
from providers import create_provider

provider = create_provider('claude', {
    'api_key': os.getenv('ANTHROPIC_API_KEY')
})

# Execute
response = provider.execute(
    model='claude-3-haiku-20240307',
    prompt='Explain AI in simple terms',
    parameters={'max_tokens': 100}
)
print(response)
```

### 5. OpenRouter (Multi-Provider)

```bash
# Set API key
export OPENROUTER_API_KEY="sk-or-..."
```

```python
import os
from providers import create_provider

provider = create_provider('openrouter', {
    'api_key': os.getenv('OPENROUTER_API_KEY')
})

# Search for models
coding_models = provider.search_models(query='coding')

# Execute on any model
response = provider.execute(
    model='openai/gpt-4',
    prompt='Write a sorting algorithm'
)
print(response)

# Check credits
credits = provider.get_credits()
print(f"Credits remaining: {credits['credits']}")
```

## Using Provider Manager

```python
from providers import ProviderManager
import os

# Create manager
manager = ProviderManager()

# Add providers
manager.add_provider('llama-cpp', {
    'models_dir': '/mnt/d/models/organized'
})

manager.add_provider('openai', {
    'api_key': os.getenv('OPENAI_API_KEY')
})

manager.add_provider('ollama')

# List providers
print("Providers:", manager.list_providers())

# Execute on specific provider
response = manager.execute('openai', 'gpt-3.5-turbo', 'Hello!')

# Auto-select provider based on model
response = manager.auto_execute('gpt-4', 'Hello!')  # Uses OpenAI
response = manager.auto_execute('mistral', 'Hello!')  # Uses Ollama

# Get all models
all_models = manager.list_all_models()
for provider_name, models in all_models.items():
    print(f"{provider_name}: {len(models)} models")
```

## Common Patterns

### Pattern 1: Try Cloud, Fallback to Local

```python
from providers import ProviderManager

manager = ProviderManager()
manager.add_provider('openai', {'api_key': os.getenv('OPENAI_API_KEY')})
manager.add_provider('ollama')

def execute_with_fallback(prompt):
    try:
        # Try cloud first
        return manager.execute('openai', 'gpt-3.5-turbo', prompt)
    except Exception as e:
        print(f"Cloud failed: {e}, using local...")
        # Fallback to local
        return manager.execute('ollama', 'mistral', prompt)
```

### Pattern 2: Cost-Aware Routing

```python
def smart_route(prompt, complexity='simple'):
    if complexity == 'simple':
        # Use cheap/fast model
        return manager.execute('ollama', 'mistral', prompt)
    elif complexity == 'medium':
        return manager.execute('openai', 'gpt-3.5-turbo', prompt)
    else:
        # Use most powerful
        return manager.execute('openai', 'gpt-4', prompt)
```

### Pattern 3: Streaming with Progress

```python
def stream_with_progress(provider, model, prompt):
    print("Response: ", end='', flush=True)
    char_count = 0

    for chunk in provider.stream_execute(model, prompt):
        print(chunk, end='', flush=True)
        char_count += len(chunk)

        # Show progress every 100 chars
        if char_count % 100 == 0:
            print(f"\n[{char_count} chars]", end='', flush=True)

    print(f"\n\nTotal: {char_count} characters")
```

### Pattern 4: Parallel Comparison

```python
import concurrent.futures

def compare_providers(prompt):
    manager = ProviderManager()
    manager.add_provider('openai', {'api_key': os.getenv('OPENAI_API_KEY')})
    manager.add_provider('claude', {'api_key': os.getenv('ANTHROPIC_API_KEY')})

    def get_response(provider_name, model):
        return manager.execute(provider_name, model, prompt)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(get_response, 'openai', 'gpt-4'): 'OpenAI',
            executor.submit(get_response, 'claude', 'claude-3-opus-20240229'): 'Claude'
        }

        for future in concurrent.futures.as_completed(futures):
            provider_name = futures[future]
            response = future.result()
            print(f"\n{provider_name} Response:\n{response}\n")
```

## Testing Your Setup

```python
from providers import create_provider, list_providers

# 1. List available providers
print("Available providers:")
for p in list_providers():
    print(f"  - {p['name']}: {p['description']}")

# 2. Test local provider
try:
    provider = create_provider('llama-cpp')
    if provider.validate_config():
        print("✓ llama.cpp is ready")
    else:
        print("✗ llama.cpp not configured")
except Exception as e:
    print(f"✗ llama.cpp error: {e}")

# 3. Test Ollama
try:
    provider = create_provider('ollama')
    if provider.validate_config():
        print("✓ Ollama is ready")
    else:
        print("✗ Ollama not running")
except Exception as e:
    print(f"✗ Ollama error: {e}")

# 4. Test OpenAI
if os.getenv('OPENAI_API_KEY'):
    try:
        provider = create_provider('openai', {
            'api_key': os.getenv('OPENAI_API_KEY')
        })
        if provider.validate_config():
            print("✓ OpenAI is ready")
        else:
            print("✗ OpenAI API key invalid")
    except Exception as e:
        print(f"✗ OpenAI error: {e}")
else:
    print("✗ OPENAI_API_KEY not set")
```

## Environment Setup

Create a `.env` file:

```bash
# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_ORG_ID=org-...

# Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-...

# OpenRouter
OPENROUTER_API_KEY=sk-or-...

# Ollama (if remote)
OLLAMA_BASE_URL=http://localhost:11434
```

Load in Python:

```python
from dotenv import load_dotenv
import os

load_dotenv()

# Now use os.getenv() to access keys
```

## Common Parameters

All providers support these parameters (with auto-normalization):

```python
parameters = {
    'temperature': 0.7,      # Randomness (0.0-2.0)
    'top_p': 0.9,           # Nucleus sampling (0.0-1.0)
    'top_k': 40,            # Top-k sampling
    'max_tokens': 2000,     # Max response length
    'stop': ['\n\n'],       # Stop sequences
    'seed': 42              # Random seed (reproducibility)
}
```

## Error Handling

```python
from providers import create_provider

try:
    provider = create_provider('openai', {
        'api_key': 'invalid-key'
    })
    response = provider.execute('gpt-4', 'Hello')
except ValueError as e:
    print(f"Configuration error: {e}")
except RuntimeError as e:
    print(f"API error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Next Steps

1. Read the [full documentation](README.md)
2. Run the [example script](example_usage.py)
3. Check provider-specific features in README
4. Integrate into your AI Router

## Getting Help

- Check README.md for detailed documentation
- Run example_usage.py to see all providers in action
- Enable debug logging: `logging.basicConfig(level=logging.DEBUG)`
- Validate configuration: `provider.validate_config()`
- Check provider info: `provider.get_info()`

## Useful Commands

```bash
# Test imports
python -c "from providers import list_providers; print(list_providers())"

# Run examples
python providers/example_usage.py

# Check Ollama status
curl http://localhost:11434/api/version

# List Ollama models
ollama list

# Test llama.cpp
wsl ~/llama.cpp/build/bin/llama-cli --help
```

## Summary

You now have access to:
- 5 different LLM providers
- Unified interface for all
- Streaming support
- Automatic parameter normalization
- Provider manager for multi-provider apps
- Comprehensive error handling

Start building!
