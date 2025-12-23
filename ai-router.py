#!/usr/bin/env python3
"""
AI Router - Intelligent Model Selection and Execution CLI
Optimized for RTX 3090 (WSL) and MacBook M4 Pro
Based on 2025 Research Findings (Sep-Nov 2025)
"""

import os
import sys
import subprocess
import platform
import time
import json
import argparse
from pathlib import Path
from logging_config_v2 import setup_structured_logging, set_trace_id

# Import centralized model configuration (single source of truth)
from config.models import ModelDatabase

# Import config validator for validation commands
sys.path.insert(0, str(Path(__file__).parent))
try:
    from utils.config_validator import ConfigValidator
except ImportError:
    ConfigValidator = None


def detect_machine():
    """
    Auto-detect which machine we're running on based on hardware
    Returns: machine_id string (m4-macbook-pro, ryzen-3900x-3090, or xeon-4060ti)
    """
    # First check if .machine-id file exists (manual override)
    machine_id_file = Path(".machine-id")
    if machine_id_file.exists():
        return machine_id_file.read_text().strip()

    # Auto-detect based on platform and CPU info
    system = platform.system()

    if system == "Darwin":  # macOS
        return "m4-macbook-pro"

    if system == "Linux":
        try:
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read()
                if 'Ryzen' in cpuinfo:
                    return "ryzen-3900x-3090"
                elif 'Xeon' in cpuinfo or 'Intel' in cpuinfo:
                    return "xeon-4060ti"
        except Exception:
            pass

    # Default fallback
    return "ryzen-3900x-3090"


def load_machine_config(machine_id):
    """Load the machine-specific configuration file"""
    config_path = Path(f"configs/{machine_id}/ai-router-config.json")
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    return None


def is_wsl():
    """Detect if running in WSL (Windows Subsystem for Linux)"""
    try:
        with open('/proc/version', 'r') as f:
            return 'microsoft' in f.read().lower()
    except Exception:
        return False


class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

    # Foreground colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'

    # Bright foreground colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'

    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'


