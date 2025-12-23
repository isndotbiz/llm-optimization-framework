# CLI UX Examples - Before & After Comparisons

---

## Example 1: Running a Model

### BEFORE (Current)
```
$ python ai-router.py
[Interactive banner and menu]

What would you like to do?
[1] Auto-select model based on prompt
[2] Manually select model
[3] List all available models
[4] View system prompt examples
[5] View optimal parameters guide
[6] View documentation guides
[7] Exit

Enter choice [1-7]: 2

╔══════════════════════════════════════════════════════════════╗
║  AVAILABLE MODELS║
╚══════════════════════════════════════════════════════════════╝

[1] qwen3-coder-30b
    Qwen3 Coder 30B Q4_K_M
    Use case: Advanced coding, code review, architecture design
    18GB | 25-35 tok/sec

[2] phi4-14b
    Phi-4 Reasoning Plus 14B Q6_K
    Use case: Math, reasoning, STEM, logical analysis
    12GB | 35-55 tok/sec

[... more models ...]

Select model number (or 'back'): 1

[Model info displayed]

Run this model? [Y/n]: y

Enter your prompt: write a function that sorts a list

[Model executes]
```

### AFTER (Proposed)
```
$ ai-router run --model qwen3-coder-30b --prompt "write a function that sorts"

Launching Qwen3 Coder 30B Q4_K_M...

[Model executes immediately]
```

**Benefits:**
- Instant execution: 0 seconds vs. 7+ menu clicks
- Scriptable: Can use in bash scripts, CI/CD
- One-liner automation
- Clearer intent from command

---

## Example 2: Finding a Model

### BEFORE (Current)
```
$ python ai-router.py
[Interactive menu]
> Enter choice [1-7]: 3

[Long list of all models appears]

User must scroll through and manually evaluate each one
```

### AFTER (Proposed)
```
$ ai-router models search coding

╔══════════════════════════════════════════════════════════════╗
║  MODELS MATCHING: "coding"                                   ║
╚══════════════════════════════════════════════════════════════╝

[1] qwen3-coder-30b ⭐⭐⭐⭐⭐
    Best for coding, code review, architecture
    18GB | 25-35 tok/sec | Framework: llama.cpp

[2] qwen25-coder-14b-mlx
    Great for coding on macOS
    8GB | 50-75 tok/sec | Framework: mlx

[3] phi4-14b
    Good for math/logic in coding
    12GB | 35-55 tok/sec | Framework: llama.cpp

Run: ai-router models info qwen3-coder-30b (for details)
Run: ai-router run --model qwen3-coder-30b --prompt "..." (to use)
```

**Alternative: JSON output for parsing**
```
$ ai-router models search coding --json

[
  {
    "id": "qwen3-coder-30b",
    "name": "Qwen3 Coder 30B",
    "use_case": "Advanced coding",
    "size": "18GB",
    "speed": "25-35 tok/sec",
    "framework": "llama.cpp"
  },
  ...
]
```

**Benefits:**
- Instant search results
- See recommendations immediately
- JSON output for programmatic use
- Clear next steps

---

## Example 3: Checking Configuration

### BEFORE (Current)
No way to see active configuration from CLI. Must:
1. Know config location exists: `configs/[machine-id]/`
2. Manually find and open the JSON file
3. Guess which settings matter

### AFTER (Proposed)
```
$ ai-router config show

╔══════════════════════════════════════════════════════════════╗
║  ACTIVE CONFIGURATION                                        ║
╚══════════════════════════════════════════════════════════════╝

Machine:
  ID:       ryzen-3900x-3090
  Name:     Ryzen 3900X + RTX 3090
  Platform: Linux (WSL)

Primary Model:
  Model ID:          qwen3-coder-30b
  Path:              /mnt/d/models/organized/qwen3-coder-30b.gguf
  Framework:         llama.cpp
  Size:              18GB

Performance Parameters:
  Temperature:       0.7
  Top P:             0.8
  Top K:             20
  Context:           32768 tokens

GPU Settings:
  Framework:         llama.cpp
  Device:            CUDA
  GPU Memory Util:   0.95

Config Location: configs/ryzen-3900x-3090/ai-router-config.json

Edit configuration: ai-router config edit
```

