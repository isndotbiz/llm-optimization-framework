# Feature Documentation - AI Router Enhanced v2.0

**Comprehensive Feature Reference** | All 9 Core Features + Enhancements

---

## Table of Contents

1. [Session Management & Conversation History](#1-session-management--conversation-history)
2. [Prompt Templates Library](#2-prompt-templates-library)
3. [Model Comparison Mode](#3-model-comparison-mode-ab-testing)
4. [Response Post-Processing](#4-response-post-processing--formatting)
5. [Batch Processing Mode](#5-batch-processing-mode)
6. [Smart Model Auto-Selection](#6-smart-model-auto-selection)
7. [Performance Analytics Dashboard](#7-performance-analytics-dashboard)
8. [Context Management & Injection](#8-context-management--injection)
9. [Prompt Chaining Workflows](#9-prompt-chaining-workflows)

---

## 1. Session Management & Conversation History

### Overview

Persistent conversation storage with SQLite backend, enabling save/resume functionality, search, tags, and full history management.

### Key Capabilities

- **Persistent Storage**: All conversations saved to SQLite database
- **Full CRUD**: Create, Read, Update, Delete sessions
- **Search**: Find conversations by keyword, date, model, or tags
- **Tags**: Organize sessions with custom tags
- **Bookmarks**: Mark important sessions for quick access
- **Export**: Multiple formats (JSON, Markdown, HTML, PDF)
- **Metadata**: Track model, tokens, duration, timestamps

### Architecture

```
SessionManager (session_manager.py)
├── Database: .ai-router-sessions.db
├── Tables:
│   ├── sessions (session metadata)
│   ├── messages (conversation messages)
│   ├── session_tags (tag associations)
│   ├── bookmarks (starred sessions)
│   └── analytics (performance metrics)
└── Schema: schema.sql
```

### Database Schema

```sql
-- Sessions table
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    title TEXT,
    model_id TEXT NOT NULL,
    model_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message_count INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0
);

-- Messages table
CREATE TABLE messages (
    message_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,  -- 'user' or 'assistant'
    content TEXT NOT NULL,
    tokens_used INTEGER,
    duration_seconds REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);

-- Session tags
CREATE TABLE session_tags (
    session_id TEXT NOT NULL,
    tag TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (session_id, tag),
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);

-- Bookmarks
CREATE TABLE bookmarks (
    session_id TEXT PRIMARY KEY,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);
```

### Usage Examples

#### Create New Session

```python
from session_manager import SessionManager

# Initialize
sm = SessionManager(Path(".ai-router-sessions.db"))

# Create session
session_id = sm.create_session(
    model_id="qwen3-coder-30b",
    model_name="Qwen3 Coder 30B Q4_K_M",
    title="Python Flask API Development"
)

# Add messages
sm.add_message(
    session_id=session_id,
    role="user",
    content="Create a REST API for user management",
    tokens_used=15
)

sm.add_message(
    session_id=session_id,
    role="assistant",
    content="[Model response...]",
    tokens_used=456,
    duration_seconds=2.3
)
```

#### Resume Session

```python
# List recent sessions
recent = sm.list_sessions(limit=10)

for session in recent:
    print(f"{session['title']} - {session['message_count']} messages")

# Get full session
session = sm.get_session(session_id)
messages = sm.get_messages(session_id)

# Continue conversation
sm.add_message(session_id, "user", "Add authentication", 12)
```

#### Search Sessions

```python
# Search by keyword
results = sm.search_sessions("flask api")

# Filter by tag
tagged = sm.get_sessions_by_tag("python")

# Filter by model
model_sessions = sm.get_sessions_by_model("qwen3-coder-30b")

# Date range
from datetime import datetime, timedelta
start = datetime.now() - timedelta(days=7)
recent_week = sm.get_sessions_in_range(start, datetime.now())
```

#### Tag Management

```python
# Add tags
sm.add_tag(session_id, "python")
sm.add_tag(session_id, "flask")
sm.add_tag(session_id, "api")

# List all tags
all_tags = sm.get_all_tags()  # Returns: [("python", 45), ("flask", 12), ...]

# Remove tag
sm.remove_tag(session_id, "api")
```

#### Bookmarks

```python
# Bookmark session
sm.add_bookmark(session_id, notes="Best Flask API example")

# List bookmarked
bookmarked = sm.get_bookmarked_sessions()

# Remove bookmark
sm.remove_bookmark(session_id)
```

#### Export Sessions

```python
# Export as JSON
export_data = sm.export_session(session_id, format="json")

# Export as Markdown
markdown = sm.export_session(session_id, format="markdown")

# Export all sessions
all_data = sm.export_all_sessions(format="json")
```

### Advanced Features

#### Session Statistics

```python
stats = sm.get_session_statistics(session_id)
# Returns:
# {
#     "total_messages": 24,
#     "user_messages": 12,
#     "assistant_messages": 12,
#     "total_tokens": 8456,
#     "avg_tokens_per_message": 352,
#     "duration": 45.6,  # seconds
#     "tokens_per_second": 185.3
# }
```

#### Session Cleanup

```python
# Delete old sessions
deleted = sm.delete_sessions_older_than(days=90)

# Archive to JSON before deleting
archive = sm.export_sessions_in_range(start, end, format="json")
with open("archive.json", "w") as f:
    json.dump(archive, f)

sm.delete_sessions_in_range(start, end)
```

### Troubleshooting

**Issue**: Database locked
**Solution**: Ensure no other processes are accessing the database

**Issue**: Slow searches
**Solution**: Run `VACUUM` command periodically

```python
sm.vacuum_database()  # Optimizes and compacts database
```

---

## 2. Prompt Templates Library

### Overview

YAML + Jinja2 template system for reusable prompt structures with variable substitution, defaults, and validation.

### Key Capabilities

- **Variable Substitution**: Dynamic prompts with placeholders
- **Default Values**: Fallback values for missing variables
- **Validation**: Type checking and required field validation
- **Metadata**: Description, version, author, tags
- **Built-in Templates**: Code review, research, creative, debug
- **Custom Creation**: UI for creating new templates
- **Version Control**: Track template changes over time

### Template Structure

```yaml
metadata:
  name: "Code Review Template"
  description: "Comprehensive code review with focus areas"
  author: "AI Router Team"
  version: "1.0.0"
  tags: [coding, review, quality]
  variables:
    - name: language
      type: string
      required: true
      description: "Programming language"
      default: "Python"
    - name: code
      type: text
      required: true
      description: "Code to review"
    - name: focus_areas
      type: string
      required: false
      description: "Areas to focus on"
      default: "all"

system_prompt: |
  You are an expert {{language}} code reviewer with 10+ years of experience.
  Your reviews are thorough, constructive, and actionable.

  Focus areas: {{focus_areas}}

user_prompt: |
  Please review the following {{language}} code:

  ```{{language}}
  {{code}}
  ```

  Provide analysis on:
  {% if focus_areas == "all" %}
  - Code quality and style
  - Performance optimization
  - Security vulnerabilities
  - Best practices compliance
  - Potential bugs or edge cases
  {% else %}
  - {{focus_areas}}
  {% endif %}

  Format your response with:
  1. Summary (2-3 sentences)
  2. Detailed findings
  3. Recommended changes
  4. Priority assessment (Critical/High/Medium/Low)
```

### Usage Examples

#### Using Built-in Templates

```python
from template_manager import TemplateManager

# Initialize
tm = TemplateManager(Path("prompt-templates/"))

# List available templates
templates = tm.list_templates()
for template in templates:
    print(f"{template['name']} - {template['description']}")

# Load template
template = tm.load_template("code-review.yaml")

# Get required variables
variables = template.get_required_variables()
# Returns: [
#   {"name": "language", "default": "Python", "required": True},
#   {"name": "code", "required": True},
#   {"name": "focus_areas", "default": "all", "required": False}
# ]

# Render with values
rendered = template.render({
    "language": "Python",
    "code": "def add(a, b): return a + b",
    "focus_areas": "performance"
})

# Use rendered prompts
system_prompt = rendered['system_prompt']
user_prompt = rendered['user_prompt']
```

#### Creating Custom Templates

```python
# Programmatically
template_yaml = """
metadata:
  name: "API Testing"
  description: "Generate API test cases"
  variables:
    - name: endpoint
      default: "/api/users"
    - name: method
      default: "GET"

system_prompt: |
  You are an API testing expert.

user_prompt: |
  Generate test cases for {{method}} {{endpoint}}
"""

tm.save_template("api-testing.yaml", template_yaml)
```

Or via UI:
```
Menu → [7] Manage Templates → [c] Create New Template
```

#### Advanced: Conditional Logic

```yaml
user_prompt: |
  {% if complexity == "simple" %}
  Explain {{topic}} in simple terms for beginners.
  {% elif complexity == "intermediate" %}
  Provide a technical explanation of {{topic}} with examples.
  {% else %}
  Give an in-depth, expert-level analysis of {{topic}}.
  {% endif %}

  {% if include_examples %}
  Include at least 3 practical examples.
  {% endif %}
```

### Built-in Templates

1. **code-review.yaml** - Code quality analysis
2. **research-summary.yaml** - Summarize research papers
3. **creative-story.yaml** - Generate creative fiction
4. **debug-assistant.yaml** - Debug code with stack traces
5. **eli5.yaml** - Explain Like I'm 5
6. **api-documentation.yaml** - Generate API docs
7. **unit-tests.yaml** - Create unit tests

### Best Practices

1. **Variable Naming**: Use descriptive, snake_case names
2. **Defaults**: Always provide sensible defaults
3. **Documentation**: Describe each variable clearly
4. **Validation**: Mark required fields explicitly
5. **Testing**: Test with edge cases before deployment
6. **Versioning**: Update version number on changes
7. **Organization**: Use tags for categorization

### Troubleshooting

**Issue**: Variable not rendering
**Solution**: Check variable name spelling (case-sensitive)

**Issue**: Template syntax error
**Solution**: Validate YAML syntax, check Jinja2 syntax

```python
# Validate template
is_valid, errors = tm.validate_template("my-template.yaml")
if not is_valid:
    print(errors)
```

---

## 3. Model Comparison Mode (A/B Testing)

### Overview

Side-by-side comparison of multiple models for the same prompt, with performance metrics and preference learning.

### Key Capabilities

- **Side-by-Side Comparison**: Run same prompt on 2+ models
- **Performance Metrics**: Speed, tokens, quality
- **Cost Comparison**: For cloud models
- **Preference Voting**: Learn from user preferences
- **Export Results**: Save comparisons for analysis
- **Statistical Analysis**: Compare average performance

### Architecture

```
ModelComparison (model_comparison.py)
├── Comparison Engine
├── Metrics Collection
├── Preference Learning
├── Results Storage
└── Export System
```

### Usage Examples

#### Basic A/B Test

```python
from model_comparison import ModelComparison

mc = ModelComparison(ai_router)

# Compare two models
result = mc.compare_models(
    model_a_id="qwen3-coder-30b",
    model_b_id="phi4-14b",
    prompt="Explain the halting problem"
)

# Result structure:
# {
#     "model_a": {
#         "response": "...",
#         "duration": 2.3,
#         "tokens": 247,
#         "tokens_per_sec": 107.4,
#         "cost": 0.0  # Local model
#     },
#     "model_b": {
#         "response": "...",
#         "duration": 1.8,
#         "tokens": 312,
#         "tokens_per_sec": 173.3,
#         "cost": 0.0
#     }
# }
```

#### Multi-Model Comparison (3+)

```python
# Compare multiple models
result = mc.compare_multiple(
    model_ids=["qwen3-coder-30b", "phi4-14b", "gemma3-27b"],
    prompt="Write a sorting algorithm"
)

# Display side-by-side
mc.display_comparison(result)
```

#### Preference Learning

```python
# User votes for preferred response
mc.record_preference(
    comparison_id=result['id'],
    winner="model_a",
    reason="more detailed explanation"
)

# System learns from votes
# Future recommendations weighted by preferences
```

#### Performance Analysis

```python
# Compare average performance
stats = mc.get_model_statistics("qwen3-coder-30b")
# Returns:
# {
#     "avg_response_time": 2.1,
#     "avg_tokens": 387,
#     "avg_tokens_per_sec": 184.3,
#     "comparison_wins": 45,
#     "comparison_losses": 12,
#     "win_rate": 0.789
# }
```

#### Cost Comparison

```python
# Compare costs for cloud models
cost_analysis = mc.compare_costs(
    models=["gpt-4", "claude-sonnet", "llama-70b-openrouter"],
    prompt="Long analysis task...",
    expected_output_tokens=2000
)

# Returns estimated costs before running
```

### Metrics Collected

| Metric | Description | Unit |
|--------|-------------|------|
| **Duration** | Time to generate response | seconds |
| **Tokens** | Total tokens in response | count |
| **Tokens/Sec** | Generation speed | tok/s |
| **Cost** | API cost (cloud models) | USD |
| **Quality** | User rating (1-5 stars) | 1-5 |
| **Accuracy** | For factual queries | % |
| **Clarity** | Readability score | 1-10 |

### Export Options

```python
# Export comparison
mc.export_comparison(
    result,
    format="json",  # json, markdown, html, csv
    filename="comparison_2025-12-08.json"
)

# Batch export all comparisons
mc.export_all_comparisons(
    start_date="2025-12-01",
    end_date="2025-12-08",
    format="csv"
)
```

### Advanced Features

#### Automated Testing

```python
# Run benchmark suite
results = mc.run_benchmark(
    models=["qwen3-coder-30b", "phi4-14b"],
    test_suite="coding_benchmark_100.json"
)

# Generate report
report = mc.generate_benchmark_report(results)
```

#### Statistical Significance

```python
# Calculate statistical significance of differences
significance = mc.calculate_significance(
    model_a="qwen3-coder-30b",
    model_b="phi4-14b",
    metric="tokens_per_sec",
    n_samples=30
)

# Returns p-value and confidence interval
```

---

_Continuing with remaining features 4-9..._

---

## 4. Response Post-Processing & Formatting

### Overview

The Response Post-Processing system provides comprehensive tools for capturing, formatting, extracting, and exporting AI model responses. Built around the `ResponseProcessor` class, this feature enables automatic code extraction, syntax highlighting, format conversion, and metadata tracking. Whether you need to save responses for documentation, extract code snippets for testing, or convert outputs to presentation-ready formats, this system handles all post-processing needs with precision and flexibility.

The processor maintains full compatibility with all 30+ programming languages, supports multiple export formats (Markdown, HTML, JSON, PDF), and integrates seamlessly with the session management system for unified response tracking.

### Key Capabilities

- **Code Block Extraction**: Automatically detect and extract code blocks with language tags
- **Multi-Format Export**: Convert responses to Markdown, HTML, JSON, and plain text
- **Metadata Management**: Attach comprehensive metadata to every saved response
- **Syntax Highlighting**: Apply language-specific formatting (30+ languages supported)
- **Statistics Generation**: Word count, line count, token estimation, code block analysis
- **Clipboard Integration**: Quick copy-to-clipboard functionality
- **File Management**: Automatic file naming, directory organization, and retrieval
- **Language Detection**: Intelligent programming language identification
- **Response Validation**: Check for completeness and format correctness

### Architecture

```
ResponseProcessor (response_processor.py)
├── Output Directory Management
├── Code Block Extraction Engine
├── Format Conversion Pipeline
├── Metadata Header Builder
├── Statistics Calculator
├── File Extension Mapping (30+ languages)
└── Clipboard Integration
```

### Complete API Reference

#### ResponseProcessor Class

```python
class ResponseProcessor:
    """Post-processing utilities for model responses"""

    def __init__(self, output_dir: Path)
    def save_response(self, response: str, filename: Optional[str] = None,
                     model_name: str = "", metadata: Optional[Dict] = None) -> Path
    def extract_code_blocks(self, text: str) -> List[Dict[str, str]]
    def save_code_blocks(self, text: str, base_name: str) -> List[Path]
    def format_as_markdown(self, response: str, model_name: str = "",
                          metadata: Optional[Dict] = None) -> str
    def get_statistics(self, text: str) -> Dict
    def copy_to_clipboard(self, text: str) -> bool
    def list_saved_responses(self, limit: int = 10) -> List[Path]
```

### Configuration Options

#### Initialization Parameters

```python
# Basic initialization
rp = ResponseProcessor(output_dir=Path("outputs/"))

# Custom output directory structure
rp = ResponseProcessor(output_dir=Path("responses/2025-12"))

# Project-specific responses
rp = ResponseProcessor(output_dir=Path("projects/myapp/ai-responses"))
```

#### Output Directory Management

The processor automatically creates the output directory if it doesn't exist and organizes files with timestamped filenames for easy retrieval.

### Detailed Usage Examples

#### Basic: Save Response with Metadata

```python
from response_processor import ResponseProcessor
from pathlib import Path

# Initialize processor
rp = ResponseProcessor(output_dir=Path("outputs/"))

# Save response with automatic filename
response_text = """
Here's a Python function to calculate factorial:

```python
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
```

This uses recursion to compute the factorial efficiently.
"""

saved_file = rp.save_response(
    response=response_text,
    model_name="Qwen3 Coder 30B Q4_K_M",
    metadata={
        "prompt": "Write factorial function",
        "tokens_used": 247,
        "duration": 2.3
    }
)

print(f"Response saved to: {saved_file}")
# Output: outputs/response_20251209_143052.txt
```

**Generated File Structure:**
```
================================================================================
AI ROUTER - MODEL RESPONSE
================================================================================
Generated: 2025-12-09 14:30:52
Model: Qwen3 Coder 30B Q4_K_M
prompt: Write factorial function
tokens_used: 247
duration: 2.3
================================================================================

Here's a Python function to calculate factorial:
...
```

#### Intermediate: Extract and Save Code Blocks

```python
# Extract all code blocks from response
code_blocks = rp.extract_code_blocks(response_text)

for block in code_blocks:
    print(f"Language: {block['language']}")
    print(f"Code:\n{block['code']}\n")

# Output:
# Language: python
# Code:
# def factorial(n):
#     if n <= 1:
#         return 1
#     return n * factorial(n - 1)

# Save code blocks to separate files
saved_code_files = rp.save_code_blocks(
    text=response_text,
    base_name="factorial_implementation"
)

for file_path in saved_code_files:
    print(f"Code saved to: {file_path}")
# Output: outputs/factorial_implementation_code_0.py
```

**Generated Code File:**
```python
# Language: python

def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
```

#### Advanced: Custom Formatting with Markdown Export

```python
# Format response as Markdown with metadata
markdown_output = rp.format_as_markdown(
    response=response_text,
    model_name="Qwen3 Coder 30B Q4_K_M",
    metadata={
        "category": "coding",
        "difficulty": "beginner",
        "tags": "recursion, algorithms",
        "tokens": 247
    }
)

# Save formatted Markdown
md_file = Path("outputs/factorial_response.md")
md_file.write_text(markdown_output, encoding='utf-8')
```

**Generated Markdown:**
```markdown
# AI Router Response

**Generated:** 2025-12-09 14:30:52
**Model:** Qwen3 Coder 30B Q4_K_M

## Metadata

- **category:** coding
- **difficulty:** beginner
- **tags:** recursion, algorithms
- **tokens:** 247

---

## Response

Here's a Python function to calculate factorial:
...
```

#### Real-World: Batch Code Extraction Workflow

```python
# Process multiple responses from a session
from session_manager import SessionManager

sm = SessionManager(Path(".ai-router-sessions.db"))
rp = ResponseProcessor(output_dir=Path("extracted_code/"))

# Get all messages from coding session
session_id = "abc123"
messages = sm.get_messages(session_id)

# Extract all code blocks from assistant responses
all_code_blocks = []
for msg in messages:
    if msg['role'] == 'assistant':
        blocks = rp.extract_code_blocks(msg['content'])
        all_code_blocks.extend(blocks)

# Save each code block
for i, block in enumerate(all_code_blocks):
    ext = rp._get_extension(block['language'])
    filename = f"session_{session_id}_code_{i}{ext}"
    filepath = rp.output_dir / filename

    filepath.write_text(block['code'], encoding='utf-8')
    print(f"Extracted: {filename} ({block['language']})")

# Output:
# Extracted: session_abc123_code_0.py (python)
# Extracted: session_abc123_code_1.js (javascript)
# Extracted: session_abc123_code_2.sql (sql)
```

### Response Statistics

```python
# Get comprehensive statistics
stats = rp.get_statistics(response_text)

print(f"Characters: {stats['char_count']:,}")
print(f"Words: {stats['word_count']:,}")
print(f"Lines: {stats['line_count']:,}")
print(f"Code blocks: {stats['code_blocks']}")
print(f"Avg line length: {stats['avg_line_length']:.1f}")

# Output:
# Characters: 1,247
# Words: 215
# Lines: 24
# Code blocks: 1
# Avg line length: 51.9
```

### Integration with Other Features

#### Session Management Integration

```python
from session_manager import SessionManager
from response_processor import ResponseProcessor

sm = SessionManager(Path(".ai-router-sessions.db"))
rp = ResponseProcessor(output_dir=Path("outputs/"))

# Save response and add to session
session_id = "xyz789"
response_text = "[model response...]"

# Save with ResponseProcessor
saved_file = rp.save_response(
    response=response_text,
    model_name="Phi-4 14B",
    metadata={"session_id": session_id}
)

# Add to session history
sm.add_message(
    session_id=session_id,
    role="assistant",
    content=response_text,
    tokens_used=456,
    duration_seconds=2.1
)

print(f"Response saved to: {saved_file}")
print(f"Added to session: {session_id}")
```

#### Workflow Engine Integration

```python
# In workflow YAML:
# steps:
#   - name: generate_code
#     type: prompt
#     model: qwen3-coder-30b
#     prompt: "Write a REST API in Flask"
#     save_to: flask_code
#
#   - name: extract_code
#     type: extract
#     from_step: generate_code
#     pattern: '```python\n(.*?)```'
#     save_to: extracted_code
#
#   - name: save_file
#     type: export
#     data: "{{extracted_code}}"
#     filename: "api.py"
```

### Clipboard Integration

```python
# Copy response to clipboard (requires pyperclip)
success = rp.copy_to_clipboard(response_text)

if success:
    print("Response copied to clipboard!")
else:
    print("Clipboard functionality requires: pip install pyperclip")
```

### Supported Languages (File Extension Mapping)

The processor supports 30+ programming and markup languages:

| Language | Extension | Language | Extension |
|----------|-----------|----------|-----------|
| Python | .py | JavaScript | .js |
| TypeScript | .ts | Java | .java |
| C++ | .cpp | C | .c |
| Rust | .rs | Go | .go |
| Ruby | .rb | PHP | .php |
| Swift | .swift | Kotlin | .kt |
| Scala | .scala | R | .r |
| SQL | .sql | Bash | .sh |
| PowerShell | .ps1 | HTML | .html |
| CSS | .css | SCSS | .scss |
| JSON | .json | YAML | .yaml |
| XML | .xml | Markdown | .md |
| TOML | .toml | INI | .ini |

### File Management

```python
# List recently saved responses
recent_files = rp.list_saved_responses(limit=10)

for file_path in recent_files:
    file_stat = file_path.stat()
    modified = datetime.fromtimestamp(file_stat.st_mtime)
    size = file_stat.st_size

    print(f"{file_path.name} - {size:,} bytes - {modified}")

# Output:
# response_20251209_143052.txt - 1,247 bytes - 2025-12-09 14:30:52
# response_20251209_141523.txt - 892 bytes - 2025-12-09 14:15:23
# response_20251209_135501.txt - 2,103 bytes - 2025-12-09 13:55:01
```

### Customization Guide

#### Custom Metadata Headers

```python
# Extend ResponseProcessor for custom headers
class CustomResponseProcessor(ResponseProcessor):
    def _build_metadata_header(self, model_name: str, metadata: Optional[Dict] = None) -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        header_lines = [
            "╔" + "═" * 78 + "╗",
            "║" + " " * 20 + "CUSTOM AI RESPONSE HEADER" + " " * 32 + "║",
            "╠" + "═" * 78 + "╣",
            f"║ Timestamp: {timestamp:<63} ║",
        ]

        if model_name:
            header_lines.append(f"║ Model: {model_name:<69} ║")

        if metadata:
            for key, value in metadata.items():
                line = f"║ {key}: {value}"
                padding = 78 - len(line)
                header_lines.append(line + " " * padding + "║")

        header_lines.extend([
            "╚" + "═" * 78 + "╝",
            ""
        ])

        return "\n".join(header_lines)

# Use custom processor
custom_rp = CustomResponseProcessor(output_dir=Path("outputs/"))
custom_rp.save_response(response_text, model_name="Qwen3 Coder 30B")
```

#### Custom Language Mappings

```python
# Add custom language extensions
ResponseProcessor._get_extension = staticmethod(lambda language: {
    **ResponseProcessor._get_extension.__func__.__code__.co_consts[1],  # Original mappings
    "solidity": ".sol",
    "dart": ".dart",
    "elixir": ".ex",
    "haskell": ".hs",
    "julia": ".jl"
}.get(language.lower(), ".txt"))
```

### Performance Tips

1. **Batch Processing**: Extract code from multiple responses in a single pass
2. **Lazy Loading**: Only load files when needed, use `list_saved_responses()` for metadata
3. **Directory Organization**: Use dated subdirectories for large volumes
4. **Async Export**: For large responses, consider async file I/O
5. **Memory Management**: Process responses in chunks for very large outputs

### Troubleshooting

#### Issue: Code blocks not detected

**Cause**: Malformed markdown code fences

**Solution**: Ensure proper markdown format:
```python
# Correct format:
"""
```python
code here
```
"""

# Incorrect formats that fail:
# ` ` `python (spaces in fence)
# ```python code``` (no newlines)
```

#### Issue: File permissions error

**Cause**: Output directory not writable

**Solution**: Check directory permissions
```python
output_dir = Path("outputs/")
output_dir.mkdir(exist_ok=True, parents=True)

# Verify writable
test_file = output_dir / ".test"
try:
    test_file.touch()
    test_file.unlink()
    print("Directory is writable")
except PermissionError:
    print("Permission denied - check directory permissions")
```

#### Issue: Clipboard copy fails

**Cause**: `pyperclip` not installed

**Solution**: Install dependency
```bash
pip install pyperclip
```

#### Issue: Encoding errors with special characters

**Cause**: Non-UTF-8 encoding

**Solution**: Always use UTF-8 encoding
```python
# Correct:
filepath.write_text(content, encoding='utf-8')

# Also handle read operations:
content = filepath.read_text(encoding='utf-8')
```

### Best Practices

1. **Always Attach Metadata**: Include model name, prompt, tokens, duration for traceability
2. **Use Descriptive Filenames**: For manual saves, use meaningful names instead of timestamps
3. **Extract Code Early**: Pull code blocks immediately for testing/validation
4. **Archive Regularly**: Move old responses to dated subdirectories
5. **Validate Output**: Check statistics to ensure complete responses
6. **Integrate with Sessions**: Link saved files to session IDs for full context
7. **Test Format Conversions**: Verify Markdown/HTML rendering before bulk export
8. **Clean Up**: Remove temporary/test responses regularly
9. **Backup Important Responses**: Copy critical outputs to version control
10. **Use Consistent Metadata Keys**: Standardize keys across your project

### FAQ

**Q: How do I extract only Python code blocks?**
```python
python_blocks = [
    block for block in rp.extract_code_blocks(response_text)
    if block['language'] == 'python'
]
```

**Q: Can I customize the timestamp format?**
```python
# Modify the timestamp in save_response() or format_as_markdown()
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Default
timestamp = datetime.now().strftime("%d-%b-%Y %I:%M %p")  # Custom
```

**Q: How do I export to HTML with syntax highlighting?**
```python
# Use a markdown-to-HTML library with syntax highlighting
import markdown
from pygments.formatters import HtmlFormatter

md_text = rp.format_as_markdown(response_text, model_name="Qwen3 Coder")
html = markdown.markdown(md_text, extensions=['fenced_code', 'codehilite'])

# Add Pygments CSS
formatter = HtmlFormatter()
css = formatter.get_style_defs('.codehilite')
full_html = f"<style>{css}</style>\n{html}"

Path("output.html").write_text(full_html, encoding='utf-8')
```

**Q: How do I process responses from batch jobs?**
```python
from batch_processor import BatchProcessor

bp = BatchProcessor(checkpoint_dir=Path("checkpoints/"))
job, results = bp.load_checkpoint(Path("checkpoints/batch_abc123.json"))

# Extract code from all successful results
for result in results:
    if result.success:
        blocks = rp.extract_code_blocks(result.response_text)
        # Process blocks...
```

**Q: Can I stream large responses to disk?**
```python
# For very large responses, write incrementally
filepath = rp.output_dir / "large_response.txt"

with open(filepath, 'w', encoding='utf-8') as f:
    # Write metadata header
    header = rp._build_metadata_header("Model Name", metadata)
    f.write(header + "\n")

    # Stream response chunks
    for chunk in response_chunks:
        f.write(chunk)
```

---

---

## 5. Batch Processing Mode

### Overview

The Batch Processing system enables automated execution of multiple prompts with enterprise-grade reliability features including checkpoint/resume, progress tracking, error handling strategies, and comprehensive result management. Designed for processing anywhere from 10 to 10,000+ prompts, this system handles long-running AI operations with automatic recovery from failures, detailed progress monitoring, and flexible export options.

Perfect for scenarios like test suite generation, dataset processing, documentation generation, code review automation, translation workflows, and any task requiring consistent application of AI models across multiple inputs. The checkpoint system ensures no work is lost, even if processing is interrupted.

### Key Capabilities

- **Checkpoint/Resume**: Automatic progress checkpoints every 5 prompts with full state recovery
- **Error Handling Strategies**: Configurable error policies (stop, continue, threshold-based)
- **Progress Monitoring**: Real-time callbacks for integration with UI/CLI progress bars
- **Multiple Input Formats**: Load prompts from TXT, JSON, or programmatic lists
- **Result Persistence**: Export to JSON, CSV with comprehensive metadata
- **Job Management**: List, resume, and analyze past batch jobs
- **Retry Logic**: Automatic retry with exponential backoff (optional)
- **Resource Monitoring**: Track tokens, duration, success rates per job
- **Parallel Execution**: Process multiple prompts concurrently (future enhancement)
- **Result Analytics**: Success rates, performance metrics, failure analysis

### Architecture

```
BatchProcessor (batch_processor.py)
├── Job Creation & Management
│   ├── BatchJob (dataclass)
│   └── BatchResult (dataclass)
├── Checkpoint System
│   ├── save_checkpoint()
│   ├── load_checkpoint()
│   └── list_checkpoints()
├── Execution Engine
│   ├── process_batch()
│   ├── Error Strategy Parser
│   └── Progress Callbacks
└── Export System
    ├── export_results() (JSON/CSV)
    └── Result Analysis
```

### Complete API Reference

#### BatchJob Dataclass

```python
@dataclass
class BatchJob:
    job_id: str                      # Unique 8-char identifier
    model_id: str                    # Model to use
    prompts: List[str]               # All prompts to process
    total_prompts: int               # Total count
    completed: int = 0               # Successfully completed
    failed: int = 0                  # Failed count
    status: str = "pending"          # pending|running|paused|completed|failed
    started_at: Optional[datetime]   # Start timestamp
    completed_at: Optional[datetime] # Completion timestamp
    checkpoint_file: Optional[Path]  # Path to checkpoint JSON
```

#### BatchResult Dataclass

```python
@dataclass
class BatchResult:
    prompt_index: int                # Index in original prompts list
    prompt: str                      # Original prompt text
    response_text: str               # Model response
    tokens_input: int                # Input tokens
    tokens_output: int               # Output tokens
    duration: float                  # Time in seconds
    success: bool                    # True if succeeded
    error_message: Optional[str]     # Error details if failed
```

#### BatchProcessor Class

```python
class BatchProcessor:
    def __init__(self, checkpoint_dir: Path)
    def load_prompts_from_file(self, file_path: Path) -> List[str]
    def create_job(self, model_id: str, prompts: List[str]) -> BatchJob
    def process_batch(self, job: BatchJob, execute_fn: Callable,
                     progress_callback: Optional[Callable] = None,
                     error_strategy: str = "continue") -> List[BatchResult]
    def save_checkpoint(self, job: BatchJob, results: List[BatchResult])
    def load_checkpoint(self, checkpoint_file: Path) -> tuple[BatchJob, List[BatchResult]]
    def list_checkpoints(self) -> List[Dict[str, Any]]
    def export_results(self, job: BatchJob, results: List[BatchResult],
                      output_file: Path, format: str = 'json')
```

### Configuration Options

#### Error Handling Strategies

```python
# Continue on all errors (default)
error_strategy = "continue"

# Stop on first error
error_strategy = "stop"

# Stop after N errors
error_strategy = "threshold:5"  # Stop after 5 failures
```

#### Checkpoint Frequency

```python
# Default: Checkpoint every 5 prompts
# Modify in process_batch():
if (idx + 1) % 5 == 0:  # Change 5 to desired frequency
    self.save_checkpoint(job, results)
```

### Detailed Usage Examples

#### Basic: Simple Batch Processing

```python
from batch_processor import BatchProcessor
from pathlib import Path

# Initialize
bp = BatchProcessor(checkpoint_dir=Path("batch_checkpoints/"))

# Define prompts
prompts = [
    "Explain quantum entanglement",
    "Write a Python sorting algorithm",
    "Summarize the French Revolution",
    "Calculate the factorial of 10",
    "Describe photosynthesis process"
]

# Create job
job = bp.create_job(
    model_id="qwen25-14b",
    prompts=prompts
)

print(f"Created job {job.job_id} with {job.total_prompts} prompts")

# Define execution function
def execute_prompt(prompt):
    # This should call your AI router
    response = ai_router.run_model(
        model_id=job.model_id,
        model_data=ai_router.models[job.model_id],
        prompt=prompt
    )
    return response

# Execute batch
results = bp.process_batch(
    job=job,
    execute_fn=execute_prompt,
    error_strategy="continue"
)

# Export results
bp.export_results(
    job=job,
    results=results,
    output_file=Path("batch_results.json"),
    format="json"
)

print(f"Completed: {job.completed}/{job.total_prompts}")
print(f"Failed: {job.failed}")
```

#### Intermediate: Progress Tracking with Callbacks

```python
from datetime import datetime
import sys

def progress_callback(job, current):
    """Custom progress display"""
    progress = (current / job.total_prompts) * 100
    bar_length = 50
    filled = int(bar_length * current / job.total_prompts)
    bar = '█' * filled + '░' * (bar_length - filled)

    elapsed = (datetime.now() - job.started_at).total_seconds()
    rate = current / elapsed if elapsed > 0 else 0
    remaining = (job.total_prompts - current) / rate if rate > 0 else 0

    sys.stdout.write(f'\r[{bar}] {progress:.1f}% ({current}/{job.total_prompts}) '
                    f'| Success: {job.completed} | Failed: {job.failed} '
                    f'| ETA: {remaining:.0f}s')
    sys.stdout.flush()

# Execute with progress tracking
results = bp.process_batch(
    job=job,
    execute_fn=execute_prompt,
    progress_callback=progress_callback,
    error_strategy="continue"
)

print("\nBatch processing complete!")
```

**Output:**
```
[████████████████████████░░░░░░░░] 60.0% (30/50) | Success: 28 | Failed: 2 | ETA: 45s
```

#### Advanced: Resume from Checkpoint

```python
# List available checkpoints
checkpoints = bp.list_checkpoints()

print("Available batch jobs:")
for ckpt in checkpoints:
    print(f"  {ckpt['job_id']}: {ckpt['status']} - "
          f"{ckpt['completed']}/{ckpt['total']} completed "
          f"({ckpt['failed']} failed)")

# Resume incomplete job
checkpoint_file = Path("batch_checkpoints/batch_abc12345.json")
job, results = bp.load_checkpoint(checkpoint_file)

print(f"Resuming job {job.job_id} from {len(results)} completed prompts")

# Continue processing from where we left off
remaining_prompts = job.prompts[len(results):]
remaining_indices = range(len(results), job.total_prompts)

for idx, prompt in zip(remaining_indices, remaining_prompts):
    try:
        response = execute_prompt(prompt)
        result = BatchResult(
            prompt_index=idx,
            prompt=prompt,
            response_text=response.text,
            tokens_input=response.tokens_input,
            tokens_output=response.tokens_output,
            duration=response.duration_seconds,
            success=True
        )
        job.completed += 1
    except Exception as e:
        result = BatchResult(
            prompt_index=idx,
            prompt=prompt,
            response_text="",
            tokens_input=0,
            tokens_output=0,
            duration=0.0,
            success=False,
            error_message=str(e)
        )
        job.failed += 1

    results.append(result)

    # Checkpoint every 5 prompts
    if (idx + 1) % 5 == 0:
        bp.save_checkpoint(job, results)

job.status = "completed"
job.completed_at = datetime.now()
bp.save_checkpoint(job, results)

print(f"Job {job.job_id} resumed and completed!")
```

#### Real-World: Test Suite Generation

```python
# Generate comprehensive test suite for API endpoints
test_scenarios = [
    "Generate unit tests for user registration endpoint",
    "Generate integration tests for login flow",
    "Generate tests for password reset functionality",
    "Generate edge case tests for email validation",
    "Generate performance tests for search endpoint",
    # ... 100+ more scenarios
]

# Create batch job
job = bp.create_job(
    model_id="qwen3-coder-30b",
    prompts=test_scenarios
)

# Execute with threshold error strategy
results = bp.process_batch(
    job=job,
    execute_fn=execute_prompt,
    progress_callback=progress_callback,
    error_strategy="threshold:10"  # Stop after 10 failures
)

# Analyze results
successful_tests = [r for r in results if r.success]
failed_tests = [r for r in results if not r.success]

print(f"\nTest Generation Summary:")
print(f"  Total scenarios: {len(test_scenarios)}")
print(f"  Tests generated: {len(successful_tests)}")
print(f"  Failed: {len(failed_tests)}")
print(f"  Success rate: {len(successful_tests)/len(results)*100:.1f}%")

# Extract and save all test code
from response_processor import ResponseProcessor
rp = ResponseProcessor(output_dir=Path("generated_tests/"))

for i, result in enumerate(successful_tests):
    code_blocks = rp.extract_code_blocks(result.response_text)
    for j, block in enumerate(code_blocks):
        if block['language'] == 'python':
            filename = f"test_{i:03d}_{j}.py"
            (rp.output_dir / filename).write_text(block['code'], encoding='utf-8')

print(f"Extracted test files saved to generated_tests/")
```

### Loading Prompts from Files

#### TXT Format (One prompt per line)

```text
# prompts.txt
Explain machine learning
Write a binary search algorithm
Summarize World War II
Calculate compound interest
Describe the water cycle
```

```python
prompts = bp.load_prompts_from_file(Path("prompts.txt"))
# Returns: ["Explain machine learning", "Write a binary search algorithm", ...]
```

#### JSON Format (Array)

```json
[
  "Explain machine learning",
  "Write a binary search algorithm",
  "Summarize World War II"
]
```

```python
prompts = bp.load_prompts_from_file(Path("prompts.json"))
```

#### JSON Format (Object with metadata)

```json
{
  "prompts": [
    "Explain machine learning",
    "Write a binary search algorithm"
  ],
  "metadata": {
    "created": "2025-12-09",
    "category": "education"
  }
}
```

```python
prompts = bp.load_prompts_from_file(Path("prompts.json"))
# Extracts from "prompts" key
```

### Checkpoint System

#### Checkpoint File Structure

```json
{
  "job": {
    "job_id": "abc12345",
    "model_id": "qwen25-14b",
    "prompts": ["prompt1", "prompt2", ...],
    "total_prompts": 50,
    "completed": 30,
    "failed": 2,
    "status": "running",
    "started_at": "2025-12-09T14:30:00",
    "completed_at": null,
    "checkpoint_file": "batch_checkpoints/batch_abc12345.json"
  },
  "results": [
    {
      "prompt_index": 0,
      "prompt": "Explain quantum physics",
      "response_text": "Quantum physics is...",
      "tokens_input": 15,
      "tokens_output": 247,
      "duration": 2.3,
      "success": true,
      "error_message": null
    },
    ...
  ],
  "timestamp": "2025-12-09T14:32:15"
}
```

### Export Formats

#### JSON Export

```python
bp.export_results(
    job=job,
    results=results,
    output_file=Path("batch_results.json"),
    format="json"
)
```

**Generated JSON:**
```json
{
  "job": {
    "job_id": "abc12345",
    "model_id": "qwen25-14b",
    "total_prompts": 50,
    "completed": 48,
    "failed": 2,
    "status": "completed",
    "started_at": "2025-12-09T14:30:00",
    "completed_at": "2025-12-09T14:45:30"
  },
  "results": [...],
  "summary": {
    "total": 50,
    "completed": 48,
    "failed": 2,
    "success_rate": 96.0
  }
}
```

#### CSV Export

```python
bp.export_results(
    job=job,
    results=results,
    output_file=Path("batch_results.csv"),
    format="csv"
)
```

**Generated CSV:**
```csv
index,prompt,response,success,tokens_in,tokens_out,duration,error
0,"Explain quantum physics","Quantum physics is...",True,15,247,2.30,
1,"Write sorting algorithm","Here's a sorting...",True,12,189,1.85,
2,"Calculate factorial","To calculate...",False,8,0,0.00,"Timeout error"
```

### Integration with Other Features

#### Template Library Integration

```python
from template_manager import TemplateManager

tm = TemplateManager(Path("prompt-templates/"))
template = tm.load_template("code-review.yaml")

# Generate prompts from template
code_files = Path("src/").glob("*.py")
prompts = []

for code_file in code_files:
    code_content = code_file.read_text()
    rendered = template.render({
        "language": "Python",
        "code": code_content,
        "focus_areas": "security, performance"
    })
    prompts.append(rendered['user_prompt'])

# Batch process all code reviews
job = bp.create_job(model_id="qwen3-coder-30b", prompts=prompts)
results = bp.process_batch(job, execute_fn=execute_prompt)
```

#### Analytics Dashboard Integration

```python
# After batch completion, analyze with analytics
from analytics_dashboard import AnalyticsDashboard

# Calculate batch statistics
total_tokens = sum(r.tokens_input + r.tokens_output for r in results)
total_duration = sum(r.duration for r in results)
avg_tokens_per_prompt = total_tokens / len(results)
avg_duration = total_duration / len(results)

print(f"Batch Analytics:")
print(f"  Total tokens: {total_tokens:,}")
print(f"  Avg tokens/prompt: {avg_tokens_per_prompt:.0f}")
print(f"  Total time: {total_duration:.1f}s")
print(f"  Avg time/prompt: {avg_duration:.2f}s")
print(f"  Throughput: {len(results)/total_duration:.2f} prompts/sec")
```

### Performance Tips

1. **Optimal Batch Size**: 50-200 prompts per job for balance between checkpointing and overhead
2. **Checkpoint Frequency**: Every 5-10 prompts is optimal (too frequent = slow, too rare = data loss risk)
3. **Error Strategy**: Use "threshold:N" for production, "continue" for testing
4. **Parallel Processing**: Future enhancement for 10x speed improvement
5. **Memory Management**: Process in chunks if dealing with 1000+ prompts
6. **Model Selection**: Use faster models for large batches, reserve premium models for small critical batches

### Troubleshooting

#### Issue: Checkpoint file corrupted

**Cause**: Process killed during checkpoint save

**Solution**: Checkpoint files are atomic writes, use backup
```python
import shutil
checkpoint_backup = Path("batch_checkpoints/batch_abc12345.json.backup")
if checkpoint_backup.exists():
    shutil.copy(checkpoint_backup, checkpoint_file)
    job, results = bp.load_checkpoint(checkpoint_file)
```

#### Issue: Memory usage grows over time

**Cause**: Large responses stored in memory

**Solution**: Export results incrementally
```python
# Export every 50 results
if len(results) % 50 == 0:
    bp.export_results(job, results, Path(f"batch_partial_{len(results)}.json"))
```

#### Issue: Slow processing rate

**Cause**: Model latency or network issues

**Solution**: Monitor duration per prompt
```python
slow_prompts = [r for r in results if r.duration > 10.0]
print(f"Slow prompts (>10s): {len(slow_prompts)}")
for sp in slow_prompts[:5]:
    print(f"  {sp.prompt[:50]}... took {sp.duration:.1f}s")
```

#### Issue: High failure rate

**Cause**: Malformed prompts or model issues

**Solution**: Analyze failure patterns
```python
failures = [r for r in results if not r.success]
error_types = {}
for f in failures:
    error_type = f.error_message.split(':')[0] if f.error_message else "Unknown"
    error_types[error_type] = error_types.get(error_type, 0) + 1

print("Failure breakdown:")
for error, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
    print(f"  {error}: {count}")
```

### Best Practices

1. **Always Use Checkpoints**: Enable automatic checkpointing for all batch jobs
2. **Test with Small Batches**: Run 5-10 prompts first to validate setup
3. **Monitor Progress**: Use progress callbacks to detect issues early
4. **Set Error Thresholds**: Use "threshold:N" to avoid wasting resources on systematic failures
5. **Export Incrementally**: For large batches (500+), export results periodically
6. **Name Jobs Meaningfully**: Use descriptive job IDs in production
7. **Archive Completed Jobs**: Move old checkpoints to archive directory
8. **Validate Results**: Check success rates and durations after completion
9. **Use Templates**: Combine with template library for consistent prompt formatting
10. **Log Everything**: Capture all batch metadata for auditing

### FAQ

**Q: Can I run multiple batch jobs in parallel?**

A: Yes, create separate BatchProcessor instances with different checkpoint directories:
```python
bp1 = BatchProcessor(checkpoint_dir=Path("batch_checkpoints/job1/"))
bp2 = BatchProcessor(checkpoint_dir=Path("batch_checkpoints/job2/"))
```

**Q: How do I retry only failed prompts?**

```python
failed_results = [r for r in results if not r.success]
failed_prompts = [r.prompt for r in failed_results]

retry_job = bp.create_job(model_id="qwen25-14b", prompts=failed_prompts)
retry_results = bp.process_batch(retry_job, execute_fn=execute_prompt)
```

**Q: Can I change models mid-batch?**

A: Resume with a new job using remaining prompts:
```python
remaining = job.prompts[len(results):]
new_job = bp.create_job(model_id="different-model", prompts=remaining)
```

**Q: How do I estimate completion time?**

```python
completed_count = len(results)
if completed_count > 0:
    avg_duration = sum(r.duration for r in results) / completed_count
    remaining = job.total_prompts - completed_count
    eta_seconds = remaining * avg_duration
    print(f"ETA: {eta_seconds/60:.1f} minutes")
```

**Q: What's the maximum number of prompts per job?**

A: No hard limit, but recommend <10,000 prompts per job for manageability. For larger workloads, split into multiple jobs.

---

---

## 6. Smart Model Auto-Selection

### Overview

AI-powered model recommendation based on task analysis and user preferences.

### Key Capabilities

- Keyword analysis
- Task type detection
- Preference learning
- Performance-based selection
- Cost awareness

### Usage Examples

```python
from model_selector import ModelSelector

ms = ModelSelector(preferences_file=Path(".ai-router-preferences.json"))

# Get recommendation
recommendation = ms.select_model(
    prompt="Optimize this Python sorting function for large datasets"
)

# Returns:
# {
#     "model_id": "qwen3-coder-30b",
#     "confidence": 0.92,
#     "reasons": [
#         "Coding task detected (keywords: Python, function, optimize)",
#         "Best coding model (94% HumanEval)",
#         "User preference: chosen 15/18 times for coding tasks"
#     ],
#     "alternatives": [
#         {"model_id": "phi4-14b", "confidence": 0.67, "reason": "Good for algorithms"}
#     ]
# }
```

---

## 7. Performance Analytics Dashboard

### Overview

Track usage, performance, and costs with visual dashboards and reports.

### Key Capabilities

- Usage statistics
- Model performance comparison
- Cost tracking
- Activity charts
- Export reports

### Usage Examples

```python
from analytics_dashboard import AnalyticsDashboard

analytics = AnalyticsDashboard(session_manager)

# Get usage overview
stats = analytics.get_usage_statistics(days=30)
# Returns: total sessions, messages, tokens, etc.

# Model usage
model_stats = analytics.get_model_usage(days=30)

# Daily activity
activity = analytics.get_daily_activity(days=30)

# Export report
analytics.export_report(
    start_date="2025-12-01",
    end_date="2025-12-08",
    format="html",
    filename="monthly_report.html"
)
```

---

## 8. Context Management & Injection

### Overview

Inject files, URLs, and code into conversations for enhanced context.

### Key Capabilities

- File content injection
- Directory indexing
- URL fetching
- Code snippet integration
- Context size management

### Usage Examples

```python
from context_manager import ContextManager

cm = ContextManager()

# Add file context
cm.add_file_context("path/to/file.py")

# Add directory (multiple files)
cm.add_directory_context("path/to/project", file_pattern="*.py")

# Add URL content
cm.add_url_context("https://example.com/article")

# Add code snippet
cm.add_code_context(
    code="def hello(): print('world')",
    language="python"
)

# Get combined context for model
full_context = cm.get_context_for_model(max_tokens=4000)
```

---

## 9. Prompt Chaining Workflows

### Overview

YAML-based workflows for multi-step AI automation with variable passing and conditional logic.

### Key Capabilities

- Multi-step workflows
- Variable passing
- Conditional execution
- Error handling
- Workflow templates

### Usage Examples

```yaml
# workflow.yaml
id: research_and_summarize
name: Research Topic and Summarize
variables:
  topic: "Quantum Computing"
  depth: "intermediate"

steps:
  - name: research
    type: prompt
    model: qwen25-14b
    prompt: "Research {{topic}} at {{depth}} level"
    save_to: research_results

  - name: summarize
    type: prompt
    model: phi4-14b
    prompt: "Summarize this research:\n\n{{research_results}}"
    save_to: final_summary

  - name: export
    type: export
    data: "{{final_summary}}"
    format: markdown
    filename: "summary_{{topic}}.md"
```

```python
from workflow_engine import WorkflowEngine

we = WorkflowEngine(workflows_dir=Path("workflows/"), ai_router=router)

# Load workflow
workflow = we.load_workflow("research_and_summarize.yaml")

# Execute
result = we.execute_workflow(workflow)

# Result contains all step outputs and final summary
```

---

## Summary: All Features at a Glance

| # | Feature | Primary Use | Status |
|---|---------|-------------|--------|
| 1 | **Session Management** | Save/resume conversations | ✅ Production |
| 2 | **Prompt Templates** | Reusable prompts | ✅ Production |
| 3 | **Model Comparison** | A/B testing | ✅ Production |
| 4 | **Response Processing** | Format & export | ✅ Production |
| 5 | **Batch Processing** | Multi-prompt automation | ✅ Production |
| 6 | **Smart Selection** | AI model recommendation | ✅ Production |
| 7 | **Analytics** | Usage tracking | ✅ Production |
| 8 | **Context Management** | File/URL injection | ✅ Production |
| 9 | **Workflow Engine** | Prompt chaining | ✅ Production |

---

**For detailed API documentation, see [API_REFERENCE.md](API_REFERENCE.md)**

_Last Updated: December 8, 2025_
