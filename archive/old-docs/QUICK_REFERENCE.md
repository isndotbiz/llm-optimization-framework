# AI Router Enhanced v2.0 - Quick Reference

**One-Page Cheat Sheet** | Print-friendly format

---

## Menu Navigation

```
MAIN MENU                          SESSION COMMANDS
────────────────                   ────────────────────────
[1] Start New Session              /help      Show commands
[2] Resume Session                 /save      Save & continue
[3] Use Template                   /exit      Save & quit
[4] Compare Models (A/B)           /tags      Add tags
[5] Batch Processing               /bookmark  Bookmark
[6] Analytics Dashboard            /context   Add context
[7] Manage Templates               /export    Export conversation
[8] Smart Model Selection          /switch    Change model
[9] Configure Settings             /clear     Clear history
[0] Exit                           /stats     Show statistics
```

---

## Model Selection Guide

| Task Type | Best Model | Why | Speed |
|-----------|------------|-----|-------|
| **Coding** | qwen3-coder-30b | 94% HumanEval, 69.6% SWE-bench | 25-40 tok/s |
| **Math/Logic** | phi4-14b | 85% AIME, 78% reasoning | 35-55 tok/s |
| **Creative** | gemma3-27b | 128K context, abliterated | 25-45 tok/s |
| **Research** | llama33-70b | 70B params, deep analysis | 20-35 tok/s |
| **General** | qwen25-14b | Balanced, reliable | 40-60 tok/s |
| **Fast/Simple** | dolphin-8b | Quick responses | 60-90 tok/s |
| **Complex Reasoning** | ministral-3-14b | 256K context, 85% AIME | 40-65 tok/s |
| **Chain-of-Thought** | deepseek-r1-14b | 94.3% MATH-500 | 40-65 tok/s |

---

## Common Workflows

### Quick Session
```bash
python ai-router.py
[1] New Session → Select model → Chat → exit
```

### Use Template
```bash
python ai-router.py
[3] Use Template → Choose template → Fill variables → Execute
```

### Batch Process
```bash
# 1. Create prompts.txt (one prompt per line)
# 2. Run: Menu → [5] Batch → Load file → Select model
```

### Compare Models
```bash
python ai-router.py
[4] Compare → Model A → Model B → Enter prompt → Vote
```

---

## File Locations

| Item | Location |
|------|----------|
| **Database** | `.ai-router-sessions.db` |
| **Templates** | `prompt-templates/*.yaml` |
| **Workflows** | `workflows/*.yaml` |
| **Outputs** | `outputs/` |
| **Batch Checkpoints** | `batch_checkpoints/` |
| **Models (WSL)** | `/mnt/d/models/organized/` |
| **Models (macOS)** | `~/models/` |
| **Config** | `.ai-router-config.json` |
| **Logs** | `logs/ai-router.log` |

---

## Configuration Options

### Parameters (per session)

| Parameter | Range | Default | Purpose |
|-----------|-------|---------|---------|
| Temperature | 0.0-2.0 | 0.7 | Creativity/randomness |
| Top P | 0.0-1.0 | 0.9 | Nucleus sampling |
| Top K | 0-200 | 40 | Token selection |
| Max Tokens | 1-32768 | 4096 | Response length |
| Context Window | Model-dependent | 32K | Input length |

### Environment Variables

```bash
export OPENROUTER_API_KEY="sk-or-..."
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

---

## Template Syntax

### Basic Template (YAML)
```yaml
metadata:
  name: "Code Review"
  description: "Review code for issues"
  variables:
    - name: language
      default: "Python"
    - name: code
      description: "Code to review"
    - name: focus
      default: "all"

system_prompt: |
  You are an expert {{language}} code reviewer.

user_prompt: |
  Review this {{language}} code:
  ```
  {{code}}
  ```
  Focus on: {{focus}}
```

### Using Templates
1. Place YAML in `prompt-templates/`
2. Menu → [3] Use Template
3. Select template
4. Fill variables
5. Execute

---

## Keyboard Shortcuts

| Shortcut | Action | Context |
|----------|--------|---------|
| `Ctrl+C` | Cancel/Interrupt | Any |
| `Ctrl+D` | Exit | Main menu |
| `/help` | Show commands | Session |
| `/exit` | Save & quit | Session |
| `Ctrl+P` | Pause | Batch processing |
| `Ctrl+S` | Save | Template editor |

---

## Analytics Quick View

```bash
Menu → [6] Analytics Dashboard

