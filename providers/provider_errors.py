"""
Provider Error Hierarchy
Defines specific exception types for intelligent error handling and fallback chains
"""


class ProviderError(Exception):
    """
    Base exception for all provider-related errors.

    Attributes:
        message: Error description
        status_code: HTTP status code if applicable
        retryable: Whether this error can be retried
        error_type: Classification of error
    """

    def __init__(self, message: str, status_code: int = None, error_type: str = None):
        """
        Initialize provider error.

        Args:
            message: Error description
            status_code: HTTP status code if applicable
            error_type: Classification of error
        """
        self.message = message
        self.status_code = status_code
        self.error_type = error_type or self.__class__.__name__
        self.retryable = False
        super().__init__(self.message)

    def __str__(self) -> str:
        """String representation of error."""
        if self.status_code:
            return f"{self.error_type} ({self.status_code}): {self.message}"
        return f"{self.error_type}: {self.message}"


class AuthenticationError(ProviderError):
    """
    Authentication failure - credentials are invalid or expired.

    Status codes: 401 Unauthorized, 403 Forbidden
    Retryable: No - authentication issue must be fixed
    Action: Update credentials and retry
    """

    def __init__(self, message: str, status_code: int = 401):
        super().__init__(message, status_code, "AuthenticationError")
        self.retryable = False


class TimeoutError(ProviderError):
    """
    Request timeout - provider took too long to respond.

    Retryable: Yes - with backoff strategy
    Action: Retry with exponential backoff
    """

    def __init__(self, message: str = "Request timeout"):
        super().__init__(message, None, "TimeoutError")
        self.retryable = True


class RateLimitError(ProviderError):
    """
    Rate limit exceeded - too many requests.

    Status codes: 429 Too Many Requests
    Retryable: Yes - wait then retry
    Action: Wait for rate limit reset and retry
    """

    def __init__(self, message: str, status_code: int = 429, retry_after: int = None):
        super().__init__(message, status_code, "RateLimitError")
        self.retryable = True
        self.retry_after = retry_after or 60  # Default 60 seconds


class InvalidParameterError(ProviderError):
    """
    Invalid configuration or parameters provided.

    Retryable: No - invalid config must be fixed
    Action: Review and correct parameters
    """

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message, status_code, "InvalidParameterError")
        self.retryable = False


class ServerError(ProviderError):
    """
    Server error - provider server encountered an error.

    Status codes: 5xx Server Errors
    Retryable: Yes - server may recover
    Action: Retry with backoff
    """

    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message, status_code, "ServerError")
        self.retryable = True


class ConnectionError(ProviderError):
    """
    Connection failed - network error or provider unreachable.

    Retryable: Yes - network may recover
    Action: Retry with backoff
    """

    def __init__(self, message: str):
        super().__init__(message, None, "ConnectionError")
        self.retryable = True


class NotFoundError(ProviderError):
    """
    Resource not found - model or endpoint doesn't exist.

    Status codes: 404 Not Found
    Retryable: No - resource doesn't exist
    Action: Check resource name/ID
    """

    def __init__(self, message: str, status_code: int = 404):
        super().__init__(message, status_code, "NotFoundError")
        self.retryable = False


class ModelError(ProviderError):
    """
    Model-specific error - model failed during execution.

    Retryable: Maybe - depends on error type
    Action: Check model parameters and retry
    """

    def __init__(self, message: str):
        super().__init__(message, None, "ModelError")
        self.retryable = True


class QuotaExceededError(ProviderError):
    """
    Quota exceeded - monthly or daily quota limit reached.

    Retryable: No - must wait for quota reset
    Action: Wait until quota resets
    """

    def __init__(self, message: str, reset_time: str = None):
        super().__init__(message, None, "QuotaExceededError")
        self.retryable = False
        self.reset_time = reset_time


def classify_error(exception: Exception, status_code: int = None) -> ProviderError:
    """
    Classify an exception into a specific ProviderError type.

    Args:
        exception: The exception to classify
        status_code: HTTP status code if applicable

    Returns:
        Classified ProviderError instance
    """
    message = str(exception)

    # HTTP status code based classification
    if status_code:
        if status_code == 401:
            return AuthenticationError(message, status_code)
        elif status_code == 403:
            return AuthenticationError(message, status_code)
        elif status_code == 404:
            return NotFoundError(message, status_code)
        elif status_code == 400:
            return InvalidParameterError(message, status_code)
        elif status_code == 429:
            return RateLimitError(message, status_code)
        elif status_code >= 500:
            return ServerError(message, status_code)

    # Exception type based classification
    if isinstance(exception, TimeoutError):
        return TimeoutError(message)
    elif isinstance(exception, ConnectionError):
        return ConnectionError(message)
    elif "timeout" in message.lower():
        return TimeoutError(message)
    elif "auth" in message.lower() or "unauthorized" in message.lower():
        return AuthenticationError(message)
    elif "not found" in message.lower():
        return NotFoundError(message)
    elif "rate limit" in message.lower() or "429" in message.lower():
        return RateLimitError(message)
    elif "parameter" in message.lower() or "invalid" in message.lower():
        return InvalidParameterError(message)
    elif "server" in message.lower() or "500" in message.lower():
        return ServerError(message)
    elif "connection" in message.lower() or "network" in message.lower():
        return ConnectionError(message)
    elif "quota" in message.lower():
        return QuotaExceededError(message)

    # Default to base ProviderError
    return ProviderError(message)
