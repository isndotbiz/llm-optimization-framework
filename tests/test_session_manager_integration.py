#!/usr/bin/env python3
"""
Session Manager Integration Tests
Comprehensive testing for session management system
"""

import sys
from pathlib import Path
import unittest
from datetime import datetime, timedelta
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from session_manager import SessionManager


class TestSessionManagerIntegration(unittest.TestCase):
    """Integration tests for SessionManager"""

    def setUp(self):
        """Set up test database"""
        self.test_db = Path(__file__).parent.parent / "test_session_integration.db"
        if self.test_db.exists():
            self.test_db.unlink()
        self.sm = SessionManager(self.test_db)

    def tearDown(self):
        """Clean up test database"""
        if self.test_db.exists():
            self.test_db.unlink()

    def test_create_session(self):
        """Test session creation"""
        session_id = self.sm.create_session("test_model", {"key": "value"})
        self.assertIsNotNone(session_id)

        session = self.sm.get_session(session_id)
        self.assertEqual(session['model_id'], "test_model")

    def test_add_messages(self):
        """Test adding messages to session"""
        session_id = self.sm.create_session("test_model")

        msg_id1 = self.sm.add_message(session_id, "user", "Hello", 10)
        msg_id2 = self.sm.add_message(session_id, "assistant", "Hi there", 15)

        self.assertIsNotNone(msg_id1)
        self.assertIsNotNone(msg_id2)

        messages = self.sm.get_messages(session_id)
        self.assertEqual(len(messages), 2)

    def test_conversation_flow(self):
        """Test complete conversation flow"""
        session_id = self.sm.create_session("gpt-4")

        # User asks question
        self.sm.add_message(session_id, "user", "What is Python?", 20)

        # Assistant responds
        self.sm.add_message(session_id, "assistant", "Python is a programming language.", 40)

        # User follows up
        self.sm.add_message(session_id, "user", "Tell me more", 15)

        # Assistant responds again
        self.sm.add_message(session_id, "assistant", "Python is versatile...", 50)

        messages = self.sm.get_messages(session_id)
        self.assertEqual(len(messages), 4)

        # Check message order
        self.assertEqual(messages[0]['role'], 'user')
        self.assertEqual(messages[1]['role'], 'assistant')
        self.assertEqual(messages[2]['role'], 'user')
        self.assertEqual(messages[3]['role'], 'assistant')

    def test_session_metadata(self):
        """Test session metadata management"""
        metadata = {
            "temperature": 0.7,
            "max_tokens": 1000,
            "top_p": 0.9
        }

        session_id = self.sm.create_session("test_model", metadata)
        session = self.sm.get_session(session_id)

        loaded_metadata = json.loads(session['metadata'])
        self.assertEqual(loaded_metadata['temperature'], 0.7)
        self.assertEqual(loaded_metadata['max_tokens'], 1000)

    def test_search_messages(self):
        """Test message search functionality"""
        # Create multiple sessions with different content
        sid1 = self.sm.create_session("model1")
        self.sm.add_message(sid1, "user", "Python programming tutorial", 20)

        sid2 = self.sm.create_session("model2")
        self.sm.add_message(sid2, "user", "JavaScript basics", 15)

        sid3 = self.sm.create_session("model3")
        self.sm.add_message(sid3, "user", "Python data science", 25)

        # Search for Python
        results = self.sm.search_messages("Python")
        self.assertGreaterEqual(len(results), 2)

    def test_session_export(self):
        """Test session export to JSON"""
        session_id = self.sm.create_session("test_model")
        self.sm.add_message(session_id, "user", "Question", 10)
        self.sm.add_message(session_id, "assistant", "Answer", 20)

        export_data = self.sm.export_session(session_id)

        self.assertIsNotNone(export_data)
        self.assertEqual(len(export_data['messages']), 2)

    def test_session_statistics(self):
        """Test session statistics"""
        session_id = self.sm.create_session("test_model")
        self.sm.add_message(session_id, "user", "Q1", 10)
        self.sm.add_message(session_id, "assistant", "A1", 20)
        self.sm.add_message(session_id, "user", "Q2", 15)

        stats = self.sm.get_session_stats(session_id)

        self.assertEqual(stats['message_count'], 3)
        self.assertEqual(stats['total_tokens'], 45)

    def test_delete_session(self):
        """Test session deletion"""
        session_id = self.sm.create_session("test_model")
        self.sm.add_message(session_id, "user", "Test", 10)

        # Verify session exists
        session = self.sm.get_session(session_id)
        self.assertIsNotNone(session)

        # Delete session
        self.sm.delete_session(session_id)

        # Verify session is gone
        session = self.sm.get_session(session_id)
        self.assertIsNone(session)

    def test_list_sessions(self):
        """Test listing sessions"""
        # Create multiple sessions
        for i in range(5):
            session_id = self.sm.create_session(f"model_{i}")
            self.sm.add_message(session_id, "user", f"Test {i}", 10)

        sessions = self.sm.list_sessions(limit=10)
        self.assertGreaterEqual(len(sessions), 5)

    def test_update_session_title(self):
        """Test updating session title"""
        session_id = self.sm.create_session("test_model")

        # Update title
        self.sm.update_session(session_id, title="My Custom Title")

        session = self.sm.get_session(session_id)
        self.assertEqual(session['title'], "My Custom Title")

    def test_concurrent_sessions(self):
        """Test multiple concurrent sessions"""
        sessions = []

        # Create 3 concurrent sessions
        for i in range(3):
            sid = self.sm.create_session(f"model_{i}")
            sessions.append(sid)

        # Add messages to each
        for i, sid in enumerate(sessions):
            self.sm.add_message(sid, "user", f"Question {i}", 10)
            self.sm.add_message(sid, "assistant", f"Answer {i}", 20)

        # Verify each session has correct messages
        for i, sid in enumerate(sessions):
            messages = self.sm.get_messages(sid)
            self.assertEqual(len(messages), 2)
            self.assertIn(f"Question {i}", messages[0]['content'])


if __name__ == "__main__":
    unittest.main()
