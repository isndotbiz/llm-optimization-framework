# CLI Implementation Reference Guide
## Quick Code Examples & Best Practices

---

## QUICK REFERENCE: Implementation Patterns

### Pattern 1: Subcommand Structure with Click

```python
# Alternative to argparse: Click library (more elegant)
import click

@click.group()
def cli():
    """AI Router - Intelligent Model Selection & Execution"""
    pass

@cli.command()
@click.option('--model', required=True, help='Model ID')
@click.option('--prompt', required=True, help='Prompt text')
@click.option('--temperature', type=float, default=0.7, help='Temperature (0.0-2.0)')
def run(model, prompt, temperature):
    """Execute a model with specified parameters"""
    if not 0.0 <= temperature <= 2.0:
        click.secho('Temperature must be 0.0-2.0', fg='red')
        raise click.Abort()

    click.secho(f'Running {model}...', fg='green')
    # ... execution code ...

@cli.group()
def models():
    """Model management"""
    pass

@models.command()
@click.option('--json', is_flag=True, help='JSON output')
def list(json):
    """List all available models"""
    # ... list code ...

@models.command()
@click.argument('query')
@click.option('--json', is_flag=True)
def search(query, json):
    """Search models by capability"""
    # ... search code ...

if __name__ == '__main__':
    cli()

# Usage:
# python ai-router.py run --model qwen3 --prompt hello
# python ai-router.py models list --json
# python ai-router.py models search coding
```

### Pattern 2: Backward Compatibility Wrapper

```python
# Maintain old behavior while adding new CLI
import sys
from typing import Optional

def main():
    """Main entry point with backward compatibility"""

    # Check for legacy arguments first
    if len(sys.argv) > 1:
        arg = sys.argv[1]

        # Legacy arguments (old CLI)
        if arg == '--help':
            show_legacy_help()
            return
        elif arg == '--list':
            show_legacy_list()
            return
        elif arg.startswith('--'):
            # Unknown flag - might be from new CLI
            try:
                import argparse
                args = parse_new_cli()
                execute_cli_command(args)
                return
            except SystemExit:
                # argparse exited - that's ok
                return
            except Exception:
                # New CLI parsing failed, show legacy help
                print("Unknown argument. Use --help for usage.")
                return

    # Default: interactive mode
    router = AIRouter()
    router.interactive_mode()


def parse_new_cli():
    """New CLI argument parser"""
    import argparse

    parser = argparse.ArgumentParser(
        prog='ai-router',
        description='AI Router - Model Execution'
    )

    subparsers = parser.add_subparsers(dest='command', required=True)

    run_parser = subparsers.add_parser('run', help='Execute a model')
    run_parser.add_argument('--model', required=True)
    run_parser.add_argument('--prompt', required=True)
    run_parser.add_argument('--temperature', type=float, default=0.7)

    models_parser = subparsers.add_parser('models', help='Model management')
    models_subparsers = models_parser.add_subparsers(dest='subcommand')
    models_subparsers.add_parser('list', help='List models')
    search_parser = models_subparsers.add_parser('search', help='Search models')
    search_parser.add_argument('query')

    return parser.parse_args()


def execute_cli_command(args):
    """Execute command based on parsed arguments"""
    if args.command == 'run':
        # ... execution ...
        pass
    elif args.command == 'models':
        if args.subcommand == 'list':
            # ... list ...
            pass
        elif args.subcommand == 'search':
            # ... search ...
            pass
```

### Pattern 3: Color Output Detection

```python
# Automatically disable colors in piped output
import sys
import os

class Colors:
    """ANSI colors with auto-detection for TTY"""

    _USE_COLORS = None

    @classmethod
    def should_use_colors(cls) -> bool:
        """Check if we should use ANSI colors"""
        if cls._USE_COLORS is not None:
            return cls._USE_COLORS

        # Check if output is a TTY (interactive terminal)
        if not sys.stdout.isatty():
            cls._USE_COLORS = False
            return False

        # Check NO_COLOR environment variable
        if os.environ.get('NO_COLOR'):
            cls._USE_COLORS = False
            return False

        cls._USE_COLORS = True
        return True

    @classmethod
    def _color(cls, code: str) -> str:
        """Return ANSI code or empty string based on TTY"""
        return code if cls.should_use_colors() else ''

    RESET = property(lambda self: self._color('\033[0m'))
    BRIGHT_GREEN = property(lambda self: self._color('\033[92m'))
    BRIGHT_RED = property(lambda self: self._color('\033[91m'))
    # ... etc

    def print_success(self, msg: str):
        """Print success message"""
        print(f"{self.BRIGHT_GREEN}✓{self.RESET} {msg}")

    def print_error(self, msg: str):
        """Print error message"""
        print(f"{self.BRIGHT_RED}✗{self.RESET} {msg}")


# Usage:
colors = Colors()
if command_succeeded:
    colors.print_success("Configuration saved")
else:
    colors.print_error("Failed to save configuration")

# Works correctly whether piped or interactive:
# Interactive: $ ai-router config setup    → colored output
# Piped:       $ ai-router config setup | tee log.txt  → no colors in log
```

