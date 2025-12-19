# MCP Server Quick Start Guide

## Installation

### Step 1: Install Dependencies

Run the installation script:
```batch
cd D:\models\mcp_tools
install.bat
```

Or manually install:
```batch
pip install pdfplumber PyPDF2
```

### Step 2: Verify Installation

Check that the server starts:
```batch
python mcp_server.py
```

You should see:
```
INFO - MCP Server initialized
INFO - MCP Server starting...
INFO - Available tools: ['read_pdf', 'store_web_data', 'retrieve_stored_data', 'store_pdf']
```

Press Ctrl+C to stop the server.

## Quick Test

Run the test suite:
```batch
python test_mcp_server.py
```

This will:
1. Start the MCP server
2. Store sample web search data
3. Retrieve the stored data
4. Display results

## Tool Usage Examples

### 1. Read a PDF

**Input (JSON-RPC):**
```json
{
  "jsonrpc": "2.0",
  "method": "read_pdf",
  "params": {
    "file_path": "D:\\documents\\report.pdf"
  },
  "id": 1
}
```

**Output:**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "success": true,
    "text": "Full text content from PDF...",
    "page_count": 15,
    "metadata": {"title": "Report", "author": "John Doe"},
    "file_path": "D:\\documents\\report.pdf",
    "file_size": 1024000
  },
  "id": 1
}
```

### 2. Store Web Search Data

**Input:**
```json
{
  "jsonrpc": "2.0",
  "method": "store_web_data",
  "params": {
    "query": "AI model optimization",
    "results": {
      "items": [
        {"title": "Guide", "url": "https://...", "snippet": "..."}
      ]
    },
    "project_name": "ai_research"
  },
  "id": 2
}
```

**Stored Location:**
```
D:\models\projects\ai_research\data\web_search\2025-12-08\AI_model_optimization_20251208_143022.json
```

### 3. Retrieve Stored Data

**Input:**
```json
{
  "jsonrpc": "2.0",
  "method": "retrieve_stored_data",
  "params": {
    "project_name": "ai_research",
    "query": "optimization"
  },
  "id": 3
}
```

**Output:**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "success": true,
    "data": [
      {
        "query": "AI model optimization",
        "results": {...},
        "timestamp": "2025-12-08T14:30:22.123456",
        "_file_path": "D:\\models\\projects\\...",
        "_file_date": "2025-12-08"
      }
    ],
    "count": 1
  },
  "id": 3
}
```

### 4. Store PDF in Project

**Input:**
```json
{
  "jsonrpc": "2.0",
  "method": "store_pdf",
  "params": {
    "pdf_path": "D:\\downloads\\whitepaper.pdf",
    "project_name": "ai_research",
    "tags": ["deep-learning", "optimization"]
  },
  "id": 4
}
```

**Result:**
- PDF copied to: `D:\models\projects\ai_research\data\pdfs\whitepaper_20251208_143022.pdf`
- Index updated at: `D:\models\projects\ai_research\data\pdfs\index.json`

## Integration with Python

```python
import json
import subprocess
import sys

# Start server
server = subprocess.Popen(
    [sys.executable, 'D:\\models\\mcp_tools\\mcp_server.py'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    text=True,
    bufsize=1
)

# Send request
request = {
    "jsonrpc": "2.0",
    "method": "read_pdf",
    "params": {"file_path": "D:\\doc.pdf"},
    "id": 1
}

server.stdin.write(json.dumps(request) + '\n')
server.stdin.flush()

# Read response
response = json.loads(server.stdout.readline())
print(response['result'])

# Cleanup
server.terminate()
```

## Common Use Cases

### Use Case 1: Research Paper Management

1. Store PDF: `store_pdf` with tags like ["machine-learning", "2025"]
2. Extract text: `read_pdf` to get full content
3. Store web data: `store_web_data` for related articles
4. Query later: `retrieve_stored_data` to find all research

### Use Case 2: Web Research Archive

1. Perform web searches in your application
2. Store results: `store_web_data` for each search
3. Retrieve by date: Use `date_range` parameter
4. Filter by topic: Use `query` parameter

### Use Case 3: Document Processing Pipeline

1. Batch process PDFs: Loop through files with `read_pdf`
2. Store in project: Use `store_pdf` to organize
3. Index creation: Automatic via `index.json`
4. Search index: Parse `index.json` for metadata

## Folder Structure Created

```
D:\models\
├── mcp_tools\
│   ├── mcp_server.py        (Main server)
│   ├── test_mcp_server.py   (Test suite)
│   ├── requirements.txt     (Dependencies)
│   ├── install.bat          (Installer)
│   ├── README.md            (Full docs)
│   ├── QUICK_START.md       (This file)
│   └── mcp_server.log       (Runtime logs)
│
└── projects\
    └── {project_name}\
        └── data\
            ├── web_search\
            │   └── YYYY-MM-DD\
            │       └── *.json
            └── pdfs\
                ├── index.json
                └── *.pdf
```

## Troubleshooting

**Problem**: "No PDF library available"
**Solution**: Run `pip install pdfplumber`

**Problem**: Permission denied when creating folders
**Solution**: Ensure write access to `D:\models\projects\`

**Problem**: JSON parse error
**Solution**: Verify request format matches JSON-RPC 2.0 spec

**Problem**: Server not responding
**Solution**: Check `mcp_server.log` for errors

## Next Steps

1. Install dependencies: `install.bat`
2. Run tests: `python test_mcp_server.py`
3. Read full docs: `README.md`
4. Integrate with your application

## Support

- Logs: `D:\models\mcp_tools\mcp_server.log`
- Full documentation: `README.md`
- Test examples: `test_mcp_server.py`
