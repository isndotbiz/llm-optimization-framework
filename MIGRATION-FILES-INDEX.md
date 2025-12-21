# Ollama→MLX Migration - File Index

This directory contains comprehensive documentation and tools for migrating from Ollama to MLX on Apple Silicon Macs.

## 📋 Quick Reference

| File | Purpose | Size | When to Use |
|------|---------|------|-------------|
| **MIGRATION-QUICKSTART.md** | Quick start guide | 8KB | Start here - 3-step migration |
| **OLLAMA-TO-MLX-MIGRATION-GUIDE.md** | Complete migration guide | 21KB | Full documentation & troubleshooting |
| **verify-mlx-health.sh** | Health check script | 26KB | Verify MLX installation & setup |
| **test-mlx-models.py** | Benchmark script | 20KB | Test model performance |

## 🚀 Getting Started

### 1. Read the Quick Start (5 minutes)
```bash
open MIGRATION-QUICKSTART.md
# or
cat MIGRATION-QUICKSTART.md
```

**What you'll learn:**
- 3-step migration process
- Quick model selection guide
- Performance expectations
- Common troubleshooting

### 2. Run Health Check (2 minutes)
```bash
./verify-mlx-health.sh
```

**What it does:**
- ✓ Checks system requirements (macOS, Apple Silicon)
- ✓ Verifies Python & MLX installation
- ✓ Tests Metal GPU support
- ✓ Lists available models
- ✓ Validates memory & disk space
- ✓ Provides readiness report

**Expected output:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                   MLX HEALTH CHECK v1.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Test Results:
  Passed:  25
  Warnings: 2
  Failed:  0

Overall Status:
  ✓ GOOD - MLX is ready to use
```

### 3. Benchmark Performance (5 minutes)
```bash
source ~/workspace/venv-mlx/bin/activate
python3 test-mlx-models.py
```

**What it does:**
- Benchmarks all installed models
- Measures load time, speed, memory
- Compares with Ollama baselines
- Identifies best performers
- Saves detailed results

**Expected output:**
```
Best Performers:
  🚀 Fastest Load: Mistral-7B (0.3s)
  🚀 Fastest Generation: Mistral-7B (85.7 tok/sec)
  🚀 Lowest Memory: Mistral-7B (2.6GB)

Average Improvement vs Ollama: ↑ 125%
```

## 📚 Detailed Documentation

### OLLAMA-TO-MLX-MIGRATION-GUIDE.md

**Comprehensive 21KB guide covering:**

1. **Executive Summary**
   - Speed improvement metrics (3-4x faster)
   - Real-world impact analysis
   - Technical architecture comparison

2. **Migration Steps**
   - System prerequisites
   - Installation instructions
   - Model downloads
   - Workflow updates
   - Ollama removal (optional)

3. **Model Replacement Chart**
   - Direct Ollama→MLX mappings
   - Model selection guide
   - Use case recommendations

4. **Performance Benchmarks**
   - Detailed speed comparisons
   - Memory usage analysis
   - Load time metrics
   - Token/sec measurements

5. **Storage Space Analysis**
   - Before/after disk usage
   - Space savings calculation (35GB+)
   - Cleanup instructions

6. **Troubleshooting Guide**
   - Installation issues
   - Model download problems
   - Runtime errors
   - Performance optimization
   - Common fixes

7. **FAQ & Resources**
   - Common questions
   - Best practices
   - External links

## 🛠 Scripts & Tools

### verify-mlx-health.sh

**Comprehensive health check script (777 lines)**

**Tests performed:**
1. System Requirements
   - macOS version (≥12.0)
   - Apple Silicon detection
   - RAM availability (16GB+)
   - Disk space (50GB+)

2. Python Environment
   - Python version (≥3.8)
   - Virtual environment
   - pip availability

3. MLX Installation
   - MLX Core library
   - MLX LM package
   - Dependencies (numpy, transformers)

4. Metal GPU Support
   - GPU detection
   - Memory tracking
   - Computation test

5. Available Models
   - Cached models scan
   - Size reporting
   - Recommended models status

6. Model Loading & Inference
   - Load time test
   - Generation test
   - Speed validation

7. Memory Usage
   - System memory check
   - Memory pressure analysis
   - Free memory calculation

**Exit codes:**
- `0` = All tests passed
- `1` = One or more tests failed

**Usage:**
```bash
# Basic run
./verify-mlx-health.sh

# Save output to file
./verify-mlx-health.sh > health-report.txt 2>&1

# Check exit code
./verify-mlx-health.sh && echo "Ready!" || echo "Needs fixes"
```

### test-mlx-models.py

**Performance benchmarking script (589 lines)**

**Features:**
- Automatic model discovery
- Load time measurement
- First token latency
- Generation speed (tok/sec)
- Memory usage tracking
- Ollama baseline comparison
- Performance statistics
- Results export (JSON)

**Test prompts:**
- Simple: "Write a Python hello world"
- Medium: "Sort a list of dictionaries"
- Complex: "Binary search tree implementation"
- Reasoning: "Quicksort complexity analysis"

**Ollama baselines included:**
- qwen2.5-coder:7b
- qwen2.5-coder:32b
- deepseek-r1:8b
- mistral:7b
- phi:14b

**Usage:**
```bash
# Activate MLX environment
source ~/workspace/venv-mlx/bin/activate

# Run all benchmarks
python3 test-mlx-models.py

