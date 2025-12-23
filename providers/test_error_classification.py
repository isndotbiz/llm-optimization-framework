"""
Test suite for Provider Error Classification and Fallback Chains
Demonstrates error handling and fallback logic
"""

import logging
from typing import Dict, Any, Optional
from unittest.mock import Mock, MagicMock

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the error classes and providers
from .provider_errors import (
    ProviderError, AuthenticationError, TimeoutError, RateLimitError,
    InvalidParameterError, ServerError, ConnectionError, classify_error
)
from .fallback_provider import FallbackProvider


class MockProvider:
    """Mock provider for testing fallback logic"""

    def __init__(self, name: str, fail_with: Optional[Exception] = None):
        """
        Create a mock provider.

        Args:
            name: Provider name
            fail_with: Exception to raise (None = success)
        """
        self.name = name
        self.fail_with = fail_with
        self.config = {'mock': True}

    def execute(self, model: str, prompt: str, system_prompt=None, parameters=None) -> str:
        """Execute with potential failure"""
        if self.fail_with:
            raise self.fail_with
        return f"Response from {self.name}"

    def stream_execute(self, model: str, prompt: str, system_prompt=None, parameters=None):
        """Stream execute with potential failure"""
        if self.fail_with:
            raise self.fail_with
        yield f"Response chunk from {self.name}"

    def list_models(self):
        """List models"""
        if self.fail_with:
            raise self.fail_with
        return [{"id": "model1", "name": "Model 1"}]

    def validate_config(self) -> bool:
        """Validate config"""
        if self.fail_with:
            raise self.fail_with
        return True

    def get_info(self) -> Dict[str, Any]:
        """Get info"""
        if self.fail_with:
            raise self.fail_with
        return {"name": self.name, "status": "online"}


def test_error_classification():
    """Test error classification"""
    print("\n=== Testing Error Classification ===\n")

    # Test 1: Classify by status code
    print("Test 1: HTTP Status Code Classification")
    auth_error = classify_error(Exception("Unauthorized"), 401)
    assert isinstance(auth_error, AuthenticationError)
    assert auth_error.status_code == 401
    print("  ✓ 401 -> AuthenticationError")

    rate_limit_error = classify_error(Exception("Rate limit"), 429)
    assert isinstance(rate_limit_error, RateLimitError)
    assert rate_limit_error.status_code == 429
    print("  ✓ 429 -> RateLimitError")

    server_error = classify_error(Exception("Server error"), 500)
    assert isinstance(server_error, ServerError)
    assert server_error.status_code == 500
    print("  ✓ 500 -> ServerError")

    # Test 2: Classify by message
    print("\nTest 2: Message-based Classification")
    timeout_error = classify_error(Exception("Request timeout"))
    assert isinstance(timeout_error, TimeoutError)
    print("  ✓ 'timeout' message -> TimeoutError")

    auth_error = classify_error(Exception("Unauthorized access"))
    assert isinstance(auth_error, AuthenticationError)
    print("  ✓ 'unauthorized' message -> AuthenticationError")

    # Test 3: Error attributes
    print("\nTest 3: Error Attributes")
    timeout = TimeoutError("Custom timeout message")
    assert timeout.retryable == True
    assert "TimeoutError" in str(timeout)
    print("  ✓ TimeoutError is retryable")

    auth = AuthenticationError("Bad credentials")
    assert auth.retryable == False
    print("  ✓ AuthenticationError is not retryable")

    print("\n✓ Error classification tests passed!")


def test_fallback_chain_success():
    """Test fallback chain with successful first provider"""
    print("\n=== Testing Fallback Chain: Success Path ===\n")

    # Create mock providers
    primary = MockProvider("Primary", fail_with=None)
    secondary = MockProvider("Secondary", fail_with=ConnectionError("Connection failed"))

    # Create fallback chain
    fallback = FallbackProvider(primary, secondary)

    # Execute should succeed on primary
    response = fallback.execute("model1", "Hello!")
    assert "Primary" in response
    print("  ✓ Successfully executed on primary provider")

    print("\n✓ Fallback chain success test passed!")


def test_fallback_chain_retry():
    """Test fallback chain retrying on retryable errors"""
    print("\n=== Testing Fallback Chain: Retry Path ===\n")

    # Create mock providers - primary fails with retryable error, secondary succeeds
    primary = MockProvider("Primary", fail_with=TimeoutError("Timeout"))
    secondary = MockProvider("Secondary", fail_with=None)
    tertiary = MockProvider("Tertiary", fail_with=ServerError("Server error", 500))

    # Create fallback chain
    fallback = FallbackProvider(primary, secondary, tertiary)

    # Execute should fallback to secondary after primary timeout
    response = fallback.execute("model1", "Hello!")
    assert "Secondary" in response
    print("  ✓ Fell back from Primary (timeout) to Secondary (success)")

    print("\n✓ Fallback chain retry test passed!")


