# CLI UX & Configuration Discovery Analysis
## Agent 6 Deep Dive - D:\models

**Date:** 2025-12-22
**Status:** Comprehensive Analysis Complete
**Scope:** ai-router.py, ai-router-enhanced.py, configuration discovery, CLI/UX patterns

---

## EXECUTIVE SUMMARY

The AI Router CLI has a **strong foundation but significant UX gaps** preventing users from discovering and using features effectively. The CLI is **purely interactive menu-driven** with minimal command-line argument support, making it difficult for:
- Scripting and automation
- CI/CD integration
- Quick command execution (no "fire and forget" mode)
- API/programmatic access
- Discovery of advanced features without exploring menus

**Current state:** 80% interactive, 20% CLI - needs inverse ratio for power users.

---

## SECTION 1: CURRENT STATE ANALYSIS

### 1.1 CLI Interface Architecture

**File:** `D:\models\ai-router.py` (Lines 1346-1408)

```python
def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--list":
            # List models
        elif sys.argv[1] == "--help":
            # Show help
        else:
            print("Unknown argument")
    else:
        # Interactive mode
        router.interactive_mode()
```

**Current Supported Arguments:**
- `--help` - Show basic usage (minimal)
- `--list` - List available models
- (nothing) - Enter interactive mode (default)

**Problem:** Only 3 effective commands. No way to:
- Run a specific model non-interactively
- Query model details
- Validate configuration
- Test system compatibility
- Discover available features

### 1.2 Command Structure Issues

| Feature | Current | Problem |
|---------|---------|---------|
| **Help System** | Basic text in --help | No subcommand help, no examples |
| **Model Selection** | Interactive menu | Must navigate 7 menu items to select model |
| **Batch Mode** | None | Cannot script model execution |
| **Configuration** | JSON in configs/ | Path not obvious, validation missing |
| **Error Messages** | Generic | "Invalid choice. Please try again" (no guidance) |
| **Model Discovery** | Menu-based | 8+ models but no CLI search/filter |
| **Parameter Tuning** | Interactive only | Cannot test parameters without full chat |

### 1.3 Configuration Discovery Problems

**Current Config Locations:**
```
D:\models\
├── configs/
│   ├── m4-macbook-pro/ai-router-config.json
│   ├── ryzen-3900x-3090/ai-router-config.json
│   └── xeon-4060ti/ai-router-config.json
├── projects/
│   ├── [PROJECT-NAME]/config.json (auto-created)
│   └── [BOT]/config.json
├── mlx/[MODEL]/config.json (model configs - HF format)
└── .ai-router-preferences.json (user preferences)
```

**Discovery Issues:**
1. Users don't know `configs/[machine-id]/` exists
2. Machine auto-detection hides manual override options
3. No guidance on which config to edit
4. Multiple config sources (3 levels) create confusion
5. `.ai-router-preferences.json` is undocumented
6. No config validation before runtime

**Current Auto-Detection (Lines 18-46):**
```python
def detect_machine():
    # Checks .machine-id file first (manual override)
    # Falls back to platform/CPU detection
    # Defaults to "ryzen-3900x-3090"

# Issues:
# - Silent fallback masks misdetection
# - Users don't know override mechanism exists
# - No feedback if detection fails
```

### 1.4 Help Text Quality

**Current Help (Lines 1356-1381):**
```
Usage:

  python ai-router.py
    Launch interactive mode

  python ai-router.py --list
    List all available models

  python ai-router.py --help
    Show this help message
```

**Problems:**
- No examples of actual usage
- No mention of available models
- No subcommand structure
- No hints about advanced features
- Doesn't mention configuration files
- No troubleshooting guidance

### 1.5 Error Messages - Reactive Not Helpful

**Examples Found:**
- Line 671: `"Invalid choice. Please try again."` - No hint what choices are valid
- Line 741: `"Invalid model number."` - No range shown
- Line 750: `"Invalid input."` - Doesn't say what input is expected
- Line 1385: `"Unknown argument. Use --help for usage."` - Barely helpful

**None include:**
- What was entered vs. expected
- Valid options list
- Suggested next steps
- Configuration hints
- Links to documentation

---

## SECTION 2: HIGH-IMPACT UX ISSUES (Ranked by User Pain)

### Issue #1: No Non-Interactive Model Execution (CRITICAL)
**Severity:** Critical | **Users Affected:** Scripts, Automation, Integration
**Current:** Must use interactive menu (7 clicks minimum)
**Impact:** Cannot integrate with external tools, shell scripts, CI/CD

**Example of Current Flow:**
```bash
$ python ai-router.py
[Interactive menu opens]
> Enter choice [1-7]: 2        # Manual select model
[List models menu]
> Select model number (or 'back'): 3
[Model info shown]
> Run this model? [Y/n]: y
[Chat starts]
```

**What Users Need:**
```bash
$ ai-router run --model qwen3-coder-30b --prompt "write a function"
# Executes immediately, no menu
```

### Issue #2: No Command-Line Model Discovery (HIGH)
**Severity:** High | **Users Affected:** New users, script writers
**Current:** Must enter interactive mode to list models
**Impact:** Cannot verify model availability before scripting

