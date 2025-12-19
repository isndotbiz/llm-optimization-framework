#!/usr/bin/env python3
"""
AI Router MLX - Optimized for M4 MacBook Pro
Intelligent Model Selection for MLX Framework
"""

import sys
import subprocess
import platform
from pathlib import Path


class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'


class MLXModelDatabase:
    """MLX-optimized model database for M4 MacBook Pro"""

    M4_MLX_MODELS = {
        "qwen25-coder-7b": {
            "name": "Qwen2.5 Coder 7B MLX",
            "path": "mlx-community/Qwen2.5-Coder-7B-Instruct-4bit",
            "size": "4.5GB",
            "speed": "60-80 tok/sec",
            "use_case": "Fast coding, code review, quick iterations",
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 2048,
            "system_prompt": None,
            "notes": "BEST for daily coding work. Ultra-fast on M4.",
            "framework": "mlx"
        },
        "qwen25-coder-32b": {
            "name": "Qwen2.5 Coder 32B MLX",
            "path": "mlx-community/Qwen2.5-Coder-32B-Instruct-4bit",
            "size": "18GB",
            "speed": "11-22 tok/sec",
            "use_case": (
                "Advanced coding, architecture design, "
                "complex refactoring"
            ),
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 2048,
            "system_prompt": None,
            "notes": "Requires 24GB+ RAM. Best output quality.",
            "framework": "mlx"
        },
        "qwen3-14b": {
            "name": "Qwen3 14B MLX",
            "path": "mlx-community/Qwen3-14B-Instruct-4bit",
            "size": "9GB",
            "speed": "40-60 tok/sec",
            "use_case": (
                "General purpose, research, balanced quality/speed"
            ),
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 2048,
            "system_prompt": None,
            "notes": "Qwen 3.0 - Latest generation. Excellent all-rounder.",
            "framework": "mlx"
        },
        "deepseek-r1-8b": {
            "name": "DeepSeek-R1 8B MLX",
            "path": "mlx-community/DeepSeek-R1-Distill-Llama-8B",
            "size": "4.5GB",
            "speed": "50-70 tok/sec",
            "use_case": "Math, reasoning, problem-solving, analysis",
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 2048,
            "system_prompt": None,
            "notes": "Reasoning specialist. Fast on M4.",
            "framework": "mlx"
        },
        "phi4-14b": {
            "name": "Phi-4 14B MLX",
            "path": "mlx-community/phi-4-4bit",
            "size": "8-9GB",
            "speed": "40-60 tok/sec",
            "use_case": "STEM, mathematical reasoning, logic",
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 2048,
            "system_prompt": None,
            "notes": (
                "Microsoft's math specialist. "
                "Excellent for technical tasks."
            ),
            "framework": "mlx"
        },
        "mistral-7b": {
            "name": "Mistral 7B MLX",
            "path": "mlx-community/Mistral-7B-Instruct-v0.3-4bit",
            "size": "4GB",
            "speed": "70-100 tok/sec",
            "use_case": (
                "Ultra-fast responses, mobile/battery critical, "
                "simple queries"
            ),
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 2048,
            "system_prompt": None,
            "notes": "FASTEST. For when speed is critical.",
            "framework": "mlx"
        },
        "dolphin-llama31-8b": {
            "name": "Dolphin 3.0 Llama 3.1 8B MLX",
            "path": "mlx-community/Dolphin3.0-Llama3.1-8B",
            "size": "4.5GB",
            "speed": "60-80 tok/sec",
            "use_case": (
                "Uncensored chat, creative tasks, "
                "hacking course materials"
            ),
            "temperature": 0.8,
            "top_p": 0.9,
            "max_tokens": 2048,
            "system_prompt": None,
            "notes": (
                "UNCENSORED. Fast variant for "
                "offensive security research."
            ),
            "framework": "mlx"
        }
    }

    @classmethod
    def detect_use_case(cls, prompt_text):
        """Detect use case from prompt"""
        prompt_lower = prompt_text.lower()

        coding_keywords = [
            'code', 'function', 'class', 'debug', 'error', 'python',
            'javascript', 'implement', 'refactor', 'algorithm', 'bug'
        ]
        reasoning_keywords = [
            'calculate', 'prove', 'math', 'solve', 'logic', 'analyze'
        ]
        creative_keywords = [
            'story', 'poem', 'creative', 'write', 'fiction'
        ]
        research_keywords = [
            'research', 'explain', 'summary', 'what is', 'compare'
        ]

        if any(kw in prompt_lower for kw in coding_keywords):
            return "coding"
        elif any(kw in prompt_lower for kw in reasoning_keywords):
            return "reasoning"
        elif any(kw in prompt_lower for kw in creative_keywords):
            return "creative"
        elif any(kw in prompt_lower for kw in research_keywords):
            return "research"
        return "general"

    @classmethod
    def recommend_model(cls, use_case):
        """Recommend best model for use case"""
        recommendations = {
            "coding": "qwen25-coder-7b",
            "reasoning": "deepseek-r1-8b",
            "creative": "dolphin-llama31-8b",
            "research": "qwen3-14b",
            "general": "qwen25-coder-7b"
        }
        model_id = recommendations.get(use_case, "qwen25-coder-7b")
        return model_id, cls.M4_MLX_MODELS[model_id]


