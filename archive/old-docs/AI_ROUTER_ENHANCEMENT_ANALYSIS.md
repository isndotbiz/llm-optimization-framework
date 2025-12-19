# AI Router Enhancement Analysis - Comprehensive Implementation Roadmap

**Date:** December 8, 2025
**Codebase Version:** ai-router.py v1.0 (922 lines)
**Analysis Status:** ✅ COMPLETE
**Features Analyzed:** 9 High-Priority Features

---

## EXECUTIVE SUMMARY

### Codebase Readiness Assessment

**Current State:**
- **Well-architected foundation** with clean separation of concerns (Colors, ModelDatabase, AIRouter classes)
- **Stateless execution model** - Each model run is independent, no session persistence
- **Minimal dependencies** - Only Python stdlib (no external packages currently)
- **7-option menu system** - Simple, functional, ready for expansion
- **Platform-agnostic design** - Supports Windows/WSL/macOS with automatic detection
- **Configuration persistence** - JSON-based config for bypass mode only

**Major Gaps Identified:**

| Gap | Impact | Complexity |
|-----|--------|------------|
| **No database/persistence layer** | HIGH | MEDIUM |
| **No multi-turn conversation support** | HIGH | MEDIUM |
| **No response capture mechanism** | HIGH | LOW |
| **Hardcoded model execution** | MEDIUM | LOW |
| **No template system** | MEDIUM | MEDIUM |
| **No analytics/metrics** | MEDIUM | MEDIUM |

**Overall Readiness:** 🟡 **MODERATE** - Solid foundation but requires significant enhancement

The codebase is ready for feature additions but will require:
1. **Database integration** (SQLite recommended - zero-config, local)
2. **Response capture refactoring** (subprocess output piping)
3. **Menu system expansion** (currently 7 options, will grow to 16+)
4. **Class refactoring** (add SessionManager, TemplateManager, etc.)

---

## FEATURE-BY-FEATURE ANALYSIS

### FEATURE 1: Session Management & Conversation History

**STATUS:** ❌ **NOT_STARTED** (Foundational requirement for 6 other features)

**IMPACT:** 🔴 **CRITICAL** - Enables Features 3, 5, 6, 7, 8, 9

#### EXISTING CODE TO MODIFY:

1. **Function:** `run_llamacpp_model()` at line 624
   - **Change:** Capture subprocess output to variable instead of streaming to console
   - **Before:** `subprocess.run(cmd, shell=True)` (return code only)
   - **After:** `subprocess.run(cmd, shell=True, capture_output=True, text=True)` (capture stdout/stderr)
   - **Additional:** Parse response, extract token count, calculate duration

2. **Function:** `run_mlx_model()` at line 675
   - **Change:** Same output capture modification
   - **Impact:** Both execution methods need consistent response handling

3. **Function:** `run_model()` at line 615
   - **Change:** Add session creation and response saving
   - **New logic:**
     ```python
     # Create session before execution
     session_id = self.session_manager.create_session(model_id, prompt)

     # Execute model (existing logic)
     if model_data['framework'] == 'mlx':
         result = self.run_mlx_model(model_data, prompt)
     else:
         result = self.run_llamacpp_model(model_data, prompt)

     # Save response to database
     self.session_manager.add_message(session_id, 'user', prompt)
     self.session_manager.add_message(session_id, 'assistant', result['response'], result['metadata'])
     ```

4. **Function:** `__init__()` at line 349
   - **Change:** Initialize SessionManager
   - **Addition:**
     ```python
     self.session_manager = SessionManager(self.models_dir / ".ai-router-sessions.db")
     ```

#### NEW CODE TO ADD:

1. **New Class:** `SessionManager`
   - **Location:** After line 343 (after ModelDatabase class, before AIRouter class)
   - **Purpose:** SQLite session management with full CRUD operations
   - **Dependencies:** `import sqlite3`, `from datetime import datetime`, `import uuid`
   - **Size:** ~300 lines
   - **Key Methods:**
     ```python
     create_session(model_id, initial_prompt) -> session_id
     add_message(session_id, role, content, metadata)
     get_session(session_id) -> dict
     list_sessions(limit, model_filter, date_range) -> List[dict]
     get_conversation(session_id) -> List[messages]
     delete_session(session_id)
     export_session(session_id, format='json|markdown|txt') -> str
     search_sessions(query) -> List[dict]
     ```

2. **New Function:** `view_session_history()` in AIRouter class
   - **Location:** After line 771 (after `view_parameters_guide`)
   - **Purpose:** Interactive session history browser with pagination
   - **Dependencies:** SessionManager instance
   - **Features:**
     - List last 20 sessions with timestamps, models, preview
     - View full conversation for selected session
     - Resume session (load context for next prompt)
     - Export session to file
     - Delete old sessions

3. **New Function:** `resume_session_mode()` in AIRouter class
   - **Location:** After `view_session_history()`
   - **Purpose:** Continue previous conversation with context
   - **Logic:**
     - Select session from history
     - Display conversation so far
     - Prompt for next message
     - Execute with full context (if model supports)

#### MENU INTEGRATION:

- **Add menu option:** `[8] 📜 View Session History`
- **Add menu option:** `[9] 🔄 Resume Session`
- **Menu function:** New `elif choice == "8": self.view_session_history()`
- **Menu function:** New `elif choice == "9": self.resume_session_mode()`

#### DATABASE CHANGES:

**New database:** `D:\models\.ai-router-sessions.db`

**Tables to create:**
```sql
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    model_id TEXT NOT NULL,
    model_name TEXT,
    title TEXT,  -- Auto-generated or user-provided
    message_count INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    total_duration_seconds REAL DEFAULT 0
);

CREATE TABLE messages (
    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    sequence_number INTEGER NOT NULL,
    role TEXT NOT NULL,  -- 'user' or 'assistant'
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tokens_used INTEGER,
    duration_seconds REAL,
    metadata JSON,  -- model params, temperature, etc.
    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
);

CREATE INDEX idx_sessions_created ON sessions(created_at DESC);
CREATE INDEX idx_sessions_model ON sessions(model_id);
CREATE INDEX idx_messages_session ON messages(session_id, sequence_number);

-- Full-text search
CREATE VIRTUAL TABLE sessions_fts USING fts5(
    session_id UNINDEXED,
    title,
    content
);
```

#### EXTERNAL DEPENDENCIES:

- **Library:** None (uses Python stdlib `sqlite3`)
- **Install:** Built-in with Python 3
- **Used for:** Session persistence, query, search

#### IMPLEMENTATION PRIORITY: **1** (Foundation for other features)

#### ESTIMATED COMPLEXITY: 🟡 **MEDIUM**
- Database schema: Simple (3 tables)
- Session manager: Straightforward CRUD
- Subprocess output capture: Moderate (need to parse llama.cpp output)
- UI integration: Simple (list + select pattern)

---

### FEATURE 2: Prompt Templates Library

**STATUS:** ❌ **NOT_STARTED**

**IMPACT:** 🟢 **HIGH** - Significant productivity boost, enables Feature 9

#### EXISTING CODE TO MODIFY:

1. **Function:** `auto_select_mode()` at line 567
   - **Change:** Add option to use template before executing
   - **New flow:**
     ```python
     prompt = input(f"{Colors.YELLOW}> {Colors.RESET}").strip()

     # NEW: Offer template usage
     use_template = input("Use prompt template? [y/N]: ").strip().lower()
     if use_template == 'y':
         template_prompt = self.template_manager.select_and_render()
         if template_prompt:
             prompt = template_prompt
     ```

2. **Function:** `__init__()` at line 349
   - **Change:** Initialize TemplateManager
   - **Addition:**
     ```python
     self.template_manager = TemplateManager(self.models_dir / "prompt-templates")
     ```

#### NEW CODE TO ADD:

1. **New Class:** `PromptTemplate`
   - **Location:** New file `D:\models\prompt_engine.py` (import into ai-router.py)
   - **Purpose:** YAML template with Jinja2 rendering
   - **Dependencies:** `import yaml`, `from jinja2 import Environment, Template`
   - **Size:** ~150 lines
   - **Attributes:**
     ```python
     metadata: dict  # name, id, category, description, variables
     system_prompt_template: str
     user_prompt_template: str
     examples: list
     recommended_models: list
     parameters: dict
     ```

2. **New Class:** `TemplateManager`
   - **Location:** `D:\models\prompt_engine.py`
   - **Purpose:** Load, manage, and render templates
   - **Dependencies:** `pathlib`, `yaml`, `jinja2`
   - **Size:** ~250 lines
   - **Key Methods:**
     ```python
     load_templates() -> Dict[str, PromptTemplate]
     get_template(template_id) -> PromptTemplate
     list_templates(category=None) -> List[PromptTemplate]
     search_templates(query) -> List[PromptTemplate]
     select_and_render() -> str  # Interactive selection
     create_template(name, category, ...) -> PromptTemplate
     ```

3. **New Class:** `InteractiveTemplateSelector`
   - **Location:** `D:\models\prompt_engine.py`
   - **Purpose:** CLI interface for template selection and variable collection
   - **Size:** ~100 lines
   - **Methods:**
     ```python
     select_template() -> PromptTemplate
     collect_variables(template) -> Dict
     preview_prompt(system, user) -> None
     ```

4. **New Function:** `template_mode()` in AIRouter class
   - **Location:** After line 613 (after `manual_select_mode`)
   - **Purpose:** Full template workflow (select → fill → preview → execute)
   - **Size:** ~50 lines

#### MENU INTEGRATION:

- **Add menu option:** `[10] 📝 Use Prompt Template`
- **Menu function:** `elif choice == "10": self.template_mode()`

#### DATABASE CHANGES:

**No database changes** - Templates stored as YAML files

**Directory structure:**
```
D:\models\prompt-templates\
├── coding/
│   ├── code_review.yaml
│   ├── bug_fix.yaml
│   ├── refactor.yaml
│   └── documentation.yaml
├── reasoning/
│   ├── math_solver.yaml
│   └── research_summary.yaml
├── creative/
│   ├── content_writer.yaml
│   └── brainstorm.yaml
└── metadata/
    └── template_registry.json
```

**Template file format (YAML + Jinja2):**
```yaml
metadata:
  name: "Code Review Assistant"
  id: "code_review_v1"
  category: "coding"
  description: "Performs code reviews"
  variables:
    - name: "code"
      type: "string"
      required: true
    - name: "language"
      type: "string"
      required: true
      default: "python"
  recommended_models:
    - qwen3-coder-30b
  parameters:
    temperature: 0.3

system_prompt: |
  You are an expert {{language}} code reviewer.

user_prompt: |
  Review this {{language}} code:
  ```{{language}}
  {{code}}
  ```
```

#### EXTERNAL DEPENDENCIES:

- **Library:** `PyYAML`
  - **Install:** `pip install pyyaml`
  - **Used for:** Template file loading
  - **Size:** ~150KB

- **Library:** `Jinja2`
  - **Install:** `pip install jinja2`
  - **Used for:** Variable substitution and template rendering
  - **Size:** ~250KB

#### IMPLEMENTATION PRIORITY: **3** (Can be done early, high value, independent)