class AIRouter:
    """Main AI Router application"""

    def __init__(self):
        self.platform = platform.system()
        self.models = ModelDatabase.get_platform_models()

        # Detect correct models directory based on platform
        if self.platform == "Windows":
            self.models_dir = Path("D:/models")
        elif is_wsl():
            self.models_dir = Path("/mnt/d/models")
        else:  # macOS or Linux
            self.models_dir = Path.home() / "models"

        self.system_prompts_dir = self.models_dir

        # Initialize structured logging
        self.logger = setup_structured_logging(self.models_dir)
        self.logger.info(f"AI Router initialized on {self.platform}")

    def _validate_resources_for_model(self, model_data):
        """Validate that system has sufficient resources to run the model"""
        try:
            # Check if WSL is available for llama.cpp models
            if model_data['framework'] == 'llama.cpp':
                if self.platform == "Windows":
                    # Quick WSL check
                    result = subprocess.run(
                        ['wsl', '--status'],
                        capture_output=True,
                        timeout=5
                    )
                    if result.returncode != 0:
                        self.logger.warning("WSL not available or not running")
                        return False

            # For now, assume resources are sufficient if WSL check passes
            # Could add memory checks here in the future
            return True

        except subprocess.TimeoutExpired:
            self.logger.warning("WSL status check timed out")
            # Assume OK if timeout (WSL might be slow but working)
            return True
        except Exception as e:
            self.logger.warning(f"Resource validation error: {e}")
            return True  # Be permissive on validation errors

    def _get_fallback_model(self, model_id):
        """Get a smaller fallback model if primary model fails"""
        fallback_map = {
            "qwen3-coder-30b": "dolphin-llama31-8b",
            "llama33-70b": "ministral-3-14b",
            "phi4-14b": "dolphin-llama31-8b",
            "dolphin-mistral-24b": "wizard-vicuna-13b",
            "gemma3-27b": "dolphin-llama31-8b",
        }

        fallback_id = fallback_map.get(model_id)
        if fallback_id and fallback_id in self.models:
            self.logger.info(f"Fallback model for {model_id}: {fallback_id}")
            return fallback_id
        return None

    def print_banner(self):
        """Print colorful banner"""
        print(f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}")
        print("=" * 84)
        print("                                     ")
        print("            AI ROUTER CLI v1.0       ")
        print("                                     ")
        print("  Intelligent Model Selection & Execution Framework")
        print("     Based on 2025 Research (Sep-Nov 2025)")
        print("                                     ")
        print("=" * 84)
        print(Colors.RESET)

        # Platform info
        if self.platform == "Darwin":
            platform_name = (
                f"{Colors.BRIGHT_GREEN}MacBook M4 Pro "
                f"(MLX Optimized){Colors.RESET}"
            )
        else:
            platform_name = (
                f"{Colors.BRIGHT_YELLOW}RTX 3090 "
                f"(WSL Optimized){Colors.RESET}"
            )

        print(f"\n{Colors.BRIGHT_WHITE}Platform: {platform_name}")
        print(
            f"{Colors.BRIGHT_WHITE}Available Models: "
            f"{Colors.BRIGHT_CYAN}{len(self.models)}{Colors.RESET}"
        )
        print()

    def print_model_info(self, model_id, model_data):
        """Display detailed model information"""
        sep = "=" * 64
        print(f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}{sep}{Colors.RESET}")
        print(
            f"{Colors.BRIGHT_CYAN}{Colors.BOLD}"
            f"  MODEL INFORMATION{Colors.RESET}"
        )
        print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}{sep}{Colors.RESET}\n")

        print(
            f"{Colors.BRIGHT_WHITE}Name:          "
            f"{Colors.BRIGHT_GREEN}{model_data['name']}{Colors.RESET}"
        )
        print(
            f"{Colors.BRIGHT_WHITE}Model ID:      "
            f"{Colors.BRIGHT_YELLOW}{model_id}{Colors.RESET}"
        )
        print(
            f"{Colors.BRIGHT_WHITE}Size:          "
            f"{Colors.BRIGHT_MAGENTA}{model_data['size']}{Colors.RESET}"
        )
        print(
            f"{Colors.BRIGHT_WHITE}Speed:         "
            f"{Colors.BRIGHT_CYAN}{model_data['speed']}{Colors.RESET}"
        )
        print(
            f"{Colors.BRIGHT_WHITE}Framework:     "
            f"{Colors.BRIGHT_BLUE}"
            f"{model_data['framework'].upper()}{Colors.RESET}"
        )
        print(
            f"{Colors.BRIGHT_WHITE}Use Case:      "
            f"{Colors.YELLOW}{model_data['use_case']}{Colors.RESET}"
        )
        print(
            f"{Colors.BRIGHT_WHITE}Context:       "
            f"{Colors.CYAN}{model_data['context']:,} tokens{Colors.RESET}"
        )

        print(f"\n{Colors.BRIGHT_WHITE}Optimal Parameters:{Colors.RESET}")
        print(
            f"  {Colors.WHITE}Temperature:   "
            f"{Colors.GREEN}{model_data['temperature']}{Colors.RESET}"
        )
        print(
            f"  {Colors.WHITE}Top-P:         "
            f"{Colors.GREEN}{model_data['top_p']}{Colors.RESET}"
        )
        print(
            f"  {Colors.WHITE}Top-K:         "
            f"{Colors.GREEN}{model_data['top_k']}{Colors.RESET}"
        )

        if model_data['special_flags']:
            flags = ' '.join(model_data['special_flags'])
            print(
                f"\n{Colors.BRIGHT_YELLOW}Special Flags: "
                f"{Colors.YELLOW}{flags}{Colors.RESET}"
            )

        if model_data['system_prompt']:
            print(
                f"\n{Colors.BRIGHT_GREEN}System Prompt: "
                f"{Colors.GREEN}{model_data['system_prompt']}{Colors.RESET}"
            )
        else:
            print(
                f"\n{Colors.BRIGHT_RED}"
                f"[!] NO system prompt support{Colors.RESET}"
            )

        if model_data['notes']:
            print(f"\n{Colors.BRIGHT_MAGENTA}Notes:{Colors.RESET}")
            print(f"  {Colors.MAGENTA}{model_data['notes']}{Colors.RESET}")

        print()

    def list_models(self):
        """List all available models"""
        sep1 = "╔" + "═" * 62 + "╗"
        sep2 = "╚" + "═" * 62 + "╝"
        print(
            f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}{sep1}{Colors.RESET}"
        )
        print(
            f"{Colors.BRIGHT_CYAN}{Colors.BOLD}"
            f"║  AVAILABLE MODELS{Colors.RESET}"
        )
        print(
            f"{Colors.BRIGHT_CYAN}{Colors.BOLD}{sep2}{Colors.RESET}\n"
        )

        for idx, (model_id, model_data) in enumerate(
            self.models.items(), 1
        ):
            print(
                f"{Colors.BRIGHT_YELLOW}[{idx}]{Colors.RESET} "
                f"{Colors.BRIGHT_WHITE}{model_id}{Colors.RESET}"
            )
            print(f"    {Colors.WHITE}{model_data['name']}{Colors.RESET}")
            print(
                f"    {Colors.CYAN}"
                f"Use case: {model_data['use_case']}{Colors.RESET}"
            )
            print(
                f"    {Colors.GREEN}{model_data['size']} | "
                f"{model_data['speed']}{Colors.RESET}"
            )
            print()

    def interactive_mode(self):
        """Interactive model selection"""
        self.print_banner()

        while True:
            sep = "=" * 63
            print(
                f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}{sep}{Colors.RESET}"
            )
            print(
                f"{Colors.BRIGHT_WHITE}"
                f"What would you like to do?{Colors.RESET}\n"
            )
            print(
                f"{Colors.BRIGHT_GREEN}[1]{Colors.RESET} "
                f"Auto-select model based on prompt"
            )
            print(
                f"{Colors.BRIGHT_GREEN}[2]{Colors.RESET} "
                f"Manually select model"
            )
            print(
                f"{Colors.BRIGHT_GREEN}[3]{Colors.RESET} "
                f"List all available models"
            )
            print(
                f"{Colors.BRIGHT_GREEN}[4]{Colors.RESET} "
                f"View system prompt examples"
            )
            print(
                f"{Colors.BRIGHT_GREEN}[5]{Colors.RESET} "
                f"View optimal parameters guide"
            )
            print(
                f"{Colors.BRIGHT_GREEN}[6]{Colors.RESET} "
                f"View documentation guides"
            )
            print(f"{Colors.BRIGHT_GREEN}[7]{Colors.RESET} Exit")
            print(
                f"{Colors.BRIGHT_CYAN}{Colors.BOLD}{sep}{Colors.RESET}"
            )

            choice = input(
                f"\n{Colors.BRIGHT_YELLOW}"
                f"Enter choice [1-7]: {Colors.RESET}"
            ).strip()

            if choice == "1":
                self.auto_select_mode()
            elif choice == "2":
                self.manual_select_mode()
            elif choice == "3":
                self.list_models()
            elif choice == "4":
                self.view_system_prompts()
            elif choice == "5":
                self.view_parameters_guide()
            elif choice == "6":
                self.view_documentation()
            elif choice == "7":
                print(
                    f"\n{Colors.BRIGHT_GREEN}Goodbye!{Colors.RESET}\n"
                )
                sys.exit(0)
            else:
                print(
                    f"{Colors.BRIGHT_RED}"
                    f"Invalid choice. Please try again.{Colors.RESET}"
                )

    def auto_select_mode(self):
        """Auto-select model based on prompt"""
        print(
            f"\n{Colors.BRIGHT_CYAN}"
            f"Enter your prompt (or 'back' to return):{Colors.RESET}"
        )
        prompt = input(f"{Colors.YELLOW}> {Colors.RESET}").strip()

        if prompt.lower() == 'back':
            return

        # Detect use case
        use_case = ModelDatabase.detect_use_case(prompt)
        print(
            f"\n{Colors.BRIGHT_MAGENTA}Detected use case: "
            f"{Colors.BRIGHT_WHITE}{use_case.upper()}{Colors.RESET}"
        )

        # Recommend model
        model_id, model_data = ModelDatabase.recommend_model(
            use_case, self.models
        )
        print(
            f"{Colors.BRIGHT_GREEN}Recommended model: "
            f"{Colors.BRIGHT_WHITE}{model_data['name']}{Colors.RESET}"
        )

        # Show model info
        self.print_model_info(model_id, model_data)

        # Ask if user wants to run
        confirm = input(
            f"\n{Colors.BRIGHT_YELLOW}"
            f"Run this model? [Y/n]: {Colors.RESET}"
        ).strip().lower()
        if confirm in ['', 'y', 'yes']:
            self.run_model(model_id, model_data, prompt)

    def manual_select_mode(self):
        """Manually select model"""
        self.list_models()

        model_ids = list(self.models.keys())
        choice = input(
            f"\n{Colors.BRIGHT_YELLOW}"
            f"Select model number (or 'back'): {Colors.RESET}"
        ).strip()

        if choice.lower() == 'back':
            return

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(model_ids):
                model_id = model_ids[idx]
                model_data = self.models[model_id]

                self.print_model_info(model_id, model_data)

                prompt = input(
                    f"\n{Colors.BRIGHT_CYAN}"
                    f"Enter your prompt: {Colors.RESET}"
                ).strip()
                self.run_model(model_id, model_data, prompt)
            else:
                print(
                    f"{Colors.BRIGHT_RED}"
                    f"[X] Invalid model number.{Colors.RESET}"
                )
                print(
                    f"{Colors.BRIGHT_YELLOW}"
                    f"Please enter a valid number from the list above."
                    f"{Colors.RESET}"
                )
        except ValueError:
            print(
                f"{Colors.BRIGHT_RED}[X] Invalid input.{Colors.RESET}"
            )
            print(
                f"{Colors.BRIGHT_YELLOW}"
                f"Please enter a valid number.{Colors.RESET}"
            )

    def run_model(
        self, model_id, model_data, prompt, retry_count=0, max_retries=2
    ):
        """Execute the model with optimal parameters and retry logic"""
        self.logger.info(
            f"Starting model execution: {model_id} ({model_data['name']})"
        )

        # Validate resources before execution
        if not self._validate_resources_for_model(model_data):
            self.logger.error(
                f"Insufficient resources for model {model_id}"
            )
            print(
                f"\n{Colors.BRIGHT_RED}[X] Error: "
                f"Insufficient system resources{Colors.RESET}"
            )
            print(
                f"{Colors.BRIGHT_YELLOW}Model {model_data['name']} "
                f"requires:{Colors.RESET}"
            )
            print(
                f"{Colors.YELLOW}  - Available RAM: "
                f"~{model_data['size']} free{Colors.RESET}"
            )
            print(
                f"{Colors.YELLOW}  - WSL must be running "
                f"(for llama.cpp models){Colors.RESET}\n"
            )

            # Try fallback to smaller model
            fallback_id = self._get_fallback_model(model_id)
            if fallback_id and retry_count == 0:
                print(
                    f"{Colors.BRIGHT_CYAN}→ Trying fallback model: "
                    f"{self.models[fallback_id]['name']}{Colors.RESET}\n"
                )
                return self.run_model(
                    fallback_id,
                    self.models[fallback_id],
                    prompt,
                    retry_count=1
                )
            return None

        print(
            f"\n{Colors.BRIGHT_GREEN}{Colors.BOLD}"
            f"Launching {model_data['name']}...{Colors.RESET}\n"
        )

        try:
            if model_data['framework'] == 'mlx':
                result = self.run_mlx_model(model_data, prompt)
            else:
                result = self.run_llamacpp_model(model_data, prompt)

            return result

        except Exception as e:
            self.logger.error(f"Model execution failed: {e}")

            # Retry logic
            if retry_count < max_retries:
                retry_count += 1
                self.logger.warning(
                    f"Retrying execution (attempt "
                    f"{retry_count + 1}/{max_retries + 1})..."
                )
                print(
                    f"\n{Colors.BRIGHT_YELLOW}[!] Execution failed, "
                    f"retrying ({retry_count}/{max_retries})..."
                    f"{Colors.RESET}\n"
                )
                time.sleep(2)  # Brief delay before retry
                return self.run_model(
                    model_id, model_data, prompt, retry_count, max_retries
                )
            else:
                self.logger.error(
                    f"All retry attempts exhausted for {model_id}"
                )
                print(
                    f"\n{Colors.BRIGHT_RED}[X] Error: "
                    f"Model execution failed after "
                    f"{max_retries + 1} attempts{Colors.RESET}\n"
                )
                return None

    def run_llamacpp_model(self, model_data, prompt):
        """Run model using llama.cpp (WSL)"""
        self.logger.debug("Executing llama.cpp model")
        # Load system prompt if available
        system_prompt = ""
        if model_data['system_prompt']:
            prompt_file = self.system_prompts_dir / model_data['system_prompt']
            if prompt_file.exists():
                with open(prompt_file, 'r') as f:
                    system_prompt = f.read().strip()

        # Build command with 2025 optimal parameters
        special_flags = ' '.join(model_data['special_flags'])

        # Detect if already running in WSL
        is_wsl_env = (
            os.path.exists('/proc/version') and
            'microsoft' in open('/proc/version').read().lower()
        )
        wsl_prefix = "" if is_wsl_env else "wsl "

        cmd = f"""{wsl_prefix}bash -c "~/llama.cpp/build/bin/llama-cli \\
  -m '{model_data['path']}' \\
  -p '{prompt}' \\
  -ngl 999 \\
  -t 24 \\
  -b 512 \\
  -ub 512 \\
  -fa 1 \\
  --cache-type-k q8_0 \\
  --cache-type-v q8_0 \\
  --temp {model_data['temperature']} \\
  --top-p {model_data['top_p']} \\
  --top-k {model_data['top_k']} \\
  -c {model_data['context']} \\
  {special_flags} \\
  --mlock"
"""

        if system_prompt:
            cmd = cmd.replace(
                f"-p '{prompt}'",
                f"--system-prompt '{system_prompt}' -p '{prompt}'"
            )

        print(f"{Colors.BRIGHT_CYAN}Executing command:{Colors.RESET}")
        print(f"{Colors.DIM}{cmd}{Colors.RESET}\n")

        # Execute
        self.logger.debug("Executing llama.cpp command")
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True
        )
        if result.returncode != 0:
            self.logger.error(
                f"Model execution failed with "
                f"return code {result.returncode}"
            )
        else:
            self.logger.info("Successfully executed llama.cpp model")

    def run_mlx_model(self, model_data, prompt):
        """Run model using MLX (macOS)"""
        # Load system prompt if available
        system_prompt = ""
        if model_data['system_prompt']:
            prompt_file = self.system_prompts_dir / model_data['system_prompt']
            if prompt_file.exists():
                with open(prompt_file, 'r') as f:
                    system_prompt = f.read().strip()

        # Build MLX command
        cmd = f"""mlx_lm.generate \\
  --model {model_data['path']} \\
  --prompt "{prompt}" \\
  --max-tokens 2048 \\
  --temp {model_data['temperature']} \\
  --top-p {model_data['top_p']}"""

        if system_prompt:
            cmd = cmd.replace(
                f'--prompt "{prompt}"',
                f'--system-prompt "{system_prompt}" --prompt "{prompt}"'
            )

        print(f"{Colors.BRIGHT_CYAN}Executing command:{Colors.RESET}")
        print(f"{Colors.DIM}{cmd}{Colors.RESET}\n")

        # Execute
        subprocess.run(cmd, shell=True)

    def view_system_prompts(self):
        """Display system prompt examples"""
        sep1 = "╔" + "═" * 62 + "╗"
        sep2 = "╚" + "═" * 62 + "╝"
        print(
            f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}{sep1}{Colors.RESET}"
        )
        print(
            f"{Colors.BRIGHT_CYAN}{Colors.BOLD}"
            f"║  SYSTEM PROMPT GUIDE{Colors.RESET}"
        )
        print(
            f"{Colors.BRIGHT_CYAN}{Colors.BOLD}{sep2}{Colors.RESET}\n"
        )

        print(
            f"{Colors.BRIGHT_WHITE}"
            f"System prompts are stored in:{Colors.RESET}"
        )
        print(f"{Colors.CYAN}{self.system_prompts_dir}{Colors.RESET}\n")

        print(
            f"{Colors.BRIGHT_WHITE}"
            f"How to use system prompts:{Colors.RESET}\n"
        )
        print(
            f"{Colors.WHITE}1. System prompts are automatically "
            f"loaded by AI Router{Colors.RESET}"
        )
        print(
            f"{Colors.WHITE}2. Each model has an optimized "
            f"system prompt file{Colors.RESET}"
        )
        print(
            f"{Colors.WHITE}3. You can edit these files "
            f"to customize behavior{Colors.RESET}\n"
        )

        print(
            f"{Colors.BRIGHT_YELLOW}"
            f"Example system prompt structure:{Colors.RESET}\n"
        )
        print(
            f"{Colors.GREEN}You are an expert AI assistant "
            f"specialized in [domain].{Colors.RESET}"
        )
        print(
            f"{Colors.GREEN}Your responses should be:{Colors.RESET}"
        )
        print(
            f"{Colors.GREEN}- Accurate and well-researched{Colors.RESET}"
        )
        print(f"{Colors.GREEN}- Clear and concise{Colors.RESET}")
        print(
            f"{Colors.GREEN}- Formatted with proper code blocks "
            f"when relevant{Colors.RESET}\n"
        )

        print(
            f"{Colors.BRIGHT_MAGENTA}"
            f"Available system prompt files:{Colors.RESET}\n"
        )
        for model_id, model_data in self.models.items():
            if model_data['system_prompt']:
                print(
                    f"  {Colors.GREEN}[OK]{Colors.RESET} "
                    f"{model_data['system_prompt']}"
                )
            else:
                print(
                    f"  {Colors.RED}[X]{Colors.RESET} "
                    f"{model_id} (no system prompt support)"
                )
        print()

    def view_parameters_guide(self):
        """Display optimal parameters guide"""
        sep1 = "╔" + "═" * 62 + "╗"
        sep2 = "╚" + "═" * 62 + "╝"
        print(
            f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}{sep1}{Colors.RESET}"
        )
        print(
            f"{Colors.BRIGHT_CYAN}{Colors.BOLD}"
            f"║  OPTIMAL PARAMETERS GUIDE (2025 Research){Colors.RESET}"
        )
        print(
            f"{Colors.BRIGHT_CYAN}{Colors.BOLD}{sep2}{Colors.RESET}\n"
        )

        print(
            f"{Colors.BRIGHT_WHITE}"
            f"RTX 3090 (llama.cpp WSL):{Colors.RESET}\n"
        )
        print(
            f"{Colors.GREEN}-ngl 999{Colors.RESET}           "
            f"{Colors.WHITE}Full GPU offload (Aug 2025 default)"
            f"{Colors.RESET}"
        )
        print(
            f"{Colors.GREEN}-t 24{Colors.RESET}             "
            f"{Colors.WHITE}Use all CPU threads (Ryzen 9 5900X)"
            f"{Colors.RESET}"
        )
        print(
            f"{Colors.GREEN}-b 512{Colors.RESET}            "
            f"{Colors.WHITE}Minimum batch size (2025 research)"
            f"{Colors.RESET}"
        )
        print(
            f"{Colors.GREEN}-ub 512{Colors.RESET}           "
            f"{Colors.WHITE}Logical batch for prompt processing"
            f"{Colors.RESET}"
        )
        print(
            f"{Colors.GREEN}-fa 1{Colors.RESET}             "
            f"{Colors.WHITE}Flash Attention "
            f"(+20% speed, 50% memory){Colors.RESET}"
        )
        print(
            f"{Colors.GREEN}--cache-type-k q8_0{Colors.RESET}  "
            f"{Colors.WHITE}KV cache quantization (50% memory)"
            f"{Colors.RESET}"
        )
        print(
            f"{Colors.GREEN}--cache-type-v q8_0{Colors.RESET}  "
            f"{Colors.WHITE}KV cache quantization{Colors.RESET}"
        )
        print(
            f"{Colors.GREEN}--no-ppl{Colors.RESET}          "
            f"{Colors.WHITE}Skip perplexity (+15% speedup)"
            f"{Colors.RESET}"
        )
        print(
            f"{Colors.GREEN}--mlock{Colors.RESET}           "
            f"{Colors.WHITE}Lock model in RAM{Colors.RESET}\n"
        )

        print(
            f"{Colors.BRIGHT_WHITE}"
            f"MacBook M4 Pro (MLX):{Colors.RESET}\n"
        )
        print(
            f"{Colors.GREEN}--max-tokens 2048{Colors.RESET}  "
            f"{Colors.WHITE}Maximum generation length{Colors.RESET}"
        )
        print(
            f"{Colors.GREEN}--temp 0.7{Colors.RESET}        "
            f"{Colors.WHITE}Temperature (creativity){Colors.RESET}"
        )
        print(
            f"{Colors.GREEN}--top-p 0.9{Colors.RESET}       "
            f"{Colors.WHITE}Nucleus sampling{Colors.RESET}\n"
        )

        print(
            f"{Colors.BRIGHT_WHITE}Temperature Guide:{Colors.RESET}\n"
        )
        print(
            f"{Colors.CYAN}0.2-0.4{Colors.RESET}  "
            f"{Colors.WHITE}Technical docs, code, Q&A (conservative)"
            f"{Colors.RESET}"
        )
        print(
            f"{Colors.CYAN}0.5-0.9{Colors.RESET}  "
            f"{Colors.WHITE}Content creation, conversation (balanced)"
            f"{Colors.RESET}"
        )
        print(
            f"{Colors.CYAN}0.8-1.2+{Colors.RESET} "
            f"{Colors.WHITE}Creative writing, brainstorming"
            f"{Colors.RESET}\n"
        )

        print(f"{Colors.BRIGHT_YELLOW}CRITICAL Notes:{Colors.RESET}\n")
        print(
            f"{Colors.RED}[X]{Colors.RESET} {Colors.WHITE}"
            f"NEVER use temp 0 with Qwen models (causes loops)"
            f"{Colors.RESET}"
        )
        print(
            f"{Colors.RED}[X]{Colors.RESET} {Colors.WHITE}"
            f"NEVER use 'think step-by-step' with reasoning models"
            f"{Colors.RESET}"
        )
        print(
            f"{Colors.GREEN}[OK]{Colors.RESET} {Colors.WHITE}"
            f"ALWAYS use --jinja flag with Phi-4{Colors.RESET}"
        )
        print(
            f"{Colors.GREEN}[OK]{Colors.RESET} {Colors.WHITE}"
            f"ALWAYS use --jinja flag with Qwen3{Colors.RESET}"
        )
        print(
            f"{Colors.GREEN}[OK]{Colors.RESET} {Colors.WHITE}"
            f"WSL provides near-native Linux performance (within 1%)"
            f"{Colors.RESET}\n"
        )

    def view_documentation(self):
        """Display documentation guide menu"""
        docs_dir = self.models_dir

        # Define documentation files with priority (ONLY FILES THAT EXIST)
        docs = [
            # Frequently needed (top priority)
            ("HOW-TO-RUN-AI-ROUTER.md",
             "🚀 How to Run the AI Router",
             "Getting started, usage, troubleshooting"),
            ("BOT-PROJECT-QUICK-START.md",
             "Bot & Project Management",
             "Create bots and projects with custom configs"),
            ("SYSTEM-PROMPTS-QUICK-START.md",
             "📝 System Prompts Quick Start",
             "Using and customizing system prompts"),

            # Important reference
            ("COMPREHENSIVE-EVALUATION-FRAMEWORK-PROMPT.md",
             "📊 Evaluation Framework",
             "Testing and comparing models"),
            ("2025-RESEARCH-SUMMARY.md",
             "🔬 2025 Research Summary",
             "Latest research findings and best practices"),
            ("MACBOOK-M4-OPTIMIZATION-GUIDE.md",
             "💻 MacBook M4 Optimization",
             "Optimizing for Apple M4 hardware"),

            # Additional resources
            ("GITHUB-SETUP-GUIDE.md",
             "🐙 GitHub Setup Guide",
             "Setting up Git and GitHub"),
            ("README.md",
             "📖 Project README",
             "Complete project overview and setup"),
        ]

        # Filter to only files that actually exist
        existing_docs = []
        for filename, title, desc in docs:
            doc_path = docs_dir / filename
            if doc_path.exists():
                existing_docs.append((filename, title, desc))

        docs = existing_docs

        if not docs:
            print(
                f"\n{Colors.BRIGHT_RED}"
                f"No documentation files found!{Colors.RESET}\n"
            )
            input(
                f"{Colors.BRIGHT_YELLOW}"
                f"Press Enter to return...{Colors.RESET}"
            )
            return

        sep1 = "╔" + "═" * 62 + "╗"
        sep2 = "╚" + "═" * 62 + "╝"
        print(
            f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}{sep1}{Colors.RESET}"
        )
        print(
            f"{Colors.BRIGHT_CYAN}{Colors.BOLD}"
            f"║  📚 DOCUMENTATION GUIDES ({len(docs)} available)"
            f"{Colors.RESET}"
        )
        print(
            f"{Colors.BRIGHT_CYAN}{Colors.BOLD}{sep2}{Colors.RESET}\n"
        )

        # Display docs organized by priority
        # Top 3 are most frequently needed
        if len(docs) >= 1:
            print(
                f"{Colors.BRIGHT_WHITE}"
                f"⭐ Most Frequently Needed:{Colors.RESET}\n"
            )
            for idx in range(min(3, len(docs))):
                filename, title, desc = docs[idx]
                print(
                    f"{Colors.BRIGHT_GREEN}[{idx+1}]{Colors.RESET} "
                    f"{Colors.BRIGHT_WHITE}{title}{Colors.RESET}"
                )
                print(f"    {Colors.CYAN}{desc}{Colors.RESET}")
                print()

        # Next 3 are important reference
        if len(docs) > 3:
            print(
                f"{Colors.BRIGHT_WHITE}"
                f"📚 Important Reference:{Colors.RESET}\n"
            )
            for idx in range(3, min(6, len(docs))):
                filename, title, desc = docs[idx]
                print(
                    f"{Colors.BRIGHT_GREEN}[{idx+1}]{Colors.RESET} "
                    f"{Colors.WHITE}{title}{Colors.RESET}"
                )
                print(f"    {Colors.CYAN}{desc}{Colors.RESET}")
                print()

        # Remaining are additional resources
        if len(docs) > 6:
            print(
                f"{Colors.BRIGHT_WHITE}"
                f"📖 Additional Resources:{Colors.RESET}\n"
            )
            for idx in range(6, len(docs)):
                filename, title, desc = docs[idx]
                print(
                    f"{Colors.BRIGHT_GREEN}[{idx+1}]{Colors.RESET} "
                    f"{Colors.WHITE}{title}{Colors.RESET}"
                )
                print(f"    {Colors.CYAN}{desc}{Colors.RESET}")
                print()

        print(
            f"{Colors.BRIGHT_GREEN}[0]{Colors.RESET} "
            f"{Colors.WHITE}Return to main menu{Colors.RESET}\n"
        )

        choice = input(
            f"{Colors.BRIGHT_YELLOW}"
            f"Select documentation [0-{len(docs)}]: {Colors.RESET}"
        ).strip()

        if choice == "0":
            return

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(docs):
                filename, title, desc = docs[idx]
                doc_path = docs_dir / filename

                if doc_path.exists():
                    # Read and display the documentation
                    with open(doc_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    sep1 = "╔" + "═" * 62 + "╗"
                    sep2 = "╚" + "═" * 62 + "╝"
                    print(
                        f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}"
                        f"{sep1}{Colors.RESET}"
                    )
                    print(
                        f"{Colors.BRIGHT_CYAN}{Colors.BOLD}"
                        f"║  {title}{Colors.RESET}"
                    )
                    print(
                        f"{Colors.BRIGHT_CYAN}{Colors.BOLD}"
                        f"{sep2}{Colors.RESET}\n"
                    )

                    # Display content with pagination (first 50 lines)
                    lines = content.split('\n')
                    page_size = 50

                    for i in range(0, len(lines), page_size):
                        page_lines = lines[i:i+page_size]
                        print('\n'.join(page_lines))

                        if i + page_size < len(lines):
                            cont = input(
                                f"\n{Colors.BRIGHT_YELLOW}"
                                f"Press Enter to continue, 'q' to quit: "
                                f"{Colors.RESET}"
                            ).strip().lower()
                            if cont == 'q':
                                break
                        else:
                            print(
                                f"\n{Colors.BRIGHT_GREEN}"
                                f"[End of document]{Colors.RESET}"
                            )

                    input(
                        f"\n{Colors.BRIGHT_YELLOW}"
                        f"Press Enter to return to menu...{Colors.RESET}"
                    )
                else:
                    print(
                        f"{Colors.BRIGHT_RED}"
                        f"Documentation file not found: {filename}"
                        f"{Colors.RESET}"
                    )
                    input(
                        f"\n{Colors.BRIGHT_YELLOW}"
                        f"Press Enter to continue...{Colors.RESET}"
                    )
            else:
                print(
                    f"{Colors.BRIGHT_RED}"
                    f"[X] Invalid selection.{Colors.RESET}"
                )
                print(
                    f"{Colors.BRIGHT_YELLOW}"
                    f"Please enter a valid option number.{Colors.RESET}"
                )
        except ValueError:
            print(
                f"{Colors.BRIGHT_RED}[X] Invalid input.{Colors.RESET}"
            )
            print(
                f"{Colors.BRIGHT_YELLOW}"
                f"Please enter a valid number from the menu.{Colors.RESET}"
            )

    def show_machine_info(self):
        """Display detected machine information"""
        machine_id = detect_machine()
        config_path = Path(f"configs/{machine_id}/ai-router-config.json")

        print(f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}")
        print("=" * 64)
        print("                    MACHINE DETECTION INFO")
        print("=" * 64)
        print(Colors.RESET)

        print(
            f"\n{Colors.BRIGHT_WHITE}Detected Machine:{Colors.RESET}"
        )
        print(f"  {Colors.BRIGHT_GREEN}{machine_id}{Colors.RESET}")

        print(
            f"\n{Colors.BRIGHT_WHITE}Configuration File:{Colors.RESET}"
        )
        if config_path.exists():
            print(
                f"  {Colors.GREEN}{config_path.absolute()}{Colors.RESET}"
            )
        else:
            print(
                f"  {Colors.RED}[NOT FOUND] {config_path.absolute()}"
                f"{Colors.RESET}"
            )

        print(f"\n{Colors.BRIGHT_WHITE}Platform:{Colors.RESET}")
        print(f"  {Colors.CYAN}{self.platform}{Colors.RESET}")

        print(f"\n{Colors.BRIGHT_WHITE}Available Models:{Colors.RESET}")
        print(f"  {Colors.CYAN}{len(self.models)} models{Colors.RESET}")

        print()

    def validate_config_cmd(self):
        """Validate the configuration for current machine"""
        if ConfigValidator is None:
            print(
                f"{Colors.BRIGHT_RED}[ERROR] Config validator not "
                f"available{Colors.RESET}"
            )
            return False

        machine_id = detect_machine()
        config_path = Path(f"configs/{machine_id}/ai-router-config.json")

        print(f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}")
        print("=" * 64)
        print("                 CONFIGURATION VALIDATION")
        print("=" * 64)
        print(Colors.RESET)

        validator = ConfigValidator()
        is_valid, errors = validator.validate_config(config_path)

        if is_valid:
            print(
                f"{Colors.GREEN}[OK] Configuration is valid!{Colors.RESET}"
            )
        else:
            print(
                f"{Colors.RED}[ERROR] Configuration has issues:"
                f"{Colors.RESET}\n"
            )
            for idx, error in enumerate(errors, 1):
                print(f"{Colors.RED}  [{idx}] {error}{Colors.RESET}")

        print()
        return is_valid

    def search_models(self, query: str):
        """Search models by keyword"""
        query_lower = query.lower()
        results = []

        for model_id, model_data in self.models.items():
            name_match = query_lower in model_data['name'].lower()
            use_case_match = query_lower in model_data['use_case'].lower()
            notes_match = (
                model_data.get('notes')
                and query_lower in model_data['notes'].lower()
            )

            if name_match or use_case_match or notes_match:
                results.append((model_id, model_data))

        return results

    def show_search_results(self, query: str):
        """Display search results for models"""
        results = self.search_models(query)

        print(f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}")
        print("=" * 64)
        print(f"                 SEARCH RESULTS FOR: {query.upper()}")
        print("=" * 64)
        print(Colors.RESET)

        if not results:
            print(
                f"{Colors.YELLOW}No models found matching '{query}'"
                f"{Colors.RESET}\n"
            )
            return

        print(
            f"{Colors.BRIGHT_WHITE}Found {len(results)} matching model(s):"
            f"{Colors.RESET}\n"
        )

        for model_id, model_data in results:
            print(
                f"{Colors.BRIGHT_GREEN}[{model_id}]{Colors.RESET}"
            )
            print(
                f"  {Colors.WHITE}Name: {model_data['name']}{Colors.RESET}"
            )
            print(
                f"  {Colors.CYAN}Use case: {model_data['use_case']}"
                f"{Colors.RESET}"
            )
            print(
                f"  {Colors.GREEN}{model_data['size']} | "
                f"{model_data['speed']}{Colors.RESET}\n"
            )

    def show_config(self):
        """Display current machine configuration"""
        machine_id = detect_machine()
        config_path = Path(f"configs/{machine_id}/ai-router-config.json")

        print(f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}")
        print("=" * 64)
        print("              MACHINE CONFIGURATION")
        print("=" * 64)
        print(Colors.RESET)

        if not config_path.exists():
            print(
                f"{Colors.BRIGHT_RED}[ERROR] Configuration file not "
                f"found:{Colors.RESET}"
            )
            print(f"  {config_path.absolute()}\n")
            return

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            print(
                f"\n{Colors.BRIGHT_WHITE}Machine:{Colors.RESET}"
            )
            machine = config.get('machine', {})
            print(f"  ID: {Colors.CYAN}{machine.get('id')}{Colors.RESET}")
            print(
                f"  Name: {Colors.CYAN}{machine.get('name')}{Colors.RESET}"
            )
            print(
                f"  Specs: {Colors.CYAN}{machine.get('specs')}{Colors.RESET}"
            )

            print(
                f"\n{Colors.BRIGHT_WHITE}Performance Settings:{Colors.RESET}"
            )
            perf = config.get('performance', {})
            print(
                f"  Temperature: {Colors.GREEN}{perf.get('temperature')}"
                f"{Colors.RESET}"
            )
            print(
                f"  Top-P: {Colors.GREEN}{perf.get('top_p')}{Colors.RESET}"
            )
            print(
                f"  Batch Size: {Colors.GREEN}{perf.get('batch_size')}"
                f"{Colors.RESET}"
            )

            print(
                f"\n{Colors.BRIGHT_WHITE}Inference Settings:{Colors.RESET}"
            )
            infer = config.get('inference', {})
            print(
                f"  Backend: {Colors.BLUE}{infer.get('backend')}"
                f"{Colors.RESET}"
            )
            print(
                f"  Device: {Colors.BLUE}{infer.get('device')}{Colors.RESET}"
            )
            print(
                f"  Data Type: {Colors.BLUE}{infer.get('dtype')}"
                f"{Colors.RESET}"
            )

            print()

        except Exception as e:
            print(
                f"{Colors.BRIGHT_RED}[ERROR] Failed to read config: "
                f"{e}{Colors.RESET}\n"
            )


