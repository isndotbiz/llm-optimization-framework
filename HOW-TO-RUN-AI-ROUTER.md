# 🤖 How to Run the AI Router

## ⚡ Quick Start

The AI Router is now set up to run in WSL for optimal performance!

### 💻 Option 1: PowerShell Launcher (Recommended)

```powershell
# From D:\models directory
.\LAUNCH-AI-ROUTER.ps1
```

This launcher script:
- ✓ Runs in WSL for maximum performance (within 1% of native Linux)
- ✓ Uses Python virtual environment with all dependencies
- ✓ Supports full ANSI colors and Unicode
- ✓ Provides troubleshooting instructions if needed

### ⚙️ Option 2: Direct WSL Command

```bash
wsl bash -c "cd /mnt/d/models && ~/hf_venv/bin/python3 ai-router.py"
```

### 🐧 Option 3: Inside WSL

```bash
# Open WSL terminal
wsl

# Navigate to models directory
cd /mnt/d/models

# Run the router
~/hf_venv/bin/python3 ai-router.py
```

## 🎯 What the AI Router Does

The AI Router is an intelligent model selection and execution framework that:

1. **Auto-detects use case** from your prompt (coding, reasoning, creative, research, etc.)
2. **Recommends optimal model** based on your use case
3. **Loads model-specific system prompts** automatically
4. **Executes with 2025-optimized parameters** (Flash Attention, KV cache quantization, etc.)
5. **Displays beautiful terminal UI** with colors and formatting

## 📋 Menu Options

When you run the app, you'll see these options:

```
[1] Auto-select model based on prompt
[2] Manually select model
[3] List all available models
[4] View system prompt examples
[5] View optimal parameters guide
[6] Exit
```

###  Option 1: Auto-Select (Recommended)

The smartest way to use the router:

1. Choose option `1`
2. Enter your prompt
3. The router analyzes your prompt and detects the use case:
   - **Coding**: Qwen3 Coder 30B or Qwen2.5 Coder 32B
   - **Reasoning**: Phi-4 14B or Ministral-3 14B
   - **Creative**: Gemma-3 27B
   - **Research**: Qwen2.5 32B

Example:
```
Enter choice [1-6]: 1
Enter your prompt: Write a Python function to parse JSON

🤖 Use Case Detected: CODING
📌 Recommended Model: Qwen3 Coder 30B Q4_K_M
   - Optimized for: Coding, software engineering
   - Speed: ~32 tok/sec
   - VRAM: 18GB
   - Special: --jinja flag, temp >= 0.6

Would you like to use this model? [Y/n]:
```

### Option 2: Manual Selection

Choose your model manually:

1. Choose option `2`
2. Select from list of available models
3. View full configuration before executing

### Option 3: List Models

View all 7 available models with their specs:
- Qwen3 Coder 30B Q4_K_M
- Qwen2.5 Coder 32B Q4_K_M
- Phi-4 Reasoning Plus 14B Q6_K
- Gemma-3 27B IQ2_M
- Ministral-3 14B Q5_K_M
- Qwen2.5 32B Q4_K_M
- Qwen3 14B Q4_K_M

### Option 4: System Prompts

View examples of model-specific system prompts that optimize each model's performance.

### Option 5: Parameters Guide

View the complete guide to all 50+ available configuration parameters from config-templates.json.

## 🚀 Performance Notes

Running in WSL provides:
- **Within 1% of native Linux performance** (2025 research)
- **Full GPU acceleration** via CUDA passthrough
- **Flash Attention support** (+20% speed, 50% memory reduction)
- **CUDA Graphs** (+1.2x speedup)
- **Optimal batch processing** (512 minimum)

## 🔧 Troubleshooting

### Missing Dependencies

If you see errors about missing packages:

```powershell
.\LAUNCH-AI-ROUTER.ps1 -InstallDependencies
```

This will install:
- colorama (terminal colors)
- termcolor (text formatting)

### WSL Not Available

If WSL is not installed:

```powershell
wsl --install
```

Then restart your computer.

### Python Not Found

Verify Python3 is installed in WSL:

```bash
wsl bash -c "python3 --version"
```

If not installed:

```bash
wsl bash -c "sudo apt update && sudo apt install python3 python3-pip python3-venv"
```

## 📚 Related Documentation

- **BOT-PROJECT-QUICK-START.md** - Create custom bots and projects
- **config-templates.json** - Complete parameter reference (50+ params)
- **COMPREHENSIVE-EVALUATION-FRAMEWORK-PROMPT.md** - Evaluation framework
- **MACBOOK-M4-OPTIMIZATION-GUIDE.md** - M4 Mac optimization
- **AI-ROUTER-QUICKSTART.md** - Original quick start guide

## 🔬 Advanced Usage

### Running with Custom Config

The router uses model-specific configurations from the ModelDatabase class in ai-router.py. To customize:

1. Edit `ai-router.py`
2. Modify the RTX3090_MODELS or M4_MODELS dictionaries
3. Save and relaunch

### Opening Models to Other Agents

To expose models via llama-server for multi-agent access:

```bash
wsl bash -c "~/llama.cpp/build/bin/llama-server \
  -m /mnt/d/models/organized/model.gguf \
  -ngl 999 \
  -fa 1 \
  --ctx-size 32768 \
  --parallel 4 \
  --cont-batching \
  --cache-type-k q8_0 \
  --cache-type-v q8_0 \
  --port 8080"
```

Then other agents can connect to `http://localhost:8080`

## ✅ Next Steps

1. **Try the auto-select feature** - Let the router choose the best model
2. **Create custom projects** - See BOT-PROJECT-QUICK-START.md
3. **Run evaluations** - Test all models with the evaluation framework
4. **Push to GitHub** - See GITHUB-SETUP-GUIDE.md

---

**Enjoy your optimized LLM environment!**