#### ESTIMATED COMPLEXITY: 🟢 **LOW-MEDIUM**
- YAML parsing: Simple
- Jinja2 integration: Well-documented
- File structure: Straightforward
- UI: Standard select + input pattern

---

### FEATURE 3: Model Comparison Mode (A/B Testing)

**STATUS:** ❌ **NOT_STARTED**

**IMPACT:** 🟢 **HIGH** - Unique feature, helps users choose best model

**DEPENDENCIES:** ✅ **REQUIRES Feature 1** (Session Management for saving comparisons)

#### EXISTING CODE TO MODIFY:

1. **Function:** `run_model()` at line 615
   - **Change:** Make it return result instead of just executing
   - **Before:** Returns nothing
   - **After:** Returns dict with response, metadata, duration
   - **Reason:** Comparison mode needs to collect results from multiple models

2. **Class:** `ModelDatabase` at line 60
   - **Change:** None needed (already has all model metadata)
   - **Usage:** Comparison mode will use existing model database

#### NEW CODE TO ADD:

1. **New Function:** `comparison_mode()` in AIRouter class
   - **Location:** After line 613 (after `manual_select_mode`)
   - **Purpose:** Run same prompt through 2-4 models and compare
   - **Size:** ~150 lines
   - **Logic:**
     ```python
     def comparison_mode(self):
         # Select 2-4 models
         models_to_compare = self.select_multiple_models(min=2, max=4)

         # Get prompt
         prompt = input("Enter prompt to test: ")

         # Run through each model
         results = []
         for model_id in models_to_compare:
             print(f"Running {model_id}...")
             result = self.run_model(model_id, self.models[model_id], prompt)
             results.append(result)

         # Display comparison table
         self.display_comparison_table(results)

         # Save to comparison database
         comparison_id = self.session_manager.save_comparison(
             prompt, models_to_compare, results
         )

         # Export option
         export = input("Export comparison? [y/N]: ")
         if export == 'y':
             self.export_comparison(comparison_id, format='markdown')
     ```

2. **New Function:** `select_multiple_models()` in AIRouter class
   - **Location:** After `list_models()`
   - **Purpose:** Multi-select interface for model selection
   - **Size:** ~50 lines
   - **UI Pattern:** Checkbox-style selection (1,3,5 = models 1, 3, and 5)

3. **New Function:** `display_comparison_table()` in AIRouter class
   - **Location:** After `comparison_mode()`
   - **Purpose:** Format comparison results in readable table
   - **Size:** ~80 lines
   - **Output:**
     ```
     ╔══════════════════════════════════════════════════════╗
     ║  MODEL COMPARISON RESULTS                            ║
     ╚══════════════════════════════════════════════════════╝

     Prompt: "Explain quantum computing"

     ┌─────────────────────┬────────────┬──────────┬─────────┐
     │ Model               │ Time (s)   │ Tokens   │ Length  │
     ├─────────────────────┼────────────┼──────────┼─────────┤
     │ Qwen3 Coder 30B     │ 12.3       │ 450      │ 2,100   │
     │ Phi-4 14B           │ 8.1        │ 380      │ 1,850   │
     │ Llama 3.3 70B       │ 18.7       │ 520      │ 2,400   │
     └─────────────────────┴────────────┴──────────┴─────────┘

     [Full responses shown below with headers]
     ```

4. **New Function:** `export_comparison()` in AIRouter class
   - **Location:** After `display_comparison_table()`
   - **Purpose:** Export comparison to Markdown file
   - **Size:** ~60 lines
   - **Output file:** `D:\models\outputs\comparison_{timestamp}.md`

5. **New Methods in SessionManager:**
   - `save_comparison(prompt, models, results) -> comparison_id`
   - `get_comparison(comparison_id) -> dict`
   - `list_comparisons(limit=20) -> List[dict]`

#### MENU INTEGRATION:

- **Add menu option:** `[11] ⚖️  Compare Models (A/B Test)`
- **Menu function:** `elif choice == "11": self.comparison_mode()`

#### DATABASE CHANGES:

**New tables in `.ai-router-sessions.db`:**

```sql
CREATE TABLE comparison_groups (
    comparison_id TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    prompt TEXT NOT NULL,
    model_count INTEGER NOT NULL,
    winner_model_id TEXT  -- User can mark a winner
);

CREATE TABLE comparison_results (
    result_id INTEGER PRIMARY KEY AUTOINCREMENT,
    comparison_id TEXT NOT NULL,
    model_id TEXT NOT NULL,
    model_name TEXT NOT NULL,
    response TEXT NOT NULL,
    tokens_used INTEGER,
    duration_seconds REAL,
    response_length INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (comparison_id) REFERENCES comparison_groups(comparison_id) ON DELETE CASCADE
);

CREATE INDEX idx_comparisons_created ON comparison_groups(created_at DESC);
CREATE INDEX idx_comparison_results ON comparison_results(comparison_id);
```

#### EXTERNAL DEPENDENCIES:

- **Library:** None (uses stdlib only)
- **Install:** N/A
- **Used for:** Table formatting with built-in string methods

#### IMPLEMENTATION PRIORITY: **5** (After session management, medium value)

#### ESTIMATED COMPLEXITY: 🟡 **MEDIUM**
- Multi-select UI: Moderate
- Table formatting: Simple
- Sequential execution: Simple
- Export: Simple

---

### FEATURE 4: Response Post-Processing & Formatting

**STATUS:** ⚠️ **PARTIALLY_IMPLEMENTED**

**CURRENT CAPABILITY:**
- Responses are displayed to console (via subprocess streaming)
- NO capture mechanism currently exists
- NO post-processing options

**IMPACT:** 🟢 **MEDIUM** - Quality of life improvement

**DEPENDENCIES:** ✅ **REQUIRES Feature 1** (Response capture mechanism)

#### EXISTING CODE TO MODIFY:

1. **Function:** `run_llamacpp_model()` at line 624 AND `run_mlx_model()` at line 675
   - **Change:** Capture output AND show formatting menu after completion
   - **New flow:**
     ```python
     # Execute (with output capture)
     result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

     # Parse response from stdout
     response_text = self.parse_model_output(result.stdout)

     # Display response
     print(response_text)

     # NEW: Post-processing menu
     self.post_process_menu(response_text, model_data, prompt)
     ```

#### NEW CODE TO ADD:

1. **New Function:** `post_process_menu()` in AIRouter class
   - **Location:** After line 708 (after `run_mlx_model`)
   - **Purpose:** Interactive post-processing options after each response
   - **Size:** ~120 lines
   - **Options:**
     ```
     ╔═══════════════════════════════════════╗
     ║  RESPONSE POST-PROCESSING OPTIONS     ║
     ╚═══════════════════════════════════════╝

     [1] 💾 Save Raw Response
     [2] 📝 Save as Markdown
     [3] 💻 Extract Code Blocks
     [4] 📋 Copy to Clipboard
     [5] 📊 View Statistics
     [6] 🔧 Apply Filters
     [7] ↩️  Continue
     ```

2. **New Function:** `parse_model_output()` in AIRouter class
   - **Location:** Before `post_process_menu()`
   - **Purpose:** Extract actual response from llama.cpp verbose output
   - **Size:** ~40 lines
   - **Logic:** Parse between prompt and generation stats

3. **New Function:** `extract_code_blocks()` in AIRouter class
   - **Location:** After `post_process_menu()`
   - **Purpose:** Find all ```language...``` blocks and save separately
   - **Size:** ~50 lines
   - **Returns:** List of (language, code) tuples

4. **New Function:** `response_statistics()` in AIRouter class
   - **Location:** After `extract_code_blocks()`
   - **Purpose:** Calculate and display response metrics
   - **Size:** ~60 lines
   - **Metrics:**
     - Word count
     - Character count
     - Reading time (avg 200 words/min)
     - Code block count
     - Languages detected
     - Sentence count

5. **New Function:** `apply_filters()` in AIRouter class
   - **Location:** After `response_statistics()`
   - **Purpose:** Transform response text
   - **Size:** ~70 lines
   - **Filters:**
     - Strip markdown formatting
     - Remove code blocks
     - Extract only code blocks
     - Extract lists/bullet points
     - Convert to plain text

6. **New Function:** `save_response()` in AIRouter class
   - **Location:** After `apply_filters()`
   - **Purpose:** Save response to file with auto-naming
   - **Size:** ~40 lines
   - **Filename:** `response_{model_id}_{timestamp}.{ext}`
   - **Location:** `D:\models\outputs\`

#### MENU INTEGRATION:

- **No new main menu option** - Appears automatically after each model run
- **Can be bypassed** - Respects bypass_mode setting

#### DATABASE CHANGES:

**No new tables** - Uses existing sessions table to link saved files

**New metadata field in messages table:**
```sql
-- Add to existing messages.metadata JSON:
{
  "saved_files": [
    {"path": "outputs/response_qwen3_20251208_143022.md", "format": "markdown"},
    {"path": "outputs/code_block_1.py", "format": "code"}
  ],
  "statistics": {
    "word_count": 452,
    "char_count": 2100,
    "code_blocks": 2,
    "reading_time_minutes": 2.26
  }
}
```

#### EXTERNAL DEPENDENCIES:

- **Library:** `pyperclip` (optional, for clipboard support)
  - **Install:** `pip install pyperclip`
  - **Used for:** Copy to clipboard functionality
  - **Fallback:** If not installed, skip clipboard option
  - **Size:** ~50KB

#### IMPLEMENTATION PRIORITY: **4** (After session management, nice-to-have)

#### ESTIMATED COMPLEXITY: 🟢 **LOW**
- Output parsing: Simple regex/string operations
- File operations: Basic I/O
- Statistics: Simple counting
- Code block extraction: Regex
- Clipboard: Library handles complexity

---

### FEATURE 5: Batch Processing Mode

**STATUS:** ❌ **NOT_STARTED**

**IMPACT:** 🟡 **MEDIUM** - Power user feature, significant time savings

**DEPENDENCIES:** ✅ **REQUIRES Feature 1** (Session management for batch tracking)

#### EXISTING CODE TO MODIFY:

1. **Function:** `run_model()` at line 615
   - **Change:** Make it callable programmatically (currently assumes interactive mode)
   - **Modification:** Add `silent=False` parameter to suppress interactive prompts
   - **Reason:** Batch mode needs to call run_model() in a loop without user interaction

#### NEW CODE TO ADD:

1. **New Function:** `batch_mode()` in AIRouter class
   - **Location:** After line 613
   - **Purpose:** Process multiple prompts through selected model
   - **Size:** ~200 lines
   - **Flow:**
     ```python
     def batch_mode(self):
         # Select model
         model_id, model_data = self.select_model_for_batch()

         # Select input source
         batch_input = self.get_batch_input()

         # Configure batch options
         config = self.configure_batch_processing()

         # Process batch
         results = self.process_batch(
             batch_input,
             model_id,
             model_data,
             config
         )

         # Save results
         self.save_batch_results(results, config['output_format'])
     ```

2. **New Function:** `get_batch_input()` in AIRouter class
   - **Location:** After `batch_mode()`
   - **Purpose:** Load prompts from file, JSON, or paste mode
   - **Size:** ~80 lines
   - **Input modes:**
     - **File:** One prompt per line
     - **JSON:** Array of objects with prompt + params
     - **Paste:** Delimited by `---` separator
     - **CSV:** With columns: id, prompt, temperature, etc.

3. **New Function:** `process_batch()` in AIRouter class
   - **Location:** After `get_batch_input()`
   - **Purpose:** Execute batch with progress tracking
   - **Size:** ~150 lines
   - **Features:**
     - Progress bar with ETA (using custom tracker, no external deps)
     - Error handling (continue vs stop)
     - Resume capability (checkpoint every N tasks)
     - Statistics tracking

4. **New Function:** `save_batch_results()` in AIRouter class
   - **Location:** After `process_batch()`
   - **Purpose:** Export batch results in various formats
   - **Size:** ~100 lines
   - **Formats:**
     - Individual files (one per prompt)
     - Combined JSON (all results in single file)
     - CSV (tabular format)
     - Markdown report (formatted summary)

5. **New Class:** `BatchProgressTracker`
   - **Location:** New file `D:\models\batch_processor.py` (import into ai-router.py)
   - **Purpose:** Custom progress tracker with ETA calculation
   - **Dependencies:** stdlib only (no tqdm needed)
   - **Size:** ~80 lines
   - **Display:**
     ```
     [45/100] 45.0% | ✓ 42 ✗ 3 | Elapsed: 0:03:22 | ETA: 0:04:05
     ```

6. **New Class:** `BatchCheckpointManager`
   - **Location:** `D:\models\batch_processor.py`
   - **Purpose:** Resume interrupted batches
   - **Dependencies:** json, pathlib
   - **Size:** ~100 lines
   - **Methods:**
     ```python
     save_checkpoint(completed_ids, failed_ids, results)
     load_checkpoint() -> (completed_ids, failed_ids, results)
     is_completed(task_id) -> bool
     cleanup()
     ```

#### MENU INTEGRATION:

- **Add menu option:** `[12] 🔄 Batch Processing Mode`
- **Menu function:** `elif choice == "12": self.batch_mode()`

#### DATABASE CHANGES:

**New tables in `.ai-router-sessions.db`:**

```sql
CREATE TABLE batch_jobs (
    batch_id TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    model_id TEXT NOT NULL,
    total_tasks INTEGER NOT NULL,
    completed_tasks INTEGER DEFAULT 0,
    failed_tasks INTEGER DEFAULT 0,
    status TEXT DEFAULT 'running',  -- running, completed, failed, interrupted
    input_file TEXT,
    output_file TEXT,
    checkpoint_file TEXT
);

