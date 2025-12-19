#!/usr/bin/env python3
"""
Database Initialization Script for AI Router
Properly initializes all database schemas with correct PRAGMA settings
"""

import sqlite3
from pathlib import Path


def init_database(db_path: str = "D:/models/.ai-router-sessions.db"):
    """Initialize database with all schemas"""
    db_path = Path(db_path)
    base_path = db_path.parent

    print(f"Initializing database: {db_path}")

    # Connect and enable settings
    conn = sqlite3.connect(str(db_path))

    # CRITICAL: Enable WAL mode and foreign keys
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA synchronous=NORMAL")

    print("[OK] Enabled WAL mode and foreign keys")

    # Load and execute schema.sql
    schema_path = base_path / "schema.sql"
    if schema_path.exists():
        print(f"Loading schema: {schema_path}")
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        conn.executescript(schema_sql)
        conn.commit()
        print("[OK] Executed schema.sql")
    else:
        print(f"[WARN] Warning: {schema_path} not found")

    # Load and execute analytics_schema.sql
    analytics_path = base_path / "analytics_schema.sql"
    if analytics_path.exists():
        print(f"Loading analytics schema: {analytics_path}")
        with open(analytics_path, 'r') as f:
            analytics_sql = f.read()
        conn.executescript(analytics_sql)
        conn.commit()
        print("[OK] Executed analytics_schema.sql")
    else:
        print(f"[WARN] Warning: {analytics_path} not found")

    # Load and execute comparison_schema.sql
    comparison_path = base_path / "comparison_schema.sql"
    if comparison_path.exists():
        print(f"Loading comparison schema: {comparison_path}")
        with open(comparison_path, 'r') as f:
            comparison_sql = f.read()
        conn.executescript(comparison_sql)
        conn.commit()
        print("[OK] Executed comparison_schema.sql")
    else:
        print(f"[WARN] Warning: {comparison_path} not found")

    # Verify database structure
    cursor = conn.execute("""
        SELECT type, name FROM sqlite_master
        WHERE type IN ('table', 'view', 'index', 'trigger')
        ORDER BY type, name
    """)

    objects = {}
    for row in cursor.fetchall():
        obj_type = row[0]
        if obj_type not in objects:
            objects[obj_type] = []
        objects[obj_type].append(row[1])

    print("\n" + "="*60)
    print("DATABASE STRUCTURE SUMMARY")
    print("="*60)
    for obj_type in ['table', 'view', 'index', 'trigger']:
        if obj_type in objects:
            count = len(objects[obj_type])
            print(f"{obj_type.upper()}S: {count}")
            for name in objects[obj_type][:5]:  # Show first 5
                print(f"  - {name}")
            if count > 5:
                print(f"  ... and {count - 5} more")

    # Verify PRAGMA settings
    journal_mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
    foreign_keys = conn.execute("PRAGMA foreign_keys").fetchone()[0]

    print("\n" + "="*60)
    print("DATABASE CONFIGURATION")
    print("="*60)
    print(f"Journal Mode: {journal_mode}")
    print(f"Foreign Keys: {'Enabled' if foreign_keys else 'Disabled'}")
    print(f"Database Size: {db_path.stat().st_size / 1024:.2f} KB")
    print("="*60)

    conn.close()
    print("\n[OK] Database initialization complete!")


if __name__ == "__main__":
    init_database()