### Pattern 4: Configuration Validation

```python
# Config validation with clear error reporting
from pathlib import Path
from typing import Dict, List, Tuple
import json

class ConfigValidator:
    """Validate configuration files"""

    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.config: Dict = {}
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate(self) -> bool:
        """Run all validations, return True if valid"""
        self._load_config()
        self._validate_structure()
        self._validate_machine()
        self._validate_models()
        self._validate_performance()
        self._validate_paths()
        return len(self.errors) == 0

    def _load_config(self):
        """Load and parse JSON"""
        try:
            with open(self.config_path) as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.errors.append(f"Config file not found: {self.config_path}")
        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON: {e}")

    def _validate_structure(self):
        """Check required top-level keys"""
        required = ['machine', 'models', 'performance', 'inference']
        for key in required:
            if key not in self.config:
                self.errors.append(f"Missing required key: {key}")

    def _validate_machine(self):
        """Validate machine configuration"""
        machine = self.config.get('machine', {})
        if 'id' not in machine:
            self.errors.append("machine.id is required")
        if 'name' not in machine:
            self.errors.append("machine.name is required")

    def _validate_models(self):
        """Validate model configuration"""
        models = self.config.get('models', {})
        if 'primary' not in models:
            self.errors.append("models.primary is required")

        # Check model files exist
        if 'paths' in models:
            for model_id, path in models['paths'].items():
                if not Path(path).exists():
                    self.warnings.append(f"Model file not found: {path}")

    def _validate_performance(self):
        """Validate performance parameters"""
        perf = self.config.get('performance', {})

        if 'temperature' in perf:
            temp = perf['temperature']
            if not (0.0 <= temp <= 2.0):
                self.errors.append(f"temperature must be 0.0-2.0, got {temp}")

        if 'top_p' in perf:
            top_p = perf['top_p']
            if not (0.0 <= top_p <= 1.0):
                self.errors.append(f"top_p must be 0.0-1.0, got {top_p}")

    def _validate_paths(self):
        """Validate file paths"""
        paths = self.config.get('model_paths', {})
        for key, path in paths.items():
            if path.startswith('~'):
                expanded = Path(path).expanduser()
                if not expanded.exists():
                    self.warnings.append(f"{key} path not found: {path}")

    def report(self):
        """Print validation report"""
        print("\nCONFIGURATION VALIDATION")
        print("=" * 50)

        if not self.errors and not self.warnings:
            print(f"{Colors.BRIGHT_GREEN}✓ Configuration is valid{Colors.RESET}\n")
            return

        if self.errors:
            print(f"{Colors.BRIGHT_RED}ERRORS:{Colors.RESET}")
            for error in self.errors:
                print(f"  ✗ {error}")

        if self.warnings:
            print(f"\n{Colors.BRIGHT_YELLOW}WARNINGS:{Colors.RESET}")
            for warning in self.warnings:
                print(f"  ⚠ {warning}")

        print()


# Usage:
validator = ConfigValidator('configs/ryzen-3900x-3090/ai-router-config.json')
if validator.validate():
    print("Config is valid!")
else:
    validator.report()
    sys.exit(1)
```

### Pattern 5: Machine Detection with Feedback

