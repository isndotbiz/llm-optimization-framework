#!/usr/bin/env python3
"""
Pytest Configuration and Shared Fixtures
Provides common fixtures for all tests across the project
All test modules can use these fixtures without explicit imports
"""

import pytest
import sys
import tempfile
import sqlite3
from pathlib import Path
from unittest.mock import MagicMock, patch
import platform
import json
import logging
from datetime import datetime


# ============================================================================
# SETUP: Add project root to path for imports
# ============================================================================

@pytest.fixture(scope="session", autouse=True)
def setup_python_path():
    """Add project root to Python path"""
    models_dir = Path(__file__).parent.parent
    if str(models_dir) not in sys.path:
        sys.path.insert(0, str(models_dir))
    return models_dir


# ============================================================================
# MACHINE DETECTION FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def machine_type():
    """
    Detect current machine type
    Returns: 'macos' | 'windows' | 'wsl' | 'linux' | 'unknown'
    """
    system = platform.system()

    if system == "Darwin":
        return "macos"
    elif system == "Windows":
        return "windows"
    elif system == "Linux":
        # Check if WSL
        try:
            with open('/proc/version', 'r') as f:
                if 'microsoft' in f.read().lower() or 'wsl' in f.read().lower():
                    return "wsl"
        except (FileNotFoundError, Exception):
            pass
        return "linux"

    return "unknown"


@pytest.fixture(scope="session")
def is_wsl():
    """Check if running in WSL (Windows Subsystem for Linux)"""
    try:
        with open('/proc/version', 'r') as f:
            return 'microsoft' in f.read().lower() or 'wsl' in f.read().lower()
    except (FileNotFoundError, Exception):
        return False


@pytest.fixture(scope="session")
def is_macos():
    """Check if running on macOS"""
    return platform.system() == "Darwin"


@pytest.fixture(scope="session")
def is_windows():
    """Check if running on Windows"""
    return platform.system() == "Windows"


@pytest.fixture(scope="session")
def is_linux():
    """Check if running on Linux (not WSL)"""
    if platform.system() != "Linux":
        return False
    try:
        with open('/proc/version', 'r') as f:
            return 'microsoft' not in f.read().lower()
    except FileNotFoundError:
        return False


# ============================================================================
# TEMPORARY DIRECTORY FIXTURES
# ============================================================================

@pytest.fixture
def temp_db_path(tmp_path):
    """Temporary database file path for testing"""
    return tmp_path / "test_session.db"


@pytest.fixture
def temp_checkpoint_dir(tmp_path):
    """Temporary checkpoint directory for batch processing tests"""
    checkpoint_dir = tmp_path / "checkpoints"
    checkpoint_dir.mkdir(exist_ok=True, parents=True)
    return checkpoint_dir


@pytest.fixture
def temp_workflows_dir(tmp_path):
    """Temporary workflows directory for workflow tests"""
    workflows_dir = tmp_path / "workflows"
    workflows_dir.mkdir(exist_ok=True, parents=True)
    return workflows_dir


@pytest.fixture
def temp_templates_dir(tmp_path):
    """Temporary templates directory for template tests"""
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir(exist_ok=True, parents=True)
    return templates_dir


@pytest.fixture
def temp_log_dir(tmp_path):
    """Temporary logging directory"""
    log_dir = tmp_path / "logs"
    log_dir.mkdir(exist_ok=True, parents=True)
    return log_dir


# ============================================================================
# DATABASE FIXTURES
# ============================================================================

@pytest.fixture
def schema_sql():
    """SQLite schema for session and message tables"""
    return """
    CREATE TABLE IF NOT EXISTS sessions (
        id TEXT PRIMARY KEY,
        model_id TEXT NOT NULL,
        title TEXT DEFAULT 'Untitled Session',
        metadata TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS messages (
        id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('user', 'assistant', 'system')),
        content TEXT NOT NULL,
        tokens_used INTEGER DEFAULT 0,
        created_at TEXT NOT NULL,
        FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_sessions_model ON sessions(model_id);
    CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id);
    CREATE INDEX IF NOT EXISTS idx_messages_created ON messages(created_at);
    """


@pytest.fixture
def test_db_initialized(temp_db_path, schema_sql):
    """
    Create and initialize test database with schema
    Returns path to initialized database
    """
    conn = sqlite3.connect(str(temp_db_path))
    conn.executescript(schema_sql)
    conn.commit()
    conn.close()
    return temp_db_path


