# Session Management Technical Reference

## Database Configuration Reference

### SQLite Pragmas (Performance & Correctness)

```sql
-- ESSENTIAL: Must set on every connection
PRAGMA foreign_keys = ON;              -- Enforce referential integrity
PRAGMA journal_mode = WAL;             -- Write-Ahead Logging (better concurrency)

-- STRONGLY RECOMMENDED
PRAGMA synchronous = NORMAL;           -- Balance safety vs speed (with WAL)
PRAGMA cache_size = -64000;            -- 64MB cache
PRAGMA temp_store = MEMORY;            -- Use memory for temporary tables
PRAGMA mmap_size = 268435456;          -- 256MB memory-mapped I/O

-- OPTIONAL: Only if needed
PRAGMA page_size = 4096;               -- Don't change after creation
PRAGMA busy_timeout = 5000;            -- Wait 5 seconds on lock
```

### Connection Pool Configuration

```python
# CLI Tool (single-threaded)
pool_config = {
    'pool_size': 1,
    'max_overflow': 0,
    'pool_recycle': 3600
}

# Web Server (10-50 users)
pool_config = {
    'pool_size': 5,
    'max_overflow': 10,
    'pool_recycle': 3600
}

# High Concurrency (100+ users)
pool_config = {
    'pool_size': 20,
    'max_overflow': 50,
    'pool_recycle': 1800
}
```

---

## SQL Query Optimization Patterns

### Problem: N+1 Queries

**BEFORE (N+1 anti-pattern):**
```python
# Query 1: Get sessions
sessions = db.execute("SELECT * FROM sessions").fetchall()

# Queries 2-N: For each session, get message count
for session in sessions:
    count = db.execute(
        "SELECT COUNT(*) FROM messages WHERE session_id = ?",
        (session['session_id'],)
    ).fetchone()[0]
```

**AFTER (Single aggregated query):**
```sql
SELECT
    s.*,
    COUNT(m.message_id) as message_count,
    SUM(m.tokens_used) as total_tokens
FROM sessions s
LEFT JOIN messages m ON s.session_id = m.session_id
GROUP BY s.session_id;
```

### Problem: SELECT * Performance

```sql
-- SLOW: Brings all columns
SELECT * FROM sessions WHERE model_id = 'gpt-4'

-- FAST: Only needed columns
SELECT session_id, title, model_id, message_count, last_activity
FROM sessions
WHERE model_id = 'gpt-4'
ORDER BY last_activity DESC
```

### Covering Index Strategy

```sql
-- Create covering index that includes all columns needed by query
CREATE INDEX idx_sessions_summary ON sessions(
    last_activity DESC,
    session_id,
    title,
    model_id,
    message_count,
    total_tokens
);

-- Query uses index only (no table access needed)
SELECT session_id, title, model_id, message_count
FROM sessions
WHERE status = 'active'
ORDER BY last_activity DESC
LIMIT 50;
```

---

## Data Integrity Checks

### Comprehensive Health Check

```sql
-- Orphaned messages
SELECT COUNT(*) as orphaned_messages
FROM messages
WHERE session_id NOT IN (SELECT session_id FROM sessions);

-- Message count mismatches
SELECT COUNT(*) as count_mismatches
FROM sessions s
WHERE s.message_count != (
    SELECT COUNT(*) FROM messages WHERE session_id = s.session_id
);

-- Token count mismatches
SELECT COUNT(*) as token_mismatches
FROM sessions s
WHERE s.total_tokens != (
    SELECT COALESCE(SUM(tokens_used), 0) FROM messages WHERE session_id = s.session_id
);

-- Integrity check
PRAGMA integrity_check;
```

### Automated Health Monitoring

```python
def database_health_check(db_path):
    """Run comprehensive health check"""
    conn = sqlite3.connect(str(db_path))

    checks = {}

    # FK enforcement
    cursor = conn.execute("PRAGMA foreign_keys")
    checks['foreign_keys_enabled'] = cursor.fetchone()[0] == 1

    # Orphaned records
    cursor = conn.execute("""
        SELECT COUNT(*) FROM messages
        WHERE session_id NOT IN (SELECT session_id FROM sessions)
    """)
    checks['orphaned_messages'] = cursor.fetchone()[0]

    # Message counts
    cursor = conn.execute("""
        SELECT COUNT(*) FROM sessions
        WHERE message_count != (
            SELECT COUNT(*) FROM messages WHERE session_id = sessions.session_id
        )
    """)
    checks['count_mismatches'] = cursor.fetchone()[0]

    # Integrity
    cursor = conn.execute("PRAGMA integrity_check")
    checks['database_integrity'] = cursor.fetchone()[0] == 'ok'

    conn.close()

    return {
        'healthy': all([
            checks['foreign_keys_enabled'],
            checks['orphaned_messages'] == 0,
            checks['count_mismatches'] == 0,
            checks['database_integrity']
        ]),
        'checks': checks
    }
```