```python
# Enhanced machine detection with reporting
from dataclasses import dataclass
from typing import Optional

@dataclass
class MachineDetectionResult:
    """Result of machine detection"""
    machine_id: str
    detected_os: str
    detected_cpu: str
    detected_gpu: Optional[str]
    wsl_available: bool
    confidence: float  # 0.0-1.0
    error: Optional[str] = None


def detect_machine_with_feedback() -> MachineDetectionResult:
    """Detect machine with detailed feedback"""
    import platform
    import subprocess

    result = MachineDetectionResult(
        machine_id="unknown",
        detected_os=platform.system(),
        detected_cpu="",
        detected_gpu=None,
        wsl_available=False,
        confidence=0.0
    )

    # Check for manual override
    override_file = Path('.machine-id')
    if override_file.exists():
        result.machine_id = override_file.read_text().strip()
        result.confidence = 1.0
        print(f"Using manual override from .machine-id: {result.machine_id}")
        return result

    # Detect OS
    if result.detected_os == "Darwin":
        result.machine_id = "m4-macbook-pro"
        result.confidence = 0.9
    elif result.detected_os == "Linux":
        # Detect CPU
        try:
            with open('/proc/cpuinfo') as f:
                cpu_info = f.read()
                if 'Ryzen' in cpu_info:
                    result.detected_cpu = "AMD Ryzen"
                    result.machine_id = "ryzen-3900x-3090"
                    result.confidence = 0.9
                elif 'Xeon' in cpu_info:
                    result.detected_cpu = "Intel Xeon"
                    result.machine_id = "xeon-4060ti"
                    result.confidence = 0.85
                else:
                    result.machine_id = "ryzen-3900x-3090"  # Fallback
                    result.confidence = 0.5
        except Exception as e:
            result.error = str(e)
            result.machine_id = "ryzen-3900x-3090"
            result.confidence = 0.3

        # Check WSL
        try:
            with open('/proc/version') as f:
                if 'microsoft' in f.read().lower():
                    result.wsl_available = True
        except:
            pass

    return result


def print_detection_report(result: MachineDetectionResult):
    """Print machine detection report"""
    print("\nMACHINE DETECTION")
    print("=" * 50)
    print(f"Detected OS:     {result.detected_os}")
    print(f"Detected CPU:    {result.detected_cpu}")
    print(f"WSL Available:   {'Yes' if result.wsl_available else 'No'}")
    print(f"\nResult:")
    print(f"  Machine ID:    {result.machine_id}")
    print(f"  Confidence:    {result.confidence * 100:.0f}%")

    if result.confidence < 0.8:
        print(f"\n{Colors.BRIGHT_YELLOW}⚠ Low confidence in detection{Colors.RESET}")
        print("  Override with: echo 'machine-id' > .machine-id")

    if result.error:
        print(f"\n{Colors.BRIGHT_YELLOW}Warning:{Colors.RESET} {result.error}")

    print()


# Usage:
result = detect_machine_with_feedback()
print_detection_report(result)

if result.confidence < 0.8:
    print("Would you like to specify machine ID manually? [y/N]")
    # ... etc
```

### Pattern 6: Helpful Error Messages with Context

```python
# Error messages that guide users to solutions
from enum import Enum
from typing import List, Optional

class ErrorSeverity(Enum):
    INFO = "ℹ"
    WARNING = "⚠"
    ERROR = "✗"
    FATAL = "☠"


class HelpfulError(Exception):
    """Error with suggestions and documentation links"""

    def __init__(
        self,
        title: str,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        suggestions: Optional[List[str]] = None,
        documentation_link: Optional[str] = None,
        next_steps: Optional[List[str]] = None
    ):
        self.title = title
        self.message = message
        self.severity = severity
        self.suggestions = suggestions or []
        self.documentation_link = documentation_link
        self.next_steps = next_steps or []
        super().__init__(self.format_message())

    def format_message(self) -> str:
        """Format error message for display"""
        lines = [
            f"\n{Colors.BRIGHT_RED}{self.severity.value} {self.title}{Colors.RESET}",
            f"{self.message}"
        ]

        if self.suggestions:
            lines.append(f"\n{Colors.BRIGHT_GREEN}What you can do:{Colors.RESET}")
            for suggestion in self.suggestions:
                lines.append(f"  • {suggestion}")

        if self.documentation_link:
            lines.append(f"\n{Colors.BRIGHT_CYAN}Learn more:{Colors.RESET} {self.documentation_link}")

        if self.next_steps:
            lines.append(f"\n{Colors.BRIGHT_WHITE}Next steps:{Colors.RESET}")
            for i, step in enumerate(self.next_steps, 1):
                lines.append(f"  {i}. {step}")

        return '\n'.join(lines) + '\n'


# Usage examples:
def validate_temperature(value: float):
    if not 0.0 <= value <= 2.0:
        raise HelpfulError(
            title="Invalid Temperature",
            message=f"Temperature {value} is outside valid range (0.0-2.0)",
            suggestions=[
                f"Use a value between 0.0 and 2.0",
                "For coding: 0.3-0.7",
                "For creative writing: 0.8-1.2",
                "For reasoning: 0.2-0.5",
            ],
            documentation_link="https://docs.ai-router.local/parameters#temperature",
            next_steps=[
                "Run: ai-router run --temperature 0.7",
                "See all options: ai-router run --help"
            ]
        )


def check_wsl_available():
    if not is_wsl():
        raise HelpfulError(
            title="WSL Not Available",
            message="Windows Subsystem for Linux is required for llama.cpp models",
            severity=ErrorSeverity.ERROR,
            suggestions=[
                "Install WSL: wsl --install",
                "Check status: wsl --status",
                "Or use MLX (macOS only): ai-router config set framework mlx",
                "Or use Ollama (easier): ai-router config set framework ollama"
            ],
            documentation_link="https://learn.microsoft.com/en-us/windows/wsl/install",
            next_steps=[
                "Enable WSL in Windows",
                "Restart your computer",
                "Try again: python ai-router.py"
            ]
        )
```

