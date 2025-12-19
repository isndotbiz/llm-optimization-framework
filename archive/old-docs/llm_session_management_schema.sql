-- ============================================================================
-- LLM Session Management Database Schema for Python CLI Applications
-- ============================================================================
-- Best Practices Implementation:
-- - Uses TEXT for LLM responses (not BLOB) for searchability
-- - Comprehensive indexing for performance
-- - Supports sessions, comparisons, batch jobs, and workflows
-- - Optimized for analytics queries
-- - Designed for SQLite 3.35+ with JSON support
-- ============================================================================

-- Enable foreign keys (must be set per connection in SQLite)
PRAGMA foreign_keys = ON;

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- Projects/Workspaces
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSON -- Additional project-level metadata
);

CREATE INDEX idx_projects_name ON projects(name);
CREATE INDEX idx_projects_created_at ON projects(created_at DESC);

-- Models Configuration
CREATE TABLE models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider TEXT NOT NULL, -- 'openai', 'anthropic', 'ollama', etc.
    model_name TEXT NOT NULL, -- 'gpt-4', 'claude-3-opus', etc.
    model_version TEXT, -- Specific version/snapshot
    endpoint_url TEXT, -- For local/custom endpoints
    api_key_name TEXT, -- Reference to environment variable
    default_temperature REAL DEFAULT 0.7,
    default_max_tokens INTEGER,
    default_top_p REAL,
    context_window INTEGER, -- Max context size in tokens
    supports_streaming BOOLEAN DEFAULT 1,
    supports_functions BOOLEAN DEFAULT 0,
    cost_per_1k_input_tokens REAL, -- For cost tracking
    cost_per_1k_output_tokens REAL,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSON, -- Provider-specific settings
    UNIQUE(provider, model_name, model_version)
);

CREATE INDEX idx_models_provider ON models(provider);
CREATE INDEX idx_models_active ON models(is_active) WHERE is_active = 1;

-- Sessions (Conversations)
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_uuid TEXT NOT NULL UNIQUE, -- For external references
    project_id INTEGER,
    session_type TEXT NOT NULL DEFAULT 'single', -- 'single', 'comparison', 'batch', 'workflow'
    title TEXT,
    description TEXT,
    model_id INTEGER,
    system_prompt TEXT, -- System/role prompt for this session
    temperature REAL,
    max_tokens INTEGER,
    top_p REAL,
    status TEXT DEFAULT 'active', -- 'active', 'completed', 'archived', 'failed'
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    total_messages INTEGER DEFAULT 0,
    total_input_tokens INTEGER DEFAULT 0,
    total_output_tokens INTEGER DEFAULT 0,
    total_cost REAL DEFAULT 0.0,
    parent_session_id INTEGER, -- For session branching
    tags JSON, -- Array of tags for categorization
    metadata JSON, -- Session-specific metadata
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL,
    FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE SET NULL,
    FOREIGN KEY (parent_session_id) REFERENCES sessions(id) ON DELETE SET NULL
);

CREATE INDEX idx_sessions_uuid ON sessions(session_uuid);
CREATE INDEX idx_sessions_project ON sessions(project_id);
CREATE INDEX idx_sessions_type ON sessions(session_type);
CREATE INDEX idx_sessions_status ON sessions(status);
CREATE INDEX idx_sessions_started_at ON sessions(started_at DESC);
CREATE INDEX idx_sessions_model ON sessions(model_id);
CREATE INDEX idx_sessions_parent ON sessions(parent_session_id);

-- Messages (Prompts and Responses)
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_uuid TEXT NOT NULL UNIQUE,
    session_id INTEGER NOT NULL,
    parent_message_id INTEGER, -- For threading/branching
    sequence_number INTEGER NOT NULL, -- Order within session
    role TEXT NOT NULL, -- 'system', 'user', 'assistant', 'function'
    content TEXT NOT NULL, -- The actual message content
    content_type TEXT DEFAULT 'text', -- 'text', 'json', 'code', 'markdown'
    model_id INTEGER, -- Model used for this specific message
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    input_tokens INTEGER,
    output_tokens INTEGER,
    cost REAL,
    latency_ms INTEGER, -- Response time in milliseconds
    finish_reason TEXT, -- 'stop', 'length', 'function_call', etc.
    function_call JSON, -- Function call data if applicable
    tool_calls JSON, -- Tool/function calls made
    error_message TEXT, -- Error if message failed
    metadata JSON, -- Message-specific metadata (headers, etc.)
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE,
    FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE SET NULL,
    FOREIGN KEY (parent_message_id) REFERENCES messages(id) ON DELETE SET NULL,
    UNIQUE(session_id, sequence_number)
);

