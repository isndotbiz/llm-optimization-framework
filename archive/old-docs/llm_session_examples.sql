-- ============================================================================
-- EXAMPLE QUERIES FOR LLM SESSION MANAGEMENT
-- ============================================================================
-- Common operations and analytics queries for the LLM session database
-- ============================================================================

-- ============================================================================
-- 1. SESSION CREATION & BASIC OPERATIONS
-- ============================================================================

-- Create a new model configuration
INSERT INTO models (provider, model_name, model_version, context_window, cost_per_1k_input_tokens, cost_per_1k_output_tokens)
VALUES ('anthropic', 'claude-3-opus', '20240229', 200000, 0.015, 0.075);

-- Create a new project
INSERT INTO projects (name, description)
VALUES ('Customer Support Bot', 'AI assistant for handling customer inquiries');

-- Start a new single session
INSERT INTO sessions (session_uuid, project_id, model_id, title, system_prompt, temperature)
VALUES (
    hex(randomblob(16)),
    1,
    1,
    'Debug Python Script',
    'You are an expert Python developer helping debug code.',
    0.7
);

-- Add a user message
INSERT INTO messages (message_uuid, session_id, sequence_number, role, content)
VALUES (
    hex(randomblob(16)),
    1,
    1,
    'user',
    'Help me fix this error: TypeError: unsupported operand type(s)'
);

-- Add an assistant response with metrics
INSERT INTO messages (
    message_uuid, session_id, sequence_number, role, content,
    model_id, input_tokens, output_tokens, cost, latency_ms, finish_reason
)
VALUES (
    hex(randomblob(16)),
    1,
    2,
    'assistant',
    'This error typically occurs when you try to perform an operation...',
    1,
    150,
    320,
    0.0264,  -- (150*0.015 + 320*0.075) / 1000
    2340,
    'stop'
);

-- ============================================================================
-- 2. SESSION RETRIEVAL & REPLAY
-- ============================================================================

-- Get full conversation history for a session
SELECT
    m.sequence_number,
    m.role,
    m.content,
    m.timestamp,
    m.latency_ms,
    m.input_tokens,
    m.output_tokens
FROM messages m
WHERE m.session_id = 1
ORDER BY m.sequence_number;

-- Get session with context (last N messages)
SELECT
    m.role,
    m.content,
    m.timestamp
FROM messages m
WHERE m.session_id = 1
ORDER BY m.sequence_number DESC
LIMIT 10;

-- Replay session from specific checkpoint
SELECT
    m.sequence_number,
    m.role,
    m.content
FROM messages m
WHERE m.session_id = 1
  AND m.sequence_number >= (
    SELECT sequence_number
    FROM session_snapshots
    WHERE session_id = 1
      AND snapshot_type = 'checkpoint'
    ORDER BY sequence_number DESC
    LIMIT 1
  )
ORDER BY m.sequence_number;

-- Get all sessions for a project
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
WHERE s.project_id = 1
ORDER BY s.started_at DESC;

-- Search sessions by content (using FTS)
SELECT DISTINCT
    s.session_uuid,
    s.title,
    snippet(messages_fts, 2, '<mark>', '</mark>', '...', 32) as snippet
FROM messages_fts
JOIN sessions s ON messages_fts.session_uuid = s.session_uuid
WHERE messages_fts MATCH 'python AND error'
ORDER BY rank
LIMIT 20;

-- ============================================================================
-- 3. COMPARISON & A/B TESTING
-- ============================================================================

-- Create a new comparison group
INSERT INTO comparison_groups (group_uuid, project_id, name, description, comparison_type)
VALUES (
    hex(randomblob(16)),
    1,
    'Model Comparison: GPT-4 vs Claude',
    'Compare response quality for technical questions',
    'model'
);

-- Create two sessions for comparison
INSERT INTO sessions (session_uuid, project_id, model_id, title, system_prompt)
VALUES
    (hex(randomblob(16)), 1, 1, 'Variant A: GPT-4', 'You are a helpful assistant.'),
    (hex(randomblob(16)), 1, 2, 'Variant B: Claude', 'You are a helpful assistant.');

