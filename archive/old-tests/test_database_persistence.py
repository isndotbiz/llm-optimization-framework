#!/usr/bin/env python3
"""
Comprehensive Database and Persistence Testing for AI Router
Tests all database schemas, CRUD operations, and file persistence
"""

import sqlite3
import json
import yaml
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

class DatabaseTester:
    """Tests all database operations and persistence mechanisms"""

    def __init__(self, base_path: str = "D:/models"):
        self.base_path = Path(base_path)
        self.db_path = self.base_path / ".ai-router-sessions.db"
        self.test_results = {
            "passed": [],
            "failed": [],
            "warnings": [],
            "total_tests": 0
        }

    def log_test(self, test_name: str, passed: bool, message: str = ""):
        """Log test result"""
        self.test_results["total_tests"] += 1
        status = "PASS" if passed else "FAIL"
        result = f"[{status}] {test_name}"
        if message:
            result += f": {message}"

        print(result)
        if passed:
            self.test_results["passed"].append(test_name)
        else:
            self.test_results["failed"].append(test_name)

    def log_warning(self, message: str):
        """Log warning message"""
        print(f"[WARN] {message}")
        self.test_results["warnings"].append(message)

    # ========================================================================
    # SESSION DATABASE TESTS (schema.sql)
    # ========================================================================

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with proper settings"""
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def test_session_database_creation(self) -> bool:
        """Test 1.1: Database file creation and WAL mode"""
        try:
            conn = self._get_connection()

            # Check WAL mode
            cursor = conn.execute("PRAGMA journal_mode")
            mode = cursor.fetchone()[0]

            # Check foreign keys
            cursor = conn.execute("PRAGMA foreign_keys")
            fk_enabled = cursor.fetchone()[0]

            conn.close()

            passed = mode.lower() == 'wal' and fk_enabled == 1
            self.log_test(
                "Database Creation & WAL Mode",
                passed,
                f"Journal={mode}, FK={fk_enabled}"
            )
            return passed
        except Exception as e:
            self.log_test("Database Creation & WAL Mode", False, str(e))
            return False

    def test_schema_creation(self) -> bool:
        """Test 1.2: Create all tables from schema.sql"""
        try:
            schema_path = self.base_path / "schema.sql"
            if not schema_path.exists():
                self.log_test("Schema Creation", False, "schema.sql not found")
                return False

            conn = self._get_connection()

            # Execute schema
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
            conn.executescript(schema_sql)
            conn.commit()

            # Verify tables exist
            cursor = conn.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """)
            tables = [row[0] for row in cursor.fetchall()]

            expected_tables = ['sessions', 'messages', 'session_metadata',
                             'sessions_fts', 'analytics_metadata']
            missing = set(expected_tables) - set(tables)

            conn.close()

            passed = len(missing) == 0
            self.log_test(
                "Schema Table Creation",
                passed,
                f"Found {len(tables)} tables, Missing: {missing if missing else 'None'}"
            )
            return passed
        except Exception as e:
            self.log_test("Schema Table Creation", False, str(e))
            return False

    def test_indexes_creation(self) -> bool:
        """Test 1.3: Verify all indexes were created"""
        try:
            conn = self._get_connection()
            cursor = conn.execute("""
                SELECT name FROM sqlite_master
                WHERE type='index' AND name NOT LIKE 'sqlite_%'
            """)
            indexes = [row[0] for row in cursor.fetchall()]
            conn.close()

            expected_indexes = [
                'idx_sessions_created', 'idx_sessions_updated',
                'idx_sessions_model', 'idx_sessions_activity',
                'idx_messages_session', 'idx_messages_timestamp',
                'idx_messages_role',
                'idx_metadata_session', 'idx_metadata_key'
            ]

            missing = set(expected_indexes) - set(indexes)

            passed = len(missing) == 0
            self.log_test(
                "Index Creation",
                passed,
                f"Found {len(indexes)} indexes, Missing: {missing if missing else 'None'}"
            )
            return passed
        except Exception as e:
            self.log_test("Index Creation", False, str(e))
            return False

    def test_triggers_creation(self) -> bool:
        """Test 1.4: Verify all triggers were created"""
        try:
            conn = self._get_connection()
            cursor = conn.execute("""
                SELECT name FROM sqlite_master
                WHERE type='trigger'
            """)
            triggers = [row[0] for row in cursor.fetchall()]
            conn.close()

            expected_triggers = [
                'update_session_timestamp',
                'decrement_message_count',
                'sessions_fts_insert',
                'sessions_fts_update',
                'sessions_fts_delete',
                'auto_generate_title'
            ]

            missing = set(expected_triggers) - set(triggers)

            passed = len(missing) == 0
            self.log_test(
                "Trigger Creation",
                passed,
                f"Found {len(triggers)} triggers, Missing: {missing if missing else 'None'}"
            )
            return passed
        except Exception as e:
            self.log_test("Trigger Creation", False, str(e))
            return False

    def test_views_creation(self) -> bool:
        """Test 1.5: Verify all views were created"""
        try:
            conn = self._get_connection()
            cursor = conn.execute("""
                SELECT name FROM sqlite_master
                WHERE type='view'
            """)
            views = [row[0] for row in cursor.fetchall()]
            conn.close()

            expected_views = ['recent_sessions', 'session_stats']
            missing = set(expected_views) - set(views)

            passed = len(missing) == 0
            self.log_test(
                "View Creation",
                passed,
                f"Found {len(views)} views, Missing: {missing if missing else 'None'}"
            )
            return passed
        except Exception as e:
            self.log_test("View Creation", False, str(e))
            return False

    def test_crud_sessions(self) -> bool:
        """Test 1.6: Create, Read, Update, Delete operations on sessions"""
        try:
            conn = self._get_connection()

            # CREATE
            test_session_id = f"test_session_{int(time.time())}"
            conn.execute("""
                INSERT INTO sessions (session_id, model_id, model_name, title)
                VALUES (?, ?, ?, ?)
            """, (test_session_id, "test-model", "Test Model", "Test Session"))
            conn.commit()

            # READ
            cursor = conn.execute("""
                SELECT session_id, model_id, title
                FROM sessions WHERE session_id = ?
            """, (test_session_id,))
            row = cursor.fetchone()

            if not row:
                self.log_test("CRUD Sessions", False, "Failed to read session")
                conn.close()
                return False

            # UPDATE
            conn.execute("""
                UPDATE sessions SET title = ? WHERE session_id = ?
            """, ("Updated Title", test_session_id))
            conn.commit()

            cursor = conn.execute("""
                SELECT title FROM sessions WHERE session_id = ?
            """, (test_session_id,))
            updated_title = cursor.fetchone()[0]

            # DELETE
            conn.execute("DELETE FROM sessions WHERE session_id = ?", (test_session_id,))
            conn.commit()

            cursor = conn.execute("""
                SELECT COUNT(*) FROM sessions WHERE session_id = ?
            """, (test_session_id,))
            count = cursor.fetchone()[0]

            conn.close()

            passed = updated_title == "Updated Title" and count == 0
            self.log_test("CRUD Sessions", passed, "All operations successful")
            return passed
        except Exception as e:
            self.log_test("CRUD Sessions", False, str(e))
            return False

    def test_crud_messages(self) -> bool:
        """Test 1.7: CRUD operations on messages"""
        try:
            conn = self._get_connection()

            # Create test session
            test_session_id = f"test_msg_session_{int(time.time())}"
            conn.execute("""
                INSERT INTO sessions (session_id, model_id, model_name)
                VALUES (?, ?, ?)
            """, (test_session_id, "test-model", "Test Model"))

            # CREATE message
            conn.execute("""
                INSERT INTO messages (session_id, sequence_number, role, content, tokens_used)
                VALUES (?, ?, ?, ?, ?)
            """, (test_session_id, 1, "user", "Test message", 10))
            conn.commit()

            # READ message
            cursor = conn.execute("""
                SELECT content, tokens_used FROM messages
                WHERE session_id = ? AND sequence_number = ?
            """, (test_session_id, 1))
            row = cursor.fetchone()

            # UPDATE message
            conn.execute("""
                UPDATE messages SET tokens_used = ?
                WHERE session_id = ? AND sequence_number = ?
            """, (20, test_session_id, 1))
            conn.commit()

            # DELETE message
            conn.execute("""
                DELETE FROM messages WHERE session_id = ?
            """, (test_session_id,))

            # Cleanup
            conn.execute("DELETE FROM sessions WHERE session_id = ?", (test_session_id,))
            conn.commit()
            conn.close()

            passed = row and row[0] == "Test message"
            self.log_test("CRUD Messages", passed, "All operations successful")
            return passed
        except Exception as e:
            self.log_test("CRUD Messages", False, str(e))
            return False

    def test_fts5_search(self) -> bool:
        """Test 1.8: Full-text search functionality"""
        try:
            conn = self._get_connection()

            # Create test session with messages
            test_session_id = f"test_fts_{int(time.time())}"
            conn.execute("""
                INSERT INTO sessions (session_id, model_id, title)
                VALUES (?, ?, ?)
            """, (test_session_id, "test-model", "Database Testing Session"))

            conn.execute("""
                INSERT INTO messages (session_id, sequence_number, role, content)
                VALUES (?, ?, ?, ?)
            """, (test_session_id, 1, "user", "Testing database persistence functionality"))
            conn.commit()

            # Search using FTS5
            cursor = conn.execute("""
                SELECT session_id, content FROM sessions_fts
                WHERE content MATCH 'database'
            """)
            results = cursor.fetchall()

            # Cleanup
            conn.execute("DELETE FROM sessions WHERE session_id = ?", (test_session_id,))
            conn.commit()
            conn.close()

            passed = len(results) > 0
            self.log_test("FTS5 Search", passed, f"Found {len(results)} results")
            return passed
        except Exception as e:
            self.log_test("FTS5 Search", False, str(e))
            return False

    def test_triggers_execution(self) -> bool:
        """Test 1.9: Verify triggers execute correctly"""
        try:
            conn = self._get_connection()

            # Create test session
            test_session_id = f"test_trigger_{int(time.time())}"
            conn.execute("""
                INSERT INTO sessions (session_id, model_id, message_count)
                VALUES (?, ?, ?)
            """, (test_session_id, "test-model", 0))
            conn.commit()

            # Insert message - should trigger update_session_timestamp and increment count
            conn.execute("""
                INSERT INTO messages (session_id, sequence_number, role, content)
                VALUES (?, ?, ?, ?)
            """, (test_session_id, 1, "user", "First message"))
            conn.commit()

            # Check message count was incremented
            cursor = conn.execute("""
                SELECT message_count FROM sessions WHERE session_id = ?
            """, (test_session_id,))
            count = cursor.fetchone()[0]

            # Insert another message to test auto-title generation
            test_session_id2 = f"test_trigger_title_{int(time.time())}"
            conn.execute("""
                INSERT INTO sessions (session_id, model_id)
                VALUES (?, ?)
            """, (test_session_id2, "test-model"))

            conn.execute("""
                INSERT INTO messages (session_id, sequence_number, role, content)
                VALUES (?, ?, ?, ?)
            """, (test_session_id2, 1, "user", "This should become the title"))
            conn.commit()

            cursor = conn.execute("""
                SELECT title FROM sessions WHERE session_id = ?
            """, (test_session_id2,))
            title = cursor.fetchone()[0]

            # Cleanup
            conn.execute("DELETE FROM sessions WHERE session_id IN (?, ?)",
                        (test_session_id, test_session_id2))
            conn.commit()
            conn.close()

            passed = count == 1 and title == "This should become the title"
            self.log_test(
                "Trigger Execution",
                passed,
                f"Count={count}, Title='{title[:20]}...'"
            )
            return passed
        except Exception as e:
            self.log_test("Trigger Execution", False, str(e))
            return False

    def test_foreign_keys(self) -> bool:
        """Test 1.10: Verify foreign key constraints"""
        try:
            conn = self._get_connection()

            # Try to insert message with non-existent session
            try:
                conn.execute("""
                    INSERT INTO messages (session_id, sequence_number, role, content)
                    VALUES (?, ?, ?, ?)
                """, ("nonexistent_session", 1, "user", "test"))
                conn.commit()
                # If we get here, foreign key constraint failed
                conn.close()
                self.log_test("Foreign Key Constraints", False, "FK not enforced")
                return False
            except sqlite3.IntegrityError:
                # This is expected - FK constraint working
                conn.close()
                self.log_test("Foreign Key Constraints", True, "FK enforced correctly")
                return True
        except Exception as e:
            self.log_test("Foreign Key Constraints", False, str(e))
            return False

    # ========================================================================
    # ANALYTICS DATABASE TESTS (analytics_schema.sql)
    # ========================================================================

    def test_analytics_schema(self) -> bool:
        """Test 2.1: Create analytics schema"""
        try:
            schema_path = self.base_path / "analytics_schema.sql"
            if not schema_path.exists():
                self.log_test("Analytics Schema", False, "analytics_schema.sql not found")
                return False

            conn = self._get_connection()

            with open(schema_path, 'r') as f:
                analytics_sql = f.read()
            conn.executescript(analytics_sql)
            conn.commit()

            # Verify views created
            cursor = conn.execute("""
                SELECT name FROM sqlite_master
                WHERE type='view'
            """)
            views = [row[0] for row in cursor.fetchall()]
            conn.close()

            expected_analytics_views = [
                'model_performance', 'daily_stats', 'hourly_activity',
                'session_quality', 'token_usage_trends', 'response_time_analysis',
                'user_interaction_patterns', 'model_comparison',
                'top_sessions_by_tokens', 'most_active_days', 'model_diversity'
            ]

            missing = set(expected_analytics_views) - set(views)

            passed = len(missing) == 0
            self.log_test(
                "Analytics Schema",
                passed,
                f"Found {len(views)} views, Missing: {missing if missing else 'None'}"
            )
            return passed
        except Exception as e:
            self.log_test("Analytics Schema", False, str(e))
            return False

    def test_analytics_views_with_data(self) -> bool:
        """Test 2.2: Test analytics views with sample data"""
        try:
            conn = self._get_connection()

            # Create sample data
            test_session_id = f"analytics_test_{int(time.time())}"
            conn.execute("""
                INSERT INTO sessions (session_id, model_id, model_name, total_tokens)
                VALUES (?, ?, ?, ?)
            """, (test_session_id, "test-model", "Test Model", 1000))

            conn.execute("""
                INSERT INTO messages (session_id, sequence_number, role, content, tokens_used, duration_seconds)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (test_session_id, 1, "user", "Test", 100, 1.5))
            conn.commit()

            # Test various analytics views
            view_tests = [
                "model_performance",
                "daily_stats",
                "session_quality",
                "model_comparison"
            ]

            results = {}
            for view in view_tests:
                cursor = conn.execute(f"SELECT * FROM {view} LIMIT 1")
                results[view] = cursor.fetchone() is not None

            # Cleanup
            conn.execute("DELETE FROM sessions WHERE session_id = ?", (test_session_id,))
            conn.commit()
            conn.close()

            passed = all(results.values())
            self.log_test(
                "Analytics Views Query",
                passed,
                f"Working views: {sum(results.values())}/{len(results)}"
            )
            return passed
        except Exception as e:
            self.log_test("Analytics Views Query", False, str(e))
            return False

    # ========================================================================
    # COMPARISON DATABASE TESTS (comparison_schema.sql)
    # ========================================================================

    def test_comparison_schema(self) -> bool:
        """Test 3.1: Create comparison schema"""
        try:
            schema_path = self.base_path / "comparison_schema.sql"
            if not schema_path.exists():
                self.log_test("Comparison Schema", False, "comparison_schema.sql not found")
                return False

            conn = self._get_connection()

            with open(schema_path, 'r') as f:
                comparison_sql = f.read()
            conn.executescript(comparison_sql)
            conn.commit()

            # Verify tables
            cursor = conn.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name LIKE 'comparison%'
            """)
            tables = [row[0] for row in cursor.fetchall()]
            conn.close()

            expected_tables = ['comparison_results', 'comparison_responses']
            missing = set(expected_tables) - set(tables)

            passed = len(missing) == 0
            self.log_test(
                "Comparison Schema",
                passed,
                f"Found {len(tables)} tables, Missing: {missing if missing else 'None'}"
            )
            return passed
        except Exception as e:
            self.log_test("Comparison Schema", False, str(e))
            return False

    def test_comparison_crud(self) -> bool:
        """Test 3.2: CRUD operations for comparisons"""
        try:
            conn = self._get_connection()

            # CREATE comparison
            test_comp_id = f"comp_{int(time.time())}"
            conn.execute("""
                INSERT INTO comparison_results (comparison_id, prompt, model_count)
                VALUES (?, ?, ?)
            """, (test_comp_id, "Test prompt", 2))

            conn.execute("""
                INSERT INTO comparison_responses
                (comparison_id, model_id, model_name, response_text, tokens_output, duration_seconds)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (test_comp_id, "model1", "Model 1", "Response 1", 100, 2.5))

            conn.execute("""
                INSERT INTO comparison_responses
                (comparison_id, model_id, model_name, response_text, tokens_output, duration_seconds)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (test_comp_id, "model2", "Model 2", "Response 2", 120, 3.0))
            conn.commit()

            # READ comparison
            cursor = conn.execute("""
                SELECT COUNT(*) FROM comparison_responses
                WHERE comparison_id = ?
            """, (test_comp_id,))
            response_count = cursor.fetchone()[0]

            # UPDATE comparison
            conn.execute("""
                UPDATE comparison_results SET winner_model_id = ?
                WHERE comparison_id = ?
            """, ("model1", test_comp_id))
            conn.commit()

            # DELETE comparison (should cascade)
            conn.execute("""
                DELETE FROM comparison_results WHERE comparison_id = ?
            """, (test_comp_id,))
            conn.commit()

            cursor = conn.execute("""
                SELECT COUNT(*) FROM comparison_responses
                WHERE comparison_id = ?
            """, (test_comp_id,))
            remaining = cursor.fetchone()[0]

            conn.close()

            passed = response_count == 2 and remaining == 0
            self.log_test(
                "Comparison CRUD",
                passed,
                f"Created 2 responses, CASCADE delete verified"
            )
            return passed
        except Exception as e:
            self.log_test("Comparison CRUD", False, str(e))
            return False

    # ========================================================================
    # FILE PERSISTENCE TESTS
    # ========================================================================

    def test_json_preference_storage(self) -> bool:
        """Test 4.1: JSON preference file storage"""
        try:
            pref_path = self.base_path / ".ai-router-preferences.json"

            # Write preferences
            test_prefs = {
                "default_model": "qwen2.5:14b",
                "temperature": 0.7,
                "max_tokens": 2048,
                "last_updated": datetime.now().isoformat()
            }

            with open(pref_path, 'w') as f:
                json.dump(test_prefs, f, indent=2)

            # Read preferences
            with open(pref_path, 'r') as f:
                loaded_prefs = json.load(f)

            # Verify
            passed = (
                loaded_prefs["default_model"] == "qwen2.5:14b" and
                loaded_prefs["temperature"] == 0.7
            )

            self.log_test(
                "JSON Preference Storage",
                passed,
                f"Saved and loaded {len(test_prefs)} preferences"
            )
            return passed
        except Exception as e:
            self.log_test("JSON Preference Storage", False, str(e))
            return False

    def test_batch_checkpoint_storage(self) -> bool:
        """Test 4.2: Batch checkpoint JSON storage"""
        try:
            checkpoint_dir = self.base_path / "batch_checkpoints"
            checkpoint_dir.mkdir(exist_ok=True)

            checkpoint_file = checkpoint_dir / f"checkpoint_{int(time.time())}.json"

            # Create checkpoint
            checkpoint_data = {
                "batch_id": "test_batch_001",
                "completed_prompts": 5,
                "total_prompts": 10,
                "current_model": "qwen2.5:14b",
                "timestamp": datetime.now().isoformat(),
                "results": [
                    {"prompt_id": 1, "status": "completed"},
                    {"prompt_id": 2, "status": "completed"}
                ]
            }

            with open(checkpoint_file, 'w') as f:
                json.dump(checkpoint_data, f, indent=2)

            # Load checkpoint
            with open(checkpoint_file, 'r') as f:
                loaded = json.load(f)

            # Verify structure
            passed = (
                loaded["batch_id"] == "test_batch_001" and
                loaded["completed_prompts"] == 5 and
                len(loaded["results"]) == 2
            )

            # Cleanup
            checkpoint_file.unlink()

            self.log_test(
                "Batch Checkpoint Storage",
                passed,
                f"Checkpoint with {len(checkpoint_data['results'])} results"
            )
            return passed
        except Exception as e:
            self.log_test("Batch Checkpoint Storage", False, str(e))
            return False

    def test_yaml_template_storage(self) -> bool:
        """Test 4.3: YAML template file storage and parsing"""
        try:
            template_dir = self.base_path / "prompt-templates"

            if not template_dir.exists():
                self.log_warning("prompt-templates directory doesn't exist")
                template_dir.mkdir(exist_ok=True)

            # Create test template
            test_template_path = template_dir / "test_template.yaml"
            template_data = {
                "name": "Test Template",
                "description": "A test template for validation",
                "category": "testing",
                "variables": ["topic", "detail_level"],
                "template": "Explain {topic} at {detail_level} level"
            }

            with open(test_template_path, 'w') as f:
                yaml.dump(template_data, f)

            # Load and parse
            with open(test_template_path, 'r') as f:
                loaded = yaml.safe_load(f)

            # Validate structure
            passed = (
                loaded["name"] == "Test Template" and
                "variables" in loaded and
                len(loaded["variables"]) == 2
            )

            # Cleanup
            test_template_path.unlink()

            self.log_test(
                "YAML Template Storage",
                passed,
                f"Template with {len(loaded.get('variables', []))} variables"
            )
            return passed
        except Exception as e:
            self.log_test("YAML Template Storage", False, str(e))
            return False

    def test_yaml_workflow_storage(self) -> bool:
        """Test 4.4: YAML workflow file storage and parsing"""
        try:
            workflow_dir = self.base_path / "workflows"

            if not workflow_dir.exists():
                self.log_warning("workflows directory doesn't exist")
                workflow_dir.mkdir(exist_ok=True)

            # Create test workflow
            test_workflow_path = workflow_dir / "test_workflow.yaml"
            workflow_data = {
                "name": "Test Workflow",
                "description": "Multi-step test workflow",
                "steps": [
                    {
                        "id": 1,
                        "name": "Generate outline",
                        "model": "qwen2.5:14b",
                        "prompt": "Create an outline"
                    },
                    {
                        "id": 2,
                        "name": "Write content",
                        "model": "llama3.1:8b",
                        "prompt": "Write based on outline",
                        "depends_on": [1]
                    }
                ]
            }

            with open(test_workflow_path, 'w') as f:
                yaml.dump(workflow_data, f)

            # Load and parse
            with open(test_workflow_path, 'r') as f:
                loaded = yaml.safe_load(f)

            # Validate structure
            passed = (
                loaded["name"] == "Test Workflow" and
                "steps" in loaded and
                len(loaded["steps"]) == 2 and
                "depends_on" in loaded["steps"][1]
            )

            # Cleanup
            test_workflow_path.unlink()

            self.log_test(
                "YAML Workflow Storage",
                passed,
                f"Workflow with {len(loaded.get('steps', []))} steps"
            )
            return passed
        except Exception as e:
            self.log_test("YAML Workflow Storage", False, str(e))
            return False

    def test_comparison_json_export(self) -> bool:
        """Test 4.5: Comparison results JSON export"""
        try:
            comparison_dir = self.base_path / "comparisons"
            comparison_dir.mkdir(exist_ok=True)

            export_file = comparison_dir / f"comparison_{int(time.time())}.json"

            # Create comparison export
            comparison_export = {
                "comparison_id": "comp_001",
                "timestamp": datetime.now().isoformat(),
                "prompt": "Explain quantum computing",
                "models": [
                    {
                        "model_id": "qwen2.5:14b",
                        "response": "Quantum computing uses qubits...",
                        "tokens": 250,
                        "duration": 3.2,
                        "rank": 1
                    },
                    {
                        "model_id": "llama3.1:8b",
                        "response": "Quantum computers leverage...",
                        "tokens": 220,
                        "duration": 2.8,
                        "rank": 2
                    }
                ],
                "winner": "qwen2.5:14b"
            }

            with open(export_file, 'w') as f:
                json.dump(comparison_export, f, indent=2)

            # Load and verify
            with open(export_file, 'r') as f:
                loaded = json.load(f)

            passed = (
                loaded["comparison_id"] == "comp_001" and
                len(loaded["models"]) == 2 and
                loaded["winner"] == "qwen2.5:14b"
            )

            # Cleanup
            export_file.unlink()

            self.log_test(
                "Comparison JSON Export",
                passed,
                f"Export with {len(loaded['models'])} model responses"
            )
            return passed
        except Exception as e:
            self.log_test("Comparison JSON Export", False, str(e))
            return False

    # ========================================================================
    # DATA INTEGRITY TESTS
    # ========================================================================

    def test_not_null_constraints(self) -> bool:
        """Test 5.1: NOT NULL constraints"""
        try:
            conn = self._get_connection()

            # Try to insert session without required model_id
            try:
                conn.execute("""
                    INSERT INTO sessions (session_id, model_id)
                    VALUES (?, ?)
                """, ("test_null", None))
                conn.commit()
                conn.close()
                self.log_test("NOT NULL Constraints", False, "NULL accepted where not allowed")
                return False
            except sqlite3.IntegrityError:
                # Expected - NOT NULL working
                conn.close()
                self.log_test("NOT NULL Constraints", True, "NOT NULL enforced")
                return True
        except Exception as e:
            self.log_test("NOT NULL Constraints", False, str(e))
            return False

    def test_unique_constraints(self) -> bool:
        """Test 5.2: UNIQUE constraints"""
        try:
            conn = self._get_connection()

            test_session = f"unique_test_{int(time.time())}"

            # Insert first message
            conn.execute("""
                INSERT INTO sessions (session_id, model_id)
                VALUES (?, ?)
            """, (test_session, "test-model"))

            conn.execute("""
                INSERT INTO messages (session_id, sequence_number, role, content)
                VALUES (?, ?, ?, ?)
            """, (test_session, 1, "user", "First"))
            conn.commit()

            # Try to insert duplicate sequence number
            try:
                conn.execute("""
                    INSERT INTO messages (session_id, sequence_number, role, content)
                    VALUES (?, ?, ?, ?)
                """, (test_session, 1, "user", "Duplicate"))
                conn.commit()
                conn.execute("DELETE FROM sessions WHERE session_id = ?", (test_session,))
                conn.commit()
                conn.close()
                self.log_test("UNIQUE Constraints", False, "Duplicate allowed")
                return False
            except sqlite3.IntegrityError:
                # Expected - UNIQUE working
                conn.execute("DELETE FROM sessions WHERE session_id = ?", (test_session,))
                conn.commit()
                conn.close()
                self.log_test("UNIQUE Constraints", True, "UNIQUE enforced")
                return True
        except Exception as e:
            self.log_test("UNIQUE Constraints", False, str(e))
            return False

    def test_check_constraints(self) -> bool:
        """Test 5.3: CHECK constraints"""
        try:
            conn = self._get_connection()

            test_session = f"check_test_{int(time.time())}"
            conn.execute("""
                INSERT INTO sessions (session_id, model_id)
                VALUES (?, ?)
            """, (test_session, "test-model"))

            # Try to insert message with invalid role
            try:
                conn.execute("""
                    INSERT INTO messages (session_id, sequence_number, role, content)
                    VALUES (?, ?, ?, ?)
                """, (test_session, 1, "invalid_role", "Test"))
                conn.commit()
                conn.execute("DELETE FROM sessions WHERE session_id = ?", (test_session,))
                conn.commit()
                conn.close()
                self.log_test("CHECK Constraints", False, "Invalid value allowed")
                return False
            except sqlite3.IntegrityError:
                # Expected - CHECK working
                conn.execute("DELETE FROM sessions WHERE session_id = ?", (test_session,))
                conn.commit()
                conn.close()
                self.log_test("CHECK Constraints", True, "CHECK enforced")
                return True
        except Exception as e:
            self.log_test("CHECK Constraints", False, str(e))
            return False

    def test_cascade_delete(self) -> bool:
        """Test 5.4: CASCADE DELETE on foreign keys"""
        try:
            conn = self._get_connection()

            test_session = f"cascade_test_{int(time.time())}"

            # Create session with messages
            conn.execute("""
                INSERT INTO sessions (session_id, model_id)
                VALUES (?, ?)
            """, (test_session, "test-model"))

            conn.execute("""
                INSERT INTO messages (session_id, sequence_number, role, content)
                VALUES (?, ?, ?, ?)
            """, (test_session, 1, "user", "Test"))

            conn.execute("""
                INSERT INTO session_metadata (session_id, key, value)
                VALUES (?, ?, ?)
            """, (test_session, "test_key", "test_value"))
            conn.commit()

            # Delete session (should cascade to messages and metadata)
            conn.execute("DELETE FROM sessions WHERE session_id = ?", (test_session,))
            conn.commit()

            # Check messages deleted
            cursor = conn.execute("""
                SELECT COUNT(*) FROM messages WHERE session_id = ?
            """, (test_session,))
            msg_count = cursor.fetchone()[0]

            # Check metadata deleted
            cursor = conn.execute("""
                SELECT COUNT(*) FROM session_metadata WHERE session_id = ?
            """, (test_session,))
            meta_count = cursor.fetchone()[0]

            conn.close()

            passed = msg_count == 0 and meta_count == 0
            self.log_test(
                "CASCADE DELETE",
                passed,
                f"Messages: {msg_count}, Metadata: {meta_count}"
            )
            return passed
        except Exception as e:
            self.log_test("CASCADE DELETE", False, str(e))
            return False

    # ========================================================================
    # REPORTING
    # ========================================================================

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        total = self.test_results["total_tests"]
        passed = len(self.test_results["passed"])
        failed = len(self.test_results["failed"])
        warnings = len(self.test_results["warnings"])

        score = (passed / total * 100) if total > 0 else 0

        print("\n" + "="*70)
        print("DATABASE PERSISTENCE TEST REPORT")
        print("="*70)
        print(f"\nTotal Tests: {total}")
        print(f"Passed: {passed} ({passed/total*100:.1f}%)")
        print(f"Failed: {failed} ({failed/total*100:.1f}%)")
        print(f"Warnings: {warnings}")
        print(f"\nOverall Score: {score:.1f}%")

        if failed > 0:
            print(f"\nFailed Tests:")
            for test in self.test_results["failed"]:
                print(f"  - {test}")

        if warnings > 0:
            print(f"\nWarnings:")
            for warning in self.test_results["warnings"]:
                print(f"  - {warning}")

        print("\n" + "="*70)

        return {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "warnings": warnings,
            "score": score,
            "failed_tests": self.test_results["failed"],
            "warnings_list": self.test_results["warnings"]
        }

    def run_all_tests(self):
        """Execute all database and persistence tests"""
        print("="*70)
        print("STARTING COMPREHENSIVE DATABASE PERSISTENCE TESTS")
        print("="*70)
        print()

        print("[PHASE 1: Session Database Tests (schema.sql)]")
        self.test_session_database_creation()
        self.test_schema_creation()
        self.test_indexes_creation()
        self.test_triggers_creation()
        self.test_views_creation()
        self.test_crud_sessions()
        self.test_crud_messages()
        self.test_fts5_search()
        self.test_triggers_execution()
        self.test_foreign_keys()

        print("\n[PHASE 2: Analytics Database Tests (analytics_schema.sql)]")
        self.test_analytics_schema()
        self.test_analytics_views_with_data()

        print("\n[PHASE 3: Comparison Database Tests (comparison_schema.sql)]")
        self.test_comparison_schema()
        self.test_comparison_crud()

        print("\n[PHASE 4: File Persistence Tests]")
        self.test_json_preference_storage()
        self.test_batch_checkpoint_storage()
        self.test_yaml_template_storage()
        self.test_yaml_workflow_storage()
        self.test_comparison_json_export()

        print("\n[PHASE 5: Data Integrity Tests]")
        self.test_not_null_constraints()
        self.test_unique_constraints()
        self.test_check_constraints()
        self.test_cascade_delete()

        return self.generate_report()


def main():
    """Main test execution"""
    tester = DatabaseTester("D:/models")
    report = tester.run_all_tests()

    # Return appropriate exit code
    sys.exit(0 if report["failed"] == 0 else 1)


if __name__ == "__main__":
    main()