CREATE TABLE batch_items (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id TEXT NOT NULL,
    task_id TEXT NOT NULL,
    prompt TEXT NOT NULL,
    response TEXT,
    status TEXT DEFAULT 'pending',  -- pending, completed, failed
    error_message TEXT,
    tokens_used INTEGER,
    duration_seconds REAL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (batch_id) REFERENCES batch_jobs(batch_id) ON DELETE CASCADE
);

CREATE INDEX idx_batch_jobs_created ON batch_jobs(created_at DESC);
CREATE INDEX idx_batch_items ON batch_items(batch_id, status);
```

#### EXTERNAL DEPENDENCIES:

- **Library:** None (uses stdlib only)
- **Install:** N/A
- **Used for:** All functionality built with standard library

**Note:** Could optionally use `tqdm` or `rich` for prettier progress bars, but not required

#### IMPLEMENTATION PRIORITY: **6** (After core features, power user feature)

#### ESTIMATED COMPLEXITY: 🟡 **MEDIUM**
- Input parsing: Simple
- Batch loop: Straightforward
- Progress tracking: Custom implementation (moderate)
- Checkpoint: JSON-based (simple)
- Resume logic: Moderate

---

### FEATURE 6: Smart Model Auto-Selection Enhancement

**STATUS:** ⚠️ **PARTIALLY_IMPLEMENTED**

**CURRENT CAPABILITY:**
- ✅ Keyword-based use case detection (line 291-322)
- ✅ Basic recommendation engine (line 324-343)
- ❌ No learning from user selections
- ❌ No confidence scoring
- ❌ No preference database

**IMPACT:** 🟢 **HIGH** - Improves core UX, makes router "smarter"

**DEPENDENCIES:** ✅ **REQUIRES Feature 1** (Session database for tracking selections)

#### EXISTING CODE TO MODIFY:

1. **Function:** `detect_use_case()` at line 291
   - **Change:** Add confidence scoring and additional analysis
   - **Enhancement:**
     ```python
     @classmethod
     def detect_use_case(cls, prompt_text):
         """Enhanced detection with confidence scoring"""
         prompt_lower = prompt_text.lower()

         # Count matches per category
         matches = {
             'coding': sum(1 for kw in coding_keywords if kw in prompt_lower),
             'reasoning': sum(1 for kw in reasoning_keywords if kw in prompt_lower),
             'creative': sum(1 for kw in creative_keywords if kw in prompt_lower),
             'research': sum(1 for kw in research_keywords if kw in prompt_lower)
         }

         # Calculate confidence
         total_matches = sum(matches.values())
         if total_matches == 0:
             return "general", 0.0  # Low confidence

         top_category = max(matches, key=matches.get)
         confidence = matches[top_category] / total_matches

         return top_category, confidence
     ```

2. **Function:** `recommend_model()` at line 324
   - **Change:** Check user preferences before using hardcoded recommendations
   - **Enhancement:**
     ```python
     @classmethod
     def recommend_model(cls, use_case, platform_models, preference_db=None):
         """Recommend with user preference learning"""

         # Check preference database first
         if preference_db:
             preferred = preference_db.get_preferred_model(use_case)
             if preferred and preferred in platform_models:
                 return preferred, platform_models[preferred], "high"

         # Fall back to hardcoded recommendations
         for model_id in recommendations.get(use_case, []):
             if model_id in platform_models:
                 return model_id, platform_models[model_id], "medium"

         return list(platform_models.items())[0], "low"
     ```

3. **Function:** `auto_select_mode()` at line 567
   - **Change:** Show confidence and allow override
   - **Enhancement:**
     ```python
     # Detect use case with confidence
     use_case, confidence = ModelDatabase.detect_use_case(prompt)

     # Recommend model
     model_id, model_data, conf_level = ModelDatabase.recommend_model(
         use_case, self.models, self.preference_manager
     )

     # Show confidence
     print(f"Detected: {use_case.upper()} (confidence: {confidence:.0%})")
     print(f"Recommended: {model_data['name']} ({conf_level} confidence)")

     # Allow override if confidence is low
     if conf_level == "low":
         override = input("Confidence is low. Choose manually? [y/N]: ")
         if override == 'y':
             self.list_models()
             return

     # Track selection for learning
     if self._confirm("Run this model? [Y/n]:"):
         self.preference_manager.record_selection(prompt, use_case, model_id)
         self.run_model(model_id, model_data, prompt)
     ```

4. **Function:** `__init__()` at line 349
   - **Change:** Initialize PreferenceManager
   - **Addition:**
     ```python
     self.preference_manager = PreferenceManager(
         self.models_dir / ".ai-router-sessions.db"
     )
     ```

#### NEW CODE TO ADD:

1. **New Class:** `PreferenceManager`
   - **Location:** After SessionManager class (around line 400)
   - **Purpose:** Learn from user model selections
   - **Dependencies:** sqlite3, collections
   - **Size:** ~150 lines
   - **Methods:**
     ```python
     record_selection(prompt, use_case, model_id)
     get_preferred_model(use_case) -> model_id
     get_model_frequency(model_id) -> int
     analyze_prompt(prompt) -> dict  # Enhanced analysis
     get_analytics() -> dict
     ```

2. **New Function:** `analyze_prompt()` in ModelDatabase class
   - **Location:** After `detect_use_case()` (around line 323)
   - **Purpose:** Deep prompt analysis beyond keyword matching
   - **Size:** ~60 lines
   - **Analysis:**
     - Detect programming language (if code present)
     - Count questions
     - Measure length (short/medium/long)
     - Detect domain terms (math, medical, legal, etc.)
     - Identify intent (explain, create, debug, compare)

3. **New Function:** `view_auto_select_analytics()` in AIRouter class
   - **Location:** After `view_documentation()` (around line 885)
   - **Purpose:** Show auto-select success metrics
   - **Size:** ~80 lines
   - **Metrics:**
     - Most used models
     - Auto-select accuracy (% of times user doesn't override)
     - Use case distribution
     - Model preferences per use case

#### MENU INTEGRATION:

- **Add menu option:** `[13] 📊 Auto-Select Analytics`
- **Menu function:** `elif choice == "13": self.view_auto_select_analytics()`

#### DATABASE CHANGES:

**New tables in `.ai-router-sessions.db`:**

```sql
CREATE TABLE user_preferences (
    preference_id INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt_hash TEXT,  -- Hash of prompt for similarity matching
    use_case TEXT NOT NULL,
    selected_model_id TEXT NOT NULL,
    was_recommended BOOLEAN,  -- Did user accept recommendation?
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE prompt_analytics (
    analytics_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    prompt_text TEXT NOT NULL,
    detected_use_case TEXT,
    confidence_score REAL,
    detected_language TEXT,  -- programming language if applicable
    question_count INTEGER,
    word_count INTEGER,
    domain_terms JSON,  -- Array of detected domain terms
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);

CREATE INDEX idx_preferences_use_case ON user_preferences(use_case, selected_model_id);
CREATE INDEX idx_preferences_timestamp ON user_preferences(timestamp DESC);
CREATE INDEX idx_analytics_use_case ON prompt_analytics(detected_use_case);
```

#### EXTERNAL DEPENDENCIES:

- **Library:** None (uses stdlib only)
- **Install:** N/A
- **Used for:** All functionality with standard library

#### IMPLEMENTATION PRIORITY: **7** (Enhancement, depends on session management)

#### ESTIMATED COMPLEXITY: 🟢 **LOW-MEDIUM**
- Confidence scoring: Simple math
- Preference tracking: Basic database inserts
- Prompt analysis: String parsing and regex
- Analytics: SQL aggregation queries

---

### FEATURE 7: Performance Analytics Dashboard

**STATUS:** ❌ **NOT_STARTED**

**IMPACT:** 🟡 **MEDIUM** - Insights feature, helps optimize usage

**DEPENDENCIES:** ✅ **REQUIRES Feature 1** (Session database with metrics)

#### EXISTING CODE TO MODIFY:

**None** - This is entirely additive, uses existing session data

#### NEW CODE TO ADD:

1. **New Function:** `analytics_dashboard()` in AIRouter class
   - **Location:** After line 884 (after `view_documentation`)
   - **Purpose:** Interactive analytics menu
   - **Size:** ~250 lines
   - **Sections:**
     ```
     ╔══════════════════════════════════════════╗
     ║  PERFORMANCE ANALYTICS DASHBOARD         ║
     ╚══════════════════════════════════════════╝

     Time Period: Last 30 days

     [1] Model Usage Statistics
     [2] Performance Metrics
     [3] Cost Analysis
     [4] Usage Patterns (by hour/day)
     [5] Recommendations
     [6] Export Report
     [0] Back
     ```

2. **New Function:** `model_usage_stats()` in AIRouter class
   - **Location:** After `analytics_dashboard()`
   - **Purpose:** Show most-used models with ASCII bar chart
   - **Size:** ~100 lines
   - **Output:**
     ```
     Model Usage (Last 30 days)

     Qwen3 Coder 30B    ████████████████████ 45 uses (30%)
     Phi-4 14B          ████████████ 28 uses (19%)
     Llama 3.3 70B      ██████████ 22 uses (15%)
     Gemma3 27B         ████████ 18 uses (12%)
     Others             ████████████████ 37 uses (24%)

     Total Sessions: 150
     ```

3. **New Function:** `performance_metrics()` in AIRouter class
   - **Location:** After `model_usage_stats()`
   - **Purpose:** Speed and token analysis per model
   - **Size:** ~120 lines
   - **Metrics:**
     - Average tokens/second
     - Average response time
     - P95 response time
     - Total tokens processed
     - Success rate (% of non-failed runs)

4. **New Function:** `cost_analysis()` in AIRouter class
   - **Location:** After `performance_metrics()`
   - **Purpose:** Token costs and time investment
   - **Size:** ~80 lines
   - **Analysis:**
     - Total tokens used per model
     - Estimated cost (if using cloud APIs)
     - Time investment (total duration)
     - Cost per session
     - Most expensive models

5. **New Function:** `usage_patterns()` in AIRouter class
   - **Location:** After `cost_analysis()`
   - **Purpose:** Usage by time of day/day of week
   - **Size:** ~90 lines
   - **Visualization:**
     ```
     Usage by Hour (Last 7 days)

     00:00 ▁
     01:00
     02:00
     03:00
     ...
     09:00 ████
     10:00 ███████
     11:00 █████
     ...
     14:00 ██████████  (Peak usage)
     ```

6. **New Function:** `usage_recommendations()` in AIRouter class
   - **Location:** After `usage_patterns()`
   - **Purpose:** AI-generated insights based on usage
   - **Size:** ~100 lines
   - **Recommendations:**
     - "You use Qwen3 Coder 30B 80% of the time. Consider trying Qwen2.5 Coder 32B for similar tasks."
     - "Phi-4 14B is 2x faster than Llama 3.3 70B for reasoning tasks."
     - "Your most productive hours are 2-4 PM."

7. **New Function:** `export_analytics_report()` in AIRouter class
   - **Location:** After `usage_recommendations()`
   - **Purpose:** Generate comprehensive PDF/HTML/Markdown report
   - **Size:** ~80 lines
   - **Output:** `analytics_report_{date}.md`

8. **New Function:** `generate_ascii_chart()` in AIRouter class (utility)
   - **Location:** After `export_analytics_report()`
   - **Purpose:** Create simple bar charts without external libraries
   - **Size:** ~40 lines
   - **Returns:** String with ASCII bar chart

#### MENU INTEGRATION:

- **Add menu option:** `[14] 📊 Performance Analytics`
- **Menu function:** `elif choice == "14": self.analytics_dashboard()`

#### DATABASE CHANGES:

**No new tables** - Uses existing sessions and messages tables

**New queries needed:**
```sql
-- Model usage frequency
SELECT model_id, COUNT(*) as usage_count,
       AVG(total_duration_seconds) as avg_duration
FROM sessions
WHERE created_at >= datetime('now', '-30 days')
GROUP BY model_id
ORDER BY usage_count DESC;

-- Performance metrics
SELECT model_id,
       AVG(total_tokens / total_duration_seconds) as avg_tokens_per_sec,
       AVG(total_duration_seconds) as avg_duration,
       COUNT(*) as total_runs
FROM sessions
WHERE total_duration_seconds > 0
GROUP BY model_id;

-- Usage by hour
SELECT strftime('%H', created_at) as hour,
       COUNT(*) as session_count
FROM sessions
WHERE created_at >= datetime('now', '-7 days')
GROUP BY hour
ORDER BY hour;

-- Success rate
SELECT model_id,
       COUNT(*) as total,
       SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful,
       (successful * 100.0 / total) as success_rate
FROM sessions
GROUP BY model_id;
```

#### EXTERNAL DEPENDENCIES:

- **Library:** None (uses ASCII charts, no plotting libraries)
- **Install:** N/A
- **Used for:** All charts are text-based

**Optional Enhancement:**
- **Library:** `matplotlib` or `plotext` for better charts
- **Install:** `pip install plotext` (terminal-based plotting)
- **Benefit:** Prettier charts, but adds dependency

#### IMPLEMENTATION PRIORITY: **8** (Nice-to-have, low priority)

#### ESTIMATED COMPLEXITY: 🟢 **LOW-MEDIUM**
- SQL queries: Simple aggregations
- ASCII charts: String formatting
- Recommendations: Rule-based logic
- Export: Template-based report generation

---

### FEATURE 8: Context Management & Injection

**STATUS:** ❌ **NOT_STARTED**

**IMPACT:** 🟡 **MEDIUM** - Productivity feature for document-based tasks

**DEPENDENCIES:** ⚠️ **OPTIONAL Feature 1** (Can work standalone but better with sessions)

#### EXISTING CODE TO MODIFY:

1. **Function:** `auto_select_mode()` at line 567 AND `list_models()` at line 486
   - **Change:** Add context injection step before prompt execution
   - **New flow:**
     ```python
     # Get user prompt
     prompt = input(f"{Colors.YELLOW}> {Colors.RESET}").strip()

     # NEW: Offer context injection
     add_context = input("Add context from files? [y/N]: ").strip().lower()
     if add_context == 'y':
         context = self.context_manager.collect_context()
         prompt = self.context_manager.inject_context(context, prompt)

     # Check context size
     est_tokens = self.context_manager.estimate_tokens(prompt)
     if est_tokens > model_data['context']:
         print(f"Warning: Estimated {est_tokens} tokens exceeds context limit")
         truncate = input("Truncate/summarize context? [Y/n]: ")
         if truncate != 'n':
             prompt = self.context_manager.truncate_context(prompt, model_data['context'])

     # Continue with execution
     ```

2. **Function:** `__init__()` at line 349
   - **Change:** Initialize ContextManager
   - **Addition:**
     ```python
     self.context_manager = ContextManager(self.models_dir / "context-templates")
     ```

#### NEW CODE TO ADD:

1. **New Class:** `ContextManager`
   - **Location:** New file `D:\models\context_manager.py` (import into ai-router.py)
   - **Purpose:** Load and inject context from various sources
   - **Dependencies:** pathlib, json
   - **Size:** ~300 lines
   - **Methods:**
     ```python
     collect_context() -> str  # Interactive file/template selection
     load_file(path) -> str  # Load .txt, .md, .py, .js, .json
     load_template(template_name) -> str
     inject_context(context, prompt) -> str  # Format: context + prompt
     estimate_tokens(text) -> int  # Rough estimate (words * 1.3)
     truncate_context(text, max_tokens) -> str
     summarize_context(text, target_tokens) -> str  # Extract key info
     ```

2. **New Function:** `collect_context()` implementation
   - **Location:** In ContextManager class
   - **Purpose:** Interactive context collection
   - **Size:** ~100 lines
   - **Options:**
     ```
     Add context from:
     [1] Single file
     [2] Multiple files
     [3] Context template
     [4] Previous session
     [5] Paste text directly
     [0] Cancel
     ```

3. **New Function:** `load_file()` with format detection
   - **Location:** In ContextManager class
   - **Purpose:** Load and format different file types
   - **Size:** ~80 lines
   - **Formats:**
     - `.txt`, `.md`: Direct load
     - `.py`, `.js`, `.cpp`, etc.: Add code block markers
     - `.json`: Pretty-print
     - Others: Read as text

4. **New Function:** `inject_context()` with smart formatting
   - **Location:** In ContextManager class
   - **Purpose:** Combine context and prompt with clear delimiters
   - **Size:** ~40 lines
   - **Template:**
     ```
     <context>
     {context_content}
     </context>

     {user_prompt}
     ```

5. **New Function:** `estimate_tokens()`
   - **Location:** In ContextManager class
   - **Purpose:** Rough token estimation
   - **Size:** ~20 lines
   - **Formula:** `word_count * 1.3` (approximate)

6. **New Function:** `truncate_context()`
   - **Location:** In ContextManager class
   - **Purpose:** Truncate to fit context window
   - **Size:** ~30 lines
   - **Strategy:** Take first N tokens + last N tokens (preserve beginning and end)

7. **New Function:** `summarize_context()` (advanced)
   - **Location:** In ContextManager class
   - **Purpose:** Use a fast model to summarize large context
   - **Size:** ~60 lines
   - **Strategy:** Use Dolphin 8B to create concise summary

#### MENU INTEGRATION:

**No new main menu option** - Integrated into existing prompt flow

**Alternative:** Add menu option for context templates:
- **Add menu option:** `[15] 📂 Manage Context Templates`
- **Menu function:** `elif choice == "15": self.context_manager.manage_templates()`

#### DATABASE CHANGES:

**Optional table for context templates:**

```sql
CREATE TABLE context_templates (
    template_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT,
    description TEXT,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Example templates
INSERT INTO context_templates VALUES
('code_review_rules', 'Code Review Guidelines', 'coding',
 'Standard code review checklist',
 'Check for:\n- Code quality\n- Security\n- Performance\n- Tests'),
('python_best_practices', 'Python Best Practices', 'coding',
 'PEP 8 and Python conventions',
 'Follow PEP 8...');
```

**Directory structure for file-based templates:**
```
D:\models\context-templates\
├── coding/
│   ├── code_review_rules.txt
│   ├── python_best_practices.txt
│   └── security_checklist.txt
├── research/
│   ├── academic_writing.txt
│   └── citation_format.txt
└── general/
    └── professional_tone.txt
```

#### EXTERNAL DEPENDENCIES:

- **Library:** None (uses stdlib only)
- **Install:** N/A
- **Used for:** File I/O and string operations

#### IMPLEMENTATION PRIORITY: **9** (Low priority, nice-to-have)

#### ESTIMATED COMPLEXITY: 🟢 **LOW**
- File loading: Simple I/O
- Token estimation: Basic math
- Context injection: String templating
- Truncation: String slicing
- Summarization: Reuses existing model execution (moderate)

---

### FEATURE 9: Prompt Chaining Workflows

**STATUS:** ❌ **NOT_STARTED**

**IMPACT:** 🔴 **HIGH** - Most complex feature, enables multi-step AI workflows

**DEPENDENCIES:**
- ✅ **REQUIRES Feature 1** (Session management)
- ✅ **REQUIRES Feature 2** (Template system for workflow steps)
- ⚠️ **OPTIONAL Feature 8** (Context injection for step outputs)

#### EXISTING CODE TO MODIFY:

1. **Function:** `run_model()` at line 615
   - **Change:** Make it return structured results for workflow use
   - **Already needed for:** Feature 3 (comparison mode)
   - **Impact:** Same refactoring benefits multiple features

2. **Function:** `__init__()` at line 349
   - **Change:** Initialize WorkflowEngine
   - **Addition:**
     ```python
     self.workflow_engine = WorkflowEngine(
         self.models_dir / "workflows",
         self  # Pass AIRouter instance for model execution
     )
     ```

#### NEW CODE TO ADD:

1. **New Class:** `WorkflowEngine`
   - **Location:** New file `D:\models\workflow_engine.py` (import into ai-router.py)
   - **Purpose:** Parse and execute YAML workflows
   - **Dependencies:** `yaml`, `jinja2`
   - **Size:** ~400 lines
   - **Methods:**
     ```python
     load_workflow(path) -> Workflow
     execute_workflow(workflow_id, initial_vars) -> dict
     parse_yaml(file) -> dict
     validate_workflow(workflow_dict) -> bool
     execute_step(step, state) -> result
     handle_conditional(condition, state) -> bool
     substitute_variables(template, state) -> str
     ```

2. **New Class:** `Workflow` (data class)
   - **Location:** In `workflow_engine.py`
   - **Purpose:** Represent parsed workflow
   - **Size:** ~100 lines
   - **Attributes:**
     ```python
     workflow_id: str
     name: str
     description: str
     steps: List[WorkflowStep]
     variables: Dict[str, Any]
     metadata: dict
     ```

3. **New Class:** `WorkflowStep` (data class)
   - **Location:** In `workflow_engine.py`
   - **Purpose:** Represent single workflow step
   - **Size:** ~80 lines
   - **Attributes:**
     ```python
     step_id: str
     type: str  # llm, user_input, conditional, etc.
     model: str
     prompt_template: str
     output_var: str
     depends_on: List[str]
     condition: Optional[str]
     retry: Optional[dict]
     ```

4. **New Function:** `workflow_mode()` in AIRouter class
   - **Location:** After line 613
   - **Purpose:** Interactive workflow selection and execution
   - **Size:** ~150 lines
   - **Flow:**
     ```python
     def workflow_mode(self):
         # List available workflows
         workflows = self.workflow_engine.list_workflows()

         # Select workflow
         workflow_id = self.select_workflow(workflows)

         # Collect initial variables
         initial_vars = self.collect_workflow_variables(workflow_id)

         # Execute with progress
         result = self.workflow_engine.execute_workflow(
             workflow_id,
             initial_vars
         )

         # Display results
         self.display_workflow_results(result)

         # Save to session
         self.session_manager.save_workflow_execution(
             workflow_id, initial_vars, result
         )
     ```

5. **New Function:** `workflow_builder()` in AIRouter class
   - **Location:** After `workflow_mode()`
   - **Purpose:** Interactive workflow builder wizard
   - **Size:** ~200 lines
   - **Wizard steps:**
     1. Workflow name and description
     2. Add steps (loop)
     3. Configure each step (model, prompt, output)
     4. Define dependencies
     5. Add conditionals (optional)
     6. Test workflow
     7. Save to YAML

6. **Built-in Workflow Templates:**
   - **File:** `D:\models\workflows\code_review_and_fix.yaml`
   - **File:** `D:\models\workflows\brainstorm_and_refine.yaml`
   - **File:** `D:\models\workflows\explain_then_implement.yaml`
   - **File:** `D:\models\workflows\test_generation.yaml`
   - **File:** `D:\models\workflows\research_and_summarize.yaml`

#### MENU INTEGRATION:

- **Add menu option:** `[16] 🔗 Run Workflow`
- **Add menu option:** `[17] 🛠️  Build Workflow (Wizard)`
- **Menu functions:**
   ```python
   elif choice == "16": self.workflow_mode()
   elif choice == "17": self.workflow_builder()
   ```

#### DATABASE CHANGES:

**New tables in `.ai-router-sessions.db`:**

```sql
CREATE TABLE workflows (
    workflow_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    file_path TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    execution_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0
);

CREATE TABLE workflow_executions (
    execution_id TEXT PRIMARY KEY,
    workflow_id TEXT NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    status TEXT DEFAULT 'running',  -- running, completed, failed
    initial_variables JSON,
    final_state JSON,
    step_count INTEGER,
    steps_completed INTEGER DEFAULT 0,
    FOREIGN KEY (workflow_id) REFERENCES workflows(workflow_id)
);

CREATE TABLE workflow_steps_log (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_id TEXT NOT NULL,
    step_id TEXT NOT NULL,
    step_name TEXT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    status TEXT,  -- success, failed, skipped
    input_variables JSON,
    output_variables JSON,
    error_message TEXT,
    FOREIGN KEY (execution_id) REFERENCES workflow_executions(execution_id)
);

CREATE INDEX idx_workflow_executions ON workflow_executions(workflow_id, started_at DESC);
CREATE INDEX idx_workflow_steps_log ON workflow_steps_log(execution_id, step_id);
```

#### EXTERNAL DEPENDENCIES:

- **Library:** `PyYAML`
  - **Install:** `pip install pyyaml`
  - **Used for:** Workflow file parsing
  - **Already required for:** Feature 2 (Templates)

- **Library:** `Jinja2`
  - **Install:** `pip install jinja2`
  - **Used for:** Variable substitution in workflows
  - **Already required for:** Feature 2 (Templates)

#### IMPLEMENTATION PRIORITY: **10** (Most complex, implement last)

#### ESTIMATED COMPLEXITY: 🔴 **HIGH**
- YAML parsing: Simple (PyYAML)
- Workflow execution engine: Complex (state management, dependencies)
- Variable substitution: Moderate (Jinja2)
- Conditional logic: Moderate
- Error handling and retry: Moderate
- Workflow builder wizard: Complex (multi-step UI)
- Testing: Complex (many edge cases)

**Estimated development time:** 2-3 weeks for full implementation

---

## RECOMMENDED IMPLEMENTATION ORDER

### Phase 1: Foundation (Week 1-2)
**Priority:** CRITICAL - Required for other features

1. **Feature 1: Session Management** (Priority 1)
   - **Why first:** Foundation for 6 other features
   - **Effort:** ~3 days
   - **Dependencies:** None
   - **Deliverables:**
     - SQLite database with sessions/messages tables
     - SessionManager class
     - Response capture in run_model()
     - Basic session history viewer

### Phase 2: Quick Wins (Week 2-3)
**Priority:** HIGH VALUE - Low complexity, high impact

2. **Feature 2: Prompt Templates** (Priority 3)
   - **Why second:** High value, independent, adds external dependencies early
   - **Effort:** ~2 days
   - **Dependencies:** None (can work standalone)
   - **Deliverables:**
     - TemplateManager and PromptTemplate classes
     - 10-15 built-in templates
     - Interactive template selector

3. **Feature 4: Response Post-Processing** (Priority 4)
   - **Why third:** Leverages response capture from Feature 1
   - **Effort:** ~1 day
   - **Dependencies:** Feature 1 (response capture)
   - **Deliverables:**
     - Post-processing menu after each run
     - Code extraction, statistics, filters
     - File save functionality

### Phase 3: Power User Features (Week 3-4)
**Priority:** MEDIUM - Advanced functionality

4. **Feature 3: Model Comparison** (Priority 5)
   - **Why fourth:** Unique differentiator, uses session DB
   - **Effort:** ~2 days
   - **Dependencies:** Feature 1 (session DB)
   - **Deliverables:**
     - Multi-model comparison mode
     - Comparison table display
     - Export to Markdown

5. **Feature 5: Batch Processing** (Priority 6)
   - **Why fifth:** Power user feature, builds on session management
   - **Effort:** ~3 days
   - **Dependencies:** Feature 1 (batch tracking)
   - **Deliverables:**
     - Batch input loader (JSON/CSV/TXT)
     - Progress tracker with ETA
     - Checkpoint/resume capability
     - Multiple output formats

### Phase 4: Intelligence & Insights (Week 4-5)
**Priority:** ENHANCEMENTS - Make router smarter

6. **Feature 6: Smart Auto-Selection** (Priority 7)
   - **Why sixth:** Enhances core UX, needs usage data
   - **Effort:** ~2 days
   - **Dependencies:** Feature 1 (preference tracking)
   - **Deliverables:**
     - Confidence scoring
     - Preference learning database
     - Enhanced prompt analysis
     - Override options

7. **Feature 7: Analytics Dashboard** (Priority 8)
   - **Why seventh:** Insights feature, needs historical data
   - **Effort:** ~2 days
   - **Dependencies:** Feature 1 (session history)
   - **Deliverables:**
     - Usage statistics
     - Performance metrics
     - ASCII charts
     - Recommendations engine

### Phase 5: Advanced Features (Week 5-6+)
**Priority:** ADVANCED - Complex, optional

8. **Feature 8: Context Management** (Priority 9)
   - **Why eighth:** Nice-to-have, relatively simple
   - **Effort:** ~2 days
   - **Dependencies:** None (optional Feature 1)
   - **Deliverables:**
     - ContextManager class
     - File loader (multiple formats)
     - Token estimation
     - Context templates

9. **Feature 9: Workflows** (Priority 10)
   - **Why last:** Most complex, depends on multiple features
   - **Effort:** ~5 days
   - **Dependencies:** Features 1, 2 (essential), 8 (optional)
   - **Deliverables:**
     - WorkflowEngine with YAML parser
     - 5 built-in workflows
     - Workflow builder wizard
     - Execution tracking

---

## DATABASE SCHEMA DESIGN

### Complete SQLite Schema (`.ai-router-sessions.db`)

```sql
-- ============================================================================
-- AI ROUTER ENHANCED DATABASE SCHEMA
-- Version: 2.0
-- Description: Complete schema for all 9 features
-- ============================================================================

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;  -- Better concurrency
PRAGMA synchronous = NORMAL;  -- Performance vs safety balance

-- ============================================================================
-- FEATURE 1: SESSION MANAGEMENT
-- ============================================================================

CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    model_id TEXT NOT NULL,
    model_name TEXT,
    framework TEXT,  -- 'llama.cpp' or 'mlx'
    title TEXT,  -- Auto-generated from first prompt (first 50 chars)
    message_count INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    total_duration_seconds REAL DEFAULT 0.0,
    status TEXT DEFAULT 'active',  -- active, archived, deleted
    tags JSON,  -- Array of user-defined tags
    metadata JSON  -- Flexible metadata storage
);

CREATE TABLE messages (
    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    sequence_number INTEGER NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tokens_used INTEGER,
    duration_seconds REAL,
    temperature REAL,
    top_p REAL,
    top_k INTEGER,
    metadata JSON,  -- Model params, file paths, etc.
    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE,
    UNIQUE (session_id, sequence_number)
);

-- Triggers for automatic statistics updates
CREATE TRIGGER update_session_stats_insert
AFTER INSERT ON messages
BEGIN
    UPDATE sessions
    SET message_count = message_count + 1,
        total_tokens = total_tokens + COALESCE(NEW.tokens_used, 0),
        total_duration_seconds = total_duration_seconds + COALESCE(NEW.duration_seconds, 0.0),
        updated_at = CURRENT_TIMESTAMP
    WHERE session_id = NEW.session_id;
END;

CREATE TRIGGER update_session_title
AFTER INSERT ON messages
WHEN NEW.role = 'user' AND NEW.sequence_number = 1
BEGIN
    UPDATE sessions
    SET title = SUBSTR(NEW.content, 1, 50) || CASE WHEN LENGTH(NEW.content) > 50 THEN '...' ELSE '' END
    WHERE session_id = NEW.session_id AND title IS NULL;
END;

-- Indexes for fast queries
CREATE INDEX idx_sessions_created ON sessions(created_at DESC);
CREATE INDEX idx_sessions_model ON sessions(model_id);
CREATE INDEX idx_sessions_status ON sessions(status);
CREATE INDEX idx_messages_session ON messages(session_id, sequence_number);
CREATE INDEX idx_messages_role ON messages(role);

-- Full-text search for sessions
CREATE VIRTUAL TABLE sessions_fts USING fts5(
    session_id UNINDEXED,
    title,
    content='messages',
    content_rowid='message_id'
);

-- Triggers to keep FTS index updated
CREATE TRIGGER sessions_fts_insert AFTER INSERT ON messages BEGIN
    INSERT INTO sessions_fts(session_id, title, content)
    VALUES (NEW.session_id, (SELECT title FROM sessions WHERE session_id = NEW.session_id), NEW.content);
END;

CREATE TRIGGER sessions_fts_delete AFTER DELETE ON messages BEGIN
    DELETE FROM sessions_fts WHERE rowid = OLD.message_id;
END;

-- ============================================================================
-- FEATURE 3: MODEL COMPARISON
-- ============================================================================

CREATE TABLE comparison_groups (
    comparison_id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    prompt TEXT NOT NULL,
    model_count INTEGER NOT NULL CHECK(model_count BETWEEN 2 AND 10),
    winner_model_id TEXT,  -- User can mark best model
    notes TEXT,
    metadata JSON
);

CREATE TABLE comparison_results (
    result_id INTEGER PRIMARY KEY AUTOINCREMENT,
    comparison_id TEXT NOT NULL,
    model_id TEXT NOT NULL,
    model_name TEXT NOT NULL,
    response TEXT NOT NULL,
    tokens_used INTEGER,
    duration_seconds REAL,
    response_length INTEGER,  -- Character count
    word_count INTEGER,
    code_block_count INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    quality_rating INTEGER CHECK(quality_rating BETWEEN 1 AND 5),  -- User rating
    FOREIGN KEY (comparison_id) REFERENCES comparison_groups(comparison_id) ON DELETE CASCADE
);

CREATE INDEX idx_comparisons_created ON comparison_groups(created_at DESC);
CREATE INDEX idx_comparison_results ON comparison_results(comparison_id);
CREATE INDEX idx_comparison_winner ON comparison_groups(winner_model_id);

-- ============================================================================
-- FEATURE 5: BATCH PROCESSING
-- ============================================================================

CREATE TABLE batch_jobs (
    batch_id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    model_id TEXT NOT NULL,
    model_name TEXT,
    total_tasks INTEGER NOT NULL,
    completed_tasks INTEGER DEFAULT 0,
    failed_tasks INTEGER DEFAULT 0,
    skipped_tasks INTEGER DEFAULT 0,
    status TEXT DEFAULT 'pending',  -- pending, running, completed, failed, interrupted
    input_file TEXT,
    output_file TEXT,
    checkpoint_file TEXT,
    error_strategy TEXT DEFAULT 'continue',  -- continue, stop_on_first, stop_on_threshold
    checkpoint_interval INTEGER DEFAULT 10,
    metadata JSON
);

CREATE TABLE batch_items (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id TEXT NOT NULL,
    task_id TEXT NOT NULL,
    sequence_number INTEGER NOT NULL,
    prompt TEXT NOT NULL,
    response TEXT,
    status TEXT DEFAULT 'pending',  -- pending, running, completed, failed, skipped
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    tokens_used INTEGER,
    duration_seconds REAL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSON,
    FOREIGN KEY (batch_id) REFERENCES batch_jobs(batch_id) ON DELETE CASCADE,
    UNIQUE (batch_id, task_id)
);

-- Triggers for batch statistics
CREATE TRIGGER update_batch_stats
AFTER UPDATE OF status ON batch_items
BEGIN
    UPDATE batch_jobs
    SET completed_tasks = (SELECT COUNT(*) FROM batch_items WHERE batch_id = NEW.batch_id AND status = 'completed'),
        failed_tasks = (SELECT COUNT(*) FROM batch_items WHERE batch_id = NEW.batch_id AND status = 'failed'),
        skipped_tasks = (SELECT COUNT(*) FROM batch_items WHERE batch_id = NEW.batch_id AND status = 'skipped')
    WHERE batch_id = NEW.batch_id;
END;

CREATE INDEX idx_batch_jobs_created ON batch_jobs(created_at DESC);
CREATE INDEX idx_batch_jobs_status ON batch_jobs(status);
CREATE INDEX idx_batch_items ON batch_items(batch_id, status);
CREATE INDEX idx_batch_items_sequence ON batch_items(batch_id, sequence_number);

-- ============================================================================
-- FEATURE 6: SMART AUTO-SELECTION
-- ============================================================================

CREATE TABLE user_preferences (
    preference_id INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt_hash TEXT,  -- MD5 hash for similarity matching
    use_case TEXT NOT NULL CHECK(use_case IN ('coding', 'reasoning', 'creative', 'research', 'general')),
    selected_model_id TEXT NOT NULL,
    was_recommended BOOLEAN NOT NULL,  -- Did user accept AI recommendation?
    confidence_score REAL,  -- Confidence of auto-selection (0.0-1.0)
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE prompt_analytics (
    analytics_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    prompt_text TEXT NOT NULL,
    detected_use_case TEXT,
    confidence_score REAL,
    detected_language TEXT,  -- Programming language (if code-related)
    question_count INTEGER DEFAULT 0,
    word_count INTEGER,
    char_count INTEGER,
    domain_terms JSON,  -- Array of detected domain keywords
    override_used BOOLEAN DEFAULT 0,  -- Did user override recommendation?
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);

CREATE INDEX idx_preferences_use_case ON user_preferences(use_case, selected_model_id);
CREATE INDEX idx_preferences_model ON user_preferences(selected_model_id);
CREATE INDEX idx_preferences_timestamp ON user_preferences(timestamp DESC);
CREATE INDEX idx_analytics_use_case ON prompt_analytics(detected_use_case);
CREATE INDEX idx_analytics_session ON prompt_analytics(session_id);

-- ============================================================================
-- FEATURE 7: ANALYTICS
-- ============================================================================

-- Uses existing tables but adds materialized views for performance

CREATE VIEW model_usage_stats AS
SELECT
    model_id,
    model_name,
    COUNT(*) as session_count,
    SUM(message_count) as total_messages,
    SUM(total_tokens) as total_tokens,
    AVG(total_duration_seconds) as avg_duration_seconds,
    MIN(created_at) as first_used,
    MAX(created_at) as last_used
FROM sessions
GROUP BY model_id, model_name;

CREATE VIEW daily_usage_stats AS
SELECT
    DATE(created_at) as date,
    COUNT(*) as session_count,
    SUM(total_tokens) as total_tokens,
    AVG(total_duration_seconds) as avg_duration
FROM sessions
GROUP BY DATE(created_at);

CREATE VIEW hourly_usage_pattern AS
SELECT
    CAST(strftime('%H', created_at) AS INTEGER) as hour,
    COUNT(*) as session_count
FROM sessions
WHERE created_at >= datetime('now', '-30 days')
GROUP BY hour
ORDER BY hour;

-- ============================================================================
-- FEATURE 8: CONTEXT MANAGEMENT
-- ============================================================================

CREATE TABLE context_templates (
    template_id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(8)))),
    name TEXT NOT NULL,
    category TEXT,  -- coding, research, general
    description TEXT,
    content TEXT NOT NULL,
    file_path TEXT,  -- If loaded from file
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE context_injections (
    injection_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    message_id INTEGER,
    source_type TEXT NOT NULL,  -- 'file', 'template', 'paste', 'previous_session'
    source_identifier TEXT,  -- File path or template ID
    content_preview TEXT,  -- First 200 chars
    estimated_tokens INTEGER,
    was_truncated BOOLEAN DEFAULT 0,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id),
    FOREIGN KEY (message_id) REFERENCES messages(message_id)
);

