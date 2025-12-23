#!/usr/bin/env python3
"""
LLM Session Database Setup and Migration Utilities

This module provides utilities for:
- Database initialization
- Schema migrations
- Database maintenance
- Backup and restore
"""

import sqlite3
import json
import shutil
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager
from typing import Optional, Dict, List, Any


class DatabaseSetup:
    """Database initialization and setup utilities"""

    def __init__(self, db_path: str = 'llm_sessions.db'):
        self.db_path = Path(db_path)
        self.schema_path = Path(__file__).parent / 'llm_session_management_schema.sql'

    @contextmanager
    def get_connection(self):
        """Get database connection with proper configuration"""
        conn = sqlite3.connect(str(self.db_path))
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

    def initialize(self, overwrite: bool = False):
        """
        Initialize database with schema

        Args:
            overwrite: If True, drops all tables and recreates them
        """
        if self.db_path.exists() and not overwrite:
            print(f"Database already exists at {self.db_path}")
            print("Use overwrite=True to recreate it")
            return False

        if not self.schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {self.schema_path}")

        print(f"Initializing database at {self.db_path}...")

        with self.get_connection() as conn:
            with open(self.schema_path, 'r') as f:
                schema_sql = f.read()
                conn.executescript(schema_sql)

        print("Database initialized successfully")
        self.optimize()
        return True

    def optimize(self):
        """Apply performance optimizations"""
        with self.get_connection() as conn:
            # WAL mode for better concurrency
            conn.execute("PRAGMA journal_mode = WAL")

            # Increase cache size to 64MB
            conn.execute("PRAGMA cache_size = -64000")

            # Use memory for temp tables
            conn.execute("PRAGMA temp_store = MEMORY")

            # Synchronous = NORMAL (faster, still safe with WAL)
            conn.execute("PRAGMA synchronous = NORMAL")

            # Memory-mapped I/O for better read performance
            conn.execute("PRAGMA mmap_size = 268435456")  # 256MB

            # Update statistics
            conn.execute("ANALYZE")

        print("Database optimized")

    def get_info(self) -> Dict[str, Any]:
        """Get database information"""
        with self.get_connection() as conn:
            # Get database size
            db_size = self.db_path.stat().st_size if self.db_path.exists() else 0

            # Get table counts
            cursor = conn.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)
            tables = [row['name'] for row in cursor.fetchall()]

            # Get counts for main tables
            counts = {}
            for table in ['sessions', 'messages', 'models', 'projects']:
                if table in tables:
                    cursor = conn.execute(f"SELECT COUNT(*) as count FROM {table}")
                    counts[table] = cursor.fetchone()['count']

            # Get schema version (if migrations table exists)
            version = None
            if 'schema_migrations' in tables:
                cursor = conn.execute("SELECT MAX(version) as version FROM schema_migrations")
                result = cursor.fetchone()
                version = result['version'] if result else 0

            # Get configuration
            cursor = conn.execute("PRAGMA journal_mode")
            journal_mode = cursor.fetchone()[0]

            cursor = conn.execute("PRAGMA page_size")
            page_size = cursor.fetchone()[0]

            return {
                'db_path': str(self.db_path),
                'db_size_bytes': db_size,
                'db_size_mb': round(db_size / 1024 / 1024, 2),
                'schema_version': version,
                'table_count': len(tables),
                'tables': tables,
                'counts': counts,
                'journal_mode': journal_mode,
                'page_size': page_size,
            }

    def backup(self, backup_path: Optional[str] = None) -> str:
        """
        Create database backup

        Args:
            backup_path: Path for backup file. If None, generates timestamped name.

        Returns:
            Path to backup file
        """
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found: {self.db_path}")

        if backup_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f"{self.db_path.stem}_backup_{timestamp}.db"

        backup_path = Path(backup_path)

        print(f"Creating backup: {backup_path}")

        # Use SQLite backup API for safe backup
        with sqlite3.connect(str(self.db_path)) as source:
            with sqlite3.connect(str(backup_path)) as dest:
                source.backup(dest)

        print(f"Backup created: {backup_path} ({backup_path.stat().st_size / 1024 / 1024:.2f} MB)")
        return str(backup_path)

    def restore(self, backup_path: str, overwrite: bool = False):
        """
        Restore from backup

        Args:
            backup_path: Path to backup file
            overwrite: If True, overwrites existing database
        """
        backup_path = Path(backup_path)

        if not backup_path.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_path}")

        if self.db_path.exists() and not overwrite:
            raise FileExistsError(
                f"Database already exists: {self.db_path}. Use overwrite=True to replace it."
            )

        print(f"Restoring from: {backup_path}")
        shutil.copy2(backup_path, self.db_path)
        print(f"Restored to: {self.db_path}")


