# AI Router - Observability Quick Reference
**Agent 7 Analysis - Executive Summary**

## Current State vs. Target State

| Aspect | Current | Target | Status |
|--------|---------|--------|--------|
| **Log Format** | Plain text | Structured JSON | ✗ Need to implement |
| **Request Correlation** | None | Trace ID propagation | ✗ Need to implement |
| **Performance Metrics** | Not tracked | Prometheus-ready | ✗ Need to implement |
| **Secret Protection** | Partial (code level) | Automatic (logging layer) | ⚠ Partial |
| **Error Context** | Minimal | Rich diagnostic info | ✗ Need to implement |
| **Real-time Visibility** | Dashboard-only stats | Live metrics + dashboard | ✗ Need to implement |
| **Log Retention** | No rotation | Daily + archive | ✗ Need to implement |
| **Audit Trail** | None | Complete operation history | ✗ Need to implement |

---

## 5 Critical Issues & Quick Fixes

### Issue #1: Plain Text Logs (Can't Parse)
**Problem:** Logs like `2025-12-18 15:30:44,483 - ERROR - llama.cpp execution failed with return code 2`
- Not machine-parseable
- No field extraction possible
- Can't aggregate/analyze at scale

**Fix (1 hour):** Replace `logging_config.py` with `logging_config_v2.py`
```python
from logging_config_v2 import setup_structured_logging
logger = setup_structured_logging(models_dir)  # JSON output now
```

**Result:** Logs become JSON, queryable instantly
```json
{"timestamp": "2025-12-18T15:30:44Z", "level": "ERROR", "model": "llama33-70b", "return_code": 2}
```

---

### Issue #2: No Request Correlation (Can't Debug)
**Problem:** Retries appear as separate logs, no way to correlate database queries to model execution
```
...Attempt 2/3
...Attempt 3/3
...All retry attempts exhausted
^ No connection between these!
```

**Fix (2 hours):** Add trace IDs to main entry points
```python
from logging_config_v2 import set_trace_id

def run_chat_session(self):
    trace_id = set_trace_id()  # Auto-generates UUID
    self.logger.info(f"Session started")  # trace_id included automatically
    # All logs now correlated by trace_id
```

**Result:** Can query "show me all operations for session X"

---

### Issue #3: No Performance Visibility (Can't Optimize)
**Problem:** No timing data, no bottleneck identification
- Is model slow or database?
- Which model is fastest?
- Are retries wasting time?

**Fix (3 hours):** Add metrics collection
```python
from metrics_collector import metrics

@metrics.timed_operation('model_execution', {'model': model_id})
def _run_llamacpp_model(self, ...):
    # timing captured automatically
    pass
```

**Result:** Prometheus metrics available
```
ai_router_model_execution_duration_ms{model="qwen3-coder-30b"} 2150.0
ai_router_model_execution_duration_ms{model="dolphin-llama31-8b"} 1850.0
```

---

### Issue #4: Secrets Could Be Logged (Security Risk)
**Problem:** If code logs user data, API keys, passwords - they end up in plain text logs

**Fix (30 minutes):** Add secret filter to all logs
```python
from logging_config_v2 import SecretFilter
# Already integrated in logging_config_v2!
```

**Result:** Automatic masking
```
Before: "Initializing with api_key=sk-1234567890abcdefgh"
After:  "Initializing with api_key=***API_KEY_REDACTED***"
```

---

### Issue #5: No Visibility into Database/Utils (Blind Spots)
**Problem:** Major components have zero logging
- `session_manager.py` - 50+ operations, no logs
- `analytics_dashboard.py` - No logging at all
- `template_manager.py` - No logging at all

**Fix (4 hours):** Add logging throughout core utils
```python
# In session_manager.py
logger = logging.getLogger('ai-router.session-manager')

def create_session(self, model_id):
    logger.info("Creating session", extra={
        'extra_fields': {'model': model_id}
    })
    # ... existing code ...
    logger.debug("Session created", extra={
        'extra_fields': {'session_id': session_id, 'duration_ms': elapsed}
    })
```

**Result:** Full visibility into 100% of operations

---

## Implementation Priority Matrix