CREATE INDEX idx_messages_uuid ON messages(message_uuid);
CREATE INDEX idx_messages_session ON messages(session_id);
CREATE INDEX idx_messages_timestamp ON messages(timestamp DESC);
CREATE INDEX idx_messages_role ON messages(role);
CREATE INDEX idx_messages_parent ON messages(parent_message_id);
CREATE INDEX idx_messages_session_sequence ON messages(session_id, sequence_number);

-- ============================================================================
-- COMPARISON & A/B TESTING TABLES
-- ============================================================================

-- Comparison Groups (for A/B testing)
CREATE TABLE comparison_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_uuid TEXT NOT NULL UNIQUE,
    project_id INTEGER,
    name TEXT NOT NULL,
    description TEXT,
    comparison_type TEXT DEFAULT 'model', -- 'model', 'prompt', 'parameter', 'mixed'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    metadata JSON,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL
);

CREATE INDEX idx_comparison_groups_uuid ON comparison_groups(group_uuid);
CREATE INDEX idx_comparison_groups_project ON comparison_groups(project_id);
CREATE INDEX idx_comparison_groups_created_at ON comparison_groups(created_at DESC);

-- Comparison Sessions (links sessions to comparison groups)
CREATE TABLE comparison_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    comparison_group_id INTEGER NOT NULL,
    session_id INTEGER NOT NULL,
    variant_name TEXT, -- 'A', 'B', 'baseline', 'variant_1', etc.
    variant_config JSON, -- Configuration differences for this variant
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (comparison_group_id) REFERENCES comparison_groups(id) ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE,
    UNIQUE(comparison_group_id, session_id)
);

CREATE INDEX idx_comparison_sessions_group ON comparison_sessions(comparison_group_id);
CREATE INDEX idx_comparison_sessions_session ON comparison_sessions(session_id);

-- Comparison Results (evaluations and ratings)
CREATE TABLE comparison_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    comparison_group_id INTEGER NOT NULL,
    session_id INTEGER,
    message_id INTEGER,
    metric_name TEXT NOT NULL, -- 'quality', 'relevance', 'latency', 'cost', etc.
    metric_value REAL,
    metric_unit TEXT, -- 'score', 'ms', 'usd', 'tokens', etc.
    evaluator TEXT, -- 'human', 'llm_judge', 'automated', etc.
    notes TEXT,
    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSON,
    FOREIGN KEY (comparison_group_id) REFERENCES comparison_groups(id) ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE,
    FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE CASCADE
);

CREATE INDEX idx_comparison_results_group ON comparison_results(comparison_group_id);
CREATE INDEX idx_comparison_results_session ON comparison_results(session_id);
CREATE INDEX idx_comparison_results_metric ON comparison_results(metric_name);

-- ============================================================================
-- BATCH JOBS & WORKFLOWS
-- ============================================================================

-- Batch Jobs (for processing multiple prompts)
CREATE TABLE batch_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_uuid TEXT NOT NULL UNIQUE,
    project_id INTEGER,
    name TEXT NOT NULL,
    description TEXT,
    job_type TEXT DEFAULT 'standard', -- 'standard', 'evaluation', 'benchmark', etc.
    model_id INTEGER,
    input_source TEXT, -- 'file', 'database', 'api', etc.
    input_data JSON, -- Input prompts or references
    status TEXT DEFAULT 'pending', -- 'pending', 'running', 'completed', 'failed', 'cancelled'
    total_items INTEGER DEFAULT 0,
    completed_items INTEGER DEFAULT 0,
    failed_items INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    metadata JSON,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL,
    FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE SET NULL
);

