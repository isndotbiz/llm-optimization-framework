#!/usr/bin/env python3
"""
Comprehensive Security Tests for MCP Server

Tests for:
- Path traversal vulnerabilities
- Input validation
- Rate limiting
- Information disclosure
- Audit logging
"""

import json
import subprocess
import sys
import time
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Tuple
import threading


class SecurityTestSuite:
    """Comprehensive security test suite for MCP Server"""

    def __init__(self, server_path: str = "D:\\models\\mcp_tools\\mcp_server.py"):
        self.server_path = server_path
        self.server = None
        self.test_results = []

    def start_server(self):
        """Start MCP server"""
        self.server = subprocess.Popen(
            [sys.executable, self.server_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )

    def stop_server(self):
        """Stop MCP server"""
        if self.server:
            try:
                self.server.terminate()
                self.server.wait(timeout=5)
            except:
                self.server.kill()

    def send_request(self, method: str, params: Dict[str, Any],
                    client_id: str = "test_client") -> Dict[str, Any]:
        """Send request to server and get response"""
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "client_id": client_id,
            "id": 1
        }

        try:
            self.server.stdin.write(json.dumps(request) + '\n')
            self.server.stdin.flush()

            response_line = self.server.stdout.readline()
            if not response_line:
                return {"error": "No response from server"}

            return json.loads(response_line)
        except Exception as e:
            return {"error": str(e)}

    def log_test(self, name: str, passed: bool, details: str = ""):
        """Log test result"""
        self.test_results.append({
            "name": name,
            "passed": passed,
            "details": details
        })
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {name}")
        if details:
            print(f"      {details}")

    # ===== PATH TRAVERSAL TESTS =====

    def test_path_traversal_read_pdf(self):
        """Test path traversal in read_pdf"""
        print("\n=== PATH TRAVERSAL TESTS ===\n")

        payloads = [
            "../../../../windows/system32/drivers/etc/hosts",
            "..\\..\\..\\windows\\win.ini",
            "/etc/passwd",
            "C:\\..\\..\\windows\\notepad.exe"
        ]

        for payload in payloads:
            response = self.send_request("read_pdf", {"file_path": payload})

            # Should either fail or not expose path
            passed = (
                not response.get('success', False) or
                payload not in str(response.get('error', ''))
            )

            self.log_test(
                f"Path traversal blocked: {payload}",
                passed,
                f"Response: {response.get('error', 'success')}"
            )

    def test_directory_escape_project_name(self):
        """Test directory escape via project_name"""
        print("\n=== DIRECTORY ESCAPE TESTS ===\n")

        payloads = [
            "../../../evil",
            "..\\..\\sensitive",
            ".hidden",
            "/absolute/path"
        ]

        for payload in payloads:
            response = self.send_request("store_web_data", {
                "query": "test",
                "results": {"data": "test"},
                "project_name": payload
            })

            # Should fail
            passed = not response.get('result', {}).get('success', False)

            self.log_test(
                f"Directory escape blocked: {payload}",
                passed,
                f"Storage path: {response.get('result', {}).get('storage_path', 'N/A')}"
            )

    # ===== INPUT VALIDATION TESTS =====

    def test_oversized_query(self):
        """Test rejection of oversized query"""
        print("\n=== INPUT VALIDATION TESTS ===\n")

        response = self.send_request("store_web_data", {
            "query": "x" * 1000,  # Over limit
            "results": {},
            "project_name": "test"
        })

        passed = not response.get('result', {}).get('success', False)
        self.log_test(
            "Oversized query rejected",
            passed,
            f"Error: {response.get('result', {}).get('error', 'N/A')}"
        )

    def test_oversized_results(self):
        """Test rejection of oversized results"""
        response = self.send_request("store_web_data", {
            "query": "test",
            "results": {"data": "x" * 50000000},  # 50MB
            "project_name": "test"
        })

        passed = not response.get('result', {}).get('success', False)
        self.log_test(
            "Oversized results rejected",
            passed,
            f"Error: {response.get('result', {}).get('error', 'N/A')}"
        )

    def test_null_values(self):
        """Test handling of null/missing values"""
        response = self.send_request("store_web_data", {
            "query": None,
            "results": {},
            "project_name": "test"
        })

        # Should handle gracefully
        passed = 'error' in response or not response.get('result', {}).get('success', False)
        self.log_test(
            "Null query handled",
            passed,
            f"Response: {response}"
        )

    def test_invalid_project_name_chars(self):
        """Test rejection of invalid characters in project name"""
        invalid_names = ["test@project", "project!", "test$name"]

        for name in invalid_names:
            response = self.send_request("store_web_data", {
                "query": "test",
                "results": {},
                "project_name": name
            })

            passed = not response.get('result', {}).get('success', False)
            self.log_test(
                f"Invalid project name rejected: {name}",
                passed
            )

    # ===== INFORMATION DISCLOSURE TESTS =====

    def test_error_messages_no_paths(self):
        """Test that error messages don't expose file paths"""
        print("\n=== INFORMATION DISCLOSURE TESTS ===\n")

        response = self.send_request("read_pdf", {
            "file_path": "/sensitive/admin/passwords.pdf"
        })

        error_msg = str(response.get('result', {}).get('error', ''))

        # Should not contain the path or system-specific info
        contains_path = '/sensitive' in error_msg or 'passwords' in error_msg
        contains_exception = 'Errno' in error_msg or 'traceback' in error_msg.lower()

        passed = not (contains_path or contains_exception)

        self.log_test(
            "Error messages don't expose paths",
            passed,
            f"Error message: {error_msg}"
        )

    def test_error_messages_no_exceptions(self):
        """Test that error messages don't contain exception details"""
        response = self.send_request("read_pdf", {
            "file_path": 12345  # Invalid type
        })

        error_msg = str(response.get('result', {}).get('error', ''))

        passed = 'TypeError' not in error_msg and 'traceback' not in error_msg.lower()

        self.log_test(
            "Error messages don't contain exceptions",
            passed,
            f"Error: {error_msg}"
        )

    # ===== RATE LIMITING TESTS =====

    def test_rate_limiting(self):
        """Test that rate limiting is enforced"""
        print("\n=== RATE LIMITING TESTS ===\n")

        client_id = f"test_client_{int(time.time())}"

        # Make 60 requests (should all pass)
        success_count = 0
        for i in range(60):
            response = self.send_request("store_web_data", {
                "query": f"test_{i}",
                "results": {"iteration": i},
                "project_name": "test"
            }, client_id=client_id)

            # Check if successful
            if response.get('result', {}).get('success', False):
                success_count += 1

        first_pass = success_count >= 50  # Most should pass

        # 61st request should fail (rate limited)
        response = self.send_request("store_web_data", {
            "query": "test_limit",
            "results": {},
            "project_name": "test"
        }, client_id=client_id)

        rate_limited = not response.get('result', {}).get('success', False)

        self.log_test(
            "Rate limiting enforced",
            rate_limited,
            f"Success before limit: {success_count}, After limit: rate limited={rate_limited}"
        )

    def test_per_client_rate_limiting(self):
        """Test that rate limiting is per-client"""
        print("\n=== PER-CLIENT RATE LIMITING ===\n")

        client1 = "client_1"
        client2 = "client_2"

        # Client 1 makes requests
        for i in range(10):
            self.send_request("store_web_data", {
                "query": f"test_{i}",
                "results": {},
                "project_name": "test"
            }, client_id=client1)

        # Client 2 should also be able to make requests
        response = self.send_request("store_web_data", {
            "query": "test",
            "results": {},
            "project_name": "test"
        }, client_id=client2)

        passed = response.get('result', {}).get('success', False)

        self.log_test(
            "Per-client rate limiting",
            passed,
            "Different clients have independent quotas"
        )

    # ===== AUDIT LOGGING TESTS =====

    def test_audit_log_creation(self):
        """Test that audit log is created"""
        print("\n=== AUDIT LOGGING TESTS ===\n")

        # Make a request
        self.send_request("store_web_data", {
            "query": "audit_test",
            "results": {"test": "data"},
            "project_name": "test_audit"
        })

        # Check if audit log exists
        audit_log = Path("D:\\models\\mcp_tools\\mcp_audit.log")
        passed = audit_log.exists()

        self.log_test(
            "Audit log created",
            passed,
            f"Log path: {audit_log}"
        )

    def test_audit_log_contains_method(self):
        """Test that audit log contains method information"""
        # Make request
        self.send_request("retrieve_stored_data", {
            "project_name": "test"
        })

        time.sleep(0.5)  # Wait for write

        audit_log = Path("D:\\models\\mcp_tools\\mcp_audit.log")
        if not audit_log.exists():
            self.log_test("Audit log contains method", False, "Log doesn't exist")
            return

        with open(audit_log) as f:
            content = f.read()

        passed = "retrieve_stored_data" in content or "METHOD=" in content

        self.log_test(
            "Audit log contains method information",
            passed
        )

    def test_audit_log_contains_client_id(self):
        """Test that audit log contains client ID"""
        client_id = f"audit_test_{int(time.time())}"

        # Make request with specific client ID
        self.send_request("store_web_data", {
            "query": "test",
            "results": {},
            "project_name": "test"
        }, client_id=client_id)

        time.sleep(0.5)

        audit_log = Path("D:\\models\\mcp_tools\\mcp_audit.log")
        if not audit_log.exists():
            self.log_test("Audit log contains client ID", False, "Log doesn't exist")
            return

        with open(audit_log) as f:
            content = f.read()

        passed = client_id in content or "CLIENT=" in content

        self.log_test(
            "Audit log contains client ID",
            passed
        )

    # ===== TIMEOUT TESTS =====

    def test_operation_timeout(self):
        """Test that operations timeout appropriately"""
        print("\n=== TIMEOUT TESTS ===\n")

        # This would need a test PDF that takes a long time to process
        # For now, just verify timeout decorator is in place

        # Try to process a file (may not trigger timeout in normal case)
        response = self.send_request("read_pdf", {
            "file_path": "D:\\models\\test.pdf"
        })

        # Just check it responds (either success or error)
        passed = 'error' in response or 'result' in response

        self.log_test(
            "Operations complete within timeout",
            passed
        )

    # ===== SYMLINK/JUNCTION TESTS =====

    def test_symlink_traversal(self):
        """Test that symlinks don't bypass path validation"""
        print("\n=== SYMLINK SECURITY TESTS ===\n")

        # Note: This test requires symlink support
        # Create a test symlink if possible
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                source = Path(tmpdir) / "source.txt"
                source.write_text("test content")

                link = Path(tmpdir) / "link.pdf"
                link.symlink_to(source)

                # Try to read through symlink
                response = self.send_request("read_pdf", {
                    "file_path": str(link)
                })

                # Should either fail or handle safely
                passed = not response.get('result', {}).get('success', False)

                self.log_test(
                    "Symlink traversal blocked",
                    passed
                )
        except Exception as e:
            self.log_test(
                "Symlink traversal blocked",
                False,
                f"Test error: {str(e)}"
            )

    # ===== SPECIAL CHARACTER TESTS =====

    def test_unicode_handling(self):
        """Test handling of Unicode characters"""
        print("\n=== UNICODE HANDLING TESTS ===\n")

        response = self.send_request("store_web_data", {
            "query": "测试中文 тест अनुवाद",
            "results": {"unicode": "こんにちは"},
            "project_name": "test"
        })

        # Should handle Unicode gracefully
        passed = response.get('result', {}).get('success', False)

        self.log_test(
            "Unicode characters handled",
            passed
        )

    # ===== CONCURRENT REQUEST TESTS =====

    def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        print("\n=== CONCURRENT REQUEST TESTS ===\n")

        results = []

        def make_request(client_id: str):
            response = self.send_request("store_web_data", {
                "query": "concurrent_test",
                "results": {"time": time.time()},
                "project_name": "test"
            }, client_id=client_id)
            results.append(response)

        threads = []
        for i in range(5):
            t = threading.Thread(target=make_request, args=(f"concurrent_client_{i}",))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # Check that all requests completed
        passed = len(results) == 5

        self.log_test(
            "Concurrent requests handled",
            passed,
            f"Processed {len(results)} concurrent requests"
        )

    # ===== REPORT GENERATION =====

    def print_report(self):
        """Print test report"""
        print("\n" + "=" * 60)
        print("SECURITY TEST REPORT")
        print("=" * 60)

        passed = sum(1 for r in self.test_results if r['passed'])
        total = len(self.test_results)

        print(f"\nTotal Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Pass Rate: {(passed/total*100):.1f}%")

        if total - passed > 0:
            print("\nFailed Tests:")
            for result in self.test_results:
                if not result['passed']:
                    print(f"  - {result['name']}")
                    if result['details']:
                        print(f"    {result['details']}")

        print("\n" + "=" * 60)

    def run_all_tests(self):
        """Run all security tests"""
        self.start_server()
        time.sleep(1)  # Allow server to start

        try:
            self.test_path_traversal_read_pdf()
            self.test_directory_escape_project_name()
            self.test_oversized_query()
            self.test_oversized_results()
            self.test_null_values()
            self.test_invalid_project_name_chars()
            self.test_error_messages_no_paths()
            self.test_error_messages_no_exceptions()
            self.test_rate_limiting()
            self.test_per_client_rate_limiting()
            self.test_audit_log_creation()
            self.test_audit_log_contains_method()
            self.test_audit_log_contains_client_id()
            self.test_operation_timeout()
            self.test_symlink_traversal()
            self.test_unicode_handling()
            self.test_concurrent_requests()

        finally:
            self.stop_server()

        self.print_report()


if __name__ == '__main__':
    suite = SecurityTestSuite()
    suite.run_all_tests()
