#!/usr/bin/env python3
"""
TrueNAS AI Router - Production Edition
RTX 4060 Ti (16GB) - Pre-Tuned Model Collection
Built for: D:/models/rtx4060ti-16gb model collection
Version: 3.1 Production
"""

import sys
import json
import subprocess
import platform
import shutil

try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False

from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from logging_config import setup_logging

try:
    from flask import jsonify
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

# ============================================================================
# VRAM Utilities
# ============================================================================


class VRAMMonitor:
    """Monitor and manage GPU VRAM usage"""

    MAX_VRAM_GB = 16  # RTX 4060 Ti = 16GB
    SAFETY_MARGIN_GB = 1  # Keep 1GB free
    USABLE_VRAM_GB = MAX_VRAM_GB - SAFETY_MARGIN_GB

    @staticmethod
    def get_vram_usage() -> Dict[str, float]:
        """Get current GPU VRAM usage"""
        try:
            if GPU_AVAILABLE:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]
                    return {
                        "used": gpu.memoryUsed,
                        "total": gpu.memoryTotal,
                        "free": gpu.memoryFree,
                        "percent": gpu.memoryUtil
                    }
        except Exception:
            pass

        # Fallback: try nvidia-smi
        try:
            result = subprocess.run(
                ['nvidia-smi',
                 '--query-gpu=memory.used,memory.total',
                 '--format=csv,nounits,noheader'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                used, total = map(float, result.stdout.strip().split(','))
                return {
                    "used": used,
                    "total": total,
                    "free": total - used,
                    "percent": (used / total * 100) if total > 0 else 0
                }
        except Exception:
            pass

        return {"used": 0, "total": 16, "free": 16, "percent": 0}

    @staticmethod
    def can_fit_model(model_size_gb: float) -> bool:
        """Check if model can fit in available VRAM"""
        usage = VRAMMonitor.get_vram_usage()
        return usage["free"] >= model_size_gb + 0.5


# ============================================================================
# Color codes for terminal output
# ============================================================================

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


# ============================================================================
# Model Database - Your Production Models
# ============================================================================

class ModelDatabase:
    """Production model database for RTX 4060 Ti"""

    # Your actual production models
    PRODUCTION_MODELS = {
        "dolphin-llama31-8b": {
            "name": "Dolphin 3.0 Llama 3.1 8B Q6_K",
            "path": "/mnt/models/organized/Dolphin3.0-Llama3.1-8B-Q6_K.gguf",
            "size_gb": 6.2,
            "speed": "65-85 tok/sec",
            "use_case": "Fast uncensored chat, quick responses, general tasks",
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "context": 32768,
            "special_flags": [],
            "system_prompt": None,  # Uses internal default
            "framework": "llama.cpp",
            "optimal": True,
            "notes": "Uncensored, very fast, production-ready"
        },

        "llama31-8b-instruct": {
            "name": "Meta Llama 3.1 8B Instruct Q6_K",
            "path": ("/mnt/models/organized/llama31-8b-instruct/"
                     "Meta-Llama-3.1-8B-Instruct-Q6_K.gguf"),
            "size_gb": 6.2,
            "speed": "60-80 tok/sec",
            "use_case": ("Production-grade instruction following, "
                         "reliable responses"),
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "context": 128000,
            "special_flags": [],
            "system_prompt": ("/mnt/models/organized/"
                              "Llama-3.1-8B-SYSTEM-PROMPT.txt"),
            "framework": "llama.cpp",
            "optimal": True,
            "notes": ("Official Meta model, excellent safety guardrails, "
                      "128K context")
        },

        "qwen25-14b-instruct": {
            "name": "Qwen 2.5 14B Instruct Q4_K_M",
            "path": ("/mnt/models/organized/qwen25-14b-instruct/"
                     "Qwen2.5-14B-Instruct-Q4_K_M.gguf"),
            "size_gb": 8.4,
            "speed": "55-75 tok/sec",
            "use_case": ("Balanced instruction following, multilingual, "
                         "professional tasks"),
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "context": 32768,
            "special_flags": [],
            "system_prompt": ("/mnt/models/organized/"
                              "Qwen-14B-Instruct-SYSTEM-PROMPT.txt"),
            "framework": "llama.cpp",
            "optimal": True,
            "notes": ("Alibaba Qwen 2.5, excellent multilingual support, "
                      "25+ languages")
        },

        "qwen25-14b-uncensored": {
            "name": "Qwen 2.5 14B Uncensored Q4_K_M",
            "path": ("/mnt/models/organized/qwen25-14b-uncensored/"
                     "Qwen2.5-14B_Uncensored_Instruct-Q4_K_M.gguf"),
            "size_gb": 8.4,
            "speed": "55-75 tok/sec",
            "use_case": ("Uncensored instruction following, creative tasks, "
                         "roleplay"),
            "temperature": 0.8,
            "top_p": 0.9,
            "top_k": 40,
            "context": 32768,
            "special_flags": [],
            "system_prompt": ("/mnt/models/organized/"
                              "Qwen-14B-Uncensored-SYSTEM-PROMPT.txt"),
            "framework": "llama.cpp",
            "optimal": True,
            "notes": ("Uncensored variant, excellent for creative and "
                      "roleplay tasks")
        },

        "qwen25-coder-7b": {
            "name": "Qwen 2.5 Coder 7B Q5_K_M",
            "path": ("/mnt/models/organized/qwen25-coder-7b/"
                     "qwen2.5-coder-7b-instruct-q5_k_m.gguf"),
            "size_gb": 5.1,
            "speed": "70-90 tok/sec",
            "use_case": ("Code generation, programming tasks, debugging, "
                         "technical help"),
            "temperature": 0.2,
            "top_p": 0.95,
            "top_k": 40,
            "context": 32768,
            "special_flags": [],
            "system_prompt": ("/mnt/models/organized/"
                              "Qwen-Coder-7B-SYSTEM-PROMPT.txt"),
            "framework": "llama.cpp",
            "optimal": True,
            "notes": ("Specialized for coding, fastest model, low "
                      "temperature for accuracy")
        },
    }

    @classmethod
    def get_models(cls):
        """Return production models"""
        return cls.PRODUCTION_MODELS

    @classmethod
    def get_optimal_models(cls) -> Dict[str, Dict]:
        """Return optimal models (all in this collection)"""
        return cls.PRODUCTION_MODELS

    @classmethod
    def list_summary(cls) -> str:
        """Get human-readable model summary"""
        models = cls.PRODUCTION_MODELS
        summary = (f"\n{Colors.BRIGHT_CYAN}{'='*70}{Colors.RESET}\n")
        summary += (f"{Colors.BRIGHT_WHITE}"
                    f"RTX 4060 Ti Production Model Collection"
                    f"{Colors.RESET}\n")
        summary += (f"{Colors.BRIGHT_CYAN}{'='*70}{Colors.RESET}\n\n")

        for model_id, info in models.items():
            summary += (f"{Colors.BRIGHT_GREEN}✓ {model_id}"
                        f"{Colors.RESET}\n")
            summary += f"  Name: {info['name']}\n"
            summary += (f"  Size: {info['size_gb']}GB | "
                        f"Speed: {info['speed']}\n")
            summary += f"  Use: {info['use_case']}\n"
            summary += f"  Notes: {info['notes']}\n\n"

        total_size = sum(m['size_gb'] for m in models.values())
        summary += (f"{Colors.BRIGHT_YELLOW}Total Collection Size: "
                    f"{total_size:.1f}GB{Colors.RESET}\n")
        summary += (f"{Colors.BRIGHT_CYAN}{'='*70}{Colors.RESET}\n")
        return summary


# ============================================================================
# Project Manager
# ============================================================================

class ProjectManager:
    """Manages AI projects with configurations and memory"""

    def __init__(self, projects_dir: Path):
        self.projects_dir = projects_dir
        self.projects_dir.mkdir(parents=True, exist_ok=True)
        self.current_project = None
        self.current_config = None

    def create_project(
        self, project_name: str, config: Dict[str, Any]
    ) -> bool:
        """Create a new project with configuration"""
        try:
            project_path = self.projects_dir / project_name
            if project_path.exists():
                print(f"{Colors.BRIGHT_RED}Project '{project_name}' "
                      f"already exists!{Colors.RESET}")
                return False

            project_path.mkdir(parents=True, exist_ok=True)
            (project_path / "data").mkdir(exist_ok=True)

            config_path = project_path / "config.json"
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)

            memory_path = project_path / "memory.json"
            with open(memory_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "conversations": [],
                    "created": datetime.now().isoformat(),
                    "modified": datetime.now().isoformat()
                }, f, indent=2)

            print(f"{Colors.BRIGHT_GREEN}Project '{project_name}' "
                  f"created successfully!{Colors.RESET}")
            return True
        except Exception as e:
            print(f"{Colors.BRIGHT_RED}Error creating project: "
                  f"{e}{Colors.RESET}")
            return False

    def list_projects(self) -> List[str]:
        """List all available projects"""
        try:
            return sorted([p.name for p in self.projects_dir.iterdir()
                          if p.is_dir()])
        except Exception:
            return []

    def load_project(self, project_name: str) -> Optional[Dict[str, Any]]:
        """Load a project configuration"""
        try:
            project_path = self.projects_dir / project_name
            config_path = project_path / "config.json"

            if not config_path.exists():
                print(f"{Colors.BRIGHT_RED}Project configuration "
                      f"not found!{Colors.RESET}")
                return None

            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            self.current_project = project_name
            self.current_config = config
            return config
        except Exception as e:
            print(f"{Colors.BRIGHT_RED}Error loading project: "
                  f"{e}{Colors.RESET}")
            return None

    def save_project(
        self, project_name: str, config: Dict[str, Any]
    ) -> bool:
        """Save project configuration"""
        try:
            project_path = self.projects_dir / project_name
            config_path = project_path / "config.json"

            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)

            return True
        except Exception as e:
            print(f"{Colors.BRIGHT_RED}Error saving project: "
                  f"{e}{Colors.RESET}")
            return False

    def delete_project(self, project_name: str) -> bool:
        """Delete a project"""
        try:
            project_path = self.projects_dir / project_name
            if project_path.exists():
                shutil.rmtree(project_path)
                print(f"{Colors.BRIGHT_GREEN}Project '{project_name}' "
                      f"deleted successfully!{Colors.RESET}")
                return True
            return False
        except Exception as e:
            print(f"{Colors.BRIGHT_RED}Error deleting project: "
                  f"{e}{Colors.RESET}")
            return False


