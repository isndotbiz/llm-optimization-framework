-- Analytics Schema Extension for AI Router
-- Additional views and indexes for performance analytics
-- SQLite 3.x compatible
-- Created: December 8, 2025

-- ============================================================================
-- ANALYTICS VIEWS
-- ============================================================================

-- Model Performance View
-- Aggregates usage statistics by model
CREATE VIEW IF NOT EXISTS model_performance AS
SELECT
    s.model_id,
    s.model_name,
    COUNT(DISTINCT s.session_id) as session_count,
    COUNT(m.message_id) as message_count,
    AVG(m.tokens_used) as avg_tokens,
    SUM(m.tokens_used) as total_tokens,
    AVG(m.duration_seconds) as avg_duration,
    SUM(m.duration_seconds) as total_duration,
    MIN(s.created_at) as first_used,
    MAX(s.last_activity) as last_used
FROM sessions s
LEFT JOIN messages m ON s.session_id = m.session_id
GROUP BY s.model_id, s.model_name
ORDER BY session_count DESC;

-- Daily Statistics View
-- Aggregates daily usage metrics
CREATE VIEW IF NOT EXISTS daily_stats AS
SELECT
    DATE(created_at) as date,
    COUNT(DISTINCT session_id) as session_count,
    COUNT(DISTINCT model_id) as models_used,
    SUM(message_count) as total_messages,
    SUM(total_tokens) as total_tokens,
    AVG(total_duration_seconds) as avg_duration
FROM sessions
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- Hourly Activity View
-- Shows usage patterns by hour of day
CREATE VIEW IF NOT EXISTS hourly_activity AS
SELECT
    CAST(strftime('%H', created_at) AS INTEGER) as hour,
    COUNT(*) as session_count,
    COUNT(DISTINCT model_id) as models_used,
    AVG(message_count) as avg_messages
FROM sessions
GROUP BY hour
ORDER BY hour;

-- Session Quality View
-- Analyzes session engagement metrics
CREATE VIEW IF NOT EXISTS session_quality AS
SELECT
    s.session_id,
    s.title,
    s.model_id,
    s.message_count,
    s.total_tokens,
    s.total_duration_seconds,
    ROUND(s.total_tokens * 1.0 / NULLIF(s.message_count, 0), 2) as tokens_per_message,
    ROUND(s.total_duration_seconds * 1.0 / NULLIF(s.message_count, 0), 2) as seconds_per_message,
    CASE
        WHEN s.message_count >= 10 THEN 'High Engagement'
        WHEN s.message_count >= 5 THEN 'Medium Engagement'
        ELSE 'Low Engagement'
    END as engagement_level
FROM sessions s
WHERE s.message_count > 0
ORDER BY s.last_activity DESC;

-- Token Usage Trends
-- Tracks token consumption over time
CREATE VIEW IF NOT EXISTS token_usage_trends AS
SELECT
    DATE(s.created_at) as date,
    s.model_id,
    SUM(m.tokens_used) as tokens_used,
    COUNT(m.message_id) as message_count,
    AVG(m.tokens_used) as avg_tokens_per_message
FROM sessions s
JOIN messages m ON s.session_id = m.session_id
WHERE m.tokens_used IS NOT NULL
GROUP BY DATE(s.created_at), s.model_id
ORDER BY date DESC, tokens_used DESC;

-- Response Time Analysis
-- Analyzes model response performance
CREATE VIEW IF NOT EXISTS response_time_analysis AS
SELECT
    s.model_id,
    COUNT(m.message_id) as response_count,
    AVG(m.duration_seconds) as avg_response_time,
    MIN(m.duration_seconds) as min_response_time,
    MAX(m.duration_seconds) as max_response_time,
    ROUND(AVG(m.tokens_used * 1.0 / NULLIF(m.duration_seconds, 0)), 2) as avg_tokens_per_second
FROM sessions s
JOIN messages m ON s.session_id = m.session_id
WHERE m.duration_seconds IS NOT NULL AND m.duration_seconds > 0
    AND m.role = 'assistant'
GROUP BY s.model_id
ORDER BY avg_response_time ASC;

-- User Interaction Patterns
-- Analyzes user message characteristics
CREATE VIEW IF NOT EXISTS user_interaction_patterns AS
SELECT
    DATE(m.timestamp) as date,
    COUNT(*) as user_messages,
    AVG(LENGTH(m.content)) as avg_message_length,
    AVG(m.tokens_used) as avg_tokens
