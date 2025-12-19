# AI Router Enhanced - Troubleshooting Guide

**Version**: 1.0
**Last Updated**: 2025-12-09
**Platforms**: Windows, WSL, macOS, Linux

---

## Table of Contents

1. [Quick Diagnosis](#quick-diagnosis)
2. [Installation Issues](#installation-issues)
3. [Runtime Errors](#runtime-errors)
4. [Menu Issues](#menu-issues)
5. [Feature-Specific Issues](#feature-specific-issues)
6. [Performance Issues](#performance-issues)
7. [Provider Issues](#provider-issues)
8. [Database Issues](#database-issues)
9. [Platform-Specific Issues](#platform-specific-issues)
10. [Getting Help](#getting-help)
11. [FAQ](#faq)

---

## Quick Diagnosis

Use this decision tree to quickly identify your issue:

```
Is the application starting?
├─ NO → See "Installation Issues" or "Runtime Errors"
└─ YES
    ├─ Menu not working? → See "Menu Issues"
    ├─ Model execution failing? → See "Provider Issues"
    ├─ Database errors? → See "Database Issues"
    ├─ Slow performance? → See "Performance Issues"
    └─ Feature not working? → See "Feature-Specific Issues"
```

**Common Quick Fixes:**
```bash
# 1. Check Python version (need 3.7+)
python --version

# 2. Reinstall dependencies
pip install --upgrade pyyaml jinja2

# 3. Check file permissions
ls -la /d/models/ai-router.py

# 4. Verify llama.cpp path
which llama-cli

# 5. Check database
ls -la /d/models/.ai-router-sessions.db
```

---

## Installation Issues

### Issue: Python Version Incompatible

**Symptoms:**
- Error: `SyntaxError: invalid syntax`
- Error: `ModuleNotFoundError: No module named 'dataclasses'`
- Features not available on older Python versions

**Cause:**
AI Router requires Python 3.7 or higher. Some features require 3.8+.

**Solution:**
1. Check your Python version:
   ```bash
   python --version
   # or
   python3 --version
   ```

2. If below 3.7, upgrade Python:

   **Windows:**
   ```bash
   # Download from https://www.python.org/downloads/
   # Or use chocolatey:
   choco install python
   ```

   **WSL/Linux:**
   ```bash
   sudo apt update
   sudo apt install python3.10 python3-pip
   ```

   **macOS:**
   ```bash
   brew install python@3.10
   ```

3. Verify the upgrade:
   ```bash
   python3 --version
   ```

**Verification:**
- Python 3.7+ should be installed
- `python3 --version` shows correct version

**Prevention:**
- Use virtual environments to isolate Python versions
- Document Python version requirements in your project

---

### Issue: Missing Dependencies

**Symptoms:**
- `ModuleNotFoundError: No module named 'yaml'`
- `ModuleNotFoundError: No module named 'jinja2'`
- Import errors when starting application

**Cause:**
Required Python packages not installed.

**Solution:**
1. Install core dependencies:
   ```bash
   pip install pyyaml jinja2
   ```

2. Install optional dependencies:
   ```bash
   # For clipboard support
   pip install pyperclip

   # For CSV export
   pip install csv
   ```

3. Verify installation:
   ```bash
   python3 -c "import yaml; import jinja2; print('Dependencies OK')"
   ```

**Verification:**
- No import errors when running AI Router
- All features accessible

**Prevention:**
- Create a `requirements.txt`:
  ```bash
  pip freeze > requirements.txt
  ```
- Install from requirements:
  ```bash
  pip install -r requirements.txt
  ```

---

### Issue: Database Initialization Failed

**Symptoms:**
- `FileNotFoundError: Schema file not found: schema.sql`
- `RuntimeError: Database exists but missing sessions table`
- Database errors on first run

**Cause:**
Missing schema.sql file or corrupted database.

**Solution:**
1. Check if schema.sql exists:
   ```bash
   ls -la /d/models/schema.sql
   ```

2. If missing, the schema.sql should contain:
   ```sql
   -- Sessions table
   CREATE TABLE IF NOT EXISTS sessions (
       session_id TEXT PRIMARY KEY,
       model_id TEXT NOT NULL,
       model_name TEXT,
       title TEXT,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       message_count INTEGER DEFAULT 0,
       total_tokens INTEGER DEFAULT 0,
       total_duration_seconds REAL DEFAULT 0
   );

   -- Messages table
   CREATE TABLE IF NOT EXISTS messages (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       session_id TEXT NOT NULL,
       sequence_number INTEGER NOT NULL,
       role TEXT NOT NULL CHECK(role IN ('user', 'assistant', 'system')),
       content TEXT NOT NULL,
       timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       tokens_used INTEGER,
       duration_seconds REAL,
       metadata TEXT,
       FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE,
       UNIQUE(session_id, sequence_number)
   );

   -- Session metadata
   CREATE TABLE IF NOT EXISTS session_metadata (
       session_id TEXT NOT NULL,
       key TEXT NOT NULL,
       value TEXT,
       PRIMARY KEY (session_id, key),
       FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
   );

   -- Full-text search
   CREATE VIRTUAL TABLE IF NOT EXISTS sessions_fts USING fts5(
       session_id UNINDEXED,
       title,
       content
   );

   -- View for recent sessions
   CREATE VIEW IF NOT EXISTS recent_sessions AS
   SELECT
       s.session_id,
       s.model_id,
       s.model_name,
       s.title,
       s.created_at,
       s.last_activity,
       s.message_count,
       s.total_tokens,
       s.total_duration_seconds
   FROM sessions s
   ORDER BY s.last_activity DESC;

   -- Indexes
   CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id);
   CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp);
   CREATE INDEX IF NOT EXISTS idx_sessions_model ON sessions(model_id);
   CREATE INDEX IF NOT EXISTS idx_sessions_activity ON sessions(last_activity);
   ```

3. If database is corrupted, delete and reinitialize:
   ```bash
   # Backup first (if exists)
   cp /d/models/.ai-router-sessions.db /d/models/.ai-router-sessions.db.backup

   # Delete corrupted database
   rm /d/models/.ai-router-sessions.db

   # Restart application (will recreate)
   python /d/models/ai-router.py
   ```

**Verification:**
- Application starts without database errors
- Can create and view sessions

**Prevention:**
- Keep schema.sql in the models directory
- Regular database backups
- Don't manually edit the database

---

### Issue: Path/Import Errors

**Symptoms:**
- `ModuleNotFoundError: No module named 'response_processor'`
- `ModuleNotFoundError: No module named 'model_selector'`
- Import errors for custom modules

**Cause:**
Python cannot find the custom modules. Usually caused by running from wrong directory.

**Solution:**
1. Check your current directory:
   ```bash
   pwd
   ```

2. Navigate to models directory:
   ```bash
   cd /d/models
   ```

3. Run from the models directory:
   ```bash
   python ai-router.py
   # or
   python3 ai-router.py
   ```

4. If still failing, check if module files exist:
   ```bash
   ls -la /d/models/*.py | grep -E "response_processor|model_selector|context_manager|template_manager|session_manager|batch_processor|analytics_dashboard|workflow_engine|model_comparison"
   ```

5. Add current directory to Python path:
   ```bash
   export PYTHONPATH="${PYTHONPATH}:/d/models"
   python ai-router.py
   ```

**Verification:**
- No import errors
- Application starts successfully

**Prevention:**
- Always run from `/d/models` directory
- Use absolute paths in scripts
- Create a launcher script:
  ```bash
  #!/bin/bash
  cd /d/models
  python3 ai-router.py "$@"
  ```

---

### Issue: Permission Errors

**Symptoms:**
- `PermissionError: [Errno 13] Permission denied`
- Cannot write to files or directories
- Cannot execute scripts

**Cause:**
Insufficient file permissions or ownership issues.

**Solution:**

**For File Permissions:**
```bash
# Make script executable
chmod +x /d/models/ai-router.py

# Fix directory permissions
chmod 755 /d/models

# Fix all Python files
chmod 644 /d/models/*.py
chmod +x /d/models/ai-router.py
```

**For Ownership Issues (WSL/Linux):**
```bash
# Check ownership
ls -la /d/models

# Fix ownership (replace USERNAME with your username)
sudo chown -R USERNAME:USERNAME /d/models
```

**For Windows:**
- Right-click folder → Properties → Security
- Ensure your user has "Full Control"
- Apply to all subfolders and files

**Verification:**
- Can read and write files
- Can execute scripts
- No permission errors

**Prevention:**
- Don't use `sudo` unnecessarily
- Keep files in your home directory
- Use proper umask settings

---

## Runtime Errors

### Issue: Module Not Found Errors

**Symptoms:**
- `ModuleNotFoundError: No module named 'X'`
- Errors when importing specific modules
- Features failing to load

**Cause:**
Missing Python dependencies or module files.

**Solution:**

**For Standard Library Modules:**
```bash
# These should be included with Python
# If missing, Python installation may be incomplete
python3 -m pip install --upgrade pip
```

**For Custom Modules:**
1. Verify all required files exist:
   ```bash
   ls -la /d/models/{response_processor,model_selector,context_manager,template_manager,session_manager,batch_processor,analytics_dashboard,workflow_engine,model_comparison}.py
   ```

2. If missing, download from repository or restore from backup

**For Third-Party Modules:**
```bash
# Install missing dependencies
pip install pyyaml jinja2 pyperclip
```

**Verification:**
- All imports succeed
- No module not found errors

**Prevention:**
- Keep all module files together
- Use version control (git)
- Regular backups

---

### Issue: Database Connection Errors

**Symptoms:**
- `sqlite3.OperationalError: database is locked`
- `sqlite3.DatabaseError: database disk image is malformed`
- Cannot access session history

**Cause:**
Database file locked by another process or corrupted.

**Solution:**

**For "Database is locked":**
1. Check for other processes:
   ```bash
   # Linux/WSL
   lsof /d/models/.ai-router-sessions.db

   # Windows
   # Use Process Explorer or Task Manager
   ```

2. Close other AI Router instances

3. If still locked, wait 30 seconds and retry

4. Force unlock (use with caution):
   ```bash
   # Backup first
   cp /d/models/.ai-router-sessions.db /d/models/.ai-router-sessions.db.backup

   # Open and close database
   sqlite3 /d/models/.ai-router-sessions.db "VACUUM;"
   ```

**For "Database malformed":**
1. Attempt recovery:
   ```bash
   # Backup corrupted database
   cp /d/models/.ai-router-sessions.db /d/models/.ai-router-sessions.db.corrupted

   # Try to recover
   sqlite3 /d/models/.ai-router-sessions.db.corrupted ".dump" | sqlite3 /d/models/.ai-router-sessions.db.recovered

   # If successful, replace
   mv /d/models/.ai-router-sessions.db.recovered /d/models/.ai-router-sessions.db
   ```

2. If recovery fails, start fresh:
   ```bash
   mv /d/models/.ai-router-sessions.db /d/models/.ai-router-sessions.db.corrupted
   # Application will create new database on next run
   ```

**Verification:**
- Can access session history
- No database errors
- Sessions save correctly

**Prevention:**
- Don't force-quit the application
- Regular database backups
- Close application properly
- Don't run multiple instances simultaneously

---

### Issue: Template Loading Errors

**Symptoms:**
- `ValueError: Failed to load template from X.yaml`
- YAML syntax errors
- Template variables not substituting

**Cause:**
Invalid YAML syntax or missing template files.

**Solution:**

**For Syntax Errors:**
1. Validate YAML syntax:
   ```bash
   python3 -c "import yaml; yaml.safe_load(open('/d/models/prompt-templates/TEMPLATE.yaml'))"
   ```

2. Common YAML errors to check:
   - Incorrect indentation (use spaces, not tabs)
   - Missing colons
   - Unquoted special characters
   - Missing quotes around strings with colons

3. Example of correct template:
   ```yaml
   metadata:
     name: "Example Template"
     id: example-template
     category: general
     description: "A simple example"
     variables:
       - name: topic
         description: "The topic to discuss"
         required: true
       - name: style
         description: "Writing style"
         required: false
         default: "professional"

   system_prompt: |
     You are an expert on {{ topic }}.
     Use a {{ style }} tone.

   user_prompt: |
     Please explain {{ topic }} in detail.
   ```

**For Missing Templates:**
1. Check template directory:
   ```bash
   ls -la /d/models/prompt-templates/
   ```

2. Create directory if missing:
   ```bash
   mkdir -p /d/models/prompt-templates
   ```

3. Verify template file exists:
   ```bash
   ls -la /d/models/prompt-templates/TEMPLATE.yaml
   ```

**For Variable Substitution:**
1. Ensure variables are defined in metadata:
   ```yaml
   metadata:
     variables:
       - name: variable_name
         description: "Description"
         required: true
   ```

2. Use correct Jinja2 syntax:
   ```yaml
   user_prompt: |
     This is {{ variable_name }}.
   ```

**Verification:**
- Templates load without errors
- Variables substitute correctly
- No YAML parsing errors

**Prevention:**
- Use YAML linter before saving
- Test templates after creation
- Keep backup of working templates
- Use version control

---

### Issue: Context File Loading Errors

**Symptoms:**
- `FileNotFoundError: File not found: X`
- `ValueError: Access denied: Path 'X' is outside the allowed base directory`
- Context files not loading

**Cause:**
File doesn't exist, path traversal attempt, or permission issues.

**Solution:**

**For File Not Found:**
1. Verify file exists:
   ```bash
   ls -la /path/to/file
   ```

2. Check path is absolute:
   ```bash
   # Good: Absolute path
   /d/models/context/example.txt

   # Bad: Relative path (may fail)
   ../context/example.txt
   ```

3. Use absolute paths:
   ```python
   context_manager.add_file(Path("/d/models/context/example.txt"))
   ```

**For Path Traversal Error:**
This is a security feature. You can only load files from within `/d/models/` or current working directory.

1. Move file to allowed directory:
   ```bash
   cp /other/location/file.txt /d/models/context/
   ```

2. Or change to that directory first:
   ```bash
   cd /other/location
   python /d/models/ai-router.py
   ```

**For Permission Issues:**
```bash
# Check file permissions
ls -la /path/to/file

# Make readable
chmod 644 /path/to/file
```

**Verification:**
- Files load successfully
- No path errors
- Context displays correctly

**Prevention:**
- Use absolute paths
- Keep context files in organized directories
- Check file exists before adding to context

---

### Issue: Model Execution Failures

**Symptoms:**
- `RuntimeError: Model execution failed with return code X`
- Model hangs indefinitely
- No output from model

**Cause:**
llama.cpp errors, incorrect model path, or parameter issues.

**Solution:**

**General Debugging:**
1. Test llama.cpp directly:
   ```bash
   llama-cli -m /mnt/d/models/organized/MODEL.gguf -p "Hello" -n 10
   ```

2. Check error messages carefully:
   - `Error loading model` → Wrong path or corrupted file
   - `Out of memory` → Model too large for VRAM
   - `Unsupported architecture` → Wrong llama.cpp version

**For Model Path Issues:**
1. Verify model file exists:
   ```bash
   ls -la /mnt/d/models/organized/MODEL.gguf
   ```

2. Check path in model database:
   ```bash
   # Edit ai-router.py and verify paths in RTX3090_MODELS or M4_MODELS
   grep -A5 "model-id" /d/models/ai-router.py
   ```

**For Memory Issues:**
1. Check VRAM usage:
   ```bash
   # NVIDIA GPU
   nvidia-smi

   # AMD GPU
   rocm-smi
   ```

2. Use smaller quantization:
   - If using Q6_K, try Q4_K_M
   - If using Q4_K_M, try Q2_K

**For Timeout Issues:**
1. Increase timeout in code (temporary):
   ```python
   # In ai-router.py, find timeout parameter
   result = subprocess.run(..., timeout=600)  # 10 minutes
   ```

**Verification:**
- Model executes successfully
- Generates output
- No errors or timeouts

**Prevention:**
- Test models individually first
- Monitor VRAM usage
- Use appropriate quantizations for your hardware

---

### Issue: YAML Parsing Errors

**Symptoms:**
- `yaml.scanner.ScannerError`
- `yaml.parser.ParserError`
- Workflows or templates fail to load

**Cause:**
Invalid YAML syntax.

**Solution:**

**Common YAML Issues:**

1. **Indentation errors** (use spaces, not tabs):
   ```yaml
   # WRONG
   metadata:
   	name: "Example"

   # CORRECT
   metadata:
     name: "Example"
   ```

2. **Missing colons:**
   ```yaml
   # WRONG
   metadata
     name "Example"

   # CORRECT
   metadata:
     name: "Example"
   ```

3. **Unquoted special characters:**
   ```yaml
   # WRONG
   description: This has a colon: problem

   # CORRECT
   description: "This has a colon: no problem"
   ```

4. **List formatting:**
   ```yaml
   # WRONG
   items
     - item1
     - item2

   # CORRECT
   items:
     - item1
     - item2
   ```

**Validation:**
```bash
# Test YAML syntax
python3 -c "import yaml; print(yaml.safe_load(open('file.yaml')))"

# Or use online validator
# https://www.yamllint.com/
```

**Verification:**
- YAML parses without errors
- All fields accessible

**Prevention:**
- Use YAML-aware editor (VS Code with YAML extension)
- Enable syntax highlighting
- Validate before saving
- Use YAML linter

---

### Issue: Import Errors

**Symptoms:**
- `ImportError: cannot import name 'X' from 'module'`
- Circular import errors
- Missing attributes

**Cause:**
Incompatible module versions or circular dependencies.

**Solution:**

**For Missing Imports:**
1. Check Python version compatibility:
   ```bash
   python3 --version
   ```

2. Update dependencies:
   ```bash
   pip install --upgrade pyyaml jinja2
   ```

**For Circular Imports:**
This shouldn't happen in the current codebase, but if it does:
1. Check for mutual imports between modules
2. Restructure to avoid circular dependencies
3. Use lazy imports if necessary

**For Attribute Errors:**
```python
# If you see: AttributeError: module 'X' has no attribute 'Y'
# Possible causes:
# 1. Outdated module version
pip install --upgrade MODULE_NAME

# 2. Name conflict (module.py in current directory)
# Remove or rename conflicting file

# 3. __pycache__ issues
find /d/models -name "__pycache__" -type d -exec rm -rf {} +
find /d/models -name "*.pyc" -delete
```

**Verification:**
- All imports work
- No attribute errors
- Correct module versions

**Prevention:**
- Pin dependency versions
- Use virtual environments
- Clear `__pycache__` regularly

---

## Menu Issues

### Issue: Menu Options Not Working

**Symptoms:**
- Selecting menu option does nothing
- Returns to main menu immediately
- Features don't execute

**Cause:**
Invalid input, missing features, or code errors.

**Solution:**

1. **Verify input format:**
   - Enter just the number: `1`
   - Don't include brackets: NOT `[1]`
   - Press Enter after typing

2. **Check for error messages:**
   - Look for red error text
   - Read error carefully for clues

3. **Try different menu options:**
   - If one fails, try others
   - Helps identify if problem is specific or general

4. **Restart application:**
   ```bash
   # Exit cleanly
   # Select [12] Exit from menu

   # Or Ctrl+C, then restart
   python /d/models/ai-router.py
   ```

5. **Check for required setup:**
   - Some features need database (auto-created)
   - Templates need template directory
   - Models need correct paths

**Verification:**
- Menu options execute
- Features work as expected
- No errors

**Prevention:**
- Read menu descriptions carefully
- Ensure prerequisites met
- Update to latest version

---

### Issue: Invalid Input Handling

**Symptoms:**
- Error messages for valid inputs
- Cannot escape from prompts
- Input not recognized

**Cause:**
Unexpected input format or encoding issues.

**Solution:**

1. **For numeric menus:**
   ```
   # Enter just the number
   1

   # NOT these:
   [1]
   menu 1
   option 1
   ```

2. **For yes/no prompts:**
   ```
   # Valid responses
   y
   yes
   Y
   YES
   (empty - defaults to yes)

   n
   no
   ```

3. **For text input:**
   - Use plain ASCII when possible
   - Avoid special characters unless needed
   - Check for paste formatting issues

4. **To cancel/exit:**
   - Type: `exit`, `quit`, or `q`
   - Or press Ctrl+C (may be messy)

**Verification:**
- Input recognized correctly
- Can navigate menus
- Can exit when needed

**Prevention:**
- Follow prompt instructions exactly
- Use simple inputs when possible
- Avoid copy-paste when possible

---

### Issue: Navigation Problems

**Symptoms:**
- Cannot return to previous menu
- Stuck in submenu
- Menu loops

**Cause:**
Navigation flow issue or missing return options.

**Solution:**

1. **Look for back/return options:**
   - Usually at bottom of menu
   - May be option 0 or highest number

2. **Complete current action:**
   - Some features return to menu after completion
   - Others may need explicit exit

3. **Force exit:**
   ```bash
   # Press Ctrl+C
   # Then restart application
   python /d/models/ai-router.py
   ```

4. **Use application exit:**
   - Navigate to main menu
   - Select Exit option (usually last)

**Verification:**
- Can navigate all menus
- Can return to main menu
- Can exit application

**Prevention:**
- Note menu structure
- Complete actions before exiting
- Use proper exit methods

---

### Issue: Display Issues

**Symptoms:**
- Garbled text or colors
- Missing formatting
- Overlapping text
- Unicode errors

**Cause:**
Terminal encoding issues or unsupported ANSI codes.

**Solution:**

**For Color/Formatting Issues:**
1. Check terminal support:
   ```bash
   # Linux/WSL/macOS
   echo $TERM
   # Should show: xterm-256color or similar
   ```

2. Set terminal to support colors:
   ```bash
   export TERM=xterm-256color
   ```

3. Use different terminal:
   - Windows: Windows Terminal (best), PowerShell, CMD
   - WSL: Windows Terminal with WSL profile
   - macOS: iTerm2, Terminal.app
   - Linux: GNOME Terminal, Konsole

**For Unicode Issues:**
1. Set correct encoding:
   ```bash
   export LANG=en_US.UTF-8
   export LC_ALL=en_US.UTF-8
   ```

2. Check Python encoding:
   ```python
   python3 -c "import sys; print(sys.stdout.encoding)"
   # Should show: UTF-8
   ```

**For Windows CMD Issues:**
```cmd
REM Set UTF-8 encoding
chcp 65001
```

**Verification:**
- Colors display correctly
- Text readable
- No encoding errors
- Formatting intact

**Prevention:**
- Use modern terminal emulator
- Set UTF-8 encoding by default
- Test on your platform before deployment

---

## Feature-Specific Issues

### Session Management

#### Issue: Database Locked Errors

**Symptoms:**
- `sqlite3.OperationalError: database is locked`
- Cannot save sessions
- Cannot view history

**Cause:**
Multiple processes accessing database or previous crash.

**Solution:**

1. **Check for multiple instances:**
   ```bash
   # Linux/WSL
   ps aux | grep ai-router

   # Kill extra instances
   kill PID
   ```

2. **Wait for lock timeout:**
   - SQLite will retry for up to 30 seconds
   - Wait and try again

3. **Manual unlock (last resort):**
   ```bash
   # Backup first
   cp /d/models/.ai-router-sessions.db /d/models/.ai-router-sessions.db.backup

   # Unlock
   sqlite3 /d/models/.ai-router-sessions.db "PRAGMA locking_mode=EXCLUSIVE; VACUUM; PRAGMA locking_mode=NORMAL;"
   ```

**Verification:**
- Can save sessions
- Can view history
- No lock errors

**Prevention:**
- Run only one instance
- Exit cleanly
- Don't force-kill application

---

#### Issue: Session Not Found

**Symptoms:**
- `ValueError: Session not found: session_id`
- Cannot load previous conversations
- Session list empty

**Cause:**
Session deleted, database corruption, or wrong session ID.

**Solution:**

1. **List all sessions:**
   ```bash
   # Use Analytics feature in menu
   # Or query database directly
   sqlite3 /d/models/.ai-router-sessions.db "SELECT session_id, title, created_at FROM sessions ORDER BY created_at DESC LIMIT 20;"
   ```

2. **Check session ID:**
   - Session IDs are UUIDs (e.g., `a1b2c3d4-...`)
   - Verify you're using correct ID
   - Check for typos

3. **Verify database integrity:**
   ```bash
   sqlite3 /d/models/.ai-router-sessions.db "PRAGMA integrity_check;"
   ```

**Verification:**
- Can find sessions
- Can load session history
- Session IDs work correctly

**Prevention:**
- Use session listing feature to find IDs
- Copy session IDs carefully
- Regular database backups

---

#### Issue: Export Failures

**Symptoms:**
- Cannot export to JSON
- Cannot export to Markdown
- Export file empty or corrupted

**Cause:**
Permission issues, disk space, or encoding problems.

**Solution:**

1. **Check disk space:**
   ```bash
   df -h /d/models
   ```

2. **Check write permissions:**
   ```bash
   ls -la /d/models/outputs

   # Create directory if missing
   mkdir -p /d/models/outputs

   # Fix permissions
   chmod 755 /d/models/outputs
   ```

3. **Test export manually:**
   ```python
   from session_manager import SessionManager
   from pathlib import Path

   sm = SessionManager(Path("/d/models/.ai-router-sessions.db"))

   # Export to JSON
   export_data = sm.export_session("session_id", format="json")
   print(export_data[:200])  # Preview

   # Save to file
   with open("/d/models/test_export.json", "w") as f:
       f.write(export_data)
   ```

**Verification:**
- Export completes without errors
- Export file contains data
- File is readable

**Prevention:**
- Ensure adequate disk space
- Regular cleanup of old exports
- Use descriptive filenames

---

### Templates

#### Issue: Template Not Found

**Symptoms:**
- `ValueError: Template 'X' not found`
- Template list empty
- Cannot load template

**Cause:**
Template file missing or wrong directory.

**Solution:**

1. **Check template directory:**
   ```bash
   ls -la /d/models/prompt-templates/
   ```

2. **Verify template file:**
   ```bash
   ls -la /d/models/prompt-templates/*.yaml
   ls -la /d/models/prompt-templates/*.yml
   ```

3. **Check template ID:**
   - Template ID must match `metadata.id` in YAML
   - Or match filename without extension

4. **Create template directory if missing:**
   ```bash
   mkdir -p /d/models/prompt-templates
   ```

5. **Create sample template:**
   ```bash
   cat > /d/models/prompt-templates/sample.yaml << 'EOF'
   metadata:
     name: "Sample Template"
     id: sample
     category: general
     description: "A sample template"
     variables:
       - name: topic
         description: "Topic to discuss"
         required: true

   system_prompt: |
     You are an expert on {{ topic }}.

   user_prompt: |
     Explain {{ topic }} clearly.
   EOF
   ```

**Verification:**
- Templates appear in list
- Can load template
- Template renders correctly

**Prevention:**
- Keep templates organized
- Use consistent naming
- Backup template directory

---

#### Issue: Variable Substitution Errors

**Symptoms:**
- Variables not replaced in output
- `{{ variable }}` appears in prompt literally
- Missing variable errors

**Cause:**
Variable not defined or wrong syntax.

**Solution:**

1. **Check variable is defined:**
   ```yaml
   metadata:
     variables:
       - name: topic  # Must match usage below
         description: "The topic"
         required: true
   ```

2. **Use correct Jinja2 syntax:**
   ```yaml
   # CORRECT
   user_prompt: |
     Explain {{ topic }}.

   # WRONG - extra spaces
   user_prompt: |
     Explain {{topic}}.

   # WRONG - wrong brackets
   user_prompt: |
     Explain { topic }.
   ```

3. **Provide variable value:**
   - Required variables must be provided
   - Use default values for optional variables

4. **Test template rendering:**
   ```python
   from template_manager import TemplateManager, PromptTemplate
   from pathlib import Path

   tm = TemplateManager(Path("/d/models/prompt-templates"))
   template = tm.get_template("template_id")
   result = template.render({"topic": "Python"})
   print(result)
   ```

**Verification:**
- Variables substitute correctly
- No literal `{{ }}` in output
- All required variables provided

**Prevention:**
- Test templates after creation
- Use descriptive variable names
- Document required variables

---

#### Issue: YAML Syntax Errors

**Symptoms:**
- `yaml.scanner.ScannerError`
- Template fails to load
- Parsing errors

**Cause:**
Invalid YAML syntax (see "YAML Parsing Errors" in Runtime Errors section).

**Solution:**

1. **Validate YAML:**
   ```bash
   python3 -c "import yaml; yaml.safe_load(open('/d/models/prompt-templates/TEMPLATE.yaml'))"
   ```

2. **Common fixes:**
   - Use spaces, not tabs
   - Quote strings with colons
   - Check indentation
   - Use `|` for multiline strings

3. **Example correct template:**
   ```yaml
   metadata:
     name: "Coding Assistant"
     id: coding-assistant
     category: coding
     description: "Helps with coding tasks"
     variables:
       - name: language
         description: "Programming language"
         required: true
         default: "Python"
       - name: task
         description: "Coding task"
         required: true

   system_prompt: |
     You are an expert {{ language }} programmer.
     You write clean, efficient, well-documented code.

   user_prompt: |
     Task: {{ task }}

     Please provide:
     1. Complete code solution
     2. Explanation
     3. Test cases
   ```

**Verification:**
- YAML parses without errors
- Template loads successfully
- All fields accessible

**Prevention:**
- Use YAML-aware editor
- Validate before saving
- Keep templates simple
- Use template creation wizard

---

### Batch Processing

#### Issue: Checkpoint Errors

**Symptoms:**
- `FileNotFoundError: Checkpoint file not found`
- Cannot resume batch job
- Checkpoint corrupted

**Cause:**
Missing checkpoint file or JSON corruption.

**Solution:**

1. **List checkpoints:**
   ```bash
   ls -la /d/models/batch_checkpoints/
   ```

2. **Verify checkpoint format:**
   ```bash
   python3 -c "import json; print(json.load(open('/d/models/batch_checkpoints/batch_XXXXX.json')))" | head -20
   ```

3. **If corrupted, cannot recover:**
   - Checkpoints save progress
   - If corrupted, restart batch job
   - Previous completed prompts lost

4. **Create checkpoint directory:**
   ```bash
   mkdir -p /d/models/batch_checkpoints
   ```

**Verification:**
- Checkpoints save correctly
- Can resume from checkpoint
- JSON is valid

**Prevention:**
- Don't manually edit checkpoints
- Ensure adequate disk space
- Regular checkpoint directory cleanup (old jobs)

---

#### Issue: Resume Failures

**Symptoms:**
- Cannot resume batch job
- Job restarts from beginning
- Progress lost

**Cause:**
Checkpoint not found or model mismatch.

**Solution:**

1. **Verify checkpoint exists:**
   ```bash
   ls -la /d/models/batch_checkpoints/batch_*.json
   ```

2. **Check model still available:**
   - Resume requires same model
   - If model removed, cannot resume
   - Must restart with different model

3. **Resume from menu:**
   - Use Batch Processing menu
   - Select "Resume from Checkpoint"
   - Choose checkpoint from list

4. **Manual resume (advanced):**
   ```python
   from batch_processor import BatchProcessor
   from pathlib import Path

   bp = BatchProcessor(Path("/d/models/batch_checkpoints"))
   job, results = bp.load_checkpoint(Path("/d/models/batch_checkpoints/batch_XXXXX.json"))
   # Continue processing...
   ```

**Verification:**
- Can resume from checkpoint
- Continues from last completed prompt
- No duplicate processing

**Prevention:**
- Note checkpoint IDs
- Keep models available during batch jobs
- Complete batches before removing models

---

#### Issue: Progress Tracking Issues

**Symptoms:**
- Progress not updating
- Incorrect completed count
- Stuck on one prompt

**Cause:**
Display update issue or prompt execution hanging.

**Solution:**

1. **Wait for timeout:**
   - Each prompt has timeout (default 5 minutes)
   - Long prompts may take time
   - Check for progress after timeout

2. **Check for errors:**
   - Look for red error messages
   - Check batch job status

3. **Review checkpoint:**
   ```bash
   # Check latest checkpoint
   ls -lt /d/models/batch_checkpoints/ | head -5

   # View progress
   python3 -c "import json; data=json.load(open('/d/models/batch_checkpoints/batch_XXXXX.json')); print(f\"{data['job']['completed']}/{data['job']['total_prompts']}\")"
   ```

**Verification:**
- Progress updates correctly
- Completed count increases
- No hangs

**Prevention:**
- Use shorter prompts in batches
- Test prompts individually first
- Set reasonable error strategy

---

### Workflows

#### Issue: Workflow Parsing Errors

**Symptoms:**
- `ValueError: Failed to load workflow from X.yaml`
- Missing required fields
- Invalid step types

**Cause:**
Invalid workflow YAML structure.

**Solution:**

1. **Validate workflow:**
   ```python
   from workflow_engine import WorkflowEngine
   from pathlib import Path

   we = WorkflowEngine(Path("/d/models/workflows"), None)
   is_valid, errors = we.validate_workflow(Path("/d/models/workflows/WORKFLOW.yaml"))

   if not is_valid:
       for error in errors:
           print(f"ERROR: {error}")
   ```

2. **Check required fields:**
   ```yaml
   # Minimal workflow
   id: my-workflow
   name: "My Workflow"
   description: "Description"

   steps:
     - name: step1
       type: prompt
       prompt: "Hello, world!"
   ```

3. **Valid step types:**
   - `prompt` - Execute AI prompt
   - `template` - Use template
   - `conditional` - If/then/else
   - `loop` - Iterate over items
   - `extract` - Extract from previous step
   - `sleep` - Wait (for rate limiting)

4. **Example complete workflow:**
   ```yaml
   id: example-workflow
   name: "Example Workflow"
   description: "Demonstrates all step types"

   variables:
     topic: "Python programming"
     items:
       - "functions"
       - "classes"
       - "decorators"

   steps:
     - name: introduction
       type: prompt
       prompt: "Introduce {{ topic }} in one sentence."
       output_var: intro

     - name: detailed_explanation
       type: prompt
       prompt: "Based on this intro: {{ intro }}, provide details."
       depends_on:
         - introduction

     - name: process_items
       type: loop
       items_var: items
       loop_var: item
       body:
         type: prompt
         prompt: "Explain {{ item }} in {{ topic }}."
   ```

**Verification:**
- Workflow parses without errors
- All steps recognized
- Validation passes

**Prevention:**
- Use workflow validation
- Start with simple workflows
- Test each step individually
- Use examples as templates

---

#### Issue: Execution Failures

**Symptoms:**
- `RuntimeError: Execution error: X`
- Workflow stops mid-execution
- Steps fail silently

**Cause:**
Step errors, model failures, or invalid variables.

**Solution:**

1. **Check error handling:**
   ```yaml
   steps:
     - name: risky_step
       type: prompt
       prompt: "Some prompt"
       on_error: continue  # Don't stop workflow on error
   ```

2. **Verify variables:**
   ```yaml
   # Variables must be defined
   variables:
     required_var: "value"

   steps:
     - name: step1
       type: prompt
       prompt: "Use {{ required_var }}"
   ```

3. **Check dependencies:**
   ```yaml
   steps:
     - name: step1
       type: prompt
       prompt: "First step"

     - name: step2
       type: prompt
       prompt: "Second step"
       depends_on:
         - step1  # Must exist and complete successfully
   ```

4. **Test models individually:**
   - Ensure model works outside workflow
   - Check model exists and is accessible

5. **Enable verbose logging:**
   - Add print statements to debug
   - Check workflow execution results

**Verification:**
- Workflow completes successfully
- All steps execute
- Results saved correctly

**Prevention:**
- Add error handling to critical steps
- Test workflows with simple prompts first
- Validate before running
- Use small datasets for testing

---

#### Issue: Variable Errors

**Symptoms:**
- `KeyError: 'variable_name'`
- Variables not substituting
- Undefined variable errors

**Cause:**
Variable not defined or wrong syntax.

**Solution:**

1. **Define variables:**
   ```yaml
   variables:
     topic: "Default value"
     count: 5
   ```

2. **Use correct syntax:**
   ```yaml
   # CORRECT
   prompt: "Explain {{ topic }}."

   # WRONG
   prompt: "Explain { topic }."
   ```

3. **Set output variables:**
   ```yaml
   steps:
     - name: step1
       type: prompt
       prompt: "Generate a topic."
       output_var: generated_topic  # Makes result available as variable

     - name: step2
       type: prompt
       prompt: "Expand on {{ generated_topic }}."
   ```

4. **Check variable scope:**
   - Workflow variables available in all steps
   - Output variables available after step completes
   - Loop variables only in loop body

**Verification:**
- All variables defined
- Substitution works correctly
- No undefined variable errors

**Prevention:**
- Document required variables
- Use descriptive names
- Initialize all variables
- Test substitution

---

### Analytics

#### Issue: No Data Showing

**Symptoms:**
- Analytics dashboard empty
- "No sessions found"
- Zero statistics

**Cause:**
No sessions in database or database connection issue.

**Solution:**

1. **Check database:**
   ```bash
   sqlite3 /d/models/.ai-router-sessions.db "SELECT COUNT(*) FROM sessions;"
   ```

2. **Create test session:**
   - Run a simple query through AI Router
   - Check analytics again

3. **Verify database path:**
   ```python
   from session_manager import SessionManager
   from pathlib import Path

   sm = SessionManager(Path("/d/models/.ai-router-sessions.db"))
   stats = sm.get_statistics()
   print(stats)
   ```

**Verification:**
- Statistics show correct counts
- Data displays in analytics
- Charts/graphs populate

**Prevention:**
- Regular usage creates data
- Don't delete database
- Backup before cleanup

---

#### Issue: Query Errors

**Symptoms:**
- `sqlite3.OperationalError: near "X": syntax error`
- Analytics crashes
- Invalid SQL

**Cause:**
Database schema mismatch or SQL error.

**Solution:**

1. **Check database schema:**
   ```bash
   sqlite3 /d/models/.ai-router-sessions.db ".schema"
   ```

2. **Compare with expected schema:**
   - See "Database Initialization Failed" section for correct schema

3. **Rebuild database (last resort):**
   ```bash
   # Backup
   cp /d/models/.ai-router-sessions.db /d/models/.ai-router-sessions.db.backup

   # Export data
   sqlite3 /d/models/.ai-router-sessions.db ".dump" > backup.sql

   # Recreate
   rm /d/models/.ai-router-sessions.db
   python /d/models/ai-router.py  # Creates new database
   ```

**Verification:**
- Queries execute without errors
- Data retrieves correctly
- Analytics functional

**Prevention:**
- Don't manually modify database
- Use provided methods only
- Keep schema up to date

---

#### Issue: Export Failures

**Symptoms:**
- Cannot export analytics data
- Export file corrupted
- Format errors

**Cause:**
Encoding issues or disk space.

**Solution:**

1. **Check disk space:**
   ```bash
   df -h /d/models
   ```

2. **Verify export directory:**
   ```bash
   mkdir -p /d/models/analytics_exports
   chmod 755 /d/models/analytics_exports
   ```

3. **Try different format:**
   - JSON usually more reliable than CSV
   - CSV may have encoding issues with special characters

4. **Manual export:**
   ```bash
   sqlite3 /d/models/.ai-router-sessions.db -csv -header "SELECT * FROM sessions;" > export.csv
   ```

**Verification:**
- Export completes
- File readable
- Data intact

**Prevention:**
- Regular exports for backup
- Clean old exports
- Use UTF-8 encoding

---

### Model Comparison

#### Issue: Comparison Failures

**Symptoms:**
- Cannot run comparison
- Models don't execute
- Results incomplete

**Cause:**
Model availability or execution errors.

**Solution:**

1. **Verify all models available:**
   ```bash
   # Check model files exist
   ls -la /mnt/d/models/organized/*.gguf
   ```

2. **Test models individually:**
   - Run each model separately first
   - Ensure they work before comparing

3. **Check comparison parameters:**
   - Same prompt for all models
   - Compatible parameters
   - Adequate timeout

4. **Use fewer models:**
   - Start with 2-3 models
   - Add more after successful comparison

**Verification:**
- All models execute
- Results collected
- Comparison completes

**Prevention:**
- Test models before comparing
- Use consistent parameters
- Limit comparison count

---

#### Issue: Export Errors

**Symptoms:**
- Cannot export comparison results
- Format errors
- Missing data

**Cause:**
Encoding or format issues.

**Solution:**

1. **Check export format:**
   - JSON: Most reliable
   - CSV: May have issues with special characters
   - Markdown: Good for reports

2. **Verify export directory:**
   ```bash
   mkdir -p /d/models/comparisons
   chmod 755 /d/models/comparisons
   ```

3. **Manual export:**
   ```python
   from model_comparison import ModelComparison
   from pathlib import Path

   mc = ModelComparison(Path("/d/models/comparisons"))
   # Export results...
   ```

**Verification:**
- Export completes
- File contains all data
- Format correct

**Prevention:**
- Use standard formats
- Regular exports
- Descriptive filenames

---

## Performance Issues

### Issue: Slow Startup

**Symptoms:**
- Application takes long to start
- Delays loading menu
- Hangs during initialization

**Cause:**
Database size, file system issues, or many templates/workflows.

**Solution:**

1. **Database cleanup:**
   ```python
   from session_manager import SessionManager
   from pathlib import Path

   sm = SessionManager(Path("/d/models/.ai-router-sessions.db"))

   # Delete sessions older than 90 days
   deleted = sm.cleanup_old_sessions(days=90)
   print(f"Deleted {deleted} old sessions")
   ```

2. **Database vacuum:**
   ```bash
   sqlite3 /d/models/.ai-router-sessions.db "VACUUM;"
   ```

3. **Reduce templates/workflows:**
   ```bash
   # Move unused templates
   mkdir -p /d/models/prompt-templates/archive
   mv /d/models/prompt-templates/unused*.yaml /d/models/prompt-templates/archive/
   ```

4. **Check disk performance:**
   ```bash
   # Test write speed
   dd if=/dev/zero of=/d/models/test.tmp bs=1M count=100
   rm /d/models/test.tmp
   ```

**Verification:**
- Startup under 5 seconds
- Menu appears promptly
- Responsive interface

**Prevention:**
- Regular database cleanup
- Archive old sessions
- Keep templates organized
- Use SSD if possible

---

### Issue: Slow Queries

**Symptoms:**
- Session list takes long to load
- Analytics slow to display
- Search times out

**Cause:**
Large database or missing indexes.

**Solution:**

1. **Rebuild indexes:**
   ```bash
   sqlite3 /d/models/.ai-router-sessions.db << 'EOF'
   DROP INDEX IF EXISTS idx_messages_session;
   DROP INDEX IF EXISTS idx_messages_timestamp;
   DROP INDEX IF EXISTS idx_sessions_model;
   DROP INDEX IF EXISTS idx_sessions_activity;

   CREATE INDEX idx_messages_session ON messages(session_id);
   CREATE INDEX idx_messages_timestamp ON messages(timestamp);
   CREATE INDEX idx_sessions_model ON sessions(model_id);
   CREATE INDEX idx_sessions_activity ON sessions(last_activity);

   ANALYZE;
   EOF
   ```

2. **Vacuum database:**
   ```bash
   sqlite3 /d/models/.ai-router-sessions.db "VACUUM;"
   ```

3. **Check database size:**
   ```bash
   ls -lh /d/models/.ai-router-sessions.db

   # If > 100MB, consider archiving old data
   ```

4. **Archive old sessions:**
   ```bash
   # Export old sessions
   sqlite3 /d/models/.ai-router-sessions.db << 'EOF'
   .output /d/models/archived_sessions.sql
   .dump
   SELECT * FROM sessions WHERE created_at < date('now', '-180 days');
   .output stdout
   EOF

   # Delete old sessions
   sqlite3 /d/models/.ai-router-sessions.db "DELETE FROM sessions WHERE created_at < date('now', '-180 days');"
   ```

**Verification:**
- Queries complete under 1 second
- Analytics responsive
- Search fast

**Prevention:**
- Regular cleanup (quarterly)
- Archive old data
- Monitor database size
- Keep indexes updated

---

### Issue: High Memory Usage

**Symptoms:**
- Application uses excessive RAM
- System becomes slow
- Out of memory errors

**Cause:**
Large context, many active sessions, or memory leak.

**Solution:**

1. **Check memory usage:**
   ```bash
   # Linux/WSL
   ps aux | grep python

   # Windows
   # Task Manager → Details → Find python.exe
   ```

2. **Reduce context size:**
   ```python
   # Limit context token count
   context_manager.set_max_tokens(2048)  # Instead of 4096+

   # Clear context after use
   context_manager.clear_context()
   ```

3. **Close unused sessions:**
   ```python
   # Exit session cleanly
   # Don't keep multiple sessions open
   ```

4. **Restart application periodically:**
   ```bash
   # If running long-term, restart daily
   ```

**Verification:**
- Memory usage reasonable (<500MB typical)
- No memory growth over time
- System responsive

**Prevention:**
- Clear context regularly
- Limit context size
- Exit sessions when done
- Restart for long runs

---

### Issue: Slow Model Execution

**Symptoms:**
- Model takes very long to respond
- Timeouts
- Low tokens/second

**Cause:**
Hardware limitations, wrong settings, or model too large.

**Solution:**

**For GPU Models (CUDA):**
1. **Check GPU utilization:**
   ```bash
   nvidia-smi
   # Should show ~100% GPU utilization during execution
   ```

2. **Verify GPU is being used:**
   ```bash
   llama-cli --help | grep -i gpu
   # Should show GPU options
   ```

3. **Optimize GPU layers:**
   ```bash
   # Load more layers to GPU (adjust based on VRAM)
   llama-cli -m MODEL.gguf -ngl 99 -p "Test"
   ```

**For CPU Models:**
1. **Use smaller quantization:**
   - Q6_K → Q4_K_M (faster, slight quality loss)
   - Q4_K_M → Q2_K (much faster, more quality loss)

2. **Reduce context size:**
   ```bash
   llama-cli -m MODEL.gguf -c 2048 -p "Test"  # Instead of 4096+
   ```

3. **Use faster model:**
   - 70B → 32B or 14B
   - Trade size for speed

**For MLX (M4):**
1. **Verify MLX is installed:**
   ```bash
   pip list | grep mlx
   ```

2. **Use MLX-optimized models:**
   - Models should be in MLX format, not GGUF
   - Check model path points to MLX directory

**General:**
1. **Reduce output length:**
   ```bash
   # Limit tokens generated
   llama-cli -m MODEL.gguf -n 512 -p "Test"  # Instead of 2048+
   ```

2. **Use appropriate model for task:**
   - Don't use 70B for simple queries
   - Match model size to task complexity

**Verification:**
- Tokens/second matches expected range
- No timeouts
- Acceptable response time

**Prevention:**
- Choose right model for hardware
- Monitor performance
- Upgrade hardware if needed
- Use smaller models for testing

---

## Provider Issues

### Issue: llama.cpp Not Found

**Symptoms:**
- `FileNotFoundError: llama-cli not found`
- `RuntimeError: llama.cpp executable not found`
- Cannot execute models

**Cause:**
llama.cpp not installed or not in PATH.

**Solution:**

**For WSL/Linux:**
1. **Check if installed:**
   ```bash
   which llama-cli
   llama-cli --version
   ```

2. **Install llama.cpp:**
   ```bash
   # Clone repository
   cd ~
   git clone https://github.com/ggerganov/llama.cpp
   cd llama.cpp

   # Build with CUDA (RTX 3090)
   make LLAMA_CUBLAS=1

   # Or build CPU-only
   make

   # Add to PATH
   echo 'export PATH="$HOME/llama.cpp:$PATH"' >> ~/.bashrc
   source ~/.bashrc
   ```

3. **Verify installation:**
   ```bash
   llama-cli --help
   ```

**For macOS:**
1. **Using Homebrew:**
   ```bash
   brew install llama.cpp
   ```

2. **Or build from source:**
   ```bash
   git clone https://github.com/ggerganov/llama.cpp
   cd llama.cpp
   make

   # Add to PATH
   echo 'export PATH="$HOME/llama.cpp:$PATH"' >> ~/.zshrc
   source ~/.zshrc
   ```

**For Windows:**
1. **Download pre-built binary:**
   - Visit: https://github.com/ggerganov/llama.cpp/releases
   - Download latest release for Windows
   - Extract to `C:\llama.cpp`

2. **Add to PATH:**
   ```cmd
   setx PATH "%PATH%;C:\llama.cpp"
   ```

3. **Restart terminal and verify:**
   ```cmd
   llama-cli --version
   ```

**Verification:**
- `llama-cli --help` works
- Can execute test model
- AI Router finds llama.cpp

**Prevention:**
- Add llama.cpp to PATH permanently
- Update regularly for bug fixes
- Build with appropriate GPU support

---

### Issue: Model Path Errors

**Symptoms:**
- `Error loading model: failed to load model`
- `FileNotFoundError: Model file not found`
- Model not accessible

**Cause:**
Wrong path, file doesn't exist, or permission issues.

**Solution:**

1. **Verify file exists:**
   ```bash
   ls -la /mnt/d/models/organized/MODEL.gguf
   ```

2. **Check path format:**
   - WSL: `/mnt/d/models/organized/MODEL.gguf`
   - Linux: `/home/user/models/MODEL.gguf`
   - macOS: `/Users/user/models/MODEL.gguf`
   - Windows: `D:\models\organized\MODEL.gguf`

3. **Verify permissions:**
   ```bash
   # Should be readable
   ls -la /mnt/d/models/organized/MODEL.gguf

   # Fix if needed
   chmod 644 /mnt/d/models/organized/MODEL.gguf
   ```

4. **Update model path in code:**
   ```python
   # Edit ai-router.py
   # Find model definition in RTX3090_MODELS or M4_MODELS
   "path": "/mnt/d/models/organized/CORRECT-MODEL-NAME.gguf",
   ```

5. **Test model directly:**
   ```bash
   llama-cli -m /mnt/d/models/organized/MODEL.gguf -p "Test" -n 10
   ```

**Verification:**
- Model loads successfully
- No path errors
- Can execute model

**Prevention:**
- Use absolute paths
- Verify paths after moving models
- Keep organized directory structure
- Document model locations

---

### Issue: Execution Failures

**Symptoms:**
- Model starts but crashes
- Segmentation fault
- CUDA/GPU errors
- Out of memory

**Cause:**
Hardware limitations, driver issues, or model incompatibility.

**Solution:**

**For GPU Out of Memory:**
1. **Check VRAM usage:**
   ```bash
   nvidia-smi
   ```

2. **Use smaller quantization:**
   - Q6_K → Q4_K_M
   - Q4_K_M → Q2_K

3. **Reduce GPU layers:**
   ```bash
   # Offload fewer layers to GPU
   llama-cli -m MODEL.gguf -ngl 30 -p "Test"  # Instead of -ngl 99
   ```

**For Segmentation Fault:**
1. **Update llama.cpp:**
   ```bash
   cd ~/llama.cpp
   git pull
   make clean
   make LLAMA_CUBLAS=1  # Or appropriate flags
   ```

2. **Test with simple model:**
   - Use smaller model first
   - If works, issue is with specific model

3. **Check system logs:**
   ```bash
   dmesg | tail -50
   journalctl -xe
   ```

**For CUDA Errors:**
1. **Verify CUDA installation:**
   ```bash
   nvcc --version
   nvidia-smi
   ```

2. **Reinstall CUDA drivers:**
   ```bash
   # WSL
   # Follow: https://docs.nvidia.com/cuda/wsl-user-guide/

   # Linux
   sudo apt install nvidia-cuda-toolkit
   ```

3. **Rebuild llama.cpp with CUDA:**
   ```bash
   cd ~/llama.cpp
   make clean
   make LLAMA_CUBLAS=1
   ```

**Verification:**
- Model executes without crashes
- No GPU errors
- Stable performance

**Prevention:**
- Match model size to hardware
- Keep drivers updated
- Regular llama.cpp updates
- Test new models before production use

---

### Issue: MLX Errors (M4)

**Symptoms:**
- `ModuleNotFoundError: No module named 'mlx'`
- MLX execution fails
- Poor performance with MLX

**Cause:**
MLX not installed or not configured correctly.

**Solution:**

1. **Install MLX:**
   ```bash
   pip install mlx mlx-lm
   ```

2. **Verify MLX installation:**
   ```bash
   python3 -c "import mlx; print(mlx.__version__)"
   ```

3. **Check model format:**
   - MLX models are different from GGUF
   - Should be in directory, not single file
   - Usually downloaded with `mlx_lm.load`

4. **Download MLX model:**
   ```bash
   python3 << 'EOF'
   from mlx_lm import load

   # Download and convert model
   model, tokenizer = load("mlx-community/Qwen2.5-14B-Instruct-8bit")
   EOF
   ```

5. **Update model path:**
   ```python
   # In ai-router.py, M4_MODELS section
   "path": "~/models/qwen25-14b",  # Directory, not file
   ```

**Verification:**
- MLX imports successfully
- Models execute with MLX
- Performance better than llama.cpp on M4

**Prevention:**
- Keep MLX updated
- Use MLX-optimized models on M4
- Don't mix GGUF and MLX formats

---

### Issue: API Key Errors (Cloud Providers)

**Symptoms:**
- `Authentication failed: Invalid API key`
- `401 Unauthorized`
- Cannot access cloud models

**Cause:**
Missing or invalid API key.

**Solution:**

1. **Verify API key:**
   - OpenRouter: https://openrouter.ai/keys
   - OpenAI: https://platform.openai.com/api-keys
   - Claude: https://console.anthropic.com/

2. **Set API key:**
   ```bash
   # Environment variable (temporary)
   export OPENROUTER_API_KEY="sk-or-v1-..."
   export OPENAI_API_KEY="sk-..."
   export ANTHROPIC_API_KEY="sk-ant-..."
   ```

3. **Save permanently:**
   ```bash
   # Add to ~/.bashrc or ~/.zshrc
   echo 'export OPENROUTER_API_KEY="sk-or-v1-..."' >> ~/.bashrc
   source ~/.bashrc
   ```

4. **Configure in application:**
   - Use menu: Configure Providers
   - Enter API key when prompted
   - Saved to config file

**Verification:**
- API key accepted
- Can query cloud models
- No authentication errors

**Prevention:**
- Keep API keys secure
- Don't commit to git
- Rotate keys periodically
- Monitor usage/billing

---

## Database Issues

### Issue: Database Corruption

**Symptoms:**
- `sqlite3.DatabaseError: database disk image is malformed`
- Cannot open database
- Queries fail with corruption errors

**Cause:**
System crash, forced shutdown, or disk errors.

**Solution:**

1. **Attempt recovery:**
   ```bash
   # Backup corrupted database
   cp /d/models/.ai-router-sessions.db /d/models/.ai-router-sessions.db.corrupted

   # Try to recover
   sqlite3 /d/models/.ai-router-sessions.db.corrupted ".dump" | sqlite3 /d/models/.ai-router-sessions.db.recovered

   # If successful, replace
   mv /d/models/.ai-router-sessions.db.recovered /d/models/.ai-router-sessions.db
   ```

2. **Check integrity:**
   ```bash
   sqlite3 /d/models/.ai-router-sessions.db "PRAGMA integrity_check;"
   ```

3. **If recovery fails, restore from backup:**
   ```bash
   # If you have backup
   cp /d/models/.ai-router-sessions.db.backup /d/models/.ai-router-sessions.db
   ```

4. **Last resort - start fresh:**
   ```bash
   # Save corrupted for reference
   mv /d/models/.ai-router-sessions.db /d/models/.ai-router-sessions.db.corrupted

   # Application will create new database on next run
   python /d/models/ai-router.py
   ```

**Verification:**
- Database opens without errors
- Integrity check passes
- Can query data

**Prevention:**
- Regular backups (daily/weekly)
- Clean shutdown always
- Fix disk errors promptly
- Use reliable storage

---

### Issue: Migration Errors

**Symptoms:**
- Schema version mismatch
- Missing columns
- Incompatible database

**Cause:**
Database created with older version of application.

**Solution:**

1. **Check schema version:**
   ```bash
   sqlite3 /d/models/.ai-router-sessions.db "PRAGMA user_version;"
   ```

2. **Backup before migration:**
   ```bash
   cp /d/models/.ai-router-sessions.db /d/models/.ai-router-sessions.db.backup
   ```

3. **Manual migration (if needed):**
   ```bash
   # Example: Add missing column
   sqlite3 /d/models/.ai-router-sessions.db "ALTER TABLE sessions ADD COLUMN new_field TEXT;"
   ```

4. **Or recreate database:**
   ```bash
   # Export data
   sqlite3 /d/models/.ai-router-sessions.db ".dump" > sessions_backup.sql

   # Remove old database
   mv /d/models/.ai-router-sessions.db /d/models/.ai-router-sessions.db.old

   # Create new (application will initialize)
   python /d/models/ai-router.py

   # Import data if possible
   # (May need manual adjustment for schema changes)
   ```

**Verification:**
- Schema up to date
- All features work
- No missing columns

**Prevention:**
- Backup before upgrading
- Read upgrade notes
- Test on copy first
- Keep old version until verified

---

### Issue: FTS5 Search Not Working

**Symptoms:**
- Search returns no results
- `no such module: fts5`
- Full-text search disabled

**Cause:**
SQLite compiled without FTS5 support.

**Solution:**

1. **Check FTS5 support:**
   ```bash
   sqlite3 /d/models/.ai-router-sessions.db "PRAGMA compile_options;" | grep FTS5
   ```

2. **If missing, rebuild SQLite:**

   **Ubuntu/Debian:**
   ```bash
   sudo apt install sqlite3 libsqlite3-dev
   ```

   **macOS:**
   ```bash
   brew install sqlite
   ```

3. **Or use Python's sqlite3:**
   ```python
   import sqlite3
   print(sqlite3.sqlite_version)
   # Should be 3.9.0+
   ```

4. **Rebuild FTS index:**
   ```bash
   sqlite3 /d/models/.ai-router-sessions.db << 'EOF'
   DROP TABLE IF EXISTS sessions_fts;

   CREATE VIRTUAL TABLE sessions_fts USING fts5(
       session_id UNINDEXED,
       title,
       content
   );
   EOF
   ```

**Verification:**
- Search queries work
- FTS5 table exists
- Results returned

**Prevention:**
- Use modern SQLite (3.9+)
- Keep system updated
- Test search after setup

---

### Issue: Lock Errors

**Symptoms:**
- `sqlite3.OperationalError: database is locked`
- Operations timeout
- Cannot write to database

**Cause:**
See "Database Connection Errors" in Runtime Errors section.

**Solution:**
See "Database Connection Errors" section above for detailed solutions.

**Quick Fix:**
```bash
# Close all AI Router instances
# Wait 30 seconds
# Retry operation

# Or force unlock (use with caution)
sqlite3 /d/models/.ai-router-sessions.db "VACUUM;"
```

---

## Platform-Specific Issues

### Windows-Specific Problems

#### Issue: Path Separator Issues

**Symptoms:**
- Paths with backslashes fail
- File not found errors
- Import errors

**Cause:**
Windows uses backslashes, Python expects forward slashes or escaping.

**Solution:**

1. **Use forward slashes:**
   ```python
   # Good
   path = "D:/models/file.txt"

   # Also good
   from pathlib import Path
   path = Path("D:/models/file.txt")
   ```

2. **Or escape backslashes:**
   ```python
   # Good
   path = "D:\\models\\file.txt"

   # Or raw string
   path = r"D:\models\file.txt"
   ```

**Verification:**
- Paths work correctly
- No file not found errors

**Prevention:**
- Use `pathlib.Path`
- Use forward slashes
- Or raw strings

---

#### Issue: ANSI Color Codes Not Working

**Symptoms:**
- Strange characters in output
- Colors not displaying
- Garbled text

**Cause:**
Windows CMD doesn't support ANSI by default.

**Solution:**

1. **Enable ANSI in CMD:**
   ```cmd
   REM Run this in CMD
   REG ADD HKCU\Console /v VirtualTerminalLevel /t REG_DWORD /d 1
   ```

2. **Or use Windows Terminal:**
   - Download from Microsoft Store
   - Built-in ANSI support
   - Better experience overall

3. **Or use PowerShell:**
   - Better ANSI support than CMD
   - Works with colors

**Verification:**
- Colors display correctly
- No strange characters
- Text readable

**Prevention:**
- Use Windows Terminal
- Or PowerShell
- Avoid CMD if possible

---

#### Issue: Long Path Issues

**Symptoms:**
- `FileNotFoundError` for long paths
- Path too long errors
- Cannot create files

**Cause:**
Windows MAX_PATH limit (260 characters).

**Solution:**

1. **Enable long paths:**
   ```powershell
   # Run PowerShell as Administrator
   New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
   ```

2. **Or use shorter paths:**
   - Move to `C:\models` instead of `D:\very\long\path\...`
   - Use shorter directory names

**Verification:**
- Long paths work
- Can create files in deep directories

**Prevention:**
- Keep paths short
- Enable long paths on new systems
- Use drive root when possible

---

### WSL-Specific Problems

#### Issue: WSL Path Detection

**Symptoms:**
- Cannot find Windows files
- Path format errors
- Models not loading

**Cause:**
WSL uses different path format than Windows.

**Solution:**

1. **Use WSL paths for Windows drives:**
   ```bash
   # Windows: D:\models
   # WSL: /mnt/d/models
   ```

2. **Verify path format:**
   ```bash
   # Check if path exists
   ls -la /mnt/d/models

   # Should show files
   ```

3. **Update paths in code:**
   ```python
   # Use WSL format
   models_dir = Path("/mnt/d/models")
   ```

**Verification:**
- Paths resolve correctly
- Files accessible
- Models load

**Prevention:**
- Always use `/mnt/` prefix for Windows drives in WSL
- Document path format
- Test paths after setup

---

#### Issue: Performance Slower than Native

**Symptoms:**
- Slower file access
- Slower model execution
- High latency

**Cause:**
WSL I/O overhead, especially for Windows filesystem.

**Solution:**

1. **Use WSL filesystem for better performance:**
   ```bash
   # Copy models to WSL home
   cp -r /mnt/d/models ~/models

   # Update paths
   # Use ~/models instead of /mnt/d/models
   ```

2. **Or use WSL 2 (better performance):**
   ```powershell
   # Check WSL version
   wsl --list --verbose

   # Upgrade to WSL 2
   wsl --set-version Ubuntu 2
   ```

3. **Optimize for cross-filesystem access:**
   - Keep frequently accessed files in WSL filesystem
   - Use Windows filesystem for large, rarely accessed files

**Verification:**
- Acceptable performance
- No significant lag
- Model execution speed normal

**Prevention:**
- Use WSL 2
- Keep working files in WSL filesystem
- Large archives on Windows filesystem

---

#### Issue: GPU Not Accessible

**Symptoms:**
- NVIDIA GPU not detected in WSL
- Cannot use CUDA
- GPU acceleration not working

**Cause:**
WSL not configured for GPU access.

**Solution:**

1. **Verify WSL 2:**
   ```powershell
   wsl --list --verbose
   # Should show version 2
   ```

2. **Install NVIDIA drivers on Windows:**
   - Download from NVIDIA website
   - Install latest driver
   - Restart

3. **Install CUDA in WSL:**
   ```bash
   # WSL
   # Follow: https://docs.nvidia.com/cuda/wsl-user-guide/

   # Install CUDA toolkit
   sudo apt install nvidia-cuda-toolkit
   ```

4. **Verify GPU access:**
   ```bash
   nvidia-smi
   # Should show GPU info
   ```

5. **Rebuild llama.cpp with CUDA:**
   ```bash
   cd ~/llama.cpp
   make clean
   make LLAMA_CUBLAS=1
   ```

**Verification:**
- `nvidia-smi` works
- GPU detected
- CUDA acceleration working

**Prevention:**
- Use WSL 2
- Keep drivers updated
- Follow official NVIDIA WSL guide

---

### macOS-Specific Problems

#### Issue: Permissions Issues with Gatekeeper

**Symptoms:**
- `Operation not permitted`
- Cannot execute binaries
- Security warnings

**Cause:**
macOS Gatekeeper blocking execution.

**Solution:**

1. **Allow execution:**
   ```bash
   # Make executable
   chmod +x /path/to/binary

   # Remove quarantine attribute
   xattr -d com.apple.quarantine /path/to/binary
   ```

2. **Or allow in System Preferences:**
   - System Preferences → Security & Privacy
   - Allow blocked application
   - Retry execution

**Verification:**
- Binary executes without prompts
- No permission errors

**Prevention:**
- Build from source instead of downloading binaries
- Sign applications (for distribution)
- Understand macOS security model

---

#### Issue: MLX Performance Not Optimal

**Symptoms:**
- MLX slower than expected on M4
- Not using GPU acceleration
- High CPU usage

**Cause:**
MLX not configured properly or wrong model format.

**Solution:**

1. **Verify MLX installation:**
   ```bash
   pip install --upgrade mlx mlx-lm
   ```

2. **Use MLX-optimized models:**
   - Models should be MLX format, not GGUF
   - Download from mlx-community on Hugging Face

3. **Check Metal GPU usage:**
   ```bash
   # Activity Monitor → GPU History
   # Should show GPU usage during inference
   ```

4. **Use proper MLX commands:**
   ```bash
   # Use mlx_lm, not llama-cli
   python -m mlx_lm.generate --model /path/to/model --prompt "Test"
   ```

**Verification:**
- Using GPU acceleration
- Performance matches expectations
- Low CPU usage during inference

**Prevention:**
- Use MLX for M-series Macs
- Don't use llama.cpp on M-series (slower)
- Use MLX-optimized models

---

### Linux-Specific Problems

#### Issue: Missing Dependencies

**Symptoms:**
- Library not found errors
- Cannot build llama.cpp
- Import errors

**Cause:**
Missing development packages.

**Solution:**

**For Ubuntu/Debian:**
```bash
# Install build essentials
sudo apt update
sudo apt install build-essential git cmake

# For CUDA support
sudo apt install nvidia-cuda-toolkit

# For Python development
sudo apt install python3-dev python3-pip
```

**For Fedora/RHEL:**
```bash
# Install development tools
sudo dnf groupinstall "Development Tools"
sudo dnf install git cmake

# For CUDA
sudo dnf install cuda-toolkit
```

**For Arch:**
```bash
# Install base development
sudo pacman -S base-devel git cmake

# For CUDA
sudo pacman -S cuda
```

**Verification:**
- Can build llama.cpp
- All imports work
- No library errors

**Prevention:**
- Install development packages early
- Keep system updated
- Document dependencies

---

#### Issue: CUDA Version Mismatch

**Symptoms:**
- CUDA version errors
- Cannot use GPU
- Driver incompatibility

**Cause:**
CUDA toolkit version doesn't match driver version.

**Solution:**

1. **Check versions:**
   ```bash
   # Driver version
   nvidia-smi

   # CUDA toolkit version
   nvcc --version
   ```

2. **Ensure compatibility:**
   - Driver version must support CUDA toolkit version
   - See: https://docs.nvidia.com/cuda/cuda-toolkit-release-notes/

3. **Update driver:**
   ```bash
   # Ubuntu
   sudo ubuntu-drivers autoinstall
   sudo reboot
   ```

4. **Or downgrade CUDA toolkit:**
   ```bash
   # Remove current
   sudo apt remove --purge cuda-toolkit-*

   # Install compatible version
   sudo apt install cuda-toolkit-11-8  # Example
   ```

**Verification:**
- CUDA works
- GPU accessible
- No version warnings

**Prevention:**
- Check compatibility before installing
- Keep driver updated first
- Read CUDA release notes

---

## Getting Help

### Before Asking for Help

1. **Check this troubleshooting guide**
   - Use Ctrl+F to search for error message
   - Follow solution steps carefully
   - Try verification steps

2. **Check documentation:**
   - `AI-ROUTER-ENHANCED-QUICKSTART.md`
   - `BATCH_PROCESSING_GUIDE.md`
   - `ANALYTICS_DASHBOARD_EXAMPLE.md`
   - `COMPARISON_MODE_SUMMARY.md`

3. **Gather information:**
   ```bash
   # System information
   uname -a
   python3 --version
   pip list | grep -E "yaml|jinja"

   # llama.cpp version
   llama-cli --version

   # Database info
   ls -lh /d/models/.ai-router-sessions.db
   sqlite3 /d/models/.ai-router-sessions.db "PRAGMA integrity_check;"

   # Recent errors
   # (Copy last 50 lines of error output)
   ```

### Where to Get Help

1. **GitHub Issues:**
   - Check existing issues first
   - Provide system information
   - Include error messages
   - Describe steps to reproduce

2. **Documentation:**
   - README files in `/d/models/`
   - Example files
   - Code comments

3. **Community:**
   - llama.cpp discussions for model issues
   - SQLite forums for database issues
   - Python forums for code issues

### How to Report Issues

Include:
- **System Information:**
  - OS and version
  - Python version
  - llama.cpp version
  - GPU model (if applicable)

- **Error Details:**
  - Full error message
  - Stack trace
  - When error occurs
  - What you were trying to do

- **Steps to Reproduce:**
  ```
  1. Navigate to /d/models
  2. Run: python ai-router.py
  3. Select option X
  4. Enter value Y
  5. Error appears
  ```

- **What You've Tried:**
  - Solutions from this guide
  - Workarounds attempted
  - Other troubleshooting steps

- **Logs/Output:**
  ```bash
  # Capture full output
  python ai-router.py 2>&1 | tee debug.log
  ```

---

## FAQ

### General

**Q: Do I need an internet connection?**
A: Only for:
- Installing dependencies (`pip install`)
- Cloud providers (OpenRouter, OpenAI, Claude)
- Web search features
- Local models work offline

**Q: How much disk space do I need?**
A: Depends on models:
- Application: ~10MB
- Database: Grows with usage (typically 10-100MB)
- Models: 4GB - 40GB each
- Recommend: 100GB+ for multiple models

**Q: Can I use cloud-only (no local models)?**
A: Yes, configure cloud providers (OpenRouter/OpenAI/Claude) and use without local models.

**Q: Can I run multiple instances?**
A: Not recommended. Database locking issues. Use single instance with sessions instead.

### Installation

**Q: Which Python version do I need?**
A: Python 3.7+ required. Python 3.10+ recommended.

**Q: Do I need a GPU?**
A: No, but highly recommended:
- CPU: Works but slow
- GPU: Much faster (5-10x)
- Best: NVIDIA GPU with CUDA

**Q: Can I use on Mac M1/M2/M3/M4?**
A: Yes! Use MLX for best performance (2-3x faster than llama.cpp).

### Models

**Q: Where do I get models?**
A:
- Hugging Face: https://huggingface.co/models
- TheBloke: GGUF quantizations
- mlx-community: MLX models for Mac

**Q: What's the difference between Q2_K, Q4_K_M, Q6_K?**
A:
- Q2_K: Smallest, fastest, lower quality
- Q4_K_M: Balanced (recommended)
- Q6_K: Larger, slower, best quality

**Q: Can I use multiple models?**
A: Yes! Switch between models or compare them.

**Q: Model is too slow, what can I do?**
A:
1. Use smaller quantization (Q6_K → Q4_K_M)
2. Use smaller model (70B → 32B → 14B)
3. Reduce context size
4. Upgrade hardware

### Features

**Q: How do I save my conversations?**
A: Automatically saved to database. Use Analytics to view.

**Q: Can I export conversations?**
A: Yes, to JSON or Markdown. Use Session Management features.

**Q: What are templates?**
A: Reusable prompt structures with variables. Saves time for common tasks.

**Q: What are workflows?**
A: Multi-step AI automations. Chain prompts together, pass variables between steps.

**Q: Can I batch process prompts?**
A: Yes! Use Batch Processing feature. Supports checkpointing and resume.

### Performance

**Q: Why is startup slow?**
A: Usually large database. Run cleanup:
```bash
python -c "from session_manager import SessionManager; from pathlib import Path; sm = SessionManager(Path('/d/models/.ai-router-sessions.db')); print(f'Deleted {sm.cleanup_old_sessions(90)} sessions')"
```

**Q: Why is model execution slow?**
A:
- Wrong hardware (CPU vs GPU)
- Model too large for system
- Insufficient VRAM
- Wrong quantization
See "Performance Issues" section.

**Q: Can I speed up queries?**
A: Yes:
1. Vacuum database: `sqlite3 /d/models/.ai-router-sessions.db "VACUUM;"`
2. Rebuild indexes (see "Slow Queries" section)
3. Archive old data

### Database

**Q: Where is the database?**
A: `/d/models/.ai-router-sessions.db`

**Q: Can I delete the database?**
A: Yes, but you'll lose all history. Backup first:
```bash
cp /d/models/.ai-router-sessions.db /d/models/.ai-router-sessions.db.backup
```

**Q: How do I backup?**
A:
```bash
# File copy
cp /d/models/.ai-router-sessions.db /d/models/backup-$(date +%Y%m%d).db

# Or SQL dump
sqlite3 /d/models/.ai-router-sessions.db ".dump" > backup.sql
```

**Q: Can I query the database directly?**
A: Yes:
```bash
sqlite3 /d/models/.ai-router-sessions.db

# Example queries
SELECT COUNT(*) FROM sessions;
SELECT * FROM sessions ORDER BY created_at DESC LIMIT 10;
SELECT model_id, COUNT(*) FROM sessions GROUP BY model_id;
```

### Troubleshooting

**Q: Application won't start, what do I do?**
A:
1. Check Python version: `python --version`
2. Check dependencies: `pip list | grep -E "yaml|jinja"`
3. Check directory: `pwd` (should be `/d/models`)
4. Check error message carefully
5. Search this guide for error

**Q: Getting "Module not found" errors**
A:
```bash
# Check you're in right directory
cd /d/models

# Reinstall dependencies
pip install --upgrade pyyaml jinja2
```

**Q: Database locked errors**
A:
1. Close other AI Router instances
2. Wait 30 seconds
3. Retry
4. If persists: `sqlite3 /d/models/.ai-router-sessions.db "VACUUM;"`

**Q: Model execution fails**
A:
1. Test llama.cpp directly: `llama-cli -m MODEL.gguf -p "Test" -n 10`
2. Check model path in code
3. Verify model file exists
4. Check VRAM if using GPU
5. Try smaller model

### Advanced

**Q: Can I customize the code?**
A: Yes! It's Python. Edit carefully and keep backups.

**Q: Can I add new models?**
A: Yes! Edit `RTX3090_MODELS` or `M4_MODELS` in `ai-router.py`.

**Q: Can I add new features?**
A: Yes! The codebase is modular. Each feature is a separate Python module.

**Q: How do I contribute?**
A:
1. Fork repository
2. Make changes
3. Test thoroughly
4. Submit pull request

**Q: Can I use for commercial projects?**
A: Check license. Usually open source licenses allow commercial use with attribution.

---

## Appendix: Quick Reference

### Common Commands

```bash
# Start application
cd /d/models && python ai-router.py

# Test llama.cpp
llama-cli -m MODEL.gguf -p "Test" -n 10

# Check database
sqlite3 /d/models/.ai-router-sessions.db "SELECT COUNT(*) FROM sessions;"

# Vacuum database
sqlite3 /d/models/.ai-router-sessions.db "VACUUM;"

# Backup database
cp /d/models/.ai-router-sessions.db /d/models/backup-$(date +%Y%m%d).db

# Clean old sessions (90 days)
python -c "from session_manager import SessionManager; from pathlib import Path; sm = SessionManager(Path('/d/models/.ai-router-sessions.db')); print(f'Deleted {sm.cleanup_old_sessions(90)} sessions')"

# Check Python version
python3 --version

# Check dependencies
pip list | grep -E "yaml|jinja|pyperclip"

# Check GPU
nvidia-smi

# Check CUDA
nvcc --version
```

### Directory Structure

```
/d/models/
├── ai-router.py                  # Main application
├── ai-router-enhanced.py         # Enhanced version
├── schema.sql                    # Database schema
├── .ai-router-sessions.db        # Session database
├── .ai-router-preferences.json   # User preferences
├── .ai-router-config.json        # Application config
├── response_processor.py         # Response handling
├── model_selector.py             # Model selection
├── context_manager.py            # Context injection
├── template_manager.py           # Template system
├── session_manager.py            # Session management
├── batch_processor.py            # Batch processing
├── analytics_dashboard.py        # Analytics
├── workflow_engine.py            # Workflows
├── model_comparison.py           # Comparisons
├── outputs/                      # Response outputs
├── prompt-templates/             # Prompt templates
├── workflows/                    # Workflow definitions
├── batch_checkpoints/            # Batch job checkpoints
├── comparisons/                  # Comparison results
└── projects/                     # Enhanced version projects
```

### Important File Locations

| File | Location | Purpose |
|------|----------|---------|
| Main Script | `/d/models/ai-router.py` | Entry point |
| Database | `/d/models/.ai-router-sessions.db` | Session storage |
| Schema | `/d/models/schema.sql` | Database structure |
| Config | `/d/models/.ai-router-config.json` | App settings |
| Preferences | `/d/models/.ai-router-preferences.json` | User preferences |
| Templates | `/d/models/prompt-templates/*.yaml` | Prompt templates |
| Workflows | `/d/models/workflows/*.yaml` | Workflow definitions |
| Checkpoints | `/d/models/batch_checkpoints/` | Batch progress |

---

**Last Updated**: 2025-12-09
**Version**: 1.0
**For AI Router Enhanced**: v2.0+

---

*If you've followed all troubleshooting steps and still have issues, please open a GitHub issue with detailed information about your problem.*
