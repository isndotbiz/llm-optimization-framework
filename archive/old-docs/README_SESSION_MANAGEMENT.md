# LLM Session Management System

A comprehensive, production-ready SQLite database schema and Python implementation for managing AI/LLM interactions in CLI applications.

## Quick Start

```bash
# Initialize the database
python session_db_setup.py init

# Create a session
python session_manager.py create "My First Chat" --model gpt-4 --provider openai

# List sessions
python session_manager.py list

# Add a message
python session_manager.py add <session_uuid> user "Hello, help me with Python"

# Search conversations
python session_manager.py search "python error"
```

## Files Overview

### 1. `llm_session_management_schema.sql`
Complete SQLite schema with:
- 15+ tables covering all use cases
- Automatic triggers for metrics tracking
- Views for common queries
- Full-text search support (FTS5)
- Comprehensive indexing

**Key Tables:**
- **Core**: `projects`, `models`, `sessions`, `messages`
- **Comparison**: `comparison_groups`, `comparison_sessions`, `comparison_results`
- **Batch**: `batch_jobs`, `batch_items`
- **Workflows**: `workflows`, `workflow_executions`, `workflow_steps`
- **Analytics**: `performance_metrics`, `session_snapshots`, `annotations`

### 2. `llm_session_examples.sql`
100+ example queries for:
- Session creation and retrieval
- Conversation replay
- A/B testing and comparisons
- Batch job processing
- Workflow execution
- Analytics and reporting
- Performance analysis
- Data cleanup

### 3. `llm_session_implementation_guide.md`
Comprehensive 500+ line guide covering:
- Database design principles (TEXT vs BLOB, indexing, JSON support)
- Python library recommendations (SQLAlchemy, Peewee, raw SQLite)
- Best practices (transactions, error handling, performance)
- Session persistence and recovery
- Complete working examples

### 4. `session_db_setup.py`
Python utility module with:
- `DatabaseSetup`: Initialize, optimize, backup, restore
- `DatabaseMigration`: Version-controlled schema changes
- `DatabaseMaintenance`: Vacuum, analyze, cleanup, integrity checks
- CLI interface for all operations

## Features

### Session Management
- Single conversations with full history
- Session branching from checkpoints
- Auto-save and recovery
- Session snapshots for replay

### A/B Testing
- Compare different models side-by-side
- Evaluate prompt variations
- Track metrics (quality, latency, cost)
- Statistical analysis of results

### Batch Processing
- Process multiple prompts in parallel
- Track progress and errors
- Retry failed items
- Bulk operations support

### Workflows
- Multi-step AI pipelines
- DAG-based execution
- Step-by-step tracking
- Output passing between steps

### Analytics
- Cost tracking per session/model/project
- Token usage monitoring
- Latency analysis (avg, p95, p99)
- Error tracking and reporting
- Daily/hourly statistics

### Performance
- Optimized for 1M+ messages
- Full-text search (FTS5)
- Efficient indexing strategy
- WAL mode for concurrency
- Memory-mapped I/O

## Design Decisions

### Why SQLite?
- **Zero-config**: No server required
- **Portable**: Single file database
- **Fast**: Optimized for local operations
- **Reliable**: ACID-compliant transactions
- **Feature-rich**: JSON support, FTS5, window functions

### TEXT vs BLOB for LLM Responses
Use **TEXT** (not BLOB) because:
- LLM outputs are text strings
- TEXT allows full-text search
- SQL functions work on TEXT (LIKE, regex, etc.)
- No significant size difference for text data
- BLOB is only for true binary (embeddings, images)

### Python Library Recommendations

#### For Large Projects: SQLAlchemy
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

engine = create_engine('sqlite:///llm_sessions.db')
session = Session(engine)
```

**Pros**: Industry standard, powerful ORM, great migration support (Alembic)
**Cons**: Steeper learning curve, more boilerplate

#### For CLI Apps: Peewee
```python
from peewee import *

db = SqliteDatabase('llm_sessions.db')
```

**Pros**: Lightweight, simple API, perfect for SQLite
**Cons**: Smaller ecosystem, limited async

#### For Maximum Control: Raw SQLite
```python
import sqlite3

conn = sqlite3.connect('llm_sessions.db')
conn.row_factory = sqlite3.Row
```

**Pros**: Full control, no overhead, built-in to Python
**Cons**: More manual work, no automatic migrations

### Indexing Strategy

All critical paths are indexed:
- UUID lookups (O(log n) with B-tree)
- Foreign key relationships
- Timestamp range queries
- Status filtering
- Composite indexes for common query patterns

### JSON Support

SQLite 3.38+ has excellent JSON functions:
```sql
-- Store flexible metadata
INSERT INTO sessions (metadata) VALUES (json('{"key": "value"}'));

-- Query nested data
SELECT * FROM sessions WHERE json_extract(metadata, '$.key') = 'value';
```

## Usage Examples

### Basic Session Management

```python
from session_manager import SessionManager

db = SessionManager('llm_sessions.db')

# Create session
session_uuid = db.create_session(
    title="Debug Python Script",
    model_id=1,
    system_prompt="You are an expert Python developer."
)

