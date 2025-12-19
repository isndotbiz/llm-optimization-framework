# AI Router Enhanced v2.0 - Complete Deployment Checklist

**Deployment Date:** _________________
**Deployment Lead:** _________________
**Environment:** ☐ Development  ☐ Staging  ☐ Production

---

## Pre-Deployment Checks

### 1. Environment Verification

#### Python Environment
- [ ] **Python version verified** (3.8+ required)
  ```bash
  python --version  # Should show 3.8 or higher
  ```
  Expected: `Python 3.8+`

- [ ] **Virtual environment created** (recommended)
  ```bash
  python -m venv venv
  source venv/bin/activate  # Linux/Mac
  # OR
  venv\Scripts\activate  # Windows
  ```

#### System Requirements
- [ ] **Disk space available** (minimum 100 MB, recommended 500 MB)
  ```bash
  df -h .  # Linux/Mac
  # OR check in File Explorer (Windows)
  ```

- [ ] **Platform detected correctly**
  - [ ] Windows 10/11
  - [ ] WSL (Windows Subsystem for Linux)
  - [ ] macOS (Intel or M-series)
  - [ ] Linux (Ubuntu/Debian/RHEL)

### 2. Source Files Verification

#### Core Application Files
- [ ] **ai-router.py present** (main application, 2,932 lines)
- [ ] **ai-router-enhanced.py present** (alternative version)

#### Feature Modules (9 required)
- [ ] session_manager.py (15,358 bytes)
- [ ] template_manager.py (9,346 bytes)
- [ ] context_manager.py (9,457 bytes)
- [ ] response_processor.py (7,476 bytes)
- [ ] model_selector.py (10,732 bytes)
- [ ] model_comparison.py (15,033 bytes)
- [ ] batch_processor.py (12,368 bytes)
- [ ] analytics_dashboard.py (12,471 bytes)
- [ ] workflow_engine.py (19,159 bytes)

#### Database Schema Files
- [ ] schema.sql (main session schema)
- [ ] analytics_schema.sql
- [ ] comparison_schema.sql
- [ ] llm_session_management_schema.sql
- [ ] llm_session_examples.sql

#### Directory Structure
- [ ] `providers/` directory present (7 files)
- [ ] `prompt-templates/` directory present (5+ files)
- [ ] `context-templates/` directory present (3+ files)
- [ ] `workflows/` directory present (4+ files)
- [ ] `workflow_examples/` directory present (5+ files)
- [ ] `tests/` directory present (4+ files)

#### Documentation
- [ ] README-ENHANCED.md present
- [ ] USER_GUIDE.md present
- [ ] QUICK_REFERENCE.md present
- [ ] FEATURE_DOCUMENTATION.md present
- [ ] TESTING_GUIDE.md present

### 3. Dependencies Installation

#### Install Core Dependencies
```bash
pip install -r requirements.txt
```

**Required packages (verify installation):**
- [ ] **PyYAML** (>= 6.0)
  ```bash
  python -c "import yaml; print('PyYAML:', yaml.__version__)"
  ```
  Expected: `PyYAML: 6.0+`

- [ ] **Jinja2** (>= 3.1.0)
  ```bash
  python -c "import jinja2; print('Jinja2:', jinja2.__version__)"
  ```
  Expected: `Jinja2: 3.1+`

- [ ] **SQLite3** (built-in, verify)
  ```bash
  python -c "import sqlite3; print('SQLite3:', sqlite3.sqlite_version)"
  ```
  Expected: `SQLite3: 3.x+`

- [ ] **Requests** (for cloud providers)
  ```bash
  python -c "import requests; print('Requests:', requests.__version__)"
  ```

#### Optional Dependencies
- [ ] **pyperclip** (clipboard functionality)
  ```bash
  pip install pyperclip
  python -c "import pyperclip; print('pyperclip: installed')"
  ```
  Note: If fails, clipboard features will be disabled (non-critical)

### 4. Configuration Setup

#### Directory Creation
The application will auto-create these, but verify permissions:
- [ ] `sessions/` - Session storage directory
- [ ] `outputs/` - Response output files
- [ ] `batch_checkpoints/` - Batch processing checkpoints
- [ ] `comparisons/` - Model comparison results

#### API Keys (if using cloud providers)
- [ ] **OpenAI API Key** (if using OpenAI models)
  ```bash
  export OPENAI_API_KEY="sk-..."
  # OR add to ~/.bashrc or ~/.zshrc
  ```

