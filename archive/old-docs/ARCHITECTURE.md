# AI Router Enhanced - System Architecture

**Version**: 2.0.0
**Last Updated**: December 9, 2025
**Status**: Production Ready

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Core Components](#core-components)
4. [Data Flow](#data-flow)
5. [Database Design](#database-design)
6. [Provider System](#provider-system)
7. [Menu System](#menu-system)
8. [Design Patterns](#design-patterns)
9. [Extensibility Points](#extensibility-points)
10. [Performance Considerations](#performance-considerations)
11. [Security Architecture](#security-architecture)

---

## Overview

AI Router Enhanced is a sophisticated multi-model AI orchestration system built on a modular, extensible architecture. The system provides intelligent model selection, conversation management, batch processing, and workflow automation across local and cloud AI providers.

### Core Design Principles

1. **Modularity**: Each feature is self-contained in its own module
2. **Extensibility**: Easy to add new features, providers, and models
3. **Performance**: Optimized for local execution with GPU acceleration
4. **Security**: Defense-in-depth with input validation and sandboxing
5. **Usability**: Menu-driven interface with intelligent defaults

### Architecture Goals

- **Single Interface**: Unified CLI for 14+ models across 5 providers
- **Intelligent Selection**: ML-based model recommendation with confidence scoring
- **Persistent History**: SQLite-based conversation and analytics storage
- **Template System**: Reusable prompts with Jinja2 variable substitution
- **Workflow Automation**: YAML-based multi-step AI pipelines

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                      (Menu-Driven CLI)                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                          AIRouter                               │
│                    (Main Orchestrator)                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  ModelDatabase    │  Colors       │  is_wsl()            │  │
│  │  (14 models)      │  (Terminal)   │  (Platform)          │  │
│  └──────────────────────────────────────────────────────────┘  │
└──┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬────┘
   │      │      │      │      │      │      │      │      │
   ▼      ▼      ▼      ▼      ▼      ▼      ▼      ▼      ▼
┌──────┐┌──────┐┌──────┐┌──────┐┌──────┐┌──────┐┌──────┐┌──────┐┌──────┐
│Model ││Sess- ││Temp- ││Cont- ││Resp- ││Batch ││Analy-││Work- ││Model │
│Selec-││ion   ││late  ││ext   ││onse  ││Proc- ││tics  ││flow  ││Comp- │
│tor   ││Mgr   ││Mgr   ││Mgr   ││Proc  ││essor ││Dash  ││Eng   ││arison│
└──┬───┘└──┬───┘└──┬───┘└──┬───┘└──┬───┘└──┬───┘└──┬───┘└──┬───┘└──┬───┘
   │       │       │       │       │       │       │       │       │
   │       │       └───────┴───────┴───────┴───────┘       │       │
   │       │                      │                        │       │
   │       ▼                      ▼                        │       │
   │   ┌───────────────────┐ ┌───────────────────┐       │       │
   │   │  SQLite Database  │ │  File System      │       │       │
   │   │  - Sessions       │ │  - Templates      │       │       │
   │   │  - Messages       │ │  - Workflows      │       │       │
   │   │  - Analytics      │ │  - Context Files  │       │       │
   │   │  - Tags/Bookmarks │ │  - Checkpoints    │       │       │
   │   └───────────────────┘ └───────────────────┘       │       │
   │                                                       │       │
   ▼                                                       ▼       ▼
┌─────────────────────────────────────────────────────────────────┐
│                      PROVIDER LAYER                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐              │
│  │ llama.cpp   │ │   Ollama    │ │     MLX     │ (Local)      │
│  │   (WSL)     │ │  (Windows)  │ │   (macOS)   │              │
│  └─────────────┘ └─────────────┘ └─────────────┘              │
│  ┌─────────────┐ ┌─────────────┐                               │
│  │ OpenRouter  │ │   OpenAI    │ │   Claude   │ (Cloud)       │
│  │    (API)    │ │    (API)    │ │    (API)   │               │
│  └─────────────┘ └─────────────┘ └────────────┘               │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     MODEL EXECUTION LAYER                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  RTX 3090: 10 models (llama.cpp via WSL)                 │  │
│  │  M4 Pro:    4 models (MLX native)                        │  │
│  │  Cloud:     100+ models (API)                            │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. AIRouter (ai-router.py)

**Purpose**: Main orchestrator and entry point

**Responsibilities**:
- Menu system and user interaction
- Model database management (14 models)
- Provider routing and execution
- Interactive mode coordination
- Platform detection (Windows/WSL/macOS)

**Key Methods**:
- `interactive_mode()`: Main menu loop
- `auto_select_mode()`: Smart model selection
- `manual_select_mode()`: Browse and select
- `run_model()`: Execute model inference
- `run_llama_cpp()`: Local llama.cpp execution (WSL)
- `run_mlx()`: Apple Silicon MLX execution

**Dependencies**: All feature modules, Colors, platform

---

### 2. ModelSelector (model_selector.py)

**Purpose**: Intelligent model selection with ML-based scoring

**Responsibilities**:
- Analyze prompts to detect intent category
- Calculate confidence scores (0-100%)
- Recommend top-3 models with justifications
- Learn from user preferences
- Handle edge cases and fallbacks

**Algorithm**:
```python
def select_model(prompt, models):
    # 1. Keyword extraction and TF-IDF analysis
    keywords = extract_keywords(prompt)

    # 2. Category detection (coding, reasoning, creative, research)
    category = detect_category(keywords)

    # 3. Score all models for category fit
    scores = {}
    for model_id, model in models.items():
        score = calculate_score(model, category, keywords)
        scores[model_id] = score

    # 4. Select highest scoring model
    best_model = max(scores, key=scores.get)
    confidence = scores[best_model] / 100.0

    return best_model, category, confidence
```

**Patterns**: Strategy pattern for category detection

---

### 3. SessionManager (session_manager.py)

**Purpose**: Persistent conversation history with SQLite

**Responsibilities**:
- Create/load/save/delete sessions
- Store messages with metadata
- Full-text search (FTS5)
- Export to JSON/Markdown
- Tag and bookmark management

**Database Tables**:
- `sessions`: Session metadata
- `messages`: Individual messages (linked to sessions)
- `session_tags`: Many-to-many tag associations
- `message_search`: FTS5 virtual table for full-text search

**Key Methods**:
- `create_session(model_id)`: New session
- `add_message(session_id, role, content)`: Add message
- `get_session_messages(session_id)`: Retrieve history
- `search_sessions(query)`: FTS5 search
- `export_session(session_id, format)`: Export to file

**Patterns**: Repository pattern, Active Record

---

### 4. TemplateManager (template_manager.py)

**Purpose**: YAML + Jinja2 template system for reusable prompts

**Responsibilities**:
- Load/save YAML templates
- Render templates with variable substitution
- Validate template syntax
- List available templates
- Manage template library

**Template Format**:
```yaml
name: "Code Review"
description: "Review code for quality and bugs"
category: "coding"
variables:
  - name: "code"
    description: "Code to review"
    required: true
  - name: "language"
    description: "Programming language"
    required: true
    default: "Python"
template: |
  Review this {{ language }} code for quality, bugs, and best practices:

  ```{{ language }}
  {{ code }}
  ```
```

**Key Methods**:
- `load_template(name)`: Load from YAML
- `render(template, variables)`: Jinja2 rendering
- `list_templates()`: Available templates
- `create_template(...)`: Create new template

**Patterns**: Template Method pattern, Builder pattern

---

### 5. ContextManager (context_manager.py)

**Purpose**: File/text context injection with security

**Responsibilities**:
- Load context from files (30+ languages)
- Validate file paths (prevent path traversal)
- Estimate token count
- Optimize context for model limits
- Support multi-file contexts

**Security**:
```python
def load_file(file_path):
    # Path traversal protection (CVE-2025-AIR-002 FIX)
    base_dir = Path.cwd().resolve()
    file_path_resolved = Path(file_path).resolve()

    try:
        file_path_resolved.relative_to(base_dir)
    except ValueError:
        raise ValueError("Access denied: Path outside base directory")

    # Safe to load
    with open(file_path_resolved, 'r') as f:
        return f.read()
```

**Supported Languages**: 30+ (Python, JavaScript, Java, C++, Rust, Go, etc.)

**Patterns**: Facade pattern, Proxy pattern (security)

---

### 6. ResponseProcessor (response_processor.py)

**Purpose**: Automatic response formatting and post-processing

**Responsibilities**:
- Extract code blocks by language
- Calculate response statistics (words, tokens, lines)
- Format output with syntax highlighting
- Save responses to files
- Generate summaries

**Key Methods**:
- `process_response(text)`: Main processing
- `extract_code_blocks(text)`: Find all code blocks
- `calculate_stats(text)`: Word/token/line counts
- `format_output(text)`: ANSI formatting
- `save_to_file(text, path)`: Export

**Patterns**: Chain of Responsibility, Decorator

---

### 7. BatchProcessor (batch_processor.py)

**Purpose**: Process multiple prompts with checkpointing

**Responsibilities**:
- Load prompts from files (TXT, JSON)
- Execute with progress tracking
- Checkpoint every N prompts
- Resume from checkpoints
- Error handling strategies (stop/continue/threshold)
- Export results (JSON, CSV)

**Checkpoint Format**:
```json
{
  "job_id": "batch_20251209_001234",
  "model_id": "qwen3-coder-30b",
  "total_prompts": 100,
  "completed": 47,
  "failed": 2,
  "checkpoint_time": "2025-12-09T00:12:34",
  "results": [...]
}
```

**Key Methods**:
- `create_job(model_id, prompts)`: New batch
- `run_batch(job)`: Execute
- `save_checkpoint(job)`: Save progress
- `resume_batch(checkpoint_file)`: Resume
- `export_results(job, format)`: Export

**Patterns**: Command pattern, Memento pattern (checkpointing)

---

### 8. AnalyticsDashboard (analytics_dashboard.py)

**Purpose**: Usage statistics and performance metrics

**Responsibilities**:
- Track all model executions
- Calculate usage statistics
- Generate performance reports
- Model usage charts (ASCII sparklines)
- Export analytics (JSON)

**Database Views**:
- `model_usage_stats`: Aggregated by model
- `daily_activity`: Usage by day
- `session_durations`: Time analysis
- `popular_models`: Ranking
- `response_times`: Performance metrics

**Key Metrics**:
- Total messages
- Model usage distribution
- Average tokens per message
- Peak usage times
- Response time percentiles

**Patterns**: Observer pattern, Facade pattern

---

### 9. WorkflowEngine (workflow_engine.py)

**Purpose**: YAML-based multi-step AI automation

**Responsibilities**:
- Parse YAML workflow definitions
- Execute steps sequentially
- Variable substitution between steps
- Conditional execution
- Error handling and retry logic
- Output aggregation

**Workflow Format**:
```yaml
name: "Research Pipeline"
description: "Multi-step research workflow"
steps:
  - name: "gather_info"
    model: "llama-3.3-70b-abliterated"
    prompt: "Research {{ topic }}"
    capture_output: true

  - name: "analyze"
    model: "qwen3-coder-30b"
    prompt: "Analyze: {{ steps.gather_info.output }}"
    depends_on: ["gather_info"]

  - name: "summarize"
    model: "dolphin-mistral-24b"
    prompt: "Summarize findings"
    depends_on: ["analyze"]
```

**Key Methods**:
- `load_workflow(yaml_file)`: Parse YAML
- `execute_workflow(workflow, variables)`: Run all steps
- `execute_step(step, context)`: Execute single step
- `substitute_variables(text, context)`: Variable replacement

**Patterns**: Chain of Responsibility, Interpreter pattern

---

### 10. ModelComparison (model_comparison.py)

**Purpose**: Side-by-side A/B testing of multiple models

**Responsibilities**:
- Execute same prompt on 2-4 models in parallel
- Calculate performance metrics
- Compare outputs side-by-side
- Generate comparison reports
- Export results (JSON, Markdown)

**Metrics Calculated**:
- Response time
- Token count
- Response length
- Quality score (if available)
- Cost (for API models)

**Key Methods**:
- `compare_models(prompt, model_ids)`: Run comparison
- `calculate_metrics(results)`: Performance analysis
- `format_comparison(results)`: Pretty output
- `export_comparison(results, format)`: Export

**Patterns**: Strategy pattern, Composite pattern

---

## Data Flow

### User Request Flow

```
1. User Input
   ↓
2. Menu Selection (AIRouter.interactive_mode)
   ↓
3. Route to Feature Module
   ├─ Auto-select → ModelSelector.select_model()
   ├─ Manual → AIRouter.list_models()
   ├─ Context → ContextManager.load_context()
   ├─ Session → SessionManager.load_session()
   ├─ Batch → BatchProcessor.run_batch()
   ├─ Workflow → WorkflowEngine.execute_workflow()
   ├─ Analytics → AnalyticsDashboard.show_dashboard()
   ├─ Comparison → ModelComparison.compare_models()
   └─ Templates → TemplateManager.render_template()
   ↓
4. Build Prompt (with context/template)
   ↓
5. Select Model & Provider
   ├─ llama.cpp (WSL) → AIRouter.run_llama_cpp()
   ├─ MLX (macOS) → AIRouter.run_mlx()
   └─ API (Cloud) → Provider-specific call
   ↓
6. Execute Model Inference
   ↓
7. Post-Process Response (ResponseProcessor)
   ├─ Extract code blocks
   ├─ Calculate statistics
   ├─ Format output
   └─ Save to file (optional)
   ↓
8. Store in Database (SessionManager)
   ├─ Add message to session
   ├─ Update analytics
   └─ Index for FTS5 search
   ↓
9. Display to User
   └─ Formatted output with colors
```

### Database Operations Flow

```
1. Create Session
   ↓
   INSERT INTO sessions (model_id, created_at, ...)
   ↓
   Return session_id

2. Add Message
   ↓
   INSERT INTO messages (session_id, role, content, ...)
   ↓
   INSERT INTO message_search (content) -- FTS5
   ↓
   Update session last_updated
   ↓
   Trigger: Update analytics views

3. Search Sessions
   ↓
   SELECT FROM message_search WHERE content MATCH ?
   ↓
   JOIN with messages and sessions
   ↓
   Return ranked results

4. Generate Analytics
   ↓
   Query analytics views (pre-aggregated)
   ↓
   Calculate sparklines
   ↓
   Format and display
```

### Template Rendering Flow

```
1. Load Template YAML
   ↓
   yaml.safe_load(template_file)

2. Validate Template
   ├─ Check required fields
   ├─ Validate Jinja2 syntax
   └─ Check variable definitions
   ↓
3. Collect Variable Values
   ├─ Prompt user for required variables
   └─ Use defaults for optional
   ↓
4. Render with Jinja2
   ↓
   Environment.from_string(template).render(variables)
   ↓
5. Return Rendered Prompt
```

---

## Database Design

### Schema Overview

```sql
-- Sessions table
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_id TEXT NOT NULL,
    title TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message_count INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0
);

-- Messages table
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    role TEXT NOT NULL, -- 'user' or 'assistant'
    content TEXT NOT NULL,
    tokens INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

-- Tags (many-to-many)
CREATE TABLE session_tags (
    session_id INTEGER NOT NULL,
    tag TEXT NOT NULL,
    PRIMARY KEY (session_id, tag),
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

-- Full-text search (FTS5)
CREATE VIRTUAL TABLE message_search USING fts5(
    message_id UNINDEXED,
    content,
    content=messages,
    content_rowid=id
);

-- Triggers to keep FTS5 in sync
CREATE TRIGGER messages_ai AFTER INSERT ON messages BEGIN
    INSERT INTO message_search(rowid, content) VALUES (new.id, new.content);
END;

CREATE TRIGGER messages_ad AFTER DELETE ON messages BEGIN
    DELETE FROM message_search WHERE rowid = old.id;
END;

CREATE TRIGGER messages_au AFTER UPDATE ON messages BEGIN
    UPDATE message_search SET content = new.content WHERE rowid = new.id;
END;
```

### Indexing Strategy

```sql
-- Performance indexes
CREATE INDEX idx_messages_session ON messages(session_id);
CREATE INDEX idx_messages_created ON messages(created_at DESC);
CREATE INDEX idx_sessions_updated ON sessions(updated_at DESC);
CREATE INDEX idx_sessions_model ON sessions(model_id);
CREATE INDEX idx_tags_session ON session_tags(session_id);
CREATE INDEX idx_tags_tag ON session_tags(tag);
```

### Analytics Views

```sql
-- Model usage statistics
CREATE VIEW model_usage_stats AS
SELECT
    model_id,
    COUNT(*) as total_sessions,
    SUM(message_count) as total_messages,
    SUM(total_tokens) as total_tokens,
    AVG(message_count) as avg_messages_per_session
FROM sessions
GROUP BY model_id;

-- Daily activity
CREATE VIEW daily_activity AS
SELECT
    DATE(created_at) as date,
    COUNT(*) as sessions,
    SUM(message_count) as messages
FROM sessions
GROUP BY DATE(created_at);
```

---

## Provider System

### Provider Abstraction

The system supports multiple execution providers through a unified interface:

```python
class Provider:
    """Abstract provider interface"""

    def execute(self, model_id, prompt, params):
        """Execute model inference"""
        raise NotImplementedError

    def is_available(self):
        """Check if provider is available"""
        raise NotImplementedError
```

### Supported Providers

1. **llama.cpp (Local - WSL)**
   - Platform: Windows with WSL
   - Models: 10 RTX 3090 models
   - Execution: `wsl bash -c "~/llama.cpp/build/bin/llama-cli ..."`
   - Features: Full GPU offload, optimal parameters, Flash Attention

2. **MLX (Local - macOS)**
   - Platform: Apple Silicon (M4 Pro)
   - Models: 4 models optimized for Apple GPU
   - Execution: `mlx_lm.generate --model ... --prompt ...`
   - Features: Unified memory, optimized for M-series chips

3. **Ollama (Local - Alternative)**
   - Platform: Cross-platform
   - Models: Any GGUF model
   - Execution: `ollama run model_name "prompt"`
   - Features: Simple API, automatic model management

4. **OpenRouter (Cloud API)**
   - Platform: Cloud
   - Models: 100+ models via unified API
   - Execution: HTTP POST to api.openrouter.ai
   - Features: Cost tracking, fallbacks, load balancing

5. **OpenAI (Cloud API)**
   - Platform: Cloud
   - Models: GPT-3.5, GPT-4, GPT-4-Turbo
   - Execution: HTTP POST to api.openai.com
   - Features: Function calling, JSON mode, vision

6. **Claude (Cloud API - Future)**
   - Platform: Cloud
   - Models: Claude 3 family
   - Execution: HTTP POST to api.anthropic.com
   - Features: 200K context, vision, tool use

### Provider Selection Logic

```python
def select_provider(model_id, model_data):
    framework = model_data['framework']
    platform = detect_platform()

    if framework == 'llama.cpp':
        if platform == 'Windows' and is_wsl():
            return LlamaCppWSLProvider()
        elif platform == 'Linux':
            return LlamaCppNativeProvider()

    elif framework == 'mlx':
        if platform == 'Darwin':  # macOS
            return MLXProvider()

    elif framework == 'api':
        provider_name = model_data['provider']
        if provider_name == 'openrouter':
            return OpenRouterProvider()
        elif provider_name == 'openai':
            return OpenAIProvider()

    raise ValueError(f"No provider for {framework} on {platform}")
```

---

## Menu System

### Menu Architecture

The menu system uses a state machine pattern:

```
Main Menu
├── [1] Auto-select → ModelSelector
├── [2] Manual select → list_models() → model selection
├── [3] Context Management → ContextManager sub-menu
│   ├── Load file
│   ├── Load text
│   ├── Clear context
│   └── View context
├── [4] Session Management → SessionManager sub-menu
│   ├── New session
│   ├── Load session
│   ├── List sessions
│   ├── Search sessions
│   ├── Export session
│   └── Delete session
├── [5] Batch Processing → BatchProcessor sub-menu
├── [6] Workflow Automation → WorkflowEngine sub-menu
├── [7] Analytics Dashboard → AnalyticsDashboard
├── [8] System Prompts → view_system_prompts()
├── [9] Parameters Guide → view_parameters_guide()
├── [10] Documentation → view_documentation()
├── [11] Model Comparison → ModelComparison sub-menu
├── [12] Prompt Templates → TemplateManager sub-menu
├── [A] Toggle Auto-Yes → toggle_bypass_mode()
└── [0] Exit
```

### State Management

```python
class AIRouter:
    def __init__(self):
        self.bypass_mode = False  # Auto-yes mode
        self.current_session = None
        self.current_context = []
        self.current_template = None

    def interactive_mode(self):
        while True:
            self.print_banner()
            self.show_menu()
            choice = input("Enter choice: ")
            self.handle_choice(choice)
```

---

## Design Patterns

### 1. Strategy Pattern
**Used in**: ModelSelector, ResponseProcessor
**Purpose**: Different algorithms for model selection and response processing

### 2. Repository Pattern
**Used in**: SessionManager, TemplateManager
**Purpose**: Abstract data access layer

### 3. Factory Pattern
**Used in**: Provider selection
**Purpose**: Create appropriate provider based on platform

### 4. Template Method Pattern
**Used in**: TemplateManager
**Purpose**: Define template rendering workflow

### 5. Chain of Responsibility
**Used in**: ResponseProcessor, WorkflowEngine
**Purpose**: Sequential processing steps

### 6. Observer Pattern
**Used in**: AnalyticsDashboard (future)
**Purpose**: Track events and update analytics

### 7. Command Pattern
**Used in**: BatchProcessor, WorkflowEngine
**Purpose**: Encapsulate operations as objects

### 8. Memento Pattern
**Used in**: BatchProcessor (checkpoints)
**Purpose**: Save and restore state

### 9. Facade Pattern
**Used in**: AIRouter
**Purpose**: Simplified interface to complex subsystems

### 10. Proxy Pattern
**Used in**: ContextManager (security)
**Purpose**: Control access to file system

---

## Extensibility Points

### Adding a New Feature Module

1. Create module file (e.g., `new_feature.py`)
2. Implement main class with public API
3. Import in `ai-router.py`
4. Add menu option in `interactive_mode()`
5. Add handler method
6. Update documentation

Example:
```python
# new_feature.py
class NewFeature:
    def __init__(self, db_path):
        self.db_path = db_path

    def do_something(self):
        # Implementation
        pass

# ai-router.py
from new_feature import NewFeature

class AIRouter:
    def __init__(self):
        self.new_feature = NewFeature(self.db_path)

    def interactive_mode(self):
        # Add menu option
        print("[13] New Feature")

        # Handle choice
        if choice == "13":
            self.new_feature_mode()

    def new_feature_mode(self):
        self.new_feature.do_something()
```

### Adding a New Provider

1. Create provider module in `providers/` directory
2. Implement provider interface
3. Register in provider factory
4. Add models to ModelDatabase
5. Update documentation

### Adding a New Model

1. Download model (GGUF format for local)
2. Add to ModelDatabase in `ai-router.py`:
```python
'new-model-id': {
    'name': 'New Model Name',
    'path': '/path/to/model.gguf',
    'framework': 'llama.cpp',
    'size': '14GB',
    'use_case': 'coding',
    'temperature': 0.7,
    # ... other parameters
}
```
3. Create system prompt file
4. Test execution
5. Update documentation

---

## Performance Considerations

### Current Performance

- **Startup Time**: 900ms (target: 350ms)
- **Database Queries**: 500ms average (target: 350ms)
- **File I/O**: 200ms for large files (target: 80ms)
- **Template Rendering**: 50ms (target: 25ms)

### Optimization Strategies

1. **Lazy Module Loading**
   - Load feature modules only when needed
   - Expected: 200ms startup improvement

2. **System Prompt Caching**
   - Cache loaded system prompts in memory
   - Expected: 50-100ms per execution

3. **Database Connection Pooling**
   - Reuse connections instead of opening/closing
   - Expected: 15-20% query improvement

4. **Composite Indexes**
   - Add indexes for common query patterns
   - Expected: 60-120ms per query improvement

5. **Template Compilation Caching**
   - Compile Jinja2 templates once
   - Expected: 50% render time reduction

6. **Async File I/O** (Future)
   - Use asyncio for file operations
   - Expected: 60% I/O improvement

### Memory Management

- **Session Cache**: LRU cache for recent sessions (max 10)
- **Context Limits**: Enforce max context size (128K tokens)
- **Batch Processing**: Stream results to disk, don't hold in memory
- **Analytics**: Pre-aggregate data, use views instead of complex queries

---

## Security Architecture

### Security Layers

1. **Input Validation**
   - All user input sanitized
   - Path traversal prevention (CVE-2025-AIR-002 fixed)
   - Length limits enforced
   - Type checking

2. **Sandboxing**
   - Command injection prevention (CVE-2025-AIR-001/003 fixed)
   - Use argument lists instead of shell=True
   - Whitelist allowed commands

3. **Database Security**
   - SQL injection prevention (parameterized queries)
   - Database file permissions (600)
   - No sensitive data in plaintext (future: encryption)

4. **File System Security**
   - Base directory restriction
   - Path canonicalization
   - File extension whitelist
   - Size limits

5. **API Security** (Future)
   - API key encryption
   - Rate limiting
   - Authentication
   - Audit logging

### Threat Model

**Protected Against**:
- Command injection (CVSS 9.8) ✅ FIXED
- Path traversal (CVSS 9.1) ✅ FIXED
- SQL injection (CVSS 7.5) ⚠️ Needs work
- XSS in output ✅ (CLI only, no web interface)

**Not Protected Against**:
- Physical access to machine
- Malicious YAML/templates (user responsibility)
- Compromised API keys
- DDoS (no rate limiting yet)

See SECURITY-AUDIT-REPORT-100.md for full threat analysis.

---

## Future Architecture

### Planned Improvements

1. **Microservices Architecture** (v3.0)
   - Separate services for each feature
   - REST API for external integration
   - gRPC for internal communication

2. **Plugin System** (v2.5)
   - Dynamic plugin loading
   - Plugin marketplace
   - Sandboxed execution

3. **Distributed Execution** (v3.0)
   - Distribute batch jobs across multiple machines
   - Load balancing
   - Fault tolerance

4. **Web Interface** (v2.5)
   - Vue.js/React frontend
   - WebSocket for real-time updates
   - Mobile-responsive design

5. **Advanced Analytics** (v2.2)
   - Machine learning for usage prediction
   - Anomaly detection
   - Cost optimization recommendations

---

## Conclusion

The AI Router Enhanced architecture is designed for:
- **Modularity**: Easy to extend and maintain
- **Performance**: Optimized for local execution
- **Security**: Defense-in-depth approach
- **Usability**: Intuitive menu-driven interface
- **Scalability**: Ready for future enhancements

For implementation details, see:
- API_REFERENCE.md - Complete API documentation
- DEVELOPER_GUIDE.md - Development guidelines
- FEATURE_DOCUMENTATION.md - Feature deep-dives

---

**Version**: 2.0.0
**Last Updated**: December 9, 2025
**Authors**: AI Router Enhanced Team