---

## Transaction Safety

### Atomic Multi-Statement Operation

```python
def atomic_create_session(db_path, session_id, model_id, initial_message):
    """Create session and add first message atomically"""
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON")

    try:
        # Start explicit transaction
        conn.execute("BEGIN IMMEDIATE")

        # Insert session
        conn.execute(
            "INSERT INTO sessions (session_id, model_id) VALUES (?, ?)",
            (session_id, model_id)
        )

        # Insert message (trigger updates count)
        conn.execute(
            "INSERT INTO messages (session_id, sequence_number, role, content) "
            "VALUES (?, 1, 'user', ?)",
            (session_id, initial_message)
        )

        # Commit on success
        conn.commit()
        return True

    except Exception as e:
        # Rollback on any error
        conn.rollback()
        print(f"Transaction failed: {e}")
        return False

    finally:
        conn.close()
```

### Savepoint for Partial Rollback

```python
def batch_operation_with_savepoints(db_path, operations):
    """Rollback specific operations without losing others"""
    conn = sqlite3.connect(str(db_path))
    conn.execute("BEGIN")

    results = []

    for op_id, (sql, params) in enumerate(operations):
        conn.execute(f"SAVEPOINT sp_{op_id}")

        try:
            conn.execute(sql, params)
            results.append({'operation': op_id, 'status': 'success'})
        except Exception as e:
            # Rollback only this operation
            conn.execute(f"ROLLBACK TO sp_{op_id}")
            results.append({'operation': op_id, 'status': 'failed', 'error': str(e)})

    # Commit all successful operations
    conn.commit()
    conn.close()

    return results
```

---

## Performance Profiling

### Query Performance Analysis

```python
import sqlite3
import time

def profile_query(db_path, query, params=(), iterations=1):
    """Profile query execution time"""
    conn = sqlite3.connect(db_path)

    # Warm up
    conn.execute(query, params)

    # Measure
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        cursor = conn.execute(query, params)
        results = cursor.fetchall()
        elapsed = (time.perf_counter() - start) * 1000
        times.append(elapsed)

    conn.close()

    return {
        'min_ms': min(times),
        'max_ms': max(times),
        'avg_ms': sum(times) / len(times),
        'row_count': len(results)
    }
```

### Query Plan Analysis

```sql
-- Understand execution strategy
EXPLAIN QUERY PLAN
SELECT s.*, COUNT(m.message_id) as msg_count
FROM sessions s
LEFT JOIN messages m ON s.session_id = m.session_id
GROUP BY s.session_id
ORDER BY s.last_activity DESC
LIMIT 50;

-- Output analysis:
-- SCAN/SEARCH indicates table access
-- USING index_name means index is used (good)
-- TEMP B-TREE indicates sorting in memory
```

---

## Backup & Recovery

### Backup Strategy

```python
def create_backup(db_path, backup_dir):
    """Create complete database backup"""
    import datetime

    backup_dir.mkdir(exist_ok=True)
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = backup_dir / f"sessions_{timestamp}.db"

    source = sqlite3.connect(str(db_path))
    dest = sqlite3.connect(str(backup_path))

    # Use SQLite backup API
    source.backup(dest)

    source.close()
    dest.close()

    print(f"Backup created: {backup_path}")
    return backup_path

# Recommended: Daily automated backups
# Retention: Keep 30 days
# Testing: Weekly restore test
```

### Restore Procedure

```python
def restore_from_backup(backup_path, restore_to):
    """Restore database from backup"""
    if restore_to.exists():
        # Create safety copy
        restore_to.rename(str(restore_to) + '.pre_restore')

    source = sqlite3.connect(str(backup_path))
    dest = sqlite3.connect(str(restore_to))

    source.backup(dest)

    source.close()
    dest.close()

    # Verify integrity
    verify = sqlite3.connect(str(restore_to))
    cursor = verify.execute("PRAGMA integrity_check")
    result = cursor.fetchone()[0]
    verify.close()

    return result == 'ok'
```

