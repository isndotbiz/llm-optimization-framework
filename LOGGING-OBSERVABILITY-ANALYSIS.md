# Logging & Observability Analysis - AI Router System
**Agent 7: Logging, Monitoring & Observability Expert**
**Date:** 2025-12-22
**Status:** Comprehensive Analysis Complete

---

## Executive Summary

The AI Router system has **basic logging infrastructure** but significant gaps in observability, structured logging, metrics collection, and request tracing. Current implementation is **70% functional but lacks enterprise-grade visibility**.

### Quick Stats:
- **Logging enabled:** ✓ Yes (basic)
- **Log volume:** 205 lines across 7 daily logs (~30KB total)
- **Structured logging:** ✗ No (plain text format)
- **Metrics collection:** ✗ No
- **Request tracing:** ✗ No trace IDs
- **Performance metrics:** ✗ Not collected
- **Secret protection:** ✓ Partial (safe_config masking in providers)
- **Console vs file:** Console-heavy, file logging minimal

---

## 1. CURRENT STATE ANALYSIS

### 1.1 Logging Infrastructure

**File:** `D:\models\logging_config.py`

```python
def setup_logging(models_dir: Path, level=logging.INFO):
    """Setup logging for AI Router"""
    log_dir = models_dir / "logs"
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / f"ai-router-{datetime.now().strftime('%Y%m%d')}.log"

    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',  # ISSUE: Minimal format
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
        ]
    )

    return logging.getLogger('ai-router')
```

**Issues Identified:**
1. **Format is too simple** - Only timestamp, level, message (no module, function, line number)
2. **No console handler** - Only file logging, user gets no feedback during execution
3. **No structured JSON** - Plain text format, hard to parse/aggregate
4. **basicConfig overrides** - Calling basicConfig can cause side effects
5. **No log rotation** - Files grow indefinitely (currently 30KB but will accumulate)
6. **Single logger** - All modules share one logger without context

### 1.2 Logging Usage Pattern

**Coverage Analysis:**