**Benefits:**
- See active settings without opening files
- Understand what's being used
- Know where config is stored
- Easy to find what to modify

---

## Example 4: Machine Detection

### BEFORE (Current)
```
$ python ai-router.py
[App starts, silently detects machine, loads config]
[User runs model, crash happens]
[User confused about what went wrong]
```

### AFTER (Proposed)
```
$ ai-router machine detect

╔══════════════════════════════════════════════════════════════╗
║  MACHINE DETECTION                                           ║
╚══════════════════════════════════════════════════════════════╝

DETECTION PROCESS:
[1/5] Checking OS platform...      ✓ Linux (Ubuntu 22.04)
[2/5] Detecting CPU...             ✓ AMD Ryzen 9 3900X (12-core)
[3/5] Detecting GPU...             ✓ NVIDIA RTX 3090 (24GB VRAM)
[4/5] Checking memory...           ✓ 64GB DDR4 available
[5/5] Checking WSL...              ✓ WSL 2.0.9 enabled

RESULT:
  Machine ID:      ryzen-3900x-3090
  Confidence:      98% (very confident)
  Config:          configs/ryzen-3900x-3090/ai-router-config.json

HARDWARE SPECS:
  CPU:             AMD Ryzen 9 3900X (12-core / 24-thread @ 3.8-4.6 GHz)
  RAM:             64GB DDR4
  GPU:             NVIDIA RTX 3090 (24GB GDDR6X)
  WSL:             2.0.9

OPTIMIZATION:
  ✓ GPU offload:        Enabled (perfect for NVIDIA)
  ✓ Thread count:       24 (optimal for Ryzen)
  ✓ Memory allocation:  Up to 48GB available
  ✓ Framework:          llama.cpp (WSL optimized)

If detection is incorrect:
  $ echo "m4-macbook-pro" > .machine-id
  $ ai-router machine detect (to verify)

Next: ai-router validate full
```

**Benefits:**
- See what was detected and why
- Confidence metric shows reliability
- Clear override instructions
- Prevents silent failures

---

## Example 5: Parameter Validation

### BEFORE (Current)
```
$ python ai-router.py
[User goes through menu, sets temperature to 2.5]
[User starts chat, model crashes with cryptic error]
[User investigates, discovers temperature was out of range]
[Wasted 5+ minutes]
```

### AFTER (Proposed)
```
$ ai-router validate parameters --model qwen3-coder-30b --temp 2.5

ERROR: Temperature parameter out of range
Context: Entered 2.5 but valid range is 0.0-2.0

Suggestions:
  • Valid range is 0.0 (very focused) to 2.0 (very creative)
  • For coding: use 0.3-0.7
  • For creative writing: use 0.8-1.2
  • For reasoning: use 0.2-0.5

Fix: ai-router run --model qwen3-coder-30b --temperature 0.7 --prompt "..."

Or use config: ai-router config set temperature 0.7
```

**Or, test parameters before use:**
```
$ ai-router validate parameters --model qwen3-coder-30b \
  --temp 0.7 --top-p 0.8 --top-k 20

✓ All parameters valid

Model:           Qwen3 Coder 30B
Temperature:     0.7 ✓ (good for coding)
Top P:           0.8 ✓
Top K:           20 ✓
Max tokens:      2048

Ready to use: ai-router run --model qwen3-coder-30b --prompt "..."
```

**Benefits:**
- Validate before running (fail fast)
- Get suggestions for fixing
- Avoid wasted time on errors
- Learn what parameters mean

---

## Example 6: Error Messages

### BEFORE (Current - Lines 1384-1387)
```
Unknown argument. Use --help for usage.
```

