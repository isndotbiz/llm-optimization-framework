#!/usr/bin/env python3
"""
Test script for MCP Server
Demonstrates how to interact with the MCP server
"""

import json
import subprocess
import sys
from pathlib import Path


def send_request(server, method, params, request_id):
    """Send a JSON-RPC request to the MCP server"""
    request = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": request_id
    }

    print(f"\n>>> Sending request: {method}")
    print(json.dumps(request, indent=2))

    server.stdin.write(json.dumps(request) + '\n')
    server.stdin.flush()

    response_line = server.stdout.readline()
    response = json.loads(response_line)

    print(f"\n<<< Response:")
    print(json.dumps(response, indent=2))

    return response


def test_store_web_data():
    """Test storing web search data"""
    print("\n" + "=" * 60)
    print("TEST: Store Web Data")
    print("=" * 60)

    server_path = Path(__file__).parent / 'mcp_server.py'

    # Start MCP server
    server = subprocess.Popen(
        [sys.executable, str(server_path)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    try:
        # Test 1: Store web data
        response1 = send_request(
            server,
            "store_web_data",
            {
                "query": "python async programming",
                "results": {
                    "items": [
                        {
                            "title": "Async Python Tutorial",
                            "url": "https://example.com/async",
                            "snippet": "Learn async programming in Python..."
                        },
                        {
                            "title": "AsyncIO Guide",
                            "url": "https://example.com/asyncio",
                            "snippet": "Complete guide to asyncio..."
                        }
                    ],
                    "total_results": 2
                },
                "project_name": "test_project"
            },
            1
        )

        # Test 2: Retrieve stored data
        response2 = send_request(
            server,
            "retrieve_stored_data",
            {
                "project_name": "test_project",
                "query": "python"
            },
            2
        )

        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Store operation: {'SUCCESS' if response1['result']['success'] else 'FAILED'}")
        print(f"Retrieve operation: {'SUCCESS' if response2['result']['success'] else 'FAILED'}")
        print(f"Retrieved {response2['result']['count']} entries")

    finally:
        server.terminate()
        server.wait(timeout=5)


def test_pdf_operations():
    """Test PDF reading (requires a test PDF file)"""
    print("\n" + "=" * 60)
    print("TEST: PDF Operations")
    print("=" * 60)
    print("Note: This test requires a PDF file to be present")
    print("Update the pdf_path variable to point to a real PDF file")
    print("=" * 60)

    # Example request structure (commented out - requires real PDF)
    example_read_request = {
        "jsonrpc": "2.0",
        "method": "read_pdf",
        "params": {
            "file_path": "D:\\path\\to\\your\\document.pdf"
        },
        "id": 1
    }

    example_store_request = {
        "jsonrpc": "2.0",
        "method": "store_pdf",
        "params": {
            "pdf_path": "D:\\path\\to\\your\\document.pdf",
            "project_name": "test_project",
            "tags": ["research", "documentation"]
        },
        "id": 2
    }

    print("\nExample read_pdf request:")
    print(json.dumps(example_read_request, indent=2))

    print("\nExample store_pdf request:")
    print(json.dumps(example_store_request, indent=2))


if __name__ == '__main__':
    print("MCP Server Test Suite")
    print("=" * 60)

    # Run web data test (this works without external files)
    test_store_web_data()

    # Show PDF test examples
    test_pdf_operations()

    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)
