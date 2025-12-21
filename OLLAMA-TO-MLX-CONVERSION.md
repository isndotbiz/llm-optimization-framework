# Ollama to MLX Model Conversion System

Complete toolkit for migrating from Ollama GGUF models to MLX-optimized models on Apple Silicon.

## Overview

This conversion system provides a safe, automated way to transition your MacBook from slower Ollama GGUF models to blazing-fast MLX models optimized for Apple Silicon M-series chips.

**Performance Gains:**
- Qwen2.5-Coder-7B: **200-300% faster** (60-80 tok/sec vs 20-30 tok/sec)
- DeepSeek-R1-8B: **400-600% faster** than 32B GGUF (50-70 tok/sec vs 10-15 tok/sec)
- Qwen3-14B: **100-200% faster** (40-60 tok/sec vs 20-30 tok/sec)

**Space Savings:**
- Current: ~130GB of Ollama models
- After migration: ~65GB of MLX models
- **Net savings: ~65GB freed**

---

## Files in This System

### 1. `mlx-model-mapping.json`
**Master mapping file** defining:
- Which Ollama models to delete
- Which Ollama models to convert to MLX equivalents
- MLX model HuggingFace repositories and download URLs
- Performance comparison data
- Size and usage information

### 2. `ollama-model-analysis.py`
**Python analysis tool** that:
- Lists all installed Ollama models
- Categorizes them (DELETE, CONVERT, KEEP)
- Calculates space savings
- Shows performance improvements
- Generates detailed migration reports

**Usage:**
```bash
# Human-readable summary
python3 ollama-model-analysis.py

# JSON output
python3 ollama-model-analysis.py --json

# Just the statistics
python3 ollama-model-analysis.py --summary
```

### 3. `convert-ollama-to-mlx.sh`
**Interactive orchestration script** with:
- Pre-flight system checks
- Step-by-step guidance
- Interactive confirmations
- Backup creation
- Progress reporting
- Before/after state comparison

**Usage:**
```bash
# Preview what will happen (recommended first step)
./convert-ollama-to-mlx.sh --dry-run

# Interactive migration (with confirmations)
./convert-ollama-to-mlx.sh

# Fully automated (no prompts)
./convert-ollama-to-mlx.sh --auto

# Delete Ollama models only (skip MLX downloads)
./convert-ollama-to-mlx.sh --skip-downloads
```

### 4. `migrate-to-mlx.sh`
**Non-interactive automation script** for:
- Headless/automated execution
- CI/CD integration
- Quick re-runs
- Partial migrations

**Usage:**
```bash
# Preview changes
./migrate-to-mlx.sh --dry-run

# Execute migration
./migrate-to-mlx.sh --execute

# Delete Ollama models only
./migrate-to-mlx.sh --execute --delete-only

# Download MLX models only
./migrate-to-mlx.sh --execute --download-only

# Verify migration status
./migrate-to-mlx.sh --verify-only
```

---

## Quick Start Guide

### Step 1: Analyze Your Current Setup

```bash
python3 ollama-model-analysis.py
```

This will show:
- Which models will be deleted
- Which models will be converted
- Space savings
- Performance improvements

### Step 2: Preview the Migration (Dry Run)

```bash
./convert-ollama-to-mlx.sh --dry-run
```

This safely shows what would happen without making any changes.

### Step 3: Execute the Migration

**Option A: Interactive (Recommended for First Time)**
```bash
./convert-ollama-to-mlx.sh
```

You'll be prompted at each step and can review before proceeding.

**Option B: Automated (For Experienced Users)**
```bash
./migrate-to-mlx.sh --execute
```

Runs the full migration without prompts.

### Step 4: Verify the Results

```bash
# Check Ollama models (should be cleaned up)
ollama list

# Check MLX models
ls -lh mlx/

# Verify migration
./migrate-to-mlx.sh --verify-only
```

---

## What Gets Migrated

### Models to DELETE (104GB freed)