### AFTER (Proposed)
```
ERROR: Unknown command 'invalid-cmd'

Valid commands:
  run              Execute a model
  models           Model discovery
  config           Configuration
  machine          Hardware detection
  validate         System validation
  interactive      Interactive mode

Did you mean one of these?
  ai-router run --help
  ai-router models list
  ai-router config show

Full help: ai-router --help
```

---

## Example 7: WSL Not Available Error

### BEFORE (Current)
```
[Silent failure or cryptic error about WSL]
User is confused and looks up documentation
```

### AFTER (Proposed)
```
ERROR: WSL (Windows Subsystem for Linux) Required
Context: Trying to run llama.cpp model on Windows

WSL is required to run llama.cpp models from Windows Command Prompt.

Solutions:
  1. Enable WSL:
     • Run in PowerShell (admin): wsl --install
     • Restart your computer
     • Run again: python ai-router.py

  2. Use alternative framework:
     • On macOS: ai-router config set framework mlx
     • Any platform: ai-router config set framework ollama

  3. Run from WSL directly:
     • Start WSL: wsl
     • Run: cd /mnt/d/models && python ai-router-enhanced.py

Learn more: https://learn.microsoft.com/en-us/windows/wsl/install

Next steps:
  1. Install WSL
  2. Restart computer
  3. Try again: python ai-router.py
```

---

## Example 8: Setup Wizard Flow

### BEFORE (Current)
User manually creates configs and edits JSON files

### AFTER (Proposed)
```
$ ai-router config setup

╔══════════════════════════════════════════════════════════════╗
║  AI ROUTER CONFIGURATION SETUP                               ║
╚══════════════════════════════════════════════════════════════╝

STEP 1: MACHINE DETECTION
────────────────────────────
✓ Detected: m4-macbook-pro (Darwin, ARM64)
✓ Confidence: 95%
✓ Hardware: Apple M4 Pro, 36GB RAM

Is this correct? [Y/n]: y

STEP 2: FRAMEWORK SELECTION
────────────────────────────
What inference framework would you like to use?

[1] llama.cpp (GPU-accelerated, all platforms)
    Best for: NVIDIA GPUs (RTX, GTX), cross-platform
    Speed: 25-50 tok/sec on RTX 3090
    Pros: Excellent quality, fast, flexible
    Cons: Complex setup, requires WSL on Windows

[2] mlx (Apple Silicon optimized, macOS only)
    Best for: MacBook Pro/Air M1/M2/M3/M4
    Speed: 50-100 tok/sec on M4 Pro
    Pros: Native, very fast, simple
    Cons: macOS only

[3] ollama (Easy setup, slower)
    Best for: Beginners, quick testing
    Speed: 10-20 tok/sec
    Pros: Very easy setup, works everywhere
    Cons: Slower, fewer models

Select [1-3]: 2

STEP 3: PRIMARY MODEL SELECTION
───────────────────────────────────
Which model would you like as your primary?

[1] qwen25-14b (Fast general purpose)
    ⭐ Best for: General chat, quick responses
    Speed: 50-70 tok/sec | Size: 8GB | Context: 32K

[2] qwen25-coder-14b ⭐
    ⭐ Best for: Coding tasks
    Speed: 50-75 tok/sec | Size: 9GB | Context: 32K

[3] phi4-14b
    ⭐ Best for: Math and reasoning
    Speed: 60-75 tok/sec | Size: 12GB | Context: 16K

[4] gemma3-9b
    ⭐ Best for: Speed and efficiency
    Speed: 85-110 tok/sec | Size: 7GB | Context: 128K

Select [1-4]: 2

STEP 4: FALLBACK MODEL (optional)
──────────────────────────────────
If primary model fails, which should we use?

[1] qwen25-14b ✓
[2] gemma3-9b
[3] None (fail instead of fallback)

Select [1-3]: 1

STEP 5: PERFORMANCE TUNING
──────────────────────────────
Adjust parameters (press Enter for defaults):

Temperature [0.2-2.0] (default: 0.7 for coding): 0.7
  ✓ Good for coding (focused, less creativity)

Top P [0.0-1.0] (default: 0.9): 0.9
  ✓ Standard (good diversity)

Top K [0-200] (default: 40): 40
  ✓ Standard

Max tokens [1-32768] (default: 2048): 2048
  ✓ Good balance

STEP 6: ADVANCED SETTINGS (optional)
──────────────────────────────────────
Enable GPU acceleration? [Y/n]: y
  ✓ Recommended for your hardware

GPU memory limit [GB] (auto for max): auto
  ✓ Will use up to 24GB (RTX 3090 capacity)

STEP 7: SUMMARY
───────────────
Machine:         m4-macbook-pro
Framework:       mlx
Primary model:   qwen25-coder-14b
Fallback model:  qwen25-14b
Temperature:     0.7
Max tokens:      2048
GPU accel:       enabled
Memory limit:    24GB

Save configuration? [Y/n]: y

✓ Configuration saved successfully!

Next steps:
  1. Validate setup:   ai-router validate full
  2. Test model:       ai-router models test --model qwen25-coder-14b
  3. Run model:        ai-router run --model qwen25-coder-14b --prompt "hello"

Your config is at: configs/m4-macbook-pro/ai-router-config.json
```

