#!/usr/bin/env python3
"""
AI Router TrueNAS Edition - Complete AI Project Management System
Optimized for TrueNAS with RTX 4060 Ti (16GB VRAM)
Features: Projects, Bots, Multi-Provider Support, Web Search,
Memory, MCP Tools, REST API
Version: 3.0 TrueNAS
Author: Enhanced AI Router System
Date: 2025-12-14
"""

import sys
import json
import subprocess
import platform
import shutil
import psutil
import GPUtil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from logging_config import setup_logging
try:
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
            gpus = GPUtil.getGPUs()
            if not gpus:
                return {"used": 0, "total": 16, "free": 16, "percent": 0}

            gpu = gpus[0]  # Use first GPU
            return {
                "used": gpu.memoryUsed,
                "total": gpu.memoryTotal,
                "free": gpu.memoryFree,
                "percent": gpu.memoryUtil
            }
        except Exception:
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
                        "percent": ((used / total * 100)
                                    if total > 0 else 0)
                    }
            except Exception:
                pass

            return {"used": 0, "total": 16, "free": 16, "percent": 0}

    @staticmethod
    def can_fit_model(model_size_gb: float) -> bool:
        """Check if model can fit in available VRAM"""
        usage = VRAMMonitor.get_vram_usage()
        return usage["free"] >= model_size_gb + 0.5  # 500MB buffer


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
# Model Database - Optimized for RTX 4060 Ti (16GB)
# ============================================================================

class ModelDatabase:
    """Model database optimized for 16GB RTX 4060 Ti"""

    # RTX 4060 Ti Models (CUDA 12.x compatible)
    RTX4060TI_MODELS = {
        "dolphin-llama31-8b": {
            "name": "Dolphin 3.0 Llama 3.1 8B Q6_K",
            "path": "/mnt/models/organized/"
                    "Dolphin3.0-Llama3.1-8B-Q6_K.gguf",
            "size_gb": 6,
            "speed": "60-85 tok/sec",
            "use_case": ("Fast general tasks, uncensored chat, "
                         "quick assistance"),
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "context": 32768,
            "special_flags": [],
            "system_prompt": "system-prompt-dolphin-8b.txt",
            "notes": ("Fastest model. Uncensored variant of Llama "
                      "3.1 8B. Perfect for 4060 Ti."),
            "framework": "llama.cpp",
            "optimal_for_4060ti": True
        },
        "phi4-14b": {
            "name": "Phi-4 Reasoning Plus 14B Q5_K_M",
            "path": ("/mnt/models/organized/"
                     "microsoft_Phi-4-reasoning-plus-Q5_K_M.gguf"),
            "size_gb": 9,
            "speed": "45-65 tok/sec",
            "use_case": "Math, reasoning, STEM, logical analysis",
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "context": 16384,
            "special_flags": ["--jinja"],
            "system_prompt": "system-prompt-phi4-14b.txt",
            "notes": ("CRITICAL: Requires --jinja flag. "
                      "Excellent reasoning for 4060 Ti."),
            "framework": "llama.cpp",
            "optimal_for_4060ti": True
        },
        "qwen25-14b-coder": {
            "name": "Qwen2.5 Coder 14B Q5_K_M",
            "path": ("/mnt/models/organized/"
                     "qwen25-coder-14b-Q5_K_M.gguf"),
            "size_gb": 9,
            "speed": "50-70 tok/sec",
            "use_case": ("Coding, debugging, technical tasks, "
                         "code review"),
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "context": 32768,
            "special_flags": [],
            "system_prompt": "system-prompt-qwen25-coder-14b.txt",
            "notes": ("Best coding model for 4060 Ti. "
                      "Strong instruction following."),
            "framework": "llama.cpp",
            "optimal_for_4060ti": True
        },
        "ministral-3-14b": {
            "name": "Ministral-3 14B Reasoning Q5_K_M",
            "path": ("/mnt/models/organized/"
                     "Ministral-3-14B-Reasoning-2512-Q5_K_M.gguf"),
            "size_gb": 9,
            "speed": "45-60 tok/sec",
            "use_case": "Complex reasoning, problem solving, analysis",
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "context": 262144,
            "special_flags": [],
            "system_prompt": "system-prompt-ministral-3-14b.txt",
            "notes": ("256K context window. "
                      "Excellent for long-context reasoning."),
            "framework": "llama.cpp",
            "optimal_for_4060ti": True
        },
        "gemma3-9b": {
            "name": "Gemma-3 9B Q6_K",
            "path": "/mnt/models/organized/gemma-3-9b-Q6_K.gguf",
            "size_gb": 7,
            "speed": "70-90 tok/sec",
            "use_case": "Fast responses, chat, general queries",
            "temperature": 0.9,
            "top_p": 0.9,
            "top_k": 40,
            "context": 128000,
            "special_flags": [],
            "system_prompt": None,
            "notes": ("Speed champion on 4060 Ti. "
                      "NO system prompt support."),
            "framework": "llama.cpp",
            "optimal_for_4060ti": True
        },
        "qwen3-coder-30b": {
            "name": "Qwen3 Coder 30B Q4_K_M",
            "path": ("/mnt/models/organized/"
                     "Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf"),
            "size_gb": 18,
            "speed": "25-35 tok/sec",
            "use_case": ("Advanced coding, code review, "
                         "architecture design"),
            "temperature": 0.7,
            "top_p": 0.8,
            "top_k": 20,
            "context": 32768,
            "special_flags": ["--jinja"],
            "system_prompt": "system-prompt-qwen3-coder-30b.txt",
            "notes": ("CRITICAL: May require quantization reduction "
                      "(Q3_K_M) for 4060 Ti. Use sparingly."),
            "framework": "llama.cpp",
            # Tight fit, requires careful VRAM management
            "optimal_for_4060ti": False
        },
        "dolphin-mistral-24b": {
            "name": "Dolphin Mistral 24B Venice Q4_K_M",
            "path": ("/mnt/models/organized/"
                     "cognitivecomputations_"
                     "Dolphin-Mistral-24B-Venice-Edition-Q4_K_M.gguf"),
            "size_gb": 14,
            "speed": "35-50 tok/sec",
            "use_case": "Uncensored chat, creative tasks, roleplay",
            "temperature": 0.8,
            "top_p": 0.9,
            "top_k": 40,
            "context": 32768,
            "special_flags": [],
            "system_prompt": None,
            "notes": ("Venice Edition: Completely uncensored. "
                      "Fits 4060 Ti with margin."),
            "framework": "llama.cpp",
            "optimal_for_4060ti": True
        },
        "llama33-70b-iq3": {
            "name": "Llama 3.3 70B Instruct IQ3_S (Extreme Quantization)",
            "path": ("/mnt/models/organized/"
                     "Llama-3.3-70B-Instruct-IQ3_S.gguf"),
            "size_gb": 15,
            "speed": "10-15 tok/sec",
            "use_case": ("Large-scale reasoning "
                         "(if you need 70B on 4060 Ti)"),
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            # Reduced context due to extreme quantization
            "context": 8192,
            "special_flags": [],
            "system_prompt": "system-prompt-llama33-70b.txt",
            "notes": ("EXTREME: Only use if absolutely necessary. "
                      "Quality degradation expected."),
            "framework": "llama.cpp",
            "optimal_for_4060ti": False  # Emergency only
        }
    }

    @classmethod
    def get_platform_models(cls):
        """Return models for current platform"""
        return cls.RTX4060TI_MODELS

    @classmethod
    def get_optimal_models(cls) -> Dict[str, Dict]:
        """Return only optimal models for 4060 Ti"""
        return {k: v for k, v in cls.RTX4060TI_MODELS.items()
                if v.get("optimal_for_4060ti", False)}

    @classmethod
    def get_all_models(cls):
        """Return all available models"""
        return cls.RTX4060TI_MODELS