```
High Impact,  High Effort  │  High Impact,  Low Effort
- Add metrics to all core  │  - Replace logging_config.py ✓
  modules (2-3 days)       │  - Add trace IDs (2 hours) ✓
                           │  - Add secret filter ✓
                           │
                           │  DO THESE FIRST
───────────────────────────┼──────────────────────────
Low Impact,   High Effort  │  Low Impact,   Low Effort
- Custom dashboards        │  - Add comments
- ELK integration          │  - Polish output
- Alerting system          │
```

### Recommended Phased Approach

**Phase 1 (CRITICAL - Day 1):**
```
[ ] 1. Copy logging_config_v2.py to project
[ ] 2. Update ai-router.py imports
[ ] 3. Update ai-router-enhanced.py imports
[ ] 4. Run tests - verify JSON output
```
**Time:** 1-2 hours | **Impact:** Immediately parse-able logs

**Phase 2 (HIGH - Days 2-3):**
```
[ ] 1. Add set_trace_id() to main_menu()
[ ] 2. Add set_trace_id() to run_chat_session()
[ ] 3. Add extra_fields to key log calls
[ ] 4. Test correlation - verify trace_id in all logs
```
**Time:** 2-3 hours | **Impact:** Can correlate operations

**Phase 3 (HIGH - Days 4-5):**
```
[ ] 1. Add logging to session_manager.py
[ ] 2. Add logging to analytics_dashboard.py
[ ] 3. Add logging to template_manager.py
[ ] 4. Add logging to provider modules
```
**Time:** 3-4 hours | **Impact:** Full visibility

**Phase 4 (MEDIUM - Week 2):**
```
[ ] 1. Create metrics_collector.py
[ ] 2. Add @timed_operation to key functions
[ ] 3. Create observability_dashboard.py
[ ] 4. Setup Prometheus exporter
```
**Time:** 4-6 hours | **Impact:** Performance metrics + dashboard

---

## Files Reference

### Analysis Report
**Location:** `D:\models\LOGGING-OBSERVABILITY-ANALYSIS.md`
- Full analysis of all 5 issues
- 4 concrete proposals with code examples
- Risk assessment and implementation roadmap
- Test suite requirements

### Implementation Files (Ready to Use)

**1. Enhanced Logging Config**
```
Location: D:\models\logging_config_v2.py
Status: READY TO USE
- Structured JSON logging
- Trace ID support
- Secret filtering
- Dual output (file + console)
```

**2. Base Provider Already Has Safety**
```
Location: D:\models\providers\base_provider.py
Has: _safe_config() method that masks API keys
Status: PARTIAL (only for this module)
```

**3. Existing Log Files**
```
Location: D:\models\logs/
Size: 30KB (7 daily files)
Format: Plain text
Status: Convert to JSON with new config
```

---

## How to Use the New Logging (Quick Start)

### 1. Replace logging config in main scripts

```python
# OLD (in ai-router.py or ai-router-enhanced.py)
from logging_config import setup_logging
logger = setup_logging(self.models_dir)

# NEW
from logging_config_v2 import setup_structured_logging, set_trace_id
logger = setup_structured_logging(self.models_dir)
```

### 2. Add trace ID at session start

```python
def main_menu(self):
    """Main entry point"""
    trace_id = set_trace_id()  # Generates "req-abc123def456"
    logger.info("Main menu displayed", extra={
        'extra_fields': {'session_type': 'interactive'}
    })
    # ... rest of code ...
```

### 3. Log with context

```python
logger.info("Model execution completed", extra={
    'request_id': operation_id,  # Optional operation-level ID
    'extra_fields': {
        'model': model_id,
        'duration_ms': 2150,
        'tokens_generated': 250,
        'status': 'success'
    }
})
```

### 4. Automatic secret masking

```python
# This is logged as-is:
logger.info("Initializing", extra={'extra_fields': {
    'api_key': 'sk-1234567890abcdefgh',
    'user_email': 'user@example.com'
}})

# Output automatically becomes:
# {"message": "Initializing", "extra_fields": {
#   "api_key": "***API_KEY_REDACTED***",
#   "user_email": "***EMAIL_REDACTED***"
# }}
```

### 5. View structured logs