**Example Problem:**
```bash
$ python ai-router.py --list
# Lists models with full info (good)
# BUT: Cannot filter, search, or get JSON output for parsing
```

**What Users Need:**
```bash
$ ai-router models list                    # List all
$ ai-router models search coding           # Find coding models
$ ai-router models info qwen3-coder-30b   # Get details
$ ai-router models list --json              # Programmatic format
```

### Issue #3: Configuration File Location Unclear (HIGH)
**Severity:** High | **Users Affected:** Operators, DevOps, Configuration
**Current:** Config locations scattered, discovery is trial-and-error

**Evidence:**
- User preferences at: `.ai-router-preferences.json` (undocumented)
- Machine configs at: `configs/[auto-detected-machine-id]/ai-router-config.json`
- Project configs at: `projects/[project-name]/config.json` (auto-created)
- Model configs at: `mlx/[model]/config.json` (HuggingFace format)

**What Users Ask:**
> "Where do I edit config? Which file controls what? How do I override auto-detection?"

**What Users Need:**
```bash
$ ai-router config show                    # Show active config
$ ai-router config list                    # List all configs
$ ai-router config edit                    # Interactive editor
$ ai-router config validate                # Check for errors
$ ai-router config --machine m4-macbook-pro # Force detection
```

### Issue #4: Machine Detection Silent Failures (MEDIUM-HIGH)
**Severity:** Medium-High | **Users Affected:** Multi-machine setups, WSL users
**Current:** Auto-detection with silent fallback

**Code Pattern (Lines 18-46):**
```python
def detect_machine():
    # ... detection logic ...
    except Exception:
        pass  # Silent failure!
    return "ryzen-3900x-3090"  # Always fallback
```

**What Happens:**
1. User on MacBook Pro or Xeon runs: `python ai-router.py`
2. Detection fails silently
3. App defaults to "ryzen-3900x-3090" config
4. Wrong models/settings loaded
5. User has no idea what went wrong

**What Users Need:**
```bash
$ ai-router machine detect
Detected machine: m4-macbook-pro (confidence: 95%)
Using config: configs/m4-macbook-pro/ai-router-config.json

$ ai-router machine detect --verbose
Checking platform... Darwin (macOS)
Checking CPU... ARM64 (M4 Pro)
Detected: m4-macbook-pro
```

### Issue #5: No Parameter Validation or Testing (MEDIUM-HIGH)
**Severity:** Medium-High | **Users Affected:** Advanced users, researchers
**Current:** Parameters set only during project creation or interactive config

**Problem:**
- Cannot test parameters before running full chat
- No validation hints (temperature range: 0.0-2.0?)
- Cannot dry-run with different parameters
- Error only discovered after model loads

**What Users Need:**
```bash
$ ai-router models info qwen3-coder-30b
# Show optimal parameters with ranges

$ ai-router validate --model qwen3-coder-30b --temp 0.7 --top-p 0.9
# Validate parameters before use (exit code: 0 if valid)

$ ai-router test --model phi4-14b --prompt "2+2="
# Quick test execution with minimal output
```

---

## SECTION 3: CONCRETE PROPOSALS

### Proposal 1: Unified CLI Command Structure with Subcommands

**Current:** `python ai-router.py [--help|--list]`
**Proposed:** `ai-router <command> <subcommand> [options]`

**Implementation:**
```
Commands structure:
├── run          - Execute models
│   ├── --model MODEL_ID
│   ├── --prompt TEXT
│   ├── --temperature 0.7
│   ├── --json (output JSON)
│   └── --test (dry-run only)
│
├── models       - Model management
│   ├── list     - List all models
│   ├── search   - Find models by capability
│   ├── info     - Get model details
│   └── test     - Quick test run
│
├── config       - Configuration management
│   ├── show     - Display active config
│   ├── list     - List all configs
│   ├── validate - Check for errors
│   ├── edit     - Interactive editor
│   └── set      - Set individual values
│
├── machine      - Machine/hardware detection
│   ├── detect   - Auto-detect hardware
│   ├── list     - List known machines
│   ├── set      - Override detection
│   └── status   - Show current settings
│
├── project      - Project management
│   ├── list     - List projects
│   ├── create   - Create new project
│   ├── load     - Load project
│   └── delete   - Remove project
│
├── validate     - System validation
│   ├── config   - Check configuration
│   ├── models   - Verify model files
│   ├── wsl      - Test WSL availability
│   └── full     - Complete system check
│
└── interactive  - Legacy interactive mode
    └── (no args) - Default behavior
```

**Example Usage:**
```bash
# Quick run
ai-router run --model qwen3-coder-30b --prompt "hello world"

# Find models for coding
ai-router models search coding

# Get model details
ai-router models info --json phi4-14b

# Validate setup
ai-router validate full

# Interactive mode (backward compatible)
ai-router interactive

# Show config
ai-router config show --machine ryzen-3900x-3090

# Machine detection
ai-router machine detect --verbose
```

### Proposal 2: Enhanced Help System with Examples

**Current:** Basic text help in `--help`
**Proposed:** Hierarchical help with examples at each level