---

## Example 9: Startup Validation

### BEFORE (Current)
```
$ python ai-router.py
[App starts]
[User selects model]
[User enters prompt]
[Waits for model to load]
[Crashes: "Model file not found"]
[User investigates for 10+ minutes]
```

### AFTER (Proposed)
```
$ python ai-router.py

╔══════════════════════════════════════════════════════════════╗
║  AI ROUTER v1.0 - STARTUP VALIDATION                         ║
╚══════════════════════════════════════════════════════════════╝

CHECKING SYSTEM...
[1/7] Python version........................ ✓ 3.11.5
[2/7] Machine detection..................... ✓ m4-macbook-pro
[3/7] Configuration file.................... ✓ Found
[4/7] Model directory....................... ✓ /Users/name/models/
[5/7] Framework (mlx)........................ ✓ Installed
[6/7] Primary model file.................... ✓ Found (qwen25-coder-14b)
[7/7] System resources...................... ⚠ Low: 2GB free (8GB+ recommended)

RESULTS:
✓ System ready (2/1 issues)

⚠ WARNINGS (non-blocking):
  • Available memory is low (2GB)
    Recommendation: Close other apps before running models
    Or set max_tokens to 1024 to reduce memory usage

Ready to start!

Main menu:
[1] Auto-select model based on prompt
[2] Manually select model
[3] List all available models
[4] Exit

Enter choice [1-4]:
```

---

## Example 10: Help Text Comparison

### BEFORE (Current - Lines 1356-1381)
```
$ python ai-router.py --help

Usage:

  python ai-router.py
    Launch interactive mode

  python ai-router.py --list
    List all available models

  python ai-router.py --help
    Show this help message
```

### AFTER (Proposed)
```
$ ai-router --help

AI ROUTER v1.0 - Intelligent Model Selection & Execution CLI

USAGE:
  ai-router <command> [options]
  ai-router [no args]     (launches interactive mode)

COMMANDS:
  run         Execute a model with specified parameters
  models      Discover, list, search, and test models
  config      Manage configuration and settings
  machine     Hardware detection and management
  project     Project and bot management
  validate    System validation and diagnostics
  interactive Legacy interactive mode (same as no args)

QUICK START:
  ai-router run --model qwen3-coder-30b --prompt "hello world"
  ai-router models search coding
  ai-router config show
  ai-router validate full

EXAMPLES:
  Quick test:         ai-router run --model phi4-14b --prompt "2+2="
  With parameters:    ai-router run --model qwen3 --prompt "hello" --temp 0.5
  Search models:      ai-router models search reasoning
  See model details:  ai-router models info --model phi4-14b
  Check config:       ai-router config show
  Detect hardware:    ai-router machine detect
  Full validation:    ai-router validate full
  Interactive mode:   ai-router (or ai-router interactive)

HELP:
  ai-router <command> --help     Show help for specific command
  ai-router run --help           Show all options for 'run' command
  ai-router models --help        Show all model commands

DOCUMENTATION:
  https://docs.ai-router.local/cli
  https://github.com/yourusername/ai-router/wiki

TROUBLESHOOTING:
  WSL not available:   https://learn.microsoft.com/windows/wsl/install
  GPU not detected:    ai-router validate full
  Model not found:     ai-router models list
```