@pytest.fixture
def test_db_with_sample_data(test_db_initialized):
    """
    Create database with sample session and message data
    Returns path to database
    """
    db_path = test_db_initialized
    conn = sqlite3.connect(str(db_path))

    # Insert sample session
    conn.execute(
        """
        INSERT INTO sessions (id, model_id, title, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        ('session_001', 'test_model', 'Test Session',
         datetime.now().isoformat(), datetime.now().isoformat())
    )

    # Insert sample messages
    messages = [
        ('msg_001', 'session_001', 'user', 'What is Python?', 5, datetime.now().isoformat()),
        ('msg_002', 'session_001', 'assistant', 'Python is a programming language...', 20, datetime.now().isoformat()),
    ]

    for msg_id, session_id, role, content, tokens, created_at in messages:
        conn.execute(
            """
            INSERT INTO messages (id, session_id, role, content, tokens_used, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (msg_id, session_id, role, content, tokens, created_at)
        )

    conn.commit()
    conn.close()
    return db_path


# ============================================================================
# MOCK FIXTURES
# ============================================================================

@pytest.fixture
def mock_ai_router():
    """Mock AI Router for testing without actual model execution"""
    mock_router = MagicMock()

    # Mock execute_prompt
    mock_router.execute_prompt = MagicMock(
        return_value="Mock response from AI Router"
    )

    # Mock get_model_info
    mock_router.get_model_info = MagicMock(
        return_value={
            "model_id": "test_model",
            "provider": "mock",
            "loaded": True
        }
    )

    # Mock list_models
    mock_router.list_models = MagicMock(
        return_value=["test_model_1", "test_model_2", "test_model_3"]
    )

    # Mock load_model
    mock_router.load_model = MagicMock(return_value=True)

    # Mock unload_model
    mock_router.unload_model = MagicMock(return_value=True)

    return mock_router


@pytest.fixture
def mock_logger():
    """Mock logger for testing"""
    mock = MagicMock(spec=logging.Logger)
    mock.info = MagicMock()
    mock.error = MagicMock()
    mock.warning = MagicMock()
    mock.debug = MagicMock()
    mock.critical = MagicMock()
    return mock


@pytest.fixture
def mock_model_config():
    """Sample model configuration for testing"""
    return {
        "machines": {
            "ryzen-3900x-3090": {
                "description": "Windows/WSL Ryzen 3900X + RTX 3090",
                "gpu_memory": 24576
            },
            "xeon-4060ti": {
                "description": "TrueNAS Xeon Platinum + RTX 4060 Ti",
                "gpu_memory": 8192
            },
            "m4-macbook-pro": {
                "description": "MacBook M4 Pro",
                "gpu_memory": 16384
            }
        },
        "models": [
            {
                "model_id": "test_model_1",
                "name": "Test Model 1",
                "provider": "ollama",
                "path": "/path/to/model1",
                "parameters": {"temperature": 0.7, "top_p": 0.9}
            },
            {
                "model_id": "test_model_2",
                "name": "Test Model 2",
                "provider": "llama.cpp",
                "path": "/path/to/model2",
                "parameters": {"temperature": 0.5}
            },
            {
                "model_id": "test_model_3",
                "name": "Test Model 3",
                "provider": "mlx",
                "path": "/path/to/model3",
                "machine_specific": True
            }
        ]
    }


# ============================================================================
# SAMPLE DATA FIXTURES
# ============================================================================

@pytest.fixture
def sample_prompts():
    """Sample prompts for batch processing tests"""
    return [
        "What is Python?",
        "Explain machine learning in simple terms",
        "Write a Python function to calculate fibonacci",
        "What are the benefits of microservices architecture?",
        "How does JWT authentication work?",
        "Describe REST API principles",
        "What is Docker containerization?",
        "Explain the difference between SQL and NoSQL databases",
    ]


@pytest.fixture
def sample_workflow_yaml():
    """Sample workflow YAML content for workflow tests"""
    return """
name: Test Workflow
description: Sample workflow for testing
version: 1.0
variables:
  topic: Python
  complexity: intermediate

steps:
  - name: research
    type: prompt
    config:
      prompt: "Research {{ topic }} at {{ complexity }} level"
      model: test_model
      output_var: research_result
      max_tokens: 500

  - name: summarize
    type: prompt
    config:
      prompt: "Summarize the research: {{ research_result }}"
      model: test_model
      output_var: summary
      depends_on:
        - research

  - name: expand
    type: prompt
    config:
      prompt: "Expand on: {{ summary }}"
      model: test_model
      depends_on:
        - summarize
"""


@pytest.fixture
def sample_template_yaml(temp_templates_dir):
    """Sample prompt template YAML file"""
    template_content = """
metadata:
  name: Code Generation Template
  version: 1.0
  description: Generate code in specified language
  variables:
    - name: Language to use
      default: Python
    - name: Description
      default: "Write a function"

system_prompt: |
  You are an expert {{ language }} programmer.
  Generate clean, well-documented, production-ready code.
  Follow best practices and include docstrings.

user_prompt: |
  Write a {{ language }} {{ type }}.
  Description: {{ description }}

  Requirements:
  - Clean, readable code
  - Proper error handling
  - Type hints (if applicable)
  - Docstrings
"""
    template_file = temp_templates_dir / "code_gen.yaml"
    template_file.write_text(template_content)
    return template_file


@pytest.fixture
def batch_job_samples(sample_prompts):
    """Sample batch job data"""
    return {
        "job_id": "batch_001",
        "model_id": "test_model",
        "total_prompts": len(sample_prompts),
        "prompts": sample_prompts,
        "status": "pending"
    }


# ============================================================================
# PERFORMANCE & MONITORING FIXTURES
# ============================================================================

@pytest.fixture
def track_memory():
    """Track memory usage during test"""
    import tracemalloc

    tracemalloc.start()
    initial = tracemalloc.get_traced_memory()[0]

    class MemoryTracker:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            current = tracemalloc.get_traced_memory()[0]
            self.used = current - initial
            tracemalloc.stop()

        def __repr__(self):
            return f"MemoryUsed: {self.used / 1024 / 1024:.2f} MB"

    return MemoryTracker()


@pytest.fixture
def track_time():
    """Track execution time of code"""
    import time

    class Timer:
        def __enter__(self):
            self.start = time.time()
            return self

        def __exit__(self, *args):
            self.duration = time.time() - self.start

        def __repr__(self):
            return f"Duration: {self.duration:.3f}s"

    return Timer()


# ============================================================================
# CLEANUP & TEARDOWN
# ============================================================================

@pytest.fixture(autouse=True)
def cleanup_after_test(tmp_path):
    """
    Automatically cleanup after each test
    Removes temporary files and databases
    """
    yield

    # Cleanup happens automatically with tmp_path fixture
    # but we can add custom cleanup logic here if needed
    import shutil
    if tmp_path.exists():
        shutil.rmtree(tmp_path, ignore_errors=True)


# ============================================================================
# PYTEST HOOKS
# ============================================================================

def pytest_configure(config):
    """Configure pytest before running tests"""
    # Register custom markers
    config.addinivalue_line(
        "markers", "unit: Unit test - fast, isolated"
    )
    config.addinivalue_line(
        "markers", "integration: Integration test - medium speed"
    )
    config.addinivalue_line(
        "markers", "performance: Performance test - slower, benchmarks"
    )
    config.addinivalue_line(
        "markers", "smoke: Smoke test - very fast basic checks"
    )
    config.addinivalue_line(
        "markers", "windows: Windows-specific test"
    )
    config.addinivalue_line(
        "markers", "wsl: WSL-specific test"
    )
    config.addinivalue_line(
        "markers", "macos: macOS-specific test"
    )
    config.addinivalue_line(
        "markers", "linux: Linux-specific test"
    )
    config.addinivalue_line(
        "markers", "gpu: GPU-dependent test"
    )
    config.addinivalue_line(
        "markers", "slow: Slow-running test"
    )
    config.addinivalue_line(
        "markers", "flaky: Known flaky test"
    )
    config.addinivalue_line(
        "markers", "machine_specific: Machine-specific test"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection - add markers based on path"""
    for item in items:
        # Mark by directory
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)
        elif "smoke" in str(item.fspath):
            item.add_marker(pytest.mark.smoke)
        elif "machine_specific" in str(item.fspath):
            item.add_marker(pytest.mark.machine_specific)

        # Add slow marker to tests with long names
        if "performance" in item.name or "large" in item.name:
            item.add_marker(pytest.mark.slow)


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_logreport(report):
    """Log test results"""
    if report.when == "call":
        if report.outcome == "failed":
            logging.error(f"TEST FAILED: {report.nodeid}")
        elif report.outcome == "passed":
            logging.debug(f"TEST PASSED: {report.nodeid}")