**Implementation:**
```bash
$ ai-router --help
AI ROUTER v1.0 - Intelligent Model Selection & Execution

COMMANDS:
  run                Run a model with specified parameters
  models            List, search, and test available models
  config            Manage configuration and settings
  machine           Hardware detection and configuration
  project           Project management
  validate          System validation and diagnostics
  interactive       Legacy interactive mode (default)

QUICK START:
  ai-router run --model qwen3-coder-30b --prompt "hello"
  ai-router models list
  ai-router validate full

HELP:
  ai-router <command> --help     Show command help with examples
  ai-router config --help        Show config options
  ai-router validate --help      Show validation options

For documentation: ai-router docs

$ ai-router run --help
Run a model with specified parameters

USAGE:
  ai-router run [OPTIONS]

OPTIONS:
  --model TEXT           Model ID to use [required]
  --prompt TEXT          Prompt text [required]
  --temperature FLOAT    Creativity level (0.0-2.0) [default: 0.7]
  --top-p FLOAT          Diversity (0.0-1.0) [default: 0.9]
  --top-k INT            Top tokens (0-200) [default: 40]
  --max-tokens INT       Max output tokens [default: 2048]
  --system-prompt TEXT   Custom system prompt
  --json                 Output as JSON
  --test                 Dry-run (validate but don't execute)
  --quiet                Suppress non-essential output
  --help                 Show this message

EXAMPLES:
  ai-router run --model phi4-14b --prompt "What is 2+2?"
  ai-router run --model qwen3-coder-30b --prompt "write a function" --temp 0.5
  ai-router run --model gemma3-27b --prompt "story" --max-tokens 4096 --json

INTERACTIVE MODE:
  ai-router run          (will prompt for model and prompt interactively)

NOTES:
  - Temperature: lower (0.3) = more focused, higher (1.0+) = creative
  - For coding: temperature 0.3-0.7, top-p 0.8-0.9
  - For creative: temperature 0.8-1.2, top-p 0.9
  - For reasoning: temperature 0.2-0.5, top-p 0.95

RELATED COMMANDS:
  ai-router models list      Show all available models
  ai-router models info      Get model details
  ai-router validate full    Check system configuration
```

### Proposal 3: Interactive Config Generator with Validation

**Current:** Scattered config files, no validation
**Proposed:** Interactive setup wizard with validation

**Implementation:**
```bash
$ ai-router config setup
========================================
   AI ROUTER CONFIGURATION SETUP
========================================

STEP 1: Machine Detection
✓ Detected: m4-macbook-pro (Darwin, ARM64)
✓ Confidence: 95%
✓ Hardware: Apple M4 Pro, 36GB RAM

Override? [y/N]: n

STEP 2: Framework Selection
Available frameworks:
[1] llama.cpp (GPU acceleration, Windows/Linux/macOS)
[2] mlx      (Apple Silicon optimized, macOS only)
[3] ollama   (Easy setup, slower)

Select framework [1-3]: 2

STEP 3: Model Selection
Available MLX models:
[1] qwen25-14b       (Fast, general purpose)
[2] qwen25-coder-14b (Best for coding)
[3] phi4-14b         (Best for reasoning)
[4] gemma3-9b        (Fastest)

Primary model [1-4]: 2
Fallback model (for when primary fails) [1-4]: 1

STEP 4: Performance Settings
Temperature [0.2-2.0] (default: 0.7): 0.7
Top P [0.0-1.0] (default: 0.9): 0.9
Top K [0-200] (default: 40): 40
Max tokens [1-32768] (default: 2048): 2048

STEP 5: Performance Tuning (optional)
Enable GPU acceleration? [y/N]: y
GPU memory limit [GB] (auto): auto

SUMMARY:
✓ Machine:        m4-macbook-pro
✓ Framework:      mlx
✓ Primary model:  qwen25-coder-14b
✓ Fallback:       qwen25-14b
✓ Temperature:    0.7
✓ Max tokens:     2048
✓ GPU accel:      enabled

Save configuration? [Y/n]: y
Configuration saved to: configs/m4-macbook-pro/ai-router-config.json

Next steps:
  ai-router validate full    (check everything)
  ai-router models test      (test your models)
  ai-router run --model qwen25-coder-14b --prompt "hello" (quick test)
```

### Proposal 4: Better Error Messages with Actionable Guidance

**Current Error Pattern:**
```python
if choice.lower() == 'back':
    return
else:
    print(f"{Colors.BRIGHT_RED}Invalid choice. Please try again.{Colors.RESET}")
```

**Proposed Error Pattern:**
```python
def print_error(error_type, context=None, suggestions=None):
    """Print helpful error messages with guidance"""
    print(f"\n{Colors.BRIGHT_RED}ERROR:{Colors.RESET} {error_type}")

    if context:
        print(f"{Colors.YELLOW}Context:{Colors.RESET} {context}")

    if suggestions:
        print(f"{Colors.BRIGHT_GREEN}Suggestions:{Colors.RESET}")
        for suggestion in suggestions:
            print(f"  • {suggestion}")

    print()

# Usage:
if choice not in valid_choices:
    print_error(
        error_type="Invalid model selection",
        context=f"You entered '{choice}' but expected a number 1-{len(models)}",
        suggestions=[
            f"Enter a number from 1 to {len(models)}",
            "Type 'back' to return to menu",
            "Type 'list' to see available models again",
            "Run 'ai-router models list' to view models from command line"
        ]
    )
```