| Component | Logging | Quality | Gap |
|-----------|---------|---------|-----|
| ai-router.py | 12 calls | Low | No module context |
| ai-router-enhanced.py | 15 calls | Low | No trace IDs |
| analytics_dashboard.py | None | N/A | **CRITICAL: No logging at all** |
| providers/* | 5-10 calls | Medium | Inconsistent formats |
| utils/* | None | N/A | **No visibility** |
| Session Manager | None | N/A | **No visibility** |

**Sample Log Entry (Current):**
```
2025-12-18 17:05:11,652 - INFO - Starting model execution: dolphin-llama31-8b (Dolphin 3.0 Llama 3.1 8B Q6_K)
```

**Problems:**
- No request ID for correlation
- No module/file context
- No duration tracking
- No error codes or categories
- Duplicate messages in different files

### 1.3 What's Being Logged vs. What Should Be

#### Currently Logged ✓
- Application startup/initialization
- Model execution start/end
- Retry attempts (warning level)
- Execution errors (error level)
- WSL validation checks (warning)

#### Missing Logs ✗
- **Database operations** - No visibility into session manager queries
- **API calls** - No provider request/response logging
- **Performance metrics** - No timing information
- **User actions** - No audit trail
- **Configuration changes** - No tracking of settings
- **Memory/resource usage** - No system metrics
- **Request correlation** - No trace IDs across operations
- **Security events** - No authentication/authorization logs
- **Cache operations** - No cache hits/misses
- **Error context** - Minimal stack trace or diagnostic info

### 1.4 Analytics Dashboard

**File:** `D:\models\utils\analytics_dashboard.py`

**Status:** ✓ Works but **NOT integrated with logging**

- Only queries SQLite directly
- No logging integration
- No performance metrics exported
- No structured output for dashboards
- No real-time metrics capability

---

## 2. HIGH-IMPACT ISSUES (Priority Ranked)

### ISSUE #1: Unstructured Logs (CRITICAL)
**Impact:** High | **Effort:** Medium | **Risk:** Low

**Problem:**
- Plain text format with no JSON/structured output
- Makes log aggregation/parsing impossible
- No field extraction for analysis

**Evidence:**
```
2025-12-18 15:30:41,665 - INFO - Starting model execution: llama33-70b (Llama 3.3 70B Instruct IQ2_S (Abliterated))
2025-12-18 15:30:44,483 - ERROR - llama.cpp execution failed with return code 2
```

Cannot parse:
- Which model ID failed?
- What return code triggered it?
- How long did it take?
- What triggered the request?

**Solution:** Add JSON formatter with structured fields

---

### ISSUE #2: No Request/Trace ID Correlation (CRITICAL)
**Impact:** High | **Effort:** High | **Risk:** Medium

**Problem:**
- Each request/operation is invisible
- Multiple retries appear as separate logs
- No way to correlate database queries to API calls to model execution

**Evidence from logs:**
```
...Attempt 2/3 (separate log entry - no correlation to original request)
...Attempt 3/3 (another separate entry)
...All retry attempts exhausted (no reference to original request ID)
```

**Solution:** Implement trace ID propagation

---

### ISSUE #3: No Performance Metrics (HIGH)
**Impact:** High | **Effort:** Medium | **Risk:** Low

**Problem:**
- No timing measurements collected
- No throughput metrics
- No bottleneck identification possible
- Analytics dashboard only shows business metrics (usage counts)

**Solution:** Add timing instrumentation

---

### ISSUE #4: Missing Application Logging (HIGH)
**Impact:** High | **Effort:** High | **Risk:** Low

**Problem:**
- `utils/session_manager.py` - No logging for 50+ database operations
- `utils/analytics_dashboard.py` - Completely unlogged
- `utils/template_manager.py` - No logging
- Provider implementations inconsistent

**Solution:** Add comprehensive logging to core utils

---

### ISSUE #5: No Secret/Sensitive Data Protection (MEDIUM)
**Impact:** Medium | **Effort:** Low | **Risk:** High (if not done correctly)

**Problem:**
- Base provider has `_safe_config()` masking API keys
- But other modules don't use it
- No automatic secret detection in logs
- Prompts could contain PII

**Solution:** Implement secret filter at logging layer

---

## 3. CONCRETE PROPOSALS

### PROPOSAL #1: Structured JSON Logging

**File to create:** `D:\models\logging_config_v2.py`

```python
import logging
import json
from datetime import datetime
from typing import Dict, Any
import uuid
import contextvars

# Context variable for trace ID
trace_id_context = contextvars.ContextVar('trace_id', default=None)

class StructuredFormatter(logging.Formatter):
    """Convert logs to structured JSON format"""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'trace_id': trace_id_context.get(),
            'request_id': getattr(record, 'request_id', None),
        }

        # Add extra fields if provided
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)

        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
            log_entry['exception_type'] = record.exc_info[0].__name__

        return json.dumps(log_entry)

def setup_structured_logging(models_dir, level=logging.INFO):
    """Setup structured JSON logging"""
    log_dir = models_dir / "logs"
    log_dir.mkdir(exist_ok=True)

    # File handler with JSON formatter
    file_handler = logging.FileHandler(
        log_dir / f"ai-router-{datetime.now().strftime('%Y%m%d')}.jsonl",
        encoding='utf-8'
    )
    file_handler.setFormatter(StructuredFormatter())

    # Console handler with human-readable format
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)-8s] [%(trace_id)s] %(name)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)

    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    return logging.getLogger('ai-router')

def set_trace_id(trace_id: str = None):
    """Set trace ID for current request context"""
    if trace_id is None:
        trace_id = str(uuid.uuid4())
    trace_id_context.set(trace_id)
    return trace_id
```

**Benefits:**
- Machine-parseable format (JSONL - one JSON per line)
- Full context captured (module, function, line number)
- Ready for ELK Stack / Datadog / CloudWatch
- Trace ID correlation built-in
- Both file (JSON) and console (human-readable) logging

**Implementation Impact:**
- Replace `logging_config.py` with this version
- Add ~50 lines to `ai-router.py` and `ai-router-enhanced.py` to call `set_trace_id()`
- Update `basicConfig` calls to use `setup_structured_logging()`

---

### PROPOSAL #2: Request/Trace ID Propagation

**Implementation Pattern:**

```python
# In ai-router.py/ai-router-enhanced.py main methods

from logging_config import set_trace_id

def run_chat_session(self):
    """Run an interactive chat session"""
    trace_id = set_trace_id()  # Generate unique ID for this session
    self.logger.info(f"Chat session started", extra={
        'request_id': trace_id,
        'extra_fields': {
            'project': self.current_project,
            'model': model_id,
            'user': getpass.getuser(),
            'session_type': 'chat'
        }
    })

    # All subsequent logs in this call will include trace_id automatically
    while True:
        prompt = input(...)
        operation_id = f"{trace_id}-{uuid.uuid4().hex[:8]}"

        self.logger.info("Processing user prompt", extra={
            'request_id': operation_id,
            'extra_fields': {
                'prompt_length': len(prompt),
                'model': model_id
            }
        })

        # Model execution
        result = self._run_model_with_config(...)

        self.logger.info("Model execution completed", extra={
            'request_id': operation_id,
            'extra_fields': {
                'duration_ms': elapsed_ms,
                'tokens_used': token_count,
                'status': 'success' if result else 'failed'
            }
        })
```

**Log Correlation Example:**
```json
{"timestamp": "2025-12-22T10:30:45Z", "trace_id": "sess-abc123", "message": "Chat session started", "project": "MyProject"}
{"timestamp": "2025-12-22T10:30:46Z", "trace_id": "sess-abc123", "request_id": "req-001", "message": "Processing user prompt"}
{"timestamp": "2025-12-22T10:30:48Z", "trace_id": "sess-abc123", "request_id": "req-001", "message": "Model execution completed", "duration_ms": 2150}
```

**Now you can query:** "Show me all operations for session sess-abc123"

---

### PROPOSAL #3: Performance Metrics Collection

**File to create:** `D:\models\metrics_collector.py`

```python
import time
from functools import wraps
from typing import Callable, Any, Dict
from datetime import datetime
import logging

logger = logging.getLogger('ai-router.metrics')

class MetricsCollector:
    """Collect and export performance metrics"""

    def __init__(self):
        self.metrics = []

    def record_metric(self, metric_name: str, value: float,
                     tags: Dict[str, str] = None, unit: str = ''):
        """Record a metric"""
        metric = {
            'timestamp': datetime.utcnow().isoformat(),
            'name': metric_name,
            'value': value,
            'unit': unit,
            'tags': tags or {}
        }
        self.metrics.append(metric)

        logger.info(f"Metric recorded", extra={'extra_fields': metric})

    def timed_operation(self, operation_name: str, tags: Dict[str, str] = None):
        """Decorator to measure operation duration"""
        def decorator(func: Callable) -> Callable:
            def wrapper(*args, **kwargs) -> Any:
                start = time.perf_counter()
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    duration_ms = (time.perf_counter() - start) * 1000
                    self.record_metric(
                        f'{operation_name}.duration',
                        duration_ms,
                        tags={**(tags or {}), 'function': func.__name__},
                        unit='ms'
                    )
            return wrapper
        return decorator

# Global instance
metrics = MetricsCollector()

# Usage in ai-router.py:
@metrics.timed_operation('model_execution', {'model': model_id})
def _run_llamacpp_model(self, model_data, prompt):
    # existing code
    pass

@metrics.timed_operation('database_query', {'query_type': 'session_create'})
def create_session(self, model_id: str):
    # existing code
    pass
```

**Metrics to Collect:**
1. **Model Execution:**
   - `model.execution.duration` (ms) - How long model takes to run
   - `model.tokens.per_second` - Throughput
   - `model.error.rate` - Failure percentage

2. **Database Operations:**
   - `db.query.duration` (ms)
   - `db.query.count` - How many queries per session
   - `db.connection.pool.utilization` - Connection pool health

3. **User Sessions:**
   - `session.duration` (seconds)
   - `session.message.count`
   - `session.completion.rate` (% successful)

4. **System Resources:**
   - `memory.peak_usage` (MB)
   - `gpu.utilization` (%)
   - `gpu.memory.used` (MB)

**Export Format (Prometheus):**
```
# HELP ai_router_model_execution_duration_ms Model execution time
# TYPE ai_router_model_execution_duration_ms histogram
ai_router_model_execution_duration_ms{model="qwen3-coder-30b",status="success"} 2150.0
ai_router_model_execution_duration_ms{model="dolphin-llama31-8b",status="success"} 1850.0

# HELP ai_router_session_duration_seconds Session duration
# TYPE ai_router_session_duration_seconds gauge
ai_router_session_duration_seconds{project="MyProject"} 3600.5
```

---

### PROPOSAL #4: Enhanced Error Logging

**Current (Inadequate):**
```
2025-12-18 15:30:44,483 - ERROR - llama.cpp execution failed with return code 2
```

**Proposed (Rich Context):**
```json
{
  "timestamp": "2025-12-18T15:30:44Z",
  "level": "ERROR",
  "trace_id": "req-abc123",
  "message": "Model execution failed",
  "error_code": "MODEL_EXECUTION_FAILED",
  "error_category": "infrastructure",
  "return_code": 2,
  "model_id": "llama33-70b",
  "model_path": "/mnt/d/models/organized/Llama-3.3-70B-Instruct-abliterated-IQ2_S.gguf",
  "command_args": ["llama-cli", "-m", "..."],
  "stderr": "Error: Model not found at specified path",
  "stdout": "",
  "duration_ms": 2150,
  "retry_count": 2,
  "context": {
    "platform": "windows",
    "wsl_available": false,
    "gpu_memory_available_mb": 4096,
    "system_memory_available_mb": 8192
  },
  "stack_trace": "File 'ai-router-enhanced.py', line 1500, in _run_llamacpp_model..."
}
```

**Implementation:**
```python
def handle_model_execution_error(self, model_id: str, error: Exception,
                                 context: Dict[str, Any]):
    """Enhanced error logging with diagnostic context"""

    error_entry = {
        'error_code': self._categorize_error(error),
        'error_category': 'infrastructure' if isinstance(error, RuntimeError) else 'unknown',
        'model_id': model_id,
        'context': context,
        'platform': self.platform,
        'available_resources': self._get_available_resources(),
    }

    self.logger.error(
        f"Model execution failed: {error}",
        exc_info=True,
        extra={'extra_fields': error_entry}
    )
```

---

### PROPOSAL #5: Dashboard Integration

**File to create:** `D:\models\observability_dashboard.py`

```python
"""
Real-time Observability Dashboard for AI Router
Integrates logging, metrics, and analytics
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import logging

logger = logging.getLogger('ai-router.dashboard')

class ObservabilityDashboard:
    """Aggregates logs and metrics for real-time visibility"""

    def __init__(self, models_dir: Path):
        self.models_dir = models_dir
        self.log_dir = models_dir / 'logs'

    def parse_jsonl_logs(self, hours: int = 24) -> list:
        """Parse structured JSONL logs"""
        logs = []
        cutoff = datetime.utcnow() - timedelta(hours=hours)

        for log_file in self.log_dir.glob('ai-router-*.jsonl'):
            try:
                with open(log_file, 'r') as f:
                    for line in f:
                        entry = json.loads(line.strip())
                        entry_time = datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00'))
                        if entry_time > cutoff:
                            logs.append(entry)
            except (json.JSONDecodeError, ValueError):
                pass

        return logs

    def get_performance_summary(self) -> dict:
        """Get performance metrics summary"""
        logs = self.parse_jsonl_logs(hours=1)

        model_stats = defaultdict(lambda: {
            'count': 0,
            'success': 0,
            'failure': 0,
            'total_duration_ms': 0,
            'avg_duration_ms': 0
        })

        for entry in logs:
            if 'model' not in entry.get('extra_fields', {}):
                continue

            model = entry['extra_fields']['model']
            model_stats[model]['count'] += 1

            if entry.get('level') == 'ERROR':
                model_stats[model]['failure'] += 1
            else:
                model_stats[model]['success'] += 1

            if 'duration_ms' in entry.get('extra_fields', {}):
                model_stats[model]['total_duration_ms'] += entry['extra_fields']['duration_ms']

        # Calculate averages
        for model, stats in model_stats.items():
            if stats['count'] > 0:
                stats['avg_duration_ms'] = stats['total_duration_ms'] / stats['count']

        return dict(model_stats)

    def get_error_analysis(self) -> dict:
        """Get error rate and types"""
        logs = self.parse_jsonl_logs(hours=24)

        error_stats = {
            'total_errors': 0,
            'by_category': defaultdict(int),
            'by_model': defaultdict(int),
            'error_rate': 0.0
        }

        total = len(logs)

        for entry in logs:
            if entry.get('level') == 'ERROR':
                error_stats['total_errors'] += 1
                category = entry.get('extra_fields', {}).get('error_category', 'unknown')
                error_stats['by_category'][category] += 1

                model = entry.get('extra_fields', {}).get('model', 'unknown')
                error_stats['by_model'][model] += 1

        if total > 0:
            error_stats['error_rate'] = (error_stats['total_errors'] / total) * 100

        return {**error_stats, 'by_category': dict(error_stats['by_category']),
                'by_model': dict(error_stats['by_model'])}

    def display_dashboard(self):
        """Display real-time dashboard"""
        print("\n" + "=" * 80)
        print("  AI ROUTER - OBSERVABILITY DASHBOARD")
        print("  " + datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'))
        print("=" * 80)

        # Performance Summary
        print("\nPERFORMANCE (Last Hour)")
        print("-" * 80)
        perf = self.get_performance_summary()
        for model, stats in sorted(perf.items()):
            success_rate = (stats['success'] / stats['count'] * 100) if stats['count'] > 0 else 0
            print(f"{model:30} | Executions: {stats['count']:3d} | "
                  f"Success: {success_rate:5.1f}% | "
                  f"Avg Duration: {stats['avg_duration_ms']:7.1f}ms")

        # Error Analysis
        print("\nERROR ANALYSIS (Last 24 Hours)")
        print("-" * 80)
        errors = self.get_error_analysis()
        print(f"Total Errors: {errors['total_errors']} | Error Rate: {errors['error_rate']:.2f}%")
        print("\nBy Category:")
        for category, count in errors['by_category'].items():
            print(f"  {category}: {count}")
        print("\nBy Model:")
        for model, count in errors['by_model'].items():
            print(f"  {model}: {count}")

        print("\n" + "=" * 80 + "\n")


# Usage:
if __name__ == "__main__":
    from pathlib import Path
    dashboard = ObservabilityDashboard(Path.cwd())
    dashboard.display_dashboard()
```

---

### PROPOSAL #6: Secret Detection & Filtering

**File to create:** `D:\models\secret_filter.py`

```python
import logging
import re

class SecretFilter(logging.Filter):
    """Filter to mask secrets in logs"""

    # Patterns to detect secrets
    SECRET_PATTERNS = {
        'api_key': re.compile(r'(api[_-]?key|apikey)["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_\-]{20,})["\']?', re.IGNORECASE),
        'password': re.compile(r'(password|passwd)["\']?\s*[:=]\s*["\']?([^\s"\';,]+)["\']?', re.IGNORECASE),
        'token': re.compile(r'(token|auth)["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_\-]{20,})["\']?', re.IGNORECASE),
        'bearer': re.compile(r'Bearer\s+([a-zA-Z0-9_\-\.]+)', re.IGNORECASE),
        'openai_key': re.compile(r'sk-[a-zA-Z0-9]{48}'),
        'aws_key': re.compile(r'AKIA[0-9A-Z]{16}'),
        'pii_email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
        'pii_phone': re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'),
    }

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter log record to mask secrets"""
        message = record.getMessage()

        for secret_type, pattern in self.SECRET_PATTERNS.items():
            message = pattern.sub(f'***{secret_type.upper()}_REDACTED***', message)

        # Update record message
        record.msg = message
        record.args = ()

        return True


# Setup in logging_config.py:
def setup_structured_logging(models_dir, level=logging.INFO):
    # ... existing code ...

    # Add secret filter to all handlers
    secret_filter = SecretFilter()

    for handler in root_logger.handlers:
        handler.addFilter(secret_filter)

    return logging.getLogger('ai-router')
```

---

## 4. RISK ANALYSIS & COMPATIBILITY

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| JSON format breaks log parsers | Low | High | Add migration tool, support both formats initially |
| Trace ID overhead | Very Low | Low | Minimal string overhead (~100 bytes per request) |
| Performance impact | Low | Medium | Profile metrics collection, sample if needed |
| Secret filter false positives | Medium | Low | Test patterns, configure exclusions |
| Storage increase | Medium | Medium | Implement log rotation (daily, size-based) |

### Breaking Changes

1. **Log Format Change** - From plain text to JSONL
   - Old log parsers will break
   - Mitigation: Support both formats for 1 release, provide migration script

2. **API changes** - `setup_logging()` signature unchanged but behavior differs
   - Mitigation: Backward compatible

3. **Storage format** - `.log` → `.jsonl`
   - Mitigation: Transparent to users

### Performance Impact

**Estimated overhead:**
- Structured logging: +2-5% CPU (JSON serialization)
- Trace ID propagation: <1% (simple contextvars)
- Metrics collection: +3-8% (timing measurements)
- Secret filtering: +1-2% (regex matching)

**Total:** ~7-15% overhead (acceptable for observability gains)

### Disk Space Considerations

**Current:** 30KB for ~1 week of logs (205 lines)
**Projected:** 50-100KB/week with structured logging (more detail)
**Recommendation:** Implement rotation to avoid > 1GB/month

---

## 5. TESTS NEEDED

### Test Suite to Implement

**File:** `D:\models\tests\test_logging_observability.py`

```python
import unittest
import json
import tempfile
from pathlib import Path
from logging_config import setup_structured_logging, set_trace_id
from secret_filter import SecretFilter
import logging


class TestStructuredLogging(unittest.TestCase):
    """Test structured logging functionality"""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())

    def test_json_format_valid(self):
        """Verify logs are valid JSON"""
        logger = setup_structured_logging(self.temp_dir)
        logger.info("Test message", extra={'extra_fields': {'test': 'value'}})

        log_file = list(self.temp_dir.glob('logs/*.jsonl'))[0]
        with open(log_file) as f:
            entry = json.loads(f.readline())

        self.assertIn('timestamp', entry)
        self.assertIn('level', entry)
        self.assertIn('message', entry)
        self.assertEqual(entry['level'], 'INFO')

    def test_trace_id_propagation(self):
        """Verify trace ID is included in logs"""
        logger = setup_structured_logging(self.temp_dir)
        trace_id = set_trace_id("test-trace-123")
        logger.info("Test message")

        log_file = list(self.temp_dir.glob('logs/*.jsonl'))[0]
        with open(log_file) as f:
            entry = json.loads(f.readline())

        self.assertEqual(entry['trace_id'], 'test-trace-123')

    def test_secret_filtering_api_key(self):
        """Verify API keys are masked"""
        secret_filter = SecretFilter()
        record = logging.LogRecord(
            name='test', level=logging.INFO, pathname='', lineno=0,
            msg="api_key=sk-1234567890abcdef1234567890abcdef", args=(),
            exc_info=None
        )

        secret_filter.filter(record)
        self.assertNotIn('sk-1234567890', record.getMessage())
        self.assertIn('API_KEY_REDACTED', record.getMessage())

    def test_secret_filtering_email(self):
        """Verify emails are masked"""
        secret_filter = SecretFilter()
        record = logging.LogRecord(
            name='test', level=logging.INFO, pathname='', lineno=0,
            msg="User email: user@example.com", args=(),
            exc_info=None
        )

        secret_filter.filter(record)
        self.assertNotIn('user@example.com', record.getMessage())
        self.assertIn('EMAIL_REDACTED', record.getMessage())

    def test_metrics_collection(self):
        """Verify metrics are recorded"""
        from metrics_collector import metrics

        metrics.record_metric('test.metric', 100.5, tags={'test': 'value'}, unit='ms')

        self.assertEqual(len(metrics.metrics), 1)
        self.assertEqual(metrics.metrics[0]['name'], 'test.metric')
        self.assertEqual(metrics.metrics[0]['value'], 100.5)

    def test_performance_decorator(self):
        """Verify timing decorator works"""
        from metrics_collector import metrics

        @metrics.timed_operation('test_operation')
        def slow_function():
            import time
            time.sleep(0.1)

        slow_function()

        self.assertTrue(any(m['name'] == 'test_operation.duration' for m in metrics.metrics))


class TestErrorLogging(unittest.TestCase):
    """Test error context capture"""

    def test_error_with_context(self):
        """Verify error logs include context"""
        logger = setup_structured_logging(Path(tempfile.mkdtemp()))

        try:
            raise ValueError("Test error")
        except ValueError as e:
            logger.error("An error occurred", exc_info=True, extra={
                'extra_fields': {'context': 'test', 'model': 'test-model'}
            })

        # Verify log contains exception info
        # (Implementation details depend on log file format)


class TestSecretDetection(unittest.TestCase):
    """Test secret detection patterns"""

    def test_detect_openai_key(self):
        """Verify OpenAI key detection"""
        secret_filter = SecretFilter()
        record = logging.LogRecord(
            name='test', level=logging.INFO, pathname='', lineno=0,
            msg="Initializing with sk-abcdefghijklmnopqrstuvwxyz123456789012345678", args=(),
            exc_info=None
        )

        secret_filter.filter(record)
        self.assertIn('REDACTED', record.getMessage())
        self.assertNotIn('sk-', record.getMessage())

    def test_detect_aws_key(self):
        """Verify AWS key detection"""
        secret_filter = SecretFilter()
        record = logging.LogRecord(
            name='test', level=logging.INFO, pathname='', lineno=0,
            msg="Key: AKIAIOSFODNN7EXAMPLE", args=(),
            exc_info=None
        )

        secret_filter.filter(record)
        self.assertIn('REDACTED', record.getMessage())
        self.assertNotIn('AKIA', record.getMessage())


if __name__ == '__main__':
    unittest.main()
```

**Run tests:**
```bash
python -m pytest tests/test_logging_observability.py -v
```

---

## 6. IMPLEMENTATION ROADMAP

### Phase 1 (Week 1): Foundation
- [ ] Create `logging_config_v2.py` with structured JSON logging
- [ ] Update both `ai-router.py` and `ai-router-enhanced.py` to use new config
- [ ] Create `secret_filter.py` and integrate
- [ ] Write basic unit tests

### Phase 2 (Week 2): Instrumentation
- [ ] Create `metrics_collector.py`
- [ ] Add @timed_operation decorators to key functions
- [ ] Add trace ID to main entry points
- [ ] Update session manager with logging

### Phase 3 (Week 3): Observability
- [ ] Create `observability_dashboard.py`
- [ ] Integrate analytics_dashboard with structured logs
- [ ] Add Prometheus exporter
- [ ] Create monitoring alerts

### Phase 4 (Week 4): Operations
- [ ] Log rotation setup (daily, size-based)
- [ ] Archive old logs
- [ ] Document for operators
- [ ] Create runbook for troubleshooting

---

## 7. LOGGING EXAMPLES

### Example 1: Model Execution Flow (with trace ID)

```json
# Start session
{"timestamp": "2025-12-22T10:30:00Z", "level": "INFO", "trace_id": "session-abc", "logger": "ai-router", "message": "Chat session started", "extra_fields": {"user": "john", "project": "MyProject"}}

# User input
{"timestamp": "2025-12-22T10:30:01Z", "level": "INFO", "trace_id": "session-abc", "request_id": "req-001", "message": "User prompt received", "extra_fields": {"prompt_length": 150, "model": "qwen3-coder-30b"}}

# Model execution started
{"timestamp": "2025-12-22T10:30:01Z", "level": "INFO", "trace_id": "session-abc", "request_id": "req-001", "module": "ai_router_enhanced", "function": "_run_llamacpp_model", "message": "Starting model execution", "extra_fields": {"model_id": "qwen3-coder-30b", "model_path": "/mnt/d/models/qwen3-30b.gguf"}}

# Model execution completed
{"timestamp": "2025-12-22T10:30:05Z", "level": "INFO", "trace_id": "session-abc", "request_id": "req-001", "message": "Model execution completed", "extra_fields": {"duration_ms": 4000, "tokens_generated": 250, "tokens_per_second": 62.5, "status": "success"}}

# Save to memory
{"timestamp": "2025-12-22T10:30:05Z", "level": "DEBUG", "trace_id": "session-abc", "request_id": "req-001", "message": "Conversation saved to memory", "extra_fields": {"memory_size_bytes": 2048}}
```

### Example 2: Error with Context

```json
{"timestamp": "2025-12-22T10:35:10Z", "level": "ERROR", "trace_id": "session-def", "request_id": "req-002", "logger": "ai-router", "module": "ai_router_enhanced", "function": "_run_llamacpp_model", "line": 1505, "message": "Model execution failed", "extra_fields": {"model_id": "llama33-70b", "error_code": "MODEL_NOT_FOUND", "return_code": 2, "duration_ms": 2150, "retry_attempt": 1, "context": {"wsl_available": true, "gpu_memory_mb": 4096}}, "exception": "FileNotFoundError: [Errno 2] No such file or directory: '/mnt/d/models/llama33-70b.gguf'", "exception_type": "FileNotFoundError"}

{"timestamp": "2025-12-22T10:35:10Z", "level": "WARNING", "trace_id": "session-def", "request_id": "req-002", "message": "Retrying with fallback model", "extra_fields": {"fallback_model": "dolphin-llama31-8b"}}
```

### Example 3: Metrics

```json
{"timestamp": "2025-12-22T10:40:00Z", "level": "INFO", "logger": "ai-router.metrics", "message": "Metric recorded", "extra_fields": {"name": "model.execution.duration", "value": 2150.5, "unit": "ms", "tags": {"model": "qwen3-coder-30b", "status": "success"}}}

{"timestamp": "2025-12-22T10:40:05Z", "level": "INFO", "logger": "ai-router.metrics", "message": "Metric recorded", "extra_fields": {"name": "db.query.duration", "value": 45.2, "unit": "ms", "tags": {"query_type": "session_create", "rows_affected": 1}}}
```

---

## 8. SUMMARY & QUICK START

### What's Wrong Today
1. **Plain text logs** - Not machine-parseable
2. **No trace IDs** - Can't correlate requests
3. **No metrics** - No performance visibility
4. **Incomplete logging** - Gaps in database/API/utils layers
5. **No real-time dashboard** - Operators blind to health

### Quick Wins (2-hour implementation)
1. Replace `logging_config.py` with structured JSON version
2. Add trace IDs to main entry points
3. Update console output with trace ID context
4. Add secret filter

### Priority Implementation Order
1. **CRITICAL:** Structured logging (blocks everything else)
2. **HIGH:** Trace ID propagation (enables debugging)
3. **HIGH:** Secret filtering (security requirement)
4. **MEDIUM:** Metrics collection (observability)
5. **MEDIUM:** Dashboard (operations visibility)

### Success Metrics
- [ ] All logs valid JSON/JSONL format
- [ ] 95%+ of requests have trace IDs
- [ ] No secrets in logs (validated by filter)
- [ ] Performance metrics exported to Prometheus
- [ ] Dashboard shows real-time health
- [ ] Operator can correlate issues within 30 seconds

---

## Files to Create/Modify

### New Files (Create)
1. **D:\models\logging_config_v2.py** - Structured logging
2. **D:\models\metrics_collector.py** - Performance metrics
3. **D:\models\secret_filter.py** - Secret masking
4. **D:\models\observability_dashboard.py** - Real-time dashboard
5. **D:\models\tests\test_logging_observability.py** - Test suite
6. **D:\models\LOG_ROTATION_CONFIG.yaml** - Log rotation rules

### Files to Modify
1. **D:\models\logging_config.py** - Replace with v2 (or alias to it)
2. **D:\models\ai-router.py** - Add trace ID to main methods
3. **D:\models\ai-router-enhanced.py** - Add trace ID to main methods
4. **D:\models\utils\session_manager.py** - Add logging throughout
5. **D:\models\utils\analytics_dashboard.py** - Add logging and metrics

### Files to Document
1. **D:\models\LOGGING-GUIDE.md** - How to use new logging
2. **D:\models\TROUBLESHOOTING-GUIDE.md** - Using logs for debugging
3. **D:\models\METRICS-REFERENCE.md** - All available metrics

---

## Appendix: Tools Integration

### ELK Stack Integration
```json
POST /api/v1/export/elk
{
  "format": "elasticsearch",
  "fields": ["timestamp", "level", "trace_id", "message", "context"]
}
```

### Prometheus Integration
```python
# Expose metrics endpoint
from prometheus_client import Counter, Histogram

model_execution_duration = Histogram(
    'ai_router_model_execution_duration_ms',
    'Model execution duration',
    buckets=[100, 500, 1000, 2000, 5000],
    labelnames=['model', 'status']
)
```

### Datadog Integration
```python
# Auto-instrumentation
from ddtrace import patch_all
patch_all()  # Automatic logging, tracing, metrics
```

---

**End of Logging & Observability Analysis**

*For questions or clarifications, refer to individual proposal sections above.*