---

## TESTING EXAMPLES

### Unit Test Template

```python
# tests/test_cli.py
import pytest
import subprocess
import json
from pathlib import Path

class TestCLIRun:
    """Test ai-router run command"""

    def test_run_with_required_args(self, tmp_path):
        """Test: ai-router run --model qwen3 --prompt hello"""
        result = subprocess.run(
            ['python', 'ai-router.py', 'run', '--model', 'qwen3-coder-30b', '--prompt', 'test', '--test'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert 'qwen3' in result.stdout.lower()

    def test_run_missing_model(self):
        """Test: ai-router run --prompt hello (missing --model)"""
        result = subprocess.run(
            ['python', 'ai-router.py', 'run', '--prompt', 'test'],
            capture_output=True,
            text=True
        )
        assert result.returncode != 0
        assert '--model' in result.stderr.lower()

    def test_run_invalid_temperature(self):
        """Test: ai-router run --temperature 2.5 (out of range)"""
        result = subprocess.run(
            ['python', 'ai-router.py', 'run',
             '--model', 'qwen3',
             '--prompt', 'hello',
             '--temperature', '2.5'],
            capture_output=True,
            text=True
        )
        assert result.returncode != 0
        assert 'temperature' in result.stderr.lower() or 'range' in result.stderr.lower()

    def test_run_json_output(self):
        """Test: ai-router run ... --json produces valid JSON"""
        result = subprocess.run(
            ['python', 'ai-router.py', 'run',
             '--model', 'qwen3',
             '--prompt', 'hello',
             '--json',
             '--test'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        # Should have valid JSON output
        data = json.loads(result.stdout)
        assert 'model' in data
        assert 'prompt' in data


class TestCLIModels:
    """Test ai-router models commands"""

    def test_models_list(self):
        """Test: ai-router models list"""
        result = subprocess.run(
            ['python', 'ai-router.py', 'models', 'list'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert 'qwen' in result.stdout.lower()

    def test_models_list_json(self):
        """Test: ai-router models list --json"""
        result = subprocess.run(
            ['python', 'ai-router.py', 'models', 'list', '--json'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert isinstance(data, list)
        assert len(data) > 0

    def test_models_search(self):
        """Test: ai-router models search coding"""
        result = subprocess.run(
            ['python', 'ai-router.py', 'models', 'search', 'coding'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert 'qwen' in result.stdout.lower() or 'coder' in result.stdout.lower()


class TestBackwardCompatibility:
    """Test legacy argument support"""

    def test_legacy_help(self):
        """Test: python ai-router.py --help (old format)"""
        result = subprocess.run(
            ['python', 'ai-router.py', '--help'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert 'Usage' in result.stdout

    def test_legacy_list(self):
        """Test: python ai-router.py --list (old format)"""
        result = subprocess.run(
            ['python', 'ai-router.py', '--list'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert 'qwen' in result.stdout.lower()
```

---

## FILE STRUCTURE AFTER IMPLEMENTATION

```
D:\models\
├── ai-router.py (updated with new CLI)
├── ai-router-enhanced.py (updated with new CLI)
├── cli/
│   ├── __init__.py
│   ├── parser.py          (argparse setup)
│   ├── commands/
│   │   ├── __init__.py
│   │   ├── run.py         (run command)
│   │   ├── models.py      (models commands)
│   │   ├── config.py      (config commands)
│   │   ├── machine.py     (machine detection)
│   │   └── validate.py    (validation)
│   ├── errors.py          (helpful error classes)
│   ├── colors.py          (color handling with TTY detection)
│   └── validators.py      (config validation logic)
├── tests/
│   ├── __init__.py
│   ├── test_cli.py        (CLI parsing tests)
│   ├── test_commands.py   (command execution tests)
│   ├── test_errors.py     (error message tests)
│   ├── test_config.py     (config validation tests)
│   └── test_machine.py    (machine detection tests)
├── docs/
│   ├── CLI-REFERENCE.md   (user documentation)
│   ├── MIGRATION.md       (old to new CLI guide)
│   └── EXAMPLES.md        (command examples)
└── START-AI-ROUTER.bat    (unchanged)
```

---

## MIGRATION CHECKLIST

- [ ] Create `cli/` module with argparse setup
- [ ] Implement backward compatibility layer
- [ ] Add `cli/commands/` for each subcommand
- [ ] Create helpful error classes in `cli/errors.py`
- [ ] Add TTY detection for colors in `cli/colors.py`
- [ ] Write 100+ tests
- [ ] Update docstring examples
- [ ] Create migration guide for users
- [ ] Test all backward compatibility
- [ ] Deploy with version flag: `ai-router --version`