-- Link sessions to comparison group
INSERT INTO comparison_sessions (comparison_group_id, session_id, variant_name, variant_config)
VALUES
    (1, 2, 'GPT-4', '{"model": "gpt-4", "temperature": 0.7}'),
    (1, 3, 'Claude', '{"model": "claude-3-opus", "temperature": 0.7}');

-- Record comparison results
INSERT INTO comparison_results (comparison_group_id, session_id, metric_name, metric_value, metric_unit, evaluator)
VALUES
    (1, 2, 'response_quality', 4.2, 'score', 'human'),
    (1, 3, 'response_quality', 4.7, 'score', 'human'),
    (1, 2, 'latency', 2340, 'ms', 'automated'),
    (1, 3, 'latency', 1890, 'ms', 'automated');

-- Compare results side by side
SELECT
    cs.variant_name,
    s.session_uuid,
    s.total_messages,
    s.total_cost,
    AVG(CASE WHEN cr.metric_name = 'response_quality' THEN cr.metric_value END) as avg_quality,
    AVG(CASE WHEN cr.metric_name = 'latency' THEN cr.metric_value END) as avg_latency_ms
FROM comparison_sessions cs
JOIN sessions s ON cs.session_id = s.id
LEFT JOIN comparison_results cr ON cs.session_id = cr.session_id
WHERE cs.comparison_group_id = 1
GROUP BY cs.variant_name, s.session_uuid;

-- Get messages from both variants for same prompt
SELECT
    cs.variant_name,
    m.role,
    m.content,
    m.latency_ms,
    m.cost
FROM comparison_sessions cs
JOIN messages m ON cs.session_id = m.session_id
WHERE cs.comparison_group_id = 1
  AND m.sequence_number <= 10
ORDER BY m.sequence_number, cs.variant_name;

-- Statistical comparison of variants
SELECT
    cs.variant_name,
    COUNT(DISTINCT cr.session_id) as sample_count,
    AVG(cr.metric_value) as avg_score,
    MIN(cr.metric_value) as min_score,
    MAX(cr.metric_value) as max_score,
    -- Standard deviation approximation
    AVG(cr.metric_value * cr.metric_value) - AVG(cr.metric_value) * AVG(cr.metric_value) as variance
FROM comparison_sessions cs
LEFT JOIN comparison_results cr ON cs.session_id = cr.session_id
WHERE cs.comparison_group_id = 1
  AND cr.metric_name = 'response_quality'
GROUP BY cs.variant_name;

-- ============================================================================
-- 4. BATCH JOBS
-- ============================================================================

-- Create a batch job
INSERT INTO batch_jobs (job_uuid, project_id, name, model_id, total_items, input_data)
VALUES (
    hex(randomblob(16)),
    1,
    'Summarize Product Reviews',
    1,
    100,
    json_array('review_1.txt', 'review_2.txt', 'review_3.txt')
);

-- Add batch items
INSERT INTO batch_items (batch_job_id, item_index, input_data, status)
VALUES
    (1, 0, '{"text": "Great product! Highly recommend."}', 'pending'),
    (1, 1, '{"text": "Not worth the price."}', 'pending'),
    (1, 2, '{"text": "Excellent quality and fast shipping."}', 'pending');

-- Update batch item with results
UPDATE batch_items
SET status = 'completed',
    result_data = json('{"summary": "Positive review highlighting quality and delivery speed."}'),
    completed_at = CURRENT_TIMESTAMP
WHERE batch_job_id = 1 AND item_index = 2;

-- Monitor batch job progress
SELECT
    bj.name,
    bj.status,
    bj.total_items,
    bj.completed_items,
    bj.failed_items,
    ROUND(100.0 * bj.completed_items / bj.total_items, 2) as completion_pct,
    bj.created_at,
    bj.started_at,
    bj.completed_at
FROM batch_jobs bj
WHERE bj.id = 1;

-- Get failed batch items for retry
SELECT
    bi.item_index,
    bi.input_data,
    bi.error_message,
    bi.started_at,
    bi.completed_at
FROM batch_items bi
WHERE bi.batch_job_id = 1
  AND bi.status = 'failed'
ORDER BY bi.item_index;

-- ============================================================================
-- 5. WORKFLOWS
-- ============================================================================