CREATE INDEX idx_batch_jobs_uuid ON batch_jobs(job_uuid);
CREATE INDEX idx_batch_jobs_project ON batch_jobs(project_id);
CREATE INDEX idx_batch_jobs_status ON batch_jobs(status);
CREATE INDEX idx_batch_jobs_created_at ON batch_jobs(created_at DESC);

-- Batch Items (individual items in a batch job)
CREATE TABLE batch_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_job_id INTEGER NOT NULL,
    session_id INTEGER, -- Links to created session
    item_index INTEGER NOT NULL,
    input_data JSON, -- Specific input for this item
    status TEXT DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed'
    result_data JSON, -- Output/result data
    error_message TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (batch_job_id) REFERENCES batch_jobs(id) ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE SET NULL,
    UNIQUE(batch_job_id, item_index)
);

CREATE INDEX idx_batch_items_job ON batch_items(batch_job_id);
CREATE INDEX idx_batch_items_session ON batch_items(session_id);
CREATE INDEX idx_batch_items_status ON batch_items(status);

-- Workflows (multi-step processes)
CREATE TABLE workflows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workflow_uuid TEXT NOT NULL UNIQUE,
    project_id INTEGER,
    name TEXT NOT NULL,
    description TEXT,
    workflow_definition JSON NOT NULL, -- DAG or step definition
    status TEXT DEFAULT 'draft', -- 'draft', 'active', 'archived'
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSON,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL
);

CREATE INDEX idx_workflows_uuid ON workflows(workflow_uuid);
CREATE INDEX idx_workflows_project ON workflows(project_id);
CREATE INDEX idx_workflows_status ON workflows(status);

-- Workflow Executions
CREATE TABLE workflow_executions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_uuid TEXT NOT NULL UNIQUE,
    workflow_id INTEGER NOT NULL,
    status TEXT DEFAULT 'pending', -- 'pending', 'running', 'completed', 'failed', 'cancelled'
    input_data JSON,
    output_data JSON,
    current_step TEXT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    metadata JSON,
    FOREIGN KEY (workflow_id) REFERENCES workflows(id) ON DELETE CASCADE
);

CREATE INDEX idx_workflow_executions_uuid ON workflow_executions(execution_uuid);
CREATE INDEX idx_workflow_executions_workflow ON workflow_executions(workflow_id);
CREATE INDEX idx_workflow_executions_status ON workflow_executions(status);
CREATE INDEX idx_workflow_executions_started_at ON workflow_executions(started_at DESC);

-- Workflow Steps (links sessions to workflow executions)
CREATE TABLE workflow_steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workflow_execution_id INTEGER NOT NULL,
    step_name TEXT NOT NULL,
    step_index INTEGER NOT NULL,
    session_id INTEGER,
    status TEXT DEFAULT 'pending', -- 'pending', 'running', 'completed', 'failed', 'skipped'
    input_data JSON,
    output_data JSON,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    FOREIGN KEY (workflow_execution_id) REFERENCES workflow_executions(id) ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE SET NULL,
    UNIQUE(workflow_execution_id, step_index)
);

CREATE INDEX idx_workflow_steps_execution ON workflow_steps(workflow_execution_id);
CREATE INDEX idx_workflow_steps_session ON workflow_steps(session_id);
CREATE INDEX idx_workflow_steps_status ON workflow_steps(status);

-- ============================================================================
-- PERFORMANCE METRICS & ANALYTICS
-- ============================================================================

-- Performance Metrics (aggregated metrics)
CREATE TABLE performance_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_type TEXT NOT NULL, -- 'session', 'model', 'daily', 'hourly', etc.
    entity_type TEXT, -- 'session', 'model', 'project', 'global'
    entity_id INTEGER, -- ID of the entity being measured
    metric_name TEXT NOT NULL,
    metric_value REAL NOT NULL,
    metric_unit TEXT,
    period_start TIMESTAMP,
    period_end TIMESTAMP,
    sample_count INTEGER, -- Number of samples in aggregation
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSON
);

CREATE INDEX idx_performance_metrics_type ON performance_metrics(metric_type);
CREATE INDEX idx_performance_metrics_entity ON performance_metrics(entity_type, entity_id);
CREATE INDEX idx_performance_metrics_name ON performance_metrics(metric_name);
CREATE INDEX idx_performance_metrics_period ON performance_metrics(period_start, period_end);

