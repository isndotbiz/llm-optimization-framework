# MCP TOOLS SECURITY FIXES - IMPLEMENTATION GUIDE

## Overview
This guide provides concrete code implementations to fix all identified security vulnerabilities in the MCP Server.

---

## FIX 1: PATH TRAVERSAL PROTECTION

### File: `D:\models\mcp_tools\mcp_server.py`

### Add Import
```python
import os
from pathlib import PureWindowsPath, PurePosixPath
```

### Add Validation Class (After Imports, Before MCPServer Class)
```python
class SecurityValidator:
    """Security validation for MCP Server"""

    MAX_PROJECT_NAME_LEN = 50
    MAX_QUERY_LEN = 500
    MAX_FILE_SIZE_MB = 100
    RESERVED_NAMES = {'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'LPT1'}

    @staticmethod
    def validate_project_name(name: str) -> tuple[bool, str]:
        """
        Validate project_name doesn't contain path traversal
        Returns: (is_valid, error_message)
        """
        if not name or not isinstance(name, str):
            return False, "Project name required"

        name = name.strip()
        if not name:
            return False, "Project name cannot be empty"

        if len(name) > SecurityValidator.MAX_PROJECT_NAME_LEN:
            return False, f"Project name exceeds {SecurityValidator.MAX_PROJECT_NAME_LEN} chars"

        # Block path traversal patterns
        if '..' in name or '/' in name or '\\' in name:
            return False, "Project name contains invalid characters"

        # Block hidden directories
        if name.startswith('.'):
            return False, "Project name cannot start with dot"

        # Block absolute paths
        if os.path.isabs(name):
            return False, "Project name must be relative"

        # Block Windows reserved names
        if name.upper() in SecurityValidator.RESERVED_NAMES:
            return False, f"'{name}' is a reserved name"

        # Only alphanumeric, underscore, hyphen, space
        import re
        if not re.match(r'^[a-zA-Z0-9_\- ]+$', name):
            return False, "Project name contains invalid characters"

        return True, "OK"

    @staticmethod
    def validate_file_within_base(file_path: str, allowed_base: Path) -> tuple[bool, str]:
        """
        Verify file_path is within allowed_base directory
        Resolves symlinks and relative paths safely
        """
        try:
            # Resolve both paths to absolute
            requested = Path(file_path).resolve()
            base = Path(allowed_base).resolve()

            # Verify requested is under base
            requested.relative_to(base)
            return True, "OK"

        except ValueError:
            return False, "Path outside allowed directory"
        except Exception as e:
            logger.warning(f"Path validation error: {type(e).__name__}")
            return False, "Invalid path"

    @staticmethod
    def validate_query(query: str) -> tuple[bool, str]:
        """Validate query parameter"""
        if not query or not isinstance(query, str):
            return False, "Query required"

        if len(query) > SecurityValidator.MAX_QUERY_LEN:
            return False, f"Query exceeds {SecurityValidator.MAX_QUERY_LEN} characters"

        return True, "OK"

    @staticmethod
    def validate_results(results: Any) -> tuple[bool, str]:
        """Verify results is JSON-serializable"""
        try:
            serialized = json.dumps(results)
            size_mb = len(serialized.encode('utf-8')) / (1024 * 1024)

            if size_mb > SecurityValidator.MAX_FILE_SIZE_MB:
                return False, f"Results exceed {SecurityValidator.MAX_FILE_SIZE_MB}MB"

            return True, "OK"
        except (TypeError, ValueError):
            return False, "Results not JSON-serializable"
```