# Add messages
db.add_message(session_uuid, 'user', 'Help me fix this error...')
db.add_message(
    session_uuid,
    'assistant',
    'This error occurs when...',
    input_tokens=150,
    output_tokens=320,
    cost=0.0264,
    latency_ms=2340
)

# Get conversation
messages = db.get_conversation(session_uuid)
for msg in messages:
    print(f"[{msg['role']}]: {msg['content']}")
```

### A/B Testing

```python
# Create comparison group
comparison_id = create_comparison_group(
    "GPT-4 vs Claude",
    comparison_type='model'
)

# Create two sessions with different models
session_a = create_session("Variant A", model_id=1)
session_b = create_session("Variant B", model_id=2)

# Link to comparison
link_comparison(comparison_id, session_a, variant_name='GPT-4')
link_comparison(comparison_id, session_b, variant_name='Claude')

# Run same prompts on both
for prompt in test_prompts:
    add_message(session_a, 'user', prompt)
    add_message(session_b, 'user', prompt)

    # Get and record responses...

# Compare results
results = get_comparison_results(comparison_id)
```

### Batch Processing

```python
# Create batch job
job_id = create_batch_job(
    name="Summarize Reviews",
    model_id=1,
    input_data=reviews
)

# Process items
for i, review in enumerate(reviews):
    result = llm.complete(review)

    update_batch_item(
        job_id,
        item_index=i,
        status='completed',
        result_data=result
    )

# Monitor progress
progress = get_batch_job_progress(job_id)
print(f"Completed: {progress['completion_pct']}%")
```

### Search and Analytics

```python
# Full-text search
results = db.search('python AND error')
for r in results:
    print(f"{r['session_uuid']}: {r['snippet']}")

# Cost analysis
stats = get_cost_stats(days=30)
print(f"Total cost: ${stats['total_cost']}")
print(f"Avg per session: ${stats['avg_cost_per_session']}")

# Model comparison
models = get_model_performance()
for m in models:
    print(f"{m['model_name']}: {m['avg_latency_ms']}ms, ${m['total_cost']}")
```

## Maintenance

### Backup and Restore

```bash
# Create backup
python session_db_setup.py backup --output backup_20250108.db

# Restore from backup
python session_db_setup.py restore backup_20250108.db --overwrite
```

### Database Maintenance

```bash
# Show database info
python session_db_setup.py info

# Run full maintenance
python session_db_setup.py maintenance --cleanup

# Individual tasks
python session_db_setup.py maintenance --vacuum
python session_db_setup.py maintenance --analyze
python session_db_setup.py maintenance --check
python session_db_setup.py maintenance --sizes
```

### Migrations

```bash
# Apply all pending migrations
python session_db_setup.py migrate

# Migrate to specific version
python session_db_setup.py migrate --version 2
```

## Performance Tips

### 1. Use WAL Mode (Enabled by Default)
Allows concurrent reads while writing.

### 2. Batch Operations
```python
# Bad: Individual inserts
for msg in messages:
    add_message(session_id, msg['role'], msg['content'])

# Good: Batch insert
bulk_add_messages(session_id, messages)
```

### 3. Use Covering Indexes
Query only indexed columns when possible:
```sql
-- Uses index-only scan
SELECT session_uuid, started_at FROM sessions
WHERE status = 'active'
ORDER BY started_at DESC;
```

### 4. Limit Large Queries
```python
# Pagination for large result sets
results = get_sessions_paginated(page=1, per_page=50)
```

### 5. Regular Maintenance
```python
# Run weekly
db.maintenance.analyze()  # Update statistics
db.maintenance.vacuum()   # Reclaim space
```

## Best Practices

1. **Always use transactions** for multi-step operations
2. **Index columns** you frequently query (already done in schema)
3. **Use prepared statements** to prevent SQL injection
4. **Archive old data** to keep database size manageable
5. **Backup regularly** before major operations
6. **Monitor performance** with EXPLAIN QUERY PLAN
7. **Use connection pooling** for multi-threaded applications
8. **Enable foreign keys** (PRAGMA foreign_keys = ON)
9. **Use context managers** for automatic cleanup
10. **Log errors and metrics** for debugging

## Scalability

This schema handles:
- ✅ 1M+ messages
- ✅ 100K+ sessions
- ✅ Sub-millisecond UUID lookups
- ✅ Fast full-text search
- ✅ Concurrent read/write (WAL mode)
- ✅ Database size: 1-10GB typical

When to migrate to PostgreSQL:
- 10M+ messages
- Multiple concurrent writers
- Need for advanced features (row-level security, replication)
- Multi-server deployment

## Support

For implementation questions, refer to:
1. `llm_session_implementation_guide.md` - Comprehensive guide
2. `llm_session_examples.sql` - 100+ query examples
3. `session_db_setup.py` - Source code with docstrings

## License

This implementation is based on industry best practices and open-source standards.

## References

Key resources used in this implementation:
- SQLite official documentation
- Simon Willison's LLM tool (llm.datasette.io)
- LangChain session management patterns
- Helicone session replay features
- Industry best practices for database design

## Version

Schema Version: 1.0
Last Updated: 2025-01-08