---

## Maintenance Operations

### Database Optimization

```python
def optimize_database(db_path):
    """Run maintenance tasks"""
    conn = sqlite3.connect(str(db_path))

    print("Running database optimization...")

    # Update statistics (improves query planning)
    print("  - ANALYZE...", end='')
    conn.execute("ANALYZE")
    print(" done")

    # Rebuild indexes
    print("  - REINDEX...", end='')
    conn.execute("REINDEX")
    print(" done")

    # Reclaim space
    print("  - VACUUM...", end='')
    conn.execute("VACUUM")
    print(" done")

    conn.commit()
    conn.close()

    print("Optimization complete")
```

### Periodic Maintenance Schedule

```python
import schedule
import datetime

# Daily: ANALYZE (update statistics)
schedule.every().day.at("02:00").do(lambda: run_analyze(db_path))

# Weekly: REINDEX (rebuild indexes)
schedule.every().monday.at("03:00").do(lambda: run_reindex(db_path))

# Monthly: VACUUM (reclaim space)
schedule.every().month.do(lambda: run_vacuum(db_path))

# Daily: Backup
schedule.every().day.at("01:00").do(lambda: create_backup(db_path, backup_dir))

# Hourly: Health check
schedule.every().hour.do(lambda: database_health_check(db_path))
```

---

## Debugging Guide

### Enable Query Logging

```python
def enable_debug_logging(db_path):
    """Log all SQL for debugging"""
    conn = sqlite3.connect(str(db_path))

    def trace_callback(statement):
        print(f"[SQL] {statement}")

    conn.set_trace(trace_callback)
    return conn

# Usage
db = enable_debug_logging(".ai-router-sessions.db")
db.execute("SELECT * FROM sessions LIMIT 1")
# Output: [SQL] SELECT * FROM sessions LIMIT 1
```

### Check Database Size

```python
def analyze_database_size(db_path):
    """Analyze space usage"""
    conn = sqlite3.connect(str(db_path))

    # Get database size
    db_size = db_path.stat().st_size

    # Get table sizes
    cursor = conn.execute("""
        SELECT name, SUM(pgcount)*4096 as size_bytes
        FROM dbstat
        WHERE name NOT LIKE 'sqlite_%'
        GROUP BY name
        ORDER BY size_bytes DESC
    """)

    table_sizes = []
    for row in cursor.fetchall():
        size_mb = row[1] / 1024 / 1024
        table_sizes.append((row[0], size_mb))

    conn.close()

    return {
        'total_size_mb': db_size / 1024 / 1024,
        'table_sizes': table_sizes
    }
```

---

## Version Compatibility Matrix

| Feature | Min Version | Recommended | Note |
|---------|------------|-------------|------|
| Foreign Keys | 3.6.19 | 3.35+ | Working set mode default |
| WAL Mode | 3.7.0 | 3.35+ | Better concurrency |
| JSON Functions | 3.38.0 | 3.45+ | json_extract, etc |
| Window Functions | 3.25.0 | 3.35+ | ROW_NUMBER, PARTITION BY |
| RETURNING Clause | 3.35.0 | 3.45+ | INSERT RETURNING |
| FTS5 | 3.9.0 | 3.35+ | Full-text search |
| PRAGMA mmap_size | 3.7.11 | 3.35+ | Memory-mapped I/O |

Check version: `sqlite3 --version`

---

## Alert Thresholds

```python
ALERT_THRESHOLDS = {
    'orphaned_messages': {
        'warning': 1,
        'critical': 10
    },
    'count_mismatches': {
        'warning': 5,
        'critical': 100
    },
    'database_size_mb': {
        'warning': 1000,
        'critical': 5000
    },
    'avg_query_time_ms': {
        'warning': 100,
        'critical': 1000
    },
    'connection_pool_exhaustion': {
        'warning': 0.8,
        'critical': 0.95
    }
}
```

---

## Summary: Production Checklist

- [x] Foreign keys enabled in every connection
- [x] WAL mode configured
- [x] Connection pooling implemented
- [x] Message count triggers created
- [x] Health checks scheduled (hourly)
- [x] Backups automated (daily)
- [x] Performance monitoring enabled
- [x] Maintenance tasks scheduled
- [x] Alert thresholds configured
- [x] Recovery procedures tested