CREATE INDEX idx_context_templates_category ON context_templates(category);
CREATE INDEX idx_context_injections_session ON context_injections(session_id);

-- ============================================================================
-- FEATURE 9: WORKFLOWS
-- ============================================================================

CREATE TABLE workflows (
    workflow_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    file_path TEXT NOT NULL UNIQUE,
    category TEXT,
    step_count INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    execution_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    avg_duration_seconds REAL,
    is_built_in BOOLEAN DEFAULT 0,
    metadata JSON
);

CREATE TABLE workflow_executions (
    execution_id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    workflow_id TEXT NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    status TEXT DEFAULT 'running',  -- running, completed, failed, interrupted
    initial_variables JSON,
    final_state JSON,
    step_count INTEGER NOT NULL,
    steps_completed INTEGER DEFAULT 0,
    steps_failed INTEGER DEFAULT 0,
    error_message TEXT,
    total_tokens INTEGER DEFAULT 0,
    total_duration_seconds REAL,
    FOREIGN KEY (workflow_id) REFERENCES workflows(workflow_id)
);

CREATE TABLE workflow_steps_log (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_id TEXT NOT NULL,
    step_id TEXT NOT NULL,
    step_name TEXT,
    step_type TEXT,  -- llm, user_input, conditional, loop, etc.
    sequence_number INTEGER NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    status TEXT,  -- success, failed, skipped
    input_variables JSON,
    output_variables JSON,
    model_used TEXT,
    tokens_used INTEGER,
    duration_seconds REAL,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    FOREIGN KEY (execution_id) REFERENCES workflow_executions(execution_id) ON DELETE CASCADE
);