class DatabaseMigration:
    """Database migration utilities"""

    def __init__(self, db_path: str = 'llm_sessions.db'):
        self.db_path = db_path
        self._ensure_migrations_table()

    @contextmanager
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _ensure_migrations_table(self):
        """Create migrations table if it doesn't exist"""
        with self.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version INTEGER PRIMARY KEY,
                    description TEXT,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def get_version(self) -> int:
        """Get current schema version"""
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT MAX(version) as version FROM schema_migrations")
            result = cursor.fetchone()
            return result['version'] if result['version'] is not None else 0

    def get_migrations(self) -> List[Dict[str, Any]]:
        """Get list of applied migrations"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT version, description, applied_at
                FROM schema_migrations
                ORDER BY version
            """)
            return [dict(row) for row in cursor.fetchall()]

    def apply_migration(self, version: int, description: str, sql: str) -> bool:
        """
        Apply a migration

        Args:
            version: Migration version number
            description: Migration description
            sql: SQL statements to execute

        Returns:
            True if migration was applied, False if already applied
        """
        current = self.get_version()

        if current >= version:
            print(f"Migration {version} already applied (current version: {current})")
            return False

        print(f"Applying migration {version}: {description}")

        with self.get_connection() as conn:
            # Execute migration SQL
            conn.executescript(sql)

            # Record migration
            conn.execute("""
                INSERT INTO schema_migrations (version, description)
                VALUES (?, ?)
            """, (version, description))

        print(f"Migration {version} applied successfully")
        return True

    def rollback_migration(self, version: int, rollback_sql: str):
        """
        Rollback a migration

        Args:
            version: Migration version to rollback
            rollback_sql: SQL to undo the migration
        """
        current = self.get_version()

        if current < version:
            print(f"Migration {version} not applied (current version: {current})")
            return False

        print(f"Rolling back migration {version}")

        with self.get_connection() as conn:
            # Execute rollback SQL
            conn.executescript(rollback_sql)

            # Remove migration record
            conn.execute("""
                DELETE FROM schema_migrations WHERE version = ?
            """, (version,))

        print(f"Migration {version} rolled back successfully")
        return True


