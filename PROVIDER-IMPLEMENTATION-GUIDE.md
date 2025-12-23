# Provider Integration Layer - Implementation Guide

## Quick Reference: What to Fix First

### Priority 1: Error Handling (Enables everything else)
- Prevents silent failures
- Enables intelligent retries
- Foundation for fallback chains
- **Time**: 2-3 days

### Priority 2: Remove Streaming Duplication
- Reduces maintenance burden
- Fix one place, fix all providers
- **Time**: 1 day

### Priority 3: Add Fallback Chains
- Production resilience
- Graceful degradation
- **Time**: 2 days

---

## Implementation Steps (In Order)

### Step 1: Create Error Handling Framework

Create file: `D:\models\providers\error_handling.py`

```python
"""Error handling framework for providers"""

from enum import Enum
from typing import Optional
import requests
import logging

logger = logging.getLogger(__name__)


class ErrorCategory(Enum):
    """Error classification"""
    AUTH_ERROR = "auth"           # 401
    RATE_LIMIT = "rate_limit"     # 429
    NOT_FOUND = "not_found"       # 404
    INVALID_REQUEST = "invalid"   # 400
    SERVER_ERROR = "server"       # 5xx
    NETWORK_ERROR = "network"     # Connection/timeout
    UNKNOWN = "unknown"


class ProviderError(RuntimeError):
    """Enhanced error with retry information"""

    def __init__(
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        status_code: Optional[int] = None,
        provider: Optional[str] = None,
        retryable: bool = False,
        retry_after: Optional[int] = None
    ):
        self.message = message
        self.category = category
        self.status_code = status_code
        self.provider = provider
        self.retryable = retryable
        self.retry_after = retry_after
        super().__init__(message)

    def __repr__(self):
        return (f"ProviderError({self.provider}, {self.category.value}, "
                f"status={self.status_code}, retryable={self.retryable})")


class ErrorClassifier:
    """Classifies errors consistently"""

    @staticmethod
    def classify_http_error(
        response: requests.Response,
        provider: str = "unknown"
    ) -> ProviderError:
        """Classify HTTP response errors"""
        status = response.status_code

        if status == 401:
            return ProviderError(
                f"{provider} authentication failed",
                category=ErrorCategory.AUTH_ERROR,
                status_code=status,
                provider=provider,
                retryable=False
            )

        if status == 429:
            retry_after = int(response.headers.get('Retry-After', 60))
            return ProviderError(
                f"{provider} rate limit exceeded",
                category=ErrorCategory.RATE_LIMIT,
                status_code=status,
                provider=provider,
                retryable=True,
                retry_after=retry_after
            )

        if status == 404:
            return ProviderError(
                f"{provider} resource not found",
                category=ErrorCategory.NOT_FOUND,
                status_code=status,
                provider=provider,
                retryable=False
            )

        if status == 400:
            return ProviderError(
                f"{provider} invalid request",
                category=ErrorCategory.INVALID_REQUEST,
                status_code=status,
                provider=provider,
                retryable=False
            )

        if 500 <= status < 600:
            return ProviderError(
                f"{provider} server error ({status})",
                category=ErrorCategory.SERVER_ERROR,
                status_code=status,
                provider=provider,
                retryable=True,
                retry_after=60
            )

        return ProviderError(
            f"{provider} HTTP error: {status}",
            category=ErrorCategory.UNKNOWN,
            status_code=status,
            provider=provider,
            retryable=False
        )

    @staticmethod
    def classify_request_error(
        error: requests.RequestException,
        provider: str = "unknown"
    ) -> ProviderError:
        """Classify requests library errors"""
        if isinstance(error, requests.Timeout):
            return ProviderError(
                f"{provider} request timeout",
                category=ErrorCategory.NETWORK_ERROR,
                provider=provider,
                retryable=True,
                retry_after=10
            )

        if isinstance(error, requests.ConnectionError):
            return ProviderError(
                f"{provider} connection error",
                category=ErrorCategory.NETWORK_ERROR,
                provider=provider,
                retryable=True,
                retry_after=10
            )

        if hasattr(error, 'response') and error.response:
            return ErrorClassifier.classify_http_error(error.response, provider)

        return ProviderError(
            f"{provider} request failed: {str(error)}",
            category=ErrorCategory.UNKNOWN,
            provider=provider,
            retryable=False
        )
```