[1] Usage Overview      - Sessions, messages, tokens
[2] Model Performance   - Speed, quality comparisons
[3] Cost Analysis       - API spending breakdown
[4] Session Stats       - Individual session details
[5] Custom Range        - Filter by date
[6] Export Report       - Save as JSON/CSV/HTML
```

---

## Batch Processing Checklist

- [ ] Create prompts file (txt or JSON)
- [ ] Choose model based on task type
- [ ] Set delay between prompts (default: 2s)
- [ ] Configure retry attempts (default: 3)
- [ ] Start processing
- [ ] Monitor progress
- [ ] Review results in outputs/

---

## Troubleshooting Quick Fixes

| Problem | Quick Fix |
|---------|-----------|
| **CUDA out of memory** | Use smaller model or Q4_K_M quantization |
| **Slow responses** | Check GPU usage (`nvidia-smi`), use WSL |
| **Database locked** | Close other AI Router instances |
| **Template errors** | Check variable names (case-sensitive) |
| **API auth failed** | Verify API key: `echo $OPENROUTER_API_KEY` |
| **Model not found** | Check path in ModelDatabase config |

---

## Performance Optimization

### Local Models (RTX 3090)
```bash
# Optimal llama.cpp flags (WSL)
-ngl 99 -t 24 -b 2048 --no-ppl --enable-chunked-prefill
```

### Faster Inference
- Use Q4_K_M instead of Q6_K (-15% quality, +30% speed)
- Smaller models (8B instead of 30B)
- Reduce max_tokens
- WSL instead of Windows (+45-60% speed)

### Better Quality
- Larger models (30B, 70B)
- Higher quantization (Q6_K, Q8_0)
- Add context with `/context`
- Use templates for structure

---

## API Cost Estimates

| Provider | Model Tier | Cost per 1M tokens | Example |
|----------|------------|-------------------|---------|
| **OpenRouter** | Small (7-13B) | $0.01-0.10 | 100 chats ≈ $0.50 |
| **OpenRouter** | Medium (30-70B) | $0.50-2.00 | 100 chats ≈ $5.00 |
| **OpenAI** | GPT-3.5 | $0.50-1.50 | 100 chats ≈ $2.00 |
| **OpenAI** | GPT-4 | $30-60 | 100 chats ≈ $50.00 |
| **Claude** | Haiku | $0.25-1.25 | 100 chats ≈ $1.50 |
| **Claude** | Sonnet | $3-15 | 100 chats ≈ $10.00 |
| **Local** | Any | $0.00 | ∞ chats = FREE |

*Track actual costs in Analytics Dashboard*

---

## Database Maintenance

```bash
# Backup database
cp .ai-router-sessions.db backups/sessions-$(date +%Y%m%d).db

# Vacuum (optimize)
python session_db_setup.py --vacuum

# Export all sessions
Menu → [6] Analytics → [6] Export → Select "All sessions"

# Clear old sessions (interactive)
Menu → [9] Settings → [d] Delete old sessions
```

---

## Model Parameter Presets

### Conservative (Factual)
```
Temperature: 0.3
Top P: 0.85
Top K: 20
```

### Balanced (Default)
```
Temperature: 0.7
Top P: 0.9
Top K: 40
```

### Creative
```
Temperature: 0.9
Top P: 0.95
Top K: 80
```

### Very Creative
```
Temperature: 1.2
Top P: 0.98
Top K: 120
```

---

## Export Formats

| Format | Use Case | Command |
|--------|----------|---------|
| **JSON** | Machine processing | `/export → [1] JSON` |
| **Markdown** | Documentation | `/export → [2] Markdown` |
| **HTML** | Web publishing | `/export → [3] HTML` |
| **PDF** | Printing | `/export → [4] PDF` |
| **TXT** | Plain text | `/export → [5] Plain text` |

---

## Session Tags

**Recommended Tag Categories**:
- **Type**: coding, math, creative, research, debug
- **Language**: python, javascript, rust, etc.
- **Project**: project-name
- **Status**: draft, review, final
- **Priority**: urgent, important, low

**Tag Commands**:
```
/tags add coding python flask
/tags remove draft
/tags list
/tags search coding
```

---

## Context Injection

### Add File Context
```
/context
Type: [1] File
Path: /path/to/file.py
Added: 245 lines
```

### Add Directory Context
```
/context
Type: [2] Directory
Path: /path/to/project
Indexed: 47 files (12,445 lines)
```

### Add URL Context
```
/context
Type: [3] URL
URL: https://example.com/article
Fetched: 2,345 words
```

### Add Code Snippet
```
/context
Type: [4] Code snippet
Language: Python
[Paste code, end with Ctrl+D]
```

---

## Emergency Commands

| Situation | Command |
|-----------|---------|
| **Stuck/Frozen** | `Ctrl+C` (safe interrupt) |
| **Lost session** | Menu → [2] Resume → [r] Recent |
| **Corrupted database** | Restore from backup |
| **Out of disk** | Clear `outputs/`, `batch_checkpoints/` |
| **GPU crash** | Restart, use smaller model |

---

## Support Resources

| Resource | Location |
|----------|----------|
| **Full Documentation** | `USER_GUIDE.md` |
| **Technical Docs** | `DEVELOPER_GUIDE.md` |
| **Feature Details** | `FEATURE_DOCUMENTATION.md` |
| **API Reference** | `API_REFERENCE.md` |
| **Migration Guide** | `MIGRATION_GUIDE.md` |
| **GitHub Issues** | github.com/yourrepo/issues |
| **Discord** | discord.gg/yourserver |
| **Email** | support@yourproject.com |

---

## Version Information

- **Version**: 2.0.0
- **Release**: December 8, 2025
- **Status**: Production Ready
- **Python**: 3.7+
- **Platform**: Windows, WSL, macOS, Linux

---

**Print this page for offline reference**

📄 **[Download PDF Version](docs/AI-Router-Quick-Reference.pdf)** (Coming Soon)

---

_Last Updated: December 8, 2025_