### Update read_pdf Method
```python
def read_pdf(self, file_path: str) -> Dict[str, Any]:
    """Extract text and metadata from PDF files"""
    try:
        # SECURITY FIX: Validate file path
        pdf_path = Path(file_path)
        valid, msg = SecurityValidator.validate_file_within_base(
            file_path,
            Path.cwd()
        )

        if not valid:
            logger.warning(f"Invalid PDF path attempted")
            return {
                'success': False,
                'error': 'Invalid file path',
                'error_code': 'INVALID_PATH'
            }

        if not pdf_path.exists():
            logger.warning(f"PDF file not found")
            return {
                'success': False,
                'error': 'File not found',
                'error_code': 'FILE_NOT_FOUND'
            }

        # ... rest of method unchanged ...

    except Exception as e:
        logger.error(f"PDF read failed: {type(e).__name__}", exc_info=True)
        return {
            'success': False,
            'error': 'Unable to process PDF',
            'error_code': 'PDF_ERROR'
        }
```

### Update store_web_data Method
```python
def store_web_data(self, query: str, results: Union[Dict, List, str],
                   project_name: str) -> Dict[str, Any]:
    """Store web search results with validation"""
    try:
        # SECURITY FIX: Validate inputs
        valid, msg = SecurityValidator.validate_project_name(project_name)
        if not valid:
            logger.warning(f"Invalid project name attempted: {msg}")
            return {
                'success': False,
                'error': msg,
                'error_code': 'INVALID_PROJECT_NAME'
            }

        valid, msg = SecurityValidator.validate_query(query)
        if not valid:
            logger.warning(f"Invalid query: {msg}")
            return {
                'success': False,
                'error': msg,
                'error_code': 'INVALID_QUERY'
            }

        valid, msg = SecurityValidator.validate_results(results)
        if not valid:
            logger.warning(f"Invalid results: {msg}")
            return {
                'success': False,
                'error': msg,
                'error_code': 'INVALID_RESULTS'
            }

        # Create project directory structure
        project_dir = self.base_projects_dir / project_name

        # SECURITY FIX: Verify directory is within base
        valid, msg = SecurityValidator.validate_file_within_base(
            str(project_dir),
            self.base_projects_dir
        )
        if not valid:
            logger.error(f"Project directory escape attempt detected")
            return {
                'success': False,
                'error': 'Invalid project directory',
                'error_code': 'INVALID_PROJECT_DIR'
            }

        data_dir = project_dir / 'data' / 'web_search'

        # ... rest of method ...

    except Exception as e:
        logger.error(f"Store failed: {type(e).__name__}", exc_info=True)
        return {
            'success': False,
            'error': 'Unable to store data',
            'error_code': 'STORAGE_ERROR'
        }
```

### Update retrieve_stored_data Method
```python
def retrieve_stored_data(self, project_name: str,
                        query: Optional[str] = None,
                        date_range: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Retrieve stored data with validation"""
    try:
        # SECURITY FIX: Validate project name
        valid, msg = SecurityValidator.validate_project_name(project_name)
        if not valid:
            logger.warning(f"Invalid project name in retrieve: {msg}")
            return {
                'success': False,
                'error': msg,
                'error_code': 'INVALID_PROJECT_NAME'
            }

        if query:
            valid, msg = SecurityValidator.validate_query(query)
            if not valid:
                return {
                    'success': False,
                    'error': msg,
                    'error_code': 'INVALID_QUERY'
                }

        # ... rest of method unchanged ...

    except Exception as e:
        logger.error(f"Retrieve failed: {type(e).__name__}", exc_info=True)
        return {
            'success': False,
            'error': 'Unable to retrieve data',
            'error_code': 'RETRIEVAL_ERROR'
        }
```

### Update store_pdf Method
```python
def store_pdf(self, pdf_path: str, project_name: str,
              tags: Optional[List[str]] = None) -> Dict[str, Any]:
    """Store PDF with path validation"""
    try:
        # SECURITY FIX: Validate project name
        valid, msg = SecurityValidator.validate_project_name(project_name)
        if not valid:
            logger.warning(f"Invalid project name: {msg}")
            return {
                'success': False,
                'error': msg,
                'error_code': 'INVALID_PROJECT_NAME'
            }

        # SECURITY FIX: Validate file path
        valid, msg = SecurityValidator.validate_file_within_base(
            pdf_path,
            Path.cwd()
        )
        if not valid:
            logger.warning(f"Invalid PDF path")
            return {
                'success': False,
                'error': 'Invalid file path',
                'error_code': 'INVALID_PATH'
            }

        source_path = Path(pdf_path)

        if not source_path.exists():
            logger.warning(f"PDF not found")
            return {
                'success': False,
                'error': 'File not found',
                'error_code': 'FILE_NOT_FOUND'
            }

        # ... rest of method unchanged ...

    except Exception as e:
        logger.error(f"PDF storage failed: {type(e).__name__}", exc_info=True)
        return {
            'success': False,
            'error': 'Unable to store PDF',
            'error_code': 'PDF_STORAGE_ERROR'
        }
```

