-- AI Router Session Management Database Schema
-- SQLite 3.x compatible
-- Created: December 8, 2025

-- Enable WAL mode for better concurrent performance
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;
PRAGMA synchronous=NORMAL;

-- ============================================================================
-- SESSIONS TABLE
-- ============================================================================
-- Stores conversation session metadata
CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    model_id TEXT NOT NULL,
    model_name TEXT,
    title TEXT,                     -- Auto-generated from first message or user-provided
    message_count INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    total_duration_seconds REAL DEFAULT 0,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- MESSAGES TABLE
-- ============================================================================
-- Stores individual messages within sessions
CREATE TABLE IF NOT EXISTS messages (
    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    sequence_number INTEGER NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tokens_used INTEGER,
    duration_seconds REAL,
    metadata TEXT,                  -- JSON string for flexible metadata storage
    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE,
    UNIQUE(session_id, sequence_number)
);

-- ============================================================================
-- SESSION_METADATA TABLE
-- ============================================================================
-- Stores additional session-level key-value metadata
CREATE TABLE IF NOT EXISTS session_metadata (
    metadata_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE,
    UNIQUE(session_id, key)
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================
-- Sessions indexes
CREATE INDEX IF NOT EXISTS idx_sessions_created ON sessions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_sessions_updated ON sessions(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_sessions_model ON sessions(model_id);
CREATE INDEX IF NOT EXISTS idx_sessions_activity ON sessions(last_activity DESC);

-- Messages indexes
CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id, sequence_number);
CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_messages_role ON messages(role);

-- Metadata indexes
CREATE INDEX IF NOT EXISTS idx_metadata_session ON session_metadata(session_id);
CREATE INDEX IF NOT EXISTS idx_metadata_key ON session_metadata(key);

-- ============================================================================
-- FULL-TEXT SEARCH
-- ============================================================================
-- Enable full-text search on session titles and message content
CREATE VIRTUAL TABLE IF NOT EXISTS sessions_fts USING fts5(
    session_id UNINDEXED,
    title,
    content,
    tokenize='porter unicode61'
);

-- ============================================================================
-- TRIGGERS
-- ============================================================================
-- Automatically update session.updated_at when messages are added
CREATE TRIGGER IF NOT EXISTS update_session_timestamp
AFTER INSERT ON messages
BEGIN
    UPDATE sessions
    SET
        updated_at = CURRENT_TIMESTAMP,
        last_activity = CURRENT_TIMESTAMP,
        message_count = message_count + 1
    WHERE session_id = NEW.session_id;
END;

-- Decrement message count when messages are deleted
CREATE TRIGGER IF NOT EXISTS decrement_message_count
AFTER DELETE ON messages
BEGIN
    UPDATE sessions
    SET message_count = message_count - 1
    WHERE session_id = OLD.session_id;
END;

-- Keep FTS index synchronized with message inserts
CREATE TRIGGER IF NOT EXISTS sessions_fts_insert
AFTER INSERT ON messages
BEGIN
    INSERT INTO sessions_fts(session_id, title, content)
    SELECT
        NEW.session_id,
        s.title,
        NEW.content
    FROM sessions s
    WHERE s.session_id = NEW.session_id;
END;

-- Keep FTS index synchronized with message updates
CREATE TRIGGER IF NOT EXISTS sessions_fts_update
AFTER UPDATE ON messages
BEGIN
    DELETE FROM sessions_fts WHERE session_id = OLD.session_id;
    INSERT INTO sessions_fts(session_id, title, content)
    SELECT
        NEW.session_id,
        s.title,
        NEW.content
    FROM sessions s
    WHERE s.session_id = NEW.session_id;
END;

-- Keep FTS index synchronized with message deletes
CREATE TRIGGER IF NOT EXISTS sessions_fts_delete
AFTER DELETE ON messages
BEGIN
    DELETE FROM sessions_fts WHERE session_id = OLD.session_id;
END;

-- Auto-generate session title from first user message
CREATE TRIGGER IF NOT EXISTS auto_generate_title
AFTER INSERT ON messages
WHEN NEW.role = 'user' AND NEW.sequence_number = 1
BEGIN
    UPDATE sessions
    SET title = CASE
        WHEN LENGTH(NEW.content) > 60 THEN SUBSTR(NEW.content, 1, 60) || '...'
        ELSE NEW.content
    END
    WHERE session_id = NEW.session_id AND (title IS NULL OR title = '');
END;

-- ============================================================================
-- INITIAL DATA / VIEWS
-- ============================================================================
-- View for recent sessions with details
CREATE VIEW IF NOT EXISTS recent_sessions AS
SELECT
    s.session_id,
    s.title,
    s.model_id,
    s.model_name,
    s.message_count,
    s.total_tokens,
    s.total_duration_seconds,
    s.created_at,
    s.updated_at,
    s.last_activity,
    (SELECT content FROM messages
     WHERE session_id = s.session_id AND role = 'user'
     ORDER BY sequence_number ASC LIMIT 1) as first_prompt,
    (SELECT content FROM messages
     WHERE session_id = s.session_id
     ORDER BY sequence_number DESC LIMIT 1) as last_message
FROM sessions s
ORDER BY s.last_activity DESC;

-- View for session statistics
CREATE VIEW IF NOT EXISTS session_stats AS
SELECT
    model_id,
    COUNT(*) as session_count,
    SUM(message_count) as total_messages,
    SUM(total_tokens) as total_tokens,
    AVG(total_duration_seconds) as avg_duration,
    MIN(created_at) as first_session,
    MAX(last_activity) as last_session
FROM sessions
GROUP BY model_id;