-- Triggers for workflow statistics
CREATE TRIGGER update_workflow_stats
AFTER UPDATE OF status ON workflow_executions
BEGIN
    UPDATE workflows
    SET execution_count = execution_count + 1,
        success_count = success_count + CASE WHEN NEW.status = 'completed' THEN 1 ELSE 0 END,
        avg_duration_seconds = (
            SELECT AVG(total_duration_seconds)
            FROM workflow_executions
            WHERE workflow_id = NEW.workflow_id AND status = 'completed'
        )
    WHERE workflow_id = NEW.workflow_id;
END;

CREATE INDEX idx_workflow_executions ON workflow_executions(workflow_id, started_at DESC);
CREATE INDEX idx_workflow_executions_status ON workflow_executions(status);
CREATE INDEX idx_workflow_steps_log ON workflow_steps_log(execution_id, sequence_number);

-- ============================================================================
-- MAINTENANCE & CLEANUP
-- ============================================================================

-- Archive old sessions (move to separate archive table)
CREATE TABLE sessions_archive AS SELECT * FROM sessions WHERE 1=0;
CREATE TABLE messages_archive AS SELECT * FROM messages WHERE 1=0;

-- Cleanup procedure (to be called periodically)
-- Example: Archive sessions older than 90 days
-- DELETE FROM sessions WHERE created_at < datetime('now', '-90 days') AND status = 'archived';

