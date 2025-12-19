# Quick Start Guide - LLM Session Management

Get started with the LLM Session Management system in 5 minutes.

## Installation

No dependencies required! The system uses Python's built-in `sqlite3` module.

```bash
# All files are ready to use
cd D:/models

# Files included:
# - llm_session_management_schema.sql      (22KB) - Database schema
# - llm_session_examples.sql               (20KB) - 100+ query examples
# - session_manager.py                     (28KB) - Main CLI application
# - session_db_setup.py                    (20KB) - Setup and maintenance
# - llm_session_implementation_guide.md    (32KB) - Complete guide
# - README_SESSION_MANAGEMENT.md           (11KB) - Overview
# Total: ~4,100 lines of production-ready code
```

## Step 1: Initialize Database

```bash
# Create and initialize the database
python session_db_setup.py init

# Check database info
python session_db_setup.py info
```

Output:
```
Initializing database at llm_sessions.db...
Database initialized successfully
Database optimized

Database Information:
  Path: llm_sessions.db
  Size: 0.15 MB
  Schema Version: None
  Journal Mode: wal
  Page Size: 4096

Table Counts:
  sessions: 0
  messages: 0
  models: 0
  projects: 0
```

## Step 2: Create Your First Session

```bash
# Create a session (will auto-create model if it doesn't exist)
python session_manager.py create "My First Chat" --model gpt-4 --provider openai

# Output: Created session: a1b2c3d4e5f6g7h8
```

## Step 3: Add Messages

```bash
# Add a user message
python session_manager.py add a1b2c3d4e5f6g7h8 user "Help me write a Python function"

# Add an assistant response with metrics
python session_manager.py add a1b2c3d4e5f6g7h8 assistant "Here's a Python function..." \
  --tokens 150 --cost 0.005 --latency 1200

# Output: Added message: xyz123...
```

## Step 4: View Conversation

```bash
# Show the full conversation
python session_manager.py show a1b2c3d4e5f6g7h8
```

Output:
```
================================================================================
[USER] 2025-01-08 20:30:45
================================================================================
Help me write a Python function

================================================================================
[ASSISTANT] 2025-01-08 20:30:47
================================================================================
Here's a Python function...

  Tokens: 150 in / 150 out
  Cost: $0.0050
  Latency: 1200ms
```

## Step 5: List All Sessions

```bash
# List recent sessions
python session_manager.py list --limit 10
```

Output:
```
UUID                                 Title                          Status     Msgs   Cost
-----------------------------------------------------------------------------------------------
a1b2c3d4e5f6g7h8                     My First Chat                  active     2      $0.0050
```

## Common Operations

### Search Conversations

```bash
# Full-text search across all messages
python session_manager.py search "python function"
```

### Get Statistics

```bash
# Session-level stats
python session_manager.py stats a1b2c3d4e5f6g7h8

# Cost summary (last 30 days)
python session_manager.py cost --days 30

# Model performance comparison
python session_manager.py performance
```

### Export Session

```bash
# Export to JSON
python session_manager.py export a1b2c3d4e5f6g7h8 --format json --output session.json

# Export to Markdown
python session_manager.py export a1b2c3d4e5f6g7h8 --format markdown --output session.md

# Export to plain text
python session_manager.py export a1b2c3d4e5f6g7h8 --format text
```

### Manage Sessions

```bash
# Mark session as completed
python session_manager.py complete a1b2c3d4e5f6g7h8

# Delete session (with confirmation)
python session_manager.py delete a1b2c3d4e5f6g7h8 --confirm
```

## Maintenance

### Backup Database

```bash
# Create timestamped backup
python session_db_setup.py backup

# Output: Backup created: llm_sessions_backup_20250108_203045.db (2.5 MB)

# Backup to specific location
python session_db_setup.py backup --output ~/backups/sessions.db
```

### Run Maintenance

```bash
# Full maintenance (analyze, vacuum, integrity check)
python session_db_setup.py maintenance --cleanup

# Individual tasks
python session_db_setup.py maintenance --vacuum    # Reclaim space
python session_db_setup.py maintenance --analyze   # Update statistics
python session_db_setup.py maintenance --check     # Integrity check
python session_db_setup.py maintenance --sizes     # Show table sizes
```

## Integration Example

### Using in Your Python Code

```python
from session_manager import SessionManager

# Initialize
db = SessionManager('llm_sessions.db')

# Create session
session_uuid = db.create_session(
    title="Code Review",
    model_id=1,
    system_prompt="You are a code review expert.",
    temperature=0.3
)

# Add messages
db.add_message(session_uuid, 'user', 'Review this Python code...')

# Simulate LLM call
response = "Here's my review..."
db.add_message(
    session_uuid,
    'assistant',
    response,
    input_tokens=200,
    output_tokens=450,
    cost=0.012,
    latency_ms=2300
)

# Get conversation history
messages = db.get_conversation(session_uuid)
for msg in messages:
    print(f"[{msg['role']}]: {msg['content']}")

# Get statistics
stats = db.get_session_stats(session_uuid)
print(f"Total cost: ${stats['total_cost']:.4f}")
print(f"Total tokens: {stats['total_input_tokens'] + stats['total_output_tokens']}")

# Search
results = db.search('python code')
for r in results:
    print(f"{r['session_uuid']}: {r['snippet']}")
```