def test_fallback_chain_non_retryable():
    """Test fallback chain with non-retryable error"""
    print("\n=== Testing Fallback Chain: Non-Retryable Error ===\n")

    # Create mock providers - primary fails with non-retryable error
    primary = MockProvider("Primary", fail_with=AuthenticationError("Invalid key", 401))
    secondary = MockProvider("Secondary", fail_with=None)

    # Create fallback chain
    fallback = FallbackProvider(primary, secondary)

    # Execute should raise immediately (not try secondary)
    try:
        fallback.execute("model1", "Hello!")
        assert False, "Should have raised AuthenticationError"
    except AuthenticationError as e:
        assert "Invalid key" in str(e)
        print("  ✓ Raised AuthenticationError immediately (non-retryable)")
        print("  ✓ Did not try secondary provider")

    print("\n✓ Non-retryable error test passed!")


def test_fallback_chain_all_fail():
    """Test fallback chain when all providers fail"""
    print("\n=== Testing Fallback Chain: All Fail ===\n")

    # Create mock providers - all fail with retryable errors
    primary = MockProvider("Primary", fail_with=TimeoutError("Timeout"))
    secondary = MockProvider("Secondary", fail_with=ServerError("Server error", 503))
    tertiary = MockProvider("Tertiary", fail_with=ConnectionError("Connection lost"))

    # Create fallback chain
    fallback = FallbackProvider(primary, secondary, tertiary)

    # Execute should raise ProviderError after trying all
    try:
        fallback.execute("model1", "Hello!")
        assert False, "Should have raised ProviderError"
    except ProviderError as e:
        assert "All 3 provider(s) failed" in str(e)
        print("  ✓ Tried all providers in chain")
        print("  ✓ Raised ProviderError when all failed")

    print("\n✓ All providers fail test passed!")


def test_provider_info():
    """Test getting info from fallback chain"""
    print("\n=== Testing Fallback Chain Info ===\n")

    primary = MockProvider("Primary")
    secondary = MockProvider("Secondary")

    fallback = FallbackProvider(primary, secondary)

    info = fallback.get_info()
    assert info["type"] == "fallback_chain"
    assert info["provider_count"] == 2
    assert len(info["providers"]) == 2
    print("  ✓ Got fallback chain info")
    print(f"    - Type: {info['type']}")
    print(f"    - Providers: {info['provider_count']}")

    print("\n✓ Provider info test passed!")


def test_parameter_validation():
    """Test parameter validation in error classification"""
    print("\n=== Testing Parameter Validation ===\n")

    try:
        # Test InvalidParameterError
        error = InvalidParameterError(
            "Unknown parameter 'invalid_param' provided. "
            "Valid parameters: temperature, top_p, max_tokens"
        )
        assert not error.retryable
        print("  ✓ InvalidParameterError created and is not retryable")

        # Test that it can be raised
        raise error
    except InvalidParameterError as e:
        print(f"  ✓ Successfully caught InvalidParameterError: {e}")

    print("\n✓ Parameter validation test passed!")


def test_rate_limit_handling():
    """Test rate limit error handling"""
    print("\n=== Testing Rate Limit Handling ===\n")

    # Create rate limit error with retry-after
    rate_limit = RateLimitError(
        "Too many requests",
        status_code=429,
        retry_after=60
    )

    assert rate_limit.retryable == True
    assert rate_limit.retry_after == 60
    assert rate_limit.status_code == 429

    print("  ✓ RateLimitError created with retry_after info")
    print(f"    - Retryable: {rate_limit.retryable}")
    print(f"    - Retry after: {rate_limit.retry_after} seconds")
    print(f"    - Status code: {rate_limit.status_code}")

    print("\n✓ Rate limit handling test passed!")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("PROVIDER ERROR CLASSIFICATION & FALLBACK TESTS")
    print("="*60)

    try:
        test_error_classification()
        test_fallback_chain_success()
        test_fallback_chain_retry()
        test_fallback_chain_non_retryable()
        test_fallback_chain_all_fail()
        test_provider_info()
        test_parameter_validation()
        test_rate_limit_handling()

        print("\n" + "="*60)
        print("ALL TESTS PASSED!")
        print("="*60 + "\n")

        return True

    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}\n")
        return False
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
