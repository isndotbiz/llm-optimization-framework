# LLM Session Management Implementation Guide

This guide provides comprehensive information for implementing session management in Python CLI applications for AI/LLM interactions using SQLite.

## Table of Contents

1. [Overview](#overview)
2. [Database Schema Design](#database-schema-design)
3. [Python Library Recommendations](#python-library-recommendations)
4. [Implementation Best Practices](#implementation-best-practices)
5. [Session Persistence and Recovery](#session-persistence-and-recovery)
6. [Performance Optimization](#performance-optimization)
7. [Example Implementation](#example-implementation)

---

## Overview

This implementation provides a robust foundation for managing LLM interactions with support for:

- **Single sessions**: Standard chat conversations
- **Comparison sessions**: A/B testing different models or prompts
- **Batch jobs**: Processing multiple prompts in parallel
- **Workflows**: Multi-step AI pipelines
- **Analytics**: Comprehensive metrics and reporting

---

## Database Schema Design

### Core Design Principles

1. **TEXT vs BLOB for Responses**
   - Use `TEXT` columns for LLM responses (not `BLOB`)
   - TEXT allows full-text search, pattern matching, and SQL functions
   - BLOB is only for true binary data (embeddings, images, etc.)
   - Base64-encoded data should use TEXT (33% larger but searchable)

2. **Normalization**
   - Models are normalized into separate table for reuse
   - Sessions link to models via foreign keys
   - Messages belong to sessions in parent-child relationship

3. **JSON Support**
   - SQLite 3.38+ has excellent JSON functions
   - Use JSON columns for flexible metadata
   - Allows querying nested data: `json_extract(metadata, '$.key')`

4. **UUIDs for External References**
   - Use `session_uuid` and `message_uuid` for API/CLI references
   - Integer IDs for internal foreign keys (better performance)
   - Generated with `hex(randomblob(16))` in SQLite

### Schema Tables

#### Core Tables

- **projects**: Top-level organization
- **models**: LLM model configurations with cost tracking
- **sessions**: Conversation instances with aggregated metrics
- **messages**: Individual prompts and responses

#### Comparison & Testing

- **comparison_groups**: A/B test definitions
- **comparison_sessions**: Links sessions to comparisons
- **comparison_results**: Evaluation metrics and scores

#### Batch Processing

- **batch_jobs**: Bulk processing jobs
- **batch_items**: Individual items in batch jobs

#### Workflows

- **workflows**: Multi-step process definitions
- **workflow_executions**: Workflow run instances
- **workflow_steps**: Individual workflow step executions

#### Analytics

- **performance_metrics**: Aggregated performance data
- **session_snapshots**: Checkpoints for replay
- **annotations**: User feedback and ratings

---

## Python Library Recommendations

### SQLite ORM Options

#### 1. SQLAlchemy (Recommended for Large Projects)

**Pros:**
- Industry standard with 57% market share
- Excellent async support (SQLAlchemy 2.0+)
- Powerful query API
- Great migration support via Alembic
- Strong type hints

**Cons:**
- Steeper learning curve
- More boilerplate code
- Heavier dependency

**Installation:**
```bash
pip install sqlalchemy alembic
```

**Example:**
```python
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, Session
from datetime import datetime

Base = declarative_base()

class SessionModel(Base):
    __tablename__ = 'sessions'

    id = Column(Integer, primary_key=True)
    session_uuid = Column(String, unique=True, nullable=False)
    title = Column(String)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

engine = create_engine('sqlite:///llm_sessions.db')
Base.metadata.create_all(engine)
```

#### 2. Peewee (Recommended for CLI Applications)

**Pros:**
- Lightweight (6,600 lines, single module)
- Simple, intuitive API
- Perfect for SQLite
- Minimal boilerplate
- Easy to learn

**Cons:**
- Smaller ecosystem
- Limited async support
- No built-in migrations (use external tools)

**Installation:**
```bash
pip install peewee
```

**Example:**
```python
from peewee import *
from datetime import datetime

db = SqliteDatabase('llm_sessions.db')

class Session(Model):
    session_uuid = CharField(unique=True)
    title = CharField(null=True)
    content = TextField()
    created_at = DateTimeField(default=datetime.now)

    class Meta:
        database = db

db.connect()
db.create_tables([Session])
```

#### 3. No ORM (Raw SQLite - Recommended for Maximum Control)

**Pros:**
- Full control over queries
- No abstraction overhead
- Easier debugging
- Best performance
- Simple for CLI tools

**Cons:**
- More manual work
- No automatic migrations
- Need to handle SQL injection carefully

**Installation:**
```bash
# Built into Python standard library
import sqlite3
```

**Example:**
```python
import sqlite3
import json
from datetime import datetime

class SessionDB:
    def __init__(self, db_path='llm_sessions.db'):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row  # Dict-like access
        self.conn.execute("PRAGMA foreign_keys = ON")

    def create_session(self, title, model_id, system_prompt):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO sessions (session_uuid, title, model_id, system_prompt)
            VALUES (hex(randomblob(16)), ?, ?, ?)
        """, (title, model_id, system_prompt))
        self.conn.commit()
        return cursor.lastrowid

    def add_message(self, session_id, role, content, tokens=None):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO messages (
                message_uuid, session_id, sequence_number, role, content,
                input_tokens, output_tokens
            )
            SELECT
                hex(randomblob(16)), ?,
                COALESCE(MAX(sequence_number), 0) + 1,
                ?, ?, ?, ?
            FROM (
                SELECT sequence_number FROM messages WHERE session_id = ?
                UNION ALL SELECT 0
            )
        """, (session_id, role, content, tokens, tokens, session_id))
        self.conn.commit()
        return cursor.lastrowid

    def get_conversation(self, session_id):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT role, content, timestamp, input_tokens, output_tokens
            FROM messages
            WHERE session_id = ?
            ORDER BY sequence_number
        """, (session_id,))
        return cursor.fetchall()
```

### Database Migration Tools

#### 1. Alembic (with SQLAlchemy)

```bash
pip install alembic

# Initialize
alembic init migrations

# Create migration
alembic revision --autogenerate -m "Add new column"

# Apply migrations
alembic upgrade head
```

#### 2. Simple Python Migration Script (No Dependencies)

```python
import sqlite3

class Migration:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self._ensure_migrations_table()

    def _ensure_migrations_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version INTEGER PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

    def get_version(self):
        cursor = self.conn.execute(
            "SELECT MAX(version) FROM schema_migrations"
        )
        result = cursor.fetchone()[0]
        return result if result else 0

    def apply_migration(self, version, sql):
        current = self.get_version()
        if current >= version:
            return False

        self.conn.executescript(sql)
        self.conn.execute(
            "INSERT INTO schema_migrations (version) VALUES (?)",
            (version,)
        )
        self.conn.commit()
        return True

# Usage
db = Migration('llm_sessions.db')

# Migration 1: Add temperature column
db.apply_migration(1, """
    ALTER TABLE sessions ADD COLUMN temperature REAL DEFAULT 0.7;
""")

# Migration 2: Add tags column
db.apply_migration(2, """
    ALTER TABLE sessions ADD COLUMN tags JSON;
""")
```

### JSON Serialization

#### 1. Standard Library json (Recommended)

```python
import json

# Serialize
data = {"model": "gpt-4", "temperature": 0.7}
json_str = json.dumps(data)

# Deserialize
data = json.loads(json_str)

# With SQLite
cursor.execute(
    "INSERT INTO sessions (metadata) VALUES (?)",
    (json.dumps(data),)
)
```

#### 2. orjson (for Performance)

```bash
pip install orjson
```

```python
import orjson

# 2-3x faster than json
data = {"large": "dataset" * 1000}
json_bytes = orjson.dumps(data)  # Returns bytes
json_str = json_bytes.decode('utf-8')

# Parse
data = orjson.loads(json_bytes)
```

---

## Implementation Best Practices

### 1. Connection Management

```python
import sqlite3
from contextlib import contextmanager

class SessionDB:
    def __init__(self, db_path='llm_sessions.db'):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")  # Better concurrency
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_db(self):
        """Initialize database schema"""
        with self.get_connection() as conn:
            # Load schema from file
            with open('schema.sql', 'r') as f:
                conn.executescript(f.read())
```

### 2. Transaction Safety

```python
def create_session_with_initial_message(db, title, system_prompt, user_message):
    """Atomic operation: create session + add messages"""
    with db.get_connection() as conn:
        # Create session
        cursor = conn.execute("""
            INSERT INTO sessions (session_uuid, title, system_prompt)
            VALUES (hex(randomblob(16)), ?, ?)
            RETURNING id, session_uuid
        """, (title, system_prompt))

        session = cursor.fetchone()
        session_id = session['id']

        # Add system message
        conn.execute("""
            INSERT INTO messages (message_uuid, session_id, sequence_number, role, content)
            VALUES (hex(randomblob(16)), ?, 1, 'system', ?)
        """, (session_id, system_prompt))

        # Add user message
        conn.execute("""
            INSERT INTO messages (message_uuid, session_id, sequence_number, role, content)
            VALUES (hex(randomblob(16)), ?, 2, 'user', ?)
        """, (session_id, user_message))

        # Transaction commits automatically when context exits
        return session['session_uuid']
```

### 3. Handling Large Responses

```python
def add_large_message(db, session_id, role, content):
    """
    For very large responses (>100KB), consider chunking or external storage.
    SQLite handles TEXT up to 1GB, but performance degrades.
    """
    content_size = len(content.encode('utf-8'))

    if content_size > 100_000:  # 100KB
        # Option 1: Store externally
        file_path = f"messages/{session_id}_{role}_{timestamp}.txt"
        with open(file_path, 'w') as f:
            f.write(content)

        # Store reference
        db.add_message(
            session_id, role,
            content=f"[Large message stored externally: {file_path}]",
            metadata={"external_file": file_path, "size_bytes": content_size}
        )
    else:
        # Option 2: Store directly
        db.add_message(session_id, role, content)
```

### 4. Full-Text Search Implementation

```python
def search_messages(db, query, limit=20):
    """Search messages using FTS5"""
    with db.get_connection() as conn:
        cursor = conn.execute("""
            SELECT
                m.message_uuid,
                s.session_uuid,
                s.title,
                m.role,
                snippet(messages_fts, 2, '<mark>', '</mark>', '...', 32) as snippet,
                m.timestamp
            FROM messages_fts
            JOIN messages m ON messages_fts.rowid = m.id
            JOIN sessions s ON m.session_id = s.id
            WHERE messages_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        """, (query, limit))

        return [dict(row) for row in cursor.fetchall()]

# Usage
results = search_messages(db, 'python AND error')
for result in results:
    print(f"{result['session_uuid']}: {result['snippet']}")
```

---

## Session Persistence and Recovery

### 1. Session State Snapshots

```python
def create_snapshot(db, session_id, snapshot_type='checkpoint'):
    """Create a snapshot for session replay"""
    with db.get_connection() as conn:
        cursor = conn.execute("""
            SELECT MAX(sequence_number) as seq FROM messages WHERE session_id = ?
        """, (session_id,))

        current_seq = cursor.fetchone()['seq']

        # Get session state
        cursor = conn.execute("""
            SELECT * FROM sessions WHERE id = ?
        """, (session_id,))
        session = dict(cursor.fetchone())

        # Get all messages up to this point
        cursor = conn.execute("""
            SELECT role, content, timestamp FROM messages
            WHERE session_id = ? AND sequence_number <= ?
            ORDER BY sequence_number
        """, (session_id, current_seq))
        messages = [dict(row) for row in cursor.fetchall()]

        # Store snapshot
        conn.execute("""
            INSERT INTO session_snapshots (
                session_id, snapshot_type, sequence_number,
                session_state, context_window
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            session_id,
            snapshot_type,
            current_seq,
            json.dumps(session),
            json.dumps(messages)
        ))

        return current_seq
```

### 2. Session Recovery

```python
def recover_session(db, session_uuid):
    """Recover session from crash or interruption"""
    with db.get_connection() as conn:
        # Get session
        cursor = conn.execute("""
            SELECT * FROM sessions WHERE session_uuid = ?
        """, (session_uuid,))
        session = cursor.fetchone()

        if not session:
            raise ValueError(f"Session {session_uuid} not found")

        # Get last snapshot
        cursor = conn.execute("""
            SELECT * FROM session_snapshots
            WHERE session_id = ?
            ORDER BY sequence_number DESC
            LIMIT 1
        """, (session['id'],))
        snapshot = cursor.fetchone()

        if snapshot:
            # Restore from snapshot
            return {
                'session': json.loads(snapshot['session_state']),
                'messages': json.loads(snapshot['context_window']),
                'sequence': snapshot['sequence_number']
            }
        else:
            # Restore from messages table
            cursor = conn.execute("""
                SELECT role, content, timestamp
                FROM messages
                WHERE session_id = ?
                ORDER BY sequence_number
            """, (session['id'],))

            return {
                'session': dict(session),
                'messages': [dict(row) for row in cursor.fetchall()],
                'sequence': session['total_messages']
            }
```

### 3. Auto-save Implementation

```python
import time
from threading import Thread, Event

class AutoSaveManager:
    def __init__(self, db, session_id, interval=300):
        """Auto-save session every 5 minutes"""
        self.db = db
        self.session_id = session_id
        self.interval = interval
        self.stop_event = Event()
        self.thread = None

    def start(self):
        """Start auto-save thread"""
        self.thread = Thread(target=self._auto_save_loop, daemon=True)
        self.thread.start()

    def stop(self):
        """Stop auto-save thread"""
        self.stop_event.set()
        if self.thread:
            self.thread.join()

    def _auto_save_loop(self):
        """Auto-save loop"""
        while not self.stop_event.wait(self.interval):
            try:
                create_snapshot(self.db, self.session_id, 'auto_save')
                print(f"Auto-saved session {self.session_id}")
            except Exception as e:
                print(f"Auto-save failed: {e}")

# Usage
auto_save = AutoSaveManager(db, session_id, interval=300)
auto_save.start()

# ... do work ...

auto_save.stop()
```

---

## Performance Optimization

### 1. Database Configuration

```python
def configure_database(conn):
    """Apply performance optimizations"""
    # Enable Write-Ahead Logging (better concurrency)
    conn.execute("PRAGMA journal_mode = WAL")

    # Increase cache size (default is 2MB, increase to 64MB)
    conn.execute("PRAGMA cache_size = -64000")

    # Use memory for temp tables
    conn.execute("PRAGMA temp_store = MEMORY")

    # Synchronous = NORMAL (faster, still safe)
    conn.execute("PRAGMA synchronous = NORMAL")

    # Increase page size for large BLOBs (if used)
    # conn.execute("PRAGMA page_size = 8192")  # Only at creation

    # Memory-mapped I/O (faster reads)
    conn.execute("PRAGMA mmap_size = 268435456")  # 256MB
```

### 2. Batch Inserts

```python
def bulk_add_messages(db, messages):
    """Insert multiple messages efficiently"""
    with db.get_connection() as conn:
        conn.executemany("""
            INSERT INTO messages (
                message_uuid, session_id, sequence_number,
                role, content, input_tokens, output_tokens
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, [
            (
                msg['uuid'], msg['session_id'], msg['sequence'],
                msg['role'], msg['content'],
                msg.get('input_tokens'), msg.get('output_tokens')
            )
            for msg in messages
        ])
```

### 3. Indexing Strategy

**Indexes already included in schema:**
- Primary keys (automatic)
- Foreign keys
- UUID columns (for lookups)
- Timestamp columns (for date range queries)
- Status columns (for filtering)
- Composite indexes (session_id, sequence_number)

**When to add more indexes:**
- After analyzing slow queries with `EXPLAIN QUERY PLAN`
- Balance: indexes speed up reads but slow down writes

```sql
-- Example: Add index if you often query by model and date
CREATE INDEX idx_sessions_model_date ON sessions(model_id, started_at);

-- Check query plan
EXPLAIN QUERY PLAN
SELECT * FROM sessions WHERE model_id = 1 AND started_at > '2025-01-01';
```

### 4. Query Optimization

```python
def get_recent_sessions_optimized(db, limit=50):
    """Efficiently get recent sessions with model info"""
    with db.get_connection() as conn:
        # Use covering index (all columns in index)
        # Avoid SELECT * when possible
        cursor = conn.execute("""
            SELECT
                s.session_uuid,
                s.title,
                s.status,
                s.total_messages,
                s.total_cost,
                s.started_at,
                m.provider || '/' || m.model_name as model
            FROM sessions s
            LEFT JOIN models m ON s.model_id = m.id
            WHERE s.status = 'active'
            ORDER BY s.started_at DESC
            LIMIT ?
        """, (limit,))

        return [dict(row) for row in cursor.fetchall()]
```

### 5. Pagination for Large Result Sets

```python
def get_sessions_paginated(db, page=1, per_page=50):
    """Paginate results efficiently"""
    offset = (page - 1) * per_page

    with db.get_connection() as conn:
        # Get total count
        cursor = conn.execute("SELECT COUNT(*) as total FROM sessions")
        total = cursor.fetchone()['total']

        # Get page
        cursor = conn.execute("""
            SELECT * FROM v_session_summary
            ORDER BY started_at DESC
            LIMIT ? OFFSET ?
        """, (per_page, offset))

        sessions = [dict(row) for row in cursor.fetchall()]

        return {
            'sessions': sessions,
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page
        }
```

### 6. Maintenance Tasks

```python
def maintenance(db):
    """Run periodic maintenance"""
    with db.get_connection() as conn:
        # Update query planner statistics
        conn.execute("ANALYZE")

        # Reclaim unused space
        conn.execute("VACUUM")

        # Check integrity
        cursor = conn.execute("PRAGMA integrity_check")
        result = cursor.fetchone()[0]

        if result != 'ok':
            raise RuntimeError(f"Database integrity check failed: {result}")

        print("Maintenance completed successfully")
```

---

## Example Implementation

### Complete CLI Application

```python
#!/usr/bin/env python3
"""
LLM Session Manager - Complete example implementation
"""

import sqlite3
import json
import sys
from datetime import datetime
from contextlib import contextmanager
from pathlib import Path

class SessionManager:
    def __init__(self, db_path='llm_sessions.db'):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_db(self):
        """Initialize database from schema file"""
        schema_path = Path(__file__).parent / 'llm_session_management_schema.sql'

        if not schema_path.exists():
            print(f"Error: Schema file not found at {schema_path}")
            sys.exit(1)

        with self.get_connection() as conn:
            with open(schema_path, 'r') as f:
                conn.executescript(f.read())

    # Models
    def add_model(self, provider, model_name, **kwargs):
        """Add a new model configuration"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO models (
                    provider, model_name, model_version, context_window,
                    cost_per_1k_input_tokens, cost_per_1k_output_tokens
                ) VALUES (?, ?, ?, ?, ?, ?)
                RETURNING id
            """, (
                provider,
                model_name,
                kwargs.get('model_version'),
                kwargs.get('context_window'),
                kwargs.get('cost_per_1k_input_tokens'),
                kwargs.get('cost_per_1k_output_tokens')
            ))
            return cursor.fetchone()['id']

    def get_model(self, provider, model_name):
        """Get model by provider and name"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM models
                WHERE provider = ? AND model_name = ?
            """, (provider, model_name))
            return cursor.fetchone()

    # Sessions
    def create_session(self, title, model_id, system_prompt=None, **kwargs):
        """Create a new session"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO sessions (
                    session_uuid, title, model_id, system_prompt,
                    temperature, max_tokens, session_type, project_id
                ) VALUES (
                    hex(randomblob(16)), ?, ?, ?, ?, ?, ?, ?
                )
                RETURNING id, session_uuid
            """, (
                title,
                model_id,
                system_prompt,
                kwargs.get('temperature', 0.7),
                kwargs.get('max_tokens'),
                kwargs.get('session_type', 'single'),
                kwargs.get('project_id')
            ))

            result = cursor.fetchone()

            # Add system message if provided
            if system_prompt:
                conn.execute("""
                    INSERT INTO messages (
                        message_uuid, session_id, sequence_number,
                        role, content
                    ) VALUES (hex(randomblob(16)), ?, 1, 'system', ?)
                """, (result['id'], system_prompt))

            return result['session_uuid']

    def get_session(self, session_uuid):
        """Get session by UUID"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM v_session_summary
                WHERE session_uuid = ?
            """, (session_uuid,))
            return cursor.fetchone()

    def list_sessions(self, limit=50):
        """List recent sessions"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM v_session_summary
                ORDER BY started_at DESC
                LIMIT ?
            """, (limit,))
            return cursor.fetchall()

    # Messages
    def add_message(self, session_uuid, role, content, **kwargs):
        """Add a message to a session"""
        with self.get_connection() as conn:
            # Get session ID
            cursor = conn.execute("""
                SELECT id FROM sessions WHERE session_uuid = ?
            """, (session_uuid,))
            session = cursor.fetchone()

            if not session:
                raise ValueError(f"Session {session_uuid} not found")

            session_id = session['id']

            # Get next sequence number
            cursor = conn.execute("""
                SELECT COALESCE(MAX(sequence_number), 0) + 1 as next_seq
                FROM messages WHERE session_id = ?
            """, (session_id,))
            sequence = cursor.fetchone()['next_seq']

            # Insert message
            cursor = conn.execute("""
                INSERT INTO messages (
                    message_uuid, session_id, sequence_number, role, content,
                    input_tokens, output_tokens, cost, latency_ms
                ) VALUES (
                    hex(randomblob(16)), ?, ?, ?, ?, ?, ?, ?, ?
                )
                RETURNING id, message_uuid
            """, (
                session_id, sequence, role, content,
                kwargs.get('input_tokens'),
                kwargs.get('output_tokens'),
                kwargs.get('cost'),
                kwargs.get('latency_ms')
            ))

            return cursor.fetchone()['message_uuid']

    def get_conversation(self, session_uuid):
        """Get all messages in a session"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT
                    m.sequence_number,
                    m.role,
                    m.content,
                    m.timestamp,
                    m.input_tokens,
                    m.output_tokens,
                    m.latency_ms
                FROM messages m
                JOIN sessions s ON m.session_id = s.id
                WHERE s.session_uuid = ?
                ORDER BY m.sequence_number
            """, (session_uuid,))
            return cursor.fetchall()

    # Search
    def search(self, query, limit=20):
        """Search messages using full-text search"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT
                    s.session_uuid,
                    s.title,
                    m.role,
                    snippet(messages_fts, 2, '<mark>', '</mark>', '...', 32) as snippet,
                    m.timestamp
                FROM messages_fts
                JOIN messages m ON messages_fts.rowid = m.id
                JOIN sessions s ON m.session_id = s.id
                WHERE messages_fts MATCH ?
                ORDER BY rank
                LIMIT ?
            """, (query, limit))
            return cursor.fetchall()

# CLI Interface
def main():
    import argparse

    parser = argparse.ArgumentParser(description='LLM Session Manager')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Create session
    create_parser = subparsers.add_parser('create', help='Create new session')
    create_parser.add_argument('title', help='Session title')
    create_parser.add_argument('--model', required=True, help='Model name')
    create_parser.add_argument('--provider', default='openai', help='Model provider')
    create_parser.add_argument('--system-prompt', help='System prompt')

    # List sessions
    list_parser = subparsers.add_parser('list', help='List sessions')
    list_parser.add_argument('--limit', type=int, default=10, help='Number of sessions')

    # Show conversation
    show_parser = subparsers.add_parser('show', help='Show conversation')
    show_parser.add_argument('session_uuid', help='Session UUID')

    # Add message
    msg_parser = subparsers.add_parser('add', help='Add message')
    msg_parser.add_argument('session_uuid', help='Session UUID')
    msg_parser.add_argument('role', choices=['user', 'assistant'], help='Message role')
    msg_parser.add_argument('content', help='Message content')

    # Search
    search_parser = subparsers.add_parser('search', help='Search messages')
    search_parser.add_argument('query', help='Search query')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    db = SessionManager()

    if args.command == 'create':
        # Get or create model
        model = db.get_model(args.provider, args.model)
        if not model:
            print(f"Model {args.provider}/{args.model} not found. Creating...")
            model_id = db.add_model(args.provider, args.model)
        else:
            model_id = model['id']

        # Create session
        session_uuid = db.create_session(
            args.title,
            model_id,
            system_prompt=args.system_prompt
        )
        print(f"Created session: {session_uuid}")

    elif args.command == 'list':
        sessions = db.list_sessions(args.limit)
        print(f"\n{'UUID':<40} {'Title':<30} {'Messages':<10} {'Cost':<10}")
        print("-" * 95)
        for s in sessions:
            print(f"{s['session_uuid']:<40} {s['title']:<30} "
                  f"{s['total_messages']:<10} ${s['total_cost']:<10.4f}")

    elif args.command == 'show':
        conversation = db.get_conversation(args.session_uuid)
        for msg in conversation:
            print(f"\n[{msg['role'].upper()}] {msg['timestamp']}")
            print(msg['content'])
            if msg['input_tokens']:
                print(f"  ({msg['input_tokens']} in / {msg['output_tokens']} out, "
                      f"{msg['latency_ms']}ms)")

    elif args.command == 'add':
        msg_uuid = db.add_message(args.session_uuid, args.role, args.content)
        print(f"Added message: {msg_uuid}")

    elif args.command == 'search':
        results = db.search(args.query)
        for r in results:
            print(f"\n{r['session_uuid']} - {r['title']}")
            print(f"[{r['role']}] {r['snippet']}")

if __name__ == '__main__':
    main()
```

### Usage Examples

```bash
# Create a new session
python session_manager.py create "Debug Python Code" --model gpt-4 --provider openai

# List sessions
python session_manager.py list --limit 20

# Show conversation
python session_manager.py show <session_uuid>

# Add message
python session_manager.py add <session_uuid> user "Help me fix this bug"

# Search
python session_manager.py search "python error"
```

---

## Summary

This implementation provides:

1. **Robust Schema**: Supports all use cases (single, comparison, batch, workflows)
2. **Flexible Libraries**: Choose based on project needs (SQLAlchemy, Peewee, or raw SQLite)
3. **Best Practices**: Transactions, indexing, full-text search, performance optimization
4. **Session Management**: Persistence, recovery, snapshots, auto-save
5. **Production Ready**: Error handling, migration support, maintenance tasks

The schema is designed to scale from simple CLI tools to complex AI applications with comprehensive analytics and A/B testing capabilities.