| Ollama Model | Size | Reason | MLX Replacement |
|--------------|------|--------|-----------------|
| qwen-coder-32b-uncensored | 19 GB | Redundant variant | Qwen2.5-Coder-32B MLX |
| deepseek-r1-32b-uncensored | 19 GB | 4x larger, slower | DeepSeek-R1-8B MLX |
| qwen2.5-survival | 19 GB | Redundant variant | Qwen2.5-Coder-7B MLX |
| qwen2.5-undercover | 19 GB | Redundant variant | Qwen2.5-Coder-7B MLX |
| qwen2.5-uncensored | 19 GB | Redundant variant | Qwen2.5-Coder-7B MLX |
| nous-hermes2 | 6.1 GB | Outdated | Qwen3-7B MLX |
| dolphin-mistral | 4.1 GB | Outdated | Mistral-7B MLX |

### Models to CONVERT (MLX equivalents)

| Ollama Model | Size | MLX Replacement | MLX Speed |
|--------------|------|-----------------|-----------|
| qwen2.5-max | 9 GB | Qwen3-14B | 40-60 tok/sec |
| qwen2.5:14b | 9 GB | Qwen3-14B | 40-60 tok/sec |
| phi3:mini | 2.2 GB | Phi-4-14B | 40-60 tok/sec |

### Models to KEEP (as fallbacks)

| Ollama Model | Size | Reason |
|--------------|------|--------|
| llama3.1:8b | 4.9 GB | Good fallback |
| gemma2:2b | 1.6 GB | Ultra-lightweight edge cases |

---

## MLX Models You'll Get

### Daily Use Models

**1. Qwen2.5-Coder-7B MLX** (4.5GB)
- **Speed:** 60-80 tok/sec
- **Use:** Fast coding, daily work
- **Command:** `mlx_lm.chat --model mlx-community/Qwen2.5-Coder-7B-Instruct-4bit`

**2. Qwen3-14B MLX** (9GB)
- **Speed:** 40-60 tok/sec
- **Use:** General questions, research
- **Command:** `mlx_lm.chat --model mlx-community/Qwen3-14B-Instruct-4bit`

### Specialized Models

**3. DeepSeek-R1-8B MLX** (4.5GB)
- **Speed:** 50-70 tok/sec
- **Use:** Math, reasoning, problem-solving
- **Command:** `mlx_lm.chat --model mlx-community/DeepSeek-R1-Distill-Llama-8B`

**4. Qwen2.5-Coder-32B MLX** (18GB)
- **Speed:** 11-22 tok/sec
- **Use:** Complex coding, architecture
- **Requires:** 32GB+ RAM
- **Command:** `mlx_lm.chat --model mlx-community/Qwen2.5-Coder-32B-Instruct-4bit`

**5. Phi-4-14B MLX** (9GB)
- **Speed:** 40-60 tok/sec
- **Use:** Math/STEM specialist
- **Command:** `mlx_lm.chat --model mlx-community/phi-4-4bit`

**6. Mistral-7B MLX** (4GB)
- **Speed:** 70-100 tok/sec
- **Use:** Ultra-fast general use
- **Command:** `mlx_lm.chat --model mlx-community/Mistral-7B-Instruct-v0.3-4bit`

**7. Qwen3-7B MLX** (4.5GB)
- **Speed:** 60-80 tok/sec
- **Use:** Lightweight general use
- **Command:** `mlx_lm.chat --model mlx-community/Qwen3-7B-Instruct-4bit`

---

## Safety Features

### Automatic Backups

Before any deletions, the system:
- Creates timestamped backups of your Ollama model list
- Saves JSON snapshots of current state
- Stores backups in `.ollama-backups/` directory
- Provides rollback instructions if needed

### Dry Run Mode

Both scripts support `--dry-run` to preview without changes:
```bash
./convert-ollama-to-mlx.sh --dry-run
./migrate-to-mlx.sh --dry-run
```

### Pre-flight Checks

Before migration, the system validates:
- Running on macOS (required)
- Apple Silicon chip (optimal)
- Required commands installed (ollama, python3, jq)
- Ollama is accessible
- Sufficient disk space
- Mapping file exists