- [ ] **Anthropic API Key** (if using Claude models)
  ```bash
  export ANTHROPIC_API_KEY="sk-ant-..."
  ```

- [ ] **OpenRouter API Key** (if using OpenRouter)
  ```bash
  export OPENROUTER_API_KEY="sk-or-..."
  ```

#### File Permissions
- [ ] **Verify read/write permissions** on deployment directory
  ```bash
  ls -la ai-router.py  # Should show read/execute permissions
  chmod +x ai-router.py  # If needed
  ```

### 5. Pre-Deployment Validation

#### Run Validation Suite
- [ ] **Installation validator**
  ```bash
  python validate_installation.py
  ```
  Expected: `26/26 checks passed`

- [ ] **Module import test**
  ```bash
  python -c "from session_manager import SessionManager; from template_manager import TemplateManager; from context_manager import ContextManager; from response_processor import ResponseProcessor; from model_selector import ModelSelector; from batch_processor import BatchProcessor; from analytics_dashboard import AnalyticsDashboard; from workflow_engine import WorkflowEngine; from model_comparison import ModelComparison; print('All modules imported successfully')"
  ```
  Expected: `All modules imported successfully`

#### Smoke Test (Optional but Recommended)
- [ ] **Run smoke test**
  ```bash
  python smoke_test.py
  ```
  Expected: 6+ tests pass (some test issues expected, non-critical)

### 6. Backup Current State

If upgrading existing installation:
- [ ] **Backup existing session database**
  ```bash
  cp .ai-router-sessions.db .ai-router-sessions.db.backup-$(date +%Y%m%d)
  ```

- [ ] **Backup existing configuration files**
  ```bash
  cp -r prompt_templates prompt_templates.backup-$(date +%Y%m%d)
  cp -r workflows workflows.backup-$(date +%Y%m%d)
  ```

---

## Installation Steps

### Step 1: Deploy Files

#### Option A: Fresh Installation
```bash
# Clone or extract to deployment directory
cd /path/to/deployment
# Extract AI Router Enhanced files here
```

#### Option B: Update Existing Installation
```bash
# Backup first (see above)
# Replace files with new version
# Preserve custom templates and workflows
```

### Step 2: Initialize Application

- [ ] **Run initial setup**
  ```bash
  python ai-router.py
  ```

- [ ] **Verify menu displays**
  Expected output:
  ```
  ============================================================
  AI ROUTER ENHANCED v2.0
  Intelligent Multi-Model AI Orchestration
  ============================================================
  ```

- [ ] **Exit cleanly** (type `0` or `/exit`)

### Step 3: Create First Session (Basic Functionality Test)

- [ ] **Start new session**
  ```bash
  python ai-router.py
  # Select [1] Start New Session
  ```

- [ ] **Select any available model**
  - Local model (if configured)
  - Cloud model (if API keys set)

- [ ] **Send test prompt**
  ```
  Say "Hello, World!" and confirm you're working correctly.
  ```

- [ ] **Verify response received**

- [ ] **Exit session** (type `/exit`)

---

## Configuration Steps

### 1. Model Configuration

#### Local Models (Optional)
- [ ] **Configure llama.cpp models** (if using)
  - Edit model paths in `ai-router.py` (lines 95-240)
  - Verify model files exist
  - Test model loading

- [ ] **Configure Ollama models** (if using)
  ```bash
  ollama list  # Verify Ollama installed and models available
  ```

#### Cloud Models
- [ ] **Verify API keys set** (see Pre-Deployment step 4)
- [ ] **Test API connectivity**
  ```bash
  # Run test session with cloud model
  python ai-router.py
  # Select cloud model and send test prompt
  ```

### 2. Template Configuration

- [ ] **Review default templates** in `prompt-templates/`
- [ ] **Add custom templates** (if needed)
  ```yaml
  # Create new template in prompt-templates/
  metadata:
    name: Custom Template
    description: Your description

  user_prompt: |
    Your prompt template here
  ```

### 3. Workflow Configuration

- [ ] **Review example workflows** in `workflows/`
- [ ] **Add custom workflows** (if needed)
  ```yaml
  # Create new workflow in workflows/
  name: Custom Workflow
  description: Your description

  steps:
    - name: step1
      type: prompt
      config:
        prompt: "Your prompt"
  ```