class DatabaseMaintenance:
    """Database maintenance utilities"""

    def __init__(self, db_path: str = 'llm_sessions.db'):
        self.db_path = db_path

    @contextmanager
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def vacuum(self):
        """Reclaim unused space"""
        print("Running VACUUM...")
        with self.get_connection() as conn:
            conn.execute("VACUUM")
        print("VACUUM completed")

    def create_message_count_triggers(self):
        """
        Create triggers to automatically update message count on insert/delete
        
        This ensures message_count in sessions table stays accurate
        """
        print("Creating message count triggers...")
        
        with self.get_connection() as conn:
            # Trigger for INSERT on messages table
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS update_message_count_insert
                AFTER INSERT ON messages
                BEGIN
                    UPDATE sessions 
                    SET total_messages = total_messages + 1
                    WHERE session_id = NEW.session_id;
                END;
            """)
            
            # Trigger for DELETE on messages table
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS update_message_count_delete
                AFTER DELETE ON messages
                BEGIN
                    UPDATE sessions 
                    SET total_messages = MAX(0, total_messages - 1)
                    WHERE session_id = OLD.session_id;
                END;
            """)
            
        print("Message count triggers created successfully")

    def analyze(self):
        """Update query planner statistics"""
        print("Running ANALYZE...")
        with self.get_connection() as conn:
            conn.execute("ANALYZE")
        print("ANALYZE completed")

    def integrity_check(self) -> bool:
        """Check database integrity"""
        print("Checking database integrity...")
        with self.get_connection() as conn:
            cursor = conn.execute("PRAGMA integrity_check")
            result = cursor.fetchone()[0]

            if result == 'ok':
                print("Integrity check passed")
                return True
            else:
                print(f"Integrity check FAILED: {result}")
                return False

    def get_table_sizes(self) -> List[Dict[str, Any]]:
        """Get size of each table"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT
                    name,
                    SUM(pgsize) as total_bytes,
                    ROUND(SUM(pgsize) / 1024.0 / 1024.0, 2) as total_mb
                FROM dbstat
                WHERE name NOT LIKE 'sqlite_%'
                GROUP BY name
                ORDER BY total_bytes DESC
            """)
            return [dict(row) for row in cursor.fetchall()]

    def archive_old_sessions(self, days: int = 90):
        """
        Archive sessions older than specified days

        Args:
            days: Archive sessions completed more than this many days ago
        """
        print(f"Archiving sessions older than {days} days...")

        with self.get_connection() as conn:
            cursor = conn.execute("""
                UPDATE sessions
                SET status = 'archived'
                WHERE status = 'completed'
                  AND completed_at < datetime('now', '-' || ? || ' days')
            """, (days,))

            count = cursor.rowcount

        print(f"Archived {count} sessions")
        return count

    def delete_archived_messages(self, days: int = 365):
        """
        Delete messages from archived sessions

        Args:
            days: Delete messages from sessions archived more than this many days ago
        """
        print(f"Deleting messages from sessions archived {days}+ days ago...")

        with self.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM messages
                WHERE session_id IN (
                    SELECT id FROM sessions
                    WHERE status = 'archived'
                      AND completed_at < datetime('now', '-' || ? || ' days')
                )
            """, (days,))

            count = cursor.rowcount

        print(f"Deleted {count} messages")
        return count

    def cleanup(self, archive_days: int = 90, delete_days: int = 365):
        """
        Full cleanup routine

        Args:
            archive_days: Archive sessions older than this
            delete_days: Delete messages from sessions archived longer than this
        """
        print("Starting cleanup...")

        self.archive_old_sessions(archive_days)
        self.delete_archived_messages(delete_days)
        self.analyze()
        self.vacuum()
        self.integrity_check()

        print("Cleanup completed")


# Example migrations
MIGRATIONS = [
    {
        'version': 1,
        'description': 'Add user_id column to sessions',
        'sql': """
            ALTER TABLE sessions ADD COLUMN user_id TEXT;
            CREATE INDEX idx_sessions_user ON sessions(user_id);
        """,
        'rollback': """
            DROP INDEX IF EXISTS idx_sessions_user;
            -- Note: SQLite doesn't support DROP COLUMN, would need table recreation
        """
    },
    {
        'version': 2,
        'description': 'Add embeddings table for vector search',
        'sql': """
            CREATE TABLE embeddings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER NOT NULL,
                embedding BLOB NOT NULL,
                model TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE CASCADE
            );
            CREATE INDEX idx_embeddings_message ON embeddings(message_id);
        """,
        'rollback': """
            DROP TABLE IF EXISTS embeddings;
        """
    },
    {
        'version': 3,
        'description': 'Add session tags for better organization',
        'sql': """
            CREATE TABLE session_tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                tag TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE,
                UNIQUE(session_id, tag)
            );
            CREATE INDEX idx_session_tags_session ON session_tags(session_id);
            CREATE INDEX idx_session_tags_tag ON session_tags(tag);
        """,
        'rollback': """
            DROP TABLE IF EXISTS session_tags;
        """
    }
]


def main():
    """CLI for database setup and maintenance"""
    import argparse

    parser = argparse.ArgumentParser(description='LLM Session Database Setup and Maintenance')
    parser.add_argument('--db', default='llm_sessions.db', help='Database path')

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Initialize
    init_parser = subparsers.add_parser('init', help='Initialize database')
    init_parser.add_argument('--overwrite', action='store_true', help='Overwrite existing database')

    # Info
    subparsers.add_parser('info', help='Show database information')

    # Backup
    backup_parser = subparsers.add_parser('backup', help='Create backup')
    backup_parser.add_argument('--output', help='Backup file path')

    # Restore
    restore_parser = subparsers.add_parser('restore', help='Restore from backup')
    restore_parser.add_argument('backup_file', help='Backup file to restore')
    restore_parser.add_argument('--overwrite', action='store_true', help='Overwrite existing database')

    # Migration
    migrate_parser = subparsers.add_parser('migrate', help='Run migrations')
    migrate_parser.add_argument('--version', type=int, help='Migrate to specific version')

    # Maintenance
    maint_parser = subparsers.add_parser('maintenance', help='Run maintenance tasks')
    maint_parser.add_argument('--vacuum', action='store_true', help='Run VACUUM')
    maint_parser.add_argument('--analyze', action='store_true', help='Run ANALYZE')
    maint_parser.add_argument('--check', action='store_true', help='Integrity check')
    maint_parser.add_argument('--sizes', action='store_true', help='Show table sizes')
    maint_parser.add_argument('--cleanup', action='store_true', help='Full cleanup')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Execute command
    if args.command == 'init':
        setup = DatabaseSetup(args.db)
        setup.initialize(overwrite=args.overwrite)

    elif args.command == 'info':
        setup = DatabaseSetup(args.db)
        info = setup.get_info()
        print("\nDatabase Information:")
        print(f"  Path: {info['db_path']}")
        print(f"  Size: {info['db_size_mb']} MB")
        print(f"  Schema Version: {info['schema_version']}")
        print(f"  Journal Mode: {info['journal_mode']}")
        print(f"  Page Size: {info['page_size']}")
        print(f"\nTable Counts:")
        for table, count in info['counts'].items():
            print(f"  {table}: {count}")

    elif args.command == 'backup':
        setup = DatabaseSetup(args.db)
        backup_file = setup.backup(args.output)
        print(f"\nBackup created: {backup_file}")

    elif args.command == 'restore':
        setup = DatabaseSetup(args.db)
        setup.restore(args.backup_file, overwrite=args.overwrite)

    elif args.command == 'migrate':
        migration = DatabaseMigration(args.db)
        current = migration.get_version()
        print(f"Current schema version: {current}")

        if args.version:
            target = args.version
        else:
            target = max(m['version'] for m in MIGRATIONS)

        for mig in MIGRATIONS:
            if mig['version'] <= current:
                continue
            if mig['version'] > target:
                break

            migration.apply_migration(
                mig['version'],
                mig['description'],
                mig['sql']
            )

    elif args.command == 'maintenance':
        maint = DatabaseMaintenance(args.db)

        if args.vacuum:
            maint.vacuum()

        if args.analyze:
            maint.analyze()

        if args.check:
            maint.integrity_check()

        if args.sizes:
            sizes = maint.get_table_sizes()
            print("\nTable Sizes:")
            for table in sizes:
                print(f"  {table['name']}: {table['total_mb']} MB")

        if args.cleanup:
            maint.cleanup()

        if not any([args.vacuum, args.analyze, args.check, args.sizes, args.cleanup]):
            # Default: run all maintenance
            maint.integrity_check()
            maint.analyze()
            print("\nTable Sizes:")
            for table in maint.get_table_sizes():
                print(f"  {table['name']}: {table['total_mb']} MB")


if __name__ == '__main__':
    main()
