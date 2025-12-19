# AI Router Enhanced - Developer Guide

**Complete Technical Documentation for Contributors**

Version: 2.0
Last Updated: December 9, 2025
Target Audience: Developers, Contributors, Maintainers

---

## Table of Contents

1. [Introduction](#introduction)
2. [Quick Start for Developers](#quick-start-for-developers)
3. [Development Environment Setup](#development-environment-setup)
4. [Project Architecture](#project-architecture)
5. [Project Structure](#project-structure)
6. [Core Components Deep Dive](#core-components-deep-dive)
7. [Development Workflow](#development-workflow)
8. [Code Standards and Style Guide](#code-standards-and-style-guide)
9. [Adding New Features](#adding-new-features)
10. [Testing Guide](#testing-guide)
11. [Database Development](#database-development)
12. [API Development](#api-development)
13. [Debugging and Troubleshooting](#debugging-and-troubleshooting)
14. [Performance Optimization](#performance-optimization)
15. [Security Best Practices](#security-best-practices)
16. [Documentation Standards](#documentation-standards)
17. [Code Review Process](#code-review-process)
18. [Release Process](#release-process)
19. [Contributing Guidelines](#contributing-guidelines)
20. [Getting Help](#getting-help)

---

## Introduction

### Welcome to AI Router Enhanced Development

AI Router Enhanced is a sophisticated CLI application for intelligent model selection and execution across local and cloud LLMs. This guide will help you understand the codebase, contribute effectively, and maintain high code quality.

### What is AI Router Enhanced?

**Purpose**: Unified interface for managing and executing multiple AI models (local GGUF via llama.cpp, cloud APIs) with advanced features like session management, templates, batch processing, and analytics.

**Key Technologies**:
- **Language**: Python 3.8+
- **Database**: SQLite 3
- **Templates**: YAML + Jinja2
- **Local Models**: llama.cpp (WSL/Linux)
- **Cloud APIs**: OpenRouter, OpenAI, Anthropic
- **CLI Framework**: Custom (no external framework dependencies)

### Project Philosophy

1. **Simplicity First**: Keep the codebase accessible to new contributors
2. **Modularity**: Each feature is a self-contained module
3. **Production-Ready**: All features must be thoroughly tested
4. **User-Focused**: Prioritize user experience and reliability
5. **Documentation**: Code should be self-documenting with clear comments

### Who Should Use This Guide?

- New contributors wanting to add features
- Developers debugging issues
- Maintainers reviewing pull requests
- Advanced users customizing the system
- Teams deploying in production environments

---

## Quick Start for Developers

### 5-Minute Setup

Get up and running quickly:

```bash
# 1. Clone repository
cd D:\models  # Or your preferred location
git pull origin main  # If already cloned

# 2. Create virtual environment
python -m venv venv

# 3. Activate environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# Linux/WSL/macOS:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Initialize database
python session_db_setup.py

# 6. Validate installation
python validate_installation.py

# 7. Run smoke test
python smoke_test.py

# 8. Start development
python ai-router.py
```

### First Contribution Workflow

```bash
# 1. Create feature branch
git checkout -b feature/your-feature-name

# 2. Make changes
# Edit files...

# 3. Run tests
python test_integration.py

# 4. Commit changes
git add .
git commit -m "Add: Your feature description"

# 5. Push and create PR
git push origin feature/your-feature-name
# Then create Pull Request on GitHub
```

---

## Development Environment Setup

### System Requirements

**Minimum**:
- Python 3.8+
- 8GB RAM
- 10GB disk space
- Windows 10/11, Linux, or macOS

**Recommended**:
- Python 3.11+
- 16GB+ RAM
- 50GB+ disk space (for local models)
- WSL2 (for Windows users running local models)
- NVIDIA GPU with 12GB+ VRAM (for local model inference)

### Python Environment Setup

#### Option 1: Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import yaml, jinja2; print('Dependencies OK')"
```

#### Option 2: Conda Environment

```bash
# Create conda environment
conda create -n ai-router python=3.11

# Activate
conda activate ai-router

# Install dependencies
pip install -r requirements.txt
```

### Required Dependencies

```txt
# Core dependencies (required)
PyYAML>=6.0          # Template system
Jinja2>=3.1.0        # Template rendering

# Optional dependencies
pyperclip            # Clipboard functionality
requests             # HTTP requests for cloud APIs
beautifulsoup4       # HTML parsing (if needed)
```

### Development Dependencies

```bash
# Install development dependencies
pip install pytest pytest-cov black flake8 mypy pylint

# Or create requirements-dev.txt:
pip install -r requirements-dev.txt
```

Example `requirements-dev.txt`:
```txt
# Testing
pytest>=7.0
pytest-cov>=4.0
pytest-asyncio>=0.21

# Code quality
black>=23.0
flake8>=6.0
mypy>=1.0
pylint>=2.17

# Documentation
sphinx>=5.0
sphinx-rtd-theme>=1.2
```

### IDE Setup

#### Visual Studio Code

Create `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length=100"],
    "editor.formatOnSave": true,
    "editor.rulers": [100],
    "files.trimTrailingWhitespace": true,
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": [
        "tests"
    ]
}
```

Create `.vscode/launch.json` for debugging:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: AI Router",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/ai-router.py",
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        },
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal"
        },
        {
            "name": "Python: Tests",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": ["tests/", "-v"],
            "console": "integratedTerminal"
        }
    ]
}
```

#### PyCharm

1. Open project directory
2. Configure Python interpreter: Settings → Project → Python Interpreter → Add → Virtualenv Environment → Existing environment → Select `venv/bin/python`
3. Enable pytest: Settings → Tools → Python Integrated Tools → Testing → pytest
4. Configure code style: Settings → Editor → Code Style → Python → Set line length to 100

### Git Configuration

```bash
# Set up git hooks (optional)
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Run tests before commit
python -m pytest tests/ -x
if [ $? -ne 0 ]; then
    echo "Tests failed. Commit aborted."
    exit 1
fi
EOF

chmod +x .git/hooks/pre-commit
```

### Environment Variables

Create `.env` file (never commit this):
```bash
# API Keys (optional, for cloud models)
OPENROUTER_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here

# Development settings
DEBUG=True
LOG_LEVEL=DEBUG
DATABASE_PATH=.ai-router-sessions.db
TEMPLATE_DIR=prompt-templates
OUTPUT_DIR=outputs
```

Load in Python:
```python
from pathlib import Path
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Access variables
DEBUG = os.getenv('DEBUG', 'False') == 'True'
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
```

---

## Project Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface (CLI)                     │
│                      ai-router.py                            │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
┌───────▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐
│   Session    │ │  Template  │ │   Model    │
│   Manager    │ │  Manager   │ │  Selector  │
└───────┬──────┘ └─────┬──────┘ └─────┬──────┘
        │              │              │
        │      ┌───────▼──────────────▼──────┐
        │      │    Context Manager          │
        │      └───────┬─────────────────────┘
        │              │
┌───────▼──────────────▼─────────────────────┐
│           Core AI Router Engine             │
│  (Model execution, response handling)       │
└───────┬─────────────────────────────────────┘
        │
┌───────▼──────┬──────────┬──────────┬────────┐
│   Batch      │ Workflow │Analytics │Response│
│  Processor   │  Engine  │Dashboard │Processor│
└──────────────┴──────────┴──────────┴────────┘
        │              │              │
┌───────▼──────────────▼──────────────▼────────┐
│            SQLite Database                    │
│       (.ai-router-sessions.db)                │
└───────────────────────────────────────────────┘
```

### Component Interaction Flow

**Example: User starts a new session**

```
User Input → CLI Menu → SessionManager.create_session()
                              ↓
                    Database INSERT (sessions table)
                              ↓
            ModelSelector.select_model(user_prompt)
                              ↓
                    AIRouter.execute_model()
                              ↓
           llama.cpp execution (or cloud API call)
                              ↓
                 ResponseProcessor.process()
                              ↓
           SessionManager.add_message(response)
                              ↓
                    Database INSERT (messages table)
                              ↓
                         Display to user
```

### Data Flow Diagram

```
┌──────────┐
│  User    │
│  Prompt  │
└────┬─────┘
     │
     ▼
┌────────────────┐     ┌──────────────┐
│  Smart Model   │────▶│  Model       │
│  Selection     │     │  Database    │
└────┬───────────┘     └──────────────┘
     │
     ▼
┌────────────────┐     ┌──────────────┐
│  Template      │────▶│  Template    │
│  Rendering     │     │  Library     │
└────┬───────────┘     └──────────────┘
     │
     ▼
┌────────────────┐     ┌──────────────┐
│  Context       │────▶│  File        │
│  Injection     │     │  System      │
└────┬───────────┘     └──────────────┘
     │
     ▼
┌────────────────┐
│  Model         │
│  Execution     │
│  (llama.cpp    │
│   or API)      │
└────┬───────────┘
     │
     ▼
┌────────────────┐
│  Response      │
│  Processing    │
└────┬───────────┘
     │
     ▼
┌────────────────┐     ┌──────────────┐
│  Session       │────▶│  SQLite      │
│  Storage       │     │  Database    │
└────┬───────────┘     └──────────────┘
     │
     ▼
┌────────────────┐
│  Display to    │
│  User          │
└────────────────┘
```

### Module Dependencies

```python
# Core modules (no dependencies on other project modules)
response_processor.py       # Independent
context_manager.py          # Independent
template_manager.py         # Independent
model_selector.py          # Independent

# Database layer (depends on schema)
session_manager.py         # Requires: schema.sql

# Feature modules (depend on core + database)
model_comparison.py        # Requires: session_manager
batch_processor.py         # Requires: session_manager
analytics_dashboard.py     # Requires: session_manager
workflow_engine.py         # Requires: session_manager, template_manager

# Main application (depends on all modules)
ai-router.py              # Imports all above modules
```

### Design Patterns Used

1. **Singleton Pattern**: `SessionManager` - single database connection
2. **Factory Pattern**: `ModelSelector` - creates model configurations
3. **Strategy Pattern**: `ResponseProcessor` - different formatting strategies
4. **Observer Pattern**: `BatchProcessor` - progress callbacks
5. **Template Method Pattern**: `WorkflowEngine` - workflow execution steps
6. **Repository Pattern**: `SessionManager` - data access abstraction

---

## Project Structure

### Directory Layout

```
D:\models\
├── ai-router.py                    # Main application entry point
├── requirements.txt                # Python dependencies
│
├── Core Modules (Feature Implementation)
├── session_manager.py              # Session & database management
├── template_manager.py             # Template system
├── context_manager.py              # Context injection
├── response_processor.py           # Response formatting
├── model_selector.py               # Smart model selection
├── batch_processor.py              # Batch processing
├── analytics_dashboard.py          # Analytics & reporting
├── workflow_engine.py              # Workflow automation
├── model_comparison.py             # A/B testing
│
├── Database & Schema
├── .ai-router-sessions.db          # SQLite database (runtime)
├── schema.sql                      # Database schema definition
├── analytics_schema.sql            # Analytics tables
├── comparison_schema.sql           # Comparison tracking
├── session_db_setup.py             # Database initialization
├── init_database.py                # Quick DB reset
│
├── Testing
├── test_integration.py             # Master integration tests
├── validate_installation.py        # Installation validator
├── smoke_test.py                   # Quick smoke tests
├── benchmark_features.py           # Performance benchmarks
├── test_compatibility.py           # Cross-platform tests
├── comprehensive_feature_test.py   # Full feature testing
├── tests/                          # Unit tests directory
│   ├── test_session_manager_integration.py
│   ├── test_template_manager_integration.py
│   ├── test_batch_processor_integration.py
│   └── test_workflow_engine_integration.py
│
├── Templates & Workflows
├── prompt-templates/               # YAML template files
│   ├── code-review.yaml
│   ├── research-summary.yaml
│   ├── creative-story.yaml
│   └── ...
├── workflows/                      # Workflow definitions
│   ├── research-and-summarize.yaml
│   └── ...
├── context-templates/              # Context file templates
│   └── ...
│
├── Data Directories (runtime)
├── outputs/                        # Exported files
├── batch_checkpoints/              # Batch job checkpoints
├── comparisons/                    # Model comparison results
├── sessions/                       # Exported sessions
├── logs/                           # Application logs
│
├── Documentation
├── README.md                       # Project overview
├── README-ENHANCED.md              # Enhanced features doc
├── DEVELOPER_GUIDE.md              # This file
├── USER_GUIDE.md                   # End-user documentation
├── FEATURE_DOCUMENTATION.md        # Detailed feature docs
├── TESTING_GUIDE.md                # Testing instructions
├── MIGRATION_GUIDE.md              # Upgrade guide
├── CHANGELOG.md                    # Version history
├── QUICK_START_GUIDE.md            # Quick start for users
├── DEPLOYMENT_CHECKLIST.md         # Production deployment
├── API_REFERENCE.md                # API documentation (if exists)
│
├── Configuration & Scripts
├── .gitignore                      # Git ignore patterns
├── .ai-router-preferences.json     # User preferences (runtime)
├── config-templates.json           # Configuration templates
├── LAUNCH-AI-ROUTER.ps1            # Windows launcher
├── LAUNCH-AI-ROUTER-ENHANCED.ps1   # Enhanced launcher
├── SETUP-ENVIRONMENT.ps1           # Environment setup
│
├── Model-Specific Files
├── model_examples_rtx3090.py       # RTX 3090 model configs
├── MODEL_REFERENCE_GUIDE.md        # Model documentation
├── OPTIMIZED-SYSTEM-PROMPTS-2025-RESEARCH-BASED.txt
│
├── Analysis & Reports
├── CODE-QUALITY-ANALYSIS-100.md    # Code quality report
├── SECURITY-AUDIT-REPORT-100.md    # Security audit
├── PERFORMANCE-OPTIMIZATION-REPORT-100.md
├── DOCUMENTATION-QUALITY-REPORT-100.md
├── FINAL-SYSTEM-STATUS-2025-12-08.md
├── START-HERE-SYSTEM-HEALTH-SUMMARY.md
│
├── Archive (historical/deprecated)
├── archive/                        # Old versions
├── organized/                      # Organized resources
└── bots/                          # Bot configurations (if any)
```

### File Naming Conventions

**Python Modules**:
- `snake_case.py` for all Python files
- Descriptive names: `session_manager.py`, not `sm.py`
- Test files: `test_<module_name>.py`

**Documentation**:
- `UPPER-CASE-WITH-DASHES.md` for guides: `DEVELOPER_GUIDE.md`
- `lowercase-with-dashes.md` for examples: `example-workflow.md`

**Data Files**:
- YAML: `lowercase-with-dashes.yaml`
- JSON: `camelCase.json` or `snake_case.json`
- SQL: `lowercase_schema.sql`

**Directories**:
- `lowercase-with-dashes/` for resource directories
- `lowercase_no_dashes/` for Python package directories

### Module Organization

Each feature module follows this structure:

```python
"""
module_name.py - Brief description

Detailed description of module purpose and capabilities.
"""

# Standard library imports
import os
import sys
from pathlib import Path
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from datetime import datetime

# Third-party imports
import yaml
from jinja2 import Template

# Local imports
from session_manager import SessionManager

# Constants
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3

# Data classes
@dataclass
class FeatureConfig:
    """Configuration for feature"""
    param1: str
    param2: int = 10

# Main class
class FeatureManager:
    """Main class for feature functionality"""

    def __init__(self, config: Optional[FeatureConfig] = None):
        """Initialize feature manager"""
        self.config = config or FeatureConfig()

    def public_method(self, param: str) -> str:
        """Public method with clear docstring"""
        return self._private_method(param)

    def _private_method(self, param: str) -> str:
        """Private method (prefix with underscore)"""
        return f"Processed: {param}"

# Utility functions
def helper_function(data: Dict[str, Any]) -> bool:
    """Standalone helper function"""
    return True

# Main execution (for standalone testing)
if __name__ == "__main__":
    # Quick test code
    manager = FeatureManager()
    result = manager.public_method("test")
    print(result)
```

---

## Core Components Deep Dive

### 1. Session Manager (`session_manager.py`)

**Purpose**: Manage persistent conversation storage and retrieval.

**Key Classes**:

```python
class SessionManager:
    """
    Handles all database operations for sessions and messages.

    Responsibilities:
    - CRUD operations on sessions and messages
    - Search and filtering
    - Export functionality
    - Statistics and analytics data gathering
    """

    def __init__(self, db_path: Path):
        """Initialize with database path"""
        self.db_path = db_path
        self.conn = self._connect()

    # Core operations
    def create_session(self, model_id: str, model_name: str,
                       title: Optional[str] = None) -> str:
        """Create new session, return session_id"""

    def add_message(self, session_id: str, role: str, content: str,
                   tokens_used: Optional[int] = None,
                   duration_seconds: Optional[float] = None) -> str:
        """Add message to session, return message_id"""

    def get_session(self, session_id: str) -> Optional[Dict]:
        """Retrieve session metadata"""

    def get_messages(self, session_id: str) -> List[Dict]:
        """Retrieve all messages in session"""

    # Search and filtering
    def search_sessions(self, query: str) -> List[Dict]:
        """Full-text search across sessions and messages"""

    def get_sessions_by_tag(self, tag: str) -> List[Dict]:
        """Filter sessions by tag"""

    # Tagging
    def add_tag(self, session_id: str, tag: str) -> None:
        """Add tag to session"""

    def get_all_tags(self) -> List[Tuple[str, int]]:
        """Get all tags with usage counts"""

    # Export
    def export_session(self, session_id: str,
                       format: str = "json") -> Dict[str, Any]:
        """Export session in specified format"""
```

**Database Interaction Pattern**:

```python
def create_session(self, model_id: str, model_name: str,
                   title: Optional[str] = None) -> str:
    """Create new session"""
    import uuid
    from datetime import datetime

    session_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()

    # Auto-generate title if not provided
    if not title:
        title = f"Session {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    # Execute INSERT
    cursor = self.conn.cursor()
    cursor.execute("""
        INSERT INTO sessions (
            session_id, title, model_id, model_name,
            created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, (session_id, title, model_id, model_name, timestamp, timestamp))

    self.conn.commit()
    return session_id
```

**Testing Pattern**:

```python
# tests/test_session_manager.py
import unittest
from session_manager import SessionManager
from pathlib import Path

class TestSessionManager(unittest.TestCase):
    def setUp(self):
        """Create test database before each test"""
        self.db_path = Path("test_sessions.db")
        self.manager = SessionManager(self.db_path)

    def tearDown(self):
        """Clean up test database after each test"""
        if self.db_path.exists():
            self.db_path.unlink()

    def test_create_session(self):
        """Test session creation"""
        session_id = self.manager.create_session(
            model_id="test-model",
            model_name="Test Model",
            title="Test Session"
        )

        self.assertIsNotNone(session_id)

        # Verify session was created
        session = self.manager.get_session(session_id)
        self.assertEqual(session['title'], "Test Session")
        self.assertEqual(session['model_id'], "test-model")
```

### 2. Template Manager (`template_manager.py`)

**Purpose**: Load, render, and manage YAML+Jinja2 prompt templates.

**Key Classes**:

```python
class TemplateManager:
    """
    Manages prompt template library with variable substitution.

    Template Structure:
    - metadata: name, description, version, author, tags
    - variables: list of template variables with defaults
    - system_prompt: system message template
    - user_prompt: user message template
    """

    def __init__(self, templates_dir: Path):
        """Initialize with templates directory"""
        self.templates_dir = templates_dir
        self._template_cache = {}

    def load_template(self, template_name: str) -> 'Template':
        """Load template from YAML file"""

    def list_templates(self, category: Optional[str] = None) -> List[Dict]:
        """List all available templates"""

    def render_template(self, template_name: str,
                        variables: Dict[str, Any]) -> Dict[str, str]:
        """Render template with provided variables"""

    def create_template(self, template_data: Dict[str, Any],
                       filename: str) -> None:
        """Create new template file"""

    def validate_template(self, template_name: str) -> Tuple[bool, List[str]]:
        """Validate template syntax and structure"""
```

**Template Loading**:

```python
def load_template(self, template_name: str) -> Dict[str, Any]:
    """Load and parse YAML template"""
    import yaml

    # Check cache first
    if template_name in self._template_cache:
        return self._template_cache[template_name]

    # Construct file path
    template_path = self.templates_dir / f"{template_name}.yaml"

    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_name}")

    # Load YAML
    with open(template_path, 'r', encoding='utf-8') as f:
        template_data = yaml.safe_load(f)

    # Validate structure
    required_keys = ['metadata', 'user_prompt']
    for key in required_keys:
        if key not in template_data:
            raise ValueError(f"Template missing required key: {key}")

    # Cache for future use
    self._template_cache[template_name] = template_data

    return template_data
```

**Template Rendering**:

```python
def render_template(self, template_name: str,
                   variables: Dict[str, Any]) -> Dict[str, str]:
    """Render template with Jinja2"""
    from jinja2 import Template

    # Load template
    template_data = self.load_template(template_name)

    # Get variable defaults
    defaults = {}
    for var in template_data.get('metadata', {}).get('variables', []):
        if 'default' in var:
            defaults[var['name']] = var['default']

    # Merge defaults with provided variables
    render_vars = {**defaults, **variables}

    # Render system prompt (if exists)
    system_prompt = None
    if 'system_prompt' in template_data:
        system_template = Template(template_data['system_prompt'])
        system_prompt = system_template.render(**render_vars)

    # Render user prompt
    user_template = Template(template_data['user_prompt'])
    user_prompt = user_template.render(**render_vars)

    return {
        'system_prompt': system_prompt,
        'user_prompt': user_prompt,
        'metadata': template_data.get('metadata', {})
    }
```

### 3. Context Manager (`context_manager.py`)

**Purpose**: Inject file contents, URLs, and code into conversations.

**Key Methods**:

```python
class ContextManager:
    """
    Manages context injection from various sources.

    Supported sources:
    - Files (text, code, markdown)
    - Directories (multiple files)
    - URLs (fetch and parse)
    - Code snippets
    - Raw text
    """

    def add_file_context(self, file_path: Path) -> Dict[str, Any]:
        """Load file content and estimate tokens"""

    def add_directory_context(self, dir_path: Path,
                              file_pattern: str = "*") -> List[Dict]:
        """Load multiple files from directory"""

    def add_url_context(self, url: str) -> Dict[str, Any]:
        """Fetch and parse URL content"""

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text"""

    def get_combined_context(self, max_tokens: Optional[int] = None) -> str:
        """Get all context combined, truncated to max_tokens"""
```

**Token Estimation**:

```python
def estimate_tokens(self, text: str) -> int:
    """
    Estimate token count using simple heuristic.

    More accurate: Use tiktoken library
    Quick estimate: ~1.3 tokens per word
    """
    # Simple word-based estimate
    words = len(text.split())
    estimated_tokens = int(words * 1.3)

    # Adjust for code (more tokens per word)
    if self._is_code(text):
        estimated_tokens = int(words * 1.5)

    return estimated_tokens

def _is_code(self, text: str) -> bool:
    """Heuristic to detect if text is code"""
    code_indicators = ['def ', 'class ', 'import ', 'function ', 'const ', 'var ']
    return any(indicator in text for indicator in code_indicators)
```

### 4. Batch Processor (`batch_processor.py`)

**Purpose**: Execute multiple prompts with progress tracking and checkpointing.

**Key Classes**:

```python
@dataclass
class BatchJob:
    """Batch job configuration"""
    job_id: str
    model_id: str
    prompts: List[str]
    created_at: datetime
    status: str = "pending"  # pending, running, paused, completed, failed

@dataclass
class BatchResult:
    """Result for single prompt in batch"""
    prompt: str
    response: str
    duration: float
    tokens: int
    success: bool
    error: Optional[str] = None

class BatchProcessor:
    """
    Process multiple prompts with checkpointing.

    Features:
    - Progress tracking
    - Checkpoint save/resume
    - Error handling and retry
    - Parallel processing (optional)
    - Result aggregation
    """

    def create_job(self, model_id: str,
                   prompts: List[str]) -> BatchJob:
        """Create new batch job"""

    def execute_batch(self, job: BatchJob,
                     progress_callback: Optional[Callable] = None,
                     checkpoint_interval: int = 5) -> List[BatchResult]:
        """Execute batch job with checkpointing"""

    def save_checkpoint(self, job: BatchJob,
                       completed_results: List[BatchResult]) -> None:
        """Save current progress"""

    def load_checkpoint(self, job_id: str) -> Tuple[BatchJob, List[BatchResult]]:
        """Resume from checkpoint"""
```

**Checkpoint Pattern**:

```python
def execute_batch(self, job: BatchJob,
                 progress_callback: Optional[Callable] = None,
                 checkpoint_interval: int = 5) -> List[BatchResult]:
    """Execute batch with automatic checkpointing"""
    results = []

    for i, prompt in enumerate(job.prompts):
        # Execute single prompt
        try:
            result = self._execute_single(job.model_id, prompt)
            results.append(result)

            # Progress callback
            if progress_callback:
                progress_callback(i + 1, len(job.prompts))

            # Checkpoint at intervals
            if (i + 1) % checkpoint_interval == 0:
                self.save_checkpoint(job, results)

        except Exception as e:
            # Record error and continue
            results.append(BatchResult(
                prompt=prompt,
                response="",
                duration=0,
                tokens=0,
                success=False,
                error=str(e)
            ))

    # Final checkpoint
    job.status = "completed"
    self.save_checkpoint(job, results)

    return results

def save_checkpoint(self, job: BatchJob,
                   results: List[BatchResult]) -> None:
    """Save checkpoint to disk"""
    import json

    checkpoint_path = self.checkpoint_dir / f"{job.job_id}.json"

    checkpoint_data = {
        'job': {
            'job_id': job.job_id,
            'model_id': job.model_id,
            'total_prompts': len(job.prompts),
            'status': job.status,
            'created_at': job.created_at.isoformat()
        },
        'completed': len(results),
        'results': [
            {
                'prompt': r.prompt,
                'response': r.response,
                'duration': r.duration,
                'tokens': r.tokens,
                'success': r.success,
                'error': r.error
            }
            for r in results
        ]
    }

    with open(checkpoint_path, 'w', encoding='utf-8') as f:
        json.dump(checkpoint_data, f, indent=2)
```

### 5. Model Selector (`model_selector.py`)

**Purpose**: Intelligently recommend models based on task analysis.

**Selection Algorithm**:

```python
class ModelSelector:
    """
    AI-powered model recommendation system.

    Selection criteria:
    1. Keyword analysis (detect task type)
    2. Model capabilities matching
    3. User preference history
    4. Performance metrics
    5. Resource availability
    """

    def select_model(self, prompt: str,
                    available_models: List[str]) -> Dict[str, Any]:
        """Recommend best model for prompt"""

        # 1. Analyze prompt
        task_type = self._analyze_prompt(prompt)

        # 2. Get model capabilities
        candidates = self._filter_by_capability(available_models, task_type)

        # 3. Apply user preferences
        candidates = self._apply_preferences(candidates, task_type)

        # 4. Rank by performance
        ranked = self._rank_by_performance(candidates)

        # 5. Return top recommendation
        return {
            'model_id': ranked[0]['model_id'],
            'confidence': ranked[0]['score'],
            'reasons': ranked[0]['reasons'],
            'alternatives': ranked[1:3]
        }

    def _analyze_prompt(self, prompt: str) -> str:
        """Detect task type from keywords"""
        prompt_lower = prompt.lower()

        # Coding keywords
        coding_keywords = [
            'code', 'function', 'class', 'bug', 'debug',
            'algorithm', 'implement', 'python', 'javascript'
        ]
        if any(kw in prompt_lower for kw in coding_keywords):
            return 'coding'

        # Math keywords
        math_keywords = [
            'calculate', 'solve', 'equation', 'proof',
            'theorem', 'derivative', 'integral'
        ]
        if any(kw in prompt_lower for kw in math_keywords):
            return 'math'

        # Creative keywords
        creative_keywords = [
            'story', 'write', 'creative', 'poem',
            'narrative', 'fiction', 'character'
        ]
        if any(kw in prompt_lower for kw in creative_keywords):
            return 'creative'

        # Default to general
        return 'general'
```

---

## Development Workflow

### Branch Strategy

**Main Branches**:
- `main` - Production-ready code
- `develop` - Integration branch for features

**Feature Branches**:
- `feature/feature-name` - New features
- `bugfix/issue-description` - Bug fixes
- `hotfix/critical-fix` - Emergency fixes
- `docs/documentation-update` - Documentation only

### Development Cycle

```bash
# 1. Start new feature
git checkout develop
git pull origin develop
git checkout -b feature/new-feature

# 2. Develop feature
# ... write code ...
# ... write tests ...
# ... update documentation ...

# 3. Test locally
python test_integration.py
python validate_installation.py

# 4. Commit with clear message
git add .
git commit -m "Add: Implement new feature XYZ

- Add core functionality
- Add unit tests
- Update documentation
- Add example usage"

# 5. Push and create PR
git push origin feature/new-feature

# 6. Create Pull Request on GitHub
# - Target: develop branch
# - Add description
# - Request review

# 7. Address review feedback
# ... make changes ...
git add .
git commit -m "Fix: Address review feedback"
git push origin feature/new-feature

# 8. Merge (after approval)
# Maintainer merges to develop

# 9. Clean up
git checkout develop
git pull origin develop
git branch -d feature/new-feature
```

### Commit Message Format

Follow conventional commits:

```
<type>: <subject>

<body>

<footer>
```

**Types**:
- `Add:` - New feature
- `Fix:` - Bug fix
- `Update:` - Update existing feature
- `Refactor:` - Code refactoring
- `Docs:` - Documentation only
- `Test:` - Test updates
- `Chore:` - Maintenance tasks

**Examples**:

```
Add: Implement session export to PDF

- Add PDF export functionality to SessionManager
- Add dependencies: reportlab, pypdf
- Add unit tests for PDF export
- Update USER_GUIDE.md with export examples

Closes #123
```

```
Fix: Resolve database locking issue in batch processing

The batch processor was keeping database connections open,
causing "database locked" errors. Changed to use connection
pooling and proper connection cleanup.

Fixes #456
```

### Code Review Checklist

**Before Requesting Review**:
- [ ] All tests pass locally
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] Code follows style guide
- [ ] No debugging code left (print statements, etc.)
- [ ] Commit messages are clear
- [ ] PR description explains changes

**Reviewer Checklist**:
- [ ] Code solves the stated problem
- [ ] Tests are comprehensive
- [ ] No security vulnerabilities
- [ ] Performance considerations addressed
- [ ] Error handling is robust
- [ ] Code is maintainable
- [ ] Documentation is clear
- [ ] Breaking changes are documented

---

## Code Standards and Style Guide

### Python Style Guide (PEP 8 + Project Conventions)

**Line Length**: 100 characters (not 79)

**Indentation**: 4 spaces (no tabs)

**Imports**:
```python
# Standard library (alphabetical)
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any

# Third-party (alphabetical)
import yaml
from jinja2 import Template

# Local (alphabetical)
from session_manager import SessionManager
from template_manager import TemplateManager
```

**Naming Conventions**:
```python
# Classes: PascalCase
class SessionManager:
    pass

# Functions and methods: snake_case
def create_session():
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30

# Private methods: prefix with underscore
def _internal_helper():
    pass

# Variables: snake_case
user_input = "test"
session_id = "abc123"
```

**Type Hints**:
```python
# Always use type hints for function signatures
def create_session(
    model_id: str,
    model_name: str,
    title: Optional[str] = None
) -> str:
    """Create new session"""
    pass

# Use from typing for complex types
from typing import Optional, Dict, List, Any, Callable, Union

def process_data(
    data: Dict[str, Any],
    callback: Optional[Callable[[int], None]] = None
) -> List[str]:
    pass
```

**Docstrings** (Google Style):
```python
def complex_function(param1: str, param2: int = 10) -> Dict[str, Any]:
    """
    Brief one-line description.

    Longer description explaining the function's purpose,
    behavior, and any important details.

    Args:
        param1: Description of param1
        param2: Description of param2 (default: 10)

    Returns:
        Dictionary containing:
        - key1: Description
        - key2: Description

    Raises:
        ValueError: If param1 is empty
        FileNotFoundError: If file doesn't exist

    Example:
        >>> result = complex_function("test", 20)
        >>> print(result['key1'])
        'value'
    """
    pass
```

**Error Handling**:
```python
# Specific exceptions
try:
    result = risky_operation()
except FileNotFoundError as e:
    logger.error(f"File not found: {e}")
    raise
except ValueError as e:
    logger.warning(f"Invalid value: {e}")
    return default_value
except Exception as e:
    logger.exception("Unexpected error")
    raise

# Custom exceptions
class SessionNotFoundError(Exception):
    """Raised when session ID doesn't exist"""
    pass

# Use context managers
with open(file_path, 'r') as f:
    content = f.read()
```

### Code Quality Tools

**Black** (Code Formatter):
```bash
# Format all Python files
black . --line-length 100

# Check without modifying
black . --check --line-length 100

# Format specific file
black ai-router.py --line-length 100
```

**Flake8** (Linter):
```bash
# Lint all files
flake8 . --max-line-length=100 --extend-ignore=E203,W503

# Lint specific file
flake8 ai-router.py --max-line-length=100
```

**MyPy** (Type Checker):
```bash
# Type check all files
mypy . --ignore-missing-imports

# Type check specific file
mypy ai-router.py --ignore-missing-imports
```

**Pylint** (Advanced Linter):
```bash
# Full lint with pylint
pylint ai-router.py --max-line-length=100

# Generate config
pylint --generate-rcfile > .pylintrc
```

### Pre-Commit Configuration

Create `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        args: [--line-length=100]

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=100, --extend-ignore=E203,W503]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
        args: [--ignore-missing-imports]
```

Install and run:
```bash
# Install pre-commit
pip install pre-commit

# Install git hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

---

## Adding New Features

### Step-by-Step Guide

#### Phase 1: Planning

1. **Define Requirements**
   - What problem does this solve?
   - Who are the users?
   - What are the inputs and outputs?
   - What are the edge cases?

2. **Design API**
   - What classes/functions are needed?
   - What are the method signatures?
   - How does it integrate with existing code?

3. **Write Specification**
   - Create issue or RFC document
   - Get feedback from maintainers
   - Update based on feedback

#### Phase 2: Implementation

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/new-feature
   ```

2. **Create Module File**
   ```bash
   touch new_feature.py
   ```

3. **Implement Core Functionality**
   ```python
   """
   new_feature.py - Brief description

   Detailed description of feature.
   """

   from pathlib import Path
   from typing import Optional, Dict, Any
   from dataclasses import dataclass

   @dataclass
   class NewFeatureConfig:
       """Configuration for new feature"""
       param1: str
       param2: int = 10

   class NewFeatureManager:
       """Main class for new feature"""

       def __init__(self, config: Optional[NewFeatureConfig] = None):
           """Initialize feature"""
           self.config = config or NewFeatureConfig()

       def main_method(self, input_data: str) -> Dict[str, Any]:
           """Main public method"""
           # Implementation
           pass
   ```

4. **Add Database Schema** (if needed)
   ```sql
   -- In schema.sql or new_feature_schema.sql
   CREATE TABLE IF NOT EXISTS new_feature_data (
       id TEXT PRIMARY KEY,
       data TEXT NOT NULL,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );

   CREATE INDEX IF NOT EXISTS idx_new_feature_created
   ON new_feature_data(created_at);
   ```

5. **Integrate with Main Application**
   ```python
   # In ai-router.py
   from new_feature import NewFeatureManager

   # In AIRouter class
   def __init__(self):
       # ... existing code ...
       self.new_feature = NewFeatureManager()

   def menu_new_feature(self):
       """Menu option for new feature"""
       # Implementation
       pass
   ```

#### Phase 3: Testing

1. **Create Unit Tests**
   ```python
   # tests/test_new_feature.py
   import unittest
   from new_feature import NewFeatureManager

   class TestNewFeature(unittest.TestCase):
       def setUp(self):
           self.manager = NewFeatureManager()

       def test_main_method(self):
           result = self.manager.main_method("test")
           self.assertIsNotNone(result)
   ```

2. **Add Integration Test**
   ```python
   # In test_integration.py
   def test_new_feature_integration(self):
       """Test new feature integration"""
       # Implementation
       pass
   ```

3. **Run Tests**
   ```bash
   python -m pytest tests/test_new_feature.py -v
   python test_integration.py
   ```

#### Phase 4: Documentation

1. **Add Docstrings** (already done in code)

2. **Update FEATURE_DOCUMENTATION.md**
   ```markdown
   ## 10. New Feature Name

   ### Overview
   Brief description...

   ### Key Capabilities
   - Capability 1
   - Capability 2

   ### Usage Examples
   ...code examples...
   ```

3. **Update USER_GUIDE.md**
   ```markdown
   ### Feature X: New Feature

   **How to Use**:
   1. Step 1
   2. Step 2
   ...
   ```

4. **Update README.md** (if major feature)

#### Phase 5: Review and Merge

1. **Self-Review**
   - Run all tests
   - Check code style
   - Review documentation
   - Test edge cases

2. **Commit and Push**
   ```bash
   git add .
   git commit -m "Add: Implement new feature

   - Core functionality
   - Unit tests
   - Integration tests
   - Documentation

   Closes #XXX"

   git push origin feature/new-feature
   ```

3. **Create Pull Request**
   - Clear title and description
   - Link to issue
   - Add screenshots/examples
   - Request reviewers

4. **Address Feedback**
   - Make requested changes
   - Update tests if needed
   - Push updates

5. **Merge** (after approval)

### Example: Adding a New Menu Option

Let's add a "Session Statistics" menu option:

**1. Add Menu Method**:
```python
# In ai-router.py, AIRouter class
def menu_session_statistics(self):
    """Display detailed session statistics"""
    print(f"\n{Colors.CYAN}{'=' * 60}")
    print(f"  SESSION STATISTICS")
    print(f"{'=' * 60}{Colors.RESET}\n")

    # Get all sessions
    sessions = self.session_manager.list_sessions(limit=None)

    if not sessions:
        print("No sessions found.")
        return

    # Calculate statistics
    total_sessions = len(sessions)
    total_messages = sum(s['message_count'] for s in sessions)
    total_tokens = sum(s.get('total_tokens', 0) for s in sessions)

    # Display
    print(f"Total Sessions: {total_sessions}")
    print(f"Total Messages: {total_messages}")
    print(f"Total Tokens: {total_tokens:,}")
    print(f"Avg Messages/Session: {total_messages / total_sessions:.1f}")

    # Top models
    model_counts = {}
    for session in sessions:
        model = session.get('model_name', 'Unknown')
        model_counts[model] = model_counts.get(model, 0) + 1

    print(f"\n{Colors.BOLD}Top Models:{Colors.RESET}")
    for model, count in sorted(
        model_counts.items(),
        key=lambda x: x[1],
        reverse=True
    )[:5]:
        print(f"  {model}: {count} sessions")

    input(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")
```

**2. Add to Main Menu**:
```python
# In display_main_menu method
def display_main_menu(self):
    """Display main menu"""
    # ... existing options ...
    print(f"{Colors.GREEN}[10]{Colors.RESET} Session Statistics")
    # ... rest of menu ...

# In run method
def run(self):
    while True:
        self.display_main_menu()
        choice = input(f"\n{Colors.BOLD}Enter choice: {Colors.RESET}")

        if choice == "10":
            self.menu_session_statistics()
        # ... other options ...
```

**3. Add Test**:
```python
# In test_integration.py
def test_session_statistics():
    """Test session statistics feature"""
    # Create test sessions
    session_manager = SessionManager(Path("test_stats.db"))

    # Add sample data
    for i in range(5):
        session_id = session_manager.create_session(
            model_id="test-model",
            model_name="Test Model",
            title=f"Session {i}"
        )
        session_manager.add_message(
            session_id, "user", f"Message {i}", tokens_used=10
        )

    # Test statistics calculation
    sessions = session_manager.list_sessions(limit=None)
    assert len(sessions) == 5

    # Cleanup
    Path("test_stats.db").unlink()
```

### Example: Adding a New Provider

Let's add support for Google Gemini API:

**1. Add Provider Configuration**:
```python
# In ai-router.py, ModelDatabase class
CLOUD_PROVIDERS = {
    # ... existing providers ...
    "gemini-pro": {
        "name": "Google Gemini Pro",
        "provider": "google",
        "api_endpoint": "https://generativelanguage.googleapis.com/v1beta",
        "model_id": "gemini-pro",
        "max_tokens": 30720,
        "pricing": {
            "input": 0.00025,   # per 1K tokens
            "output": 0.0005
        },
        "requires_api_key": "GOOGLE_API_KEY"
    }
}
```

**2. Implement API Client**:
```python
# Create providers/google_client.py
"""
google_client.py - Google Gemini API client
"""

import os
import requests
from typing import Dict, Any, Optional

class GoogleGeminiClient:
    """Client for Google Gemini API"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize client"""
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not set")

        self.base_url = "https://generativelanguage.googleapis.com/v1beta"

    def generate(self, prompt: str, model: str = "gemini-pro",
                max_tokens: int = 2048, temperature: float = 0.7) -> Dict[str, Any]:
        """Generate completion"""

        url = f"{self.base_url}/models/{model}:generateContent"

        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        }

        headers = {
            "Content-Type": "application/json"
        }

        params = {
            "key": self.api_key
        }

        response = requests.post(
            url,
            json=payload,
            headers=headers,
            params=params,
            timeout=60
        )

        response.raise_for_status()

        data = response.json()

        # Extract response text
        candidates = data.get('candidates', [])
        if not candidates:
            raise ValueError("No response from API")

        content = candidates[0].get('content', {})
        parts = content.get('parts', [])
        response_text = parts[0].get('text', '') if parts else ''

        # Extract token counts
        usage = data.get('usageMetadata', {})
        prompt_tokens = usage.get('promptTokenCount', 0)
        completion_tokens = usage.get('candidatesTokenCount', 0)

        return {
            'response': response_text,
            'tokens_input': prompt_tokens,
            'tokens_output': completion_tokens,
            'total_tokens': prompt_tokens + completion_tokens
        }
```

**3. Integrate into AIRouter**:
```python
# In ai-router.py
from providers.google_client import GoogleGeminiClient

class AIRouter:
    def __init__(self):
        # ... existing code ...
        self.google_client = None

        # Initialize if API key exists
        if os.getenv('GOOGLE_API_KEY'):
            try:
                self.google_client = GoogleGeminiClient()
            except Exception as e:
                logger.warning(f"Google client initialization failed: {e}")

    def execute_model(self, model_id: str, prompt: str,
                     system_prompt: Optional[str] = None) -> ModelResponse:
        """Execute model - updated to support Google"""

        # Check if Google model
        if model_id.startswith('gemini-'):
            if not self.google_client:
                raise ValueError("Google API key not configured")

            # Combine system prompt and user prompt
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"

            # Execute
            start_time = time.time()
            result = self.google_client.generate(
                prompt=full_prompt,
                model=model_id
            )
            duration = time.time() - start_time

            return ModelResponse(
                text=result['response'],
                model_id=model_id,
                model_name=f"Google {model_id}",
                tokens_input=result['tokens_input'],
                tokens_output=result['tokens_output'],
                duration_seconds=duration
            )

        # ... existing provider logic ...
```

**4. Add Tests**:
```python
# tests/test_google_provider.py
import unittest
from unittest.mock import Mock, patch
from providers.google_client import GoogleGeminiClient

class TestGoogleProvider(unittest.TestCase):
    @patch('providers.google_client.requests.post')
    def test_generate(self, mock_post):
        """Test Google Gemini API call"""

        # Mock response
        mock_post.return_value.json.return_value = {
            'candidates': [{
                'content': {
                    'parts': [{'text': 'Test response'}]
                }
            }],
            'usageMetadata': {
                'promptTokenCount': 10,
                'candidatesTokenCount': 5
            }
        }
        mock_post.return_value.raise_for_status = Mock()

        # Test
        client = GoogleGeminiClient(api_key="test-key")
        result = client.generate("Test prompt")

        # Assertions
        self.assertEqual(result['response'], 'Test response')
        self.assertEqual(result['tokens_input'], 10)
        self.assertEqual(result['tokens_output'], 5)
```

**5. Update Documentation**:
```markdown
# In README.md or PROVIDER_GUIDE.md

## Supported Providers

### Google Gemini

**Setup**:
1. Get API key from https://makersuite.google.com/app/apikey
2. Set environment variable:
   ```bash
   export GOOGLE_API_KEY="your_key_here"
   ```
3. Available models:
   - `gemini-pro` - General purpose
   - `gemini-pro-vision` - Multimodal (coming soon)

**Usage**:
```bash
# Via AI Router
python ai-router.py
# Select: [3] Cloud Models
# Choose: Google Gemini Pro
```

**Pricing**: $0.00025 per 1K input tokens, $0.0005 per 1K output tokens
```

---

## Testing Guide

### Testing Philosophy

1. **Test Coverage**: Aim for 80%+ code coverage
2. **Test Pyramid**: Many unit tests, some integration tests, few E2E tests
3. **Fast Tests**: Unit tests should run in milliseconds
4. **Isolated Tests**: Tests should not depend on each other
5. **Readable Tests**: Tests are documentation

### Test Structure

```
tests/
├── __init__.py
├── unit/                          # Unit tests
│   ├── test_session_manager.py
│   ├── test_template_manager.py
│   ├── test_context_manager.py
│   └── ...
├── integration/                   # Integration tests
│   ├── test_session_template_integration.py
│   ├── test_batch_workflow_integration.py
│   └── ...
└── e2e/                          # End-to-end tests
    ├── test_full_session_flow.py
    └── test_batch_processing_flow.py
```

### Unit Test Template

```python
"""
tests/unit/test_new_feature.py - Unit tests for new feature
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import os

from new_feature import NewFeatureManager, NewFeatureConfig

class TestNewFeatureManager(unittest.TestCase):
    """Unit tests for NewFeatureManager"""

    def setUp(self):
        """Set up test fixtures before each test"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = NewFeatureConfig(param1="test", param2=20)
        self.manager = NewFeatureManager(self.config)

    def tearDown(self):
        """Clean up after each test"""
        # Remove temporary files
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_initialization(self):
        """Test manager initialization"""
        self.assertIsNotNone(self.manager)
        self.assertEqual(self.manager.config.param1, "test")
        self.assertEqual(self.manager.config.param2, 20)

    def test_initialization_with_defaults(self):
        """Test initialization with default config"""
        manager = NewFeatureManager()
        self.assertIsNotNone(manager.config)
        self.assertEqual(manager.config.param2, 10)  # Default value

    def test_main_method_success(self):
        """Test main method with valid input"""
        result = self.manager.main_method("valid input")

        self.assertIsNotNone(result)
        self.assertIn('key1', result)
        self.assertEqual(result['status'], 'success')

    def test_main_method_empty_input(self):
        """Test main method with empty input"""
        with self.assertRaises(ValueError) as context:
            self.manager.main_method("")

        self.assertIn("input cannot be empty", str(context.exception))

    @patch('new_feature.external_dependency')
    def test_method_with_external_dependency(self, mock_dependency):
        """Test method that uses external dependency"""
        # Mock the external dependency
        mock_dependency.return_value = "mocked result"

        # Call method
        result = self.manager.method_using_dependency()

        # Assert dependency was called
        mock_dependency.assert_called_once()

        # Assert result
        self.assertEqual(result, "mocked result")

    def test_private_method(self):
        """Test private helper method"""
        # Test private methods by calling them directly
        result = self.manager._private_helper("test")
        self.assertIsNotNone(result)

class TestNewFeatureConfig(unittest.TestCase):
    """Unit tests for NewFeatureConfig dataclass"""

    def test_config_creation(self):
        """Test config creation"""
        config = NewFeatureConfig(param1="test")

        self.assertEqual(config.param1, "test")
        self.assertEqual(config.param2, 10)  # Default

    def test_config_validation(self):
        """Test config validation"""
        # Test invalid config raises error
        with self.assertRaises(TypeError):
            # Missing required param1
            config = NewFeatureConfig()

if __name__ == '__main__':
    unittest.main()
```

### Integration Test Template

```python
"""
tests/integration/test_feature_integration.py - Integration tests
"""

import unittest
from pathlib import Path
import tempfile
import shutil

from session_manager import SessionManager
from new_feature import NewFeatureManager

class TestFeatureIntegration(unittest.TestCase):
    """Integration tests for feature with session manager"""

    @classmethod
    def setUpClass(cls):
        """Set up once before all tests"""
        cls.temp_dir = tempfile.mkdtemp()

    @classmethod
    def tearDownClass(cls):
        """Clean up once after all tests"""
        if Path(cls.temp_dir).exists():
            shutil.rmtree(cls.temp_dir)

    def setUp(self):
        """Set up before each test"""
        self.db_path = Path(self.temp_dir) / "test_integration.db"
        self.session_manager = SessionManager(self.db_path)
        self.feature_manager = NewFeatureManager()

    def tearDown(self):
        """Clean up after each test"""
        if self.db_path.exists():
            self.db_path.unlink()

    def test_feature_with_session(self):
        """Test feature integration with session manager"""
        # Create session
        session_id = self.session_manager.create_session(
            model_id="test-model",
            model_name="Test Model"
        )

        # Use feature
        result = self.feature_manager.process_with_session(
            session_id,
            data="test data"
        )

        # Verify result stored in session
        session = self.session_manager.get_session(session_id)
        self.assertIsNotNone(session)

        # Verify feature data
        self.assertEqual(result['status'], 'success')

    def test_end_to_end_workflow(self):
        """Test complete workflow from start to finish"""
        # 1. Create session
        session_id = self.session_manager.create_session(
            model_id="test-model",
            model_name="Test Model"
        )

        # 2. Process data with feature
        result1 = self.feature_manager.main_method("input 1")

        # 3. Store in session
        self.session_manager.add_message(
            session_id, "user", "input 1", tokens_used=10
        )
        self.session_manager.add_message(
            session_id, "assistant", result1['output'], tokens_used=50
        )

        # 4. Continue processing
        result2 = self.feature_manager.main_method("input 2")
        self.session_manager.add_message(
            session_id, "user", "input 2", tokens_used=10
        )
        self.session_manager.add_message(
            session_id, "assistant", result2['output'], tokens_used=45
        )

        # 5. Verify complete session
        messages = self.session_manager.get_messages(session_id)
        self.assertEqual(len(messages), 4)  # 2 user + 2 assistant

        # 6. Verify statistics
        stats = self.session_manager.get_session_statistics(session_id)
        self.assertEqual(stats['total_messages'], 4)
        self.assertEqual(stats['total_tokens'], 115)  # 10+50+10+45

if __name__ == '__main__':
    unittest.main()
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/unit/test_new_feature.py -v

# Run specific test class
python -m pytest tests/unit/test_new_feature.py::TestNewFeatureManager -v

# Run specific test method
python -m pytest tests/unit/test_new_feature.py::TestNewFeatureManager::test_main_method_success -v

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html

# Run integration tests only
python -m pytest tests/integration/ -v

# Run with verbose output
python -m pytest tests/ -vv

# Stop on first failure
python -m pytest tests/ -x

# Run in parallel (with pytest-xdist)
python -m pytest tests/ -n 4
```

### Test Coverage

```bash
# Generate coverage report
python -m pytest tests/ --cov=. --cov-report=html --cov-report=term

# View HTML report
# Open htmlcov/index.html in browser

# Generate coverage badge (requires coverage-badge)
coverage-badge -o coverage.svg -f
```

### Mocking External Dependencies

```python
# Mock file system
@patch('pathlib.Path.exists')
def test_with_mocked_file(self, mock_exists):
    mock_exists.return_value = True
    # Test code

# Mock HTTP requests
@patch('requests.get')
def test_with_mocked_api(self, mock_get):
    mock_get.return_value.json.return_value = {'key': 'value'}
    mock_get.return_value.status_code = 200
    # Test code

# Mock database
@patch('sqlite3.connect')
def test_with_mocked_db(self, mock_connect):
    mock_cursor = MagicMock()
    mock_connect.return_value.cursor.return_value = mock_cursor
    # Test code

# Mock environment variables
@patch.dict(os.environ, {'API_KEY': 'test_key'})
def test_with_env_var(self):
    # Test code that uses os.getenv('API_KEY')
```

---

## Database Development

### Schema Design Principles

1. **Normalization**: Avoid data duplication
2. **Indexes**: Index foreign keys and frequently queried columns
3. **Timestamps**: Always include `created_at` and `updated_at`
4. **Cascade**: Use `ON DELETE CASCADE` where appropriate
5. **Constraints**: Use CHECK constraints for data validation

### Adding a New Table

**1. Design Schema**:
```sql
-- new_feature_data.sql
CREATE TABLE IF NOT EXISTS new_feature_data (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    feature_type TEXT NOT NULL CHECK(feature_type IN ('type1', 'type2')),
    data TEXT NOT NULL,
    metadata TEXT,  -- JSON
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_new_feature_session
ON new_feature_data(session_id);

CREATE INDEX IF NOT EXISTS idx_new_feature_status
ON new_feature_data(status);

CREATE INDEX IF NOT EXISTS idx_new_feature_created
ON new_feature_data(created_at);

-- Trigger for updated_at
CREATE TRIGGER IF NOT EXISTS update_new_feature_timestamp
AFTER UPDATE ON new_feature_data
BEGIN
    UPDATE new_feature_data SET updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END;
```

**2. Add to schema.sql** or create separate file

**3. Create Migration**:
```python
# migration_add_new_feature_table.py
"""
Migration: Add new_feature_data table

Adds table and indexes for new feature.
"""

import sqlite3
from pathlib import Path

def upgrade(db_path: Path):
    """Apply migration"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Read schema
    with open('new_feature_data.sql', 'r') as f:
        schema = f.read()

    # Execute schema
    cursor.executescript(schema)

    conn.commit()
    conn.close()

    print("Migration applied successfully")

def downgrade(db_path: Path):
    """Rollback migration"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Drop table
    cursor.execute("DROP TABLE IF EXISTS new_feature_data")

    conn.commit()
    conn.close()

    print("Migration rolled back")

if __name__ == "__main__":
    # Test migration
    test_db = Path("test_migration.db")

    print("Testing upgrade...")
    upgrade(test_db)

    print("Testing downgrade...")
    downgrade(test_db)

    # Cleanup
    if test_db.exists():
        test_db.unlink()

    print("Migration test complete")
```

**4. Update Database Initialization**:
```python
# In session_db_setup.py or init_database.py
def initialize_database(db_path: Path):
    """Initialize or update database schema"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Load and execute main schema
    with open('schema.sql', 'r') as f:
        cursor.executescript(f.read())

    # Load and execute new feature schema
    if Path('new_feature_data.sql').exists():
        with open('new_feature_data.sql', 'r') as f:
            cursor.executescript(f.read())

    conn.commit()
    conn.close()
```

### Database Access Patterns

**Repository Pattern**:
```python
class NewFeatureRepository:
    """Data access layer for new feature"""

    def __init__(self, db_path: Path):
        """Initialize repository"""
        self.db_path = db_path

    def create(self, session_id: str, feature_type: str,
               data: str) -> str:
        """Create new record"""
        import uuid
        from datetime import datetime

        record_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO new_feature_data (
                id, session_id, feature_type, data, created_at
            ) VALUES (?, ?, ?, ?, ?)
        """, (record_id, session_id, feature_type, data, timestamp))

        conn.commit()
        conn.close()

        return record_id

    def get_by_id(self, record_id: str) -> Optional[Dict[str, Any]]:
        """Get record by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM new_feature_data WHERE id = ?
        """, (record_id,))

        row = cursor.fetchone()
        conn.close()

        return dict(row) if row else None

    def get_by_session(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all records for session"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM new_feature_data
            WHERE session_id = ?
            ORDER BY created_at DESC
        """, (session_id,))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def update(self, record_id: str, **kwargs) -> None:
        """Update record"""
        # Build UPDATE query dynamically
        set_clause = ', '.join(f"{k} = ?" for k in kwargs.keys())
        values = list(kwargs.values()) + [record_id]

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(f"""
            UPDATE new_feature_data
            SET {set_clause}
            WHERE id = ?
        """, values)

        conn.commit()
        conn.close()

    def delete(self, record_id: str) -> None:
        """Delete record"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM new_feature_data WHERE id = ?
        """, (record_id,))

        conn.commit()
        conn.close()
```

### Database Performance Optimization

**1. Use Indexes**:
```sql
-- Index frequently queried columns
CREATE INDEX idx_sessions_model ON sessions(model_id);
CREATE INDEX idx_messages_session ON messages(session_id);

-- Composite indexes for common queries
CREATE INDEX idx_sessions_model_date ON sessions(model_id, created_at);
```

**2. Use EXPLAIN QUERY PLAN**:
```python
def analyze_query(query: str):
    """Analyze query performance"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get query plan
    cursor.execute(f"EXPLAIN QUERY PLAN {query}")
    plan = cursor.fetchall()

    for row in plan:
        print(row)

    conn.close()

# Usage
analyze_query("SELECT * FROM sessions WHERE model_id = 'qwen3-coder-30b'")
```

**3. Use Transactions**:
```python
def bulk_insert(records: List[Dict]):
    """Insert multiple records in single transaction"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Begin transaction (implicit with executemany)
        cursor.executemany("""
            INSERT INTO new_feature_data (id, session_id, data)
            VALUES (?, ?, ?)
        """, [(r['id'], r['session_id'], r['data']) for r in records])

        conn.commit()
    except Exception as e:
        conn.rollback()
        raise
    finally:
        conn.close()
```

**4. Vacuum Periodically**:
```python
def vacuum_database(db_path: Path):
    """Optimize database file"""
    conn = sqlite3.connect(db_path)
    conn.execute("VACUUM")
    conn.close()
```

---

## API Development

### RESTful API Design

If you're adding an API server mode, follow these guidelines:

**1. Use Flask or FastAPI**:
```python
# api_server.py
"""
API Server for AI Router
"""

from flask import Flask, request, jsonify
from pathlib import Path
from session_manager import SessionManager
from ai_router import AIRouter

app = Flask(__name__)

# Initialize components
session_manager = SessionManager(Path(".ai-router-sessions.db"))
ai_router = AIRouter()

@app.route('/api/v1/sessions', methods=['GET'])
def list_sessions():
    """List all sessions"""
    limit = request.args.get('limit', 10, type=int)
    sessions = session_manager.list_sessions(limit=limit)

    return jsonify({
        'sessions': sessions,
        'count': len(sessions)
    })

@app.route('/api/v1/sessions', methods=['POST'])
def create_session():
    """Create new session"""
    data = request.json

    # Validate input
    if 'model_id' not in data:
        return jsonify({'error': 'model_id required'}), 400

    # Create session
    session_id = session_manager.create_session(
        model_id=data['model_id'],
        model_name=data.get('model_name', 'Unknown'),
        title=data.get('title')
    )

    return jsonify({
        'session_id': session_id,
        'status': 'created'
    }), 201

@app.route('/api/v1/sessions/<session_id>', methods='GET'])
def get_session(session_id: str):
    """Get session details"""
    session = session_manager.get_session(session_id)

    if not session:
        return jsonify({'error': 'Session not found'}), 404

    messages = session_manager.get_messages(session_id)

    return jsonify({
        'session': session,
        'messages': messages
    })

@app.route('/api/v1/execute', methods=['POST'])
def execute_model():
    """Execute model with prompt"""
    data = request.json

    # Validate
    required = ['model_id', 'prompt']
    if not all(k in data for k in required):
        return jsonify({'error': f'Required: {required}'}), 400

    # Execute
    try:
        response = ai_router.execute_model(
            model_id=data['model_id'],
            prompt=data['prompt'],
            system_prompt=data.get('system_prompt')
        )

        return jsonify({
            'response': response.text,
            'tokens_input': response.tokens_input,
            'tokens_output': response.tokens_output,
            'duration': response.duration_seconds
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '2.0.0'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

**2. API Documentation**:
```markdown
# API Reference

## Endpoints

### GET /api/v1/sessions
List all sessions

**Query Parameters**:
- `limit` (optional): Max sessions to return (default: 10)

**Response**:
```json
{
  "sessions": [
    {
      "session_id": "abc123",
      "title": "My Session",
      "model_id": "qwen3-coder-30b",
      "created_at": "2025-12-08T10:30:00"
    }
  ],
  "count": 1
}
```

### POST /api/v1/execute
Execute model with prompt

**Request Body**:
```json
{
  "model_id": "qwen3-coder-30b",
  "prompt": "Write hello world in Python",
  "system_prompt": "You are a coding assistant"
}
```

**Response**:
```json
{
  "response": "print('Hello, World!')",
  "tokens_input": 15,
  "tokens_output": 5,
  "duration": 1.2
}
```
```

---

## Debugging and Troubleshooting

### Logging Setup

```python
# Add to module
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai-router.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Use in code
logger.debug("Detailed information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred")
logger.exception("Exception with traceback")
```

### Python Debugger

```python
# Insert breakpoint
import pdb; pdb.set_trace()

# Or use breakpoint() (Python 3.7+)
breakpoint()

# Debugger commands:
# n - next line
# s - step into function
# c - continue
# p variable - print variable
# l - list code
# q - quit
```

### VSCode Debugging

Add to `.vscode/launch.json`:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Debug AI Router",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/ai-router.py",
            "console": "integratedTerminal",
            "justMyCode": false,
            "env": {
                "DEBUG": "True",
                "LOG_LEVEL": "DEBUG"
            }
        }
    ]
}
```

### Common Issues and Solutions

**Issue 1: Database Locked**
```python
# Solution: Use timeout and retry
import time

def execute_with_retry(query, max_retries=3):
    for attempt in range(max_retries):
        try:
            cursor.execute(query)
            return
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                time.sleep(0.1 * (attempt + 1))
            else:
                raise
    raise Exception("Database locked after retries")
```

**Issue 2: Import Errors**
```python
# Add parent directory to path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

**Issue 3: Path Issues on Windows**
```python
# Always use Path from pathlib
from pathlib import Path

# Convert to string only when needed
path = Path("D:/models/file.txt")
with open(str(path), 'r') as f:
    content = f.read()
```

---

## Performance Optimization

### Profiling

```python
# Profile with cProfile
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Code to profile
expensive_function()

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)  # Top 20 functions
```

### Memory Profiling

```python
# Install: pip install memory_profiler
from memory_profiler import profile

@profile
def memory_intensive_function():
    large_list = [i for i in range(1000000)]
    return sum(large_list)

# Run with: python -m memory_profiler script.py
```

### Database Optimization

```python
# Use connection pooling (for high-concurrency)
from queue import Queue
import sqlite3

class ConnectionPool:
    def __init__(self, db_path, pool_size=5):
        self.pool = Queue(maxsize=pool_size)
        for _ in range(pool_size):
            conn = sqlite3.connect(db_path, check_same_thread=False)
            self.pool.put(conn)

    def get_connection(self):
        return self.pool.get()

    def return_connection(self, conn):
        self.pool.put(conn)
```

### Caching

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_computation(param):
    """Cached function - results stored for repeated calls"""
    # Expensive operation
    return result
```

---

## Security Best Practices

### Input Validation

```python
def validate_session_id(session_id: str) -> bool:
    """Validate session ID format"""
    import re
    # UUID format
    pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return bool(re.match(pattern, session_id))

def sanitize_user_input(user_input: str) -> str:
    """Sanitize user input"""
    # Remove potentially dangerous characters
    sanitized = user_input.replace(';', '').replace('--', '')
    return sanitized
```

### SQL Injection Prevention

```python
# ALWAYS use parameterized queries
# BAD - vulnerable to SQL injection
cursor.execute(f"SELECT * FROM sessions WHERE id = '{session_id}'")

# GOOD - safe from SQL injection
cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
```

### API Key Security

```python
# Never hardcode API keys
# BAD
api_key = "sk-1234567890abcdef"

# GOOD - use environment variables
import os
api_key = os.getenv('OPENAI_API_KEY')

# Or use .env file
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
```

### File Path Security

```python
def safe_file_path(user_path: str, base_dir: Path) -> Path:
    """Ensure file path is within allowed directory"""
    requested = Path(user_path).resolve()
    base = base_dir.resolve()

    # Check if path is within base directory
    try:
        requested.relative_to(base)
        return requested
    except ValueError:
        raise ValueError(f"Path {user_path} is outside allowed directory")
```

---

## Documentation Standards

### Module Docstrings

```python
"""
module_name.py - Brief one-line description

Detailed description of what this module does, its purpose,
and how it fits into the larger system.

Key Components:
    - Component1: Description
    - Component2: Description

Example:
    Basic usage example

    >>> from module_name import MainClass
    >>> obj = MainClass()
    >>> result = obj.method()

Author: Your Name
Created: 2025-12-08
"""
```

### Function Docstrings

```python
def complex_function(param1: str, param2: int, param3: Optional[List] = None) -> Dict[str, Any]:
    """
    Brief description of what the function does.

    Longer description explaining behavior, edge cases, and important
    details. Can span multiple paragraphs.

    Args:
        param1: Description of param1. Can include details about
                expected format, constraints, etc.
        param2: Description of param2. Include valid ranges or
                expected values.
        param3: Optional parameter description. Explain default
                behavior when None.

    Returns:
        Dictionary containing:
        - key1 (str): Description
        - key2 (int): Description
        - key3 (List): Description

    Raises:
        ValueError: When param1 is empty or invalid format
        FileNotFoundError: When referenced file doesn't exist
        TypeError: When param2 is not an integer

    Examples:
        Basic usage:
        >>> result = complex_function("test", 42)
        >>> print(result['key1'])
        'value1'

        With optional parameter:
        >>> result = complex_function("test", 42, ["a", "b"])
        >>> len(result['key3'])
        2

    Note:
        Additional notes, warnings, or important information.
        Performance considerations, thread safety, etc.

    See Also:
        related_function: Related functionality
        OtherClass.method: Alternative approach
    """
    pass
```

### README Template for New Features

```markdown
# Feature Name

**Status**: Alpha / Beta / Production
**Version**: 1.0.0
**Author**: Your Name
**Created**: 2025-12-08

## Overview

Brief description of what this feature does and why it exists.

## Features

- Feature 1: Description
- Feature 2: Description
- Feature 3: Description

## Installation

```bash
# If additional dependencies needed
pip install additional-package
```

## Quick Start

```python
# Minimal example
from new_feature import FeatureManager

manager = FeatureManager()
result = manager.do_something()
```

## Usage

### Basic Usage

Detailed example with explanation...

### Advanced Usage

Complex examples...

## API Reference

### Class: FeatureManager

#### Methods

**`method_name(param1, param2)`**

Description...

**Parameters**:
- `param1` (str): Description
- `param2` (int): Description

**Returns**: Description

**Example**:
```python
result = manager.method_name("value", 42)
```

## Configuration

Configuration options...

## Testing

How to test this feature...

## Troubleshooting

Common issues and solutions...

## Contributing

How to contribute to this feature...

## License

MIT

## Changelog

### v1.0.0 (2025-12-08)
- Initial release
- Feature 1 implemented
- Feature 2 implemented
```

---

## Code Review Process

### Reviewer Guidelines

**What to Look For**:
1. **Correctness**: Does code work as intended?
2. **Tests**: Are there adequate tests?
3. **Security**: Any vulnerabilities?
4. **Performance**: Any bottlenecks?
5. **Maintainability**: Is code readable and well-structured?
6. **Documentation**: Is it well-documented?
7. **Style**: Follows coding standards?
8. **Breaking Changes**: Are they necessary and documented?

**How to Review**:
```markdown
# Code Review Template

## Summary
Brief summary of what this PR does.

## Checklist
- [ ] Code works correctly
- [ ] Tests pass
- [ ] New tests added
- [ ] Documentation updated
- [ ] No security issues
- [ ] Follows style guide
- [ ] No unnecessary dependencies

## Detailed Review

### Strengths
- What is done well
- Good practices used

### Issues Found
1. **Issue 1**: Description
   - Location: file.py:123
   - Suggestion: How to fix

2. **Issue 2**: Description
   - Location: file.py:456
   - Suggestion: How to fix

### Questions
- Question 1?
- Question 2?

### Recommendations
- Optional improvements
- Future enhancements

## Decision
- [ ] Approve
- [ ] Request Changes
- [ ] Comment
```

### Submitter Guidelines

**Before Requesting Review**:
1. Self-review your code
2. Run all tests
3. Update documentation
4. Write clear PR description
5. Link related issues

**PR Description Template**:
```markdown
## Description
What does this PR do?

## Motivation
Why is this change needed?

## Changes Made
- Change 1
- Change 2
- Change 3

## Testing
How was this tested?

- [ ] Unit tests added
- [ ] Integration tests added
- [ ] Manual testing completed

## Breaking Changes
List any breaking changes and migration path.

## Screenshots
If UI changes, add screenshots.

## Checklist
- [ ] Code follows style guide
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] Breaking changes documented

## Related Issues
Closes #123
Relates to #456
```

---

## Release Process

### Version Numbering

Follow Semantic Versioning (semver.org):

**Format**: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

**Examples**:
- `2.0.0` → `2.1.0`: New feature added
- `2.1.0` → `2.1.1`: Bug fix
- `2.1.1` → `3.0.0`: Breaking change

### Release Checklist

```markdown
# Release Checklist for v2.X.0

## Pre-Release
- [ ] All tests pass on all platforms
- [ ] Documentation is up to date
- [ ] CHANGELOG.md updated
- [ ] Version bumped in all files
- [ ] No debug code or TODOs
- [ ] Security audit passed
- [ ] Performance benchmarks acceptable

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] E2E tests pass (if applicable)
- [ ] Manual testing on Windows
- [ ] Manual testing on Linux/WSL
- [ ] Manual testing on macOS (if applicable)

## Documentation
- [ ] README.md updated
- [ ] USER_GUIDE.md updated
- [ ] DEVELOPER_GUIDE.md updated
- [ ] API changes documented
- [ ] Migration guide (if breaking changes)

## Release
- [ ] Create release branch: `release/v2.X.0`
- [ ] Tag release: `git tag v2.X.0`
- [ ] Push tag: `git push origin v2.X.0`
- [ ] Create GitHub release
- [ ] Upload release artifacts (if any)
- [ ] Merge to main
- [ ] Merge back to develop

## Post-Release
- [ ] Announce release (GitHub, Discord, etc.)
- [ ] Monitor for issues
- [ ] Update project website (if exists)
- [ ] Close milestone
```

### Creating a Release

```bash
# 1. Update version
# Edit version in: ai-router.py, setup.py, __init__.py, etc.

# 2. Update CHANGELOG.md
# Add release notes

# 3. Commit changes
git add .
git commit -m "Release: Version 2.1.0

- Feature 1 added
- Feature 2 improved
- Bug fix for issue #123"

# 4. Create tag
git tag -a v2.1.0 -m "Release version 2.1.0"

# 5. Push
git push origin develop
git push origin v2.1.0

# 6. Create GitHub Release
# Go to GitHub → Releases → Draft a new release
# Use tag v2.1.0
# Add release notes from CHANGELOG
```

### CHANGELOG Format

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- New features that haven't been released yet

### Changed
- Changes to existing functionality

### Deprecated
- Features that will be removed in future versions

### Removed
- Features that have been removed

### Fixed
- Bug fixes

### Security
- Security updates

## [2.1.0] - 2025-12-08

### Added
- Session export to PDF format
- New template: API documentation generator
- Support for Google Gemini API

### Changed
- Improved batch processing performance (30% faster)
- Updated database schema for better search performance

### Fixed
- Fixed database locking issue in batch processor (#456)
- Resolved Windows path handling bug (#478)

## [2.0.0] - 2025-12-01

### Added
- Session management with SQLite persistence
- Prompt template system with Jinja2
- Model comparison (A/B testing)
- Batch processing with checkpoints
- Analytics dashboard
- And 5 more major features...

### Changed
- Complete rewrite of core engine
- New CLI interface

### Breaking Changes
- Configuration file format changed (see MIGRATION_GUIDE.md)
- Database schema incompatible with v1.x (migration script provided)
```

---

## Contributing Guidelines

### How to Contribute

1. **Find or Create an Issue**
   - Check existing issues
   - Create new issue if needed
   - Discuss approach before starting

2. **Fork and Clone**
   ```bash
   # Fork on GitHub, then:
   git clone https://github.com/yourusername/ai-router.git
   cd ai-router
   ```

3. **Create Branch**
   ```bash
   git checkout -b feature/your-feature
   ```

4. **Make Changes**
   - Write code
   - Add tests
   - Update docs

5. **Test**
   ```bash
   python test_integration.py
   python validate_installation.py
   ```

6. **Commit**
   ```bash
   git add .
   git commit -m "Add: Your feature description"
   ```

7. **Push and PR**
   ```bash
   git push origin feature/your-feature
   # Create PR on GitHub
   ```

### Contribution Types

**Code Contributions**:
- New features
- Bug fixes
- Performance improvements
- Refactoring

**Documentation**:
- Fix typos
- Improve clarity
- Add examples
- Translate docs

**Testing**:
- Add test cases
- Improve test coverage
- Report bugs

**Design**:
- UI/UX improvements
- Icons and graphics
- Templates

### Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Help others learn
- Focus on what's best for the project
- Be patient and understanding

---

## Getting Help

### Resources

**Documentation**:
- This guide (DEVELOPER_GUIDE.md)
- User Guide (USER_GUIDE.md)
- Feature Documentation (FEATURE_DOCUMENTATION.md)
- Testing Guide (TESTING_GUIDE.md)

**Community**:
- GitHub Issues: Bug reports and feature requests
- GitHub Discussions: Questions and discussions
- Discord: Real-time chat (if available)
- Email: support@ai-router.dev (if available)

### Asking for Help

**Good Question Format**:
```markdown
## Summary
Brief description of the problem

## Environment
- OS: Windows 11
- Python: 3.11.5
- Version: 2.0.0

## What I'm trying to do
Detailed explanation of goal

## What I've tried
- Tried solution 1: result
- Tried solution 2: result

## Code/Logs
```python
# Relevant code
```

Error message:
```
Full error message
```

## Expected vs Actual
- Expected: X
- Actual: Y
```

### Reporting Bugs

**Bug Report Template**:
```markdown
## Bug Description
Clear description of the bug

## Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: Windows 11
- Python: 3.11.5
- AI Router: 2.0.0

## Logs/Screenshots
Attach relevant logs or screenshots

## Additional Context
Any other relevant information
```

---

## Appendix

### Glossary

- **Session**: A conversation between user and AI model
- **Template**: Reusable prompt structure with variables
- **Batch**: Multiple prompts processed sequentially
- **Workflow**: Multi-step automated process
- **Context**: Additional information injected into prompts
- **GGUF**: Model file format for llama.cpp
- **Quantization**: Model compression technique
- **Token**: Basic unit of text for LLMs

### Useful Commands

```bash
# Development
python ai-router.py          # Run application
python test_integration.py   # Run tests
python validate_installation.py  # Validate setup
black . --line-length 100    # Format code
flake8 .                     # Lint code

# Git
git status                   # Check status
git log --oneline -10        # Recent commits
git diff                     # Show changes
git stash                    # Stash changes
git stash pop                # Restore stashed changes

# Database
sqlite3 .ai-router-sessions.db ".schema"  # Show schema
sqlite3 .ai-router-sessions.db "SELECT * FROM sessions LIMIT 5"  # Query
sqlite3 .ai-router-sessions.db "VACUUM"   # Optimize

# Python
python -m venv venv          # Create virtual environment
pip freeze > requirements.txt  # Export dependencies
pip install -r requirements.txt  # Install dependencies
python -m pip install --upgrade pip  # Upgrade pip
```

### File Templates

**Python Module Template**:
```python
"""
module_name.py - Brief description

Detailed description.

Example:
    >>> from module_name import MainClass
    >>> obj = MainClass()
"""

import os
from pathlib import Path
from typing import Optional, Dict, List, Any
from dataclasses import dataclass

@dataclass
class Config:
    """Configuration"""
    param: str

class MainClass:
    """Main class"""

    def __init__(self, config: Optional[Config] = None):
        """Initialize"""
        self.config = config or Config()

    def method(self, param: str) -> str:
        """Method"""
        return param

def helper_function(data: str) -> bool:
    """Helper function"""
    return True

if __name__ == "__main__":
    # Test code
    obj = MainClass()
    result = obj.method("test")
    print(result)
```

**Test File Template**:
```python
"""
tests/test_module.py - Unit tests for module
"""

import unittest
from pathlib import Path
import tempfile

from module_name import MainClass, Config

class TestMainClass(unittest.TestCase):
    """Tests for MainClass"""

    def setUp(self):
        """Set up before each test"""
        self.config = Config(param="test")
        self.obj = MainClass(self.config)

    def tearDown(self):
        """Clean up after each test"""
        pass

    def test_method(self):
        """Test method"""
        result = self.obj.method("input")
        self.assertIsNotNone(result)

if __name__ == '__main__':
    unittest.main()
```

---

## Conclusion

This developer guide provides comprehensive documentation for contributing to AI Router Enhanced. Remember:

1. **Start Small**: Begin with small contributions to understand the codebase
2. **Ask Questions**: Don't hesitate to ask for help
3. **Follow Standards**: Adhere to coding standards and testing requirements
4. **Document**: Always document your code and changes
5. **Test Thoroughly**: Write tests and validate your changes
6. **Communicate**: Keep maintainers and other contributors informed

**Happy Coding!**

For the latest version of this guide, see: https://github.com/yourrepo/ai-router

---

**Last Updated**: December 9, 2025
**Version**: 2.0.0
**Maintainers**: AI Router Development Team
**License**: MIT