class AIRouterMLX:
    """MLX-optimized AI Router for MacBook"""

    def __init__(self):
        self.platform = platform.system()
        if self.platform != "Darwin":
            print(
                f"{Colors.BRIGHT_RED}[X] This version is for "
                f"macOS only!{Colors.RESET}"
            )
            print(f"You appear to be on {self.platform}.")
            sys.exit(1)

        self.models = MLXModelDatabase.M4_MLX_MODELS
        self.models_dir = Path.home() / "workspace" / "mlx"

    def print_banner(self):
        """Print colorful banner"""
        print(f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}")
        print("=" * 70)
        print("                   AI ROUTER MLX v1.0")
        print("              M4 MacBook Pro Optimized")
        print("=" * 70)
        print(Colors.RESET)
        print(
            f"{Colors.BRIGHT_GREEN}Platform: "
            f"{Colors.BRIGHT_WHITE}MacBook M4 Pro (MLX)"
        )
        print(
            f"{Colors.BRIGHT_GREEN}Models Available: "
            f"{Colors.BRIGHT_CYAN}{len(self.models)}"
        )
        print(
            f"{Colors.BRIGHT_GREEN}Models Directory: "
            f"{Colors.BRIGHT_WHITE}{self.models_dir}\n"
        )

    def list_models(self):
        """List all available models"""
        print(
            f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}"
            f"AVAILABLE MODELS{Colors.RESET}\n"
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
                f"    {Colors.CYAN}Use case: "
                f"{model_data['use_case']}{Colors.RESET}"
            )
            print(
                f"    {Colors.GREEN}{model_data['size']} | "
                f"{model_data['speed']}{Colors.RESET}\n"
            )

    def run_model(self, model_id, model_data, prompt):
        """Run MLX model"""
        print(
            f"\n{Colors.BRIGHT_GREEN}{Colors.BOLD}Launching "
            f"{model_data['name']}...{Colors.RESET}\n"
        )

        # Build MLX chat command
        cmd = (
            f"source ~/workspace/venv-mlx/bin/activate && "
            f"mlx_lm.chat --model {model_data['path']}"
        )

        print(f"{Colors.BRIGHT_CYAN}Executing:{Colors.RESET}")
        print(f"{Colors.DIM}{cmd}{Colors.RESET}\n")
        print(f"{Colors.BRIGHT_YELLOW}Your prompt:{Colors.RESET}")
        print(f"{Colors.WHITE}{prompt}{Colors.RESET}\n")

        try:
            subprocess.run(cmd, shell=True)
        except Exception as e:
            print(
                f"{Colors.BRIGHT_RED}[X] Error: "
                f"{str(e)}{Colors.RESET}\n"
            )

    def interactive_mode(self):
        """Interactive mode"""
        self.print_banner()

        while True:
            print(f"\n{Colors.BRIGHT_CYAN}{'=' * 70}{Colors.RESET}")
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
            print(f"{Colors.BRIGHT_GREEN}[4]{Colors.RESET} Exit")
            print(f"{Colors.BRIGHT_CYAN}{'=' * 70}{Colors.RESET}")

            choice = input(
                f"\n{Colors.BRIGHT_YELLOW}"
                f"Enter choice [1-4]: {Colors.RESET}"
            ).strip()

            if choice == "1":
                self.auto_select_mode()
            elif choice == "2":
                self.manual_select_mode()
            elif choice == "3":
                self.list_models()
            elif choice == "4":
                print(f"\n{Colors.BRIGHT_GREEN}Goodbye!{Colors.RESET}\n")
                sys.exit(0)
            else:
                print(f"{Colors.BRIGHT_RED}Invalid choice.{Colors.RESET}")

    def auto_select_mode(self):
        """Auto-select based on prompt"""
        print(
            f"\n{Colors.BRIGHT_CYAN}"
            f"Enter your prompt (or 'back'):{Colors.RESET}"
        )
        prompt = input(f"{Colors.YELLOW}> {Colors.RESET}").strip()

        if prompt.lower() == 'back':
            return

        use_case = MLXModelDatabase.detect_use_case(prompt)
        model_id, model_data = MLXModelDatabase.recommend_model(use_case)

        print(
            f"\n{Colors.BRIGHT_MAGENTA}Detected use case: "
            f"{Colors.BRIGHT_WHITE}{use_case.upper()}{Colors.RESET}"
        )
        print(
            f"{Colors.BRIGHT_GREEN}Recommended: "
            f"{Colors.BRIGHT_WHITE}{model_data['name']}{Colors.RESET}"
        )
        print(f"{Colors.CYAN}{model_data['use_case']}{Colors.RESET}")

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
                prompt = input(
                    f"\n{Colors.BRIGHT_CYAN}"
                    f"Enter your prompt: {Colors.RESET}"
                ).strip()
                self.run_model(model_id, model_data, prompt)
            else:
                print(
                    f"{Colors.BRIGHT_RED}"
                    f"Invalid model number.{Colors.RESET}"
                )
        except ValueError:
            print(f"{Colors.BRIGHT_RED}Invalid input.{Colors.RESET}")