# ============================================================================
# Memory Manager
# ============================================================================

class MemoryManager:
    """Manages conversation memory and history"""

    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.memory_file = project_path / "memory.json"
        self.memory = self._load_memory()

    def _load_memory(self) -> Dict[str, Any]:
        """Load memory from file"""
        try:
            if self.memory_file.exists():
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {
            "conversations": [],
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat()
        }

    def _save_memory(self):
        """Save memory to file"""
        try:
            self.memory["modified"] = datetime.now().isoformat()
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, indent=2)
        except Exception as e:
            print(f"{Colors.BRIGHT_RED}Error saving memory: {e}{Colors.RESET}")

    def add_conversation(
        self, user_prompt: str, model_response: str, model_id: str
    ):
        """Add a conversation to memory"""
        conversation = {
            "timestamp": datetime.now().isoformat(),
            "user": user_prompt,
            "assistant": model_response,
            "model": model_id
        }
        self.memory["conversations"].append(conversation)
        self._save_memory()

    def get_recent_conversations(
        self, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent conversations"""
        return self.memory["conversations"][-limit:]

    def clear_memory(self):
        """Clear all conversation memory"""
        self.memory["conversations"] = []
        self._save_memory()
        print(f"{Colors.BRIGHT_GREEN}Memory cleared!{Colors.RESET}")


# ============================================================================
# Main AI Router Production Edition
# ============================================================================

class ProductionAIRouter:
    """Production TrueNAS AI Router for RTX 4060 Ti"""

    def __init__(self, models_base_dir: str = "/mnt/models"):
        self.platform = platform.system()
        self.models_base_dir = Path(models_base_dir)
        self.models_dir = self.models_base_dir / "projects"
        self.system_prompts_dir = self.models_base_dir

        self.models = ModelDatabase.get_models()
        self.all_models = ModelDatabase.get_models()

        # Initialize logging
        self.logger = setup_logging(self.models_base_dir)
        self.logger.info(
            f"Production AI Router initialized on {self.platform}"
        )

        # Initialize managers
        self.project_manager = ProjectManager(self.models_dir)

        # Current session state
        self.current_project = None
        self.current_memory = None

        # API state
        self.api_app = None
        self.api_port = 5000

    def print_banner(self):
        """Print welcome banner"""
        print(f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}")
        print("+" + "="*78 + "+")
        print("|" + " "*78 + "|")
        print("|" + " "*10 +
              "TrueNAS AI ROUTER v3.1 - Production Edition" + " "*25 + "|")
        print("|" + " "*78 + "|")
        print("|" + " "*10 +
              "RTX 4060 Ti (16GB) - Pre-Tuned Model Collection" +
              " "*21 + "|")
        print("|" + " "*78 + "|")
        print("+" + "="*78 + "+")
        print(Colors.RESET)

        # VRAM status
        usage = VRAMMonitor.get_vram_usage()
        if usage['percent'] < 70:
            vram_color = Colors.BRIGHT_GREEN
        elif usage['percent'] < 90:
            vram_color = Colors.BRIGHT_YELLOW
        else:
            vram_color = Colors.BRIGHT_RED
        print(f"{vram_color}GPU VRAM: {usage['used']:.1f}GB / "
              f"{usage['total']:.1f}GB ({usage['percent']:.0f}%)"
              f"{Colors.RESET}")

        if self.current_project:
            print(f"{Colors.BRIGHT_GREEN}Current Project: "
                  f"{Colors.BRIGHT_WHITE}{self.current_project}"
                  f"{Colors.RESET}")

        print(f"\n{Colors.BRIGHT_WHITE}Platform: "
              f"{Colors.BRIGHT_YELLOW}Linux/TrueNAS (RTX 4060 Ti)"
              f"{Colors.RESET}")
        print(f"{Colors.BRIGHT_WHITE}Available Models: "
              f"{Colors.BRIGHT_GREEN}{len(self.models)}{Colors.RESET}")
        print()

    def main_menu(self):
        """Display and handle main menu"""
        while True:
            self.print_banner()

            print(f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}+"
                  f"{'='*62}+{Colors.RESET}")
            print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}|  MAIN MENU"
                  f"{Colors.RESET}")
            print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}+"
                  f"{'='*62}+{Colors.RESET}\n")

            print(f"{Colors.BRIGHT_GREEN}[1]{Colors.RESET}  "
                  f"Create New Project")
            print(f"{Colors.BRIGHT_GREEN}[2]{Colors.RESET}  "
                  f"Load Existing Project")
            print(f"{Colors.BRIGHT_GREEN}[3]{Colors.RESET}  "
                  f"Run Chat Session")
            print(f"{Colors.BRIGHT_GREEN}[4]{Colors.RESET}  "
                  f"View Conversation History")
            print(f"{Colors.BRIGHT_GREEN}[5]{Colors.RESET}  "
                  f"Check GPU VRAM Status")
            print(f"{Colors.BRIGHT_GREEN}[6]{Colors.RESET}  "
                  f"View Available Models")
            if FLASK_AVAILABLE:
                print(f"{Colors.BRIGHT_GREEN}[7]{Colors.RESET}  "
                      f"Start REST API Server")
            print(f"{Colors.BRIGHT_GREEN}[8]{Colors.RESET}  Exit")

            choice = input(
                f"\n{Colors.BRIGHT_YELLOW}Enter choice: "
                f"{Colors.RESET}"
            ).strip()

            if choice == "1":
                self.create_new_project()
            elif choice == "2":
                self.load_existing_project()
            elif choice == "3":
                self.run_chat_session()
            elif choice == "4":
                self.view_conversation_history()
            elif choice == "5":
                self.check_vram()
                input(f"{Colors.BRIGHT_CYAN}Press Enter to continue..."
                      f"{Colors.RESET}")
            elif choice == "6":
                self.view_available_models()
            elif choice == "7" and FLASK_AVAILABLE:
                self.start_api_server()
            elif choice == "8":
                print(f"\n{Colors.BRIGHT_GREEN}Goodbye!{Colors.RESET}\n")
                sys.exit(0)
            else:
                print(f"{Colors.BRIGHT_RED}Invalid choice. "
                      f"Please try again.{Colors.RESET}")
                input(f"\n{Colors.BRIGHT_CYAN}Press Enter to continue..."
                      f"{Colors.RESET}")

    def create_new_project(self):
        """Create a new project"""
        print(f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}+"
              f"{'='*62}+{Colors.RESET}")
        print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}|  CREATE NEW PROJECT"
              f"{Colors.RESET}")
        print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}+"
              f"{'='*62}+{Colors.RESET}\n")

        project_name = input(f"{Colors.BRIGHT_WHITE}Project name: "
                             f"{Colors.RESET}").strip()
        if not project_name:
            print(f"{Colors.BRIGHT_RED}Project name cannot be empty!"
                  f"{Colors.RESET}")
            input(f"\n{Colors.BRIGHT_CYAN}Press Enter to continue..."
                  f"{Colors.RESET}")
            return

        title = input(f"{Colors.BRIGHT_WHITE}Project title: "
                      f"{Colors.RESET}").strip()
        if not title:
            title = project_name

        print(f"\n{Colors.BRIGHT_WHITE}Available models:{Colors.RESET}\n")
        model_ids = list(self.models.keys())
        for idx, model_id in enumerate(model_ids, 1):
            model_data = self.models[model_id]
            print(f"{Colors.BRIGHT_GREEN}[{idx}]{Colors.RESET} "
                  f"{model_id:25} - {model_data['name']:40}")
            print(f"      {model_data['size_gb']}GB | "
                  f"{model_data['speed']}")

        model_choice = input(
            f"\n{Colors.BRIGHT_YELLOW}Select model [1-{len(model_ids)}]: "
            f"{Colors.RESET}"
        ).strip()
        try:
            model_idx = int(model_choice) - 1
            if 0 <= model_idx < len(model_ids):
                model_id = model_ids[model_idx]
                model_data = self.models[model_id]

                if not VRAMMonitor.can_fit_model(model_data['size_gb']):
                    usage = VRAMMonitor.get_vram_usage()
                    print(f"\n{Colors.BRIGHT_YELLOW}Warning: "
                          f"Not enough VRAM!{Colors.RESET}")
                    print(f"Need: {model_data['size_gb']}GB, "
                          f"Available: {usage['free']:.2f}GB")
                    input(f"\n{Colors.BRIGHT_CYAN}Press Enter to "
                          f"continue...{Colors.RESET}")
                    return
            else:
                print(f"{Colors.BRIGHT_RED}Invalid selection!"
                      f"{Colors.RESET}")
                input(f"\n{Colors.BRIGHT_CYAN}Press Enter to continue..."
                      f"{Colors.RESET}")
                return
        except ValueError:
            print(f"{Colors.BRIGHT_RED}Invalid input!{Colors.RESET}")
            input(f"\n{Colors.BRIGHT_CYAN}Press Enter to continue..."
                  f"{Colors.RESET}")
            return

        config = {
            "title": title,
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
            "model": model_id,
            "provider": "llama-cpp",
            "system_prompt": "",
            "parameters": {
                "temperature": model_data['temperature'],
                "top_p": model_data['top_p'],
                "top_k": model_data['top_k'],
                "max_tokens": 2048,
            }
        }

        if self.project_manager.create_project(project_name, config):
            self.current_project = project_name
            project_path = self.models_dir / project_name
            self.current_memory = MemoryManager(project_path)
            print(f"\n{Colors.BRIGHT_GREEN}Project '{project_name}' "
                  f"created and loaded!{Colors.RESET}")

        input(f"\n{Colors.BRIGHT_CYAN}Press Enter to continue..."
              f"{Colors.RESET}")

    def load_existing_project(self):
        """Load an existing project"""
        print(f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}+"
              f"{'='*62}+{Colors.RESET}")
        print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}|  LOAD PROJECT"
              f"{Colors.RESET}")
        print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}+"
              f"{'='*62}+{Colors.RESET}\n")

        projects = self.project_manager.list_projects()
        if not projects:
            print(f"{Colors.BRIGHT_YELLOW}No projects found!"
                  f"{Colors.RESET}")
            input(f"\n{Colors.BRIGHT_CYAN}Press Enter to continue..."
                  f"{Colors.RESET}")
            return

        print(f"{Colors.BRIGHT_WHITE}Available projects:{Colors.RESET}\n")
        for idx, project in enumerate(projects, 1):
            print(f"{Colors.BRIGHT_GREEN}[{idx}]{Colors.RESET} {project}")

        print(f"{Colors.BRIGHT_GREEN}[0]{Colors.RESET} Return to menu")

        choice = input(
            f"\n{Colors.BRIGHT_YELLOW}Select project [0-{len(projects)}]: "
            f"{Colors.RESET}"
        ).strip()

        if choice == "0":
            return

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(projects):
                project_name = projects[idx]
                config = self.project_manager.load_project(project_name)
                if config:
                    self.current_project = project_name
                    project_path = self.models_dir / project_name
                    self.current_memory = MemoryManager(project_path)

                    print(f"\n{Colors.BRIGHT_GREEN}Project "
                          f"'{project_name}' loaded!{Colors.RESET}")
                    print(f"  Model: {Colors.CYAN}"
                          f"{config.get('model')}{Colors.RESET}")
                    print(f"  Title: {Colors.CYAN}"
                          f"{config.get('title')}{Colors.RESET}")
        except ValueError:
            print(f"{Colors.BRIGHT_RED}Invalid input!{Colors.RESET}")

        input(f"\n{Colors.BRIGHT_CYAN}Press Enter to continue..."
              f"{Colors.RESET}")

    def run_chat_session(self):
        """Run an interactive chat session"""
        if not self.current_project:
            print(f"\n{Colors.BRIGHT_YELLOW}No project loaded!"
                  f"{Colors.RESET}")
            input(f"\n{Colors.BRIGHT_CYAN}Press Enter to continue..."
                  f"{Colors.RESET}")
            return

        config = self.project_manager.load_project(self.current_project)
        if not config:
            return

        model_id = config.get("model")
        if model_id not in self.all_models:
            print(f"{Colors.BRIGHT_RED}Model not found!{Colors.RESET}")
            input(f"\n{Colors.BRIGHT_CYAN}Press Enter to continue..."
                  f"{Colors.RESET}")
            return

        model_data = self.all_models[model_id]

        print(f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}+"
              f"{'='*62}+{Colors.RESET}")
        print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}|  CHAT SESSION"
              f"{Colors.RESET}")
        print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}+"
              f"{'='*62}+{Colors.RESET}\n")

        print(f"{Colors.BRIGHT_WHITE}Project: {Colors.CYAN}"
              f"{config.get('title')}{Colors.RESET}")
        print(f"{Colors.BRIGHT_WHITE}Model: {Colors.CYAN}"
              f"{model_data['name']}{Colors.RESET}")
        print(f"{Colors.BRIGHT_WHITE}Type 'exit' to end session"
              f"{Colors.RESET}\n")

        # Check VRAM
        usage = VRAMMonitor.get_vram_usage()
        if not VRAMMonitor.can_fit_model(model_data['size_gb']):
            print(f"{Colors.BRIGHT_RED}Not enough VRAM! "
                  f"({usage['free']:.2f}GB available, "
                  f"{model_data['size_gb']}GB needed){Colors.RESET}")
            input(f"\n{Colors.BRIGHT_CYAN}Press Enter to continue..."
                  f"{Colors.RESET}")
            return

        while True:
            prompt = input(
                f"\n{Colors.BRIGHT_YELLOW}You: {Colors.RESET}"
            ).strip()

            if prompt.lower() in ['exit', 'quit', 'q']:
                print(f"{Colors.BRIGHT_GREEN}Session ended."
                      f"{Colors.RESET}")
                break

            if not prompt:
                continue

            print(f"\n{Colors.BRIGHT_CYAN}Assistant: {Colors.RESET}")
            self._run_model(model_id, model_data, prompt, config)

            if self.current_memory:
                self.current_memory.add_conversation(
                    prompt, "[logged]", model_id
                )

        input(f"\n{Colors.BRIGHT_CYAN}Press Enter to continue..."
              f"{Colors.RESET}")

    def _run_model(
        self, model_id: str, model_data: Dict[str, Any],
        prompt: str, config: Dict[str, Any]
    ):
        """Run model with configuration"""
        self.logger.info(f"Executing: {model_id}")

        params = config.get("parameters", {})
        system_prompt = model_data.get("system_prompt")

        # Load system prompt from file if available
        if system_prompt:
            prompt_file = Path(system_prompt)
            if prompt_file.exists():
                try:
                    with open(prompt_file, 'r', encoding='utf-8') as f:
                        system_prompt = f.read().strip()
                except Exception:
                    system_prompt = ""

        temperature = params.get("temperature", model_data['temperature'])
        top_p = params.get("top_p", model_data['top_p'])
        top_k = params.get("top_k", model_data['top_k'])
        max_tokens = params.get("max_tokens", 2048)

        special_flags = ' '.join(model_data['special_flags'])

        # Build command
        cmd = (
            f"/root/llama.cpp/build/bin/llama-cli "
            f"-m '{model_data['path']}' "
            f"-p '{prompt}' "
            f"-ngl 999 "
            f"-t 12 "
            f"-b 512 "
            f"--temp {temperature} "
            f"--top-p {top_p} "
            f"--top-k {top_k} "
            f"-n {max_tokens} "
            f"-c {model_data['context']} "
            f"--cache-type-k q8_0 "
            f"--cache-type-v q8_0 "
            f"{special_flags}"
        )

        if system_prompt:
            cmd = cmd.replace(
                f"-p '{prompt}'",
                f"--system-prompt '{system_prompt}' -p '{prompt}'"
            )

        try:
            subprocess.run(cmd, shell=True, check=False)
            self.logger.info(f"Completed: {model_id}")
        except Exception as e:
            self.logger.error(f"Error: {e}")
            print(f"\n{Colors.BRIGHT_RED}Error: {e}{Colors.RESET}")

    def view_conversation_history(self):
        """View conversation history"""
        if not self.current_project or not self.current_memory:
            print(f"\n{Colors.BRIGHT_YELLOW}No project loaded!"
                  f"{Colors.RESET}")
            input(f"\n{Colors.BRIGHT_CYAN}Press Enter to continue..."
                  f"{Colors.RESET}")
            return

        conversations = self.current_memory.get_recent_conversations(20)

        print(f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}+"
              f"{'='*62}+{Colors.RESET}")
        print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}|  CONVERSATION HISTORY"
              f"{Colors.RESET}")
        print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}+"
              f"{'='*62}+{Colors.RESET}\n")

        if not conversations:
            print(f"{Colors.BRIGHT_YELLOW}No history yet.{Colors.RESET}")
        else:
            for idx, conv in enumerate(conversations, 1):
                print(f"\n{Colors.BRIGHT_WHITE}[{idx}] "
                      f"{conv.get('timestamp')}{Colors.RESET}")
                print(f"{Colors.BRIGHT_YELLOW}You: {Colors.WHITE}"
                      f"{conv.get('user', '')[:100]}{Colors.RESET}")
                print(f"{Colors.DIM}Model: "
                      f"{conv.get('model')}{Colors.RESET}")

        input(f"\n{Colors.BRIGHT_CYAN}Press Enter to continue..."
              f"{Colors.RESET}")

    def view_available_models(self):
        """View all available models"""
        print(ModelDatabase.list_summary())
        input(f"{Colors.BRIGHT_CYAN}Press Enter to continue..."
              f"{Colors.RESET}")

    def check_vram(self):
        """Check and display VRAM status"""
        usage = VRAMMonitor.get_vram_usage()
        print(f"\n{Colors.BRIGHT_CYAN}GPU VRAM Status:{Colors.RESET}")
        print(f"  Used: {usage['used']:.1f}GB / {usage['total']:.1f}GB "
              f"({usage['percent']:.1f}%)")
        print(f"  Free: {usage['free']:.1f}GB")
        print()

    def start_api_server(self):
        """Start REST API server"""
        if not FLASK_AVAILABLE:
            print(f"{Colors.BRIGHT_RED}Flask not installed!{Colors.RESET}")
            return

        print(f"\n{Colors.BRIGHT_GREEN}Starting API Server...{Colors.RESET}")
        print("Available at: http://10.0.0.89:5000\n")

        self._setup_api_routes()
        self.api_app.run(host='0.0.0.0', port=self.api_port, debug=False)

    def _setup_api_routes(self):
        """Setup Flask API routes"""
        from flask import Flask as FlaskApp

        self.api_app = FlaskApp(__name__)

        @self.api_app.route('/api/health', methods=['GET'])
        def health():
            usage = VRAMMonitor.get_vram_usage()
            return jsonify({"status": "ok", "vram": usage})

        @self.api_app.route('/api/models', methods=['GET'])
        def list_models():
            return jsonify({
                "models": {k: v['name']
                           for k, v in self.models.items()}
            })

        @self.api_app.route('/api/projects', methods=['GET'])
        def list_projects():
            return jsonify({
                "projects": self.project_manager.list_projects()
            })


def main():
    """Main entry point"""
    try:
        router = ProductionAIRouter()
        router.main_menu()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.BRIGHT_YELLOW}Goodbye!{Colors.RESET}\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.BRIGHT_RED}Error: {e}{Colors.RESET}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
