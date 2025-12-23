#!/usr/bin/env python3
"""
Example Unit Tests - Demonstrates pytest patterns and fixtures
These tests show how to structure unit tests for the AI Router project
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
import json


class TestDatabaseOperations:
    """Test database-related operations"""

    @pytest.mark.unit
    def test_database_initialization(self, test_db_initialized):
        """Test that database initializes with schema"""
        import sqlite3

        db_path = test_db_initialized
        assert db_path.exists()

        # Verify tables exist
        conn = sqlite3.connect(str(db_path))
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='sessions'"
        )
        assert cursor.fetchone() is not None
        conn.close()

    @pytest.mark.unit
    def test_database_with_sample_data(self, test_db_with_sample_data):
        """Test database with pre-populated data"""
        import sqlite3

        db_path = test_db_with_sample_data
        conn = sqlite3.connect(str(db_path))

        # Verify sample data exists
        cursor = conn.execute("SELECT COUNT(*) FROM sessions")
        count = cursor.fetchone()[0]
        assert count >= 1

        # Verify messages exist
        cursor = conn.execute("SELECT COUNT(*) FROM messages")
        msg_count = cursor.fetchone()[0]
        assert msg_count >= 1

        conn.close()

    @pytest.mark.unit
    def test_database_message_insert(self, test_db_initialized):
        """Test inserting messages into database"""
        import sqlite3
        from datetime import datetime

        db_path = test_db_initialized
        conn = sqlite3.connect(str(db_path))

        # Insert session
        session_id = "test_session_123"
        conn.execute(
            """
            INSERT INTO sessions (id, model_id, title, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (session_id, "test_model", "Test", datetime.now().isoformat(), datetime.now().isoformat())
        )

        # Insert message
        msg_id = "msg_123"
        conn.execute(
            """
            INSERT INTO messages (id, session_id, role, content, tokens_used, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (msg_id, session_id, "user", "Hello", 2, datetime.now().isoformat())
        )
        conn.commit()

        # Verify insertion
        cursor = conn.execute(
            "SELECT content FROM messages WHERE id = ?",
            (msg_id,)
        )
        result = cursor.fetchone()
        assert result[0] == "Hello"

        conn.close()


class TestMockingPatterns:
    """Test mocking patterns and fixtures"""

    @pytest.mark.unit
    def test_mock_ai_router(self, mock_ai_router):
        """Test using mock AI Router fixture"""
        # Mock is pre-configured
        response = mock_ai_router.execute_prompt("test_model", "What is AI?")

        # Verify response
        assert response == "Mock response from AI Router"
        assert mock_ai_router.execute_prompt.called

    @pytest.mark.unit
    def test_mock_logger(self, mock_logger):
        """Test using mock logger"""
        mock_logger.info("Test message")

        # Verify logging was called
        assert mock_logger.info.called
        mock_logger.info.assert_called_with("Test message")

    @pytest.mark.unit
    def test_mock_model_config(self, mock_model_config):
        """Test with mock model configuration"""
        # Config fixture provides sample data
        assert "models" in mock_model_config
        assert len(mock_model_config["models"]) > 0

        # Verify model structure
        model = mock_model_config["models"][0]
        assert "model_id" in model
        assert "provider" in model


class TestSampleData:
    """Test working with sample data fixtures"""

    @pytest.mark.unit
    def test_sample_prompts(self, sample_prompts):
        """Test with sample prompts"""
        assert len(sample_prompts) > 0
        assert all(isinstance(p, str) for p in sample_prompts)
        assert "Python" in sample_prompts[0]

    @pytest.mark.unit
    def test_batch_job_samples(self, batch_job_samples):
        """Test batch job sample data"""
        assert "job_id" in batch_job_samples
        assert batch_job_samples["status"] == "pending"
        assert len(batch_job_samples["prompts"]) > 0

    @pytest.mark.unit
    def test_sample_workflow_yaml(self, sample_workflow_yaml):
        """Test sample workflow YAML parsing"""
        import yaml

        data = yaml.safe_load(sample_workflow_yaml)
        assert data["name"] == "Test Workflow"
        assert len(data["steps"]) > 0


class TestTemporaryDirectories:
    """Test working with temporary directories"""

    @pytest.mark.unit
    def test_temp_checkpoint_dir_creation(self, temp_checkpoint_dir):
        """Test that temp checkpoint directory exists"""
        assert temp_checkpoint_dir.exists()
        assert temp_checkpoint_dir.is_dir()

    @pytest.mark.unit
    def test_write_to_temp_dir(self, temp_checkpoint_dir):
        """Test writing files to temporary directory"""
        test_file = temp_checkpoint_dir / "test_checkpoint.json"
        test_data = {"job_id": "test_001", "status": "completed"}

        # Write test file
        test_file.write_text(json.dumps(test_data))

        # Verify it was written
        assert test_file.exists()
        loaded_data = json.loads(test_file.read_text())
        assert loaded_data["job_id"] == "test_001"

    @pytest.mark.unit
    def test_multiple_temp_dirs(self, temp_checkpoint_dir, temp_workflows_dir, temp_templates_dir):
        """Test using multiple temporary directories"""
        # All directories should exist
        assert temp_checkpoint_dir.exists()
        assert temp_workflows_dir.exists()
        assert temp_templates_dir.exists()

        # Write to each
        (temp_checkpoint_dir / "checkpoint.json").write_text("{}")
        (temp_workflows_dir / "workflow.yaml").write_text("name: test")
        (temp_templates_dir / "template.yaml").write_text("metadata:")

        # Verify all files exist
        assert (temp_checkpoint_dir / "checkpoint.json").exists()
        assert (temp_workflows_dir / "workflow.yaml").exists()
        assert (temp_templates_dir / "template.yaml").exists()


class TestParametrization:
    """Test parametrized tests - run same test with different inputs"""

    @pytest.mark.unit
    @pytest.mark.parametrize("model_id,provider", [
        ("ollama-mistral", "ollama"),
        ("gguf-dolphin", "llama.cpp"),
        ("mlx-qwen", "mlx"),
    ])
    def test_model_provider_mapping(self, model_id, provider):
        """Test that model IDs map to correct providers"""
        # This test runs 3 times with different parameters
        provider_map = {
            "ollama-mistral": "ollama",
            "gguf-dolphin": "llama.cpp",
            "mlx-qwen": "mlx",
        }
        assert provider_map[model_id] == provider

    @pytest.mark.unit
    @pytest.mark.parametrize("prompt_length,category", [
        (10, "short"),
        (100, "medium"),
        (1000, "long"),
    ])
    def test_prompt_categorization(self, prompt_length, category):
        """Test categorizing prompts by length"""
        def categorize_prompt(length):
            if length < 50:
                return "short"
            elif length < 500:
                return "medium"
            else:
                return "long"

        assert categorize_prompt(prompt_length) == category


class TestMachineDetection:
    """Test machine-specific detection and handling"""

    @pytest.mark.unit
    def test_machine_type_detection(self, machine_type, is_wsl, is_macos, is_windows, is_linux):
        """Test machine type detection"""
        # One of these should be true
        if machine_type == "wsl":
            assert is_wsl
        elif machine_type == "macos":
            assert is_macos
        elif machine_type == "windows":
            assert is_windows
        elif machine_type == "linux":
            assert is_linux

    @pytest.mark.unit
    def test_path_detection_by_machine(self, machine_type):
        """Test path handling based on machine type"""
        if machine_type == "windows":
            # Windows paths use backslashes
            test_path = "D:\\models"
            assert "\\" in test_path or machine_type != "windows"
        elif machine_type == "wsl":
            # WSL paths use /mnt/d/
            test_path = "/mnt/d/models"
            assert test_path.startswith("/mnt/")
        elif machine_type == "macos":
            # macOS paths use /Users/
            test_path = "/Users/user/models"
            assert test_path.startswith("/Users") or test_path.startswith("/")


class TestPerformanceTracking:
    """Test performance tracking fixtures"""

    @pytest.mark.unit
    def test_track_execution_time(self, track_time):
        """Test timing measurement"""
        import time

        with track_time:
            time.sleep(0.1)

        # Duration should be at least 0.1 seconds
        assert track_time.duration >= 0.1

    @pytest.mark.unit
    def test_track_memory_usage(self, track_memory):
        """Test memory tracking"""
        with track_memory:
            # Allocate some memory
            large_list = [i for i in range(10000)]

        # Should have used some memory
        assert track_memory.used > 0


class TestFixtureCombination:
    """Test combining multiple fixtures"""

    @pytest.mark.unit
    def test_with_all_fixtures(
        self,
        temp_checkpoint_dir,
        mock_ai_router,
        sample_prompts,
        machine_type,
        track_time
    ):
        """Test combining multiple fixtures together"""
        # Use all fixtures in one test
        assert temp_checkpoint_dir.exists()
        assert mock_ai_router is not None
        assert len(sample_prompts) > 0
        assert machine_type in ["windows", "wsl", "macos", "linux", "unknown"]

        # Simulate some work
        with track_time:
            # Process prompts
            for prompt in sample_prompts[:3]:
                mock_ai_router.execute_prompt("test_model", prompt)

        # Verify all fixtures worked together
        assert mock_ai_router.execute_prompt.call_count >= 3
        assert track_time.duration >= 0


# ============================================================================
# TEST COLLECTION & DISCOVERY
# ============================================================================

# Run these tests:
# pytest tests/unit/test_example_unit.py -v
#
# Run specific test:
# pytest tests/unit/test_example_unit.py::TestDatabaseOperations::test_database_initialization -v
#
# Run with coverage:
# pytest tests/unit/test_example_unit.py -v --cov=utils --cov-report=term-missing
#
# Run only unit tests:
# pytest tests/unit/ -v -m unit
