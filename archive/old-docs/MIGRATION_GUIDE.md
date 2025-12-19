# Migration Guide: AI Router v1.0 → v2.0 Enhanced

**Complete Upgrade Guide** | Zero Downtime Migration

---

## Table of Contents

1. [What's New in v2.0](#whats-new-in-v20)
2. [Breaking Changes](#breaking-changes)
3. [Migration Steps](#migration-steps)
4. [Compatibility Notes](#compatibility-notes)
5. [Feature Mapping](#feature-mapping)
6. [Rollback Plan](#rollback-plan)

---

## What's New in v2.0

### Major New Features

| Feature | Status | Impact |
|---------|--------|--------|
| **Session Management** | ✅ New | Save/resume conversations |
| **Prompt Templates** | ✅ New | Reusable prompt structures |
| **Model Comparison** | ✅ New | A/B testing |
| **Response Processing** | ✅ New | Auto-formatting, export |
| **Batch Processing** | ✅ New | Multi-prompt automation |
| **Smart Selection** | ✅ Enhanced | AI-powered recommendations |
| **Analytics Dashboard** | ✅ New | Usage tracking, costs |
| **Context Management** | ✅ New | File/URL injection |
| **Workflow Engine** | ✅ New | Prompt chaining |

### Core Improvements

1. **Database Backend**: SQLite for persistent storage
2. **Template System**: YAML + Jinja2 for dynamic prompts
3. **Enhanced UI**: Better menus, progress bars, colored output
4. **Performance Tracking**: Real-time metrics for all models
5. **Cost Optimization**: Track and reduce API costs
6. **Search & Filter**: Find past conversations easily
7. **Export Capabilities**: JSON, MD, HTML, PDF formats
8. **Tag System**: Organize sessions with custom tags

---

## Breaking Changes

### ⚠️ IMPORTANT: Read Before Upgrading

#### 1. Database Requirement (NEW)

**v1.0**: No database, sessions lost on exit
**v2.0**: SQLite database required

**Action Required**:
```bash
# Initialize database before first use
python session_db_setup.py
```

#### 2. File Structure Changes

**v1.0 Structure**:
```
D:\models\
├── ai-router.py
├── model files (*.gguf)
└── system prompts (*.txt)
```

**v2.0 Structure**:
```
D:\models\
├── ai-router.py
├── .ai-router-sessions.db        ← NEW
├── .ai-router-config.json         ← NEW
├── session_manager.py             ← NEW
├── template_manager.py            ← NEW
├── batch_processor.py             ← NEW
├── analytics_dashboard.py         ← NEW
├── workflow_engine.py             ← NEW
├── context_manager.py             ← NEW
├── model_selector.py              ← NEW
├── response_processor.py          ← NEW
├── prompt-templates/              ← NEW
├── workflows/                     ← NEW
├── outputs/                       ← NEW
├── batch_checkpoints/             ← NEW
└── logs/                          ← NEW
```

**Action Required**: None - v2.0 creates directories automatically

#### 3. Dependencies Added

**v1.0**: No dependencies (standard library only)
**v2.0**: Additional dependencies required

**Action Required**:
```bash
pip install -r requirements.txt

# Required:
# - pyyaml (templates)
# - jinja2 (template rendering)

# Optional:
# - matplotlib (analytics charts)
# - plotly (interactive visualizations)
# - pdfplumber (PDF context injection)
```

#### 4. Configuration Format

**v1.0**: No configuration file
**v2.0**: JSON configuration at `.ai-router-config.json`

**Action Required**: None - auto-created on first launch

**Example Config**:
```json
{
  "bypass_mode": false,
  "version": "2.0.0",
  "default_model": "qwen25-14b",
  "analytics_enabled": true
}
```

---

## Migration Steps

### Step 1: Backup Existing Setup

```bash
# Create backup directory
mkdir -p D:\models\backups\v1.0

# Backup v1.0 files
cp ai-router.py backups/v1.0/
cp -r organized/ backups/v1.0/  # Your models
cp *.txt backups/v1.0/           # System prompts
```

### Step 2: Install v2.0

**Option A: In-Place Upgrade** (Recommended)

```bash
# Pull latest code
git pull origin main

# Or download new files
# (copy new Python files to D:\models\)

# Install dependencies
pip install -r requirements.txt
```

**Option B: Fresh Installation**

```bash
# Clone to new directory
git clone https://github.com/yourrepo/ai-router-enhanced.git D:\models\ai-router-v2

# Copy your models
cp -r D:\models\organized\ D:\models\ai-router-v2\

# Install dependencies
cd D:\models\ai-router-v2
pip install -r requirements.txt
```

### Step 3: Initialize Database

```bash
# Run database setup
python session_db_setup.py

# Expected output:
# Creating new session database: .ai-router-sessions.db
# Database initialized successfully!
# Tables created: sessions, messages, session_tags, bookmarks, analytics
```

### Step 4: Verify Models

```bash
# Launch v2.0
python ai-router.py

# Check that all your models are detected
# Main menu should show: "Models: 15 local + 100+ cloud"
```

### Step 5: Test Core Features

```bash
# Test 1: Create session
Menu → [1] New Session → Select model → Chat → exit

# Test 2: Resume session
Menu → [2] Resume Session → Select recent → Continue

# Test 3: Analytics (should have 1 session)
Menu → [6] Analytics Dashboard → [1] Usage Overview
```

### Step 6: Migrate Workflows (If Any)

If you had custom scripts in v1.0:

```bash
# Example v1.0 script:
wsl bash -c "~/llama.cpp/build/bin/llama-cli -m model.gguf -p 'prompt' ..."

# Convert to v2.0:
# 1. Create template (Menu → [7] → [c] Create new)
# 2. Or use batch processing (Menu → [5])
# 3. Or use workflow engine (workflows/*.yaml)
```

---

## Compatibility Notes

### Backward Compatibility

✅ **Fully Compatible**:
- All v1.0 models work without changes
- All system prompt files (.txt) work as-is
- All model paths remain valid
- Original `ai-router.py` can run alongside v2.0

❌ **Not Compatible**:
- v1.0 had no sessions to migrate (fresh start in v2.0)
- No configuration to migrate (v1.0 had none)

### Side-by-Side Operation

**v1.0 and v2.0 can run simultaneously**:

```bash
# Run v1.0 (old version)
python ai-router-v1.0.py

# Run v2.0 (new version)
python ai-router.py

# Both use same models, separate databases
```

**Isolation**:
- v2.0 database: `.ai-router-sessions.db`
- v2.0 config: `.ai-router-config.json`
- v1.0 has no persistent storage

### Platform Compatibility

| Platform | v1.0 | v2.0 | Notes |
|----------|------|------|-------|
| Windows | ✅ | ✅ | Identical support |
| WSL | ✅ | ✅ | Identical support |
| macOS | ✅ | ✅ | Identical support |
| Linux | ✅ | ✅ | Identical support |

---

## Feature Mapping

### v1.0 Feature → v2.0 Equivalent

| v1.0 Feature | v2.0 Equivalent | Enhancement |
|--------------|-----------------|-------------|
| **Manual model selection** | Smart Model Selection (Menu 8) | AI-powered recommendations |
| **Direct prompting** | Start New Session (Menu 1) | + persistent history |
| **No history** | Session Management (Menu 2) | Full conversation history |
| **Copy/paste prompts** | Prompt Templates (Menu 3) | Reusable with variables |
| **N/A** | Model Comparison (Menu 4) | NEW: A/B testing |
| **N/A** | Batch Processing (Menu 5) | NEW: Multi-prompt automation |
| **N/A** | Analytics (Menu 6) | NEW: Usage tracking |
| **N/A** | Context Injection | NEW: Add files/URLs |
| **N/A** | Workflow Engine | NEW: Prompt chaining |

### Command Line → Menu Navigation

**v1.0 Workflow**:
```bash
# 1. Choose model manually by reading docs
# 2. Run llama.cpp command
# 3. Lose conversation when exiting
```

**v2.0 Equivalent**:
```bash
# 1. Launch: python ai-router.py
# 2. [8] Smart Model Selection (auto-recommends)
# 3. [1] Start session
# 4. Chat (auto-saved)
# 5. exit (resume anytime with [2])
```

---

## Rollback Plan

If you need to revert to v1.0:

### Quick Rollback

```bash
# Option 1: Use backup
cp backups/v1.0/ai-router.py .
python ai-router.py

# Option 2: Git revert (if using git)
git checkout v1.0
python ai-router.py
```

### Data Preservation

**Before rollback**:
```bash
# Export all v2.0 sessions
python ai-router.py
Menu → [6] Analytics → [6] Export Report → [a] All sessions

# Saved to: outputs/all-sessions-[timestamp].json

# Backup database
cp .ai-router-sessions.db backups/sessions-before-rollback.db
```

**After rollback**:
- v1.0 runs normally (no database needed)
- Can upgrade again later
- Exported data preserved in `outputs/`

---

## Migration Checklist

Use this checklist to ensure smooth migration:

### Pre-Migration

- [ ] Read this entire guide
- [ ] Backup v1.0 files
- [ ] Note your most-used models
- [ ] Export any important prompts/responses
- [ ] Check Python version (3.7+)
- [ ] Verify disk space (5GB minimum)

### During Migration

- [ ] Install v2.0 files
- [ ] Install Python dependencies
- [ ] Run database setup
- [ ] Verify model detection
- [ ] Test basic session
- [ ] Test model selection
- [ ] Review new features

### Post-Migration

- [ ] Create your first real session
- [ ] Set up templates (if desired)
- [ ] Configure API keys (if using cloud)
- [ ] Explore analytics dashboard
- [ ] Bookmark this guide for reference
- [ ] Update shortcuts/scripts
- [ ] Train team (if applicable)

---

## Troubleshooting Migration Issues

### Issue 1: Database Creation Failed

**Error**: `sqlite3.OperationalError: unable to open database file`

**Solution**:
```bash
# Check permissions
ls -la D:\models\

# Ensure write access
chmod +w D:\models\  # Linux/macOS
# Or check folder properties → Security (Windows)

# Retry
python session_db_setup.py
```

### Issue 2: Missing Dependencies

**Error**: `ModuleNotFoundError: No module named 'yaml'`

**Solution**:
```bash
# Install all required dependencies
pip install -r requirements.txt

# Or install individually:
pip install pyyaml jinja2 matplotlib plotly
```

### Issue 3: Models Not Detected

**Error**: `No models found for this platform`

**Solution**:
```bash
# Verify model paths in ai-router.py
# For WSL:
ls /mnt/d/models/organized/*.gguf

# For macOS:
ls ~/models/*.gguf

# Update paths in ModelDatabase.RTX3090_MODELS or M4_MODELS
```

### Issue 4: Performance Degradation

**Symptom**: v2.0 slower than v1.0

**Solution**:
```bash
# Database overhead is minimal (<1% typically)
# If experiencing slowness:

# 1. Vacuum database
python session_db_setup.py --vacuum

# 2. Check disk space
df -h

# 3. Disable analytics temporarily
Menu → [9] Settings → Disable analytics

# 4. Clear old sessions
Menu → [9] Settings → Delete old sessions
```

---

## FAQ: Migration Questions

**Q: Will v2.0 delete my v1.0 setup?**
A: No. v2.0 is fully compatible and can run alongside v1.0.

**Q: Do I need to reconfigure my models?**
A: No. All v1.0 model configurations work in v2.0 unchanged.

**Q: Can I migrate v1.0 conversations?**
A: v1.0 had no persistent storage, so nothing to migrate. Fresh start in v2.0.

**Q: Is there a performance cost for the database?**
A: Minimal (<1%). Most operations complete in <10ms.

**Q: Can I go back to v1.0 after trying v2.0?**
A: Yes. Keep v1.0 files backed up and you can switch anytime.

**Q: Do I need all the new features?**
A: No. You can use v2.0 just like v1.0 (Menu → [1] → Chat → exit).

**Q: Will this work on my platform?**
A: Yes. v2.0 supports all v1.0 platforms (Windows, WSL, macOS, Linux).

**Q: How long does migration take?**
A: 10-15 minutes for full setup, 2 minutes for minimal setup.

---

## Support During Migration

### Getting Help

1. **Check Troubleshooting** (above)
2. **Review Documentation**:
   - [README-ENHANCED.md](README-ENHANCED.md)
   - [USER_GUIDE.md](USER_GUIDE.md)
   - [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
3. **GitHub Issues**: Report migration problems
4. **Discord/Community**: Ask questions
5. **Email Support**: support@yourproject.com

### Reporting Migration Issues

When reporting issues, include:

```
Migration Issue Report
───────────────────────
v1.0 Config:
- Platform: Windows/WSL/macOS/Linux
- Python version: 3.x
- Models used: [list]

v2.0 Setup:
- Installation method: Git/Download
- Dependencies installed: Yes/No
- Database created: Yes/No
- Error message: [full text]

Steps attempted:
1. ...
2. ...
```

---

## Success Metrics

After migration, you should have:

✅ Database initialized (`.ai-router-sessions.db` exists)
✅ All models detected (same count as v1.0)
✅ First session created and saved
✅ Can resume saved session
✅ Analytics show usage data
✅ Templates accessible (Menu → [3])

---

## Next Steps After Migration

Once migrated successfully:

1. **Explore New Features**:
   - Create your first template (Menu → [7])
   - Try model comparison (Menu → [4])
   - Run a batch job (Menu → [5])
   - Check analytics (Menu → [6])

2. **Optimize Your Workflow**:
   - Set up templates for common tasks
   - Configure cloud API keys (if using)
   - Customize model preferences
   - Set up workflows (advanced)

3. **Learn Advanced Features**:
   - Read [USER_GUIDE.md](USER_GUIDE.md)
   - Try context injection
   - Explore workflow engine
   - Review API reference

---

**Migration Complete?**

🎉 **Welcome to AI Router Enhanced v2.0!**

Start exploring: `python ai-router.py`

---

_Last Updated: December 8, 2025_
_Migration Guide v2.0.0_