-- Create a workflow definition
INSERT INTO workflows (workflow_uuid, project_id, name, description, workflow_definition, status)
VALUES (
    hex(randomblob(16)),
    1,
    'Content Creation Pipeline',
    'Generate, review, and refine blog posts',
    json('{
        "steps": [
            {"name": "generate_outline", "model": "gpt-4", "prompt": "Create outline"},
            {"name": "write_draft", "model": "claude-3-opus", "prompt": "Write full draft"},
            {"name": "review", "model": "gpt-4", "prompt": "Review and suggest improvements"},
            {"name": "finalize", "model": "claude-3-opus", "prompt": "Apply improvements"}
        ]
    }'),
    'active'
);

-- Start workflow execution
INSERT INTO workflow_executions (execution_uuid, workflow_id, status, input_data)
VALUES (
    hex(randomblob(16)),
    1,
    'running',
    json('{"topic": "Best practices for Python async programming", "length": "1500 words"}')
);

-- Record workflow step completion
INSERT INTO workflow_steps (workflow_execution_id, step_name, step_index, session_id, status, output_data)
VALUES (
    1,
    'generate_outline',
    0,
    10,
    'completed',
    json('{"outline": "1. Introduction\n2. Understanding async/await\n3. Common patterns..."}')
);

-- Monitor workflow progress
SELECT
    we.execution_uuid,
    w.name as workflow_name,
    we.status,
    we.current_step,
    COUNT(ws.id) as completed_steps,
    json_extract(w.workflow_definition, '$.steps') as total_steps,
    we.started_at,
    we.completed_at
FROM workflow_executions we
JOIN workflows w ON we.workflow_id = w.id
LEFT JOIN workflow_steps ws ON we.id = ws.workflow_execution_id AND ws.status = 'completed'
WHERE we.id = 1
GROUP BY we.id;

-- Get detailed workflow execution history
SELECT
    ws.step_index,
    ws.step_name,
    ws.status,
    s.session_uuid,
    s.total_messages,
    s.total_cost,
    ws.started_at,
    ws.completed_at
FROM workflow_steps ws
LEFT JOIN sessions s ON ws.session_id = s.id
WHERE ws.workflow_execution_id = 1
ORDER BY ws.step_index;

-- ============================================================================
-- 6. ANALYTICS & REPORTING
-- ============================================================================

-- Daily usage summary
SELECT
    DATE(started_at) as date,
    COUNT(*) as sessions,
    SUM(total_messages) as total_messages,
    SUM(total_input_tokens + total_output_tokens) as total_tokens,
    SUM(total_cost) as total_cost,
    AVG(total_cost) as avg_cost_per_session
FROM sessions
WHERE started_at >= DATE('now', '-30 days')
GROUP BY DATE(started_at)
ORDER BY date DESC;

-- Model usage comparison
SELECT
    m.provider,
    m.model_name,
    COUNT(DISTINCT s.id) as session_count,
    COUNT(msg.id) as message_count,
    SUM(msg.input_tokens) as total_input_tokens,
    SUM(msg.output_tokens) as total_output_tokens,
    AVG(msg.latency_ms) as avg_latency_ms,
    SUM(msg.cost) as total_cost,
    AVG(msg.cost) as avg_cost_per_message
FROM models m
LEFT JOIN sessions s ON m.id = s.model_id
LEFT JOIN messages msg ON s.id = msg.session_id AND msg.role = 'assistant'
WHERE s.started_at >= DATE('now', '-30 days')
GROUP BY m.provider, m.model_name
ORDER BY total_cost DESC;

-- Top projects by activity
SELECT
    p.name,
    COUNT(DISTINCT s.id) as session_count,
    COUNT(DISTINCT m.id) as message_count,
    SUM(s.total_cost) as total_cost,
    MAX(s.started_at) as last_activity
FROM projects p
LEFT JOIN sessions s ON p.id = s.project_id
LEFT JOIN messages m ON s.id = m.session_id
GROUP BY p.id
ORDER BY session_count DESC
LIMIT 10;