---

## FIX 2: RATE LIMITING

### Add to MCPServer.__init__
```python
from collections import defaultdict
import time

def __init__(self):
    # ... existing init code ...
    self.rate_limiter = RateLimiter()
    logger.info("Rate limiter initialized")
```

### Add RateLimiter Class (Before MCPServer class)
```python
class RateLimiter:
    """Rate limiting to prevent DoS attacks"""

    def __init__(self, requests_per_minute: int = 60,
                 requests_per_hour: int = 1000):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.request_times = defaultdict(list)
        self.lock = __import__('threading').Lock()

    def check_rate_limit(self, client_id: str) -> tuple[bool, str]:
        """
        Check if client has exceeded rate limits
        Returns: (allowed, message)
        """
        with self.lock:
            now = time.time()
            one_minute_ago = now - 60
            one_hour_ago = now - 3600

            # Clean old entries
            self.request_times[client_id] = [
                t for t in self.request_times[client_id]
                if t > one_hour_ago
            ]

            # Check minute limit
            recent = sum(1 for t in self.request_times[client_id]
                        if t > one_minute_ago)
            if recent >= self.requests_per_minute:
                logger.warning(f"Rate limit exceeded for {client_id} (per minute)")
                return False, "Rate limit exceeded"

            # Check hour limit
            if len(self.request_times[client_id]) >= self.requests_per_hour:
                logger.warning(f"Quota exceeded for {client_id} (per hour)")
                return False, "Quota exceeded"

            self.request_times[client_id].append(now)
            return True, "OK"
```

### Update handle_request Method
```python
def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
    """Handle JSON-RPC request with rate limiting"""
    try:
        # SECURITY FIX: Rate limiting
        client_id = request.get('client_id', 'unknown')
        allowed, msg = self.rate_limiter.check_rate_limit(client_id)

        if not allowed:
            logger.warning(f"Request rate limited for {client_id}")
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': -32000,
                    'message': msg
                },
                'id': request.get('id')
            }

        method = request.get('method')
        params = request.get('params', {})
        request_id = request.get('id')

        if method not in self.tools:
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': -32601,
                    'message': 'Method not found'
                },
                'id': request_id
            }

        # Call the tool
        result = self.tools[method](**params)

        return {
            'jsonrpc': '2.0',
            'result': result,
            'id': request_id
        }

    except Exception as e:
        logger.error(f"Request handling failed: {type(e).__name__}", exc_info=True)
        return {
            'jsonrpc': '2.0',
            'error': {
                'code': -32603,
                'message': 'Internal error'
            },
            'id': request.get('id')
        }
```

---

## FIX 3: AUDIT LOGGING

