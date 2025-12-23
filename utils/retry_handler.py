#!/usr/bin/env python3
"""
Retry Handler - Implement retry logic with exponential backoff and timeouts
Handles transient failures in workflow steps with configurable retry strategies
"""

import time
import signal
import functools
from typing import Callable, Any, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class BackoffType(Enum):
    """Retry backoff strategies"""
    EXPONENTIAL = "exponential"  # 1s, 2s, 4s, 8s...
    LINEAR = "linear"             # 1s, 2s, 3s, 4s...
    FIXED = "fixed"               # 1s, 1s, 1s, 1s...


@dataclass
class RetryConfig:
    """Configuration for retry behavior"""
    max_attempts: int = 3
    initial_delay: float = 1.0  # seconds
    max_delay: float = 60.0  # seconds
    backoff: BackoffType = BackoffType.EXPONENTIAL
    timeout: Optional[float] = None  # seconds, None = no timeout

    @staticmethod
    def from_dict(config_dict: Dict[str, Any]) -> 'RetryConfig':
        """Create RetryConfig from dictionary (YAML parsed)"""
        max_attempts = config_dict.get('max_attempts', 3)
        initial_delay = config_dict.get('initial_delay', 1.0)
        max_delay = config_dict.get('max_delay', 60.0)

        # Parse backoff type
        backoff_str = config_dict.get('backoff', 'exponential')
        try:
            backoff = BackoffType(backoff_str)
        except ValueError:
            backoff = BackoffType.EXPONENTIAL

        timeout = config_dict.get('timeout')

        return RetryConfig(
            max_attempts=max_attempts,
            initial_delay=initial_delay,
            max_delay=max_delay,
            backoff=backoff,
            timeout=timeout
        )


class TimeoutError(Exception):
    """Raised when operation times out"""
    pass


class RetryHandler:
    """Handle retries with backoff for workflow steps"""

    @staticmethod
    def execute_with_retry(
        func: Callable,
        args: Tuple = (),
        kwargs: Dict = None,
        retry_config: Optional[RetryConfig] = None,
        on_retry_callback: Optional[Callable] = None
    ) -> Any:
        """
        Execute function with automatic retry on failure

        Args:
            func: Callable to execute
            args: Positional arguments for func
            kwargs: Keyword arguments for func
            retry_config: RetryConfig for retry behavior
            on_retry_callback: Optional callback(attempt, delay, error) on retry

        Returns:
            Result of func() call

        Raises:
            Last exception if all retries exhausted
            TimeoutError if operation times out
        """
        if kwargs is None:
            kwargs = {}

        if retry_config is None:
            retry_config = RetryConfig()

        last_exception = None

        for attempt in range(1, retry_config.max_attempts + 1):
            try:
                # Execute with timeout if configured
                if retry_config.timeout:
                    return RetryHandler._execute_with_timeout(
                        func, args, kwargs, retry_config.timeout
                    )
                else:
                    return func(*args, **kwargs)

            except TimeoutError as e:
                last_exception = e
                if attempt < retry_config.max_attempts:
                    delay = RetryHandler._calculate_backoff(
                        attempt, retry_config
                    )
                    if on_retry_callback:
                        on_retry_callback(attempt, delay, e)
                    time.sleep(delay)

            except Exception as e:
                last_exception = e
                if attempt < retry_config.max_attempts:
                    delay = RetryHandler._calculate_backoff(
                        attempt, retry_config
                    )
                    if on_retry_callback:
                        on_retry_callback(attempt, delay, e)
                    time.sleep(delay)

        # All retries exhausted
        raise last_exception

    @staticmethod
    def _calculate_backoff(attempt: int, config: RetryConfig) -> float:
        """
        Calculate backoff delay for given attempt

        Args:
            attempt: Attempt number (1-indexed)
            config: RetryConfig

        Returns:
            Delay in seconds
        """
        if config.backoff == BackoffType.EXPONENTIAL:
            delay = config.initial_delay * (2 ** (attempt - 1))
        elif config.backoff == BackoffType.LINEAR:
            delay = config.initial_delay * attempt
        else:  # FIXED
            delay = config.initial_delay

        # Cap at max_delay
        return min(delay, config.max_delay)

    @staticmethod
    def _execute_with_timeout(
        func: Callable,
        args: Tuple,
        kwargs: Dict,
        timeout: float
    ) -> Any:
        """
        Execute function with timeout

        Note: This is a best-effort implementation using signals on Unix-like systems.
        On Windows, it may not work as expected. A more robust implementation would
        use multiprocessing or concurrent.futures.

        Args:
            func: Callable to execute
            args: Arguments for func
            kwargs: Keyword arguments for func
            timeout: Timeout in seconds

        Returns:
            Result of func() call

        Raises:
            TimeoutError if timeout exceeded
        """
        try:
            # Try Unix-style signal-based timeout (doesn't work on Windows)
            def timeout_handler(signum, frame):
                raise TimeoutError(f"Operation timed out after {timeout} seconds")

            # Save original handler
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(int(timeout) + 1)  # Round up

            try:
                result = func(*args, **kwargs)
            finally:
                # Cancel alarm
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)

            return result

        except AttributeError:
            # signal.SIGALRM not available on Windows
            # Fall back to simple synchronous execution without timeout
            import warnings
            warnings.warn(
                "Timeout not fully supported on this platform. "
                "Use concurrent.futures for robust timeout handling.",
                RuntimeWarning
            )
            return func(*args, **kwargs)

    @staticmethod
    def retry_decorator(
        max_attempts: int = 3,
        backoff: str = 'exponential',
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        timeout: Optional[float] = None
    ):
        """
        Decorator for adding retry logic to functions

        Usage:
            @RetryHandler.retry_decorator(max_attempts=3, backoff='exponential')
            def unstable_api_call():
                return requests.get('http://api.example.com')
        """
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                config = RetryConfig(
                    max_attempts=max_attempts,
                    initial_delay=initial_delay,
                    max_delay=max_delay,
                    backoff=BackoffType(backoff),
                    timeout=timeout
                )

                def retry_callback(attempt, delay, error):
                    print(f"  Retry attempt {attempt}: {error}. Waiting {delay:.1f}s...")

                return RetryHandler.execute_with_retry(
                    func, args, kwargs, config, retry_callback
                )

            return wrapper
        return decorator

    @staticmethod
    def format_backoff_schedule(config: RetryConfig) -> str:
        """
        Format retry schedule for display

        Args:
            config: RetryConfig

        Returns:
            Human-readable schedule string
        """
        schedule = []
        for attempt in range(1, config.max_attempts):
            delay = RetryHandler._calculate_backoff(attempt, config)
            schedule.append(f"Attempt {attempt}: {delay:.1f}s delay")

        return ", ".join(schedule)