-- Session performance percentiles
WITH session_metrics AS (
    SELECT
        total_messages,
        total_input_tokens + total_output_tokens as total_tokens,
        total_cost,
        CAST((julianday(completed_at) - julianday(started_at)) * 86400000 AS INTEGER) as duration_ms
    FROM sessions
    WHERE completed_at IS NOT NULL
      AND started_at >= DATE('now', '-30 days')
)
SELECT
    COUNT(*) as sample_count,
    -- Token usage
    AVG(total_tokens) as avg_tokens,
    MIN(total_tokens) as min_tokens,
    MAX(total_tokens) as max_tokens,
    (SELECT total_tokens FROM session_metrics ORDER BY total_tokens LIMIT 1 OFFSET (COUNT(*) / 2)) as median_tokens,
    -- Cost
    AVG(total_cost) as avg_cost,
    (SELECT total_cost FROM session_metrics ORDER BY total_cost LIMIT 1 OFFSET (COUNT(*) * 95 / 100)) as p95_cost,
    -- Duration
    AVG(duration_ms) as avg_duration_ms,
    (SELECT duration_ms FROM session_metrics ORDER BY duration_ms LIMIT 1 OFFSET (COUNT(*) * 95 / 100)) as p95_duration_ms
FROM session_metrics;

-- Error analysis
SELECT
    DATE(m.timestamp) as date,
    m.error_message,
    COUNT(*) as error_count,
    COUNT(DISTINCT m.session_id) as affected_sessions
FROM messages m
WHERE m.error_message IS NOT NULL
  AND m.timestamp >= DATE('now', '-7 days')
GROUP BY DATE(m.timestamp), m.error_message
ORDER BY error_count DESC;

-- Cost trends by hour of day
SELECT
    CAST(strftime('%H', started_at) AS INTEGER) as hour,
    COUNT(*) as session_count,
    SUM(total_cost) as total_cost,
    AVG(total_cost) as avg_cost
FROM sessions
WHERE started_at >= DATE('now', '-7 days')
GROUP BY hour
ORDER BY hour;

-- Token usage by message role
SELECT
    m.role,
    COUNT(*) as message_count,
    SUM(m.input_tokens) as total_input_tokens,
    SUM(m.output_tokens) as total_output_tokens,
    AVG(m.input_tokens) as avg_input_tokens,
    AVG(m.output_tokens) as avg_output_tokens
FROM messages m
JOIN sessions s ON m.session_id = s.id
WHERE s.started_at >= DATE('now', '-30 days')
GROUP BY m.role;

-- Longest running sessions
SELECT
    s.session_uuid,
    s.title,
    s.total_messages,
    s.total_cost,
    s.started_at,
    s.completed_at,
    CAST((julianday(COALESCE(s.completed_at, CURRENT_TIMESTAMP)) - julianday(s.started_at)) * 86400 AS INTEGER) as duration_seconds
FROM sessions s
ORDER BY duration_seconds DESC
LIMIT 20;

-- ============================================================================
-- 7. SESSION MANAGEMENT
-- ============================================================================

-- Complete a session
UPDATE sessions
SET status = 'completed',
    completed_at = CURRENT_TIMESTAMP
WHERE id = 1;

-- Archive old sessions
UPDATE sessions
SET status = 'archived'
WHERE completed_at < DATE('now', '-90 days')
  AND status = 'completed';

-- Create session snapshot for replay
INSERT INTO session_snapshots (session_id, snapshot_type, sequence_number, session_state, context_window)
SELECT
    1,
    'checkpoint',
    10,
    json_object(
        'session_id', s.id,
        'total_messages', s.total_messages,
        'total_tokens', s.total_input_tokens + s.total_output_tokens
    ),
    json_group_array(
        json_object(
            'sequence', m.sequence_number,
            'role', m.role,
            'content', m.content
        )
    )
FROM sessions s
JOIN messages m ON s.id = m.session_id
WHERE s.id = 1
  AND m.sequence_number <= 10
GROUP BY s.id;

-- Branch session from checkpoint
INSERT INTO sessions (session_uuid, project_id, model_id, title, system_prompt, parent_session_id, status)
SELECT
    hex(randomblob(16)),
    project_id,
    model_id,
    title || ' (Branch)',
    system_prompt,
    id,
    'active'
FROM sessions
WHERE id = 1;

-- Copy messages up to branch point
INSERT INTO messages (message_uuid, session_id, parent_message_id, sequence_number, role, content, model_id)
SELECT
    hex(randomblob(16)),
    (SELECT id FROM sessions WHERE parent_session_id = 1 ORDER BY id DESC LIMIT 1),
    parent_message_id,
    sequence_number,
    role,
    content,
    model_id