### Replace Logging Configuration
```python
import logging
from logging.handlers import RotatingFileHandler

# Configure logging with rotation
def configure_logging():
    """Configure logging with security audit trail"""

    # Main logger
    logger = logging.getLogger('mcp_server')
    logger.setLevel(logging.INFO)

    # Remove existing handlers
    logger.handlers = []

    # Main log with rotation (10MB files, keep 5)
    main_handler = RotatingFileHandler(
        Path(__file__).parent / 'mcp_server.log',
        maxBytes=10_000_000,
        backupCount=5
    )
    main_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    main_handler.setFormatter(main_formatter)
    logger.addHandler(main_handler)

    # Audit log (separate, with rotation)
    audit_logger = logging.getLogger('mcp_audit')
    audit_logger.setLevel(logging.INFO)
    audit_logger.handlers = []

    audit_handler = RotatingFileHandler(
        Path(__file__).parent / 'mcp_audit.log',
        maxBytes=20_000_000,
        backupCount=10
    )
    audit_formatter = logging.Formatter(
        '%(asctime)s - CLIENT=%(client_id)s - REQ=%(request_id)s - '
        'METHOD=%(method)s - STATUS=%(status)s - %(message)s'
    )
    audit_handler.setFormatter(audit_formatter)
    audit_logger.addHandler(audit_handler)

    # Console handler (stderr)
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(main_formatter)
    logger.addHandler(console_handler)

    return logger, audit_logger

# Replace lines 17-26 with:
logger, audit_logger = configure_logging()
```

### Add Audit Logging to handle_request
```python
def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
    """Handle JSON-RPC request with audit logging"""
    try:
        client_id = request.get('client_id', 'unknown')
        method = request.get('method')
        request_id = request.get('id')

        # Check rate limit
        allowed, msg = self.rate_limiter.check_rate_limit(client_id)
        if not allowed:
            audit_logger.warning(
                f"Request rejected due to rate limiting",
                extra={
                    'client_id': client_id,
                    'request_id': request_id,
                    'method': method,
                    'status': 'RATE_LIMITED'
                }
            )
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': -32000,
                    'message': msg
                },
                'id': request_id
            }

        if method not in self.tools:
            audit_logger.warning(
                f"Unknown method requested",
                extra={
                    'client_id': client_id,
                    'request_id': request_id,
                    'method': method,
                    'status': 'METHOD_NOT_FOUND'
                }
            )
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': -32601,
                    'message': 'Method not found'
                },
                'id': request_id
            }

        # Call the tool
        result = self.tools[method](**request.get('params', {}))

        # Log success
        status = 'SUCCESS' if result.get('success', False) else 'FAILED'
        audit_logger.info(
            f"Tool executed successfully",
            extra={
                'client_id': client_id,
                'request_id': request_id,
                'method': method,
                'status': status
            }
        )

        return {
            'jsonrpc': '2.0',
            'result': result,
            'id': request_id
        }

    except Exception as e:
        audit_logger.error(
            f"Request processing failed: {type(e).__name__}",
            extra={
                'client_id': request.get('client_id', 'unknown'),
                'request_id': request.get('id'),
                'method': request.get('method'),
                'status': 'ERROR'
            }
        )
        logger.error(f"Exception details", exc_info=True)

        return {
            'jsonrpc': '2.0',
            'error': {
                'code': -32603,
                'message': 'Internal error'
            },
            'id': request.get('id')
        }
```

---

## FIX 4: OPERATION TIMEOUTS

### Add Timeout Wrapper (Before MCPServer class)
```python
import signal
import functools

class TimeoutError(Exception):
    """Raised when operation exceeds timeout"""
    pass

def timeout(seconds: int):
    """Decorator to add timeout to function calls"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            def handler(signum, frame):
                raise TimeoutError(f"Operation exceeded {seconds} second timeout")

            # Set signal handler
            old_handler = signal.signal(signal.SIGALRM, handler)
            signal.alarm(seconds)

            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)

            return result

        return wrapper
    return decorator
```

### Apply Timeouts to Methods
```python
@timeout(30)
def read_pdf(self, file_path: str) -> Dict[str, Any]:
    """Extract text and metadata from PDF files (30 second timeout)"""
    # ... method code ...

@timeout(10)
def store_web_data(self, query: str, results: Union[Dict, List, str],
                   project_name: str) -> Dict[str, Any]:
    """Store web search results (10 second timeout)"""
    # ... method code ...

@timeout(20)
def retrieve_stored_data(self, project_name: str,
                        query: Optional[str] = None,
                        date_range: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Retrieve stored data (20 second timeout)"""
    # ... method code ...

@timeout(15)
def store_pdf(self, pdf_path: str, project_name: str,
              tags: Optional[List[str]] = None) -> Dict[str, Any]:
    """Store PDF (15 second timeout)"""
    # ... method code ...
```