# Results saved to:
# benchmark-results/mlx_benchmark_YYYYMMDD_HHMMSS.json
```

**Output includes:**
- Per-model benchmarks
- Performance statistics
- Ollama comparisons
- Best performers list
- Recommendations
- JSON results file

## 📊 Performance Summary

### What You Can Expect

| Metric | Ollama | MLX | Improvement |
|--------|--------|-----|-------------|
| **Load Time** | 2-5s | 0.3-0.9s | **5-9x faster** |
| **First Token** | 1.5-4s | 0.2-0.6s | **5-7x faster** |
| **Generation** | 8-42 tok/sec | 15-100 tok/sec | **2-3x faster** |
| **Memory** | 5-22GB | 2-12GB | **40-50% less** |

### Real-World Impact

- **Code review (500 tokens):** 2-3 min → 30 sec (**75% faster**)
- **Model loading:** 5-10 sec → <1 sec (**90% faster**)
- **Complex reasoning (2000 tokens):** 8-10 min → 2-3 min (**70% faster**)
- **Daily coding (50 queries):** 2-3 hours → 45-60 min (**60% time saved**)
- **Disk space:** 86GB → 51GB (**35GB freed**)

## 🎯 Model Recommendations

### By Use Case

```
CODING (Fast & Daily)
→ Qwen2.5-Coder-7B-Instruct-4bit
  • 60-80 tok/sec • 4GB • Best for iterations

CODING (Best Quality)
→ Qwen2.5-Coder-32B-Instruct-4bit
  • 15-22 tok/sec • 17GB • Architecture & complex tasks

REASONING & MATH
→ DeepSeek-R1-Distill-Llama-8B
  • 50-70 tok/sec • 15GB • Problem-solving

STEM & TECHNICAL
→ phi-4-4bit
  • 40-60 tok/sec • 7.7GB • Math expert

ULTRA-FAST GENERAL
→ Mistral-7B-Instruct-v0.3-4bit
  • 70-100 tok/sec • 3.8GB • Speed champion

UNCENSORED / CREATIVE
→ Dolphin3.0-Llama3.1-8B
  • 60-80 tok/sec • 4.5GB • No restrictions

BALANCED ALL-ROUNDER
→ Qwen3-14B-Instruct-4bit
  • 40-60 tok/sec • 4GB • Research & general
```

## 🔄 Migration Workflow

### Standard Migration Path

```
1. PREPARATION (Day 1)
   ├── Read MIGRATION-QUICKSTART.md
   ├── Review OLLAMA-TO-MLX-MIGRATION-GUIDE.md
   └── Backup current Ollama setup

2. INSTALLATION (Day 1)
   ├── Install MLX (python3 -m venv, pip install mlx-lm)
   ├── Download essential models (Qwen2.5-Coder-7B, Mistral-7B)
   └── Run verify-mlx-health.sh

3. VALIDATION (Day 1-2)
   ├── Run test-mlx-models.py
   ├── Test with ai-router-mlx.py
   └── Verify speed improvements

4. MIGRATION (Week 1-2)
   ├── Update daily workflows
   ├── Test edge cases
   └── Monitor performance

5. CLEANUP (Week 2+)
   ├── Confirm MLX works for all use cases
   ├── Remove Ollama (optional)
   └── Free up 35GB+ disk space
```

## 🆘 Quick Troubleshooting

### Common Issues

**1. "ModuleNotFoundError: No module named 'mlx'"**
```bash
source ~/workspace/venv-mlx/bin/activate
pip install mlx-lm
```

**2. "Metal device not found"**
```bash
# Verify Apple Silicon
uname -m  # Should show: arm64

# Reinstall MLX
pip install --force-reinstall mlx mlx-lm
```

**3. "Model download is slow"**
```bash
# Use faster mirror (optional)
export HF_ENDPOINT=https://hf-mirror.com
```

**4. "Disk space error"**
```bash
# Check space
df -h ~

# Change cache location
export HF_HOME=~/external-drive/.cache/huggingface
```

**5. "Inference is slower than expected"**
```bash
# Close background apps
# Check thermal throttling
# Use 4-bit models (not FP16)
```

## 📞 Support Resources

### Documentation
- **MLX GitHub:** https://github.com/ml-explore/mlx
- **MLX Docs:** https://ml-explore.github.io/mlx/
- **MLX Examples:** https://github.com/ml-explore/mlx-examples

### Models
- **MLX Community:** https://huggingface.co/mlx-community
- **Model Browser:** https://huggingface.co/models?library=mlx

### Local Files
- **Migration Guide:** OLLAMA-TO-MLX-MIGRATION-GUIDE.md
- **Quick Start:** MIGRATION-QUICKSTART.md
- **Health Check:** ./verify-mlx-health.sh
- **Benchmark:** ./test-mlx-models.py

## 📝 Version History

### v1.0 (2025-12-19)
- Initial release
- Complete migration documentation
- Health check script (777 lines)
- Benchmark script (589 lines)
- Quick start guide
- Comprehensive troubleshooting

## 🎉 Success Criteria

You're ready to migrate when:

- ✓ `verify-mlx-health.sh` shows all tests passed
- ✓ `test-mlx-models.py` shows 2-3x speed improvement
- ✓ At least one model is downloaded and tested
- ✓ `mlx_lm.chat` works smoothly
- ✓ `ai-router-mlx.py` launches without errors
- ✓ Speed and memory usage meet expectations

## 💡 Pro Tips

1. **Start with Qwen2.5-Coder-7B** - fastest and most versatile
2. **Use Mistral-7B on battery** - ultra-fast with low power
3. **Save Qwen2.5-Coder-32B for complex tasks** - best quality
4. **Run health check after system updates** - ensure compatibility
5. **Benchmark periodically** - track performance over time

---

**Created:** 2025-12-19
**Version:** 1.0
**Tested On:** M4 Pro MacBook, 36GB RAM, macOS 15.1