FROM messages
WHERE session_id = 1
  AND sequence_number <= 10;

-- ============================================================================
-- 8. ANNOTATIONS & FEEDBACK
-- ============================================================================

-- Add rating to a message
INSERT INTO annotations (annotation_uuid, entity_type, entity_id, annotation_type, rating, content, annotator)
VALUES (
    hex(randomblob(16)),
    'message',
    42,
    'rating',
    5,
    'Excellent response, very helpful!',
    'user@example.com'
);

-- Tag a session
INSERT INTO annotations (annotation_uuid, entity_type, entity_id, annotation_type, content, annotator)
VALUES (
    hex(randomblob(16)),
    'session',
    1,
    'tag',
    'debugging, python, production-issue',
    'admin'
);

-- Get all annotations for a session
SELECT
    a.annotation_type,
    a.rating,
    a.content,
    a.annotator,
    a.created_at
FROM annotations a
WHERE a.entity_type = 'session'
  AND a.entity_id = 1
ORDER BY a.created_at DESC;

-- Get average ratings by model
SELECT
    m.provider,
    m.model_name,
    COUNT(a.id) as rating_count,
    AVG(a.rating) as avg_rating,
    MIN(a.rating) as min_rating,
    MAX(a.rating) as max_rating
FROM annotations a
JOIN messages msg ON a.entity_type = 'message' AND a.entity_id = msg.id
JOIN sessions s ON msg.session_id = s.id
JOIN models m ON s.model_id = m.id
WHERE a.annotation_type = 'rating'
GROUP BY m.provider, m.model_name
ORDER BY avg_rating DESC;

-- ============================================================================
-- 9. PERFORMANCE METRICS AGGREGATION
-- ============================================================================

-- Record hourly metrics for a model
INSERT INTO performance_metrics (metric_type, entity_type, entity_id, metric_name, metric_value, metric_unit, period_start, period_end, sample_count)
SELECT
    'hourly',
    'model',
    m.id,
    'avg_latency_ms',
    AVG(msg.latency_ms),
    'ms',
    datetime(strftime('%Y-%m-%d %H:00:00', msg.timestamp)),
    datetime(strftime('%Y-%m-%d %H:59:59', msg.timestamp)),
    COUNT(msg.id)
FROM messages msg
JOIN sessions s ON msg.session_id = s.id
JOIN models m ON s.model_id = m.id
WHERE msg.timestamp >= datetime('now', '-1 hour')
  AND msg.role = 'assistant'
  AND msg.latency_ms IS NOT NULL
GROUP BY m.id, strftime('%Y-%m-%d %H', msg.timestamp);

-- Get performance trends
SELECT
    DATE(period_start) as date,
    metric_name,
    AVG(metric_value) as avg_value,
    MIN(metric_value) as min_value,
    MAX(metric_value) as max_value
FROM performance_metrics
WHERE entity_type = 'model'
  AND entity_id = 1
  AND period_start >= DATE('now', '-7 days')
GROUP BY DATE(period_start), metric_name
ORDER BY date DESC, metric_name;

-- ============================================================================
-- 10. CLEANUP & MAINTENANCE
-- ============================================================================

-- Delete old archived sessions (keep metadata, remove messages)
DELETE FROM messages
WHERE session_id IN (
    SELECT id FROM sessions
    WHERE status = 'archived'
      AND completed_at < DATE('now', '-365 days')
);

-- Vacuum database to reclaim space
VACUUM;

-- Analyze tables for query optimization
ANALYZE;

-- Check database integrity
PRAGMA integrity_check;

-- Get table sizes
SELECT
    name,
    SUM(pgsize) as total_size_bytes,
    ROUND(SUM(pgsize) / 1024.0 / 1024.0, 2) as total_size_mb
FROM dbstat
GROUP BY name
ORDER BY total_size_bytes DESC;

-- Find duplicate sessions (potential cleanup candidates)
SELECT
    title,
    system_prompt,
    COUNT(*) as duplicate_count,
    GROUP_CONCAT(id) as session_ids
FROM sessions
WHERE status = 'archived'
GROUP BY title, system_prompt
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC;