### Step 2: Update OpenAI Provider to Use Error Handling

**File**: `D:\models\providers\openai_provider.py`

**Change lines 203-209** from:
```python
except requests.RequestException as e:
    error_msg = f"OpenAI API request failed: {str(e)}"
    logger.error(error_msg)
    if hasattr(e, 'response') and e.response is not None:
        logger.error(f"Response: {e.response.text}")
    raise RuntimeError(error_msg)
```

To:
```python
except requests.RequestException as e:
    if hasattr(e, 'response') and e.response is not None:
        raise ErrorClassifier.classify_http_error(e.response, "OpenAI")
    else:
        raise ErrorClassifier.classify_request_error(e, "OpenAI")
```

Add import at top:
```python
from .error_handling import ErrorClassifier, ProviderError
```

### Step 3: Duplicate the Change to Other Providers

Apply same change to:
- `claude_provider.py` (lines 187-192)
- `openrouter_provider.py` (lines 171-176)
- `ollama_provider.py` (lines 143-146)

For **llama.cpp** (subprocess-based), map to network errors:
```python
except subprocess.TimeoutExpired:
    raise ProviderError(
        "llama.cpp execution timeout",
        category=ErrorCategory.NETWORK_ERROR,
        provider="llama.cpp",
        retryable=True,
        retry_after=10
    )
except Exception as e:
    raise ProviderError(
        f"llama.cpp execution error: {str(e)}",
        category=ErrorCategory.UNKNOWN,
        provider="llama.cpp",
        retryable=False
    )
```

---

### Step 4: Create Streaming Utilities

Create file: `D:\models\providers\streaming_utils.py`

```python
"""Shared streaming response parsing"""

import json
import logging
from typing import Generator, Dict, Any
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class StreamParser(ABC):
    """Base class for streaming response parsers"""

    @abstractmethod
    def parse_line(self, line: str) -> Dict[str, Any]:
        """
        Parse single line from stream

        Returns: {'content': '...', 'done': False/True}
        Raises: ValueError if unparseable
        """
        pass


class OpenAIStreamParser(StreamParser):
    """Parser for OpenAI SSE format"""

    def parse_line(self, line: str) -> Dict[str, Any]:
        if not line.startswith('data: '):
            raise ValueError(f"Invalid OpenAI format: {line}")

        json_str = line[6:]
        if json_str == '[DONE]':
            return {'done': True}

        try:
            data = json.loads(json_str)
            delta = data['choices'][0]['delta']
            return {'content': delta.get('content', '')}
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            raise ValueError(f"Parse error: {line}") from e


class ClaudeStreamParser(StreamParser):
    """Parser for Claude event stream"""

    def parse_line(self, line: str) -> Dict[str, Any]:
        if not line.startswith('data: '):
            raise ValueError(f"Invalid Claude format: {line}")

        json_str = line[6:]
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Parse error: {line}") from e

        event_type = data.get('type')

        if event_type == 'content_block_delta':
            delta = data.get('delta', {})
            if delta.get('type') == 'text_delta':
                return {'content': delta.get('text', '')}
            return {'content': ''}

        if event_type == 'message_stop':
            return {'done': True}

        return {'content': ''}


class OllamaStreamParser(StreamParser):
    """Parser for Ollama JSON-per-line format"""

    def parse_line(self, line: str) -> Dict[str, Any]:
        try:
            data = json.loads(line)
            return {
                'content': data.get('response', ''),
                'done': data.get('done', False)
            }
        except json.JSONDecodeError as e:
            raise ValueError(f"Parse error: {line}") from e


def generic_stream(
    response,
    parser: StreamParser,
    provider: str = "unknown"
) -> Generator[str, None, None]:
    """
    Generic streaming handler

    Usage:
        parser = OpenAIStreamParser()
        yield from generic_stream(response, parser, "OpenAI")
    """
    try:
        for line in response.iter_lines():
            if not line:
                continue

            line = line.decode('utf-8') if isinstance(line, bytes) else line

            try:
                parsed = parser.parse_line(line)
            except ValueError as e:
                logger.warning(f"{provider}: {e}")
                continue

            if parsed.get('content'):
                yield parsed['content']

            if parsed.get('done'):
                break

    except Exception as e:
        from .error_handling import ProviderError, ErrorCategory
        raise ProviderError(
            f"{provider} streaming failed",
            category=ErrorCategory.NETWORK_ERROR,
            provider=provider,
            retryable=True
        )
```