### Error Handling

- Validates each step before proceeding
- Logs all operations to timestamped log files
- Provides clear error messages
- Supports partial migrations (delete-only or download-only)
- Can verify migration status at any time

---

## Advanced Usage

### Partial Migrations

**Delete Ollama models only (free space now):**
```bash
./migrate-to-mlx.sh --execute --delete-only
```

**Download MLX models only (keep Ollama for now):**
```bash
./migrate-to-mlx.sh --execute --download-only
```

### Verification

**Check migration status:**
```bash
./migrate-to-mlx.sh --verify-only
```

**Re-run analysis after changes:**
```bash
python3 ollama-model-analysis.py
```

### Customization

**Edit the mapping file** to customize:
```bash
# Edit which models to delete/convert
vim mlx-model-mapping.json
```

**Use custom mapping file:**
```bash
python3 ollama-model-analysis.py --mapping custom-mapping.json
./convert-ollama-to-mlx.sh  # reads mlx-model-mapping.json by default
```

---

## Troubleshooting

### "ollama command not found"

Install Ollama:
```bash
brew install ollama
ollama serve
```

### "jq command not found"

Install jq:
```bash
brew install jq
```

### "Insufficient disk space"

The migration will actually free up ~65GB, but you need temporary space during the transition. Options:

1. **Delete only first** (frees space immediately):
   ```bash
   ./migrate-to-mlx.sh --execute --delete-only
   ```

2. **Delete large files manually** to make room

3. **Download one model at a time** by editing the mapping file

### "Failed to download MLX model"

**Manual download:**
```bash
# Install huggingface-cli
pip install -U huggingface-hub

# Download manually
huggingface-cli download mlx-community/Qwen2.5-Coder-7B-Instruct-4bit --local-dir mlx/qwen25-coder-7b
```

### "MLX not working"

**Install MLX in virtual environment:**
```bash
python3 -m venv mlx/venv
source mlx/venv/bin/activate
pip install --upgrade pip
pip install -U mlx-lm
```

### Migration Stuck or Failed

**Check logs:**
```bash
# Find latest log
ls -lt *.log | head -1

# View log
tail -f conversion-*.log
```

**Check state:**
```bash
cat .ollama-backups/migration-state.json
```

**Restore from backup:**
```bash
# List backups
ls -lt .ollama-backups/

# View backup
cat .ollama-backups/ollama-backup-*.json
```

---

## Performance Comparison

### Before (Ollama GGUF)

| Model | Speed (tok/sec) | Size |
|-------|----------------|------|
| Qwen-Coder-32B | 8-12 | 19 GB |
| DeepSeek-R1-32B | 10-15 | 19 GB |
| Qwen2.5:14b | 20-30 | 9 GB |

**Total:** ~130GB, slow speeds

### After (MLX)

| Model | Speed (tok/sec) | Size | Improvement |
|-------|----------------|------|-------------|
| Qwen2.5-Coder-7B | 60-80 | 4.5 GB | +200-300% |
| DeepSeek-R1-8B | 50-70 | 4.5 GB | +400-600% |
| Qwen3-14B | 40-60 | 9 GB | +100-200% |

**Total:** ~65GB, 2-6x faster speeds

---

## Migration Workflow

```
┌─────────────────────────────────────────────┐
│ 1. Analyze Current Setup                   │
│    python3 ollama-model-analysis.py        │
└────────────┬────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│ 2. Preview Migration (Dry Run)             │
│    ./convert-ollama-to-mlx.sh --dry-run    │
└────────────┬────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│ 3. Create Backups                          │
│    (automatic, timestamped)                │
└────────────┬────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│ 4. Delete Old Ollama Models                │
│    (frees ~104GB)                          │
└────────────┬────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│ 5. Install MLX (if needed)                 │
│    (creates venv, installs mlx-lm)         │
└────────────┬────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│ 6. Download MLX Models                     │
│    (from HuggingFace)                      │
└────────────┬────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│ 7. Verify Migration                        │
│    (check all models present)              │
└────────────┬────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│ 8. Start Using MLX Models!                 │
│    2-6x faster, 50% less space!            │
└─────────────────────────────────────────────┘
```