---

## TESTING THE FIXES

### Test 1: Path Traversal Prevention
```python
def test_path_traversal():
    """Test that path traversal is blocked"""
    server = MCPServer()

    # Should fail
    result = server.read_pdf("../../../../windows/system32/drivers/etc/hosts")
    assert not result['success'], "Path traversal should be blocked"
    assert 'Invalid' in result.get('error', ''), "Should return generic error"

    # Should succeed with valid path
    result = server.read_pdf("D:\\models\\test.pdf")
    # Check response doesn't contain full path
    assert "D:\\" not in str(result.get('file_path', '')), "Path should not be in response"
```

### Test 2: Input Validation
```python
def test_input_validation():
    """Test input validation"""
    server = MCPServer()

    # Large query
    result = server.store_web_data(
        "x" * 1000,
        {},
        "test"
    )
    assert not result['success'], "Should reject oversized query"

    # Invalid project name
    result = server.store_web_data(
        "test",
        {},
        "../../../evil"
    )
    assert not result['success'], "Should reject traversal in project name"
```

### Test 3: Rate Limiting
```python
def test_rate_limiting():
    """Test rate limiting is enforced"""
    server = MCPServer()

    client_id = "test_client"

    # Make 60 requests (should pass)
    for i in range(60):
        allowed, msg = server.rate_limiter.check_rate_limit(client_id)
        assert allowed, f"Request {i} should be allowed"

    # 61st request should fail
    allowed, msg = server.rate_limiter.check_rate_limit(client_id)
    assert not allowed, "Should rate limit after 60 requests"
```

### Test 4: Audit Logging
```python
def test_audit_logging():
    """Test audit log is created and contains expected data"""
    server = MCPServer()

    # Make a request
    request = {
        "jsonrpc": "2.0",
        "method": "store_web_data",
        "params": {
            "query": "test",
            "results": {"data": "test"},
            "project_name": "test_project"
        },
        "client_id": "test_client",
        "id": 1
    }

    server.handle_request(request)

    # Check audit log exists
    audit_log = Path("D:\\models\\mcp_tools\\mcp_audit.log")
    assert audit_log.exists(), "Audit log should be created"

    # Check log contains required fields
    with open(audit_log) as f:
        content = f.read()

    assert "test_client" in content, "Client ID should be logged"
    assert "store_web_data" in content, "Method should be logged"
```

---

## DEPLOYMENT CHECKLIST

- [ ] Backup existing mcp_server.py
- [ ] Apply all fixes from sections 1-4
- [ ] Run all tests
- [ ] Check both log files are created
- [ ] Verify rate limiting works
- [ ] Test with legitimate client requests
- [ ] Monitor logs for new error patterns
- [ ] Document any behavioral changes for users
- [ ] Update API documentation with rate limits

---

## MIGRATION GUIDE FOR USERS

### Before and After

**Before (Vulnerable):**
```json
{
  "method": "read_pdf",
  "params": {
    "file_path": "C:\\arbitrary\\path\\file.pdf"
  }
}
```

**After (Secure):**
```json
{
  "method": "read_pdf",
  "params": {
    "file_path": "C:\\arbitrary\\path\\file.pdf"
  },
  "client_id": "my_client"
}
```

**Error Messages Changed:**
```
Before: "Error: [Errno 2] No such file or directory: 'C:\\sensitive\\file.pdf'"
After: "File not found"
```

### Rate Limits
- 60 requests per minute per client
- 1000 requests per hour per client
- Contact admin if limits need adjustment

---

## VERIFICATION AFTER DEPLOYMENT

1. Check logs are rotating properly
2. Verify audit.log is created
3. Test rate limiting is working
4. Confirm errors are generic (no path info)
5. Review first 100 audit log entries for expected format
6. Monitor for any legitimate client issues