# ============================================================================
# Project Manager (unchanged)
# ============================================================================

class ProjectManager:
    """Manages AI projects with configurations and memory"""

    def __init__(self, projects_dir: Path):
        self.projects_dir = projects_dir
        self.projects_dir.mkdir(parents=True, exist_ok=True)
        self.current_project = None
        self.current_config = None

    def create_project(self, project_name: str,
                       config: Dict[str, Any]) -> bool:
        """Create a new project with configuration"""
        try:
            project_path = self.projects_dir / project_name
            if project_path.exists():
                msg = (f"{Colors.BRIGHT_RED}Project '{project_name}' "
                       f"already exists!{Colors.RESET}")
                print(msg)
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

            msg = (f"{Colors.BRIGHT_GREEN}Project '{project_name}' "
                   f"created successfully!{Colors.RESET}")
            print(msg)
            return True
        except Exception as e:
            msg = (f"{Colors.BRIGHT_RED}Error creating project: "
                   f"{e}{Colors.RESET}")
            print(msg)
            return False

    def list_projects(self) -> List[str]:
        """List all available projects"""
        try:
            return [p.name for p in self.projects_dir.iterdir() if p.is_dir()]
        except Exception:
            return []

    def load_project(self, project_name: str) -> Optional[Dict[str, Any]]:
        """Load a project configuration"""
        try:
            project_path = self.projects_dir / project_name
            config_path = project_path / "config.json"

            if not config_path.exists():
                msg = (f"{Colors.BRIGHT_RED}Project configuration "
                       f"not found!{Colors.RESET}")
                print(msg)
                return None

            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            self.current_project = project_name
            self.current_config = config
            return config
        except Exception as e:
            msg = (f"{Colors.BRIGHT_RED}Error loading project: "
                   f"{e}{Colors.RESET}")
            print(msg)
            return None

    def save_project(self, project_name: str, config: Dict[str, Any]) -> bool:
        """Save project configuration"""
        try:
            project_path = self.projects_dir / project_name
            config_path = project_path / "config.json"

            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)

            return True
        except Exception as e:
            msg = (f"{Colors.BRIGHT_RED}Error saving project: "
                   f"{e}{Colors.RESET}")
            print(msg)
            return False

    def delete_project(self, project_name: str) -> bool:
        """Delete a project"""
        try:
            project_path = self.projects_dir / project_name
            if project_path.exists():
                shutil.rmtree(project_path)
                msg = (f"{Colors.BRIGHT_GREEN}Project '{project_name}' "
                       f"deleted successfully!{Colors.RESET}")
                print(msg)
                return True
            return False
        except Exception as e:
            msg = (f"{Colors.BRIGHT_RED}Error deleting project: "
                   f"{e}{Colors.RESET}")
            print(msg)
            return False


