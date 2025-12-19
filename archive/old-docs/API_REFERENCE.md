# AI Router Enhanced - API Reference

**Version:** 1.0
**Last Updated:** December 9, 2025
**Platform Support:** Windows/WSL (RTX 3090), macOS (Apple M4 Pro)

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Core Classes](#core-classes)
  - [AIRouter](#airouter)
  - [ModelDatabase](#modeldatabase)
  - [ModelResponse](#modelresponse)
  - [Colors](#colors)
- [Session Management](#session-management)
  - [SessionManager](#sessionmanager)
- [Template System](#template-system)
  - [TemplateManager](#templatemanager)
  - [PromptTemplate](#prompttemplate)
- [Context Management](#context-management)
  - [ContextManager](#contextmanager)
- [Response Processing](#response-processing)
  - [ResponseProcessor](#responseprocessor)
- [Model Selection](#model-selection)
  - [ModelSelector](#modelselector)
- [Batch Processing](#batch-processing)
  - [BatchProcessor](#batchprocessor)
  - [BatchJob](#batchjob)
  - [BatchResult](#batchresult)
- [Analytics](#analytics)
  - [AnalyticsDashboard](#analyticsdashboard)
- [Workflows](#workflows)
  - [WorkflowEngine](#workflowengine)
  - [WorkflowStep](#workflowstep)
  - [WorkflowExecution](#workflowexecution)
- [Model Comparison](#model-comparison)
  - [ModelComparison](#modelcomparison)
  - [ComparisonResult](#comparisonresult)
- [Database Schema](#database-schema)
- [Configuration Files](#configuration-files)
- [Examples](#examples)

---

## Overview

AI Router Enhanced is a comprehensive CLI application for intelligent model selection and execution across multiple LLM platforms. It provides sophisticated features including:

- **Intelligent Model Selection**: Automatic use-case detection and model recommendation
- **Session Management**: SQLite-based conversation history with full-text search
- **Template System**: YAML + Jinja2 prompt templating
- **Context Injection**: File and text context loading with token management
- **Batch Processing**: Process multiple prompts with checkpointing
- **Analytics Dashboard**: Usage statistics and performance metrics
- **Workflow Engine**: Multi-step AI automation with conditional logic
- **Model Comparison**: Side-by-side A/B testing

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      AIRouter                           │
│  (Main orchestration and CLI interface)                 │
└────────────┬────────────────────────────────────────────┘
             │
             ├──► ModelDatabase (Model catalog)
             ├──► SessionManager (Conversation history)
             ├──► TemplateManager (Prompt templates)
             ├──► ContextManager (File/text context)
             ├──► ModelSelector (Smart model selection)
             ├──► ResponseProcessor (Output handling)
             ├──► BatchProcessor (Batch execution)
             ├──► AnalyticsDashboard (Statistics)
             ├──► WorkflowEngine (Multi-step automation)
             └──► ModelComparison (A/B testing)
```

---

## Core Classes

### AIRouter

**Description:** Main application class that orchestrates all AI Router functionality.

**Location:** `ai-router.py`

#### Constructor

```python
def __init__(self)
```

Initializes the AI Router application with platform-specific settings.

**Parameters:** None

**Attributes:**
- `platform` (str): Current platform ('Windows', 'Linux', 'Darwin')
- `models` (Dict): Available models for current platform
- `models_dir` (Path): Base directory for models and data
- `response_processor` (ResponseProcessor): Handles response post-processing
- `model_selector` (ModelSelector): Intelligent model selection
- `context_manager` (ContextManager): Context injection manager
- `template_manager` (TemplateManager): Prompt template system
- `session_manager` (SessionManager): Conversation history
- `batch_processor` (BatchProcessor): Batch execution engine
- `analytics` (AnalyticsDashboard): Analytics and statistics
- `workflow_engine` (WorkflowEngine): Multi-step workflow automation
- `model_comparison` (ModelComparison): Model A/B testing
- `bypass_mode` (bool): Auto-yes mode for confirmations

**Example:**
```python
from pathlib import Path
import sys
sys.path.append('/mnt/d/models')

from ai_router import AIRouter

# Initialize router
router = AIRouter()

# Access components
print(f"Platform: {router.platform}")
print(f"Available models: {len(router.models)}")
```

#### Methods

##### print_banner()

```python
def print_banner(self)
```

Displays the AI Router banner with platform and model information.

**Parameters:** None

**Returns:** None

**Example:**
```python
router.print_banner()
# Outputs colorful banner with system info
```

---

##### list_models()

```python
def list_models(self)
```

Displays an interactive list of all available models with details.

**Parameters:** None

**Returns:** None

**Side Effects:** Prints formatted model list to stdout

**Example:**
```python
router.list_models()
# Displays:
# [1] Qwen3 Coder 30B Q4_K_M
#     Use Case: Advanced coding, code review, architecture design
#     Speed: 25-35 tok/sec
#     ...
```

---

##### print_model_info()

```python
def print_model_info(self, model_id: str, model_data: Dict)
```

Displays detailed information about a specific model.

**Parameters:**
- `model_id` (str): Model identifier (e.g., 'qwen3-coder-30b')
- `model_data` (Dict): Model configuration dictionary

**Returns:** None

**Example:**
```python
model_id = 'qwen3-coder-30b'
model_data = router.models[model_id]
router.print_model_info(model_id, model_data)
```

---

##### run_model()

```python
def run_model(
    self,
    model_id: str,
    model_data: Dict,
    prompt: str
) -> ModelResponse
```

Executes a model with the given prompt and returns the response.

**Parameters:**
- `model_id` (str): Model identifier
- `model_data` (Dict): Model configuration
- `prompt` (str): User prompt text

**Returns:** `ModelResponse` object with response text and metadata

**Raises:**
- `RuntimeError`: If model execution fails
- `FileNotFoundError`: If model file not found

**Example:**
```python
response = router.run_model(
    'qwen3-coder-30b',
    router.models['qwen3-coder-30b'],
    'Write a hello world function in Python'
)

print(response.text)
print(f"Tokens: {response.tokens_output}")
print(f"Duration: {response.duration_seconds}s")
```

---

##### run_llamacpp_model()

```python
def run_llamacpp_model(
    self,
    model_id: str,
    model_data: Dict,
    prompt: str
) -> ModelResponse
```

Executes a llama.cpp model (RTX 3090/WSL models).

**Parameters:**
- `model_id` (str): Model identifier
- `model_data` (Dict): Model configuration
- `prompt` (str): User prompt

**Returns:** `ModelResponse` object

**Notes:**
- Automatically handles system prompts
- Applies model-specific flags (e.g., --jinja)
- Parses token counts and timing from output

**Example:**
```python
response = router.run_llamacpp_model(
    'phi4-14b',
    router.models['phi4-14b'],
    'Solve: 2x + 5 = 15'
)
```

---

##### run_mlx_model()

```python
def run_mlx_model(
    self,
    model_id: str,
    model_data: Dict,
    prompt: str
) -> ModelResponse
```

Executes an MLX model (MacBook M4 Pro models).

**Parameters:**
- `model_id` (str): Model identifier
- `model_data` (Dict): Model configuration
- `prompt` (str): User prompt

**Returns:** `ModelResponse` object

**Notes:**
- Uses mlx_lm.generate for Apple Silicon optimization
- 2-3x faster than llama.cpp on M4

**Example:**
```python
response = router.run_mlx_model(
    'qwen25-14b-mlx',
    router.models['qwen25-14b-mlx'],
    'Explain quantum computing'
)
```

---

##### parse_llama_output()

```python
def parse_llama_output(
    self,
    raw_output: str
) -> tuple[str, int, int]
```

Parses llama.cpp output to extract response text and token counts.

**Parameters:**
- `raw_output` (str): Raw stdout from llama.cpp

**Returns:** Tuple of (response_text, input_tokens, output_tokens)

**Example:**
```python
raw = """llama_decode: n_tokens = 512
The answer is 42.
Generated 10 tokens in 2.5 seconds"""

text, tokens_in, tokens_out = router.parse_llama_output(raw)
# Returns: ('The answer is 42.', 512, 10)
```

---

##### interactive_mode()

```python
def interactive_mode(self)
```

Launches the main interactive menu for AI Router.

**Parameters:** None

**Returns:** None

**Features:**
- Model selection (auto/manual)
- Context management
- Template system
- Session history
- Batch processing
- Workflows
- Model comparison
- Analytics

**Example:**
```python
router.interactive_mode()
# Displays interactive menu and handles user input
```

---

##### auto_select_mode()

```python
def auto_select_mode(self)
```

Automatic model selection based on prompt analysis.

**Parameters:** None

**Returns:** None

**Process:**
1. User enters prompt
2. System analyzes prompt keywords
3. Recommends best model with confidence score
4. User confirms or selects alternative
5. Model executes

**Example:**
```python
router.auto_select_mode()
# Prompt: "Write a Python function to sort a list"
# Detected: coding (85% confidence)
# Recommended: Qwen3 Coder 30B
```

---

##### manual_select_mode()

```python
def manual_select_mode(self)
```

Manual model selection with full list display.

**Parameters:** None

**Returns:** None

**Example:**
```python
router.manual_select_mode()
# Displays numbered list of all models
# User selects by number
```

---

##### show_model_recommendations()

```python
def show_model_recommendations(self, prompt: str)
```

Shows top 3 model recommendations for a prompt.

**Parameters:**
- `prompt` (str): User's input prompt

**Returns:** None

**Example:**
```python
router.show_model_recommendations(
    "Calculate the derivative of x^2 + 3x + 2"
)
# Shows:
# 1. Phi-4 14B (reasoning: 92%)
# 2. Ministral-3 14B (reasoning: 88%)
# 3. DeepSeek R1 14B (reasoning: 85%)
```

---

##### toggle_bypass_mode()

```python
def toggle_bypass_mode(self)
```

Toggles auto-yes mode for all confirmations.

**Parameters:** None

**Returns:** None

**Example:**
```python
router.toggle_bypass_mode()
# Enables/disables bypass mode
# Saves to .ai-router-config.json
```

---

##### context_mode()

```python
def context_mode(self)
```

Launches context management interface.

**Parameters:** None

**Returns:** None

**Features:**
- Add files as context
- Add text snippets
- Remove context items
- Set token limits
- View context summary
- Execute with context

**Example:**
```python
router.context_mode()
# Interactive context management menu
```

---

##### add_files_to_context()

```python
def add_files_to_context(self)
```

Adds one or more files to the context manager.

**Parameters:** None

**Returns:** None

**Security:** Validates paths to prevent directory traversal (CVE-2025-AIR-002)

**Example:**
```python
router.add_files_to_context()
# Prompts for file paths
# Validates and loads file contents
```

---

##### add_text_to_context()

```python
def add_text_to_context(self)
```

Adds arbitrary text as context.

**Parameters:** None

**Returns:** None

**Example:**
```python
router.add_text_to_context()
# Prompts for label and text content
# Adds to context manager
```

---

##### template_mode()

```python
def template_mode(self)
```

Launches template management interface.

**Parameters:** None

**Returns:** None

**Features:**
- Browse templates by category
- Select and render templates
- Create new templates
- Variable substitution

**Example:**
```python
router.template_mode()
# Interactive template menu
```

---

##### session_mode()

```python
def session_mode(self)
```

Launches session management interface.

**Parameters:** None

**Returns:** None

**Features:**
- List recent sessions
- Search sessions by content
- Resume sessions
- View session details
- Export sessions
- Delete old sessions

**Example:**
```python
router.session_mode()
# Interactive session management
```

---

##### continue_session()

```python
def continue_session(self, session_id: str)
```

Continues an existing conversation session.

**Parameters:**
- `session_id` (str): UUID of session to continue

**Returns:** None

**Example:**
```python
router.continue_session('a1b2c3d4-e5f6-7890-abcd-ef1234567890')
# Loads session history
# Continues conversation with same model
```

---

##### batch_mode()

```python
def batch_mode(self)
```

Launches batch processing interface.

**Parameters:** None

**Returns:** None

**Features:**
- Load prompts from file
- Manual prompt entry
- Resume from checkpoint
- View checkpoint list
- Progress tracking
- Error handling strategies

**Example:**
```python
router.batch_mode()
# Interactive batch processing menu
```

---

##### batch_from_file()

```python
def batch_from_file(self)
```

Loads prompts from a text or JSON file for batch processing.

**Parameters:** None

**Returns:** None

**Supported Formats:**
- Text files (one prompt per line)
- JSON files (array of strings or {"prompts": [...]})

**Example:**
```python
router.batch_from_file()
# Prompts for file path
# Loads and processes all prompts
```

---

##### workflow_mode()

```python
def workflow_mode(self)
```

Launches workflow automation interface.

**Parameters:** None

**Returns:** None

**Features:**
- Run workflows
- List available workflows
- Create from template
- Validate workflows

**Example:**
```python
router.workflow_mode()
# Interactive workflow menu
```

---

##### comparison_mode()

```python
def comparison_mode(self)
```

Launches model comparison (A/B testing) interface.

**Parameters:** None

**Returns:** None

**Features:**
- Select 2-4 models
- Run same prompt on all
- Side-by-side comparison
- Performance metrics
- Export results

**Example:**
```python
router.comparison_mode()
# Select models for comparison
# Enter prompt
# View results side-by-side
```

---

##### analytics_mode()

```python
def analytics_mode(self)
```

Displays analytics dashboard with usage statistics.

**Parameters:** None

**Returns:** None

**Metrics:**
- Total sessions and messages
- Model usage distribution
- Daily activity chart
- Average response time
- Recommendations

**Example:**
```python
router.analytics_mode()
# Displays comprehensive analytics dashboard
```

---

### ModelDatabase

**Description:** Static database of available models with platform-specific configurations.

**Location:** `ai-router.py`

#### Class Attributes

##### RTX3090_MODELS

Dictionary of models optimized for RTX 3090 (llama.cpp).

**Structure:**
```python
{
    "model_id": {
        "name": str,              # Human-readable name
        "path": str,              # Absolute path to model file
        "size": str,              # Model size (e.g., "18GB")
        "speed": str,             # Speed range (e.g., "25-35 tok/sec")
        "use_case": str,          # Primary use case
        "temperature": float,     # Default temperature
        "top_p": float,           # Default top_p
        "top_k": int,             # Default top_k
        "context": int,           # Context window size
        "special_flags": List,    # Additional flags (e.g., ["--jinja"])
        "system_prompt": str,     # System prompt file name or None
        "notes": str,             # Important usage notes
        "framework": str          # "llama.cpp"
    }
}
```

**Example:**
```python
from ai_router import ModelDatabase

models = ModelDatabase.RTX3090_MODELS
qwen_config = models['qwen3-coder-30b']
print(qwen_config['temperature'])  # 0.7
print(qwen_config['context'])      # 32768
```

---

##### M4_MODELS

Dictionary of models optimized for Apple M4 Pro (MLX).

**Structure:** Same as RTX3090_MODELS but with `"framework": "mlx"`

---

#### Class Methods

##### get_platform_models()

```python
@classmethod
def get_platform_models(cls) -> Dict
```

Returns models appropriate for current platform.

**Parameters:** None

**Returns:** Dictionary of models (RTX3090_MODELS or M4_MODELS)

**Example:**
```python
models = ModelDatabase.get_platform_models()
# Returns RTX3090_MODELS on Windows/Linux
# Returns M4_MODELS on macOS
```

---

##### detect_use_case()

```python
@classmethod
def detect_use_case(cls, prompt_text: str) -> str
```

Detects use case from prompt keywords.

**Parameters:**
- `prompt_text` (str): User's prompt

**Returns:** Use case string: "coding", "reasoning", "creative", "research", or "general"

**Example:**
```python
use_case = ModelDatabase.detect_use_case(
    "Write a Python function to parse JSON"
)
# Returns: "coding"

use_case = ModelDatabase.detect_use_case(
    "Solve this equation: 2x + 5 = 15"
)
# Returns: "reasoning"
```

---

##### recommend_model()

```python
@classmethod
def recommend_model(
    cls,
    use_case: str,
    platform_models: Dict
) -> tuple[str, Dict]
```

Recommends best model for a use case.

**Parameters:**
- `use_case` (str): Detected use case
- `platform_models` (Dict): Available models

**Returns:** Tuple of (model_id, model_data)

**Example:**
```python
models = ModelDatabase.get_platform_models()
model_id, model_data = ModelDatabase.recommend_model(
    "coding",
    models
)
# Returns: ('qwen3-coder-30b', {...})
```

---

### ModelResponse

**Description:** Data class capturing a complete model response with metadata.

**Location:** `ai-router.py`

#### Attributes

```python
@dataclass
class ModelResponse:
    text: str                          # Response text
    model_id: str                      # Model identifier
    model_name: str                    # Human-readable model name
    tokens_input: Optional[int]        # Input token count
    tokens_output: Optional[int]       # Output token count
    duration_seconds: Optional[float]  # Execution time
    timestamp: datetime                # Response timestamp
    metadata: Optional[Dict[str, Any]] # Additional metadata
```

**Example:**
```python
response = ModelResponse(
    text="def hello():\n    print('Hello, World!')",
    model_id="qwen3-coder-30b",
    model_name="Qwen3 Coder 30B Q4_K_M",
    tokens_input=50,
    tokens_output=25,
    duration_seconds=1.2
)

print(f"Generated {response.tokens_output} tokens in {response.duration_seconds}s")
```

---

### Colors

**Description:** Terminal color codes for formatted output.

**Location:** `ai-router.py`

#### Class Attributes

```python
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

    # Foreground colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'

    # Bright variants
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'

    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
```

**Example:**
```python
from ai_router import Colors

print(f"{Colors.BRIGHT_GREEN}Success!{Colors.RESET}")
print(f"{Colors.BOLD}{Colors.CYAN}Title{Colors.RESET}")
print(f"{Colors.BG_RED}{Colors.WHITE}Error{Colors.RESET}")
```

---

## Session Management

### SessionManager

**Description:** SQLite-based conversation history management with full-text search.

**Location:** `session_manager.py`

#### Constructor

```python
def __init__(self, db_path: Path)
```

Initializes session manager with database.

**Parameters:**
- `db_path` (Path): Path to SQLite database file (created if doesn't exist)

**Raises:**
- `FileNotFoundError`: If schema.sql not found when creating new database
- `RuntimeError`: If existing database is corrupted

**Example:**
```python
from pathlib import Path
from session_manager import SessionManager

db_path = Path('/mnt/d/models/.ai-router-sessions.db')
session_mgr = SessionManager(db_path)
```

---

#### Methods

##### create_session()

```python
def create_session(
    self,
    model_id: str,
    model_name: Optional[str] = None,
    title: Optional[str] = None
) -> str
```

Creates a new conversation session.

**Parameters:**
- `model_id` (str): Model identifier (e.g., 'qwen3-coder-30b')
- `model_name` (str, optional): Human-readable model name
- `title` (str, optional): Session title (auto-generated from first message if None)

**Returns:** session_id (str) - Unique UUID identifier

**Example:**
```python
session_id = session_mgr.create_session(
    model_id='qwen3-coder-30b',
    model_name='Qwen3 Coder 30B',
    title='Python coding session'
)
print(f"Created session: {session_id}")
```

---

##### add_message()

```python
def add_message(
    self,
    session_id: str,
    role: str,
    content: str,
    tokens: Optional[int] = None,
    duration: Optional[float] = None,
    metadata: Optional[Dict[str, Any]] = None
)
```

Adds a message to a session.

**Parameters:**
- `session_id` (str): Session UUID
- `role` (str): Message role ('user', 'assistant', 'system')
- `content` (str): Message content
- `tokens` (int, optional): Token count
- `duration` (float, optional): Execution duration in seconds
- `metadata` (Dict, optional): Additional metadata (stored as JSON)

**Returns:** None

**Example:**
```python
# Add user message
session_mgr.add_message(
    session_id=session_id,
    role='user',
    content='Write a hello world function'
)

# Add assistant response with metrics
session_mgr.add_message(
    session_id=session_id,
    role='assistant',
    content='def hello():\n    print("Hello!")',
    tokens=150,
    duration=2.5,
    metadata={'temperature': 0.7}
)
```

---

##### get_session()

```python
def get_session(self, session_id: str) -> Optional[Dict[str, Any]]
```

Gets session metadata.

**Parameters:**
- `session_id` (str): Session UUID

**Returns:** Dictionary with session metadata or None if not found

**Returned Fields:**
- `session_id` (str)
- `created_at` (str): ISO timestamp
- `updated_at` (str): ISO timestamp
- `model_id` (str)
- `model_name` (str)
- `title` (str)
- `message_count` (int)
- `total_tokens` (int)
- `total_duration_seconds` (float)
- `last_activity` (str): ISO timestamp

**Example:**
```python
session = session_mgr.get_session(session_id)
if session:
    print(f"Title: {session['title']}")
    print(f"Messages: {session['message_count']}")
    print(f"Total tokens: {session['total_tokens']}")
```

---

##### get_session_history()

```python
def get_session_history(
    self,
    session_id: str
) -> List[Dict[str, Any]]
```

Gets all messages in a session, ordered by sequence.

**Parameters:**
- `session_id` (str): Session UUID

**Returns:** List of message dictionaries

**Message Fields:**
- `message_id` (int)
- `session_id` (str)
- `sequence_number` (int)
- `role` (str)
- `content` (str)
- `timestamp` (str)
- `tokens_used` (int)
- `duration_seconds` (float)
- `metadata` (Dict): Parsed from JSON

**Example:**
```python
messages = session_mgr.get_session_history(session_id)
for msg in messages:
    print(f"[{msg['role']}] {msg['content'][:50]}...")
    if msg['tokens_used']:
        print(f"  Tokens: {msg['tokens_used']}")
```

---

##### list_sessions()

```python
def list_sessions(
    self,
    limit: int = 50,
    model_filter: Optional[str] = None,
    offset: int = 0
) -> List[Dict[str, Any]]
```

Lists recent sessions.

**Parameters:**
- `limit` (int): Maximum number of sessions to return (default 50)
- `model_filter` (str, optional): Filter by model_id
- `offset` (int): Number of sessions to skip (for pagination)

**Returns:** List of session dictionaries (from recent_sessions view)

**Example:**
```python
# Get 10 most recent sessions
recent = session_mgr.list_sessions(limit=10)
for session in recent:
    print(f"{session['title']} - {session['message_count']} messages")

# Get sessions for specific model
qwen_sessions = session_mgr.list_sessions(
    model_filter='qwen3-coder-30b'
)
```

---

##### search_sessions()

```python
def search_sessions(
    self,
    query: str,
    limit: int = 20
) -> List[Dict[str, Any]]
```

Searches sessions by content using full-text search (FTS5).

**Parameters:**
- `query` (str): Search query (supports FTS5 syntax)
- `limit` (int): Maximum results (default 20)

**Returns:** List of matching session dictionaries

**FTS5 Query Examples:**
- `"python"` - Contains "python"
- `"python AND function"` - Contains both
- `"python OR javascript"` - Contains either
- `"code*"` - Prefix match (code, coding, coder, etc.)

**Example:**
```python
# Search for Python-related sessions
results = session_mgr.search_sessions('python function')
for session in results:
    print(f"{session['title']}")

# Search with wildcards
results = session_mgr.search_sessions('code*')
```

---

##### delete_session()

```python
def delete_session(self, session_id: str) -> bool
```

Deletes a session and all its messages (cascade delete).

**Parameters:**
- `session_id` (str): Session UUID to delete

**Returns:** True if deleted, False if not found

**Example:**
```python
if session_mgr.delete_session(old_session_id):
    print("Session deleted")
else:
    print("Session not found")
```

---

##### update_session_title()

```python
def update_session_title(self, session_id: str, title: str)
```

Updates session title.

**Parameters:**
- `session_id` (str): Session UUID
- `title` (str): New title

**Returns:** None

**Example:**
```python
session_mgr.update_session_title(
    session_id,
    "Python function implementation session"
)
```

---

##### set_session_metadata()

```python
def set_session_metadata(
    self,
    session_id: str,
    key: str,
    value: str
)
```

Sets a session metadata key-value pair (upsert).

**Parameters:**
- `session_id` (str): Session UUID
- `key` (str): Metadata key
- `value` (str): Metadata value

**Returns:** None

**Example:**
```python
session_mgr.set_session_metadata(
    session_id,
    'project_name',
    'web_scraper'
)
```

---

##### get_session_metadata()

```python
def get_session_metadata(
    self,
    session_id: str,
    key: str
) -> Optional[str]
```

Gets a session metadata value.

**Parameters:**
- `session_id` (str): Session UUID
- `key` (str): Metadata key

**Returns:** Metadata value or None if not found

**Example:**
```python
project = session_mgr.get_session_metadata(
    session_id,
    'project_name'
)
if project:
    print(f"Project: {project}")
```

---

##### export_session()

```python
def export_session(
    self,
    session_id: str,
    format: str = 'json'
) -> str
```

Exports session to JSON or Markdown format.

**Parameters:**
- `session_id` (str): Session UUID
- `format` (str): 'json' or 'markdown' (default 'json')

**Returns:** Formatted string

**Raises:**
- `ValueError`: If session not found or invalid format

**JSON Output:**
```json
{
  "session": {
    "session_id": "...",
    "title": "...",
    "model_id": "...",
    ...
  },
  "messages": [
    {
      "role": "user",
      "content": "...",
      ...
    },
    ...
  ]
}
```

**Example:**
```python
# Export as JSON
json_export = session_mgr.export_session(session_id, 'json')
with open('session_export.json', 'w') as f:
    f.write(json_export)

# Export as Markdown
md_export = session_mgr.export_session(session_id, 'markdown')
with open('session_export.md', 'w') as f:
    f.write(md_export)
```

---

##### get_statistics()

```python
def get_statistics(self) -> Dict[str, Any]
```

Gets database statistics.

**Parameters:** None

**Returns:** Dictionary with statistics

**Returned Fields:**
- `total_sessions` (int): Total number of sessions
- `total_messages` (int): Total number of messages
- `total_tokens` (int): Total tokens across all sessions
- `model_breakdown` (Dict[str, int]): Session count by model_id
- `last_session` (str): Timestamp of most recent session

**Example:**
```python
stats = session_mgr.get_statistics()
print(f"Total sessions: {stats['total_sessions']}")
print(f"Total tokens: {stats['total_tokens']:,}")
print("\nModel breakdown:")
for model, count in stats['model_breakdown'].items():
    print(f"  {model}: {count} sessions")
```

---

##### cleanup_old_sessions()

```python
def cleanup_old_sessions(self, days: int = 30) -> int
```

Deletes sessions older than specified days.

**Parameters:**
- `days` (int): Age threshold in days (default 30)

**Returns:** Number of sessions deleted

**Example:**
```python
# Delete sessions older than 90 days
deleted = session_mgr.cleanup_old_sessions(days=90)
print(f"Deleted {deleted} old sessions")
```

---

##### Convenience Function

```python
def create_session_manager(models_dir: Path) -> SessionManager
```

Creates SessionManager instance with standard database path.

**Parameters:**
- `models_dir` (Path): Base models directory

**Returns:** SessionManager instance

**Example:**
```python
from pathlib import Path
from session_manager import create_session_manager

models_dir = Path('/mnt/d/models')
session_mgr = create_session_manager(models_dir)
# Database at: /mnt/d/models/.ai-router-sessions.db
```

---

## Template System

### TemplateManager

**Description:** Manages YAML + Jinja2 prompt templates with variable substitution.

**Location:** `template_manager.py`

#### Constructor

```python
def __init__(self, templates_dir: Path)
```

Initializes template manager.

**Parameters:**
- `templates_dir` (Path): Directory containing template YAML files (created if doesn't exist)

**Example:**
```python
from pathlib import Path
from template_manager import TemplateManager

templates_dir = Path('/mnt/d/models/prompt-templates')
template_mgr = TemplateManager(templates_dir)
```

---

#### Methods

##### list_templates()

```python
def list_templates(
    self,
    category: Optional[str] = None
) -> List[Dict]
```

Lists available templates, optionally filtered by category.

**Parameters:**
- `category` (str, optional): Category filter (e.g., 'coding', 'creative')

**Returns:** List of template info dictionaries

**Template Info Fields:**
- `name` (str): Template name
- `id` (str): Template identifier
- `category` (str): Template category
- `description` (str): Description
- `recommended_models` (List[str]): Recommended model IDs
- `variables` (List[Dict]): Variable definitions

**Example:**
```python
# List all templates
all_templates = template_mgr.list_templates()
for tmpl in all_templates:
    print(f"{tmpl['name']} - {tmpl['description']}")

# List only coding templates
coding = template_mgr.list_templates(category='coding')
```

---

##### get_template()

```python
def get_template(
    self,
    template_id: str
) -> Optional[PromptTemplate]
```

Loads a specific template by ID.

**Parameters:**
- `template_id` (str): Template identifier

**Returns:** PromptTemplate object or None if not found

**Example:**
```python
template = template_mgr.get_template('code-review')
if template:
    info = template.get_template_info()
    print(f"Template: {info['name']}")
```

---

##### get_categories()

```python
def get_categories(self) -> List[str]
```

Gets list of all available template categories.

**Parameters:** None

**Returns:** Sorted list of unique categories

**Example:**
```python
categories = template_mgr.get_categories()
print(f"Available categories: {', '.join(categories)}")
# Output: "coding, creative, general, research"
```

---

##### create_template_interactive()

```python
def create_template_interactive(self) -> Optional[Path]
```

Interactive template creation wizard.

**Parameters:** None

**Returns:** Path to created template file or None if cancelled

**Process:**
1. Prompts for template metadata (name, ID, category, description)
2. Prompts for variable definitions
3. Prompts for system prompt
4. Prompts for user prompt template
5. Saves to YAML file
6. Reloads templates

**Example:**
```python
template_path = template_mgr.create_template_interactive()
if template_path:
    print(f"Template created: {template_path}")
```

---

### PromptTemplate

**Description:** Represents a single prompt template with rendering capability.

**Location:** `template_manager.py`

#### Constructor

```python
def __init__(self, template_path: Path)
```

Initializes prompt template from YAML file.

**Parameters:**
- `template_path` (Path): Path to template YAML file

**Raises:**
- `ValueError`: If template file is invalid

**Template YAML Structure:**
```yaml
metadata:
  name: "Code Review"
  id: "code-review"
  category: "coding"
  description: "Reviews code for bugs and improvements"
  recommended_models:
    - qwen3-coder-30b
    - qwen25-coder-32b
  variables:
    - name: "code"
      description: "Code to review"
      required: true
    - name: "language"
      description: "Programming language"
      required: false
      default: "Python"

system_prompt: |
  You are an expert code reviewer.

user_prompt: |
  Review this {{language}} code:

  ```
  {{code}}
  ```

  Provide feedback on bugs, improvements, and best practices.
```

**Example:**
```python
from pathlib import Path
from template_manager import PromptTemplate

template_path = Path('/mnt/d/models/prompt-templates/code-review.yaml')
template = PromptTemplate(template_path)
```

---

#### Methods

##### render()

```python
def render(self, variables: Dict[str, Any]) -> Dict[str, str]
```

Renders template with provided variables.

**Parameters:**
- `variables` (Dict[str, Any]): Variable name to value mappings

**Returns:** Dictionary with 'system_prompt' and 'user_prompt' keys

**Notes:**
- Missing variables are filled with defaults if defined
- Jinja2 syntax supported ({{variable}}, {% if %}, etc.)

**Example:**
```python
rendered = template.render({
    'code': 'def add(a, b):\n    return a + b',
    'language': 'Python'
})

print(rendered['system_prompt'])
# Output: "You are an expert code reviewer."

print(rendered['user_prompt'])
# Output: "Review this Python code:\n\n```\ndef add(a, b):\n    return a + b\n```\n..."
```

---

##### get_required_variables()

```python
def get_required_variables(self) -> List[Dict[str, Any]]
```

Gets list of required variables with descriptions.

**Parameters:** None

**Returns:** List of variable definition dictionaries

**Variable Definition:**
```python
{
    'name': 'code',
    'description': 'Code to review',
    'required': True,
    'default': None  # or default value
}
```

**Example:**
```python
vars = template.get_required_variables()
for var in vars:
    if var['required']:
        print(f"Required: {var['name']} - {var['description']}")
```

---

##### get_template_info()

```python
def get_template_info(self) -> Dict[str, Any]
```

Gets template metadata information.

**Parameters:** None

**Returns:** Dictionary with template info

**Example:**
```python
info = template.get_template_info()
print(f"Name: {info['name']}")
print(f"Category: {info['category']}")
print(f"Description: {info['description']}")
print(f"Recommended models: {info['recommended_models']}")
```

---

## Context Management

### ContextManager

**Description:** Manages file and text context injection with token estimation.

**Location:** `context_manager.py`

#### Constructor

```python
def __init__(self)
```

Initializes context manager with default settings.

**Parameters:** None

**Attributes:**
- `context_items` (List[Dict]): List of loaded context items
- `max_tokens` (int): Maximum token limit (default 4096)
- `token_estimation_ratio` (float): Words to tokens ratio (default 1.3)

**Example:**
```python
from context_manager import ContextManager

ctx_mgr = ContextManager()
ctx_mgr.set_max_tokens(8192)  # Increase limit for larger models
```

---

#### Methods

##### add_file()

```python
def add_file(
    self,
    file_path: Path,
    label: Optional[str] = None
) -> Dict
```

Adds file contents as context.

**Parameters:**
- `file_path` (Path): Path to file to load
- `label` (str, optional): Custom label (defaults to filename)

**Returns:** Context item dictionary

**Raises:**
- `FileNotFoundError`: If file doesn't exist
- `ValueError`: If path is outside allowed directory (security check)
- `RuntimeError`: If file cannot be read

**Security:** CVE-2025-AIR-002 fix - validates paths to prevent directory traversal

**Example:**
```python
from pathlib import Path

# Add Python file
ctx_item = ctx_mgr.add_file(
    Path('/mnt/d/projects/app.py'),
    label='Main Application'
)

print(f"Added: {ctx_item['label']}")
print(f"Tokens: {ctx_item['tokens']}")
print(f"Language: {ctx_item['language']}")
```

---

##### add_text()

```python
def add_text(self, text: str, label: str) -> Dict
```

Adds arbitrary text as context.

**Parameters:**
- `text` (str): Text content to add
- `label` (str): Label for this context

**Returns:** Context item dictionary

**Raises:**
- `ValueError`: If text or label is empty

**Example:**
```python
ctx_item = ctx_mgr.add_text(
    text="API Endpoint: POST /api/users",
    label="API Documentation"
)
```

---

##### estimate_tokens()

```python
def estimate_tokens(self, text: str) -> int
```

Estimates token count using words * 1.3 heuristic.

**Parameters:**
- `text` (str): Text to estimate

**Returns:** Estimated token count (int)

**Example:**
```python
text = "The quick brown fox jumps over the lazy dog."
tokens = ctx_mgr.estimate_tokens(text)
print(f"Estimated tokens: {tokens}")
# Output: ~12 tokens (9 words * 1.3)
```

---

##### build_context_prompt()

```python
def build_context_prompt(
    self,
    user_prompt: str,
    truncate: bool = True
) -> str
```

Builds final prompt with context injection.

**Parameters:**
- `user_prompt` (str): User's actual query
- `truncate` (bool): Whether to truncate if exceeding max_tokens (default True)

**Returns:** Complete prompt with context

**Raises:**
- `ValueError`: If prompt exceeds max_tokens and truncate=False

**Format:**
```
## Context Item 1 Label
```language
content
```

## Context Item 2 Label
content

================================================================================

USER REQUEST:
actual user prompt
```

**Example:**
```python
ctx_mgr.add_file(Path('app.py'))
ctx_mgr.add_text("Use Python 3.10 features", "Requirements")

full_prompt = ctx_mgr.build_context_prompt(
    "Refactor this code for better performance"
)

# full_prompt now contains:
# - app.py contents
# - Requirements text
# - Separator
# - User prompt
```

---

##### clear_context()

```python
def clear_context(self)
```

Clears all context items.

**Parameters:** None

**Returns:** None

**Example:**
```python
ctx_mgr.clear_context()
print(ctx_mgr.get_context_summary())
# Output: "No context loaded"
```

---

##### get_context_summary()

```python
def get_context_summary(self) -> str
```

Gets human-readable summary of current context.

**Parameters:** None

**Returns:** Summary string

**Example:**
```python
print(ctx_mgr.get_context_summary())
# Output:
# Context Summary:
#   Items: 2
#   Total tokens: 1,245
#   Max tokens: 4,096
#   Utilization: 30.4%
#
# Context Items:
#   [1] app.py (file, 980 tokens)
#   [2] Requirements (text, 265 tokens)
```

---

##### remove_context_item()

```python
def remove_context_item(self, index: int) -> bool
```

Removes a context item by index.

**Parameters:**
- `index` (int): 0-based index of item to remove

**Returns:** True if removed, False if index invalid

**Example:**
```python
# Remove first item
if ctx_mgr.remove_context_item(0):
    print("Item removed")
```

---

##### set_max_tokens()

```python
def set_max_tokens(self, max_tokens: int)
```

Sets maximum token limit.

**Parameters:**
- `max_tokens` (int): New maximum (must be positive)

**Raises:**
- `ValueError`: If max_tokens <= 0

**Example:**
```python
# Increase limit for model with 32K context
ctx_mgr.set_max_tokens(32768)
```

---

##### get_total_tokens()

```python
def get_total_tokens(self) -> int
```

Gets total tokens across all context items.

**Parameters:** None

**Returns:** Total token count

**Example:**
```python
total = ctx_mgr.get_total_tokens()
print(f"Context uses {total} tokens")
```

---

#### Class Attribute: LANGUAGE_MAP

Dictionary mapping file extensions to language identifiers.

**Supported Extensions:**
```python
{
    '.py': 'python',
    '.js': 'javascript',
    '.ts': 'typescript',
    '.java': 'java',
    '.cpp': 'cpp',
    '.c': 'c',
    '.rs': 'rust',
    '.go': 'go',
    '.php': 'php',
    '.rb': 'ruby',
    '.swift': 'swift',
    '.sql': 'sql',
    '.sh': 'bash',
    '.md': 'markdown',
    '.json': 'json',
    '.yaml': 'yaml',
    '.html': 'html',
    '.css': 'css',
    # ... and many more
}
```

---

## Response Processing

### ResponseProcessor

**Description:** Post-processing and formatting utilities for model responses.

**Location:** `response_processor.py`

#### Constructor

```python
def __init__(self, output_dir: Path)
```

Initializes processor with output directory.

**Parameters:**
- `output_dir` (Path): Directory to save outputs (created if doesn't exist)

**Example:**
```python
from pathlib import Path
from response_processor import ResponseProcessor

output_dir = Path('/mnt/d/models/outputs')
processor = ResponseProcessor(output_dir)
```

---

#### Methods

##### save_response()

```python
def save_response(
    self,
    response: str,
    filename: Optional[str] = None,
    model_name: str = "",
    metadata: Optional[Dict] = None
) -> Path
```

Saves response to file with metadata header.

**Parameters:**
- `response` (str): Response text to save
- `filename` (str, optional): Custom filename (auto-generated if None)
- `model_name` (str): Name of model that generated response
- `metadata` (Dict, optional): Additional metadata to include

**Returns:** Path to saved file

**Auto-generated Filename Format:** `response_YYYYMMDD_HHMMSS.txt`

**File Format:**
```
================================================================================
AI ROUTER - MODEL RESPONSE
================================================================================
Generated: 2025-12-09 14:23:45
Model: Qwen3 Coder 30B
[metadata fields]
================================================================================

[response text]
```

**Example:**
```python
filepath = processor.save_response(
    response="def hello():\n    print('Hello!')",
    filename="hello_function.txt",
    model_name="Qwen3 Coder 30B",
    metadata={
        'tokens': 150,
        'duration': 2.5
    }
)
print(f"Saved to: {filepath}")
```

---

##### extract_code_blocks()

```python
def extract_code_blocks(self, text: str) -> List[Dict[str, str]]
```

Extracts code blocks with language tags from markdown.

**Parameters:**
- `text` (str): Text containing markdown code blocks

**Returns:** List of dictionaries with 'language' and 'code' keys

**Example:**
```python
text = """
Here's a Python function:

```python
def add(a, b):
    return a + b
```

And a JavaScript version:

```javascript
function add(a, b) {
    return a + b;
}
```
"""

blocks = processor.extract_code_blocks(text)
# Returns:
# [
#     {'language': 'python', 'code': 'def add(a, b):\n    return a + b'},
#     {'language': 'javascript', 'code': 'function add(a, b) {\n    return a + b;\n}'}
# ]
```

---

##### save_code_blocks()

```python
def save_code_blocks(
    self,
    text: str,
    base_name: str
) -> List[Path]
```

Extracts and saves code blocks to separate files.

**Parameters:**
- `text` (str): Text containing code blocks
- `base_name` (str): Base name for saved files

**Returns:** List of paths to saved code files

**Filename Format:** `{base_name}_code_{index}{extension}`

**Example:**
```python
saved_files = processor.save_code_blocks(
    text=response_with_code,
    base_name="solution"
)
# Saves:
# - solution_code_0.py
# - solution_code_1.js

for file in saved_files:
    print(f"Saved code: {file}")
```

---

##### format_as_markdown()

```python
def format_as_markdown(
    self,
    response: str,
    model_name: str = "",
    metadata: Optional[Dict] = None
) -> str
```

Formats response with metadata as markdown.

**Parameters:**
- `response` (str): Response text
- `model_name` (str): Model name
- `metadata` (Dict, optional): Additional metadata

**Returns:** Formatted markdown string

**Example:**
```python
md = processor.format_as_markdown(
    response="The answer is 42.",
    model_name="Phi-4 14B",
    metadata={'tokens': 100, 'duration': 1.5}
)

print(md)
# Output:
# # AI Router Response
#
# **Generated:** 2025-12-09 14:23:45
# **Model:** Phi-4 14B
#
# ## Metadata
#
# - **tokens:** 100
# - **duration:** 1.5
#
# ---
#
# ## Response
#
# The answer is 42.
```

---

##### get_statistics()

```python
def get_statistics(self, text: str) -> Dict
```

Calculates response statistics.

**Parameters:**
- `text` (str): Text to analyze

**Returns:** Dictionary with statistics

**Statistics:**
- `char_count` (int): Total characters
- `word_count` (int): Total words
- `line_count` (int): Total lines
- `code_blocks` (int): Number of code blocks
- `avg_line_length` (float): Average line length

**Example:**
```python
stats = processor.get_statistics(response_text)
print(f"Words: {stats['word_count']}")
print(f"Lines: {stats['line_count']}")
print(f"Code blocks: {stats['code_blocks']}")
```

---

##### copy_to_clipboard()

```python
def copy_to_clipboard(self, text: str) -> bool
```

Copies text to system clipboard (requires pyperclip).

**Parameters:**
- `text` (str): Text to copy

**Returns:** True if successful, False if pyperclip not available

**Example:**
```python
if processor.copy_to_clipboard(response_text):
    print("Copied to clipboard!")
else:
    print("Install pyperclip: pip install pyperclip")
```

---

##### list_saved_responses()

```python
def list_saved_responses(self, limit: int = 10) -> List[Path]
```

Lists recently saved response files.

**Parameters:**
- `limit` (int): Maximum number of files (default 10)

**Returns:** List of paths sorted by modification time (newest first)

**Example:**
```python
recent = processor.list_saved_responses(limit=5)
for i, path in enumerate(recent, 1):
    print(f"{i}. {path.name}")
```

---

## Model Selection

### ModelSelector

**Description:** Enhanced model selection with confidence scoring and preference learning.

**Location:** `model_selector.py`

#### Constructor

```python
def __init__(self, preferences_file: Path)
```

Initializes model selector with preferences.

**Parameters:**
- `preferences_file` (Path): JSON file to store learned preferences

**Example:**
```python
from pathlib import Path
from model_selector import ModelSelector

prefs_file = Path('/mnt/d/models/.ai-router-preferences.json')
selector = ModelSelector(prefs_file)
```

---

#### Methods

##### analyze_prompt()

```python
def analyze_prompt(self, prompt: str) -> Dict[str, float]
```

Analyzes prompt and returns confidence scores for each category.

**Parameters:**
- `prompt` (str): User's input prompt

**Returns:** Dictionary mapping categories to confidence scores (0.0-1.0)

**Categories:**
- `coding`: Code-related tasks
- `reasoning`: Math, logic, problem solving
- `creative`: Creative writing, brainstorming
- `research`: Information lookup, explanations
- `math`: Mathematical calculations

**Example:**
```python
scores = selector.analyze_prompt(
    "Write a Python function to calculate Fibonacci numbers"
)
# Returns: {'coding': 0.95, 'math': 0.45, 'reasoning': 0.30}

for category, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
    print(f"{category}: {score:.0%}")
```

---

##### select_model()

```python
def select_model(
    self,
    prompt: str,
    available_models: Dict
) -> Tuple[str, str, float]
```

Selects best model based on prompt analysis.

**Parameters:**
- `prompt` (str): User's input prompt
- `available_models` (Dict): Dictionary of available models

**Returns:** Tuple of (model_id, category, confidence)

**Example:**
```python
model_id, category, confidence = selector.select_model(
    "Explain quantum entanglement",
    router.models
)

print(f"Selected: {model_id}")
print(f"Category: {category}")
print(f"Confidence: {confidence:.0%}")
# Output:
# Selected: phi4-14b
# Category: reasoning
# Confidence: 88%
```

---

##### get_recommendations()

```python
def get_recommendations(
    self,
    prompt: str,
    available_models: Dict,
    top_n: int = 3
) -> List[Dict]
```

Gets top N model recommendations with confidence scores.

**Parameters:**
- `prompt` (str): User's input prompt
- `available_models` (Dict): Available models
- `top_n` (int): Number of recommendations (default 3)

**Returns:** List of recommendation dictionaries

**Recommendation Dictionary:**
```python
{
    'model_id': 'qwen3-coder-30b',
    'category': 'coding',
    'confidence': 0.92
}
```

**Example:**
```python
recommendations = selector.get_recommendations(
    "Debug this Python code",
    router.models,
    top_n=3
)

for i, rec in enumerate(recommendations, 1):
    print(f"{i}. {rec['model_id']} ({rec['category']}: {rec['confidence']:.0%})")
# Output:
# 1. qwen3-coder-30b (coding: 92%)
# 2. qwen25-coder-32b (coding: 90%)
# 3. phi4-14b (reasoning: 45%)
```

---

##### learn_preference()

```python
def learn_preference(self, category: str, model_id: str)
```

Learns user preference for a category.

**Parameters:**
- `category` (str): Use case category
- `model_id` (str): Preferred model ID

**Returns:** None

**Side Effects:** Saves preferences to JSON file

**Example:**
```python
# User prefers Qwen3 Coder for coding tasks
selector.learn_preference('coding', 'qwen3-coder-30b')

# Future coding prompts will prefer this model
```

---

##### get_explanation()

```python
def get_explanation(
    self,
    category: str,
    confidence: float,
    prompt: str
) -> str
```

Generates human-readable explanation for model selection.

**Parameters:**
- `category` (str): Selected category
- `confidence` (float): Confidence score
- `prompt` (str): Original prompt

**Returns:** Explanation string

**Example:**
```python
explanation = selector.get_explanation(
    'coding',
    0.85,
    'Write a sorting algorithm'
)
print(explanation)
# Output: "Selected coding model with high confidence (85%) - detected code-related keywords like 'function', 'debug', 'implement'"
```

---

#### Pattern Configuration

The ModelSelector uses weighted keyword patterns for detection:

```python
patterns = {
    "coding": {
        "high": ["write code", "implement", "debug", ...],     # +0.5
        "medium": ["code", "function", "algorithm", ...],      # +0.3
        "low": ["software", "develop", "script", ...]          # +0.1
    },
    "reasoning": {
        "high": ["solve", "analyze deeply", "prove", ...],
        "medium": ["think", "reason", "explain why", ...],
        "low": ["understand", "clarify", "why"]
    },
    # ... other categories
}
```

**Category Model Mapping:**
```python
category_model_map = {
    "coding": ["qwen3-coder-30b", "qwen25-coder-32b", ...],
    "reasoning": ["phi4-14b", "ministral-3-14b", ...],
    "creative": ["gemma3-27b", "dolphin-mistral-24b", ...],
    "research": ["llama33-70b", "ministral-3-14b", ...],
    "math": ["phi4-14b", "ministral-3-14b", ...],
    "general": ["dolphin-llama31-8b", "qwen25-14b-mlx", ...]
}
```

---

## Batch Processing

### BatchProcessor

**Description:** Processes multiple prompts with progress tracking and checkpointing.

**Location:** `batch_processor.py`

#### Constructor

```python
def __init__(self, checkpoint_dir: Path)
```

Initializes batch processor.

**Parameters:**
- `checkpoint_dir` (Path): Directory to store checkpoint files (created if doesn't exist)

**Example:**
```python
from pathlib import Path
from batch_processor import BatchProcessor

checkpoint_dir = Path('/mnt/d/models/batch_checkpoints')
batch_proc = BatchProcessor(checkpoint_dir)
```

---

#### Methods

##### load_prompts_from_file()

```python
def load_prompts_from_file(self, file_path: Path) -> List[str]
```

Loads prompts from text or JSON file.

**Parameters:**
- `file_path` (Path): Path to prompts file

**Returns:** List of prompt strings

**Raises:**
- `FileNotFoundError`: If file doesn't exist

**Supported Formats:**

**Text File (one prompt per line):**
```
Write a hello world function
Calculate 2 + 2
Explain quantum physics
# Comments are ignored
```

**JSON File:**
```json
{
  "prompts": [
    "Write a hello world function",
    "Calculate 2 + 2",
    "Explain quantum physics"
  ]
}
```

or

```json
[
  "Write a hello world function",
  "Calculate 2 + 2",
  "Explain quantum physics"
]
```

**Example:**
```python
prompts = batch_proc.load_prompts_from_file(
    Path('/mnt/d/projects/prompts.txt')
)
print(f"Loaded {len(prompts)} prompts")
```

---

##### create_job()

```python
def create_job(
    self,
    model_id: str,
    prompts: List[str]
) -> BatchJob
```

Creates a new batch job.

**Parameters:**
- `model_id` (str): Model to use for processing
- `prompts` (List[str]): List of prompts to process

**Returns:** BatchJob instance

**Example:**
```python
prompts = [
    "Write a Python hello world",
    "Write a JavaScript hello world",
    "Write a Rust hello world"
]

job = batch_proc.create_job(
    model_id='qwen3-coder-30b',
    prompts=prompts
)

print(f"Job ID: {job.job_id}")
print(f"Total prompts: {job.total_prompts}")
```

---

##### process_batch()

```python
def process_batch(
    self,
    job: BatchJob,
    execute_fn: Callable,
    progress_callback: Optional[Callable] = None,
    error_strategy: str = "continue"
) -> List[BatchResult]
```

Processes batch job with progress tracking.

**Parameters:**
- `job` (BatchJob): Batch job to process
- `execute_fn` (Callable): Function that takes (prompt) and returns ModelResponse
- `progress_callback` (Callable, optional): Callback for progress updates
- `error_strategy` (str): Error handling strategy
  - `"stop"`: Stop on first error
  - `"continue"`: Continue despite errors
  - `"threshold:N"`: Stop after N errors

**Returns:** List of BatchResult objects

**Example:**
```python
def execute_model(prompt):
    return router.run_model(
        'qwen3-coder-30b',
        router.models['qwen3-coder-30b'],
        prompt
    )

def progress(job, current):
    print(f"Progress: {current}/{job.total_prompts}")

results = batch_proc.process_batch(
    job=job,
    execute_fn=execute_model,
    progress_callback=progress,
    error_strategy="continue"
)

print(f"Completed: {job.completed}")
print(f"Failed: {job.failed}")
```

---

##### save_checkpoint()

```python
def save_checkpoint(
    self,
    job: BatchJob,
    results: List[BatchResult]
)
```

Saves progress checkpoint.

**Parameters:**
- `job` (BatchJob): Current batch job
- `results` (List[BatchResult]): Results so far

**Returns:** None

**Notes:**
- Automatically saves every 5 prompts during processing
- Checkpoint file: `batch_{job_id}.json`

**Example:**
```python
# Manual checkpoint save
batch_proc.save_checkpoint(job, results)
```

---

##### load_checkpoint()

```python
def load_checkpoint(
    self,
    checkpoint_file: Path
) -> tuple[BatchJob, List[BatchResult]]
```

Loads saved checkpoint to resume processing.

**Parameters:**
- `checkpoint_file` (Path): Path to checkpoint file

**Returns:** Tuple of (BatchJob, List[BatchResult])

**Raises:**
- `FileNotFoundError`: If checkpoint doesn't exist

**Example:**
```python
checkpoint_file = Path('/mnt/d/models/batch_checkpoints/batch_a1b2c3d4.json')
job, results = batch_proc.load_checkpoint(checkpoint_file)

print(f"Resuming job: {job.job_id}")
print(f"Already completed: {len(results)} prompts")

# Continue processing from where it left off
```

---

##### list_checkpoints()

```python
def list_checkpoints(self) -> List[Dict[str, Any]]
```

Lists all available checkpoints.

**Parameters:** None

**Returns:** List of checkpoint info dictionaries (sorted by timestamp, newest first)

**Checkpoint Info:**
```python
{
    'file': Path,          # Path to checkpoint file
    'job_id': str,         # Job ID
    'model_id': str,       # Model used
    'status': str,         # Job status
    'completed': int,      # Prompts completed
    'total': int,          # Total prompts
    'failed': int,         # Failed prompts
    'timestamp': str       # ISO timestamp
}
```

**Example:**
```python
checkpoints = batch_proc.list_checkpoints()
for cp in checkpoints:
    print(f"Job {cp['job_id']}: {cp['completed']}/{cp['total']} ({cp['status']})")
```

---

##### export_results()

```python
def export_results(
    self,
    job: BatchJob,
    results: List[BatchResult],
    output_file: Path,
    format: str = 'json'
)
```

Exports batch results to JSON or CSV.

**Parameters:**
- `job` (BatchJob): Batch job
- `results` (List[BatchResult]): Results to export
- `output_file` (Path): Output file path
- `format` (str): 'json' or 'csv' (default 'json')

**Returns:** None

**JSON Format:**
```json
{
  "job": {
    "job_id": "a1b2c3d4",
    "model_id": "qwen3-coder-30b",
    "total_prompts": 10,
    "completed": 10,
    "failed": 0,
    "status": "completed"
  },
  "results": [
    {
      "prompt_index": 0,
      "prompt": "Write hello world",
      "response_text": "def hello()...",
      "tokens_input": 50,
      "tokens_output": 25,
      "duration": 1.5,
      "success": true
    }
  ],
  "summary": {
    "total": 10,
    "completed": 10,
    "failed": 0,
    "success_rate": 100.0
  }
}
```

**Example:**
```python
# Export as JSON
batch_proc.export_results(
    job, results,
    Path('/mnt/d/models/outputs/batch_results.json'),
    format='json'
)

# Export as CSV
batch_proc.export_results(
    job, results,
    Path('/mnt/d/models/outputs/batch_results.csv'),
    format='csv'
)
```

---

### BatchJob

**Description:** Data class representing a batch processing job.

**Location:** `batch_processor.py`

#### Attributes

```python
@dataclass
class BatchJob:
    job_id: str                        # Unique job ID (8-char UUID)
    model_id: str                      # Model to use
    prompts: List[str]                 # List of prompts
    total_prompts: int                 # Total prompt count
    completed: int = 0                 # Completed count
    failed: int = 0                    # Failed count
    status: str = "pending"            # Status: pending/running/paused/completed/failed
    started_at: Optional[datetime]     # Start timestamp
    completed_at: Optional[datetime]   # Completion timestamp
    checkpoint_file: Optional[Path]    # Checkpoint file path
```

**Example:**
```python
job = BatchJob(
    job_id='abc12345',
    model_id='qwen3-coder-30b',
    prompts=['prompt1', 'prompt2', 'prompt3'],
    total_prompts=3
)
```

---

### BatchResult

**Description:** Data class representing an individual batch result.

**Location:** `batch_processor.py`

#### Attributes

```python
@dataclass
class BatchResult:
    prompt_index: int                  # Index in batch (0-based)
    prompt: str                        # Original prompt
    response_text: str                 # Model response
    tokens_input: int                  # Input tokens
    tokens_output: int                 # Output tokens
    duration: float                    # Duration in seconds
    success: bool                      # Success flag
    error_message: Optional[str]       # Error message if failed
```

**Example:**
```python
result = BatchResult(
    prompt_index=0,
    prompt='Write hello world',
    response_text='def hello():\n    print("Hello!")',
    tokens_input=50,
    tokens_output=25,
    duration=1.5,
    success=True
)

if result.success:
    print(f"Response: {result.response_text}")
else:
    print(f"Error: {result.error_message}")
```

---

## Analytics

### AnalyticsDashboard

**Description:** Performance analytics and usage statistics.

**Location:** `analytics_dashboard.py`

#### Constructor

```python
def __init__(self, session_manager: SessionManager)
```

Initializes analytics dashboard.

**Parameters:**
- `session_manager` (SessionManager): Session manager instance for database access

**Example:**
```python
from analytics_dashboard import AnalyticsDashboard
from session_manager import SessionManager
from pathlib import Path

db_path = Path('/mnt/d/models/.ai-router-sessions.db')
session_mgr = SessionManager(db_path)
analytics = AnalyticsDashboard(session_mgr)
```

---

#### Methods

##### get_usage_statistics()

```python
def get_usage_statistics(self, days: int = 30) -> Dict
```

Gets usage stats for last N days.

**Parameters:**
- `days` (int): Number of days to analyze (default 30)

**Returns:** Dictionary with statistics

**Statistics:**
```python
{
    'total_sessions': int,          # Total sessions
    'total_messages': int,          # Total messages
    'user_messages': int,           # User messages only
    'assistant_messages': int,      # Assistant messages only
    'total_tokens': int,            # Total tokens used
    'avg_tokens': float             # Average tokens per message
}
```

**Example:**
```python
stats = analytics.get_usage_statistics(days=7)
print(f"Last 7 days:")
print(f"  Sessions: {stats['total_sessions']}")
print(f"  Messages: {stats['total_messages']}")
print(f"  Tokens: {stats['total_tokens']:,}")
```

---

##### get_model_usage()

```python
def get_model_usage(self, days: int = 30) -> List[Tuple[str, int]]
```

Gets usage count by model.

**Parameters:**
- `days` (int): Number of days (default 30)

**Returns:** List of (model_id, usage_count) tuples, sorted by count descending

**Example:**
```python
model_usage = analytics.get_model_usage(days=30)
for model, count in model_usage:
    print(f"{model}: {count} sessions")
# Output:
# qwen3-coder-30b: 45 sessions
# phi4-14b: 28 sessions
# gemma3-27b: 12 sessions
```

---

##### get_daily_activity()

```python
def get_daily_activity(self, days: int = 30) -> List[Tuple[str, int]]
```

Gets daily message counts for last N days.

**Parameters:**
- `days` (int): Number of days (default 30)

**Returns:** List of (date, message_count) tuples, sorted by date

**Example:**
```python
daily = analytics.get_daily_activity(days=7)
for date, count in daily:
    print(f"{date}: {count} messages")
# Output:
# 2025-12-03: 15 messages
# 2025-12-04: 23 messages
# 2025-12-05: 18 messages
```

---

##### get_avg_response_time()

```python
def get_avg_response_time(self) -> float
```

Calculates average response time across all messages.

**Parameters:** None

**Returns:** Average duration in seconds (float)

**Example:**
```python
avg_time = analytics.get_avg_response_time()
print(f"Average response time: {avg_time:.2f} seconds")
```

---

##### get_top_models_by_performance()

```python
def get_top_models_by_performance(self) -> List[Dict]
```

Ranks models by usage and performance metrics.

**Parameters:** None

**Returns:** List of model performance dictionaries

**Performance Metrics:**
```python
{
    'model_id': str,
    'model_name': str,
    'session_count': int,
    'message_count': int,
    'avg_tokens': float,
    'total_tokens': int,
    'avg_duration': float
}
```

**Example:**
```python
top_models = analytics.get_top_models_by_performance()
for model in top_models[:5]:  # Top 5
    print(f"{model['model_name']}:")
    print(f"  Sessions: {model['session_count']}")
    print(f"  Avg tokens: {model['avg_tokens']:.0f}")
    print(f"  Avg duration: {model['avg_duration']:.2f}s")
```

---

##### display_dashboard()

```python
def display_dashboard(self, days: int = 30)
```

Displays complete analytics dashboard to console.

**Parameters:**
- `days` (int): Period in days (default 30)

**Returns:** None

**Dashboard Sections:**
1. Usage Statistics
2. Model Usage Chart (horizontal bars)
3. Daily Activity Chart (vertical ASCII chart)
4. Performance Metrics
5. AI-driven Recommendations

**Example:**
```python
analytics.display_dashboard(days=7)
# Outputs:
# ======================================================================
#   PERFORMANCE ANALYTICS DASHBOARD
#   Period: Last 7 days
#   Generated: 2025-12-09 14:23:45
# ======================================================================
#
# USAGE STATISTICS
# ----------------------------------------------------------------------
#   Total Sessions:               45
#   Total Messages:              180
#     |- User Messages:           90
#     +- AI Responses:            90
#   Total Tokens:            123,456
#   Avg Tokens/Message:        685.9
# ...
```

---

## Workflows

### WorkflowEngine

**Description:** Executes multi-step AI workflows with variable passing and conditional logic.

**Location:** `workflow_engine.py`

#### Constructor

```python
def __init__(self, workflows_dir: Path, ai_router: AIRouter)
```

Initializes workflow engine.

**Parameters:**
- `workflows_dir` (Path): Directory containing workflow YAML files (created if doesn't exist)
- `ai_router` (AIRouter): Reference to AIRouter for model execution

**Example:**
```python
from workflow_engine import WorkflowEngine
from ai_router import AIRouter
from pathlib import Path

router = AIRouter()
workflows_dir = Path('/mnt/d/models/workflows')
workflow_engine = WorkflowEngine(workflows_dir, router)
```

---

#### Methods

##### load_workflow()

```python
def load_workflow(self, workflow_path: Path) -> WorkflowExecution
```

Loads workflow from YAML file.

**Parameters:**
- `workflow_path` (Path): Path to workflow YAML file

**Returns:** WorkflowExecution instance ready for execution

**Raises:**
- `ValueError`: If YAML is invalid

**Example:**
```python
workflow_path = Path('/mnt/d/models/workflows/code-review.yaml')
execution = workflow_engine.load_workflow(workflow_path)
print(f"Loaded workflow: {execution.workflow_name}")
print(f"Steps: {len(execution.steps)}")
```

---

##### execute_workflow()

```python
def execute_workflow(
    self,
    execution: WorkflowExecution,
    progress_callback: Optional[Callable] = None
) -> Dict
```

Executes complete workflow with variable passing.

**Parameters:**
- `execution` (WorkflowExecution): Workflow execution instance
- `progress_callback` (Callable, optional): Callback for progress updates

**Returns:** Dictionary of results keyed by step name

**Raises:**
- Exception from failed steps (unless `on_error: continue` configured)

**Example:**
```python
def progress(execution, step):
    print(f"Executing step: {step.name}")

results = workflow_engine.execute_workflow(
    execution,
    progress_callback=progress
)

for step_name, result in results.items():
    print(f"\n{step_name}:")
    print(result)
```

---

##### list_workflows()

```python
def list_workflows(self) -> List[Dict]
```

Lists available workflows.

**Parameters:** None

**Returns:** List of workflow info dictionaries

**Workflow Info:**
```python
{
    'id': str,              # Workflow ID
    'name': str,            # Workflow name
    'description': str,     # Description
    'file': Path,           # Path to YAML file
    'num_steps': int        # Number of steps
}
```

**Example:**
```python
workflows = workflow_engine.list_workflows()
for wf in workflows:
    print(f"{wf['name']} ({wf['num_steps']} steps)")
    print(f"  {wf['description']}")
```

---

##### validate_workflow()

```python
def validate_workflow(
    self,
    workflow_path: Path
) -> tuple[bool, List[str]]
```

Validates workflow YAML structure.

**Parameters:**
- `workflow_path` (Path): Path to workflow file

**Returns:** Tuple of (is_valid, list_of_errors)

**Example:**
```python
workflow_path = Path('/mnt/d/models/workflows/my-workflow.yaml')
is_valid, errors = workflow_engine.validate_workflow(workflow_path)

if is_valid:
    print("Workflow is valid!")
else:
    print("Validation errors:")
    for error in errors:
        print(f"  - {error}")
```

---

##### save_workflow_results()

```python
def save_workflow_results(
    self,
    execution: WorkflowExecution,
    output_file: Path
)
```

Saves workflow execution results to JSON file.

**Parameters:**
- `execution` (WorkflowExecution): Completed execution
- `output_file` (Path): Output file path

**Returns:** None

**JSON Format:**
```json
{
  "workflow_id": "code-review-workflow",
  "workflow_name": "Code Review",
  "status": "completed",
  "results": {
    "step1": "...",
    "step2": "..."
  },
  "variables": {
    "code": "...",
    "language": "Python"
  },
  "start_time": "2025-12-09T14:23:45",
  "end_time": "2025-12-09T14:25:12",
  "duration_seconds": 87.5
}
```

**Example:**
```python
workflow_engine.save_workflow_results(
    execution,
    Path('/mnt/d/models/outputs/workflow_result.json')
)
```

---

#### Workflow YAML Structure

**Basic Structure:**
```yaml
id: my-workflow
name: "My Workflow"
description: "Workflow description"

variables:
  input_var: "default value"
  another_var: 123

steps:
  - name: step1
    type: prompt
    prompt: "Process {{input_var}}"
    model: qwen3-coder-30b
    output_var: step1_result

  - name: step2
    type: prompt
    prompt: "Continue with {{step1_result}}"
    model: auto
    depends_on:
      - step1
    on_error: continue
```

**Supported Step Types:**

1. **prompt** - Execute model with prompt
```yaml
- name: analyze_code
  type: prompt
  prompt: "Analyze this code: {{code}}"
  model: qwen3-coder-30b  # or "auto" for auto-selection
  output_var: analysis
```

2. **template** - Use prompt template
```yaml
- name: review_code
  type: template
  template_id: code-review
  variables:
    code: "{{input_code}}"
    language: "Python"
  model: auto
  output_var: review
```

3. **conditional** - Conditional branching
```yaml
- name: check_quality
  type: conditional
  condition: "{{analysis}} contains 'excellent'"
  then:
    type: prompt
    prompt: "Great! {{analysis}}"
    model: auto
  else:
    type: prompt
    prompt: "Needs improvement: {{analysis}}"
    model: auto
```

4. **loop** - Iterate over items
```yaml
- name: process_files
  type: loop
  items_var: file_list
  loop_var: file
  body:
    type: prompt
    prompt: "Process {{file}}"
    model: auto
```

5. **extract** - Extract data from previous step
```yaml
- name: get_summary
  type: extract
  from_step: analyze_code
  pattern: "Summary: (.*)"
  output_var: summary
```

6. **sleep** - Delay execution
```yaml
- name: wait
  type: sleep
  duration: 2  # seconds
```

**Variable Substitution:**
Use `{{variable_name}}` in prompts to substitute variables.

**Dependencies:**
```yaml
- name: step3
  type: prompt
  prompt: "..."
  depends_on:
    - step1
    - step2
```

**Error Handling:**
```yaml
- name: risky_step
  type: prompt
  prompt: "..."
  on_error: continue  # or omit to stop on error
```

---

### WorkflowStep

**Description:** Data class representing a single workflow step.

**Location:** `workflow_engine.py`

#### Attributes

```python
@dataclass
class WorkflowStep:
    name: str                          # Step name
    step_type: str                     # Step type (prompt/template/conditional/loop/extract/sleep)
    config: Dict[str, Any]             # Step configuration
    depends_on: Optional[List[str]]    # Dependency step names
```

---

### WorkflowExecution

**Description:** Data class representing workflow execution state.

**Location:** `workflow_engine.py`

#### Attributes

```python
@dataclass
class WorkflowExecution:
    workflow_id: str                   # Workflow ID
    workflow_name: str                 # Workflow name
    steps: List[WorkflowStep]          # List of steps
    variables: Dict[str, Any]          # Variable values
    results: Dict[str, Any]            # Step name -> result
    status: str                        # Status: pending/running/completed/failed
    current_step: int                  # Current step index
    error_message: Optional[str]       # Error message if failed
    start_time: Optional[datetime]     # Start timestamp
    end_time: Optional[datetime]       # End timestamp
```

---

## Model Comparison

### ModelComparison

**Description:** Manages side-by-side model comparisons (A/B testing).

**Location:** `model_comparison.py`

#### Constructor

```python
def __init__(self, output_dir: Path)
```

Initializes model comparison manager.

**Parameters:**
- `output_dir` (Path): Directory to store comparison exports (created if doesn't exist)

**Example:**
```python
from pathlib import Path
from model_comparison import ModelComparison

comparisons_dir = Path('/mnt/d/models/comparisons')
comparison = ModelComparison(comparisons_dir)
```

---

#### Methods

##### create_comparison()

```python
def create_comparison(
    self,
    prompt: str,
    model_responses: List[Dict]
) -> ComparisonResult
```

Creates a comparison result from multiple model responses.

**Parameters:**
- `prompt` (str): The prompt text used for all models
- `model_responses` (List[Dict]): List of response dictionaries

**Response Dictionary Structure:**
```python
{
    'model_id': str,           # Model identifier
    'model_name': str,         # Human-readable name
    'response': str,           # Response text
    'tokens_input': int,       # Optional
    'tokens_output': int,      # Optional
    'duration': float          # Optional (seconds)
}
```

**Returns:** ComparisonResult object

**Example:**
```python
responses = [
    {
        'model_id': 'qwen3-coder-30b',
        'model_name': 'Qwen3 Coder 30B',
        'response': 'def hello():\n    print("Hello!")',
        'tokens_input': 50,
        'tokens_output': 25,
        'duration': 2.5
    },
    {
        'model_id': 'phi4-14b',
        'model_name': 'Phi-4 14B',
        'response': 'print("Hello, World!")',
        'tokens_input': 50,
        'tokens_output': 15,
        'duration': 1.2
    }
]

result = comparison.create_comparison(
    prompt="Write a hello world program",
    model_responses=responses
)
```

---

##### display_comparison()

```python
def display_comparison(
    self,
    result: ComparisonResult,
    colors=None
)
```

Displays side-by-side comparison in terminal.

**Parameters:**
- `result` (ComparisonResult): Comparison result to display
- `colors` (Colors, optional): Colors class for formatting

**Returns:** None

**Example:**
```python
from ai_router import Colors

comparison.display_comparison(result, colors=Colors)
# Displays:
# ╔══════════════════════════════════════════════════════════════╗
# ║  MODEL COMPARISON RESULTS
# ╚══════════════════════════════════════════════════════════════╝
#
# Prompt:
# Write a hello world program
#
# ────────────────────────────────────────────────────────────────
#
# [1] Qwen3 Coder 30B
# Model ID: qwen3-coder-30b
#
# def hello():
#     print("Hello!")
# ...
```

---

##### display_comparison_table()

```python
def display_comparison_table(
    self,
    result: ComparisonResult,
    colors=None
)
```

Displays comparison as a performance metrics table.

**Parameters:**
- `result` (ComparisonResult): Comparison result
- `colors` (Colors, optional): Colors class

**Returns:** None

**Example:**
```python
comparison.display_comparison_table(result, colors=Colors)
# Displays:
# ╔══════════════════════════════════════════════════════════════╗
# ║  PERFORMANCE METRICS
# ╚══════════════════════════════════════════════════════════════╝
#
# Model                          In/Out Tokens        Duration     Tok/Sec
# ────────────────────────────────────────────────────────────────────────────
# Phi-4 14B                      50/15                1.20s        12.5 tok/s ⭐
# Qwen3 Coder 30B                50/25                2.50s        10.0 tok/s
# ────────────────────────────────────────────────────────────────────────────
#
# ⭐ Fastest: Phi-4 14B (12.5 tok/s)
```

---

##### export_comparison()

```python
def export_comparison(
    self,
    result: ComparisonResult,
    format: str = 'json'
) -> Path
```

Exports comparison to JSON or Markdown.

**Parameters:**
- `result` (ComparisonResult): Comparison to export
- `format` (str): 'json' or 'markdown' (default 'json')

**Returns:** Path to exported file

**Filename Format:** `comparison_YYYYMMDD_HHMMSS.{json|md}`

**Example:**
```python
# Export as JSON
json_path = comparison.export_comparison(result, format='json')
print(f"Exported to: {json_path}")

# Export as Markdown
md_path = comparison.export_comparison(result, format='markdown')
```

---

##### save_comparison_to_db()

```python
def save_comparison_to_db(
    self,
    result: ComparisonResult,
    session_manager: SessionManager
)
```

Saves comparison to session database.

**Parameters:**
- `result` (ComparisonResult): Comparison to save
- `session_manager` (SessionManager): Session manager with database

**Returns:** None

**Example:**
```python
comparison.save_comparison_to_db(result, session_mgr)
```

---

##### load_comparison_from_db()

```python
def load_comparison_from_db(
    self,
    comparison_id: str,
    session_manager: SessionManager
) -> Optional[ComparisonResult]
```

Loads comparison from session database.

**Parameters:**
- `comparison_id` (str): Comparison UUID
- `session_manager` (SessionManager): Session manager

**Returns:** ComparisonResult or None if not found

**Example:**
```python
loaded = comparison.load_comparison_from_db(
    'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
    session_mgr
)
if loaded:
    comparison.display_comparison(loaded)
```

---

### ComparisonResult

**Description:** Data class storing a model comparison session.

**Location:** `model_comparison.py`

#### Attributes

```python
@dataclass
class ComparisonResult:
    comparison_id: str                 # Unique UUID
    timestamp: datetime                # Comparison timestamp
    prompt: str                        # Prompt used
    responses: List[Dict]              # List of model responses
    winner: Optional[str]              # Winning model ID (optional)
    notes: Optional[str]               # User notes (optional)
```

#### Methods

##### to_dict()

```python
def to_dict(self) -> Dict
```

Converts to dictionary for JSON serialization.

**Example:**
```python
data = result.to_dict()
import json
json.dump(data, open('comparison.json', 'w'))
```

---

##### from_dict()

```python
@classmethod
def from_dict(cls, data: Dict) -> 'ComparisonResult'
```

Creates ComparisonResult from dictionary.

**Example:**
```python
import json
data = json.load(open('comparison.json'))
result = ComparisonResult.from_dict(data)
```

---

## Database Schema

The AI Router uses SQLite 3.x for session management. The database is created automatically using `schema.sql`.

### Tables

#### sessions

Stores conversation session metadata.

```sql
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    model_id TEXT NOT NULL,
    model_name TEXT,
    title TEXT,
    message_count INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    total_duration_seconds REAL DEFAULT 0,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Indexes:**
- `idx_sessions_created` on `created_at DESC`
- `idx_sessions_updated` on `updated_at DESC`
- `idx_sessions_model` on `model_id`
- `idx_sessions_activity` on `last_activity DESC`

---

#### messages

Stores individual messages within sessions.

```sql
CREATE TABLE messages (
    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    sequence_number INTEGER NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tokens_used INTEGER,
    duration_seconds REAL,
    metadata TEXT,  -- JSON string
    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE,
    UNIQUE(session_id, sequence_number)
);
```

**Indexes:**
- `idx_messages_session` on `session_id, sequence_number`
- `idx_messages_timestamp` on `timestamp DESC`
- `idx_messages_role` on `role`

---

#### session_metadata

Stores additional session-level key-value metadata.

```sql
CREATE TABLE session_metadata (
    metadata_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE,
    UNIQUE(session_id, key)
);
```

**Indexes:**
- `idx_metadata_session` on `session_id`
- `idx_metadata_key` on `key`

---

### Full-Text Search

#### sessions_fts

FTS5 virtual table for full-text search on titles and content.

```sql
CREATE VIRTUAL TABLE sessions_fts USING fts5(
    session_id UNINDEXED,
    title,
    content,
    tokenize='porter unicode61'
);
```

**Usage:**
```python
# Search for Python-related sessions
results = session_mgr.search_sessions('python function')

# FTS5 syntax examples:
# "python AND function"     - Both terms
# "python OR javascript"    - Either term
# "code*"                   - Prefix match (code, coding, coder)
# "python NOT error"        - Python but not error
```

---

### Views

#### recent_sessions

View showing recent sessions with first/last message preview.

```sql
CREATE VIEW recent_sessions AS
SELECT
    s.session_id,
    s.title,
    s.model_id,
    s.model_name,
    s.message_count,
    s.total_tokens,
    s.total_duration_seconds,
    s.created_at,
    s.updated_at,
    s.last_activity,
    (SELECT content FROM messages
     WHERE session_id = s.session_id AND role = 'user'
     ORDER BY sequence_number ASC LIMIT 1) as first_prompt,
    (SELECT content FROM messages
     WHERE session_id = s.session_id
     ORDER BY sequence_number DESC LIMIT 1) as last_message
FROM sessions s
ORDER BY s.last_activity DESC;
```

---

#### session_stats

View showing aggregated statistics by model.

```sql
CREATE VIEW session_stats AS
SELECT
    model_id,
    COUNT(*) as session_count,
    SUM(message_count) as total_messages,
    SUM(total_tokens) as total_tokens,
    AVG(total_duration_seconds) as avg_duration,
    MIN(created_at) as first_session,
    MAX(last_activity) as last_session
FROM sessions
GROUP BY model_id;
```

---

### Triggers

#### update_session_timestamp

Automatically updates session timestamps when messages are added.

```sql
CREATE TRIGGER update_session_timestamp
AFTER INSERT ON messages
BEGIN
    UPDATE sessions
    SET
        updated_at = CURRENT_TIMESTAMP,
        last_activity = CURRENT_TIMESTAMP,
        message_count = message_count + 1
    WHERE session_id = NEW.session_id;
END;
```

---

#### auto_generate_title

Auto-generates session title from first user message.

```sql
CREATE TRIGGER auto_generate_title
AFTER INSERT ON messages
WHEN NEW.role = 'user' AND NEW.sequence_number = 1
BEGIN
    UPDATE sessions
    SET title = CASE
        WHEN LENGTH(NEW.content) > 60 THEN SUBSTR(NEW.content, 1, 60) || '...'
        ELSE NEW.content
    END
    WHERE session_id = NEW.session_id AND (title IS NULL OR title = '');
END;
```

---

#### FTS Synchronization Triggers

Keeps full-text search index synchronized:
- `sessions_fts_insert` - Sync on message insert
- `sessions_fts_update` - Sync on message update
- `sessions_fts_delete` - Sync on message delete

---

## Configuration Files

### .ai-router-config.json

Application configuration file.

**Location:** `{models_dir}/.ai-router-config.json`

**Structure:**
```json
{
  "bypass_mode": false,
  "version": "1.0"
}
```

**Fields:**
- `bypass_mode` (bool): Auto-yes mode for confirmations
- `version` (str): Config version

---

### .ai-router-preferences.json

User preferences for model selection.

**Location:** `{models_dir}/.ai-router-preferences.json`

**Structure:**
```json
{
  "coding": "qwen3-coder-30b",
  "reasoning": "phi4-14b",
  "creative": "gemma3-27b",
  "research": "llama33-70b",
  "math": "phi4-14b"
}
```

**Fields:** Category name → Preferred model ID

---

### Prompt Template YAML

Template file format.

**Location:** `{models_dir}/prompt-templates/{template_id}.yaml`

**Structure:**
```yaml
metadata:
  name: "Template Name"
  id: "template-id"
  category: "coding"  # or creative, research, general
  description: "Template description"
  recommended_models:
    - model-id-1
    - model-id-2
  variables:
    - name: "var_name"
      description: "Variable description"
      required: true
      default: "default_value"  # optional

system_prompt: |
  System prompt text here.
  Supports Jinja2 syntax: {{variable}}

user_prompt: |
  User prompt template.
  Variables: {{var_name}}

  {% if condition %}
  Conditional content
  {% endif %}
```

---

### Workflow YAML

Workflow definition file.

**Location:** `{models_dir}/workflows/{workflow_id}.yaml`

**Structure:** See [Workflow YAML Structure](#workflow-yaml-structure) section above.

---

## Examples

### Example 1: Basic Model Execution

```python
from ai_router import AIRouter

# Initialize router
router = AIRouter()

# Get model configuration
model_id = 'qwen3-coder-30b'
model_data = router.models[model_id]

# Execute model
response = router.run_model(
    model_id,
    model_data,
    'Write a Python function to calculate factorial'
)

# Access response
print(response.text)
print(f"Tokens: {response.tokens_input} → {response.tokens_output}")
print(f"Duration: {response.duration_seconds:.2f}s")
print(f"Speed: {response.tokens_output / response.duration_seconds:.1f} tok/s")
```

---

### Example 2: Auto-Selection with Context

```python
from ai_router import AIRouter
from pathlib import Path

router = AIRouter()

# Add context
router.context_manager.add_file(Path('/mnt/d/projects/app.py'))
router.context_manager.add_text(
    "Use type hints and docstrings",
    "Requirements"
)

# Build prompt with context
user_prompt = "Refactor this code for better readability"
full_prompt = router.context_manager.build_context_prompt(user_prompt)

# Auto-select model
model_id, category, confidence = router.model_selector.select_model(
    user_prompt,
    router.models
)

print(f"Selected: {router.models[model_id]['name']}")
print(f"Category: {category} ({confidence:.0%} confidence)")

# Execute
response = router.run_model(model_id, router.models[model_id], full_prompt)
print(response.text)
```

---

### Example 3: Session Management

```python
from ai_router import AIRouter

router = AIRouter()
session_mgr = router.session_manager

# Create session
session_id = session_mgr.create_session(
    model_id='phi4-14b',
    model_name='Phi-4 14B',
    title='Math homework'
)

# Add conversation messages
session_mgr.add_message(
    session_id,
    role='user',
    content='Solve: 2x + 5 = 15'
)

session_mgr.add_message(
    session_id,
    role='assistant',
    content='x = 5',
    tokens=120,
    duration=1.5
)

# Later: Resume session
messages = session_mgr.get_session_history(session_id)
for msg in messages:
    print(f"[{msg['role']}] {msg['content']}")

# Export session
markdown = session_mgr.export_session(session_id, format='markdown')
with open('session.md', 'w') as f:
    f.write(markdown)
```

---

### Example 4: Template Usage

```python
from ai_router import AIRouter

router = AIRouter()
template_mgr = router.template_manager

# Get template
template = template_mgr.get_template('code-review')

# Render with variables
rendered = template.render({
    'code': 'def add(a, b):\n    return a + b',
    'language': 'Python'
})

# Execute with rendered prompt
model_id = 'qwen3-coder-30b'
response = router.run_model(
    model_id,
    router.models[model_id],
    rendered['user_prompt']
)

print(response.text)
```

---

### Example 5: Batch Processing

```python
from ai_router import AIRouter
from pathlib import Path

router = AIRouter()
batch_proc = router.batch_processor

# Load prompts from file
prompts = batch_proc.load_prompts_from_file(
    Path('/mnt/d/projects/prompts.txt')
)

# Create job
job = batch_proc.create_job(
    model_id='qwen3-coder-30b',
    prompts=prompts
)

# Define execution function
def execute_model(prompt):
    return router.run_model(
        'qwen3-coder-30b',
        router.models['qwen3-coder-30b'],
        prompt
    )

# Process batch with progress callback
def show_progress(job, current):
    print(f"Progress: {current}/{job.total_prompts}")

results = batch_proc.process_batch(
    job=job,
    execute_fn=execute_model,
    progress_callback=show_progress,
    error_strategy="continue"
)

# Export results
batch_proc.export_results(
    job, results,
    Path('/mnt/d/models/outputs/batch_results.json'),
    format='json'
)

print(f"Completed: {job.completed}/{job.total_prompts}")
print(f"Failed: {job.failed}")
```

---

### Example 6: Workflow Execution

```python
from ai_router import AIRouter
from pathlib import Path

router = AIRouter()
workflow_engine = router.workflow_engine

# Load workflow
workflow_path = Path('/mnt/d/models/workflows/code-pipeline.yaml')
execution = workflow_engine.load_workflow(workflow_path)

# Set initial variables
execution.variables['code_file'] = 'app.py'
execution.variables['target_language'] = 'Python'

# Execute workflow
results = workflow_engine.execute_workflow(execution)

# Access results
print("Step Results:")
for step_name, result in results.items():
    print(f"\n{step_name}:")
    print(result[:200] + '...' if len(result) > 200 else result)

# Save results
workflow_engine.save_workflow_results(
    execution,
    Path('/mnt/d/models/outputs/workflow_result.json')
)
```

---

### Example 7: Model Comparison

```python
from ai_router import AIRouter, Colors

router = AIRouter()
comparison = router.model_comparison

# Define prompt
prompt = "Write a function to calculate Fibonacci numbers"

# Execute on multiple models
models_to_compare = ['qwen3-coder-30b', 'phi4-14b', 'gemma3-27b']
model_responses = []

for model_id in models_to_compare:
    response = router.run_model(
        model_id,
        router.models[model_id],
        prompt
    )

    model_responses.append({
        'model_id': model_id,
        'model_name': router.models[model_id]['name'],
        'response': response.text,
        'tokens_input': response.tokens_input,
        'tokens_output': response.tokens_output,
        'duration': response.duration_seconds
    })

# Create comparison
result = comparison.create_comparison(prompt, model_responses)

# Display comparison
comparison.display_comparison(result, colors=Colors)
comparison.display_comparison_table(result, colors=Colors)

# Export
comparison.export_comparison(result, format='markdown')
```

---

### Example 8: Analytics

```python
from ai_router import AIRouter

router = AIRouter()
analytics = router.analytics

# Display full dashboard
analytics.display_dashboard(days=30)

# Get specific statistics
stats = analytics.get_usage_statistics(days=7)
print(f"\nLast 7 days:")
print(f"  Sessions: {stats['total_sessions']}")
print(f"  Messages: {stats['total_messages']}")
print(f"  Tokens: {stats['total_tokens']:,}")

# Model usage
model_usage = analytics.get_model_usage(days=30)
print(f"\nTop 3 models:")
for model, count in model_usage[:3]:
    print(f"  {model}: {count} sessions")

# Performance metrics
top_models = analytics.get_top_models_by_performance()
print(f"\nTop performing model: {top_models[0]['model_name']}")
print(f"  Avg tokens: {top_models[0]['avg_tokens']:.0f}")
print(f"  Avg duration: {top_models[0]['avg_duration']:.2f}s")
```

---

### Example 9: Advanced Model Selection

```python
from ai_router import AIRouter

router = AIRouter()
selector = router.model_selector

# Analyze prompt
prompt = "Debug this Python code that crashes"
scores = selector.analyze_prompt(prompt)

print("Category scores:")
for category, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
    print(f"  {category}: {score:.0%}")

# Get recommendations
recommendations = selector.get_recommendations(prompt, router.models, top_n=3)

print("\nRecommendations:")
for i, rec in enumerate(recommendations, 1):
    print(f"{i}. {rec['model_id']}")
    print(f"   Category: {rec['category']}")
    print(f"   Confidence: {rec['confidence']:.0%}")

    # Get explanation
    explanation = selector.get_explanation(
        rec['category'],
        rec['confidence'],
        prompt
    )
    print(f"   Reason: {explanation}")

# Learn preference
print("\nUser prefers model #2")
selector.learn_preference(
    recommendations[1]['category'],
    recommendations[1]['model_id']
)
print("Preference saved!")
```

---

### Example 10: Custom Workflow Creation

```python
from ai_router import AIRouter
from pathlib import Path
import yaml

router = AIRouter()

# Define workflow programmatically
workflow_data = {
    'id': 'code-review-workflow',
    'name': 'Code Review Workflow',
    'description': 'Comprehensive code review with multiple steps',
    'variables': {
        'code': '',
        'language': 'Python'
    },
    'steps': [
        {
            'name': 'analyze_bugs',
            'type': 'prompt',
            'prompt': 'Analyze this {{language}} code for bugs:\n\n{{code}}',
            'model': 'qwen3-coder-30b',
            'output_var': 'bug_analysis'
        },
        {
            'name': 'check_style',
            'type': 'prompt',
            'prompt': 'Check this code for style issues:\n\n{{code}}',
            'model': 'qwen25-coder-32b',
            'output_var': 'style_report',
            'depends_on': ['analyze_bugs']
        },
        {
            'name': 'suggest_improvements',
            'type': 'prompt',
            'prompt': 'Based on bugs: {{bug_analysis}}\n\nAnd style: {{style_report}}\n\nSuggest improvements for:\n{{code}}',
            'model': 'phi4-14b',
            'output_var': 'improvements'
        },
        {
            'name': 'generate_report',
            'type': 'prompt',
            'prompt': 'Create a summary report combining:\n\nBugs: {{bug_analysis}}\nStyle: {{style_report}}\nImprovements: {{improvements}}',
            'model': 'auto',
            'output_var': 'final_report'
        }
    ]
}

# Save workflow
workflow_path = Path('/mnt/d/models/workflows/code-review-workflow.yaml')
with open(workflow_path, 'w') as f:
    yaml.dump(workflow_data, f, default_flow_style=False, sort_keys=False)

print(f"Workflow saved to: {workflow_path}")

# Validate
is_valid, errors = router.workflow_engine.validate_workflow(workflow_path)
if is_valid:
    print("Workflow is valid!")
else:
    print("Validation errors:")
    for error in errors:
        print(f"  - {error}")
```

---

## Security Notes

### CVE-2025-AIR-002: Path Traversal Fix

The `ContextManager.add_file()` method includes protection against path traversal attacks:

```python
def add_file(self, file_path: Path, label: Optional[str] = None):
    # Resolve to absolute path
    base_dir = Path.cwd().resolve()
    file_path_resolved = file_path.resolve()

    # Validate within base directory
    try:
        file_path_resolved.relative_to(base_dir)
    except ValueError:
        raise ValueError(f"Access denied: Path '{file_path}' is outside allowed directory")

    # Continue with file loading...
```

**Protection Against:**
- `../../../etc/passwd` - Directory traversal
- `/etc/shadow` - Absolute paths outside base directory
- Symbolic link attacks

**Recommendation:** Always validate user-provided file paths before passing to `add_file()`.

---

## API Versioning

**Current Version:** 1.0

**Compatibility:**
- Python 3.8+
- SQLite 3.24+ (for UPSERT support)
- llama.cpp (latest recommended)
- MLX 0.0.7+ (for macOS)

**Breaking Changes:** None (initial release)

---

## Support and Resources

**Documentation:**
- `GUIDE.md` - Comprehensive usage guide
- `API_REFERENCE.md` - This document
- `QUICKSTART.md` - Quick start guide

**Example Files:**
- Template examples: `{models_dir}/prompt-templates/`
- Workflow examples: `{models_dir}/workflows/`
- Batch prompt examples: `{models_dir}/batch_examples/`

**Configuration:**
- Model database: Edit `ModelDatabase` class in `ai-router.py`
- System prompts: `{models_dir}/system-prompt-*.txt`
- Templates: `{models_dir}/prompt-templates/*.yaml`

---

## Changelog

### Version 1.0 (December 9, 2025)

**Initial Release**

**Core Features:**
- AIRouter main application with 11 RTX 3090 models
- 4 Apple M4 Pro MLX models
- Intelligent model selection with confidence scoring
- SQLite session management with FTS5 search
- YAML + Jinja2 template system
- File and text context injection
- Response post-processing utilities
- Batch processing with checkpointing
- Analytics dashboard with visualizations
- Multi-step workflow engine
- Model comparison (A/B testing)

**Security:**
- CVE-2025-AIR-002: Path traversal protection in ContextManager

**Database:**
- SQLite schema v1.0 with sessions, messages, metadata tables
- Full-text search support
- Automatic triggers for data synchronization

---

**End of API Reference**

For usage examples and tutorials, see `GUIDE.md`.
For quick start instructions, see `QUICKSTART.md`.
For model-specific recommendations, see `model_examples_rtx3090.py`.