```bash
# Read JSON logs
cat logs/ai-router-20251222.jsonl | jq '.[]'

# Filter by trace ID
cat logs/ai-router-20251222.jsonl | jq '.[] | select(.trace_id == "req-abc123")'

# Filter by error
cat logs/ai-router-20251222.jsonl | jq '.[] | select(.level == "ERROR")'

# Get all model execution times
cat logs/ai-router-20251222.jsonl | jq '.[] | select(.extra_fields.duration_ms) | {model: .extra_fields.model, duration: .extra_fields.duration_ms}'
```

---

## Metrics Quick Reference

### Performance Metrics to Track

**Model Execution:**
```
metric: model.execution.duration
tags: [model, status]
unit: milliseconds
Example: model.execution.duration{model="qwen3-coder-30b", status="success"} = 2150
```

**Database Operations:**
```
metric: db.query.duration
tags: [query_type, table]
unit: milliseconds
Example: db.query.duration{query_type="session_create", table="sessions"} = 45
```

**Session Management:**
```
metric: session.duration
tags: [project]
unit: seconds
Example: session.duration{project="MyProject"} = 3600
```

**Error Rates:**
```
metric: error.rate
tags: [component, error_type]
unit: percent
Example: error.rate{component="model_execution", error_type="timeout"} = 5.2
```

---

## Troubleshooting Guide

### Problem: Logs still in plain text
**Solution:** Make sure using `logging_config_v2.py` not old `logging_config.py`
```python
# Check imports
from logging_config_v2 import setup_structured_logging  # ✓ Correct
from logging_config import setup_logging  # ✗ Wrong
```

### Problem: Trace ID not showing up
**Solution:** Must call `set_trace_id()` at start of operation
```python
from logging_config_v2 import set_trace_id
trace_id = set_trace_id()  # Must do this FIRST
logger.info("Now trace_id will be included")
```

### Problem: Too many log files accumulating
**Solution:** Setup log rotation (future Phase 4)
```python
# For now, manually archive old logs
# Recommended: Logs > 30 days old → archive directory
```

### Problem: Logs showing secrets
**Solution:** Ensure using `logging_config_v2.py` which has `SecretFilter`
```python
# secret_filter.py patterns include:
# - api_key, apikey, api-key
# - password, passwd
# - token, auth_token, bearer
# - OpenAI format (sk-...)
# - AWS format (AKIA...)
# - Email addresses
# - Phone numbers
```

---

## Success Criteria

When complete, you should be able to:

1. ✓ Read logs as JSON and extract fields
   ```bash
   cat logs/*.jsonl | jq '.[] | {time: .timestamp, error: .level}'
   ```

2. ✓ Correlate all operations by session
   ```bash
   cat logs/*.jsonl | jq '.[] | select(.trace_id == "session-123")'
   ```

3. ✓ Measure performance
   ```bash
   cat logs/*.jsonl | jq '.[] | select(.extra_fields.duration_ms) | .extra_fields.duration_ms' | stats
   ```

4. ✓ Find errors with context
   ```bash
   cat logs/*.jsonl | jq '.[] | select(.level == "ERROR")' | head -1
   # Shows: error_code, return_code, model, context, stack trace
   ```

5. ✓ Verify no secrets logged
   ```bash
   grep -r "api_key\|password\|token" logs/
   # Should only show REDACTED entries
   ```

---

## Next Steps

1. **Read full analysis:** `LOGGING-OBSERVABILITY-ANALYSIS.md`
2. **Copy new config:** `logging_config_v2.py` to project
3. **Update main scripts:** Replace imports in `ai-router.py` and `ai-router-enhanced.py`
4. **Add trace IDs:** 2-3 lines per main method
5. **Test:** Run application, check `logs/*.jsonl`
6. **Phase 2:** Add logging to utils modules
7. **Phase 3:** Add metrics collection
8. **Phase 4:** Setup monitoring/alerting

---

## Support & Questions

All proposals include:
- Working code examples
- Integration patterns
- Test cases
- Risk mitigation

See detailed sections in `LOGGING-OBSERVABILITY-ANALYSIS.md` for:
- Implementation examples
- API documentation
- Troubleshooting guide
- Tool integration (ELK, Prometheus, Datadog)

---

**Status:** Analysis complete, implementation ready
**Effort estimate:** 15-20 hours for full implementation
**Recommended timeline:** 2 weeks (phased approach)
**Quick wins:** 2 hours to Phase 1 (structured JSON logging)