def main():
    """Main entry point"""
    try:
        router = AIRouterMLX()

        if len(sys.argv) > 1:
            if sys.argv[1] == "--list":
                router.print_banner()
                router.list_models()
            elif sys.argv[1] == "--help":
                router.print_banner()
                print(f"{Colors.BRIGHT_WHITE}Usage:{Colors.RESET}\n")
                print(
                    f"  {Colors.GREEN}python ai-router-mlx.py"
                    f"{Colors.RESET}"
                )
                print(
                    f"    {Colors.WHITE}"
                    f"Launch interactive mode{Colors.RESET}\n"
                )
                print(
                    f"  {Colors.GREEN}python ai-router-mlx.py --list"
                    f"{Colors.RESET}"
                )
                print(
                    f"    {Colors.WHITE}List all models{Colors.RESET}\n"
                )
            else:
                print(
                    f"{Colors.BRIGHT_RED}Unknown argument. "
                    f"Use --help for usage.{Colors.RESET}"
                )
        else:
            router.interactive_mode()

    except KeyboardInterrupt:
        print(
            f"\n\n{Colors.BRIGHT_YELLOW}"
            f"Interrupted. Goodbye!{Colors.RESET}\n"
        )
        sys.exit(0)
    except Exception as e:
        print(
            f"\n{Colors.BRIGHT_RED}[X] Error: "
            f"{str(e)}{Colors.RESET}\n"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
