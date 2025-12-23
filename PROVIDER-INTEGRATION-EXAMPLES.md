# Provider Error Classification & Fallback Chains

Complete implementation of intelligent error handling and provider fallback chains for the AI Router system.

## Overview

This implementation adds:
1. **Error Classification** - Specific exception types instead of generic RuntimeError
2. **Fallback Chains** - Intelligent provider fallback on retryable errors
3. **Parameter Validation** - Strict validation with helpful error messages
4. **No Breaking Changes** - Backward compatible with existing code

## Files Created/Modified

### New Files

1. **`providers/provider_errors.py`** (168 lines)
   - Error hierarchy with 9 error types
   - `classify_error()` function for automatic classification
   - Retryable/non-retryable status for each error type

2. **`providers/openrouter_provider_enhanced.py`** (534 lines)
   - Enhanced OpenRouter provider with error classification
   - Parameter validation
   - Specific error types instead of generic RuntimeError

3. **`providers/fallback_provider.py`** (349 lines)
   - FallbackProvider class managing multiple providers
   - Intelligent retry logic based on error type
   - Chain up to 3 providers (primary, secondary, tertiary)

4. **`providers/test_error_classification.py`** (353 lines)
   - Comprehensive test suite
   - 8 test functions covering all scenarios
   - Mock providers for testing

### Modified Files

1. **`providers/base_provider.py`**
   - Added `validate_parameters()` method for strict validation

2. **`providers/__init__.py`**
   - Exported error classes and new providers
   - Added convenience imports

## Error Hierarchy

```
ProviderError (base)
├── AuthenticationError (401/403) - NOT retryable
├── TimeoutError - RETRYABLE
├── RateLimitError (429) - RETRYABLE with retry_after
├── InvalidParameterError (400) - NOT retryable
├── ServerError (5xx) - RETRYABLE
├── ConnectionError - RETRYABLE
├── NotFoundError (404) - NOT retryable
├── ModelError - RETRYABLE
└── QuotaExceededError - NOT retryable
```

## Usage Examples

### Example 1: Enhanced OpenRouter with Error Handling

```python
from providers import OpenRouterProviderEnhanced, AuthenticationError, TimeoutError

try:
    provider = OpenRouterProviderEnhanced({
        'api_key': 'sk-...',
        'app_name': 'MyApp'
    })

    response = provider.execute(
        model='openai/gpt-4',
        prompt='Hello!',
        parameters={'temperature': 0.7}
    )
    print(response)

except AuthenticationError:
    print("Invalid API key - update configuration")
except TimeoutError:
    print("Request timed out - try again later")
except Exception as e:
    print(f"Provider error: {e}")
```

### Example 2: Fallback Chain (Primary → Secondary → Tertiary)

```python
from providers import (
    OpenRouterProviderEnhanced,
    OllamaProvider,
    FallbackProvider,
    AuthenticationError,
    InvalidParameterError
)

# Set up providers
primary = OpenRouterProviderEnhanced({'api_key': 'sk-...'})
secondary = OllamaProvider({'base_url': 'http://localhost:11434'})

# Create fallback chain
fallback = FallbackProvider(primary, secondary)

try:
    # Tries primary first
    # If primary fails with timeout/server error → tries secondary
    # If primary fails with auth error → fails immediately (non-retryable)
    response = fallback.execute(
        model='gpt-4',
        prompt='Analyze this code...',
        system_prompt='You are a code reviewer'
    )
    print(f"Success: {response}")

except AuthenticationError:
    print("All providers failed: Invalid credentials")
except InvalidParameterError:
    print("All providers failed: Invalid parameters")
except Exception as e:
    print(f"All providers failed: {e}")
```

### Example 3: Streaming with Fallback

```python
from providers import FallbackProvider

fallback = FallbackProvider(primary, secondary)

try:
    # Streams from first successful provider
    for chunk in fallback.stream_execute(
        model='gpt-4',
        prompt='Write a poem...'
    ):
        print(chunk, end='', flush=True)

except Exception as e:
    print(f"Streaming failed: {e}")
```

### Example 4: Manual Error Classification

```python
from providers.provider_errors import classify_error
import requests

try:
    response = requests.get('https://api.example.com/models')
    response.raise_for_status()
except requests.exceptions.Timeout as e:
    error = classify_error(e)
    if error.retryable:
        print("Will retry with backoff...")
except requests.exceptions.HTTPError as e:
    error = classify_error(e, status_code=e.response.status_code)
    if not error.retryable:
        print(f"Fatal error: {error}")
    else:
        print(f"Retryable error: {error}")
```

### Example 5: Adding Providers Dynamically

```python
from providers import FallbackProvider

fallback = FallbackProvider(primary)

# Later, add fallback providers
fallback.add_provider(secondary)
fallback.add_provider(tertiary)

# Check how many providers are in the chain
print(f"Chain has {fallback.get_provider_count()} providers")

# Get specific provider
second_provider = fallback.get_provider(1)
```

