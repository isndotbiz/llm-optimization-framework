#!/usr/bin/env python3
"""
AI Router - Intelligent Model Selection and Execution CLI
Optimized for RTX 3090 (WSL) and MacBook M4 Pro
Based on 2025 Research Findings (Sep-Nov 2025)
"""

import os
import sys
import subprocess
import json
import platform
from pathlib import Path
from logging_config import setup_logging

def is_wsl():
    """Detect if running in WSL (Windows Subsystem for Linux)"""
    try:
        with open('/proc/version', 'r') as f:
            return 'microsoft' in f.read().lower()
    except:
        return False

# Color codes for terminal output
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


class ModelDatabase:
    """Comprehensive model database with 2025 research-optimized settings"""

    # RTX 3090 Models (WSL)
    RTX3090_MODELS = {
        "qwen3-coder-30b": {
            "name": "Qwen3 Coder 30B Q4_K_M",
            "path": "/mnt/d/models/organized/Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf",
            "size": "18GB",
            "speed": "25-35 tok/sec",
            "use_case": "Advanced coding, code review, architecture design",
            "temperature": 0.7,
            "top_p": 0.8,
            "top_k": 20,
            "context": 32768,
            "special_flags": ["--jinja"],
            "system_prompt": "system-prompt-qwen3-coder-30b.txt",
            "notes": "CRITICAL: Never use temp 0 (causes endless loops). Use enable_thinking for reasoning.",
            "framework": "llama.cpp"
        },
        "phi4-14b": {
            "name": "Phi-4 Reasoning Plus 14B Q6_K",
            "path": "/mnt/d/models/organized/microsoft_Phi-4-reasoning-plus-Q6_K.gguf",
            "size": "12GB",
            "speed": "35-55 tok/sec",
            "use_case": "Math, reasoning, STEM, logical analysis",
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "context": 16384,
            "special_flags": ["--jinja"],
            "system_prompt": "system-prompt-phi4-14b.txt",
            "notes": "CRITICAL: Requires --jinja flag. DO NOT use 'think step-by-step' prompts.",
            "framework": "llama.cpp"
        },
        "gemma3-27b": {
            "name": "Gemma 3 27B Q2_K (Abliterated)",
            "path": "/mnt/d/models/organized/mlabonne_gemma-3-27b-it-abliterated-Q2_K.gguf",
            "size": "10GB",
            "speed": "25-40 tok/sec",
            "use_case": "Uncensored chat, creative writing, research",
            "temperature": 0.9,
            "top_p": 0.9,
            "top_k": 40,
            "context": 128000,
            "special_flags": [],
            "system_prompt": None,
            "notes": "NO system prompt support. 128K context. Uncensored/abliterated variant.",
            "framework": "llama.cpp"
        },
        "ministral-3-14b": {
            "name": "Ministral-3 14B Reasoning Q5_K_M",
            "path": "/mnt/d/models/organized/Ministral-3-14B-Reasoning-2512-Q5_K_M.gguf",
            "size": "9GB",
            "speed": "35-50 tok/sec",
            "use_case": "Complex reasoning, problem solving, analysis",
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "context": 262144,
            "special_flags": [],
            "system_prompt": "system-prompt-ministral-3-14b.txt",
            "notes": "256K context window. Excellent for long-context reasoning.",
            "framework": "llama.cpp"
        },
        "deepseek-r1-14b": {
            "name": "DeepSeek R1 Distill Qwen 14B Q5_K_M",
            "path": "/mnt/d/models/organized/DeepSeek-R1-Distill-Qwen-14B-Q5_K_M.gguf",
            "size": "10GB",
            "speed": "30-50 tok/sec",
            "use_case": "Advanced reasoning, research, complex analysis",
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "context": 32768,
            "special_flags": [],
            "system_prompt": "system-prompt-deepseek-r1.txt",
            "notes": "DeepSeek R1 distilled to Qwen. Excellent reasoning capabilities.",
            "framework": "llama.cpp"
        },
        "llama33-70b": {
            "name": "Llama 3.3 70B Instruct IQ2_S (Abliterated)",
            "path": "/mnt/d/models/organized/Llama-3.3-70B-Instruct-abliterated-IQ2_S.gguf",
            "size": "21GB",
            "speed": "15-25 tok/sec",
            "use_case": "Large-scale reasoning, research, uncensored tasks",
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "context": 131072,
            "special_flags": [],
            "system_prompt": "system-prompt-llama33-70b.txt",
            "notes": "Largest model available. Excellent for complex tasks. Uncensored.",
            "framework": "llama.cpp"
        },
        "dolphin-llama31-8b": {
            "name": "Dolphin 3.0 Llama 3.1 8B Q6_K",
            "path": "/mnt/d/models/organized/Dolphin3.0-Llama3.1-8B-Q6_K.gguf",
            "size": "6GB",
            "speed": "45-65 tok/sec",
            "use_case": "Fast general tasks, uncensored chat, quick assistance",
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "context": 32768,
            "special_flags": [],
            "system_prompt": "system-prompt-dolphin-8b.txt",
            "notes": "Fastest model. Uncensored variant of Llama 3.1 8B.",
            "framework": "llama.cpp"
        },
        "dolphin-mistral-24b": {
            "name": "Dolphin Mistral 24B Venice Q4_K_M",
            "path": "/mnt/d/models/organized/cognitivecomputations_Dolphin-Mistral-24B-Venice-Edition-Q4_K_M.gguf",
            "size": "14GB",
            "speed": "25-40 tok/sec",
            "use_case": "Uncensored chat, creative tasks, roleplay",
            "temperature": 0.8,
            "top_p": 0.9,
            "top_k": 40,
            "context": 32768,
            "special_flags": [],
            "system_prompt": None,
            "notes": "Venice Edition: Completely uncensored. No system prompt support.",
            "framework": "llama.cpp"
        },
        "wizard-vicuna-13b": {
            "name": "Wizard Vicuna 13B Uncensored Q4_0",
            "path": "/mnt/d/models/organized/Wizard-Vicuna-13B-Uncensored-Q4_0.gguf",
            "size": "7GB",
            "speed": "35-50 tok/sec",
            "use_case": "General uncensored chat, creative writing",
            "temperature": 0.8,
            "top_p": 0.9,
            "top_k": 40,
            "context": 8192,
            "special_flags": [],
            "system_prompt": "system-prompt-wizard-vicuna.txt",
            "notes": "Classic uncensored model. Smaller context window.",
            "framework": "llama.cpp"
        }
    }

    # MacBook M4 Pro Models (MLX)
    M4_MODELS = {
        "qwen25-14b-mlx": {
            "name": "Qwen2.5 14B Instruct Q5_K_M (MLX)",
            "path": "~/models/qwen25-14b",
            "size": "11GB",
            "speed": "50-70 tok/sec",
            "use_case": "General purpose, research, chat",
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "context": 32768,
            "special_flags": [],
            "system_prompt": "system-prompt-qwen25-14b.txt",
            "notes": "Best daily driver for M4. Use MLX for 2-3x speedup vs llama.cpp.",
            "framework": "mlx"
        },
        "qwen25-coder-14b-mlx": {
            "name": "Qwen2.5 Coder 14B Q4_K_M (MLX)",
            "path": "~/models/qwen25-coder-14b",
            "size": "8GB",
            "speed": "50-75 tok/sec",
            "use_case": "Coding, debugging, technical tasks",
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "context": 32768,
            "special_flags": [],
            "system_prompt": "system-prompt-qwen25-coder-14b.txt",
            "notes": "Best coding model for M4.",
            "framework": "mlx"
        },
        "phi4-14b-mlx": {
            "name": "Phi-4 14B Q6_K (MLX)",
            "path": "~/models/phi4-14b",
            "size": "12GB",
            "speed": "60-75 tok/sec",
            "use_case": "Math, reasoning, STEM tasks",
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "context": 16384,
            "special_flags": [],
            "system_prompt": "system-prompt-phi4-14b.txt",
            "notes": "Excellent for reasoning on M4.",
            "framework": "mlx"
        },
        "gemma3-9b-mlx": {
            "name": "Gemma-3 9B Q6_K (MLX)",
            "path": "~/models/gemma3-9b",
            "size": "8GB",
            "speed": "85-110 tok/sec",
            "use_case": "Fast responses, chat, general queries",
            "temperature": 0.9,
            "top_p": 0.9,
            "top_k": 40,
            "context": 128000,
            "special_flags": [],
            "system_prompt": None,
            "notes": "Speed champion on M4. NO system prompt support.",
            "framework": "mlx"
        }
    }

    @classmethod
    def get_platform_models(cls):
        """Return models appropriate for current platform"""
        system = platform.system()
        if system == "Darwin":  # macOS
            return cls.M4_MODELS
        else:  # Windows/WSL - RTX 3090
            return cls.RTX3090_MODELS

    @classmethod
    def detect_use_case(cls, prompt_text):
        """Intelligently detect use case from prompt"""
        prompt_lower = prompt_text.lower()

        # Coding keywords
        coding_keywords = ['code', 'function', 'class', 'programming', 'debug', 'error',
                          'python', 'javascript', 'java', 'c++', 'rust', 'implement',
                          'refactor', 'algorithm', 'api', 'script', 'bug']

        # Math/reasoning keywords
        reasoning_keywords = ['calculate', 'prove', 'theorem', 'math', 'equation',
                             'logic', 'reasoning', 'solve', 'problem', 'analyze',
                             'deduce', 'infer', 'probability', 'statistics']

        # Creative keywords
        creative_keywords = ['story', 'poem', 'creative', 'write', 'fiction',
                            'narrative', 'character', 'plot', 'imagine']

        # Research keywords
        research_keywords = ['research', 'analyze', 'explain', 'summary', 'what is',
                            'how does', 'why', 'compare', 'contrast']

        if any(kw in prompt_lower for kw in coding_keywords):
            return "coding"
        elif any(kw in prompt_lower for kw in reasoning_keywords):
            return "reasoning"
        elif any(kw in prompt_lower for kw in creative_keywords):
            return "creative"
        elif any(kw in prompt_lower for kw in research_keywords):
            return "research"
        else:
            return "general"

    @classmethod
    def recommend_model(cls, use_case, platform_models):
        """Recommend best model for use case"""
        recommendations = {
            "coding": ["qwen3-coder-30b", "qwen25-coder-14b-mlx"],
            "reasoning": ["phi4-14b", "ministral-3-14b", "phi4-14b-mlx"],
            "creative": ["gemma3-27b", "gemma3-9b-mlx"],
            "research": ["qwen3-14b", "qwen25-14b", "qwen25-14b-mlx"],
            "general": ["qwen25-14b", "qwen3-14b", "qwen25-14b-mlx"]
        }

        for model_id in recommendations.get(use_case, []):
            if model_id in platform_models:
                return model_id, platform_models[model_id]

        # Fallback to first available model
        return list(platform_models.items())[0]


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

        # Initialize logging
        self.logger = setup_logging(self.models_dir)
        self.logger.info(f"AI Router initialized on {self.platform}")

    def _validate_resources_for_model(self, model_data):
        """Validate that system has sufficient resources to run the model"""
        try:
            # Check if WSL is available for llama.cpp models
            if model_data['framework'] == 'llama.cpp':
                if self.platform == "Windows":
                    # Quick WSL check
                    result = subprocess.run(['wsl', '--status'], capture_output=True, timeout=5)
                    if result.returncode != 0:
                        self.logger.warning("WSL not available or not running")
                        return False

            # For now, assume resources are sufficient if WSL check passes
            # Could add memory checks here in the future
            return True

        except subprocess.TimeoutExpired:
            self.logger.warning("WSL status check timed out")
            return True  # Assume OK if timeout (WSL might be slow but working)
        except Exception as e:
            self.logger.warning(f"Resource validation error: {e}")
            return True  # Be permissive on validation errors

    def _get_fallback_model(self, model_id):
        """Get a smaller fallback model if primary model fails"""
        fallback_map = {
            "qwen3-coder-30b": "dolphin-llama31-8b",      # 18GB -> 6GB
            "llama33-70b": "ministral-3-14b",              # 21GB -> 9GB
            "phi4-14b": "dolphin-llama31-8b",              # 12GB -> 6GB
            "dolphin-mistral-24b": "wizard-vicuna-13b",    # 14GB -> 7GB
            "gemma3-27b": "dolphin-llama31-8b",            # 10GB -> 6GB
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
        print("                                                                                ")
        print("                         AI ROUTER CLI v1.0                                    ")
        print("                                                                                ")
        print("           Intelligent Model Selection & Execution Framework                   ")
        print("              Based on 2025 Research (Sep-Nov 2025)                            ")
        print("                                                                                ")
        print("=" * 84)
        print(Colors.RESET)

        # Platform info
        if self.platform == "Darwin":
            platform_name = f"{Colors.BRIGHT_GREEN}MacBook M4 Pro (MLX Optimized){Colors.RESET}"
        else:
            platform_name = f"{Colors.BRIGHT_YELLOW}RTX 3090 (WSL Optimized){Colors.RESET}"

        print(f"\n{Colors.BRIGHT_WHITE}Platform: {platform_name}")
        print(f"{Colors.BRIGHT_WHITE}Available Models: {Colors.BRIGHT_CYAN}{len(self.models)}{Colors.RESET}")
        print()

    def print_model_info(self, model_id, model_data):
        """Display detailed model information"""
        print(f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}{'=' * 64}{Colors.RESET}")
        print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}  MODEL INFORMATION{Colors.RESET}")
        print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}{'=' * 64}{Colors.RESET}\n")

        print(f"{Colors.BRIGHT_WHITE}Name:          {Colors.BRIGHT_GREEN}{model_data['name']}{Colors.RESET}")
        print(f"{Colors.BRIGHT_WHITE}Model ID:      {Colors.BRIGHT_YELLOW}{model_id}{Colors.RESET}")
        print(f"{Colors.BRIGHT_WHITE}Size:          {Colors.BRIGHT_MAGENTA}{model_data['size']}{Colors.RESET}")
        print(f"{Colors.BRIGHT_WHITE}Speed:         {Colors.BRIGHT_CYAN}{model_data['speed']}{Colors.RESET}")
        print(f"{Colors.BRIGHT_WHITE}Framework:     {Colors.BRIGHT_BLUE}{model_data['framework'].upper()}{Colors.RESET}")
        print(f"{Colors.BRIGHT_WHITE}Use Case:      {Colors.YELLOW}{model_data['use_case']}{Colors.RESET}")
        print(f"{Colors.BRIGHT_WHITE}Context:       {Colors.CYAN}{model_data['context']:,} tokens{Colors.RESET}")

        print(f"\n{Colors.BRIGHT_WHITE}Optimal Parameters:{Colors.RESET}")
        print(f"  {Colors.WHITE}Temperature:   {Colors.GREEN}{model_data['temperature']}{Colors.RESET}")
        print(f"  {Colors.WHITE}Top-P:         {Colors.GREEN}{model_data['top_p']}{Colors.RESET}")
        print(f"  {Colors.WHITE}Top-K:         {Colors.GREEN}{model_data['top_k']}{Colors.RESET}")

        if model_data['special_flags']:
            print(f"\n{Colors.BRIGHT_YELLOW}Special Flags: {Colors.YELLOW}{' '.join(model_data['special_flags'])}{Colors.RESET}")

        if model_data['system_prompt']:
            print(f"\n{Colors.BRIGHT_GREEN}System Prompt: {Colors.GREEN}{model_data['system_prompt']}{Colors.RESET}")
        else:
            print(f"\n{Colors.BRIGHT_RED}[!] NO system prompt support{Colors.RESET}")

        if model_data['notes']:
            print(f"\n{Colors.BRIGHT_MAGENTA}Notes:{Colors.RESET}")
            print(f"  {Colors.MAGENTA}{model_data['notes']}{Colors.RESET}")

        print()

    def list_models(self):
        """List all available models"""
        print(f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}╔══════════════════════════════════════════════════════════════╗{Colors.RESET}")
        print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}║  AVAILABLE MODELS{Colors.RESET}")
        print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}╚══════════════════════════════════════════════════════════════╝{Colors.RESET}\n")

        for idx, (model_id, model_data) in enumerate(self.models.items(), 1):
            print(f"{Colors.BRIGHT_YELLOW}[{idx}]{Colors.RESET} {Colors.BRIGHT_WHITE}{model_id}{Colors.RESET}")
            print(f"    {Colors.WHITE}{model_data['name']}{Colors.RESET}")
            print(f"    {Colors.CYAN}Use case: {model_data['use_case']}{Colors.RESET}")
            print(f"    {Colors.GREEN}{model_data['size']} | {model_data['speed']}{Colors.RESET}")
            print()

    def interactive_mode(self):
        """Interactive model selection"""
        self.print_banner()

        while True:
            print(f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}{'=' * 63}{Colors.RESET}")
            print(f"{Colors.BRIGHT_WHITE}What would you like to do?{Colors.RESET}\n")
            print(f"{Colors.BRIGHT_GREEN}[1]{Colors.RESET} Auto-select model based on prompt")
            print(f"{Colors.BRIGHT_GREEN}[2]{Colors.RESET} Manually select model")
            print(f"{Colors.BRIGHT_GREEN}[3]{Colors.RESET} List all available models")
            print(f"{Colors.BRIGHT_GREEN}[4]{Colors.RESET} View system prompt examples")
            print(f"{Colors.BRIGHT_GREEN}[5]{Colors.RESET} View optimal parameters guide")
            print(f"{Colors.BRIGHT_GREEN}[6]{Colors.RESET} View documentation guides")
            print(f"{Colors.BRIGHT_GREEN}[7]{Colors.RESET} Exit")
            print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}{'=' * 63}{Colors.RESET}")

            choice = input(f"\n{Colors.BRIGHT_YELLOW}Enter choice [1-7]: {Colors.RESET}").strip()

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
                print(f"\n{Colors.BRIGHT_GREEN}Goodbye!{Colors.RESET}\n")
                sys.exit(0)
            else:
                print(f"{Colors.BRIGHT_RED}Invalid choice. Please try again.{Colors.RESET}")

    def auto_select_mode(self):
        """Auto-select model based on prompt"""
        print(f"\n{Colors.BRIGHT_CYAN}Enter your prompt (or 'back' to return):{Colors.RESET}")
        prompt = input(f"{Colors.YELLOW}> {Colors.RESET}").strip()

        if prompt.lower() == 'back':
            return

        # Detect use case
        use_case = ModelDatabase.detect_use_case(prompt)
        print(f"\n{Colors.BRIGHT_MAGENTA}Detected use case: {Colors.BRIGHT_WHITE}{use_case.upper()}{Colors.RESET}")

        # Recommend model
        model_id, model_data = ModelDatabase.recommend_model(use_case, self.models)
        print(f"{Colors.BRIGHT_GREEN}Recommended model: {Colors.BRIGHT_WHITE}{model_data['name']}{Colors.RESET}")

        # Show model info
        self.print_model_info(model_id, model_data)

        # Ask if user wants to run
        confirm = input(f"\n{Colors.BRIGHT_YELLOW}Run this model? [Y/n]: {Colors.RESET}").strip().lower()
        if confirm in ['', 'y', 'yes']:
            self.run_model(model_id, model_data, prompt)

    def manual_select_mode(self):
        """Manually select model"""
        self.list_models()

        model_ids = list(self.models.keys())
        choice = input(f"\n{Colors.BRIGHT_YELLOW}Select model number (or 'back'): {Colors.RESET}").strip()

        if choice.lower() == 'back':
            return

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(model_ids):
                model_id = model_ids[idx]
                model_data = self.models[model_id]

                self.print_model_info(model_id, model_data)

                prompt = input(f"\n{Colors.BRIGHT_CYAN}Enter your prompt: {Colors.RESET}").strip()
                self.run_model(model_id, model_data, prompt)
            else:
                print(f"{Colors.BRIGHT_RED}[X] Invalid model number.{Colors.RESET}")
                print(f"{Colors.BRIGHT_YELLOW}Please enter a valid number from the list above.{Colors.RESET}")
        except ValueError:
            print(f"{Colors.BRIGHT_RED}[X] Invalid input.{Colors.RESET}")
            print(f"{Colors.BRIGHT_YELLOW}Please enter a valid number.{Colors.RESET}")

    def run_model(self, model_id, model_data, prompt, retry_count=0, max_retries=2):
        """Execute the model with optimal parameters and retry logic"""
        self.logger.info(f"Starting model execution: {model_id} ({model_data['name']})")

        # Validate resources before execution
        if not self._validate_resources_for_model(model_data):
            self.logger.error(f"Insufficient resources for model {model_id}")
            print(f"\n{Colors.BRIGHT_RED}[X] Error: Insufficient system resources{Colors.RESET}")
            print(f"{Colors.BRIGHT_YELLOW}Model {model_data['name']} requires:{Colors.RESET}")
            print(f"{Colors.YELLOW}  - Available RAM: ~{model_data['size']} free{Colors.RESET}")
            print(f"{Colors.YELLOW}  - WSL must be running (for llama.cpp models){Colors.RESET}\n")

            # Try fallback to smaller model
            fallback_id = self._get_fallback_model(model_id)
            if fallback_id and retry_count == 0:
                print(f"{Colors.BRIGHT_CYAN}→ Trying fallback model: {self.models[fallback_id]['name']}{Colors.RESET}\n")
                return self.run_model(fallback_id, self.models[fallback_id], prompt, retry_count=1)
            return None

        print(f"\n{Colors.BRIGHT_GREEN}{Colors.BOLD}Launching {model_data['name']}...{Colors.RESET}\n")

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
                self.logger.warning(f"Retrying execution (attempt {retry_count + 1}/{max_retries + 1})...")
                print(f"\n{Colors.BRIGHT_YELLOW}[!] Execution failed, retrying ({retry_count}/{max_retries})...{Colors.RESET}\n")
                time.sleep(2)  # Brief delay before retry
                return self.run_model(model_id, model_data, prompt, retry_count, max_retries)
            else:
                self.logger.error(f"All retry attempts exhausted for {model_id}")
                print(f"\n{Colors.BRIGHT_RED}[X] Error: Model execution failed after {max_retries + 1} attempts{Colors.RESET}\n")
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

        cmd = f"""wsl bash -c "~/llama.cpp/build/bin/llama-cli \\
  -m '{model_data['path']}' \\
  -p '{prompt}' \\
  -ngl 999 \\
  -t 24 \\
  -b 512 \\
  -ub 512 \\
  -fa 1 \\
  --cache-type-k q8_0 \\
  --cache-type-v q8_0 \\
  --no-ppl \\
  --temp {model_data['temperature']} \\
  --top-p {model_data['top_p']} \\
  --top-k {model_data['top_k']} \\
  -c {model_data['context']} \\
  {special_flags} \\
  --mlock"
"""

        if system_prompt:
            cmd = cmd.replace(f"-p '{prompt}'", f"--system-prompt '{system_prompt}' -p '{prompt}'")

        print(f"{Colors.BRIGHT_CYAN}Executing command:{Colors.RESET}")
        print(f"{Colors.DIM}{cmd}{Colors.RESET}\n")

        # Execute
        self.logger.debug("Executing llama.cpp command")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            self.logger.error(f"Model execution failed with return code {result.returncode}")
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
            cmd = cmd.replace(f'--prompt "{prompt}"',
                            f'--system-prompt "{system_prompt}" --prompt "{prompt}"')

        print(f"{Colors.BRIGHT_CYAN}Executing command:{Colors.RESET}")
        print(f"{Colors.DIM}{cmd}{Colors.RESET}\n")

        # Execute
        subprocess.run(cmd, shell=True)

    def view_system_prompts(self):
        """Display system prompt examples"""
        print(f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}╔══════════════════════════════════════════════════════════════╗{Colors.RESET}")
        print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}║  SYSTEM PROMPT GUIDE{Colors.RESET}")
        print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}╚══════════════════════════════════════════════════════════════╝{Colors.RESET}\n")

        print(f"{Colors.BRIGHT_WHITE}System prompts are stored in:{Colors.RESET}")
        print(f"{Colors.CYAN}{self.system_prompts_dir}{Colors.RESET}\n")

        print(f"{Colors.BRIGHT_WHITE}How to use system prompts:{Colors.RESET}\n")
        print(f"{Colors.WHITE}1. System prompts are automatically loaded by AI Router{Colors.RESET}")
        print(f"{Colors.WHITE}2. Each model has an optimized system prompt file{Colors.RESET}")
        print(f"{Colors.WHITE}3. You can edit these files to customize behavior{Colors.RESET}\n")

        print(f"{Colors.BRIGHT_YELLOW}Example system prompt structure:{Colors.RESET}\n")
        print(f"{Colors.GREEN}You are an expert AI assistant specialized in [domain].{Colors.RESET}")
        print(f"{Colors.GREEN}Your responses should be:{Colors.RESET}")
        print(f"{Colors.GREEN}- Accurate and well-researched{Colors.RESET}")
        print(f"{Colors.GREEN}- Clear and concise{Colors.RESET}")
        print(f"{Colors.GREEN}- Formatted with proper code blocks when relevant{Colors.RESET}\n")

        print(f"{Colors.BRIGHT_MAGENTA}Available system prompt files:{Colors.RESET}\n")
        for model_id, model_data in self.models.items():
            if model_data['system_prompt']:
                print(f"  {Colors.GREEN}[OK]{Colors.RESET} {model_data['system_prompt']}")
            else:
                print(f"  {Colors.RED}[X]{Colors.RESET} {model_id} (no system prompt support)")
        print()

    def view_parameters_guide(self):
        """Display optimal parameters guide"""
        print(f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}╔══════════════════════════════════════════════════════════════╗{Colors.RESET}")
        print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}║  OPTIMAL PARAMETERS GUIDE (2025 Research){Colors.RESET}")
        print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}╚══════════════════════════════════════════════════════════════╝{Colors.RESET}\n")

        print(f"{Colors.BRIGHT_WHITE}RTX 3090 (llama.cpp WSL):{Colors.RESET}\n")
        print(f"{Colors.GREEN}-ngl 999{Colors.RESET}           {Colors.WHITE}Full GPU offload (Aug 2025 default){Colors.RESET}")
        print(f"{Colors.GREEN}-t 24{Colors.RESET}             {Colors.WHITE}Use all CPU threads (Ryzen 9 5900X){Colors.RESET}")
        print(f"{Colors.GREEN}-b 512{Colors.RESET}            {Colors.WHITE}Minimum batch size (2025 research){Colors.RESET}")
        print(f"{Colors.GREEN}-ub 512{Colors.RESET}           {Colors.WHITE}Logical batch for prompt processing{Colors.RESET}")
        print(f"{Colors.GREEN}-fa 1{Colors.RESET}             {Colors.WHITE}Flash Attention (+20% speed, 50% memory){Colors.RESET}")
        print(f"{Colors.GREEN}--cache-type-k q8_0{Colors.RESET}  {Colors.WHITE}KV cache quantization (50% memory){Colors.RESET}")
        print(f"{Colors.GREEN}--cache-type-v q8_0{Colors.RESET}  {Colors.WHITE}KV cache quantization{Colors.RESET}")
        print(f"{Colors.GREEN}--no-ppl{Colors.RESET}          {Colors.WHITE}Skip perplexity (+15% speedup){Colors.RESET}")
        print(f"{Colors.GREEN}--mlock{Colors.RESET}           {Colors.WHITE}Lock model in RAM{Colors.RESET}\n")

        print(f"{Colors.BRIGHT_WHITE}MacBook M4 Pro (MLX):{Colors.RESET}\n")
        print(f"{Colors.GREEN}--max-tokens 2048{Colors.RESET}  {Colors.WHITE}Maximum generation length{Colors.RESET}")
        print(f"{Colors.GREEN}--temp 0.7{Colors.RESET}        {Colors.WHITE}Temperature (creativity){Colors.RESET}")
        print(f"{Colors.GREEN}--top-p 0.9{Colors.RESET}       {Colors.WHITE}Nucleus sampling{Colors.RESET}\n")

        print(f"{Colors.BRIGHT_WHITE}Temperature Guide:{Colors.RESET}\n")
        print(f"{Colors.CYAN}0.2-0.4{Colors.RESET}  {Colors.WHITE}Technical docs, code, Q&A (conservative){Colors.RESET}")
        print(f"{Colors.CYAN}0.5-0.9{Colors.RESET}  {Colors.WHITE}Content creation, conversation (balanced){Colors.RESET}")
        print(f"{Colors.CYAN}0.8-1.2+{Colors.RESET} {Colors.WHITE}Creative writing, brainstorming{Colors.RESET}\n")

        print(f"{Colors.BRIGHT_YELLOW}CRITICAL Notes:{Colors.RESET}\n")
        print(f"{Colors.RED}[X]{Colors.RESET} {Colors.WHITE}NEVER use temp 0 with Qwen models (causes loops){Colors.RESET}")
        print(f"{Colors.RED}[X]{Colors.RESET} {Colors.WHITE}NEVER use 'think step-by-step' with reasoning models{Colors.RESET}")
        print(f"{Colors.GREEN}[OK]{Colors.RESET} {Colors.WHITE}ALWAYS use --jinja flag with Phi-4{Colors.RESET}")
        print(f"{Colors.GREEN}[OK]{Colors.RESET} {Colors.WHITE}ALWAYS use --jinja flag with Qwen3{Colors.RESET}")
        print(f"{Colors.GREEN}[OK]{Colors.RESET} {Colors.WHITE}WSL provides near-native Linux performance (within 1%){Colors.RESET}\n")

    def view_documentation(self):
        """Display documentation guide menu"""
        docs_dir = self.models_dir

        # Define documentation files with priority (ONLY FILES THAT EXIST)
        docs = [
            # Frequently needed (top priority)
            ("HOW-TO-RUN-AI-ROUTER.md", "🚀 How to Run the AI Router", "Getting started, usage, troubleshooting"),
            ("BOT-PROJECT-QUICK-START.md", "Bot & Project Management", "Create bots and projects with custom configs"),
            ("SYSTEM-PROMPTS-QUICK-START.md", "📝 System Prompts Quick Start", "Using and customizing system prompts"),

            # Important reference
            ("COMPREHENSIVE-EVALUATION-FRAMEWORK-PROMPT.md", "📊 Evaluation Framework", "Testing and comparing models"),
            ("2025-RESEARCH-SUMMARY.md", "🔬 2025 Research Summary", "Latest research findings and best practices"),
            ("MACBOOK-M4-OPTIMIZATION-GUIDE.md", "💻 MacBook M4 Optimization", "Optimizing for Apple M4 hardware"),

            # Additional resources
            ("GITHUB-SETUP-GUIDE.md", "🐙 GitHub Setup Guide", "Setting up Git and GitHub"),
            ("README.md", "📖 Project README", "Complete project overview and setup"),
        ]

        # Filter to only files that actually exist
        existing_docs = []
        for filename, title, desc in docs:
            doc_path = docs_dir / filename
            if doc_path.exists():
                existing_docs.append((filename, title, desc))

        docs = existing_docs

        if not docs:
            print(f"\n{Colors.BRIGHT_RED}No documentation files found!{Colors.RESET}\n")
            input(f"{Colors.BRIGHT_YELLOW}Press Enter to return...{Colors.RESET}")
            return

        print(f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}╔══════════════════════════════════════════════════════════════╗{Colors.RESET}")
        print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}║  📚 DOCUMENTATION GUIDES ({len(docs)} available){Colors.RESET}")
        print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}╚══════════════════════════════════════════════════════════════╝{Colors.RESET}\n")

        # Display docs organized by priority
        # Top 3 are most frequently needed
        if len(docs) >= 1:
            print(f"{Colors.BRIGHT_WHITE}⭐ Most Frequently Needed:{Colors.RESET}\n")
            for idx in range(min(3, len(docs))):
                filename, title, desc = docs[idx]
                print(f"{Colors.BRIGHT_GREEN}[{idx+1}]{Colors.RESET} {Colors.BRIGHT_WHITE}{title}{Colors.RESET}")
                print(f"    {Colors.CYAN}{desc}{Colors.RESET}")
                print()

        # Next 3 are important reference
        if len(docs) > 3:
            print(f"{Colors.BRIGHT_WHITE}📚 Important Reference:{Colors.RESET}\n")
            for idx in range(3, min(6, len(docs))):
                filename, title, desc = docs[idx]
                print(f"{Colors.BRIGHT_GREEN}[{idx+1}]{Colors.RESET} {Colors.WHITE}{title}{Colors.RESET}")
                print(f"    {Colors.CYAN}{desc}{Colors.RESET}")
                print()

        # Remaining are additional resources
        if len(docs) > 6:
            print(f"{Colors.BRIGHT_WHITE}📖 Additional Resources:{Colors.RESET}\n")
            for idx in range(6, len(docs)):
                filename, title, desc = docs[idx]
                print(f"{Colors.BRIGHT_GREEN}[{idx+1}]{Colors.RESET} {Colors.WHITE}{title}{Colors.RESET}")
                print(f"    {Colors.CYAN}{desc}{Colors.RESET}")
                print()

        print(f"{Colors.BRIGHT_GREEN}[0]{Colors.RESET} {Colors.WHITE}Return to main menu{Colors.RESET}\n")

        choice = input(f"{Colors.BRIGHT_YELLOW}Select documentation [0-{len(docs)}]: {Colors.RESET}").strip()

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

                    print(f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}╔══════════════════════════════════════════════════════════════╗{Colors.RESET}")
                    print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}║  {title}{Colors.RESET}")
                    print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}╚══════════════════════════════════════════════════════════════╝{Colors.RESET}\n")

                    # Display content with pagination (first 50 lines)
                    lines = content.split('\n')
                    page_size = 50

                    for i in range(0, len(lines), page_size):
                        page_lines = lines[i:i+page_size]
                        print('\n'.join(page_lines))

                        if i + page_size < len(lines):
                            cont = input(f"\n{Colors.BRIGHT_YELLOW}Press Enter to continue, 'q' to quit: {Colors.RESET}").strip().lower()
                            if cont == 'q':
                                break
                        else:
                            print(f"\n{Colors.BRIGHT_GREEN}[End of document]{Colors.RESET}")

                    input(f"\n{Colors.BRIGHT_YELLOW}Press Enter to return to menu...{Colors.RESET}")
                else:
                    print(f"{Colors.BRIGHT_RED}Documentation file not found: {filename}{Colors.RESET}")
                    input(f"\n{Colors.BRIGHT_YELLOW}Press Enter to continue...{Colors.RESET}")
            else:
                print(f"{Colors.BRIGHT_RED}[X] Invalid selection.{Colors.RESET}")
                print(f"{Colors.BRIGHT_YELLOW}Please enter a valid option number.{Colors.RESET}")
        except ValueError:
            print(f"{Colors.BRIGHT_RED}[X] Invalid input.{Colors.RESET}")
            print(f"{Colors.BRIGHT_YELLOW}Please enter a valid number from the menu.{Colors.RESET}")