**Example Improved Errors:**
```
ERROR: Model file not found
Context: Expected model at: /mnt/d/models/organized/qwen3-coder-30b.gguf
Suggestions:
  • Check model path in config: ai-router config show
  • Verify model exists: ls /mnt/d/models/organized/
  • Download missing model: ai-router models download qwen3-coder-30b
  • Edit path: ai-router config set model-path /path/to/model

ERROR: WSL not available
Context: WSL required for llama.cpp models on Windows
Suggestions:
  • Enable WSL: wsl --install
  • Check WSL status: wsl --status
  • Use MLX instead (macOS): ai-router config set framework mlx
  • Use Ollama fallback: ai-router config set framework ollama

ERROR: Temperature parameter out of range
Context: Entered 2.5 but valid range is 0.0-2.0
Suggestions:
  • Use valid range: 0.0 (focused) to 2.0 (creative)
  • For coding: 0.3-0.7
  • For creative writing: 0.8-1.2
  • For reasoning: 0.2-0.5
  • Reset to default: ai-router config set temperature 0.7
```

### Proposal 5: Configuration Validation at Startup

**Current:** No validation, errors appear at runtime
**Proposed:** Early validation with clear guidance

**Implementation:**
```bash
$ python ai-router.py
========================================
   AI ROUTER v1.0
========================================

STARTUP VALIDATION:
✓ Python version:        3.11.5
✓ Machine detected:       ryzen-3900x-3090
✓ Config file found:      configs/ryzen-3900x-3090/ai-router-config.json
✓ Models directory:       /mnt/d/models/organized/
⚠ WSL status:            Not running (required for llama.cpp)
✗ Model file missing:     Qwen3-Coder-30B.gguf

WARNINGS:
  • WSL must be running to execute llama.cpp models
    Fix: wsl bash -c "cd /mnt/d/models && python ai-router-enhanced.py"

ERRORS:
  • Primary model 'qwen3-coder-30b' file not found
    Location: /mnt/d/models/organized/Qwen3-Coder-30B.gguf
    Suggestions:
      1. Download model: ai-router models download qwen3-coder-30b
      2. Update path: ai-router config set models.primary.path /path/to/model
      3. Use fallback: ai-router config set models.primary qwen25-14b

Would you like to:
[1] Continue (may fail at runtime)
[2] Fix config now (interactive setup)
[3] Exit and fix manually
[4] Show detailed diagnostics
[5] Skip validation

Choice [1-5]:
```

### Proposal 6: Machine Detection UI Feedback

**Current (Lines 18-46):**
```python
def detect_machine():
    machine_id_file = Path(".machine-id")
    if machine_id_file.exists():
        return machine_id_file.read_text().strip()  # Silent override

    # Auto-detect with silent failure
    system = platform.system()
    if system == "Darwin":
        return "m4-macbook-pro"
    # ... more detection ...
    return "ryzen-3900x-3090"  # Silent fallback!
```

**Proposed:**
```bash
$ ai-router machine detect
========================================
   MACHINE DETECTION
========================================

DETECTION STEPS:
[1/5] Checking OS platform...      ✓ Linux (Ubuntu)
[2/5] Checking CPU info...         ✓ AMD Ryzen 9 3900X
[3/5] Checking GPU...              ✓ NVIDIA RTX 3090
[4/5] Checking memory...           ✓ 64GB DDR4
[5/5] Checking WSL...              ✓ WSL 2.0.9

RESULT:
Machine ID:    ryzen-3900x-3090
Confidence:    98%
Config found:  configs/ryzen-3900x-3090/ai-router-config.json

HARDWARE SPECS:
  CPU:    AMD Ryzen 9 3900X (12-core / 24-thread)
  RAM:    64GB DDR4
  GPU:    NVIDIA RTX 3090 (24GB VRAM)
  WSL:    Enabled (2.0.9)

OPTIMIZATION:
✓ GPU offload:        Enabled (perfect for NVIDIA)
✓ Thread count:       24 (optimal for Ryzen)
✓ Memory allocation:  Up to 48GB available
✓ Framework:          llama.cpp (WSL optimized)

OVERRIDE (Optional):
If detection is incorrect, create .machine-id file:
  $ echo "m4-macbook-pro" > .machine-id

Or use command-line override:
  $ ai-router run --machine xeon-4060ti --model qwen3-coder-30b

Next: ai-router validate full
```

---

## SECTION 4: CLI COMPATIBILITY & RISKS

### Breaking Changes to Avoid

1. **Keep Interactive Mode as Default**
   - Users without args expect interactive menu
   - Change: `python ai-router.py` should still work
   - Solution: Keep existing behavior, ADD new options

2. **Maintain Config File Paths**
   - Existing users have configs at `configs/[machine-id]/`
   - Change: Auto-migration from old paths
   - Solution: Support legacy paths, warn on deprecation

3. **Model ID Stability**
   - Existing projects reference models by ID
   - Change: Renaming models breaks projects
   - Solution: Keep existing IDs, add aliases for new names