### 4. Analytics Configuration

- [ ] **Verify session database created**
  ```bash
  ls -la .ai-router-sessions.db
  ```

- [ ] **Test analytics dashboard**
  ```bash
  python ai-router.py
  # Select [6] Analytics Dashboard
  # Verify display works
  ```

---

## Validation Steps

### 1. Feature Testing

Test each core feature:

#### Session Management
- [ ] **Create new session**
- [ ] **Save session**
- [ ] **Resume session**
- [ ] **Search sessions**
- [ ] **Add tags to session**
- [ ] **Export session**

#### Template System
- [ ] **List templates**
- [ ] **Use template**
- [ ] **Create custom template**
- [ ] **Template variable substitution works**

#### Model Comparison
- [ ] **Start comparison mode**
- [ ] **Select multiple models**
- [ ] **Compare responses**
- [ ] **Save comparison results**

#### Batch Processing
- [ ] **Create batch job**
- [ ] **Run batch with sample prompts**
- [ ] **Verify checkpoint system works**
- [ ] **Review batch results**

#### Analytics Dashboard
- [ ] **View usage statistics**
- [ ] **View model performance metrics**
- [ ] **View cost analysis** (if using cloud models)

#### Context Management
- [ ] **Add file context**
- [ ] **Add text context**
- [ ] **Verify context injection**
- [ ] **Clear context**

#### Workflow Engine
- [ ] **List workflows**
- [ ] **Run simple workflow**
- [ ] **Verify step execution**
- [ ] **Check workflow results**

#### Response Processing
- [ ] **Save response to file**
- [ ] **Extract code blocks**
- [ ] **Format as markdown**
- [ ] **Copy to clipboard** (if pyperclip installed)

#### Smart Model Selection
- [ ] **Use auto-selection**
- [ ] **Verify model recommendation**
- [ ] **Update preferences**

### 2. Integration Testing

Test cross-feature functionality:

- [ ] **Template + Context**
  - Use template with file context
  - Verify both work together

- [ ] **Session + Analytics**
  - Create session with multiple messages
  - View analytics for that session
  - Verify metrics calculated correctly

- [ ] **Batch + Templates**
  - Run batch job using template
  - Verify template applied to all prompts

- [ ] **Workflow + Sessions**
  - Run workflow
  - Verify workflow saved to session

### 3. Performance Testing

- [ ] **Startup time** (< 1 second expected)
  ```bash
  time python ai-router.py --version
  ```

- [ ] **Database query speed** (< 0.01s expected)
  - Create session
  - List sessions
  - Search sessions

- [ ] **Template rendering speed** (< 0.001s expected)
  - Load template
  - Render with variables

### 4. Error Handling Testing

Test graceful error handling:

- [ ] **Invalid model selection**
- [ ] **Network timeout** (cloud models)
- [ ] **File not found** (context/template)
- [ ] **Invalid YAML** (template/workflow)
- [ ] **Database locked** (concurrent access)
- [ ] **Keyboard interrupt** (Ctrl+C)

---

## Post-Deployment Verification

### 1. Smoke Test

- [ ] **Application starts without errors**
- [ ] **Menu displays correctly**
- [ ] **Navigation works**
- [ ] **Can create and save session**
- [ ] **Can exit cleanly**

### 2. Log Review

- [ ] **Check console output for errors**
- [ ] **Verify database initialized message**
- [ ] **No Python exceptions in output**

### 3. File System Check

- [ ] **Session database created** (`.ai-router-sessions.db`)
- [ ] **Output directory created** (`outputs/`)
- [ ] **No orphaned temp files**

### 4. User Acceptance Test

- [ ] **Run through USER_GUIDE.md tutorial**
- [ ] **Complete at least 3 different workflows**
- [ ] **Verify all menu options accessible**
- [ ] **Confirm documentation matches behavior**

---

## Rollback Procedure

If deployment fails, follow these steps:

### 1. Stop Application
```bash
# If running, press Ctrl+C or kill process
pkill -f ai-router.py
```

### 2. Restore Backups

#### Restore Session Database
```bash
cp .ai-router-sessions.db.backup-YYYYMMDD .ai-router-sessions.db
```

#### Restore Templates/Workflows
```bash
rm -rf prompt_templates workflows
cp -r prompt_templates.backup-YYYYMMDD prompt_templates
cp -r workflows.backup-YYYYMMDD workflows
```