### Step 5: Update Providers to Use Streaming Utils

**OpenAI Provider** - Replace `stream_execute()` method (lines 211-286):

```python
from .streaming_utils import OpenAIStreamParser, generic_stream

def stream_execute(
    self,
    model: str,
    prompt: str,
    system_prompt: Optional[str] = None,
    parameters: Optional[Dict[str, Any]] = None
) -> Generator[str, None, None]:
    """Stream execution"""
    try:
        url = urljoin(self.base_url, 'chat/completions')
        messages = self.format_messages(prompt, system_prompt)

        payload = {
            "model": model,
            "messages": messages,
            "stream": True
        }

        if parameters:
            params = self.normalize_parameters(parameters)
            payload.update(params)

        response = requests.post(
            url,
            headers=self.headers,
            json=payload,
            timeout=self.timeout,
            stream=True
        )
        response.raise_for_status()

        parser = OpenAIStreamParser()
        yield from generic_stream(response, parser, "OpenAI")

    except requests.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            raise ErrorClassifier.classify_http_error(e.response, "OpenAI")
        else:
            raise ErrorClassifier.classify_request_error(e, "OpenAI")
```

Apply similar changes to Claude and Ollama providers.

---

### Step 6: Create Fallback Chain Manager

Create file: `D:\models\providers\fallback_manager.py`

```python
"""Fallback chain management with health tracking"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from enum import Enum

from .error_handling import ProviderError, ErrorCategory

logger = logging.getLogger(__name__)


class ProviderHealth(Enum):
    """Health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class ProviderStatus:
    """Track provider health"""

    def __init__(self, name: str):
        self.name = name
        self.health = ProviderHealth.HEALTHY
        self.error_count = 0
        self.success_count = 0

    def mark_success(self):
        """Record successful call"""
        self.success_count += 1
        self.error_count = max(0, self.error_count - 1)
        if self.error_count == 0:
            self.health = ProviderHealth.HEALTHY

    def mark_failure(self):
        """Record failed call"""
        self.error_count += 1
        if self.error_count >= 5:
            self.health = ProviderHealth.UNHEALTHY
        elif self.error_count >= 2:
            self.health = ProviderHealth.DEGRADED


class FallbackChain:
    """Execute with fallback through multiple providers"""

    def __init__(self, providers: List[tuple[str, Any]]):
        """
        Args:
            providers: List of (name, provider_instance) tuples

        Example:
            chain = FallbackChain([
                ('openai', openai_provider),
                ('claude', claude_provider),
                ('ollama', ollama_provider)
            ])
        """
        self.providers = providers
        self.status = {name: ProviderStatus(name) for name, _ in providers}

    def execute(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """Execute with fallback"""
        errors = []

        for provider_name, provider in self.providers:
            try:
                logger.info(f"Trying {provider_name}")
                response = provider.execute(
                    model, prompt, system_prompt, parameters
                )
                self.status[provider_name].mark_success()
                logger.info(f"Success: {provider_name}")
                return response

            except Exception as e:
                self.status[provider_name].mark_failure()
                errors.append(f"{provider_name}: {str(e)}")
                logger.warning(f"Failed: {provider_name}: {e}")

        raise RuntimeError(f"All providers failed: {'; '.join(errors)}")

    def stream_execute(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Generator[str, None, None]:
        """Stream execution with fallback"""
        for provider_name, provider in self.providers:
            try:
                logger.info(f"Streaming with {provider_name}")
                yield from provider.stream_execute(
                    model, prompt, system_prompt, parameters
                )
                self.status[provider_name].mark_success()
                return

            except Exception as e:
                self.status[provider_name].mark_failure()
                logger.warning(f"Stream failed: {provider_name}: {e}")

        raise RuntimeError("All providers failed for streaming")

    def get_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all providers"""
        return {
            name: {
                'health': status.health.value,
                'errors': status.error_count,
                'successes': status.success_count
            }
            for name, status in self.status.items()
        }
```