4. **WSL Path Handling**
   - Windows users see `/mnt/d/` paths
   - Change: Some proposals reference `D:\` paths
   - Solution: Detect context (Windows cmd vs WSL bash) and adjust output

### Backward Compatibility Strategy

```python
# Layer new CLI on top of existing code
def main():
    """Main entry point - backward compatible"""
    if len(sys.argv) > 1:
        # NEW: Try to parse as new CLI format
        try:
            result = parse_new_cli(sys.argv[1:])
            if result:
                return result
        except UnknownCommand:
            pass  # Fall through to old behavior

        # OLD: Support legacy arguments
        if sys.argv[1] == "--help":
            show_old_help()
            return
        elif sys.argv[1] == "--list":
            show_old_list()
            return
        else:
            print("Unknown argument. Use --help for usage.")
            return
    else:
        # DEFAULT: Interactive mode (unchanged)
        router.interactive_mode()

# This way:
# ✓ Old scripts still work
# ✓ New CLI options available
# ✓ No breaking changes
```

---

## SECTION 5: TESTS NEEDED

### 5.1 CLI Parsing Tests

```python
# tests/test_cli_parsing.py
import pytest
from ai_router import parse_cli_args

def test_parse_run_command():
    """Test: ai-router run --model qwen3 --prompt hello"""
    args = parse_cli_args(['run', '--model', 'qwen3', '--prompt', 'hello'])
    assert args.command == 'run'
    assert args.model == 'qwen3'
    assert args.prompt == 'hello'

def test_parse_models_list():
    """Test: ai-router models list"""
    args = parse_cli_args(['models', 'list'])
    assert args.command == 'models'
    assert args.subcommand == 'list'

def test_parse_models_search():
    """Test: ai-router models search coding"""
    args = parse_cli_args(['models', 'search', 'coding'])
    assert args.command == 'models'
    assert args.query == 'coding'

def test_backward_compat_help():
    """Test: python ai-router.py --help (old format)"""
    # Should still work
    args = parse_cli_args(['--help'])
    assert args.show_help == True

def test_backward_compat_list():
    """Test: python ai-router.py --list (old format)"""
    # Should still work
    args = parse_cli_args(['--list'])
    assert args.list_models == True

def test_invalid_command():
    """Test: ai-router invalid-command"""
    with pytest.raises(UnknownCommand):
        parse_cli_args(['invalid-command'])

def test_missing_required_args():
    """Test: ai-router run (missing --model and --prompt)"""
    with pytest.raises(MissingRequiredArg) as exc:
        parse_cli_args(['run'])
    assert '--model' in str(exc.value)
    assert '--prompt' in str(exc.value)

def test_parameter_validation():
    """Test: Parameter ranges validated"""
    with pytest.raises(ValueError):
        parse_cli_args(['run', '--temperature', '2.5'])  # Max 2.0

    with pytest.raises(ValueError):
        parse_cli_args(['run', '--top-p', '1.5'])  # Max 1.0
```

### 5.2 Help Text Tests

```python
# tests/test_help_text.py
def test_help_contains_examples():
    """Help output should include usage examples"""
    help_text = get_help()
    assert 'ai-router run' in help_text
    assert '--model' in help_text
    assert '--prompt' in help_text

def test_command_help_detailed():
    """Detailed help for each command"""
    help_text = get_command_help('run')
    assert 'EXAMPLES:' in help_text
    assert 'OPTIONS:' in help_text
    assert '--temperature' in help_text

def test_error_message_helpful():
    """Error messages should provide guidance"""
    error = InvalidChoice('5')
    msg = error.get_message(valid_choices=['1', '2', '3'])
    assert 'valid range' in msg.lower()
    assert '1-3' in msg

def test_color_disabled_in_piped_output():
    """ANSI colors should not appear in piped output"""
    # When stdout is not a TTY, colors should be disabled
    output = run_command_piped('ai-router --help')
    assert '\033[' not in output  # No ANSI codes
```

### 5.3 Config Validation Tests

```python
# tests/test_config_validation.py
def test_config_file_exists():
    """Config file should exist for detected machine"""
    machine_id = detect_machine()
    config_path = Path(f"configs/{machine_id}/ai-router-config.json")
    assert config_path.exists()

def test_config_is_valid_json():
    """Config should be valid JSON"""
    config = load_config()
    assert isinstance(config, dict)
    assert 'machine' in config
    assert 'models' in config

def test_config_has_required_fields():
    """Config must have all required fields"""
    config = load_config()
    required = ['machine', 'models', 'performance', 'inference']
    for field in required:
        assert field in config

def test_model_paths_exist():
    """All model files should exist"""
    config = load_config()
    primary_model = config['models']['primary']
    model_path = get_model_path(primary_model)
    assert Path(model_path).exists()

def test_temperature_in_valid_range():
    """Temperature should be 0.0-2.0"""
    config = load_config()
    temp = config['performance']['temperature']
    assert 0.0 <= temp <= 2.0

def test_config_override_manual():
    """Manual config in .machine-id should override detection"""
    # Create .machine-id
    Path('.machine-id').write_text('m4-macbook-pro')

    detected = detect_machine()
    assert detected == 'm4-macbook-pro'
