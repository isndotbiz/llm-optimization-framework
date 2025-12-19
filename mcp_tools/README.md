# MCP Server for AI Router

A Model Context Protocol (MCP) server implementation providing PDF processing and web data storage tools for the AI Router system.

## Overview

This MCP server exposes four powerful tools for managing PDFs and web search data within project contexts:

1. **read_pdf** - Extract text and metadata from PDF files
2. **store_web_data** - Store web search results with organized folder structure
3. **retrieve_stored_data** - Retrieve previously stored web data with filtering
4. **store_pdf** - Copy PDFs to project folders with automatic indexing

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Install Dependencies

```bash
cd D:\models\mcp_tools
pip install -r requirements.txt
```

The server requires at least one PDF processing library:
- **pdfplumber** (recommended) - Better text extraction, handles complex layouts
- **PyPDF2** (alternative) - Lighter weight, faster for simple PDFs

## Usage

### Running the MCP Server

The server communicates via JSON-RPC over stdio:

```bash
python mcp_server.py
```

### Tool Specifications

#### 1. read_pdf

Extract text and metadata from PDF files.

**Request Format:**
```json
{
  "jsonrpc": "2.0",
  "method": "read_pdf",
  "params": {
    "file_path": "D:\\documents\\example.pdf"
  },
  "id": 1
}
```

**Response Format:**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "success": true,
    "text": "Extracted text content...",
    "page_count": 10,
    "metadata": {
      "title": "Document Title",
      "author": "Author Name",
      "creator": "PDF Creator"
    },
    "file_path": "D:\\documents\\example.pdf",
    "file_size": 524288
  },
  "id": 1
}
```

**Parameters:**
- `file_path` (string, required): Absolute path to the PDF file

**Returns:**
- `success` (boolean): Operation success status
- `text` (string): Extracted text from all pages
- `page_count` (integer): Number of pages in PDF
- `metadata` (object): PDF metadata (title, author, etc.)
- `file_path` (string): Path to the PDF file
- `file_size` (integer): File size in bytes
- `error` (string): Error message if failed

#### 2. store_web_data

Store web search results or fetched web data with automatic organization.

**Request Format:**
```json
{
  "jsonrpc": "2.0",
  "method": "store_web_data",
  "params": {
    "query": "machine learning best practices",
    "results": {
      "items": [
        {"title": "ML Guide", "url": "https://example.com", "snippet": "..."}
      ]
    },
    "project_name": "ml_research"
  },
  "id": 2
}
```

**Response Format:**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "success": true,
    "storage_path": "D:\\models\\projects\\ml_research\\data\\web_search\\2025-12-08\\machine_learning_best_practices_20251208_143022.json",
    "timestamp": "2025-12-08T14:30:22.123456",
    "query": "machine learning best practices",
    "project_name": "ml_research"
  },
  "id": 2
}
```

**Parameters:**
- `query` (string, required): Search query or data identifier
- `results` (object/array, required): Web search results (any JSON-serializable data)
- `project_name` (string, required): Project name for organization

**Storage Structure:**
```
D:\models\projects\{project_name}\data\web_search\
  └── YYYY-MM-DD\
      └── query_name_YYYYMMDD_HHMMSS.json
```

**Returns:**
- `success` (boolean): Operation success status
- `storage_path` (string): Full path where data was stored
- `timestamp` (string): ISO format timestamp
- `query` (string): Original query
- `project_name` (string): Project name
- `error` (string): Error message if failed

#### 3. retrieve_stored_data

Retrieve previously stored web data with optional filtering.

**Request Format:**
```json
{
  "jsonrpc": "2.0",
  "method": "retrieve_stored_data",
  "params": {
    "project_name": "ml_research",
    "query": "machine learning",
    "date_range": {
      "start": "2025-12-01",
      "end": "2025-12-08"
    }
  },
  "id": 3
}
```

**Response Format:**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "success": true,
    "data": [
      {
        "query": "machine learning best practices",
        "results": {...},
        "timestamp": "2025-12-08T14:30:22.123456",
        "project_name": "ml_research",
        "_file_path": "D:\\models\\projects\\ml_research\\data\\web_search\\2025-12-08\\...",
        "_file_date": "2025-12-08"
      }
    ],
    "count": 1,
    "project_name": "ml_research"
  },
  "id": 3
}
```

**Parameters:**
- `project_name` (string, required): Project name
- `query` (string, optional): Filter by query substring (case-insensitive)
- `date_range` (object, optional): Date range filter
  - `start` (string): Start date in YYYY-MM-DD format
  - `end` (string): End date in YYYY-MM-DD format

**Returns:**
- `success` (boolean): Operation success status
- `data` (array): List of matching stored data entries
- `count` (integer): Number of entries found
- `project_name` (string): Project name
- `error` (string): Error message if failed

#### 4. store_pdf

Copy PDF to project data folder and create searchable index.

**Request Format:**
```json
{
  "jsonrpc": "2.0",
  "method": "store_pdf",
  "params": {
    "pdf_path": "D:\\downloads\\research_paper.pdf",
    "project_name": "ml_research",
    "tags": ["neural-networks", "research", "2025"]
  },
  "id": 4
}
```

**Response Format:**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "success": true,
    "storage_path": "D:\\models\\projects\\ml_research\\data\\pdfs\\research_paper_20251208_143022.pdf",
    "index_path": "D:\\models\\projects\\ml_research\\data\\pdfs\\index.json",
    "filename": "research_paper_20251208_143022.pdf",
    "page_count": 25,
    "tags": ["neural-networks", "research", "2025"]
  },
  "id": 4
}
```