```
$ ai-router run --help

Execute a model with specified parameters

USAGE:
  ai-router run [OPTIONS]

REQUIRED OPTIONS:
  --model TEXT       Model ID (required)
                     Examples: qwen3-coder-30b, phi4-14b, gemma3-9b
                     List all: ai-router models list

  --prompt TEXT      Prompt text (required)
                     Example: "write a function that sorts a list"

OPTIONAL PARAMETERS:
  --temperature FLOAT    Creativity level (0.0-2.0)
                         Default: 0.7
                         • 0.2-0.4: Technical, focused (code, math)
                         • 0.5-0.9: Balanced (general chat)
                         • 0.8-1.2: Creative (stories, brainstorming)

  --top-p FLOAT         Diversity (0.0-1.0)
                        Default: 0.9
                        Higher = more diverse, Lower = more focused

  --top-k INT           Top tokens (0-200)
                        Default: 40
                        Typically 40-50 for most tasks

  --max-tokens INT      Maximum output length (1-32768)
                        Default: 2048
                        • 512: Quick responses
                        • 2048: Normal responses
                        • 4096+: Long-form content

  --system-prompt TEXT  Custom system prompt (optional)
                        Overrides model's default

OUTPUT OPTIONS:
  --json               Output as JSON (for parsing/scripting)
  --quiet              Suppress non-essential output
  --test               Dry-run (validate without executing)

EXAMPLES:
  Basic usage:
    ai-router run --model qwen3-coder-30b --prompt "write hello world"

  Coding task (focused):
    ai-router run --model qwen3-coder-30b \
      --prompt "write a function" \
      --temperature 0.3

  Creative task (exploratory):
    ai-router run --model gemma3-27b \
      --prompt "write a story" \
      --temperature 1.0 \
      --max-tokens 4096

  Math problem (precise):
    ai-router run --model phi4-14b \
      --prompt "solve this equation" \
      --temperature 0.1 \
      --top-p 0.9

  With custom system prompt:
    ai-router run --model qwen3 \
      --prompt "hello" \
      --system-prompt "You are a helpful assistant"

  JSON output (for scripting):
    ai-router run --model qwen3 --prompt "hi" --json

RELATED COMMANDS:
  ai-router models list          List available models
  ai-router models info          Get model details
  ai-router config show          Show current settings
  ai-router validate parameters  Check parameters before use

NOTES:
  • Never use temperature 0 with Qwen models (causes loops)
  • Temperature 0 works best with explicit instructions
  • Phi-4 requires --jinja flag (automatic with new CLI)
  • Models run slower on first execution (loading time)

For more help: ai-router run --help
```

---

## Key Improvements Summary

| Feature | Before | After | Impact |
|---------|--------|-------|--------|
| **Running Model** | 7 menu clicks | 1 command | High - enables scripting |
| **Finding Model** | Interactive menu | `ai-router models search` | High - discovery |
| **Checking Config** | Manual file open | `ai-router config show` | Medium - clarity |
| **Machine Detection** | Silent | Verbose with feedback | High - prevents errors |
| **Error Messages** | Generic | Contextual with suggestions | High - user friendliness |
| **Parameter Validation** | Runtime error | Pre-flight check | Medium - fail fast |
| **Help Text** | 3 lines | Detailed with examples | High - discoverability |
| **Onboarding** | Manual setup | `ai-router config setup` | High - new user experience |