```

### 5.4 Machine Detection Tests

```python
# tests/test_machine_detection.py
def test_detect_macos():
    """Should detect macOS as m4-macbook-pro"""
    with mock.patch('platform.system', return_value='Darwin'):
        assert detect_machine() == 'm4-macbook-pro'

def test_detect_linux_ryzen():
    """Should detect Linux with Ryzen as ryzen-3900x-3090"""
    with mock.patch('platform.system', return_value='Linux'):
        with mock.patch('open', mock.mock_open(read_data='Ryzen')):
            assert detect_machine() == 'ryzen-3900x-3090'

def test_detect_linux_xeon():
    """Should detect Linux with Xeon as xeon-4060ti"""
    with mock.patch('platform.system', return_value='Linux'):
        with mock.patch('open', mock.mock_open(read_data='Xeon')):
            assert detect_machine() == 'xeon-4060ti'

def test_manual_override_via_file():
    """Manual .machine-id file should override detection"""
    Path('.machine-id').write_text('xeon-4060ti\n')
    assert detect_machine() == 'xeon-4060ti'
    Path('.machine-id').unlink()

def test_detect_feedback():
    """Machine detection should provide feedback"""
    output = run_command('ai-router machine detect')
    assert 'Detected:' in output
    assert 'Confidence:' in output
    assert 'config' in output.lower()
```

### 5.5 Error Message Tests

```python
# tests/test_error_messages.py
def test_invalid_model_error_helpful():
    """Error on invalid model should show valid options"""
    try:
        validate_model('invalid-model')
    except InvalidModel as e:
        msg = str(e)
        assert 'qwen3' in msg.lower()
        assert 'phi4' in msg.lower()

def test_missing_config_error_helpful():
    """Error on missing config should show location"""
    try:
        load_config('nonexistent')
    except ConfigNotFound as e:
        msg = str(e)
        assert 'configs/' in msg
        assert 'json' in msg.lower()

def test_wsl_not_available_error():
    """WSL error should suggest alternatives"""
    error = WSLNotAvailable()
    msg = error.get_message()
    assert 'WSL' in msg
    assert 'enable' in msg.lower() or 'install' in msg.lower()

def test_model_file_not_found_error():
    """Missing model file error should show path"""
    error = ModelFileNotFound('qwen3', '/path/to/model.gguf')
    msg = error.get_message()
    assert '/path/to/model.gguf' in msg
    assert 'download' in msg.lower() or 'path' in msg.lower()
```

---

## SECTION 6: IMPLEMENTATION ROADMAP

### Phase 1: Foundation (Weeks 1-2)
- [ ] Add argparse for CLI parsing
- [ ] Implement basic subcommand structure (run, models, config)
- [ ] Add --help for all commands with examples
- [ ] Implement backward compatibility layer
- [ ] Add color disable for piped output
- **Deliverable:** `ai-router run --model qwen3-coder-30b --prompt "hello"`

### Phase 2: Discovery Features (Weeks 3-4)
- [ ] Implement `models list` with JSON output
- [ ] Implement `models search <query>` filtering
- [ ] Implement `models info <model-id>` details
- [ ] Machine detection with `machine detect`
- [ ] Config command: `config show` / `config list`
- **Deliverable:** `ai-router models search coding` finds relevant models

### Phase 3: Validation & Guidance (Weeks 5-6)
- [ ] Config validation at startup
- [ ] Parameter validation with helpful errors
- [ ] Machine detection feedback (confidence, override hints)
- [ ] WSL detection and status reporting
- [ ] Model file path validation
- **Deliverable:** Clear error messages with actionable suggestions

### Phase 4: Interactive Setup (Weeks 7-8)
- [ ] `config setup` interactive wizard
- [ ] Machine detection with override prompts
- [ ] Framework selection (llama.cpp, MLX, Ollama)
- [ ] Model selection with descriptions
- [ ] Parameter tuning with validation
- **Deliverable:** New users can run `ai-router config setup` to get started

### Phase 5: Testing (Weeks 9-10)
- [ ] CLI parsing tests (30+ test cases)
- [ ] Help text verification tests
- [ ] Config validation tests
- [ ] Machine detection tests
- [ ] Error message tests
- [ ] Integration tests
- **Deliverable:** 100+ automated tests, full coverage

### Phase 6: Documentation (Weeks 11-12)
- [ ] CLI reference guide
- [ ] Common tasks documentation
- [ ] Troubleshooting guide for errors
- [ ] Upgrade guide from old to new CLI
- [ ] Example scripts
- **Deliverable:** Comprehensive CLI docs + migration guide

---

## SECTION 7: EXAMPLE IMPLEMENTATIONS

### Example 1: Argparse Implementation

```python
# cli/parser.py
import argparse
from typing import Any