-- ============================================================================
-- INITIAL DATA
-- ============================================================================

-- Insert built-in context templates
INSERT INTO context_templates (template_id, name, category, description, content, is_built_in) VALUES
('ctx_code_review', 'Code Review Guidelines', 'coding', 'Standard code review checklist',
 'Review for:\n- Code quality and readability\n- Security vulnerabilities\n- Performance implications\n- Test coverage\n- Documentation', 1),
('ctx_python_best', 'Python Best Practices', 'coding', 'PEP 8 and Python conventions',
 'Follow PEP 8 style guide\nUse type hints\nWrite docstrings\nHandle exceptions properly', 1);

-- ============================================================================
-- PERFORMANCE NOTES
-- ============================================================================
-- 1. WAL mode enabled for better concurrency
-- 2. All foreign keys have indexes
-- 3. Timestamps indexed in DESC order for recent-first queries
-- 4. FTS5 for full-text search on sessions
-- 5. Triggers for automatic statistics (minimal overhead)
-- 6. Views for common analytics queries
-- ============================================================================
```

### Database Size Estimates

| Data Type | Avg Size | 1K Items | 10K Items | 100K Items |
|-----------|----------|----------|-----------|------------|
| Sessions | 500 bytes | 500 KB | 5 MB | 50 MB |
| Messages | 2 KB | 2 MB | 20 MB | 200 MB |
| Comparisons | 5 KB | 5 MB | 50 MB | 500 MB |
| Batch Jobs | 10 KB | 10 MB | 100 MB | 1 GB |
| Workflows | 15 KB | 15 MB | 150 MB | 1.5 GB |

**Expected Total:** 100K sessions = ~500 MB database

### Backup Strategy

```python
# Add to SessionManager class
def backup_database(self, backup_path: Path = None):
    """Create SQLite backup"""
    if backup_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.db_path.parent / f"backup_{timestamp}.db"

    # Use SQLite backup API
    src = sqlite3.connect(self.db_path)
    dst = sqlite3.connect(backup_path)
    src.backup(dst)
    src.close()
    dst.close()
    return backup_path