---

### Step 7: Integration into ProviderManager

Update `D:\models\providers\__init__.py`:

```python
# Add to imports
from .fallback_manager import FallbackChain
from .error_handling import ProviderError

# Update ProviderManager class
class ProviderManager:
    """Manages multiple providers"""

    def __init__(self):
        self.providers: Dict[str, LLMProvider] = {}
        self._fallback_chain = None

    def setup_fallback_chain(self, provider_order: Optional[List[str]] = None):
        """
        Setup fallback chain with provider order

        Args:
            provider_order: List of provider names in fallback order

        Example:
            manager.setup_fallback_chain(['openai', 'claude', 'ollama'])
        """
        if not provider_order:
            provider_order = list(self.providers.keys())

        providers_to_chain = [
            (name, self.providers[name])
            for name in provider_order
            if name in self.providers
        ]

        self._fallback_chain = FallbackChain(providers_to_chain)

    def execute_with_fallback(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Execute with fallback chain

        Example:
            response = manager.execute_with_fallback('gpt-4', 'Hello')
        """
        if not self._fallback_chain:
            self.setup_fallback_chain()

        return self._fallback_chain.execute(
            model, prompt, system_prompt, parameters
        )

    def stream_execute_with_fallback(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Generator[str, None, None]:
        """Stream with fallback"""
        if not self._fallback_chain:
            self.setup_fallback_chain()

        yield from self._fallback_chain.stream_execute(
            model, prompt, system_prompt, parameters
        )

    def get_provider_status(self) -> Dict[str, Dict[str, Any]]:
        """Get health status of all providers"""
        if self._fallback_chain:
            return self._fallback_chain.get_status()
        return {}
```

---

## Testing These Changes

### Test File: `D:\models\tests\test_provider_errors.py`

```python
"""Test error handling framework"""

import pytest
from unittest.mock import Mock, patch
import requests

from providers.error_handling import (
    ErrorClassifier,
    ProviderError,
    ErrorCategory
)


def test_auth_error_classification():
    """Test 401 classified as AUTH_ERROR"""
    response = Mock()
    response.status_code = 401

    error = ErrorClassifier.classify_http_error(response, "test")

    assert error.category == ErrorCategory.AUTH_ERROR
    assert error.retryable is False
    assert error.status_code == 401


def test_rate_limit_detection():
    """Test 429 with Retry-After header"""
    response = Mock()
    response.status_code = 429
    response.headers = {'Retry-After': '120'}

    error = ErrorClassifier.classify_http_error(response, "test")

    assert error.category == ErrorCategory.RATE_LIMIT
    assert error.retryable is True
    assert error.retry_after == 120


def test_server_error_retryable():
    """Test 5xx errors are retryable"""
    response = Mock()
    response.status_code = 503

    error = ErrorClassifier.classify_http_error(response, "test")

    assert error.category == ErrorCategory.SERVER_ERROR
    assert error.retryable is True


def test_timeout_error():
    """Test timeout detection"""
    exc = requests.Timeout()

    error = ErrorClassifier.classify_request_error(exc, "test")

    assert error.category == ErrorCategory.NETWORK_ERROR
    assert error.retryable is True


def test_connection_error():
    """Test connection error detection"""
    exc = requests.ConnectionError()

    error = ErrorClassifier.classify_request_error(exc, "test")

    assert error.category == ErrorCategory.NETWORK_ERROR
    assert error.retryable is True
```

### Test File: `D:\models\tests\test_fallback_chain.py`