def create_parser() -> argparse.ArgumentParser:
    """Create main argument parser"""
    parser = argparse.ArgumentParser(
        prog='ai-router',
        description='AI Router - Intelligent Model Selection & Execution',
        epilog='For detailed help: ai-router <command> --help'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0'
    )

    subparsers = parser.add_subparsers(
        dest='command',
        help='Available commands',
        metavar=''
    )

    # Run command
    run_parser = subparsers.add_parser(
        'run',
        help='Execute a model with specified parameters',
        description='Run a model with specified parameters',
        epilog='''
Examples:
  ai-router run --model qwen3-coder-30b --prompt "write a function"
  ai-router run --model phi4-14b --prompt "2+2=" --temperature 0.3
  ai-router run --model gemma3-27b --prompt "story" --max-tokens 4096
        '''
    )

    run_parser.add_argument(
        '--model',
        required=True,
        help='Model ID to use (e.g., qwen3-coder-30b, phi4-14b)',
        metavar='MODEL_ID'
    )

    run_parser.add_argument(
        '--prompt',
        required=True,
        help='Prompt text to send to model',
        metavar='TEXT'
    )

    run_parser.add_argument(
        '--temperature',
        type=float,
        default=0.7,
        help='Creativity level (0.0-2.0, default: 0.7)',
        metavar='FLOAT'
    )

    run_parser.add_argument(
        '--top-p',
        type=float,
        default=0.9,
        help='Diversity (0.0-1.0, default: 0.9)',
        metavar='FLOAT'
    )

    run_parser.add_argument(
        '--top-k',
        type=int,
        default=40,
        help='Top tokens (0-200, default: 40)',
        metavar='INT'
    )

    run_parser.add_argument(
        '--max-tokens',
        type=int,
        default=2048,
        help='Maximum output length (1-32768, default: 2048)',
        metavar='INT'
    )

    run_parser.add_argument(
        '--system-prompt',
        help='Custom system prompt (optional)',
        metavar='TEXT'
    )

    run_parser.add_argument(
        '--json',
        action='store_true',
        help='Output as JSON'
    )

    run_parser.add_argument(
        '--test',
        action='store_true',
        help='Dry-run (validate but do not execute)'
    )

    # Models command
    models_parser = subparsers.add_parser(
        'models',
        help='Model management (list, search, info, test)',
        description='Manage and discover models'
    )

    models_subparsers = models_parser.add_subparsers(
        dest='subcommand',
        help='Model subcommands'
    )

    # models list
    list_parser = models_subparsers.add_parser(
        'list',
        help='List all available models'
    )
    list_parser.add_argument(
        '--json',
        action='store_true',
        help='Output as JSON'
    )

    # models search
    search_parser = models_subparsers.add_parser(
        'search',
        help='Search models by capability'
    )
    search_parser.add_argument(
        'query',
        help='Search query (e.g., coding, reasoning, creative)',
        metavar='QUERY'
    )
    search_parser.add_argument(
        '--json',
        action='store_true',
        help='Output as JSON'
    )

    # models info
    info_parser = models_subparsers.add_parser(
        'info',
        help='Get detailed model information'
    )
    info_parser.add_argument(
        '--model',
        required=True,
        help='Model ID',
        metavar='MODEL_ID'
    )
    info_parser.add_argument(
        '--json',
        action='store_true',
        help='Output as JSON'
    )

    # models test
    test_parser = models_subparsers.add_parser(
        'test',
        help='Quick test of a model'
    )
    test_parser.add_argument(
        '--model',
        required=True,
        help='Model ID',
        metavar='MODEL_ID'
    )

    # Config command
    config_parser = subparsers.add_parser(
        'config',
        help='Configuration management',
        description='View, edit, and validate configuration'
    )

    config_subparsers = config_parser.add_subparsers(
        dest='subcommand',
        help='Config subcommands'
    )

    config_subparsers.add_parser('show', help='Display active configuration')
    config_subparsers.add_parser('list', help='List all configurations')
    config_subparsers.add_parser('validate', help='Validate configuration')
    config_subparsers.add_parser('edit', help='Edit configuration interactively')

    # Machine command
    machine_parser = subparsers.add_parser(
        'machine',
        help='Hardware detection and configuration',
        description='Detect machine hardware and manage configuration'
    )

    machine_subparsers = machine_parser.add_subparsers(
        dest='subcommand',
        help='Machine subcommands'
    )

    detect_parser = machine_subparsers.add_parser('detect', help='Auto-detect machine')
    detect_parser.add_argument('--verbose', action='store_true', help='Verbose output')

    machine_subparsers.add_parser('list', help='List known machines')

    set_parser = machine_subparsers.add_parser('set', help='Override machine detection')
    set_parser.add_argument('machine_id', help='Machine ID')

    machine_subparsers.add_parser('status', help='Show current machine settings')

    # Validate command
    validate_parser = subparsers.add_parser(
        'validate',
        help='System validation and diagnostics',
        description='Validate system configuration and model files'
    )

    validate_subparsers = validate_parser.add_subparsers(
        dest='subcommand',
        help='Validation checks'
    )

    validate_subparsers.add_parser('config', help='Validate configuration files')
    validate_subparsers.add_parser('models', help='Verify model files exist')
    validate_subparsers.add_parser('wsl', help='Test WSL availability')
    validate_subparsers.add_parser('full', help='Complete system check')

    # Interactive mode (for backward compatibility)
    subparsers.add_parser(
        'interactive',
        help='Legacy interactive mode (same as running with no arguments)'
    )

    # Default to interactive if no command given
    parser.set_defaults(command='interactive')

    return parser