```

---

## MENU STRUCTURE PROPOSAL

### Updated Main Menu (17 Options)

```
╔════════════════════════════════════════════════════════════════════════════════╗
║                                                                                ║
║                         🤖  AI ROUTER CLI v2.0  🤖                            ║
║                                                                                ║
║           Intelligent Model Selection & Execution Framework                   ║
║              Based on 2025 Research (Sep-Nov 2025)                            ║
║                                                                                ║
╚════════════════════════════════════════════════════════════════════════════════╝

Platform: RTX 3090 (WSL Optimized)
Available Models: 10

═══════════════════════════════════════════════════════════════
What would you like to do?

BASIC OPERATIONS
[1] 🎯 Auto-select model based on prompt
[2] 📋 Browse & select from all models

SESSIONS & HISTORY
[3] 📜 View Session History
[4] 🔄 Resume Session
[5] ⚖️  Compare Models (A/B Test)

TEMPLATES & WORKFLOWS
[6] 📝 Use Prompt Template
[7] 🔗 Run Workflow
[8] 🛠️  Build Workflow (Wizard)

ADVANCED FEATURES
[9] 🔄 Batch Processing Mode
[10] 📊 Performance Analytics
[11] 📂 Manage Context Templates

INFORMATION & SETTINGS
[12] 💬 View system prompt examples
[13] ⚙️  View optimal parameters guide
[14] 📚 View documentation guides
[15] 🔓 Toggle Auto-Yes Mode (Currently: OFF)

EXIT
[16] 🚪 Exit
═══════════════════════════════════════════════════════════════

Enter choice [1-16]:
```

### Alternative: Organized Submenu Structure

```
MAIN MENU

[1] 🚀 Quick Start (Auto-select & run)
[2] 📋 Model Selection
    ├── Browse & select from all models
    ├── Compare multiple models
    └── View model information
[3] 📜 Sessions & History
    ├── View session history
    ├── Resume previous session
    ├── Search sessions
    └── Export session
[4] 📝 Templates & Workflows
    ├── Use prompt template
    ├── Run workflow
    ├── Build new workflow
    └── Manage templates
[5] 🛠️  Advanced Features
    ├── Batch processing
    ├── Context injection
    └── Performance analytics
[6] ⚙️  Settings & Help
    ├── Toggle auto-yes mode
    ├── View documentation
    └── System configuration
[7] 🚪 Exit
```

**Recommendation:** Keep flat menu for now (easier to navigate), can refactor to submenus later if it gets too crowded.

---

## QUICK WINS

### Features That Can Be Implemented in < 1 Hour

1. **Response Statistics** (Part of Feature 4)
   - **Time:** 30 minutes
   - **Complexity:** LOW
   - **Implementation:**
     ```python
     def response_statistics(self, response: str):
         words = response.split()
         sentences = response.count('.') + response.count('!') + response.count('?')
         code_blocks = response.count('```') // 2

         print(f"Word count: {len(words)}")
         print(f"Character count: {len(response)}")
         print(f"Reading time: {len(words) / 200:.1f} minutes")
         print(f"Sentence count: {sentences}")
         print(f"Code blocks: {code_blocks}")
     ```

2. **Save Raw Response** (Part of Feature 4)
   - **Time:** 20 minutes
   - **Complexity:** LOW
   - **Implementation:**
     ```python
     def save_response(self, response: str, model_id: str):
         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
         filename = f"response_{model_id}_{timestamp}.txt"
         output_dir = self.models_dir / "outputs"
         output_dir.mkdir(exist_ok=True)

         with open(output_dir / filename, 'w', encoding='utf-8') as f:
             f.write(response)

         print(f"Saved to: {filename}")
     ```

3. **Extract Code Blocks** (Part of Feature 4)
   - **Time:** 30 minutes
   - **Complexity:** LOW
   - **Implementation:**
     ```python
     def extract_code_blocks(self, response: str) -> List[tuple]:
         import re
         pattern = r'```(\w+)?\n(.*?)```'
         matches = re.findall(pattern, response, re.DOTALL)
         return [(lang or 'text', code.strip()) for lang, code in matches]
     ```

4. **Session Title Auto-Generation** (Part of Feature 1)
   - **Time:** 15 minutes
   - **Complexity:** LOW
   - **Implementation:** Already in database trigger (line in schema)

5. **Basic Session List Viewer** (Part of Feature 1)
   - **Time:** 45 minutes
   - **Complexity:** LOW
   - **Implementation:**
     ```python
     def view_session_history(self):
         sessions = self.session_manager.list_sessions(limit=20)

         for i, session in enumerate(sessions, 1):
             print(f"[{i}] {session['title'][:50]}")
             print(f"    Model: {session['model_name']} | "
                   f"{session['message_count']} messages | "
                   f"{session['created_at']}")
     ```

---

## TECHNICAL CHALLENGES

### Challenge 1: Subprocess Output Capture

**Problem:** Current implementation streams directly to console
```python
result = subprocess.run(cmd, shell=True)  # No capture
```

**Challenge:** llama.cpp outputs complex formatted text with:
- Prompt echo
- Generation statistics
- Progress indicators
- Color codes

**Solutions:**

**Option A: Capture and Parse** (Recommended)
```python
result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
response = self.parse_llama_output(result.stdout)
```

Pros:
- Full control over output
- Can save everything
- Can filter/format

Cons:
- Need to parse llama.cpp output format
- Lose live streaming during generation
- More complex

**Option B: Tee Pattern** (Stream + Capture)
```python
import io
import sys

class TeeOutput:
    def __init__(self):
        self.terminal = sys.stdout
        self.log = io.StringIO()

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

# Redirect stdout temporarily
old_stdout = sys.stdout
sys.stdout = TeeOutput()
result = subprocess.run(cmd, shell=True)
output = sys.stdout.log.getvalue()
sys.stdout = old_stdout
```

Pros:
- Keep live streaming
- Also capture output
- User sees progress

Cons:
- More complex implementation
- Harder to test

**Recommendation:** Start with Option A, add Option B later if users request live streaming

### Challenge 2: Context Window Management

**Problem:** Models have different context limits (8K - 256K tokens)

**Challenges:**
- Token counting is approximate (no exact tokenizer for all models)
- Context includes system prompt + conversation history + new input
- Exceeding context causes silent truncation or errors

**Solutions:**

**1. Conservative Estimation**
```python
def estimate_tokens(self, text: str) -> int:
    # Conservative estimate: 1.3 tokens per word
    words = len(text.split())
    return int(words * 1.3)

def check_context_limit(self, prompt: str, model_data: dict, history: list = None):
    total_tokens = 0

    # System prompt
    if model_data['system_prompt']:
        system_text = self.load_system_prompt(model_data['system_prompt'])
        total_tokens += self.estimate_tokens(system_text)

    # History
    if history:
        for msg in history:
            total_tokens += self.estimate_tokens(msg['content'])

    # New prompt
    total_tokens += self.estimate_tokens(prompt)

    context_limit = model_data['context']

    if total_tokens > context_limit * 0.9:  # 90% threshold
        return False, total_tokens, context_limit
    return True, total_tokens, context_limit
```

**2. Automatic Truncation**
```python
def truncate_history(self, history: list, max_tokens: int) -> list:
    """Keep most recent messages that fit in context"""
    truncated = []
    current_tokens = 0

    # Process in reverse (most recent first)
    for msg in reversed(history):
        msg_tokens = self.estimate_tokens(msg['content'])
        if current_tokens + msg_tokens <= max_tokens:
            truncated.insert(0, msg)
            current_tokens += msg_tokens
        else:
            break

    return truncated
```

**3. Summarization Fallback**
```python
def summarize_history(self, history: list) -> str:
    """Use fast model to summarize long history"""
    full_text = "\n\n".join([f"{msg['role']}: {msg['content']}" for msg in history])

    # Use fastest model (Dolphin 8B) to summarize
    summary_prompt = f"Summarize this conversation in 200 words:\n\n{full_text}"
    summary = self.run_model('dolphin-llama31-8b', summary_prompt, silent=True)

    return summary
```

### Challenge 3: Workflow State Management

**Problem:** Workflows need to maintain state across multiple steps

**Challenges:**
- Variable passing between steps
- Conditional branching
- Loop handling
- Error recovery
- Partial execution (resume from step N)

**Solutions:**

**State Container:**
```python
class WorkflowState:
    def __init__(self):
        self.variables = {}  # Global variables
        self.step_outputs = {}  # Output from each step
        self.execution_path = []  # Steps executed
        self.current_step = 0
        self.status = 'running'

    def set_variable(self, name, value):
        self.variables[name] = value

    def get_variable(self, name, default=None):
        # Check step outputs first ({{steps.step1.output}})
        if '.' in name:
            parts = name.split('.')
            if parts[0] == 'steps' and parts[1] in self.step_outputs:
                return self.step_outputs[parts[1]].get(parts[2], default)

        # Check global variables
        return self.variables.get(name, default)

    def save_checkpoint(self, path):
        """Save state to file for resume"""
        with open(path, 'w') as f:
            json.dump({
                'variables': self.variables,
                'step_outputs': self.step_outputs,
                'execution_path': self.execution_path,
                'current_step': self.current_step,
                'status': self.status
            }, f, indent=2)

    @classmethod
    def load_checkpoint(cls, path):
        """Resume from saved state"""
        with open(path, 'r') as f:
            data = json.load(f)

        state = cls()
        state.variables = data['variables']
        state.step_outputs = data['step_outputs']
        state.execution_path = data['execution_path']
        state.current_step = data['current_step']
        state.status = data['status']
        return state
```

**Variable Substitution:**
```python
from jinja2 import Environment