-- Session Snapshots (for session replay)
CREATE TABLE session_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    snapshot_type TEXT DEFAULT 'checkpoint', -- 'checkpoint', 'branch_point', 'error_state'
    sequence_number INTEGER NOT NULL, -- Message sequence at snapshot
    session_state JSON NOT NULL, -- Complete session state
    context_window JSON, -- Messages in context at this point
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE,
    UNIQUE(session_id, sequence_number)
);

CREATE INDEX idx_session_snapshots_session ON session_snapshots(session_id);
CREATE INDEX idx_session_snapshots_type ON session_snapshots(snapshot_type);
CREATE INDEX idx_session_snapshots_created_at ON session_snapshots(created_at DESC);

-- Annotations (user feedback and notes)
CREATE TABLE annotations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    annotation_uuid TEXT NOT NULL UNIQUE,
    entity_type TEXT NOT NULL, -- 'session', 'message', 'comparison', etc.
    entity_id INTEGER NOT NULL,
    annotation_type TEXT NOT NULL, -- 'rating', 'tag', 'note', 'correction', etc.
    content TEXT,
    rating INTEGER, -- 1-5 stars or similar
    annotator TEXT, -- Username or identifier
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSON
);

CREATE INDEX idx_annotations_uuid ON annotations(annotation_uuid);
CREATE INDEX idx_annotations_entity ON annotations(entity_type, entity_id);
CREATE INDEX idx_annotations_type ON annotations(annotation_type);
CREATE INDEX idx_annotations_created_at ON annotations(created_at DESC);

-- ============================================================================
-- TRIGGERS FOR AUTOMATIC UPDATES
-- ============================================================================

-- Update projects.updated_at on modification
CREATE TRIGGER update_projects_timestamp
AFTER UPDATE ON projects
BEGIN
    UPDATE projects SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Update sessions.total_messages on message insert
CREATE TRIGGER update_session_message_count
AFTER INSERT ON messages
BEGIN
    UPDATE sessions
    SET total_messages = total_messages + 1,
        total_input_tokens = total_input_tokens + COALESCE(NEW.input_tokens, 0),
        total_output_tokens = total_output_tokens + COALESCE(NEW.output_tokens, 0),
        total_cost = total_cost + COALESCE(NEW.cost, 0)
    WHERE id = NEW.session_id;
END;

-- Update batch_jobs progress on batch_items completion
CREATE TRIGGER update_batch_job_progress
AFTER UPDATE ON batch_items
WHEN NEW.status = 'completed' AND OLD.status != 'completed'
BEGIN
    UPDATE batch_jobs
    SET completed_items = completed_items + 1
    WHERE id = NEW.batch_job_id;
END;

-- Update batch_jobs failed count
CREATE TRIGGER update_batch_job_failures
AFTER UPDATE ON batch_items
WHEN NEW.status = 'failed' AND OLD.status != 'failed'
BEGIN
    UPDATE batch_jobs
    SET failed_items = failed_items + 1
    WHERE id = NEW.batch_job_id;
END;

-- Auto-complete batch job when all items done
CREATE TRIGGER auto_complete_batch_job
AFTER UPDATE ON batch_jobs
WHEN NEW.completed_items + NEW.failed_items >= NEW.total_items
     AND NEW.status = 'running'
     AND NEW.total_items > 0
BEGIN
    UPDATE batch_jobs
    SET status = 'completed',
        completed_at = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END;

-- Update workflows.updated_at
CREATE TRIGGER update_workflows_timestamp
AFTER UPDATE ON workflows
BEGIN
    UPDATE workflows SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Update annotations.updated_at
CREATE TRIGGER update_annotations_timestamp
AFTER UPDATE ON annotations
BEGIN
    UPDATE annotations SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Session Summary View
CREATE VIEW v_session_summary AS
SELECT
    s.id,
    s.session_uuid,
    s.title,
    s.session_type,
    s.status,
    p.name as project_name,
    m.provider || '/' || m.model_name as model_full_name,
    s.total_messages,
    s.total_input_tokens,
    s.total_output_tokens,
    s.total_cost,
    s.started_at,
    s.completed_at,
    CAST((julianday(COALESCE(s.completed_at, CURRENT_TIMESTAMP)) - julianday(s.started_at)) * 86400000 AS INTEGER) as duration_ms