def main():
    """Main entry point"""
    try:
        router = AIRouter()

        # Check if arguments provided (non-interactive mode)
        if len(sys.argv) > 1:
            if sys.argv[1] == "--list":
                router.print_banner()
                router.list_models()
            elif sys.argv[1] == "--help":
                router.print_banner()
                print(f"{Colors.BRIGHT_WHITE}Usage:{Colors.RESET}\n")
                print(f"  {Colors.GREEN}python ai-router.py{Colors.RESET}")
                print(f"    {Colors.WHITE}Launch interactive mode{Colors.RESET}\n")
                print(f"  {Colors.GREEN}python ai-router.py --list{Colors.RESET}")
                print(f"    {Colors.WHITE}List all available models{Colors.RESET}\n")
                print(f"  {Colors.GREEN}python ai-router.py --help{Colors.RESET}")
                print(f"    {Colors.WHITE}Show this help message{Colors.RESET}\n")
            else:
                print(f"{Colors.BRIGHT_RED}Unknown argument. Use --help for usage.{Colors.RESET}")
        else:
            # Interactive mode
            router.interactive_mode()

    except KeyboardInterrupt:
        print(f"\n\n{Colors.BRIGHT_YELLOW}Interrupted by user. Goodbye!{Colors.RESET}\n")
        sys.exit(0)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"\n[X] Error: An unexpected error occurred")
        print(f"Details: {str(e)[:200]}\n")
        print(f"Troubleshooting Steps:")
        print(f"  1. Check Python version: python --version")
        print(f"  2. Verify dependencies: pip list")
        print(f"  3. Check WSL status: wsl --status")
        print(f"  4. Try reinstalling: pip install -r requirements.txt\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