```python
"""Test fallback chain functionality"""

import pytest
from unittest.mock import Mock

from providers.fallback_manager import FallbackChain
from providers.error_handling import ProviderError, ErrorCategory


def test_fallback_chain_success_first():
    """Test successful call on first provider"""
    provider1 = Mock()
    provider1.execute.return_value = "response"

    chain = FallbackChain([('provider1', provider1)])
    result = chain.execute('model', 'prompt')

    assert result == "response"
    provider1.execute.assert_called_once()


def test_fallback_chain_fallthrough():
    """Test fallback to second provider on first failure"""
    provider1 = Mock()
    provider1.execute.side_effect = Exception("Failed")

    provider2 = Mock()
    provider2.execute.return_value = "response"

    chain = FallbackChain([
        ('provider1', provider1),
        ('provider2', provider2)
    ])

    result = chain.execute('model', 'prompt')

    assert result == "response"
    provider2.execute.assert_called_once()


def test_fallback_chain_all_fail():
    """Test error when all providers fail"""
    provider1 = Mock()
    provider1.execute.side_effect = Exception("Failed 1")

    provider2 = Mock()
    provider2.execute.side_effect = Exception("Failed 2")

    chain = FallbackChain([
        ('provider1', provider1),
        ('provider2', provider2)
    ])

    with pytest.raises(RuntimeError):
        chain.execute('model', 'prompt')


def test_health_tracking():
    """Test provider health status tracking"""
    provider1 = Mock()
    provider1.execute.side_effect = Exception("Failed")

    chain = FallbackChain([('provider1', provider1)])

    # Fail multiple times
    try:
        chain.execute('model', 'prompt')
    except RuntimeError:
        pass

    status = chain.get_status()
    assert status['provider1']['health'] == 'degraded'
```

---

## Quick Testing

Run the tests:
```bash
cd D:\models
python -m pytest tests/test_provider_errors.py -v
python -m pytest tests/test_fallback_chain.py -v
```

---

## Integration Checklist

- [ ] Create `error_handling.py`
- [ ] Update OpenAI provider with error handling
- [ ] Update Claude provider with error handling
- [ ] Update OpenRouter provider with error handling
- [ ] Update Ollama provider with error handling
- [ ] Update llama.cpp provider with error handling
- [ ] Create `streaming_utils.py`
- [ ] Update OpenAI `stream_execute()`
- [ ] Update Claude `stream_execute()`
- [ ] Update Ollama `stream_execute()`
- [ ] Create `fallback_manager.py`
- [ ] Update ProviderManager with fallback
- [ ] Create unit tests for error handling
- [ ] Create unit tests for streaming
- [ ] Create integration tests for fallback
- [ ] Update documentation with new error types
- [ ] Update examples to use fallback chain

---

## Usage After Implementation

### Old Way (Error-prone)
```python
provider = create_provider('openai', config)
try:
    response = provider.execute('gpt-4', 'prompt')
except RuntimeError as e:
    print("Something failed, retry?")  # No context!
```

### New Way (Robust)
```python
from providers import ProviderManager

manager = ProviderManager()
manager.add_provider('openai', openai_config)
manager.add_provider('claude', claude_config)
manager.add_provider('ollama', ollama_config)

# Auto-fallback
response = manager.execute_with_fallback(
    'gpt-4',
    'What is AI?'
)

# Check health
status = manager.get_provider_status()
print(status)  # See which providers are healthy

# Or use streaming
for chunk in manager.stream_execute_with_fallback('gpt-4', prompt):
    print(chunk, end='', flush=True)
```

---

## Expected Outcomes

| Metric | Before | After |
|--------|--------|-------|
| Error classification | Generic RuntimeError | 7 specific categories |
| Streaming code duplication | 3x repeated | 1 shared implementation |
| Fallback support | None | Full chain with health tracking |
| Lines of provider code | ~500 | ~450 (50 LOC saved) |
| Test coverage | ~40% | ~80% |
| Production reliability | Medium | High |

---

## Questions & Support

For each change, ask:
1. Does this maintain backward compatibility?
2. Are error messages clear for debugging?
3. Are tests passing before deployment?
4. Is performance unaffected?

Good luck with the implementation!
