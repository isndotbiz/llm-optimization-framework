-- Model Comparison Database Schema
-- Extends the AI Router session database with comparison-specific tables

-- Main comparison results table
CREATE TABLE IF NOT EXISTS comparison_results (
    comparison_id TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    prompt TEXT NOT NULL,
    model_count INTEGER NOT NULL,
    winner_model_id TEXT,
    notes TEXT
);

-- Individual model responses in a comparison
CREATE TABLE IF NOT EXISTS comparison_responses (
    response_id INTEGER PRIMARY KEY AUTOINCREMENT,
    comparison_id TEXT NOT NULL,
    model_id TEXT NOT NULL,
    model_name TEXT NOT NULL,
    response_text TEXT NOT NULL,
    tokens_input INTEGER DEFAULT 0,
    tokens_output INTEGER DEFAULT 0,
    duration_seconds REAL DEFAULT 0.0,
    rank INTEGER,
    FOREIGN KEY (comparison_id) REFERENCES comparison_results(comparison_id) ON DELETE CASCADE
);

-- Index for faster lookups
CREATE INDEX IF NOT EXISTS idx_comparison_timestamp ON comparison_results(created_at);
CREATE INDEX IF NOT EXISTS idx_comparison_model ON comparison_responses(model_id);
CREATE INDEX IF NOT EXISTS idx_comparison_responses ON comparison_responses(comparison_id);

-- View for recent comparisons with summary stats
CREATE VIEW IF NOT EXISTS recent_comparisons AS
SELECT
    c.comparison_id,
    c.created_at,
    c.prompt,
    c.model_count,
    c.winner_model_id,
    GROUP_CONCAT(r.model_name, ', ') as models_used,
    AVG(r.tokens_output) as avg_tokens,
    AVG(r.duration_seconds) as avg_duration
FROM comparison_results c
LEFT JOIN comparison_responses r ON c.comparison_id = r.comparison_id
GROUP BY c.comparison_id
ORDER BY c.created_at DESC;