def create_parser():
    """Create and configure argument parser"""
    parser = argparse.ArgumentParser(
        prog='ai-router',
        description='AI Router - Intelligent Model Selection and Execution CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ai-router.py                              Launch interactive mode
  python ai-router.py run --model qwen3-coder-30b  Run model non-interactively
  python ai-router.py models search coding         Search for coding models
  python ai-router.py config show                  Display machine config
  python ai-router.py machine detect               Show detected machine info
  python ai-router.py validate                     Validate configuration

For more information, visit the documentation guides in interactive mode."""
    )

    subparsers = parser.add_subparsers(
        dest='command',
        help='Available commands'
    )

    # Run command
    run_parser = subparsers.add_parser(
        'run',
        help='Run a model with given prompt'
    )
    run_parser.add_argument(
        '--model',
        required=True,
        help='Model ID to run (e.g., qwen3-coder-30b)'
    )
    run_parser.add_argument(
        '--prompt',
        help='Prompt text (interactive if not provided)'
    )

    # Models subcommand
    models_parser = subparsers.add_parser(
        'models',
        help='Model management commands'
    )
    models_subparsers = models_parser.add_subparsers(
        dest='models_cmd',
        help='Models commands'
    )

    # models list
    models_subparsers.add_parser(
        'list',
        help='List all available models'
    )

    # models search
    search_parser = models_subparsers.add_parser(
        'search',
        help='Search models by keyword'
    )
    search_parser.add_argument(
        'query',
        help='Search query (e.g., "coding", "reasoning")'
    )

    # Config command
    config_parser = subparsers.add_parser(
        'config',
        help='Configuration management'
    )
    config_subparsers = config_parser.add_subparsers(
        dest='config_cmd',
        help='Config commands'
    )
    config_subparsers.add_parser(
        'show',
        help='Show current machine configuration'
    )

    # Machine command
    machine_parser = subparsers.add_parser(
        'machine',
        help='Machine information'
    )
    machine_subparsers = machine_parser.add_subparsers(
        dest='machine_cmd',
        help='Machine commands'
    )
    machine_subparsers.add_parser(
        'detect',
        help='Show detected machine and config location'
    )

    # Validate command
    subparsers.add_parser(
        'validate',
        help='Validate current machine configuration'
    )

    return parser


def main():
    """Main entry point with argparse-based CLI"""
    try:
        # Initialize trace ID for this session
        set_trace_id()

        # Initialize router
        router = AIRouter()
        machine_id = detect_machine()

        # Parse arguments
        parser = create_parser()
        args = parser.parse_args()

        # Handle commands
        if args.command is None:
            # No command specified - show banner and machine info,
            # then launch interactive mode
            router.print_banner()
            print(f"{Colors.BRIGHT_GREEN}Detected: {machine_id}{Colors.RESET}")
            print(
                f"{Colors.BRIGHT_GREEN}Config: "
                f"configs/{machine_id}/ai-router-config.json{Colors.RESET}\n"
            )
            router.interactive_mode()

        elif args.command == 'run':
            # Run a model
            router.print_banner()
            if args.model not in router.models:
                print(
                    f"{Colors.BRIGHT_RED}[ERROR] Unknown model: "
                    f"{args.model}{Colors.RESET}"
                )
                print(
                    f"{Colors.YELLOW}Use 'python ai-router.py models list' "
                    f"to see available models.{Colors.RESET}\n"
                )
                sys.exit(1)

            model_data = router.models[args.model]

            if args.prompt:
                prompt = args.prompt
            else:
                prompt = input(
                    f"\n{Colors.BRIGHT_CYAN}Enter your prompt: "
                    f"{Colors.RESET}"
                ).strip()

            router.run_model(args.model, model_data, prompt)

        elif args.command == 'models':
            router.print_banner()
            if args.models_cmd == 'list':
                router.list_models()
            elif args.models_cmd == 'search':
                router.show_search_results(args.query)
            else:
                print(f"{Colors.YELLOW}Use 'python ai-router.py models "
                      f"--help' for usage.{Colors.RESET}\n")

        elif args.command == 'config':
            router.print_banner()
            if args.config_cmd == 'show':
                router.show_config()
            else:
                print(f"{Colors.YELLOW}Use 'python ai-router.py config "
                      f"--help' for usage.{Colors.RESET}\n")

        elif args.command == 'machine':
            router.print_banner()
            if args.machine_cmd == 'detect':
                router.show_machine_info()
            else:
                print(f"{Colors.YELLOW}Use 'python ai-router.py machine "
                      f"--help' for usage.{Colors.RESET}\n")

        elif args.command == 'validate':
            router.print_banner()
            is_valid = router.validate_config_cmd()
            sys.exit(0 if is_valid else 1)

        else:
            parser.print_help()

    except KeyboardInterrupt:
        print(
            f"\n\n{Colors.BRIGHT_YELLOW}"
            f"Interrupted by user. Goodbye!{Colors.RESET}\n"
        )
        sys.exit(0)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print("\n[X] Error: An unexpected error occurred")
        print(f"Details: {str(e)[:200]}\n")
        print("Troubleshooting Steps:")
        print("  1. Check Python version: python --version")
        print("  2. Verify dependencies: pip list")
        print("  3. Check WSL status: wsl --status")
        print("  4. Try reinstalling: pip install -r requirements.txt\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