# ============================================================================
# Memory Manager (unchanged)
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

    def add_conversation(self, user_prompt: str,
                         model_response: str, model_id: str):
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
            self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversations"""
        return self.memory["conversations"][-limit:]

    def clear_memory(self):
        """Clear all conversation memory"""
        self.memory["conversations"] = []
        self._save_memory()
        print(f"{Colors.BRIGHT_GREEN}Memory cleared!{Colors.RESET}")


# ============================================================================
# Main AI Router TrueNAS Edition
# ============================================================================

class TrueNASAIRouter:
    """TrueNAS-optimized AI Router with REST API and VRAM monitoring"""

    def __init__(self, models_base_dir: str = "/mnt/models"):
        self.platform = platform.system()
        self.models_base_dir = Path(models_base_dir)
        self.models_dir = self.models_base_dir / "projects"
        self.system_prompts_dir = self.models_base_dir

        # Verify we're on Linux
        if self.platform != "Linux":
            msg = (f"{Colors.BRIGHT_YELLOW}Warning: Not running on "
                   f"Linux. Some features may not work.{Colors.RESET}")
            print(msg)

        self.models = ModelDatabase.get_platform_models()
        self.all_models = ModelDatabase.get_all_models()

        # Initialize logging
        self.logger = setup_logging(self.models_base_dir)
        self.logger.info(f"TrueNAS AI Router initialized on {self.platform}")

        # Initialize managers
        self.project_manager = ProjectManager(self.models_dir)

        # Current session state
        self.current_project = None
        self.current_memory = None

        # API state
        self.api_app = None
        self.api_port = 5000

    def check_vram(self):
        """Display VRAM status"""
        usage = VRAMMonitor.get_vram_usage()
        print(f"\n{Colors.BRIGHT_CYAN}GPU VRAM Status:{Colors.RESET}")
        msg = (f"  Used: {usage['used']:.2f}GB / "
               f"{usage['total']:.2f}GB ({usage['percent']:.1f}%)")
        print(msg)
        print(f"  Free: {usage['free']:.2f}GB")
        print()

    def print_banner(self):
        """Print colorful banner"""
        print(f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}")
        sep = "+" + "=" * 78 + "+"
        print(sep)
        print("|" + " " * 78 + "|")
        line1 = "TrueNAS AI ROUTER v3.0 - RTX 4060 Ti Edition"
        print("|" + line1.center(78) + "|")
        print("|" + " " * 78 + "|")
        line2 = "Complete AI Project Management with Local & REST API Support"
        print("|" + line2.center(78) + "|")
        line3 = "Optimized for 16GB VRAM (RTX 4060 Ti)"
        print("|" + line3.center(78) + "|")
        print("|" + " " * 78 + "|")
        print(sep)
        print(Colors.RESET)

        # VRAM indicator
        usage = VRAMMonitor.get_vram_usage()
        if usage['percent'] < 70:
            vram_color = Colors.BRIGHT_GREEN
        elif usage['percent'] < 90:
            vram_color = Colors.BRIGHT_YELLOW
        else:
            vram_color = Colors.BRIGHT_RED
        msg = (f"\n{vram_color}GPU VRAM: {usage['used']:.1f}GB / "
               f"{usage['total']:.1f}GB "
               f"({usage['percent']:.0f}%){Colors.RESET}")
        print(msg)

        # Current project indicator
        if self.current_project:
            msg = (f"\n{Colors.BRIGHT_GREEN}Current Project: "
                   f"{Colors.BRIGHT_WHITE}{self.current_project}"
                   f"{Colors.RESET}")
            print(msg)

        msg = (f"\n{Colors.BRIGHT_WHITE}Platform: "
               f"{Colors.BRIGHT_YELLOW}Linux/TrueNAS (RTX 4060 Ti)"
               f"{Colors.RESET}")
        print(msg)
        msg = (f"{Colors.BRIGHT_WHITE}Available Models: "
               f"{Colors.BRIGHT_CYAN}{len(self.models)}{Colors.RESET}")
        print(msg)
        optimal_count = len(ModelDatabase.get_optimal_models())
        msg = (f"{Colors.BRIGHT_WHITE}Optimal Models (for 4060 Ti): "
               f"{Colors.BRIGHT_GREEN}{optimal_count}{Colors.RESET}")
        print(msg)
        print()

    def main_menu(self):
        """Display and handle main menu"""
        while True:
            self.print_banner()

            sep = "+" + "=" * 62 + "+"
            msg = (f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}"
                   f"{sep}{Colors.RESET}")
            print(msg)
            msg = (f"{Colors.BRIGHT_CYAN}{Colors.BOLD}"
                   f"|  MAIN MENU{Colors.RESET}")
            print(msg)
            msg = (f"{Colors.BRIGHT_CYAN}{Colors.BOLD}"
                   f"{sep}{Colors.RESET}\n")
            print(msg)

            msg = (f"{Colors.BRIGHT_GREEN}[1]{Colors.RESET}  "
                   f"Create New Project")
            print(msg)
            msg = (f"{Colors.BRIGHT_GREEN}[2]{Colors.RESET}  "
                   f"Load Existing Project")
            print(msg)
            msg = (f"{Colors.BRIGHT_GREEN}[3]{Colors.RESET}  "
                   f"Run Chat Session")
            print(msg)
            msg = (f"{Colors.BRIGHT_GREEN}[4]{Colors.RESET}  "
                   f"View Conversation History")
            print(msg)
            msg = (f"{Colors.BRIGHT_GREEN}[5]{Colors.RESET}  "
                   f"Check GPU VRAM Status")
            print(msg)
            msg = (f"{Colors.BRIGHT_GREEN}[6]{Colors.RESET}  "
                   f"View Available Models")
            print(msg)
            if FLASK_AVAILABLE:
                msg = (f"{Colors.BRIGHT_GREEN}[7]{Colors.RESET}  "
                       f"Start REST API Server")
                print(msg)
            print(f"{Colors.BRIGHT_GREEN}[8]{Colors.RESET}  Settings")
            print(f"{Colors.BRIGHT_GREEN}[9]{Colors.RESET}  Exit")

            prompt = f"\n{Colors.BRIGHT_YELLOW}Enter choice: {Colors.RESET}"
            choice = input(prompt).strip()

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
                prompt = (f"{Colors.BRIGHT_CYAN}Press Enter to "
                          f"continue...{Colors.RESET}")
                input(prompt)
            elif choice == "6":
                self.view_available_models()
            elif choice == "7" and FLASK_AVAILABLE:
                self.start_api_server()
            elif choice == "8":
                self.settings_menu()
            elif choice == "9":
                print(f"\n{Colors.BRIGHT_GREEN}Goodbye!{Colors.RESET}\n")
                sys.exit(0)
            else:
                msg = (f"{Colors.BRIGHT_RED}Invalid choice. "
                       f"Please try again.{Colors.RESET}")
                print(msg)
                prompt = (f"\n{Colors.BRIGHT_CYAN}Press Enter to "
                          f"continue...{Colors.RESET}")
                input(prompt)

    def create_new_project(self):
        """Create a new project"""
        sep = "+" + "=" * 62 + "+"
        msg = f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}{sep}{Colors.RESET}"
        print(msg)
        msg = (f"{Colors.BRIGHT_CYAN}{Colors.BOLD}|  "
               f"CREATE NEW PROJECT{Colors.RESET}")
        print(msg)
        msg = f"{Colors.BRIGHT_CYAN}{Colors.BOLD}{sep}{Colors.RESET}\n"
        print(msg)

        prompt = f"{Colors.BRIGHT_WHITE}Project name: {Colors.RESET}"
        project_name = input(prompt).strip()
        if not project_name:
            msg = (f"{Colors.BRIGHT_RED}Project name cannot be "
                   f"empty!{Colors.RESET}")
            print(msg)
            prompt = (f"\n{Colors.BRIGHT_CYAN}Press Enter to "
                      f"continue...{Colors.RESET}")
            input(prompt)
            return

        prompt = (f"{Colors.BRIGHT_WHITE}Project title "
                  f"(display name): {Colors.RESET}")
        title = input(prompt).strip()
        if not title:
            title = project_name

        print(f"\n{Colors.BRIGHT_WHITE}Available models:{Colors.RESET}\n")
        model_ids = list(self.models.keys())
        optimal_models = ModelDatabase.get_optimal_models()

        for idx, model_id in enumerate(model_ids, 1):
            model_data = self.models[model_id]
            if model_id in optimal_models:
                optimal_tag = f"{Colors.BRIGHT_GREEN}[OPTIMAL]{Colors.RESET}"
            else:
                optimal_tag = ""
            msg = (f"{Colors.BRIGHT_GREEN}[{idx}]{Colors.RESET} "
                   f"{model_id:25} - {model_data['name']:40} "
                   f"{optimal_tag}")
            print(msg)
            msg = (f"      Size: {model_data['size_gb']}GB | "
                   f"Speed: {model_data['speed']}")
            print(msg)

        prompt = (f"\n{Colors.BRIGHT_YELLOW}Select model "
                  f"[1-{len(model_ids)}]: {Colors.RESET}")
        model_choice = input(prompt).strip()
        try:
            model_idx = int(model_choice) - 1
            if 0 <= model_idx < len(model_ids):
                model_id = model_ids[model_idx]
                model_data = self.models[model_id]

                # Check VRAM
                if not VRAMMonitor.can_fit_model(model_data['size_gb']):
                    usage = VRAMMonitor.get_vram_usage()
                    msg = (f"\n{Colors.BRIGHT_YELLOW}Warning: Model size "
                           f"({model_data['size_gb']}GB) may not fit!")
                    print(msg)
                    msg = (f"Available VRAM: {usage['free']:.2f}GB"
                           f"{Colors.RESET}")
                    print(msg)
                    prompt = (f"{Colors.BRIGHT_YELLOW}Continue anyway? "
                              f"[y/N]: {Colors.RESET}")
                    proceed = input(prompt).strip().lower()
                    if proceed != 'y':
                        prompt = (f"\n{Colors.BRIGHT_CYAN}Press Enter to "
                                  f"continue...{Colors.RESET}")
                        input(prompt)
                        return
            else:
                msg = (f"{Colors.BRIGHT_RED}Invalid model selection!"
                       f"{Colors.RESET}")
                print(msg)
                prompt = (f"\n{Colors.BRIGHT_CYAN}Press Enter to "
                          f"continue...{Colors.RESET}")
                input(prompt)
                return
        except ValueError:
            msg = f"{Colors.BRIGHT_RED}Invalid input!{Colors.RESET}"
            print(msg)
            prompt = (f"\n{Colors.BRIGHT_CYAN}Press Enter to "
                      f"continue...{Colors.RESET}")
            input(prompt)
            return

        # Get system prompt
        system_prompt = ""
        if model_data.get('system_prompt'):
            msg = (f"\n{Colors.BRIGHT_WHITE}System prompt "
                   f"(leave empty for default):{Colors.RESET}")
            print(msg)
            custom_prompt = input(f"{Colors.CYAN}> {Colors.RESET}").strip()
            if custom_prompt:
                system_prompt = custom_prompt

        # Create project config
        config = {
            "title": title,
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
            "model": model_id,
            "provider": "llama-cpp",
            "system_prompt": system_prompt,
            "parameters": {
                "temperature": model_data['temperature'],
                "top_p": model_data['top_p'],
                "top_k": model_data['top_k'],
                "max_tokens": 2048,
                "context_limit": 50,
            }
        }

        if self.project_manager.create_project(project_name, config):
            self.current_project = project_name
            project_path = self.models_dir / project_name
            self.current_memory = MemoryManager(project_path)
            msg = (f"\n{Colors.BRIGHT_GREEN}Project '{project_name}' "
                   f"created and loaded!{Colors.RESET}")
            print(msg)

        prompt = (f"\n{Colors.BRIGHT_CYAN}Press Enter to "
                  f"continue...{Colors.RESET}")
        input(prompt)

    def load_existing_project(self):
        """Load an existing project"""
        sep = "+" + "=" * 62 + "+"
        msg = f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}{sep}{Colors.RESET}"
        print(msg)
        msg = (f"{Colors.BRIGHT_CYAN}{Colors.BOLD}|  "
               f"LOAD PROJECT{Colors.RESET}")
        print(msg)
        msg = f"{Colors.BRIGHT_CYAN}{Colors.BOLD}{sep}{Colors.RESET}\n"
        print(msg)

        projects = self.project_manager.list_projects()
        if not projects:
            msg = (f"{Colors.BRIGHT_YELLOW}No projects found. "
                   f"Create one first!{Colors.RESET}")
            print(msg)
            prompt = (f"\n{Colors.BRIGHT_CYAN}Press Enter to "
                      f"continue...{Colors.RESET}")
            input(prompt)
            return

        print(f"{Colors.BRIGHT_WHITE}Available projects:{Colors.RESET}\n")
        for idx, project in enumerate(projects, 1):
            print(f"{Colors.BRIGHT_GREEN}[{idx}]{Colors.RESET} {project}")

        print(f"{Colors.BRIGHT_GREEN}[0]{Colors.RESET} Return to menu")

        prompt = (f"\n{Colors.BRIGHT_YELLOW}Select project "
                  f"[0-{len(projects)}]: {Colors.RESET}")
        choice = input(prompt).strip()

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

                    msg = (f"\n{Colors.BRIGHT_GREEN}Project "
                           f"'{project_name}' loaded successfully!"
                           f"{Colors.RESET}")
                    print(msg)
                    msg = (f"\n{Colors.BRIGHT_WHITE}Project Details:"
                           f"{Colors.RESET}")
                    print(msg)
                    title = config.get('title', 'Untitled')
                    msg = (f"  Title: {Colors.CYAN}{title}"
                           f"{Colors.RESET}")
                    print(msg)
                    model = config.get('model', 'Not set')
                    msg = (f"  Model: {Colors.CYAN}{model}"
                           f"{Colors.RESET}")
                    print(msg)
            else:
                msg = f"{Colors.BRIGHT_RED}Invalid selection!{Colors.RESET}"
                print(msg)
        except ValueError:
            msg = f"{Colors.BRIGHT_RED}Invalid input!{Colors.RESET}"
            print(msg)

        prompt = (f"\n{Colors.BRIGHT_CYAN}Press Enter to "
                  f"continue...{Colors.RESET}")
        input(prompt)

    def run_chat_session(self):
        """Run an interactive chat session"""
        if not self.current_project:
            msg = (f"\n{Colors.BRIGHT_YELLOW}No project loaded. "
                   f"Please load a project first.{Colors.RESET}")
            print(msg)
            prompt = (f"\n{Colors.BRIGHT_CYAN}Press Enter to "
                      f"continue...{Colors.RESET}")
            input(prompt)
            return

        sep = "+" + "=" * 62 + "+"
        msg = f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}{sep}{Colors.RESET}"
        print(msg)
        msg = (f"{Colors.BRIGHT_CYAN}{Colors.BOLD}|  "
               f"CHAT SESSION{Colors.RESET}")
        print(msg)
        msg = f"{Colors.BRIGHT_CYAN}{Colors.BOLD}{sep}{Colors.RESET}\n"
        print(msg)

        config = self.project_manager.load_project(self.current_project)
        if not config:
            return

        model_id = config.get("model", "dolphin-llama31-8b")
        if model_id not in self.all_models:
            msg = (f"{Colors.BRIGHT_RED}Model '{model_id}' "
                   f"not found!{Colors.RESET}")
            print(msg)
            prompt = (f"\n{Colors.BRIGHT_CYAN}Press Enter to "
                      f"continue...{Colors.RESET}")
            input(prompt)
            return

        model_data = self.all_models[model_id]

        title = config.get('title', self.current_project)
        msg = (f"{Colors.BRIGHT_WHITE}Project: "
               f"{Colors.CYAN}{title}{Colors.RESET}")
        print(msg)
        msg = (f"{Colors.BRIGHT_WHITE}Model: "
               f"{Colors.CYAN}{model_data['name']}{Colors.RESET}")
        print(msg)
        msg = (f"{Colors.BRIGHT_WHITE}Type 'exit' or 'quit' "
               f"to end session{Colors.RESET}\n")
        print(msg)

        # Check VRAM before starting
        usage = VRAMMonitor.get_vram_usage()
        if not VRAMMonitor.can_fit_model(model_data['size_gb']):
            msg = (f"{Colors.BRIGHT_RED}Warning: Not enough VRAM "
                   f"for this model!{Colors.RESET}")
            print(msg)
            msg = (f"Required: {model_data['size_gb']}GB, "
                   f"Available: {usage['free']:.2f}GB")
            print(msg)
            prompt = (f"\n{Colors.BRIGHT_CYAN}Press Enter to "
                      f"continue...{Colors.RESET}")
            input(prompt)
            return

        # Interactive chat loop
        while True:
            user_prompt = (f"\n{Colors.BRIGHT_YELLOW}You: "
                           f"{Colors.RESET}")
            prompt = input(user_prompt).strip()

            if prompt.lower() in ['exit', 'quit', 'q']:
                msg = (f"{Colors.BRIGHT_GREEN}Chat session ended."
                       f"{Colors.RESET}")
                print(msg)
                break

            if not prompt:
                continue

            # Execute model
            msg = f"\n{Colors.BRIGHT_CYAN}Assistant: {Colors.RESET}"
            print(msg)
            self._run_model_with_config(
                model_id, model_data, prompt, config)

            # Save to memory
            if self.current_memory:
                self.current_memory.add_conversation(
                    prompt, "[Response logged]", model_id)

        prompt = (f"\n{Colors.BRIGHT_CYAN}Press Enter to "
                  f"continue...{Colors.RESET}")
        input(prompt)

    def _run_model_with_config(
            self, model_id: str,
            model_data: Dict[str, Any],
            prompt: str,
            config: Dict[str, Any]):
        """Run model with project configuration"""
        log_msg = (f"Starting model execution: {model_id} "
                   f"({model_data['name']})")
        self.logger.info(log_msg)

        params = config.get("parameters", {})
        system_prompt = config.get("system_prompt", "")

        # Load system prompt from file if not custom
        if not system_prompt and model_data.get('system_prompt'):
            prompt_file = (self.system_prompts_dir /
                           model_data['system_prompt'])
            if prompt_file.exists():
                try:
                    with open(prompt_file, 'r', encoding='utf-8') as f:
                        system_prompt = f.read().strip()
                except Exception as e:
                    log_msg = f"Could not read system prompt: {e}"
                    self.logger.warning(log_msg)

        msg = (f"\n{Colors.BRIGHT_GREEN}{Colors.BOLD}Launching "
               f"{model_data['name']}...{Colors.RESET}\n")
        print(msg)

        try:
            self._run_llamacpp_model(model_data, prompt,
                                     system_prompt, params)
            self.logger.info("Model execution completed successfully")
        except Exception as e:
            self.logger.error(f"Model execution failed: {e}")
            msg = f"\n{Colors.BRIGHT_RED}Error: {e}{Colors.RESET}\n"
            print(msg)

    def _run_llamacpp_model(self, model_data: Dict[str, Any],
                            prompt: str, system_prompt: str,
                            params: Dict[str, Any]):
        """Run model using llama.cpp (Linux native)"""
        self.logger.debug("Executing llama.cpp model")

        temperature = params.get("temperature", model_data['temperature'])
        top_p = params.get("top_p", model_data['top_p'])
        top_k = params.get("top_k", model_data['top_k'])
        max_tokens = params.get("max_tokens", 2048)

        special_flags = ' '.join(model_data['special_flags'])

        # Build command for Linux (native, no WSL)
        cmd = f"""/root/llama.cpp/build/bin/llama-cli \\
  -m '{model_data['path']}' \\
  -p '{prompt}' \\
  -ngl 999 \\
  -t 12 \\
  -b 512 \\
  -ub 512 \\
  -fa 1 \\
  --cache-type-k q8_0 \\
  --cache-type-v q8_0 \\
  --temp {temperature} \\
  --top-p {top_p} \\
  --top-k {top_k} \\
  -n {max_tokens} \\
  -c {model_data['context']} \\
  -ptc 10 \\
  --verbose-prompt \\
  --log-colors auto \\
  {special_flags}"""

        if system_prompt:
            old_part = f"-p '{prompt}'"
            new_part = f"--system-prompt '{system_prompt}' -p '{prompt}'"
            cmd = cmd.replace(old_part, new_part)

        # Execute
        self.logger.debug("Executing llama.cpp command")
        result = subprocess.run(cmd, shell=True)

        if result.returncode != 0:
            log_msg = (f"llama.cpp execution failed with return code "
                       f"{result.returncode}")
            self.logger.error(log_msg)
            err_msg = (f"Model execution failed with return code "
                       f"{result.returncode}")
            raise RuntimeError(err_msg)
        else:
            self.logger.info("Successfully executed llama.cpp model")

    def view_conversation_history(self):
        """View conversation history"""
        if not self.current_project or not self.current_memory:
            msg = (f"\n{Colors.BRIGHT_YELLOW}No project loaded. "
                   f"Please load a project first.{Colors.RESET}")
            print(msg)
            prompt = (f"\n{Colors.BRIGHT_CYAN}Press Enter to "
                      f"continue...{Colors.RESET}")
            input(prompt)
            return

        sep = "+" + "=" * 62 + "+"
        msg = f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}{sep}{Colors.RESET}"
        print(msg)
        msg = (f"{Colors.BRIGHT_CYAN}{Colors.BOLD}|  "
               f"CONVERSATION HISTORY{Colors.RESET}")
        print(msg)
        msg = f"{Colors.BRIGHT_CYAN}{Colors.BOLD}{sep}{Colors.RESET}\n"
        print(msg)

        conversations = self.current_memory.get_recent_conversations(20)

        if not conversations:
            msg = (f"{Colors.BRIGHT_YELLOW}No conversation history yet."
                   f"{Colors.RESET}")
            print(msg)
        else:
            for idx, conv in enumerate(conversations, 1):
                timestamp = conv.get("timestamp", "Unknown")
                msg = (f"\n{Colors.BRIGHT_WHITE}[{idx}] {timestamp}"
                       f"{Colors.RESET}")
                print(msg)
                user_text = conv.get('user', '')
                msg = (f"{Colors.BRIGHT_YELLOW}You: "
                       f"{Colors.WHITE}{user_text}{Colors.RESET}")
                print(msg)
                asst_text = conv.get('assistant', '')[:200]
                msg = (f"{Colors.BRIGHT_CYAN}Assistant: "
                       f"{Colors.WHITE}{asst_text}...{Colors.RESET}")
                print(msg)
                model_name = conv.get('model', 'Unknown')
                msg = f"{Colors.DIM}Model: {model_name}{Colors.RESET}"
                print(msg)

        prompt = (f"\n{Colors.BRIGHT_CYAN}Press Enter to "
                  f"continue...{Colors.RESET}")
        input(prompt)

    def view_available_models(self):
        """View all available models with details"""
        sep = "+" + "=" * 62 + "+"
        msg = f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}{sep}{Colors.RESET}"
        print(msg)
        msg = (f"{Colors.BRIGHT_CYAN}{Colors.BOLD}|  "
               f"AVAILABLE MODELS{Colors.RESET}")
        print(msg)
        msg = f"{Colors.BRIGHT_CYAN}{Colors.BOLD}{sep}{Colors.RESET}\n"
        print(msg)

        optimal = ModelDatabase.get_optimal_models()

        msg = (f"{Colors.BRIGHT_GREEN}OPTIMAL FOR 4060 Ti (Recommended):"
               f"{Colors.RESET}\n")
        print(msg)
        for model_id, model_data in optimal.items():
            print(f"  {Colors.BRIGHT_GREEN}✓{Colors.RESET} {model_id}")
            print(f"    Name: {model_data['name']}")
            msg = (f"    Size: {model_data['size_gb']}GB | "
                   f"Speed: {model_data['speed']}")
            print(msg)
            print(f"    Use: {model_data['use_case']}\n")

        msg = (f"\n{Colors.BRIGHT_YELLOW}AVAILABLE BUT TIGHT FIT:"
               f"{Colors.RESET}\n")
        print(msg)
        for model_id, model_data in self.models.items():
            if model_id not in optimal:
                msg = (f"  {Colors.BRIGHT_YELLOW}⚠{Colors.RESET} "
                       f"{model_id}")
                print(msg)
                print(f"    Name: {model_data['name']}")
                msg = (f"    Size: {model_data['size_gb']}GB | "
                       f"Speed: {model_data['speed']}")
                print(msg)
                print(f"    Notes: {model_data['notes']}\n")

        prompt = (f"{Colors.BRIGHT_CYAN}Press Enter to "
                  f"continue...{Colors.RESET}")
        input(prompt)

    def start_api_server(self):
        """Start REST API server (requires Flask)"""
        if not FLASK_AVAILABLE:
            msg = (f"{Colors.BRIGHT_RED}Flask not installed. "
                   f"Install with: pip install flask{Colors.RESET}")
            print(msg)
            return

        msg = (f"\n{Colors.BRIGHT_GREEN}Starting REST API Server..."
               f"{Colors.RESET}")
        print(msg)
        msg = (f"API will be available at: "
               f"http://10.0.0.89:{self.api_port}")
        print(msg)
        print("Type Ctrl+C to stop the server\n")

        self._setup_api_routes()
        self.api_app.run(host='0.0.0.0', port=self.api_port,
                         debug=False)

    def _setup_api_routes(self):
        """Setup Flask API routes"""
        from flask import Flask, request, jsonify  # noqa: F401

        self.api_app = Flask(__name__)

        @self.api_app.route('/api/health', methods=['GET'])
        def health():
            usage = VRAMMonitor.get_vram_usage()
            return jsonify({
                "status": "healthy",
                "gpu_vram": {
                    "used_gb": round(usage['used'], 2),
                    "total_gb": usage['total'],
                    "free_gb": round(usage['free'], 2),
                    "percent": round(usage['percent'], 1)
                }
            })

        @self.api_app.route('/api/models', methods=['GET'])
        def list_models():
            optimal = ModelDatabase.get_optimal_models()
            models_data = {k: {"name": v['name'], "size_gb": v['size_gb']}
                           for k, v in self.models.items()}
            return jsonify({
                "total": len(self.models),
                "optimal": len(optimal),
                "models": models_data
            })

        @self.api_app.route('/api/projects', methods=['GET'])
        def list_projects():
            projects = self.project_manager.list_projects()
            return jsonify({"projects": projects})

        @self.api_app.route('/api/infer', methods=['POST'])
        def infer():
            data = request.json
            model_id = data.get('model_id')
            prompt = data.get('prompt')

            if not model_id or not prompt:
                return jsonify({"error": "Missing model_id or prompt"}), 400

            if model_id not in self.models:
                return jsonify({"error": f"Model {model_id} not found"}), 404

            model_data = self.models[model_id]

            # Check VRAM
            usage = VRAMMonitor.get_vram_usage()
            if usage['free'] < model_data['size_gb'] + 0.5:
                err_msg = (f"Insufficient VRAM. Need "
                           f"{model_data['size_gb']}GB, have "
                           f"{usage['free']:.2f}GB")
                return jsonify({"error": err_msg}), 507

            # Run model (simplified - in production, use async/queue)
            try:
                self._run_llamacpp_model(model_data, prompt, "", {})
                return jsonify({"status": "success",
                                "message": "Model executed"})
            except Exception as e:
                return jsonify({"error": str(e)}), 500

    def settings_menu(self):
        """Settings menu"""
        while True:
            sep = "+" + "=" * 62 + "+"
            msg = f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}{sep}{Colors.RESET}"
            print(msg)
            msg = (f"{Colors.BRIGHT_CYAN}{Colors.BOLD}|  "
                   f"SETTINGS{Colors.RESET}")
            print(msg)
            msg = f"{Colors.BRIGHT_CYAN}{Colors.BOLD}{sep}{Colors.RESET}\n"
            print(msg)

            msg = (f"{Colors.BRIGHT_GREEN}[1]{Colors.RESET} "
                   f"View Current Project Info")
            print(msg)
            print(f"{Colors.BRIGHT_GREEN}[2]{Colors.RESET} Delete Project")
            msg = (f"{Colors.BRIGHT_GREEN}[3]{Colors.RESET} "
                   f"Check System Info")
            print(msg)
            msg = (f"{Colors.BRIGHT_GREEN}[0]{Colors.RESET} "
                   f"Return to main menu")
            print(msg)

            prompt = f"\n{Colors.BRIGHT_YELLOW}Enter choice: {Colors.RESET}"
            choice = input(prompt).strip()

            if choice == "1":
                if self.current_project:
                    config = self.project_manager.load_project(
                        self.current_project)
                    if config:
                        msg = (f"\n{Colors.BRIGHT_WHITE}Current Project:"
                               f"{Colors.RESET}")
                        print(msg)
                        print(json.dumps(config, indent=2))
                else:
                    msg = (f"\n{Colors.BRIGHT_YELLOW}No project loaded."
                           f"{Colors.RESET}")
                    print(msg)
                prompt = (f"\n{Colors.BRIGHT_CYAN}Press Enter to "
                          f"continue...{Colors.RESET}")
                input(prompt)
            elif choice == "2":
                projects = self.project_manager.list_projects()
                if projects:
                    print(f"\n{Colors.BRIGHT_WHITE}Projects:{Colors.RESET}\n")
                    for idx, proj in enumerate(projects, 1):
                        msg = (f"{Colors.BRIGHT_GREEN}[{idx}]{Colors.RESET} "
                               f"{proj}")
                        print(msg)

                    prompt = (f"\n{Colors.BRIGHT_YELLOW}Delete project "
                              f"number (0 to cancel): {Colors.RESET}")
                    del_choice = input(prompt).strip()
                    try:
                        idx = int(del_choice) - 1
                        if 0 <= idx < len(projects):
                            proj_name = projects[idx]
                            prompt = (f"{Colors.BRIGHT_RED}Really delete "
                                      f"'{proj_name}'? [y/N]: "
                                      f"{Colors.RESET}")
                            confirm = input(prompt).strip().lower()
                            if confirm == 'y':
                                self.project_manager.delete_project(proj_name)
                                if self.current_project == proj_name:
                                    self.current_project = None
                                    self.current_memory = None
                    except Exception:
                        pass
                else:
                    msg = (f"\n{Colors.BRIGHT_YELLOW}No projects to delete."
                           f"{Colors.RESET}")
                    print(msg)
                prompt = (f"\n{Colors.BRIGHT_CYAN}Press Enter to "
                          f"continue...{Colors.RESET}")
                input(prompt)
            elif choice == "3":
                self._show_system_info()
            elif choice == "0":
                break

    def _show_system_info(self):
        """Show system information"""
        msg = (f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}System Information:"
               f"{Colors.RESET}\n")
        print(msg)
        print(f"Platform: {self.platform}")
        print(f"Python: {sys.version}")
        print(f"CPU Cores: {psutil.cpu_count()}")
        ram_gb = psutil.virtual_memory().total / (1024**3)
        print(f"RAM: {ram_gb:.2f}GB")

        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]
                print(f"\nGPU: {gpu.name}")
                print(f"CUDA Capability: {gpu.driver}")
                print(f"VRAM: {gpu.memoryTotal}MB")
        except Exception:
            print("\nGPU: Unable to detect")

        print()
        prompt = (f"{Colors.BRIGHT_CYAN}Press Enter to "
                  f"continue...{Colors.RESET}")
        input(prompt)


def main():
    """Main entry point"""
    try:
        router = TrueNASAIRouter()
        router.main_menu()
    except KeyboardInterrupt:
        msg = (f"\n\n{Colors.BRIGHT_YELLOW}Interrupted by user. "
               f"Goodbye!{Colors.RESET}\n")
        print(msg)
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.BRIGHT_RED}Error: {e}{Colors.RESET}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