def substitute_variables(self, template: str, state: WorkflowState) -> str:
    """Replace {{variable}} with actual values"""
    env = Environment()

    # Build context for Jinja2
    context = {
        'variables': state.variables,
        'steps': state.step_outputs,
        **state.variables  # Allow direct access to variables
    }

    template_obj = env.from_string(template)
    return template_obj.render(**context)
```

### Challenge 4: Async Batch Processing

**Problem:** Batch processing is slow if sequential

**Challenge:** Need concurrent execution without overwhelming system

**Solution:** Semaphore-based rate limiting (already in research)

### Challenge 5: Database Migrations

**Problem:** Schema will evolve over time

**Challenge:** Need to update user databases without losing data

**Solution:**

```python
class DatabaseMigration:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self._init_version_table()

    def _init_version_table(self):
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def get_current_version(self) -> int:
        cursor = self.conn.execute('SELECT MAX(version) FROM schema_version')
        result = cursor.fetchone()[0]
        return result if result else 0

    def migrate_to_version(self, target_version: int):
        current = self.get_current_version()

        if current >= target_version:
            return  # Already at target version

        # Apply migrations in sequence
        migrations = {
            1: self._migrate_v0_to_v1,
            2: self._migrate_v1_to_v2,
            # Add new migrations here
        }

        for version in range(current + 1, target_version + 1):
            print(f"Migrating database to version {version}...")
            migrations[version]()
            self.conn.execute('INSERT INTO schema_version (version) VALUES (?)', (version,))
            self.conn.commit()

    def _migrate_v0_to_v1(self):
        """Initial schema creation"""
        # Execute full schema SQL
        pass

    def _migrate_v1_to_v2(self):
        """Add workflow tables"""
        self.conn.execute('CREATE TABLE workflows (...)')
        # etc.
```

---

## CODE REFACTORING NEEDS

### Refactor 1: Response Capture Architecture

**Current Design:**
```python
# Line 670 and 705
result = subprocess.run(cmd, shell=True)
# Returns only exit code, no output captured
```

**New Design:**
```python
class ModelExecutor:
    """Abstraction layer for model execution"""

    def execute(self, model_data, prompt, system_prompt=None) -> ModelResponse:
        if model_data['framework'] == 'mlx':
            return self._execute_mlx(model_data, prompt, system_prompt)
        else:
            return self._execute_llamacpp(model_data, prompt, system_prompt)

    def _execute_llamacpp(self, model_data, prompt, system_prompt) -> ModelResponse:
        cmd = self._build_llamacpp_command(model_data, prompt, system_prompt)

        start_time = time.time()
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        duration = time.time() - start_time

        # Parse output
        response_text = self._parse_llamacpp_output(result.stdout)
        tokens_used = self._extract_token_count(result.stdout)

        return ModelResponse(
            text=response_text,
            raw_output=result.stdout,
            tokens_used=tokens_used,
            duration=duration,
            model_id=model_data['id'],
            exit_code=result.returncode
        )

    def _parse_llamacpp_output(self, stdout: str) -> str:
        """Extract actual response from llama.cpp output"""
        # llama.cpp format:
        # [prompt echo]
        # [response]
        # [generation stats]

        # Find response between prompt and stats
        # This needs to be robust to different output formats
        lines = stdout.split('\n')
        # ... parsing logic ...
        return response_text

@dataclass
class ModelResponse:
    text: str
    raw_output: str
    tokens_used: int
    duration: float
    model_id: str
    exit_code: int
    metadata: dict = None
```

**Benefits:**
- Single source of truth for execution
- Easy to add new frameworks
- Consistent response format
- Testable in isolation

### Refactor 2: Model Database Structure

**Current Design:**
```python
# Lines 64-279: Hardcoded dictionaries
RTX3090_MODELS = {
    "qwen3-coder-30b": {
        "name": "...",
        "path": "...",
        # 10+ fields
    },
    # ... 9 more models
}
```

**Better Design:**
```python
@dataclass
class Model:
    id: str
    name: str
    path: str
    size: str
    speed: str
    use_case: str
    temperature: float
    top_p: float
    top_k: int
    context: int
    special_flags: List[str]
    system_prompt: Optional[str]
    notes: str
    framework: str

    def to_dict(self) -> dict:
        """For backward compatibility"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'Model':
        """Load from dictionary"""
        return cls(**data)

class ModelRegistry:
    """External model registry with file-based storage"""

    def __init__(self, registry_file: Path):
        self.registry_file = registry_file
        self.models: Dict[str, Model] = {}
        self._load()

    def _load(self):
        """Load from JSON file"""
        if self.registry_file.exists():
            with open(self.registry_file, 'r') as f:
                data = json.load(f)
                for model_id, model_data in data.items():
                    self.models[model_id] = Model.from_dict(model_data)
        else:
            # Create default registry
            self._create_default_registry()

    def add_model(self, model: Model):
        """Add new model to registry"""
        self.models[model.id] = model
        self._save()

    def remove_model(self, model_id: str):
        """Remove model from registry"""
        if model_id in self.models:
            del self.models[model_id]
            self._save()

    def _save(self):
        """Save to JSON file"""
        data = {
            model_id: model.to_dict()
            for model_id, model in self.models.items()
        }
        with open(self.registry_file, 'w') as f:
            json.dump(data, f, indent=2)
```

**Benefits:**
- Type safety with dataclasses
- Easy to add/remove models via UI
- Can store in external file for easier editing
- Validation built-in

### Refactor 3: Menu System

**Current Design:**
```python
# Lines 527-565: Large if-elif chain in while loop
choice = input("Enter choice [1-7]: ")
if choice == "1":
    self.auto_select_mode()
elif choice == "2":
    self.list_models()
# ... 5 more options
```

**Better Design:**
```python
class MenuOption:
    def __init__(self, key: str, emoji: str, label: str, handler: callable, enabled: bool = True):
        self.key = key
        self.emoji = emoji
        self.label = label
        self.handler = handler
        self.enabled = enabled

    def __str__(self):
        status = "" if self.enabled else " (disabled)"
        return f"{Colors.BRIGHT_GREEN}[{self.key}]{Colors.RESET} {self.emoji} {self.label}{status}"

class MenuSystem:
    def __init__(self, router: 'AIRouter'):
        self.router = router
        self.options: List[MenuOption] = []
        self._build_menu()

    def _build_menu(self):
        """Dynamically build menu options"""
        self.options = [
            MenuOption("1", "🎯", "Auto-select model", self.router.auto_select_mode),
            MenuOption("2", "📋", "Browse models", self.router.list_models),
            MenuOption("3", "📜", "Session history", self.router.view_session_history),
            # ... all options
        ]

    def display(self):
        """Display menu and handle input"""
        print(f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}{'='*63}{Colors.RESET}")
        print(f"{Colors.BRIGHT_WHITE}What would you like to do?{Colors.RESET}\n")

        # Group options by category
        self._print_category("BASIC OPERATIONS", self.options[0:2])
        self._print_category("SESSIONS & HISTORY", self.options[2:5])
        # ... etc

        print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}{'='*63}{Colors.RESET}")

    def handle_choice(self, choice: str) -> bool:
        """Execute menu option, return False to exit"""
        for option in self.options:
            if option.key == choice and option.enabled:
                option.handler()
                return True

        if choice.lower() in ['exit', 'quit', 'q']:
            return False

        print(f"{Colors.BRIGHT_RED}Invalid choice. Try again.{Colors.RESET}")
        return True

    def _print_category(self, title: str, options: List[MenuOption]):
        print(f"\n{Colors.BRIGHT_WHITE}{title}{Colors.RESET}")
        for opt in options:
            print(opt)
```

**Benefits:**
- Easy to add/remove/reorder menu options
- Can enable/disable options programmatically
- Category grouping built-in
- Cleaner main loop

### Refactor 4: Configuration Management

**Current Design:**
```python
# Lines 364-390: Only stores bypass_mode
config = {
    'bypass_mode': self.bypass_mode,
    'version': '1.0'
}
```

**Better Design:**
```python
@dataclass
class AppConfig:
    bypass_mode: bool = False
    default_model: Optional[str] = None
    auto_save_sessions: bool = True
    checkpoint_interval: int = 10
    output_directory: Path = Path("outputs")
    theme: str = "default"
    verbose_logging: bool = False
    version: str = "2.0"

    def save(self, config_file: Path):
        with open(config_file, 'w') as f:
            json.dump(asdict(self), f, indent=2, default=str)

    @classmethod
    def load(cls, config_file: Path) -> 'AppConfig':
        if not config_file.exists():
            return cls()  # Use defaults

        with open(config_file, 'r') as f:
            data = json.load(f)
            # Convert string paths back to Path objects
            if 'output_directory' in data:
                data['output_directory'] = Path(data['output_directory'])
            return cls(**data)
```

**Benefits:**
- Type-safe configuration
- Easy to add new config options
- Default values built-in
- Validation possible

---

## SUMMARY & NEXT STEPS

### Implementation Readiness: 🟡 MODERATE

**Strengths:**
- ✅ Clean, well-organized codebase
- ✅ Good foundation classes
- ✅ Platform-agnostic design
- ✅ Color system ready for enhanced UI
- ✅ Zero external dependencies (easy to add)

**Gaps:**
- ❌ No database/persistence layer
- ❌ No response capture mechanism
- ❌ Menu system needs expansion
- ❌ Need class refactoring for features

### Recommended Approach

**Phase 1 (Week 1-2): Foundation**
1. Implement Session Management (Feature 1)
2. Refactor response capture in run_model()
3. Add SessionManager class
4. Create database with basic tables

**Phase 2 (Week 2-3): Quick Wins**
5. Add Prompt Templates (Feature 2)
6. Add Response Post-Processing (Feature 4)
7. Expand menu to 10-12 options

**Phase 3 (Week 3-4): Power Features**
8. Implement Model Comparison (Feature 3)
9. Implement Batch Processing (Feature 5)
10. Add progress tracking

**Phase 4 (Week 4-5): Intelligence**
11. Enhance Auto-Selection (Feature 6)
12. Add Analytics Dashboard (Feature 7)

**Phase 5 (Week 5-6+): Advanced**
13. Add Context Management (Feature 8)
14. Implement Workflows (Feature 9)

### Success Criteria

Each feature should:
- ✅ Have comprehensive tests
- ✅ Include user documentation
- ✅ Maintain backward compatibility
- ✅ Follow existing code style
- ✅ Add value without complexity

### Risk Mitigation

**Technical Risks:**
1. **Subprocess output capture** - Start with simple capture, iterate
2. **Database migrations** - Implement version system early
3. **Workflow complexity** - Build simple workflows first

**User Experience Risks:**
1. **Menu complexity** - Consider submenus if >15 options
2. **Learning curve** - Provide wizard/guided modes
3. **Performance** - Profile database queries, add indexes

---

## FINAL RECOMMENDATIONS

1. **Start with Feature 1** - Everything depends on it
2. **Add dependencies gradually** - PyYAML, Jinja2 only when needed
3. **Keep menu flat** - Submenus can come later
4. **Test each feature** - Don't move on until stable
5. **Document as you go** - Update docs with each feature
6. **Get user feedback** - After Phase 2, validate direction

**This analysis provides a complete roadmap for implementing all 9 features systematically with minimal risk.**