def parse_args(args=None) -> argparse.Namespace:
    """Parse command line arguments"""
    parser = create_parser()
    return parser.parse_args(args)
```

### Example 2: Enhanced Error Handling

```python
# cli/errors.py
from typing import List, Optional

class CLIError(Exception):
    """Base CLI error with helpful output"""

    def __init__(self, message: str, suggestions: Optional[List[str]] = None):
        self.message = message
        self.suggestions = suggestions or []
        super().__init__(self.get_formatted_message())

    def get_formatted_message(self) -> str:
        """Get formatted error message with suggestions"""
        lines = [f"\n{Colors.BRIGHT_RED}ERROR:{Colors.RESET} {self.message}"]

        if self.suggestions:
            lines.append(f"\n{Colors.BRIGHT_GREEN}Suggestions:{Colors.RESET}")
            for suggestion in self.suggestions:
                lines.append(f"  • {suggestion}")

        return '\n'.join(lines)


class InvalidModel(CLIError):
    """Invalid model selection"""

    def __init__(self, model_id: str, available_models: List[str]):
        message = f"Model '{model_id}' not found"
        suggestions = [
            f"Available models: {', '.join(available_models[:3])} (and {len(available_models)-3} more)",
            f"List all models: ai-router models list",
            f"Search models: ai-router models search <keyword>",
        ]
        super().__init__(message, suggestions)


class ParameterOutOfRange(CLIError):
    """Parameter outside valid range"""

    def __init__(self, param: str, value: Any, min_val: float, max_val: float):
        message = f"Parameter '{param}' value {value} is out of range"
        suggestions = [
            f"Valid range: {min_val} to {max_val}",
            self._get_param_suggestion(param)
        ]
        super().__init__(message, suggestions)

    @staticmethod
    def _get_param_suggestion(param: str) -> str:
        """Get helpful suggestion based on parameter"""
        hints = {
            'temperature': "For coding: 0.3-0.7, For creative: 0.8-1.2, For reasoning: 0.2-0.5",
            'top_p': "Typically 0.85-0.95 for most tasks",
            'top_k': "Typically 40-50, higher = more diverse",
            'max_tokens': "Usually 1024-4096, higher = longer responses"
        }
        return hints.get(param, f"Check documentation: ai-router run --help")


class ConfigNotFound(CLIError):
    """Configuration file not found"""

    def __init__(self, config_path: str, machine_id: Optional[str] = None):
        message = f"Configuration not found: {config_path}"
        suggestions = [
            f"Run setup: ai-router config setup",
            f"Detect machine: ai-router machine detect",
            f"List configs: ai-router config list",
        ]
        if machine_id:
            suggestions.append(f"For machine '{machine_id}': check configs/{machine_id}/")
        super().__init__(message, suggestions)


class WSLNotAvailable(CLIError):
    """WSL not available for llama.cpp"""

    def __init__(self):
        message = "WSL (Windows Subsystem for Linux) is required for llama.cpp models"
        suggestions = [
            "Enable WSL: wsl --install",
            "Check WSL status: wsl --status",
            "Use MLX instead (macOS only): ai-router config set framework mlx",
            "Use Ollama (easier setup): ai-router config set framework ollama",
            "Documentation: https://learn.microsoft.com/en-us/windows/wsl/install"
        ]
        super().__init__(message, suggestions)


class ModelFileNotFound(CLIError):
    """Model file missing"""

    def __init__(self, model_id: str, expected_path: str):
        message = f"Model file not found for '{model_id}'"
        suggestions = [
            f"Expected path: {expected_path}",
            f"Download model: ai-router models download {model_id}",
            f"Check path: ai-router config show",
            f"Update path: ai-router config set models.primary.path /path/to/model.gguf"
        ]
        super().__init__(message, suggestions)
```

---

## FINAL RECOMMENDATIONS

### Top 5 Priority Improvements:

1. **Add proper CLI argument parsing** (argparse)
   - Impact: Enables scripting and automation
   - Effort: 1 week
   - User benefit: High (50%+ of pain points)

2. **Implement machine detection feedback**
   - Impact: Eliminates silent failures
   - Effort: 3 days
   - User benefit: High (prevents wrong config loaded)

3. **Add configuration validation at startup**
   - Impact: Fail fast with clear guidance
   - Effort: 1 week
   - User benefit: Medium (saves debugging time)

4. **Improve error messages with suggestions**
   - Impact: Reduce user frustration
   - Effort: 1 week
   - User benefit: Medium (better troubleshooting)

5. **Create interactive config setup wizard**
   - Impact: Faster onboarding
   - Effort: 2 weeks
   - User benefit: High (new users can self-serve)

---

## CONCLUSION

The AI Router CLI has excellent functionality but poor **discoverability** and **operability**. Users struggle to:
- Run models without interactive menu
- Understand config file locations
- Get helpful error messages
- Verify system compatibility
- Automate or script execution

Implementing the proposed changes would transform it from an **interactive-first tool** into a **flexible, discoverable CLI** suitable for both interactive use and production automation.

**Estimated Timeline:** 12 weeks for full implementation (3 weeks if prioritizing core 5 items)