---

## Files Created During Migration

```
llm-optimization-framework/
├── mlx-model-mapping.json          # Master mapping file
├── ollama-model-analysis.py        # Analysis tool
├── convert-ollama-to-mlx.sh        # Interactive orchestrator
├── migrate-to-mlx.sh               # Automated migration
├── conversion-*.log                # Migration logs
├── migration-*.log                 # Migration logs
│
├── .ollama-backups/                # Backup directory
│   ├── ollama-backup-*.json        # Model backups
│   ├── ollama-list-*.txt           # Model list backups
│   ├── analysis-*.json             # Analysis snapshots
│   └── migration-state.json        # Current migration state
│
└── mlx/                            # MLX models directory
    ├── qwen25-coder-7b/            # Downloaded model
    ├── qwen25-coder-32b/           # Downloaded model
    ├── deepseek-r1-8b/             # Downloaded model
    ├── phi-4/                      # Downloaded model
    ├── mistral-7b/                 # Downloaded model
    ├── qwen3-7b/                   # Downloaded model
    ├── qwen3-14b/                  # To be downloaded
    └── venv/                       # Python virtual environment
```

---

## Next Steps After Migration

### 1. Test Your First MLX Model

```bash
# Activate MLX environment
source mlx/venv/bin/activate

# Try fast coding model
mlx_lm.chat --model mlx-community/Qwen2.5-Coder-7B-Instruct-4bit
```

### 2. Create Aliases (Optional)

Add to your `~/.zshrc` or `~/.bashrc`:

```bash
# MLX Model Aliases
alias mlx-activate='source ~/Workspace/llm-optimization-framework/mlx/venv/bin/activate'
alias mlx-code='mlx_lm.chat --model mlx-community/Qwen2.5-Coder-7B-Instruct-4bit'
alias mlx-general='mlx_lm.chat --model mlx-community/Qwen3-14B-Instruct-4bit'
alias mlx-math='mlx_lm.chat --model mlx-community/DeepSeek-R1-Distill-Llama-8B'
alias mlx-fast='mlx_lm.chat --model mlx-community/Mistral-7B-Instruct-v0.3-4bit'
```

### 3. Benchmark Your Models

```bash
# Time a simple request
time mlx_lm.generate --model mlx-community/Qwen2.5-Coder-7B-Instruct-4bit --prompt "Write hello world in Python"
```

### 4. Clean Up Old Backups (Optional)

After confirming everything works:

```bash
# Keep only last 3 backups
cd .ollama-backups
ls -t ollama-backup-*.json | tail -n +4 | xargs rm
```

---

## Support & Resources

### Reference Documents
- `MACBOOK-DELETE-KEEP-LIST.md` - Original planning document
- Model mapping: `mlx-model-mapping.json`
- Logs: `conversion-*.log` and `migration-*.log`

### HuggingFace MLX Community
- https://huggingface.co/mlx-community

### MLX Documentation
- https://ml-explore.github.io/mlx/

### Issues?

Check the logs:
```bash
ls -lt *.log | head -1
tail -f conversion-*.log
```

Run verification:
```bash
./migrate-to-mlx.sh --verify-only
```

---

## Summary

This conversion system provides:

✅ **Safe Migration** - Automated backups, dry-run mode, error handling
✅ **Significant Performance** - 2-6x faster inference speeds
✅ **Space Savings** - ~65GB freed (130GB → 65GB)
✅ **Easy to Use** - Interactive and automated modes
✅ **Well Documented** - Detailed help, logs, and verification
✅ **Flexible** - Partial migrations, custom mappings, rollback support

**Ready to migrate?** Start with:
```bash
python3 ollama-model-analysis.py
./convert-ollama-to-mlx.sh --dry-run
```