### Advanced: Batch Processing

```python
import sqlite3

conn = sqlite3.connect('llm_sessions.db')
conn.row_factory = sqlite3.Row

# Create batch job
cursor = conn.execute("""
    INSERT INTO batch_jobs (job_uuid, name, model_id, total_items)
    VALUES (hex(randomblob(16)), 'Summarize Reviews', 1, 100)
    RETURNING id, job_uuid
""")
job = cursor.fetchone()

# Add batch items
for i, review in enumerate(reviews):
    conn.execute("""
        INSERT INTO batch_items (batch_job_id, item_index, input_data)
        VALUES (?, ?, ?)
    """, (job['id'], i, json.dumps({'text': review})))

conn.commit()

# Process items...
# Update progress...

conn.close()
```

### Advanced: A/B Testing

```python
# Create comparison group
cursor = conn.execute("""
    INSERT INTO comparison_groups (group_uuid, name, comparison_type)
    VALUES (hex(randomblob(16)), 'GPT-4 vs Claude', 'model')
    RETURNING id
""")
comparison_id = cursor.fetchone()['id']

# Create two sessions
session_a = db.create_session("Variant A", model_id=1)
session_b = db.create_session("Variant B", model_id=2)

# Link to comparison
conn.execute("""
    INSERT INTO comparison_sessions (comparison_group_id, session_id, variant_name)
    VALUES (?, (SELECT id FROM sessions WHERE session_uuid = ?), 'GPT-4')
""", (comparison_id, session_a))

conn.execute("""
    INSERT INTO comparison_sessions (comparison_group_id, session_id, variant_name)
    VALUES (?, (SELECT id FROM sessions WHERE session_uuid = ?), 'Claude')
""", (comparison_id, session_b))

# Run same prompts on both...
# Record comparison results...
```

## SQL Query Examples

### Find Most Expensive Sessions

```sql
SELECT
    session_uuid,
    title,
    total_cost,
    total_messages,
    started_at
FROM sessions
ORDER BY total_cost DESC
LIMIT 10;
```

### Daily Cost Trend

```sql
SELECT
    DATE(started_at) as date,
    COUNT(*) as sessions,
    SUM(total_cost) as cost,
    SUM(total_input_tokens + total_output_tokens) as tokens
FROM sessions
WHERE started_at >= DATE('now', '-30 days')
GROUP BY DATE(started_at)
ORDER BY date DESC;
```

### Find Sessions by Model

```sql
SELECT
    s.session_uuid,
    s.title,
    m.provider || '/' || m.model_name as model,
    s.total_messages,
    s.total_cost
FROM sessions s
JOIN models m ON s.model_id = m.id
WHERE m.model_name = 'gpt-4'
ORDER BY s.started_at DESC;
```

### Search Message Content

```sql
SELECT
    s.session_uuid,
    s.title,
    m.role,
    snippet(messages_fts, 2, '<mark>', '</mark>', '...', 32) as snippet
FROM messages_fts
JOIN messages m ON messages_fts.rowid = m.id
JOIN sessions s ON m.session_id = s.id
WHERE messages_fts MATCH 'python AND error'
ORDER BY rank
LIMIT 20;
```

## Performance Tips

1. **Use WAL Mode**: Enabled by default, allows concurrent reads
2. **Batch Inserts**: Use transactions for multiple operations
3. **Index Usage**: All critical paths are pre-indexed
4. **Regular Maintenance**: Run `analyze` weekly, `vacuum` monthly
5. **Archive Old Data**: Move old sessions to archived status

## Troubleshooting

### Database Locked Error

```python
# Increase timeout
conn = sqlite3.connect('llm_sessions.db', timeout=30.0)
```

### Full-Text Search Not Working

```bash
# Check if FTS5 is available
python -c "import sqlite3; print(sqlite3.sqlite_version)"

# Should be 3.9.0 or higher
```

### Performance Issues

```bash
# Run maintenance
python session_db_setup.py maintenance --analyze --vacuum

# Check table sizes
python session_db_setup.py maintenance --sizes

# Check integrity
python session_db_setup.py maintenance --check
```

## Next Steps

1. **Read the Full Guide**: `llm_session_implementation_guide.md`
2. **Explore Examples**: `llm_session_examples.sql` has 100+ queries
3. **Review Schema**: `llm_session_management_schema.sql`
4. **Customize**: Add your own tables, triggers, views

## Support

For questions or issues:
1. Check the implementation guide (32KB of detailed documentation)
2. Review example queries (100+ examples covering all use cases)
3. Examine the source code (well-commented and documented)

## Summary

You now have a production-ready LLM session management system with:
- Complete database schema (15+ tables)
- CLI application (28KB)
- Setup and maintenance tools (20KB)
- 100+ example queries
- Comprehensive documentation (32KB guide)
- Support for sessions, comparisons, batch jobs, workflows
- Full-text search, analytics, cost tracking
- Backup, restore, and migration tools

Total: **4,100+ lines** of production-ready code!