FROM sessions s
LEFT JOIN projects p ON s.project_id = p.id
LEFT JOIN models m ON s.model_id = m.id;

-- Message Details View
CREATE VIEW v_message_details AS
SELECT
    m.id,
    m.message_uuid,
    s.session_uuid,
    s.title as session_title,
    m.sequence_number,
    m.role,
    m.content,
    m.timestamp,
    m.input_tokens,
    m.output_tokens,
    m.cost,
    m.latency_ms,
    mo.provider || '/' || mo.model_name as model_full_name
FROM messages m
JOIN sessions s ON m.session_id = s.id
LEFT JOIN models mo ON m.model_id = mo.id;

-- Comparison Summary View
CREATE VIEW v_comparison_summary AS
SELECT
    cg.id,
    cg.group_uuid,
    cg.name,
    cg.comparison_type,
    COUNT(DISTINCT cs.session_id) as variant_count,
    AVG(s.total_cost) as avg_cost,
    AVG(s.total_input_tokens + s.total_output_tokens) as avg_total_tokens,
    AVG(CAST((julianday(s.completed_at) - julianday(s.started_at)) * 86400000 AS INTEGER)) as avg_duration_ms,
    cg.created_at
FROM comparison_groups cg
LEFT JOIN comparison_sessions cs ON cg.id = cs.comparison_group_id
LEFT JOIN sessions s ON cs.session_id = s.id
GROUP BY cg.id;

-- Model Performance View
CREATE VIEW v_model_performance AS
SELECT
    m.id,
    m.provider,
    m.model_name,
    COUNT(DISTINCT s.id) as session_count,
    COUNT(msg.id) as message_count,
    SUM(msg.input_tokens) as total_input_tokens,
    SUM(msg.output_tokens) as total_output_tokens,
    AVG(msg.latency_ms) as avg_latency_ms,
    SUM(msg.cost) as total_cost
FROM models m
LEFT JOIN sessions s ON m.id = s.model_id
LEFT JOIN messages msg ON s.id = msg.session_id AND msg.role = 'assistant'
GROUP BY m.id;

-- Daily Statistics View
CREATE VIEW v_daily_stats AS
SELECT
    DATE(started_at) as date,
    COUNT(DISTINCT id) as session_count,
    SUM(total_messages) as total_messages,
    SUM(total_input_tokens) as total_input_tokens,
    SUM(total_output_tokens) as total_output_tokens,
    SUM(total_cost) as total_cost,
    AVG(total_cost) as avg_cost_per_session
FROM sessions
GROUP BY DATE(started_at)
ORDER BY date DESC;

-- ============================================================================
-- FULL-TEXT SEARCH (Optional - requires FTS5)
-- ============================================================================

-- Full-text search on message content
CREATE VIRTUAL TABLE messages_fts USING fts5(
    message_uuid UNINDEXED,
    session_uuid UNINDEXED,
    role,
    content,
    content='messages',
    content_rowid='id'
);

-- Triggers to keep FTS index in sync
CREATE TRIGGER messages_fts_insert AFTER INSERT ON messages BEGIN
    INSERT INTO messages_fts(rowid, message_uuid, session_uuid, role, content)
    SELECT NEW.id, NEW.message_uuid, s.session_uuid, NEW.role, NEW.content
    FROM sessions s WHERE s.id = NEW.session_id;
END;

CREATE TRIGGER messages_fts_delete AFTER DELETE ON messages BEGIN
    DELETE FROM messages_fts WHERE rowid = OLD.id;
END;

CREATE TRIGGER messages_fts_update AFTER UPDATE ON messages BEGIN
    DELETE FROM messages_fts WHERE rowid = OLD.id;
    INSERT INTO messages_fts(rowid, message_uuid, session_uuid, role, content)
    SELECT NEW.id, NEW.message_uuid, s.session_uuid, NEW.role, NEW.content
    FROM sessions s WHERE s.id = NEW.session_id;
END;