### 3. Restore Previous Version

#### Git-based Rollback
```bash
git checkout previous-version-tag
```

#### Manual Rollback
```bash
# Extract previous version files
# Replace current files with previous version
```

### 4. Verify Rollback

- [ ] **Application starts**
- [ ] **Sessions accessible**
- [ ] **No data loss**

### 5. Document Issue

- [ ] **Record what went wrong**
- [ ] **Note error messages**
- [ ] **Identify cause**
- [ ] **Plan remediation**

---

## Support Contacts

### Technical Support
- **Email:** _________________
- **Phone:** _________________
- **Slack/Discord:** _________________

### Documentation
- **GitHub Issues:** _________________
- **Wiki:** _________________
- **FAQ:** _________________

### Escalation Path
1. **Level 1:** Check USER_GUIDE.md and TROUBLESHOOTING.md
2. **Level 2:** Search GitHub issues / documentation
3. **Level 3:** Contact technical support
4. **Level 4:** Escalate to development team

---

## Deployment Sign-Off

### Completed By

**Name:** _________________
**Date:** _________________
**Time:** _________________

### Verification

- [ ] All pre-deployment checks completed
- [ ] Installation steps completed successfully
- [ ] Configuration verified
- [ ] All validation tests passed
- [ ] Post-deployment verification complete
- [ ] Rollback procedure documented and tested
- [ ] Support contacts updated
- [ ] Users notified (if applicable)

### Notes

_____________________________________________

_____________________________________________

_____________________________________________

### Approval

**Approved By:** _________________
**Signature:** _________________
**Date:** _________________

---

## Additional Notes

### Common Issues and Solutions

#### Issue: "Module not found" errors
**Solution:**
```bash
# Ensure you're in the correct directory
cd /path/to/ai-router
# Verify Python path
python -c "import sys; print(sys.path)"
```

#### Issue: "Permission denied" errors
**Solution:**
```bash
chmod +x ai-router.py
chmod 755 .
```

#### Issue: Database locked
**Solution:**
```bash
# Close all instances of AI Router
pkill -f ai-router.py
# Remove lock file if exists
rm -f .ai-router-sessions.db-journal
```

#### Issue: API key errors
**Solution:**
```bash
# Verify API key set
echo $OPENAI_API_KEY  # Should show key
# If empty, set it
export OPENAI_API_KEY="sk-..."
```

#### Issue: Template not found
**Solution:**
```bash
# Verify template directory
ls -la prompt-templates/
# Ensure YAML files have .yaml extension
```

### Performance Tuning

For optimal performance:
- **Use SSD** for database storage
- **Allocate sufficient RAM** (100+ MB recommended)
- **Use Python 3.10+** for best performance
- **Enable pyperclip** for clipboard functionality
- **Use local models** for fastest response times

### Security Best Practices

- **Secure API keys** - Use environment variables, never commit to git
- **Restrict database permissions** - `chmod 600 .ai-router-sessions.db`
- **Validate user input** - Already implemented in application
- **Keep dependencies updated** - Run `pip list --outdated`
- **Regular backups** - Automate session database backups

---

## Deployment Checklist Version

**Checklist Version:** 1.0
**Last Updated:** 2025-12-08
**Compatible with:** AI Router Enhanced v2.0
**Next Review Date:** _________________

---

## Appendix: Quick Command Reference

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Validate installation
python validate_installation.py

# Run smoke test
python smoke_test.py
```

### Startup
```bash
# Start AI Router
python ai-router.py

# Start with specific model (if supported)
python ai-router.py --model qwen3-coder-30b
```

### Maintenance
```bash
# Backup database
cp .ai-router-sessions.db .ai-router-sessions.db.backup-$(date +%Y%m%d)

# Clean output directory
rm -f outputs/*

# Update dependencies
pip install -r requirements.txt --upgrade
```

### Troubleshooting
```bash
# Check Python version
python --version

# Verify dependencies
pip list | grep -E "(PyYAML|Jinja2|pyperclip)"

# Test module imports
python -c "from session_manager import SessionManager; print('OK')"

# Check database
sqlite3 .ai-router-sessions.db "SELECT COUNT(*) FROM sessions;"
```

---

**END OF DEPLOYMENT CHECKLIST**
