#!/usr/bin/env python3
"""
Session Manager - SQLite-based conversation history management
for AI Router application
"""

import sqlite3
import uuid
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from contextlib import contextmanager


class SessionManager:
    """SQLite-based session management for conversation history"""

    def __init__(self, db_path: Path):
        """
        Initialize session manager with database

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.schema_path = self.db_path.parent / "schema.sql"

        # Initialize database
        self._init_database()

    def _init_database(self):
        """Initialize database with schema if needed"""
        db_exists = self.db_path.exists()

        if not db_exists:
            # Create new database
            print(f"Creating new session database: {self.db_path}")

            # Check if schema file exists
            if not self.schema_path.exists():
                raise FileNotFoundError(
                    f"Schema file not found: {self.schema_path}\n"
                    "Please ensure schema.sql exists in the models directory."
                )

            # Read schema
            with open(self.schema_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()

            # Execute schema
            with self._get_connection() as conn:
                conn.executescript(schema_sql)
                conn.commit()

            print("Database initialized successfully!")
        else:
            # Verify existing database
            with self._get_connection() as conn:
                cursor = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='sessions'"
                )
                if not cursor.fetchone():
                    raise RuntimeError(
                        f"Database exists but missing sessions table: {self.db_path}\n"
                        "Database may be corrupted. Delete and reinitialize."
                    )

    @contextmanager
    def _get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
        try:
            yield conn
        finally:
            conn.close()

    def create_session(
        self,
        model_id: str,
        model_name: Optional[str] = None,
        title: Optional[str] = None
    ) -> str:
        """
        Create new conversation session

        Args:
            model_id: Model identifier (e.g., 'qwen3-coder-30b')
            model_name: Human-readable model name
            title: Optional session title (auto-generated if None)

        Returns:
            session_id: Unique session identifier
        """
        session_id = str(uuid.uuid4())

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO sessions (session_id, model_id, model_name, title)
                VALUES (?, ?, ?, ?)
                """,
                (session_id, model_id, model_name, title)
            )
            conn.commit()

        return session_id

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        tokens: Optional[int] = None,
        duration: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Add message to session

        Args:
            session_id: Session identifier
            role: Message role ('user', 'assistant', 'system')
            content: Message content
            tokens: Token count (optional)
            duration: Execution duration in seconds (optional)
            metadata: Additional metadata dict (optional)
        """
        # Get next sequence number
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT COALESCE(MAX(sequence_number), 0) + 1 FROM messages WHERE session_id = ?",
                (session_id,)
            )
            sequence_number = cursor.fetchone()[0]

            # Convert metadata to JSON string
            metadata_json = json.dumps(metadata) if metadata else None

            # Insert message
            conn.execute(
                """
                INSERT INTO messages
                (session_id, sequence_number, role, content, tokens_used, duration_seconds, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (session_id, sequence_number, role, content, tokens, duration, metadata_json)
            )

            # Update session totals if tokens/duration provided
            if tokens or duration:
                updates = []
                params = []

                if tokens:
                    updates.append("total_tokens = total_tokens + ?")
                    params.append(tokens)

                if duration:
                    updates.append("total_duration_seconds = total_duration_seconds + ?")
                    params.append(duration)

                if updates:
                    params.append(session_id)
                    sql = f"UPDATE sessions SET {', '.join(updates)} WHERE session_id = ?"
                    conn.execute(sql, params)

            conn.commit()

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session metadata

        Args:
            session_id: Session identifier

        Returns:
            Session dict or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM sessions WHERE session_id = ?",
                (session_id,)
            )
            row = cursor.fetchone()

            if row:
                return dict(row)
            return None

    def get_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get all messages in a session

        Args:
            session_id: Session identifier

        Returns:
            List of message dicts ordered by sequence
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT * FROM messages
                WHERE session_id = ?
                ORDER BY sequence_number ASC
                """,
                (session_id,)
            )
            messages = [dict(row) for row in cursor.fetchall()]

            # Parse JSON metadata
            for msg in messages:
                if msg['metadata']:
                    try:
                        msg['metadata'] = json.loads(msg['metadata'])
                    except json.JSONDecodeError:
                        msg['metadata'] = {}

            return messages

    def list_sessions(
        self,
        limit: int = 50,
        model_filter: Optional[str] = None,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List recent sessions

        Args:
            limit: Maximum number of sessions to return
            model_filter: Filter by model_id (optional)
            offset: Number of sessions to skip

        Returns:
            List of session dicts
        """
        with self._get_connection() as conn:
            if model_filter:
                cursor = conn.execute(
                    """
                    SELECT * FROM recent_sessions
                    WHERE model_id = ?
                    ORDER BY last_activity DESC
                    LIMIT ? OFFSET ?
                    """,
                    (model_filter, limit, offset)
                )
            else:
                cursor = conn.execute(
                    """
                    SELECT * FROM recent_sessions
                    ORDER BY last_activity DESC
                    LIMIT ? OFFSET ?
                    """,
                    (limit, offset)
                )

            return [dict(row) for row in cursor.fetchall()]

    def search_sessions(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search sessions by content using full-text search

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of matching session dicts
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT DISTINCT s.*
                FROM sessions s
                JOIN sessions_fts fts ON s.session_id = fts.session_id
                WHERE sessions_fts MATCH ?
                ORDER BY s.last_activity DESC
                LIMIT ?
                """,
                (query, limit)
            )
            return [dict(row) for row in cursor.fetchall()]

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session and all its messages

        Args:
            session_id: Session to delete

        Returns:
            True if deleted, False if not found
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM sessions WHERE session_id = ?",
                (session_id,)
            )
            conn.commit()
            return cursor.rowcount > 0

    def update_session_title(self, session_id: str, title: str):
        """
        Update session title

        Args:
            session_id: Session identifier
            title: New title
        """
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE sessions SET title = ? WHERE session_id = ?",
                (title, session_id)
            )
            conn.commit()

    def set_session_metadata(self, session_id: str, key: str, value: str):
        """
        Set session metadata key-value pair

        Args:
            session_id: Session identifier
            key: Metadata key
            value: Metadata value
        """
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO session_metadata (session_id, key, value)
                VALUES (?, ?, ?)
                ON CONFLICT(session_id, key) DO UPDATE SET value = excluded.value
                """,
                (session_id, key, value)
            )
            conn.commit()

    def get_session_metadata(self, session_id: str, key: str) -> Optional[str]:
        """
        Get session metadata value

        Args:
            session_id: Session identifier
            key: Metadata key

        Returns:
            Metadata value or None
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT value FROM session_metadata WHERE session_id = ? AND key = ?",
                (session_id, key)
            )
            row = cursor.fetchone()
            return row['value'] if row else None

    def export_session(self, session_id: str, format: str = 'json') -> str:
        """
        Export session to JSON or Markdown

        Args:
            session_id: Session to export
            format: 'json' or 'markdown'

        Returns:
            Formatted string
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        messages = self.get_session_history(session_id)

        if format == 'json':
            export_data = {
                'session': session,
                'messages': messages
            }
            return json.dumps(export_data, indent=2, default=str)

        elif format == 'markdown':
            lines = [
                f"# {session['title'] or 'Untitled Session'}",
                "",
                f"**Model:** {session['model_name'] or session['model_id']}",
                f"**Created:** {session['created_at']}",
                f"**Messages:** {session['message_count']}",
                f"**Tokens:** {session['total_tokens']}",
                "",
                "---",
                ""
            ]

            for msg in messages:
                role = msg['role'].upper()
                timestamp = msg['timestamp']
                content = msg['content']

                lines.append(f"## {role} ({timestamp})")
                lines.append("")
                lines.append(content)
                lines.append("")

                if msg.get('tokens_used'):
                    lines.append(f"*Tokens: {msg['tokens_used']}*")
                if msg.get('duration_seconds'):
                    lines.append(f"*Duration: {msg['duration_seconds']:.2f}s*")
                lines.append("")

            return "\n".join(lines)

        else:
            raise ValueError(f"Unsupported format: {format}")

    def fix_orphaned_records(self) -> int:
        """
        Clean up orphaned message records (messages without corresponding sessions)
        
        Returns:
            Number of orphaned records deleted
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM messages WHERE session_id NOT IN (SELECT session_id FROM sessions)"
            )
            conn.commit()
            deleted_count = cursor.rowcount
            
        return deleted_count

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get database statistics

        Returns:
            Dict with statistics
        """
        with self._get_connection() as conn:
            # Total sessions
            cursor = conn.execute("SELECT COUNT(*) FROM sessions")
            total_sessions = cursor.fetchone()[0]

            # Total messages
            cursor = conn.execute("SELECT COUNT(*) FROM messages")
            total_messages = cursor.fetchone()[0]

            # Total tokens
            cursor = conn.execute("SELECT SUM(total_tokens) FROM sessions")
            total_tokens = cursor.fetchone()[0] or 0

            # Model breakdown
            cursor = conn.execute(
                """
                SELECT model_id, COUNT(*) as count
                FROM sessions
                GROUP BY model_id
                ORDER BY count DESC
                """
            )
            model_breakdown = {row['model_id']: row['count'] for row in cursor.fetchall()}

            # Recent activity
            cursor = conn.execute(
                "SELECT created_at FROM sessions ORDER BY created_at DESC LIMIT 1"
            )
            row = cursor.fetchone()
            last_session = row['created_at'] if row else None

            return {
                'total_sessions': total_sessions,
                'total_messages': total_messages,
                'total_tokens': total_tokens,
                'model_breakdown': model_breakdown,
                'last_session': last_session
            }

    def cleanup_old_sessions(self, days: int = 30) -> int:
        """
        Delete sessions older than specified days

        Args:
            days: Age threshold in days

        Returns:
            Number of sessions deleted
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                DELETE FROM sessions
                WHERE last_activity < datetime('now', '-' || ? || ' days')
                """,
                (days,)
            )
            conn.commit()
            return cursor.rowcount


# Convenience functions for quick access
def create_session_manager(models_dir: Path) -> SessionManager:
    """Create SessionManager instance with standard database path"""
    db_path = models_dir / ".ai-router-sessions.db"
    return SessionManager(db_path)