**Parameters:**
- `pdf_path` (string, required): Path to source PDF file
- `project_name` (string, required): Project name
- `tags` (array, optional): List of tags for categorization

**Storage Structure:**
```
D:\models\projects\{project_name}\data\pdfs\
  ├── index.json
  ├── document1_20251208_120000.pdf
  └── document2_20251208_130000.pdf
```

**Index Format:**
```json
{
  "pdfs": [
    {
      "filename": "research_paper_20251208_143022.pdf",
      "original_path": "D:\\downloads\\research_paper.pdf",
      "storage_path": "D:\\models\\projects\\ml_research\\data\\pdfs\\research_paper_20251208_143022.pdf",
      "timestamp": "2025-12-08T14:30:22.123456",
      "tags": ["neural-networks", "research", "2025"],
      "page_count": 25,
      "file_size": 2097152,
      "pdf_metadata": {
        "title": "Research Paper Title",
        "author": "Author Name"
      }
    }
  ]
}
```

**Returns:**
- `success` (boolean): Operation success status
- `storage_path` (string): Where PDF was copied
- `index_path` (string): Path to metadata index
- `filename` (string): Stored filename with timestamp
- `page_count` (integer): Number of pages
- `tags` (array): Applied tags
- `error` (string): Error message if failed

## Error Handling

All tools return graceful error responses:

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32603,
    "message": "Internal error: File not found"
  },
  "id": 1
}
```

**Error Codes:**
- `-32700`: Parse error (invalid JSON)
- `-32601`: Method not found
- `-32603`: Internal error

## Logging

The server logs all operations to:
- **File**: `D:\models\mcp_tools\mcp_server.log`
- **Console**: stderr stream

Log levels:
- INFO: Normal operations
- WARNING: Non-critical issues
- ERROR: Critical errors with stack traces

## Project Structure

```
D:\models\mcp_tools\
├── mcp_server.py       # Main MCP server implementation
├── requirements.txt    # Python dependencies
├── README.md          # This documentation
└── mcp_server.log     # Runtime logs (generated)

D:\models\projects\{project_name}\
└── data\
    ├── web_search\
    │   └── YYYY-MM-DD\
    │       └── query_*.json
    └── pdfs\
        ├── index.json
        └── *.pdf
```

## Integration with AI Router

The MCP server is designed to work seamlessly with the AI Router system:

1. **PDF Processing**: Extract text from research papers, documentation, and reports
2. **Web Data Storage**: Persist web search results for later analysis
3. **Data Retrieval**: Query stored data across projects
4. **PDF Management**: Organize and index PDF collections

## Examples

### Example 1: Process and Store a PDF

```python
import json
import subprocess

# Start MCP server
server = subprocess.Popen(
    ['python', 'D:\\models\\mcp_tools\\mcp_server.py'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# Read PDF
request = {
    "jsonrpc": "2.0",
    "method": "read_pdf",
    "params": {"file_path": "D:\\research\\paper.pdf"},
    "id": 1
}
server.stdin.write(json.dumps(request) + '\n')
server.stdin.flush()
response = json.loads(server.stdout.readline())

# Store PDF in project
store_request = {
    "jsonrpc": "2.0",
    "method": "store_pdf",
    "params": {
        "pdf_path": "D:\\research\\paper.pdf",
        "project_name": "research_project",
        "tags": ["ai", "ml"]
    },
    "id": 2
}
server.stdin.write(json.dumps(store_request) + '\n')
server.stdin.flush()
store_response = json.loads(server.stdout.readline())
```

### Example 2: Store and Retrieve Web Data

```python
# Store web search results
store_request = {
    "jsonrpc": "2.0",
    "method": "store_web_data",
    "params": {
        "query": "python async programming",
        "results": {"items": [...]},
        "project_name": "python_learning"
    },
    "id": 1
}

# Later, retrieve stored data
retrieve_request = {
    "jsonrpc": "2.0",
    "method": "retrieve_stored_data",
    "params": {
        "project_name": "python_learning",
        "query": "async"
    },
    "id": 2
}
```

## Troubleshooting

### PDF Library Not Found

If you see "No PDF library installed":
```bash
pip install pdfplumber
# or
pip install PyPDF2
```

### Permission Errors

Ensure the server has write permissions to `D:\models\projects\`

### JSON Parse Errors

Verify requests are properly formatted JSON with required fields

### File Not Found

Use absolute paths for all file operations

## Version

**Version**: 1.0.0
**Last Updated**: 2025-12-08
**Python Compatibility**: 3.8+

## License

Part of the AI Router system at D:\models

## Support

For issues or questions, check:
1. Server logs at `D:\models\mcp_tools\mcp_server.log`
2. AI Router documentation
3. MCP protocol specification