FROM messages m
WHERE m.role = 'user'
GROUP BY DATE(m.timestamp)
ORDER BY date DESC;

-- Model Comparison View
-- Side-by-side comparison of model metrics
CREATE VIEW IF NOT EXISTS model_comparison AS
SELECT
    model_id,
    session_count,
    message_count,
    ROUND(avg_tokens, 2) as avg_tokens,
    total_tokens,
    ROUND(avg_duration, 2) as avg_response_seconds,
    ROUND(avg_tokens / NULLIF(avg_duration, 0), 2) as tokens_per_second,
    ROUND(message_count * 1.0 / NULLIF(session_count, 0), 2) as messages_per_session
FROM model_performance
ORDER BY session_count DESC;

-- ============================================================================
-- ANALYTICS INDEXES
-- ============================================================================
-- Additional indexes for analytics queries

-- Index for date-based queries
CREATE INDEX IF NOT EXISTS idx_sessions_date ON sessions(DATE(created_at));

-- Index for token-based queries
CREATE INDEX IF NOT EXISTS idx_messages_tokens ON messages(tokens_used)
    WHERE tokens_used IS NOT NULL;

-- Index for duration-based queries
CREATE INDEX IF NOT EXISTS idx_messages_duration ON messages(duration_seconds)
    WHERE duration_seconds IS NOT NULL;

-- Composite index for analytics queries
CREATE INDEX IF NOT EXISTS idx_sessions_analytics ON sessions(
    created_at, model_id, message_count, total_tokens
);

-- ============================================================================
-- OPTIONAL SCHEMA EXTENSIONS
-- ============================================================================
-- Uncomment these if you want to add timing columns for future use

-- Add response time tracking to messages
-- ALTER TABLE messages ADD COLUMN response_time_ms INTEGER;
-- CREATE INDEX IF NOT EXISTS idx_messages_response_time
--     ON messages(response_time_ms) WHERE response_time_ms IS NOT NULL;

-- Add session tags for categorization
-- CREATE TABLE IF NOT EXISTS session_tags (
--     tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
--     session_id TEXT NOT NULL,
--     tag TEXT NOT NULL,
--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
--     FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE,
--     UNIQUE(session_id, tag)
-- );
-- CREATE INDEX IF NOT EXISTS idx_session_tags ON session_tags(tag);

-- Add model version tracking
-- ALTER TABLE sessions ADD COLUMN model_version TEXT;
-- CREATE INDEX IF NOT EXISTS idx_sessions_version ON sessions(model_version);

-- ============================================================================
-- ANALYTICS HELPER FUNCTIONS (Implemented as Views)
-- ============================================================================

-- Top Sessions by Token Usage
CREATE VIEW IF NOT EXISTS top_sessions_by_tokens AS
SELECT
    s.session_id,
    s.title,
    s.model_id,
    s.total_tokens,
    s.message_count,
    s.created_at
FROM sessions s
ORDER BY s.total_tokens DESC
LIMIT 10;

-- Most Active Days
CREATE VIEW IF NOT EXISTS most_active_days AS
SELECT
    DATE(created_at) as date,
    COUNT(*) as session_count,
    SUM(message_count) as total_messages,
    SUM(total_tokens) as total_tokens
FROM sessions
GROUP BY DATE(created_at)
ORDER BY session_count DESC
LIMIT 10;

-- Model Diversity Score
-- Shows how many different models are being used
CREATE VIEW IF NOT EXISTS model_diversity AS
SELECT
    COUNT(DISTINCT model_id) as unique_models,
    COUNT(*) as total_sessions,
    ROUND(COUNT(DISTINCT model_id) * 100.0 / COUNT(*), 2) as diversity_percentage
FROM sessions;

-- ============================================================================
-- ANALYTICS METADATA
-- ============================================================================
-- Store analytics configuration and metadata

CREATE TABLE IF NOT EXISTS analytics_metadata (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert version info
INSERT OR REPLACE INTO analytics_metadata (key, value) VALUES
    ('schema_version', '1.0'),
    ('created_date', datetime('now')),
    ('description', 'Analytics schema for AI Router performance tracking');

-- ============================================================================
-- VACUUM AND OPTIMIZE
-- ============================================================================
-- Optimize database for analytics queries
-- Run these periodically for best performance

-- VACUUM;
-- ANALYZE;