### Example 6: Provider Chain Information

```python
from providers import FallbackProvider

fallback = FallbackProvider(primary, secondary)

info = fallback.get_info()
print(f"Chain type: {info['type']}")
print(f"Provider count: {info['provider_count']}")
print(f"Fallback strategy: {info['fallback_strategy']}")

for provider_info in info['providers']:
    print(f"  - {provider_info['name']}: {provider_info['status']}")
```

## Error Handling Strategy

### Retryable Errors
When these errors occur, the fallback chain tries the next provider:
- `TimeoutError` - Request took too long
- `ServerError` - 5xx errors (may be temporary)
- `ConnectionError` - Network issues (may be temporary)
- `RateLimitError` - Rate limit (wait and try later)

### Non-Retryable Errors
When these occur, the chain fails immediately (no fallback):
- `AuthenticationError` - Invalid credentials
- `InvalidParameterError` - Bad configuration
- `NotFoundError` - Resource doesn't exist
- `QuotaExceededError` - Quota limits hit

## Integration with AI Router

### Option 1: Update Existing Router

```python
# In ai-router.py or ai-router-enhanced.py
from providers import FallbackProvider, OpenRouterProviderEnhanced, OllamaProvider

class AIRouter:
    def __init__(self, config):
        primary = OpenRouterProviderEnhanced(config['openrouter'])
        secondary = OllamaProvider(config.get('ollama', {}))

        # Use fallback chain instead of single provider
        self.provider = FallbackProvider(primary, secondary)

    def execute(self, model, prompt, **kwargs):
        try:
            return self.provider.execute(model, prompt, **kwargs)
        except Exception as e:
            # All providers failed
            logger.error(f"All providers failed: {e}")
            raise
```

### Option 2: Try-Except for Each Error Type

```python
from providers import (
    AuthenticationError, TimeoutError, RateLimitError,
    ServerError, InvalidParameterError
)

def execute_with_retries(provider, model, prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            return provider.execute(model, prompt)
        except TimeoutError as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # exponential backoff
                logger.info(f"Timeout, retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise
        except RateLimitError as e:
            wait_time = e.retry_after or 60
            logger.info(f"Rate limited, waiting {wait_time}s...")
            time.sleep(wait_time)
        except (AuthenticationError, InvalidParameterError):
            # Don't retry non-retryable errors
            raise
```

## Testing

Run the test suite:

```bash
cd D:\models\providers
python test_error_classification.py
```

Expected output:
```
============================================================
PROVIDER ERROR CLASSIFICATION & FALLBACK TESTS
============================================================

=== Testing Error Classification ===
  ✓ 401 -> AuthenticationError
  ✓ 429 -> RateLimitError
  ✓ 500 -> ServerError
  ...

ALL TESTS PASSED!
```

## Parameter Validation

The enhanced provider validates parameters:

```python
provider = OpenRouterProviderEnhanced({'api_key': '...'})

# This works
provider.execute('gpt-4', 'Hello', parameters={
    'temperature': 0.7,
    'max_tokens': 100
})

# This raises InvalidParameterError
provider.execute('gpt-4', 'Hello', parameters={
    'invalid_param': 123  # Unknown parameter!
})
```

## Migration Path

### Existing Code (Still Works)
```python
from providers import OpenRouterProvider

provider = OpenRouterProvider({'api_key': '...'})
response = provider.execute('gpt-4', 'Hello')  # Still works!
```

### New Code (With Error Handling)
```python
from providers import OpenRouterProviderEnhanced, TimeoutError, AuthenticationError

provider = OpenRouterProviderEnhanced({'api_key': '...'})

try:
    response = provider.execute('gpt-4', 'Hello')
except TimeoutError:
    # Handle timeout specifically
    pass
except AuthenticationError:
    # Handle auth error specifically
    pass
```

### Advanced Code (With Fallback)
```python
from providers import FallbackProvider, OpenRouterProviderEnhanced, OllamaProvider

primary = OpenRouterProviderEnhanced({'api_key': '...'})
secondary = OllamaProvider({'base_url': 'http://localhost:11434'})

chain = FallbackProvider(primary, secondary)
response = chain.execute('gpt-4', 'Hello')  # Auto-fallback if primary fails
```

## Benefits

1. **Intelligent Retries** - Only retry when sensible (not for auth errors)
2. **Graceful Degradation** - Fallback to secondary provider automatically
3. **Better Error Messages** - Know exactly what went wrong
4. **No API Changes** - Existing code continues to work
5. **Easy to Test** - Specific error types for test assertions
6. **Production Ready** - Comprehensive error handling

## Performance Impact

- Minimal overhead from error classification
- Connection pooling in OpenRouter provider improves performance
- Fallback chain only adds latency when primary fails

## Next Steps

1. Update router code to use fallback chains
2. Add logging of all error classifications
3. Create monitoring dashboard for error rates
4. Implement exponential backoff for retries
5. Add metrics for fallback chain usage