class CircuitBreaker:
    """
    Circuit breaker pattern for handling cascading failures

    States:
        - CLOSED: Requests pass through normally
        - OPEN: Requests fail immediately
        - HALF_OPEN: Limited requests allowed to test recovery
    """

    class State(Enum):
        CLOSED = "closed"
        OPEN = "open"
        HALF_OPEN = "half_open"

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: type = Exception
    ):
        """
        Initialize CircuitBreaker

        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds before attempting half-open state
            expected_exception: Exception type to catch
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.state = self.State.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.success_count = 0

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection

        Raises:
            RuntimeError if circuit is OPEN
            Expected exception if function fails
        """
        if self.state == self.State.OPEN:
            if self._should_attempt_reset():
                self.state = self.State.HALF_OPEN
                self.success_count = 0
            else:
                raise RuntimeError(
                    f"Circuit breaker OPEN. Service unavailable. "
                    f"Next retry in {self._time_until_reset():.1f}s"
                )

        try:
            result = func(*args, **kwargs)

            if self.state == self.State.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= 2:
                    # Recovery successful
                    self._reset()

            return result

        except self.expected_exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.state == self.State.HALF_OPEN:
                # Failed during recovery attempt
                self.state = self.State.OPEN
                raise

            if self.failure_count >= self.failure_threshold:
                self.state = self.State.OPEN

            raise

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt recovery"""
        if self.last_failure_time is None:
            return False
        return time.time() - self.last_failure_time >= self.recovery_timeout

    def _time_until_reset(self) -> float:
        """Time until next recovery attempt"""
        if self.last_failure_time is None:
            return 0
        elapsed = time.time() - self.last_failure_time
        return max(0, self.recovery_timeout - elapsed)

    def _reset(self):
        """Reset circuit breaker to closed state"""
        self.state = self.State.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None

    def get_status(self) -> Dict[str, Any]:
        """Get current circuit breaker status"""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "failure_threshold": self.failure_threshold,
            "last_failure_time": self.last_failure_time,
            "time_until_reset": self._time_until_reset() if self.state == self.State.OPEN else None
        }
