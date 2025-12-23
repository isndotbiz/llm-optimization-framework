#!/usr/bin/env python3
"""
AI Router Enhanced - Complete AI Project Management System
Features: Projects, Bots, Multi-Provider Support, Web Search, Memory, MCP Tools
Version: 2.0
Author: Enhanced AI Router System
Date: 2025-12-08
"""

import os
import sys
import json
import subprocess
import platform
import shutil
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from logging_config_v2 import setup_structured_logging, set_trace_id

# Import centralized model configuration (single source of truth)
from config.models import ModelDatabase


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


class ProjectManager:
    """Manages AI projects with configurations and memory"""

    def __init__(self, projects_dir: Path):
        self.projects_dir = projects_dir
        self.projects_dir.mkdir(parents=True, exist_ok=True)
        self.current_project = None
        self.current_config = None

    def create_project(self, project_name: str, config: Dict[str, Any]) -> bool:  # noqa: E501
        """Create a new project with configuration"""
        try:
            project_path = self.projects_dir / project_name
            if project_path.exists():
                print(
                    f"{Colors.BRIGHT_RED}Project '{project_name}' "
                    f"already exists!{Colors.RESET}"
                )
                return False

            # Create project structure
            project_path.mkdir(parents=True, exist_ok=True)
            (project_path / "data").mkdir(exist_ok=True)

            # Save configuration
            config_path = project_path / "config.json"
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)

            # Initialize empty memory
            memory_path = project_path / "memory.json"
            with open(memory_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "conversations": [],
                    "created": datetime.now().isoformat(),
                    "modified": datetime.now().isoformat()
                }, f, indent=2)

            print(
                f"{Colors.BRIGHT_GREEN}Project '{project_name}' "
                f"created successfully!{Colors.RESET}"
            )
            return True
        except Exception as e:
            print(
                f"{Colors.BRIGHT_RED}Error creating project: "
                f"{e}{Colors.RESET}"
            )
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
                print(
                    f"{Colors.BRIGHT_RED}Project configuration not "
                    f"found!{Colors.RESET}"
                )
                return None

            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            self.current_project = project_name
            self.current_config = config
            return config
        except Exception as e:
            print(
                f"{Colors.BRIGHT_RED}Error loading project: "
                f"{e}{Colors.RESET}"
            )
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
            print(
                f"{Colors.BRIGHT_RED}Error saving project: "
                f"{e}{Colors.RESET}"
            )
            return False

    def delete_project(self, project_name: str) -> bool:
        """Delete a project"""
        try:
            project_path = self.projects_dir / project_name
            if project_path.exists():
                shutil.rmtree(project_path)
                print(
                    f"{Colors.BRIGHT_GREEN}Project '{project_name}' "
                    f"deleted successfully!{Colors.RESET}"
                )
                return True
            return False
        except Exception as e:
            print(
                f"{Colors.BRIGHT_RED}Error deleting project: "
                f"{e}{Colors.RESET}"
            )
            return False


class BotManager:
    """Manages bot templates and specialized bots"""

    def __init__(self, bots_dir: Path):
        self.bots_dir = bots_dir
        self.bots_dir.mkdir(parents=True, exist_ok=True)

    def list_bot_templates(self) -> List[Tuple[str, Dict[str, Any]]]:
        """List all available bot templates"""
        templates = []
        try:
            for bot_file in self.bots_dir.glob("*.json"):
                with open(bot_file, 'r', encoding='utf-8') as f:
                    bot_data = json.load(f)
                    templates.append((bot_file.stem, bot_data))
        except Exception as e:
            print(
                f"{Colors.BRIGHT_YELLOW}Warning: Could not load "
                f"bot templates: {e}{Colors.RESET}"
            )
        return templates

    def load_bot_template(self, bot_name: str) -> Optional[Dict[str, Any]]:
        """Load a specific bot template"""
        try:
            bot_path = self.bots_dir / f"{bot_name}.json"
            if not bot_path.exists():
                return None

            with open(bot_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(
                f"{Colors.BRIGHT_RED}Error loading bot template: "
                f"{e}{Colors.RESET}"
            )
            return None

    def create_bot_from_template(
        self,
        template_name: str,
        project_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a project configuration from a bot template"""
        template = self.load_bot_template(template_name)
        if not template:
            return project_config

        # Merge template with project config
        project_config.update({
            "title": template.get("title", "Untitled Project"),
            "model": template.get("model", "qwen3-coder-30b"),
            "system_prompt": template.get("system_prompt", ""),
            "parameters": template.get("default_parameters", {}),
            "provider": template.get("provider", "llama-cpp"),
            "specialization": template.get("specialization", "general")
        })

        return project_config


class ProviderManager:
    """Manages different AI providers (llama-cpp, ollama, openrouter, etc.)"""

    SUPPORTED_PROVIDERS = {
        "llama-cpp": {
            "name": "llama.cpp",
            "description": "Local model execution with llama.cpp",
            "requires_api_key": False
        },
        "ollama": {
            "name": "Ollama",
            "description": "Local model execution with Ollama",
            "requires_api_key": False
        },
        "openrouter": {
            "name": "OpenRouter",
            "description": "Access to multiple models via OpenRouter API",
            "requires_api_key": True
        },
        "openai": {
            "name": "OpenAI",
            "description": "OpenAI GPT models",
            "requires_api_key": True
        },
        "claude": {
            "name": "Anthropic Claude",
            "description": "Claude models via Anthropic API",
            "requires_api_key": True
        }
    }

    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.config_file = config_dir / "providers.json"
        self.providers_config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load provider configuration"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def _save_config(self):
        """Save provider configuration"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.providers_config, f, indent=2)
        except Exception as e:
            print(
                f"{Colors.BRIGHT_RED}Error saving provider config: "
                f"{e}{Colors.RESET}"
            )

    def configure_provider(self, provider_name: str, api_key: Optional[str] = None):  # noqa: E501
        """Configure a provider with API key if needed"""
        if provider_name not in self.SUPPORTED_PROVIDERS:
            print(
                f"{Colors.BRIGHT_RED}Provider '{provider_name}' "
                f"not supported!{Colors.RESET}"
            )
            return False

        provider_info = self.SUPPORTED_PROVIDERS[provider_name]

        if provider_info["requires_api_key"] and not api_key:
            print(
                f"{Colors.BRIGHT_YELLOW}API key required for "
                f"{provider_info['name']}{Colors.RESET}"
            )
            return False

        self.providers_config[provider_name] = {
            "enabled": True,
            "api_key": api_key if api_key else None,
            "configured": datetime.now().isoformat()
        }
        self._save_config()
        return True

    def get_provider_for_model(self, model_id: str) -> str:
        """Auto-detect provider based on model"""
        # For now, just check if it's an MLX model or llama.cpp model
        if "mlx" in model_id.lower():
            return "llama-cpp"  # MLX uses similar interface
        return "llama-cpp"


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
            print(
                f"{Colors.BRIGHT_RED}Error saving memory: "
                f"{e}{Colors.RESET}"
            )

    def add_conversation(self, user_prompt: str, model_response: str, model_id: str):  # noqa: E501
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
        self,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent conversations"""
        return self.memory["conversations"][-limit:]

    def clear_memory(self):
        """Clear all conversation memory"""
        self.memory["conversations"] = []
        self._save_memory()
        print(f"{Colors.BRIGHT_GREEN}Memory cleared!{Colors.RESET}")


class WebSearchManager:
    """Manages web search integration"""

    SUPPORTED_APIS = {
        "brave": {
            "name": "Brave Search API",
            "description": "Brave Search for web results"
        },
        "perplexity": {
            "name": "Perplexity API",
            "description": "Perplexity AI for search and answers"
        }
    }

    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.config_file = config_dir / "websearch.json"
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load web search configuration"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {"enabled": False, "apis": {}}

    def _save_config(self):
        """Save web search configuration"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(
                f"{Colors.BRIGHT_RED}Error saving web search config: "
                f"{e}{Colors.RESET}"
            )

    def configure_api(self, api_name: str, api_key: str):
        """Configure a web search API"""
        if api_name not in self.SUPPORTED_APIS:
            print(
                f"{Colors.BRIGHT_RED}API '{api_name}' "
                f"not supported!{Colors.RESET}"
            )
            return False

        if "apis" not in self.config:
            self.config["apis"] = {}

        self.config["apis"][api_name] = {
            "api_key": api_key,
            "configured": datetime.now().isoformat()
        }
        self.config["enabled"] = True
        self._save_config()
        return True


class EnhancedAIRouter:
    """Enhanced AI Router with full project management"""

    def __init__(self):
        self.platform = platform.system()
        self.models = ModelDatabase.get_platform_models()
        self.all_models = ModelDatabase.get_all_models()

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
        self.logger.info(f"AI Router Enhanced initialized on {self.platform}")

        # Lazy-loaded managers (initialized on first use for faster startup)
        self._project_manager = None
        self._bot_manager = None
        self._provider_manager = None
        self._websearch_manager = None

        # Current session state
        self.current_project = None
        self.current_memory = None

        # Bypass mode
        self.bypass_mode = False
        self.config_file = self.models_dir / ".ai-router-config.json"
        self._load_config()

    def _load_config(self):
        """Load configuration from JSON file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.bypass_mode = config.get('bypass_mode', False)
        except Exception as e:
            print(
                f"{Colors.BRIGHT_YELLOW}Warning: Could not load "
                f"config: {e}{Colors.RESET}"
            )
            self.bypass_mode = False

    def _save_config(self):
        """Save configuration to JSON file"""
        try:
            config = {
                'bypass_mode': self.bypass_mode,
                'version': '2.0'
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"{Colors.BRIGHT_RED}Error saving config: {e}{Colors.RESET}")

    # Lazy-loading properties for managers (performance optimization)
    @property
    def project_manager(self):
        """Lazy-load project manager on first access"""
        if self._project_manager is None:
            self.logger.debug("Initializing ProjectManager (lazy load)")
            self._project_manager = ProjectManager(self.models_dir / "projects")
        return self._project_manager

    @property
    def bot_manager(self):
        """Lazy-load bot manager on first access"""
        if self._bot_manager is None:
            self.logger.debug("Initializing BotManager (lazy load)")
            self._bot_manager = BotManager(self.models_dir / "bots")
        return self._bot_manager

    @property
    def provider_manager(self):
        """Lazy-load provider manager on first access"""
        if self._provider_manager is None:
            self.logger.debug("Initializing ProviderManager (lazy load)")
            self._provider_manager = ProviderManager(self.models_dir)
        return self._provider_manager

    @property
    def websearch_manager(self):
        """Lazy-load web search manager on first access"""
        if self._websearch_manager is None:
            self.logger.debug("Initializing WebSearchManager (lazy load)")
            self._websearch_manager = WebSearchManager(self.models_dir)
        return self._websearch_manager

    def _confirm(
        self,
        prompt_message: str,
        default_yes: bool = True
    ) -> bool:
        """Smart confirmation that respects bypass mode"""
        if self.bypass_mode:
            print(f"{Colors.DIM}{prompt_message} [Auto-accepted]{Colors.RESET}")  # noqa: E501
            return default_yes

        response = input(f"{prompt_message} ").strip().lower()
        if default_yes:
            return response in ['', 'y', 'yes']
        else:
            return response in ['y', 'yes']

    def _validate_resources_for_model(self, model_data: Dict[str, Any]) -> bool:  # noqa: E501
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
            return True  # Assume OK if timeout (WSL might be slow but working)
        except Exception as e:
            self.logger.warning(f"Resource validation error: {e}")
            return True  # Be permissive on validation errors

    def _get_fallback_model(self, model_id: str) -> Optional[str]:
        """Get a smaller fallback model if primary model fails"""
        fallback_map = {
            "qwen3-coder-30b": "dolphin-llama31-8b",      # 18GB -> 6GB
            "llama33-70b": "ministral-3-14b",              # 21GB -> 9GB
            "phi4-14b": "dolphin-llama31-8b",              # 12GB -> 6GB
            "dolphin-mistral-24b": "wizard-vicuna-13b",    # 14GB -> 7GB
            "gemma3-27b": "dolphin-llama31-8b",            # 10GB -> 6GB
        }

        fallback_id = fallback_map.get(model_id)
        if fallback_id and fallback_id in self.all_models:
            self.logger.info(f"Fallback model for {model_id}: {fallback_id}")
            return fallback_id
        return None

    def print_banner(self):
        """Print colorful banner"""
        print(f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}")
        print(
            "+========================================"
            "========================================"
        )
        print(
            "|                                        "
            "                                        |"
        )
        print(
            "|                    AI ROUTER ENHANCED "
            "v2.0 - Project Edition                  |"
        )
        print(
            "|                                        "
            "                                        |"
        )
        print(
            "|         Complete AI Project Management"
            " with Multi-Provider Support            |"
        )
        print(
            "|                   Based on 2025 "
            "Research (Sep-Nov 2025)                       |"
        )
        print(
            "|                                        "
            "                                        |"
        )
        print(
            "+========================================"
            "========================================"
        )
        print(Colors.RESET)

        # Bypass mode indicator
        if self.bypass_mode:
            print(
                f"\n{Colors.BG_YELLOW}{Colors.BLACK}{Colors.BOLD} "
                f"AUTO-YES MODE ACTIVE {Colors.RESET}"
            )

        # Current project indicator
        if self.current_project:
            print(
                f"\n{Colors.BRIGHT_GREEN}Current Project: "
                f"{Colors.BRIGHT_WHITE}{self.current_project}"
                f"{Colors.RESET}"
            )

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

    def main_menu(self):
        """Display and handle main menu"""
        while True:
            self.print_banner()

            print(
                f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}"
                f"+=============================================="
                f"================+{Colors.RESET}"
            )
            print(
                f"{Colors.BRIGHT_CYAN}{Colors.BOLD}|  MAIN MENU"
                f"{Colors.RESET}"
            )
            print(
                f"{Colors.BRIGHT_CYAN}{Colors.BOLD}"
                f"+=============================================="
                f"================+{Colors.RESET}\n"
            )

            print(f"{Colors.BRIGHT_GREEN}[1]{Colors.RESET}  Create New Project")  # noqa: E501
            print(f"{Colors.BRIGHT_GREEN}[2]{Colors.RESET}  Load Existing Project")  # noqa: E501
            print(
                f"{Colors.BRIGHT_GREEN}[3]{Colors.RESET}  "
                f"Create Specialized Bot (from templates)"
            )
            print(f"{Colors.BRIGHT_GREEN}[4]{Colors.RESET}  View/Edit System Prompt")  # noqa: E501
            print(f"{Colors.BRIGHT_GREEN}[5]{Colors.RESET}  Configure Parameters")  # noqa: E501
            print(f"{Colors.BRIGHT_GREEN}[6]{Colors.RESET}  Run Chat Session")
            print(f"{Colors.BRIGHT_GREEN}[7]{Colors.RESET}  View Conversation History")  # noqa: E501
            print(f"{Colors.BRIGHT_GREEN}[8]{Colors.RESET}  Configure Web Search")  # noqa: E501
            print(f"{Colors.BRIGHT_GREEN}[9]{Colors.RESET}  Configure Providers")  # noqa: E501
            print(f"{Colors.BRIGHT_GREEN}[10]{Colors.RESET} View Documentation")  # noqa: E501

            if self.bypass_mode:
                bypass_status = f"{Colors.BRIGHT_GREEN}ON{Colors.RESET}"
            else:
                bypass_status = f"{Colors.BRIGHT_RED}OFF{Colors.RESET}"
            print(
                f"{Colors.BRIGHT_GREEN}[11]{Colors.RESET} "
                f"Settings (Bypass: {bypass_status})"
            )
            print(f"{Colors.BRIGHT_GREEN}[12]{Colors.RESET} Exit")

            choice = input(
                f"\n{Colors.BRIGHT_YELLOW}Enter choice [1-12]: "
                f"{Colors.RESET}"
            ).strip()

            if choice == "1":
                self.create_new_project()
            elif choice == "2":
                self.load_existing_project()
            elif choice == "3":
                self.create_specialized_bot()
            elif choice == "4":
                self.view_edit_system_prompt()
            elif choice == "5":
                self.configure_parameters()
            elif choice == "6":
                self.run_chat_session()
            elif choice == "7":
                self.view_conversation_history()
            elif choice == "8":
                self.configure_web_search()
            elif choice == "9":
                self.configure_providers()
            elif choice == "10":
                self.view_documentation()
            elif choice == "11":
                self.settings_menu()
            elif choice == "12":
                print(f"\n{Colors.BRIGHT_GREEN}Goodbye!{Colors.RESET}\n")
                sys.exit(0)
            else:
                print(
                    f"{Colors.BRIGHT_RED}Invalid choice. "
                    f"Please try again.{Colors.RESET}"
                )
                input(f"\n{Colors.BRIGHT_CYAN}Press Enter to continue...{Colors.RESET}")  # noqa: E501

    def create_new_project(self):
        """Create a new project with interactive configuration"""
        print(  # noqa: E501
                    f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}+==============================================================+{Colors.RESET}"  # noqa: E501
            )
        print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}|  CREATE NEW PROJECT{Colors.RESET}")  # noqa: E501
        print(  # noqa: E501
                    f"{Colors.BRIGHT_CYAN}{Colors.BOLD}+==============================================================+{Colors.RESET}\n"  # noqa: E501
            )

        # Get project name
        project_name = input(f"{Colors.BRIGHT_WHITE}Project name: {Colors.RESET}").strip()  # noqa: E501
        if not project_name:
            print(  # noqa: E501
                    f"{Colors.BRIGHT_RED}Project name cannot be empty!{Colors.RESET}"  # noqa: E501
            )
            input(f"\n{Colors.BRIGHT_CYAN}Press Enter to continue...{Colors.RESET}")  # noqa: E501
            return

        # Get project title
        title = input(f"{Colors.BRIGHT_WHITE}Project title (display name): {Colors.RESET}").strip()  # noqa: E501
        if not title:
            title = project_name

        # Select model
        print(f"\n{Colors.BRIGHT_WHITE}Available models:{Colors.RESET}\n")
        model_ids = list(self.models.keys())
        for idx, model_id in enumerate(model_ids, 1):
            model_data = self.models[model_id]
            print(f"{Colors.BRIGHT_GREEN}[{idx}]{Colors.RESET} {model_id} - {model_data['name']}")  # noqa: E501

        model_choice = input(f"\n{Colors.BRIGHT_YELLOW}Select model [1-{len(model_ids)}]: {Colors.RESET}").strip()  # noqa: E501
        try:
            model_idx = int(model_choice) - 1
            if 0 <= model_idx < len(model_ids):
                model_id = model_ids[model_idx]
                model_data = self.models[model_id]
            else:
                print(  # noqa: E501
                        f"{Colors.BRIGHT_RED}Invalid model selection!{Colors.RESET}"  # noqa: E501
                )
                input(f"\n{Colors.BRIGHT_CYAN}Press Enter to continue...{Colors.RESET}")  # noqa: E501
                return
        except ValueError:
            print(f"{Colors.BRIGHT_RED}Invalid input!{Colors.RESET}")  # noqa: E501
            input(f"\n{Colors.BRIGHT_CYAN}Press Enter to continue...{Colors.RESET}")  # noqa: E501
            return

        # Get system prompt (if model supports it)
        system_prompt = ""
        if model_data.get('system_prompt'):
            print(f"\n{Colors.BRIGHT_WHITE}System prompt (leave empty for default):{Colors.RESET}")  # noqa: E501
            custom_prompt = input(f"{Colors.CYAN}> {Colors.RESET}").strip()
            if custom_prompt:
                system_prompt = custom_prompt
        else:
            print(f"\n{Colors.BRIGHT_YELLOW}Note: Model '{model_id}' does not support system prompts.{Colors.RESET}")  # noqa: E501

        # Get parameters with defaults
        print(f"\n{Colors.BRIGHT_WHITE}Configure parameters (press Enter for defaults):{Colors.RESET}\n")  # noqa: E501

        temperature = self._get_float_input("Temperature", model_data['temperature'], 0.0, 2.0)  # noqa: E501
        top_p = self._get_float_input("Top P", model_data['top_p'], 0.0, 1.0)
        top_k = self._get_int_input("Top K", model_data['top_k'], 0, 200)
        max_tokens = self._get_int_input("Max tokens", 4096, 1, 32768)
        context_limit = self._get_int_input("Context limit (messages, -1 for unlimited)", 50, -1, 32768)  # noqa: E501
        presence_penalty = self._get_float_input("Presence penalty", 0.0, -2.0, 2.0)  # noqa: E501
        frequency_penalty = self._get_float_input("Frequency penalty", 0.0, -2.0, 2.0)  # noqa: E501

        # Create project config
        config = {
            "title": title,
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
            "model": model_id,
            "provider": "llama-cpp",
            "system_prompt": system_prompt,
            "parameters": {
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k,
                "max_tokens": max_tokens,
                "context_limit": context_limit,
                "presence_penalty": presence_penalty,
                "frequency_penalty": frequency_penalty
            },
            "web_search": {
                "enabled": False
            },
            "reasoning_effort": "none"  # none/low/medium/high - currently no models support this  # noqa: E501
        }

        # Create the project
        if self.project_manager.create_project(project_name, config):
            self.current_project = project_name
            project_path = self.models_dir / "projects" / project_name
            self.current_memory = MemoryManager(project_path)
            print(f"\n{Colors.BRIGHT_GREEN}Project '{project_name}' created and loaded!{Colors.RESET}")  # noqa: E501

        input(f"\n{Colors.BRIGHT_CYAN}Press Enter to continue...{Colors.RESET}")  # noqa: E501

    def _get_float_input(
        self,
        param_name: str,
        default: float,
        min_val: float,
        max_val: float
    ) -> float:
        """Get float input with validation"""
        prompt = (
            f"{Colors.WHITE}{param_name} [{min_val}-{max_val}] "
            f"(default: {default}): {Colors.RESET}"
        )
        while True:
            value = input(prompt).strip()
            if not value:
                return default
            try:
                value = float(value)
                if min_val <= value <= max_val:
                    return value
                else:
                    print(
                        f"{Colors.BRIGHT_RED}Value must be between "
                        f"{min_val} and {max_val}!{Colors.RESET}"
                    )
            except ValueError:
                print(f"{Colors.BRIGHT_RED}Invalid number!{Colors.RESET}")

    def _get_int_input(
        self,
        param_name: str,
        default: int,
        min_val: int,
        max_val: int
    ) -> int:
        """Get integer input with validation"""
        prompt = (
            f"{Colors.WHITE}{param_name} [{min_val}-{max_val}] "
            f"(default: {default}): {Colors.RESET}"
        )
        while True:
            value = input(prompt).strip()
            if not value:
                return default
            try:
                value = int(value)
                if min_val <= value <= max_val:
                    return value
                else:
                    print(
                        f"{Colors.BRIGHT_RED}Value must be between "
                        f"{min_val} and {max_val}!{Colors.RESET}"
                    )
            except ValueError:
                print(f"{Colors.BRIGHT_RED}Invalid number!{Colors.RESET}")

    def load_existing_project(self):
        """Load an existing project"""
        print(  # noqa: E501
                    f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}+==============================================================+{Colors.RESET}"  # noqa: E501
            )
        print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}|  LOAD PROJECT{Colors.RESET}")  # noqa: E501
        print(  # noqa: E501
                    f"{Colors.BRIGHT_CYAN}{Colors.BOLD}+==============================================================+{Colors.RESET}\n"  # noqa: E501
            )

        projects = self.project_manager.list_projects()
        if not projects:
            print(  # noqa: E501
                    f"{Colors.BRIGHT_YELLOW}No projects found. Create one first!{Colors.RESET}"  # noqa: E501
            )
            input(f"\n{Colors.BRIGHT_CYAN}Press Enter to continue...{Colors.RESET}")  # noqa: E501
            return

        print(f"{Colors.BRIGHT_WHITE}Available projects:{Colors.RESET}\n")
        for idx, project in enumerate(projects, 1):
            print(f"{Colors.BRIGHT_GREEN}[{idx}]{Colors.RESET} {project}")

        print(f"{Colors.BRIGHT_GREEN}[0]{Colors.RESET} Return to menu")

        choice = input(
            f"\n{Colors.BRIGHT_YELLOW}Select project "
            f"[0-{len(projects)}]: {Colors.RESET}"
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
                    project_path = self.models_dir / "projects" / project_name
                    self.current_memory = MemoryManager(project_path)

                    print(f"\n{Colors.BRIGHT_GREEN}Project '{project_name}' loaded successfully!{Colors.RESET}")  # noqa: E501
                    print(f"\n{Colors.BRIGHT_WHITE}Project Details:{Colors.RESET}")  # noqa: E501
                    print(f"  Title: {Colors.CYAN}{config.get('title', 'Untitled')}{Colors.RESET}")  # noqa: E501
                    print(f"  Model: {Colors.CYAN}{config.get('model', 'Not set')}{Colors.RESET}")  # noqa: E501
                    print(f"  Provider: {Colors.CYAN}{config.get('provider', 'llama-cpp')}{Colors.RESET}")  # noqa: E501
            else:
                print(f"{Colors.BRIGHT_RED}Invalid selection!{Colors.RESET}")  # noqa: E501
        except ValueError:
            print(f"{Colors.BRIGHT_RED}Invalid input!{Colors.RESET}")  # noqa: E501

        input(f"\n{Colors.BRIGHT_CYAN}Press Enter to continue...{Colors.RESET}")  # noqa: E501

    def create_specialized_bot(self):
        """Create a project from a bot template"""
        print(  # noqa: E501
                    f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}+==============================================================+{Colors.RESET}"  # noqa: E501
            )
        print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}|  CREATE SPECIALIZED BOT{Colors.RESET}")  # noqa: E501
        print(  # noqa: E501
                    f"{Colors.BRIGHT_CYAN}{Colors.BOLD}+==============================================================+{Colors.RESET}\n"  # noqa: E501
            )

        templates = self.bot_manager.list_bot_templates()
        if not templates:
            print(f"{Colors.BRIGHT_YELLOW}No bot templates found!{Colors.RESET}")  # noqa: E501
            input(f"\n{Colors.BRIGHT_CYAN}Press Enter to continue...{Colors.RESET}")  # noqa: E501
            return

        print(f"{Colors.BRIGHT_WHITE}Available bot templates:{Colors.RESET}\n")
        for idx, (template_name, template_data) in enumerate(templates, 1):
            print(f"{Colors.BRIGHT_GREEN}[{idx}]{Colors.RESET} {Colors.BRIGHT_WHITE}{template_data.get('title', template_name)}{Colors.RESET}")  # noqa: E501
            print(f"    {Colors.CYAN}{template_data.get('description', 'No description')}{Colors.RESET}")  # noqa: E501
            print(f"    {Colors.YELLOW}Model: {template_data.get('model', 'Not specified')}{Colors.RESET}\n")  # noqa: E501

        print(f"{Colors.BRIGHT_GREEN}[0]{Colors.RESET} Return to menu")

        choice = input(f"\n{Colors.BRIGHT_YELLOW}Select template [0-{len(templates)}]: {Colors.RESET}").strip()  # noqa: E501

        if choice == "0":
            return

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(templates):
                template_name, template_data = templates[idx]

                # Get project name
                project_name = input(f"\n{Colors.BRIGHT_WHITE}Project name for this bot: {Colors.RESET}").strip()  # noqa: E501
                if not project_name:
                    print(  # noqa: E501
                            f"{Colors.BRIGHT_RED}Project name cannot be empty!{Colors.RESET}"  # noqa: E501
                    )
                    input(f"\n{Colors.BRIGHT_CYAN}Press Enter to continue...{Colors.RESET}")  # noqa: E501
                    return

                # Create config from template
                config = {
                    "title": template_data.get("title", project_name),
                    "created": datetime.now().isoformat(),
                    "modified": datetime.now().isoformat(),
                    "model": template_data.get("model", "qwen3-coder-30b"),
                    "provider": template_data.get("provider", "llama-cpp"),
                    "system_prompt": template_data.get("system_prompt", ""),
                    "parameters": template_data.get("default_parameters", {}),
                    "web_search": {"enabled": False},
                    "specialization": template_data.get("specialization", "general"),  # noqa: E501
                    "reasoning_effort": "none"
                }

                # Create the project
                if self.project_manager.create_project(project_name, config):
                    self.current_project = project_name
                    project_path = self.models_dir / "projects" / project_name
                    self.current_memory = MemoryManager(project_path)
                    print(f"\n{Colors.BRIGHT_GREEN}Bot project '{project_name}' created and loaded!{Colors.RESET}")  # noqa: E501
            else:
                print(f"{Colors.BRIGHT_RED}Invalid selection!{Colors.RESET}")  # noqa: E501
        except ValueError:
            print(f"{Colors.BRIGHT_RED}Invalid input!{Colors.RESET}")  # noqa: E501

        input(f"\n{Colors.BRIGHT_CYAN}Press Enter to continue...{Colors.RESET}")  # noqa: E501

    def view_edit_system_prompt(self):
        """View or edit current system prompt"""
        if not self.current_project:
            print(f"\n{Colors.BRIGHT_YELLOW}No project loaded. Please load a project first.{Colors.RESET}")  # noqa: E501
            input(f"\n{Colors.BRIGHT_CYAN}Press Enter to continue...{Colors.RESET}")  # noqa: E501
            return

        print(  # noqa: E501
                    f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}+==============================================================+{Colors.RESET}"  # noqa: E501
            )
        print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}|  SYSTEM PROMPT{Colors.RESET}")  # noqa: E501
        print(  # noqa: E501
                    f"{Colors.BRIGHT_CYAN}{Colors.BOLD}+==============================================================+{Colors.RESET}\n"  # noqa: E501
            )

        config = self.project_manager.load_project(self.current_project)
        if not config:
            return

        current_prompt = config.get("system_prompt", "")

        if current_prompt:
            print(f"{Colors.BRIGHT_WHITE}Current system prompt:{Colors.RESET}\n")  # noqa: E501
            print(f"{Colors.CYAN}{current_prompt}{Colors.RESET}\n")
        else:
            print(f"{Colors.BRIGHT_YELLOW}No system prompt set.{Colors.RESET}\n")  # noqa: E501

        if self._confirm(f"{Colors.BRIGHT_WHITE}Would you like to edit the system prompt? [y/N]:{Colors.RESET}", default_yes=False):  # noqa: E501
            print(f"\n{Colors.BRIGHT_WHITE}Enter new system prompt (or 'clear' to remove):{Colors.RESET}")  # noqa: E501
            new_prompt = input(f"{Colors.CYAN}> {Colors.RESET}").strip()

            if new_prompt.lower() == 'clear':
                config["system_prompt"] = ""
                print(f"{Colors.BRIGHT_GREEN}System prompt cleared.{Colors.RESET}")  # noqa: E501
            elif new_prompt:
                config["system_prompt"] = new_prompt
                print(f"{Colors.BRIGHT_GREEN}System prompt updated.{Colors.RESET}")  # noqa: E501

            config["modified"] = datetime.now().isoformat()
            self.project_manager.save_project(self.current_project, config)

        input(f"\n{Colors.BRIGHT_CYAN}Press Enter to continue...{Colors.RESET}")  # noqa: E501

    def configure_parameters(self):
        """Configure model parameters for current project"""
        if not self.current_project:
            print(f"\n{Colors.BRIGHT_YELLOW}No project loaded. Please load a project first.{Colors.RESET}")  # noqa: E501
            input(f"\n{Colors.BRIGHT_CYAN}Press Enter to continue...{Colors.RESET}")  # noqa: E501
            return

        print(  # noqa: E501
                    f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}+==============================================================+{Colors.RESET}"  # noqa: E501
            )
        print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}|  CONFIGURE PARAMETERS{Colors.RESET}")  # noqa: E501
        print(  # noqa: E501
                    f"{Colors.BRIGHT_CYAN}{Colors.BOLD}+==============================================================+{Colors.RESET}\n"  # noqa: E501
            )

        config = self.project_manager.load_project(self.current_project)
        if not config:
            return

        params = config.get("parameters", {})

        print(f"{Colors.BRIGHT_WHITE}Current parameters:{Colors.RESET}\n")
        for key, value in params.items():
            print(f"  {Colors.CYAN}{key}: {Colors.WHITE}{value}{Colors.RESET}")

        print(f"\n{Colors.BRIGHT_WHITE}Update parameters (press Enter to keep current value):{Colors.RESET}\n")  # noqa: E501

        params["temperature"] = self._get_float_input("Temperature", params.get("temperature", 0.7), 0.0, 2.0)  # noqa: E501
        params["top_p"] = self._get_float_input("Top P", params.get("top_p", 0.9), 0.0, 1.0)  # noqa: E501
        params["top_k"] = self._get_int_input("Top K", params.get("top_k", 40), 0, 200)  # noqa: E501
        params["max_tokens"] = self._get_int_input("Max tokens", params.get("max_tokens", 4096), 1, 32768)  # noqa: E501
        params["context_limit"] = self._get_int_input("Context limit", params.get("context_limit", 50), -1, 32768)  # noqa: E501
        params["presence_penalty"] = self._get_float_input("Presence penalty", params.get("presence_penalty", 0.0), -2.0, 2.0)  # noqa: E501
        params["frequency_penalty"] = self._get_float_input("Frequency penalty", params.get("frequency_penalty", 0.0), -2.0, 2.0)  # noqa: E501

        config["parameters"] = params
        config["modified"] = datetime.now().isoformat()
        self.project_manager.save_project(self.current_project, config)

        print(f"\n{Colors.BRIGHT_GREEN}Parameters updated successfully!{Colors.RESET}")  # noqa: E501
        input(f"\n{Colors.BRIGHT_CYAN}Press Enter to continue...{Colors.RESET}")  # noqa: E501

    def run_chat_session(self):
        """Run an interactive chat session"""
        if not self.current_project:
            print(f"\n{Colors.BRIGHT_YELLOW}No project loaded. Please load a project first.{Colors.RESET}")  # noqa: E501
            input(f"\n{Colors.BRIGHT_CYAN}Press Enter to continue...{Colors.RESET}")  # noqa: E501
            return

        print(  # noqa: E501
                    f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}+==============================================================+{Colors.RESET}"  # noqa: E501
            )
        print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}|  CHAT SESSION{Colors.RESET}")  # noqa: E501
        print(  # noqa: E501
                    f"{Colors.BRIGHT_CYAN}{Colors.BOLD}+==============================================================+{Colors.RESET}\n"  # noqa: E501
            )

        config = self.project_manager.load_project(self.current_project)
        if not config:
            return

        model_id = config.get("model", "qwen3-coder-30b")
        if model_id not in self.all_models:
            print(f"{Colors.BRIGHT_RED}Model '{model_id}' not found!{Colors.RESET}")  # noqa: E501
            input(f"\n{Colors.BRIGHT_CYAN}Press Enter to continue...{Colors.RESET}")  # noqa: E501
            return

        model_data = self.all_models[model_id]

        print(f"{Colors.BRIGHT_WHITE}Project: {Colors.CYAN}{config.get('title', self.current_project)}{Colors.RESET}")  # noqa: E501
        print(f"{Colors.BRIGHT_WHITE}Model: {Colors.CYAN}{model_data['name']}{Colors.RESET}")  # noqa: E501
        print(f"{Colors.BRIGHT_WHITE}Type 'exit' or 'quit' to end session{Colors.RESET}\n")  # noqa: E501

        # Interactive chat loop
        while True:
            prompt = input(f"\n{Colors.BRIGHT_YELLOW}You: {Colors.RESET}").strip()  # noqa: E501

            if prompt.lower() in ['exit', 'quit', 'q']:
                print(f"{Colors.BRIGHT_GREEN}Chat session ended.{Colors.RESET}")  # noqa: E501
                break

            if not prompt:
                continue

            # Execute model
            print(f"\n{Colors.BRIGHT_CYAN}Assistant: {Colors.RESET}")
            self._run_model_with_config(model_id, model_data, prompt, config)

            # Save to memory (simplified - in production, capture actual response)  # noqa: E501
            if self.current_memory:
                self.current_memory.add_conversation(prompt, "[Response logged]", model_id)  # noqa: E501

        input(f"\n{Colors.BRIGHT_CYAN}Press Enter to continue...{Colors.RESET}")  # noqa: E501

    def _run_model_with_config(self, model_id: str, model_data: Dict[str, Any], prompt: str, config: Dict[str, Any], retry_count: int = 0, max_retries: int = 2):  # noqa: E501
        """Run model with project configuration and retry logic"""
        self.logger.info(f"Starting model execution: {model_id} ({model_data['name']})")  # noqa: E501

        # Validate resources before execution
        if not self._validate_resources_for_model(model_data):
            self.logger.error(f"Insufficient resources for model {model_id}")
            print(f"\n{Colors.BRIGHT_RED}Error: Insufficient system resources{Colors.RESET}")  # noqa: E501
            print(f"{Colors.BRIGHT_YELLOW}Model {model_data['name']} requires:{Colors.RESET}")  # noqa: E501
            print(f"{Colors.YELLOW}  - Available RAM: ~{model_data['size']} free{Colors.RESET}")  # noqa: E501
            print(f"{Colors.YELLOW}  - WSL must be running (for llama.cpp models){Colors.RESET}\n")  # noqa: E501

            # Try fallback to smaller model
            fallback_id = self._get_fallback_model(model_id)
            if fallback_id and retry_count == 0:
                print(f"{Colors.BRIGHT_CYAN}Trying fallback model: {self.all_models[fallback_id]['name']}{Colors.RESET}\n")  # noqa: E501
                return self._run_model_with_config(fallback_id, self.all_models[fallback_id], prompt, config, retry_count=1)  # noqa: E501
            return

        params = config.get("parameters", {})
        system_prompt = config.get("system_prompt", "")

        # Load system prompt from file if not custom
        if not system_prompt and model_data.get('system_prompt'):
            prompt_file = self.system_prompts_dir / model_data['system_prompt']
            if prompt_file.exists():
                try:
                    with open(prompt_file, 'r', encoding='utf-8') as f:
                        system_prompt = f.read().strip()
                except Exception as e:
                    self.logger.warning(f"Could not read system prompt: {e}")
                    print(f"{Colors.BRIGHT_YELLOW}Warning: Could not read system prompt: {e}{Colors.RESET}")  # noqa: E501

        print(f"\n{Colors.BRIGHT_GREEN}{Colors.BOLD}Launching {model_data['name']}...{Colors.RESET}\n")  # noqa: E501

        try:
            # Build command based on framework
            if model_data['framework'] == 'mlx':
                self._run_mlx_model(model_data, prompt, system_prompt, params)
            else:
                self._run_llamacpp_model(model_data, prompt, system_prompt, params)  # noqa: E501

            self.logger.info("Model execution completed successfully")

        except Exception as e:
            self.logger.error(f"Model execution failed: {e}")

            # Retry logic
            if retry_count < max_retries:
                retry_count += 1
                self.logger.warning(f"Retrying execution (attempt {retry_count + 1}/{max_retries + 1})...")  # noqa: E501
                print(f"\n{Colors.BRIGHT_YELLOW}Execution failed, retrying ({retry_count}/{max_retries})...{Colors.RESET}\n")  # noqa: E501
                time.sleep(2)  # Brief delay before retry
                return self._run_model_with_config(model_id, model_data, prompt, config, retry_count, max_retries)  # noqa: E501
            else:
                self.logger.error(f"All retry attempts exhausted for {model_id}")  # noqa: E501
                print(f"\n{Colors.BRIGHT_RED}Error: Model execution failed after {max_retries + 1} attempts{Colors.RESET}\n")  # noqa: E501

    def _run_llamacpp_model(self, model_data: Dict[str, Any], prompt: str, system_prompt: str, params: Dict[str, Any]):  # noqa: E501
        """Run model using llama.cpp"""
        self.logger.debug("Executing llama.cpp model")

        temperature = params.get("temperature", model_data['temperature'])
        top_p = params.get("top_p", model_data['top_p'])
        top_k = params.get("top_k", model_data['top_k'])
        max_tokens = params.get("max_tokens", 4096)

        special_flags = ' '.join(model_data['special_flags'])

        # Use the proper WSL detection function
        in_wsl = is_wsl()
        model_path = model_data['path']

        # Validate model file exists
        if in_wsl:
            # Check if file exists at the WSL path
            check_cmd = f'wsl test -f "{model_path}" && echo "exists"'
            result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)
            if "exists" not in result.stdout:
                self.logger.error(f"Model file not found: {model_path}")
                raise FileNotFoundError(f"Model file not found at: {model_path}")
        else:
            # Running in Windows - convert path for Windows and check
            win_path = model_path.replace("/mnt/d/", "D:\\").replace("/", "\\")
            if not Path(win_path).exists():
                self.logger.error(f"Model file not found: {win_path}")
                raise FileNotFoundError(f"Model file not found at: {win_path}")

        # Find llama.cpp binary - check multiple locations
        llama_cpp_paths = [
            "/mnt/d/workspace/llama.cpp/build/bin/llama-cli",
            "~/llama.cpp/build/bin/llama-cli",
            "llama-cli"  # System PATH
        ]

        llama_cli_path = None
        if in_wsl:
            for path in llama_cpp_paths:
                if path == "llama-cli":
                    check_cmd = 'wsl which llama-cli'
                else:
                    check_cmd = f'wsl test -f "{path}" && echo "exists"'
                result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)
                if "exists" in result.stdout or result.returncode == 0:
                    llama_cli_path = path
                    self.logger.info(f"Found llama.cpp at: {path}")
                    break
        else:
            for path in llama_cpp_paths:
                if path == "llama-cli":
                    check_cmd = 'wsl which llama-cli'
                    result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)
                    if result.returncode == 0:
                        llama_cli_path = "llama-cli"
                        break
                else:
                    check_cmd = f'wsl test -f "{path}" && echo "exists"'
                    result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)
                    if "exists" in result.stdout:
                        llama_cli_path = path
                        break

        if not llama_cli_path:
            self.logger.error(f"llama.cpp binary not found in: {', '.join(llama_cpp_paths)}")
            raise FileNotFoundError(f"llama.cpp binary not found. Checked: {', '.join(llama_cpp_paths)}")

        # Build command with proper escaping using list format
        cmd_args = [
            llama_cli_path,
            "-m", model_path,
            "-p", prompt,
            "-ngl", "999",
            "-t", "24",
            "-b", "512",
            "-ub", "512",
            "-fa", "1",
            "--cache-type-k", "q8_0",
            "--cache-type-v", "q8_0",
            "--temp", str(temperature),
            "--top-p", str(top_p),
            "--top-k", str(top_k),
            "-n", str(max_tokens),
            "-c", str(model_data['context']),
            "-ptc", "10",
            "--verbose-prompt",
            "--log-colors", "auto",
            "--mlock"
        ]

        # Add system prompt if provided (before -p argument)
        if system_prompt:
            # Find where -p is and insert before it
            try:
                p_index = cmd_args.index("-p")
                cmd_args.insert(p_index, "--system-prompt")
                cmd_args.insert(p_index + 1, system_prompt)
            except ValueError:
                # -p not found, just append
                cmd_args.extend(["--system-prompt", system_prompt])

        # Add special flags
        if special_flags.strip():
            cmd_args.extend(special_flags.split())

        # For WSL, wrap with wsl command if needed
        if not in_wsl:
            cmd_args = ["wsl"] + cmd_args

        # Execute with proper error capture
        self.logger.debug(f"Executing llama.cpp: {cmd_args[0]} with {len(cmd_args)-1} arguments")
        result = subprocess.run(
            cmd_args,
            capture_output=False,
            text=True
        )

        if result.returncode != 0:
            error_msg = f"llama.cpp execution failed with return code {result.returncode}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)
        else:
            self.logger.info("Successfully executed llama.cpp model")

    def _run_mlx_model(self, model_data: Dict[str, Any], prompt: str, system_prompt: str, params: Dict[str, Any]):  # noqa: E501
        """Run model using MLX"""
        self.logger.debug("Executing MLX model")

        temperature = params.get("temperature", model_data['temperature'])
        top_p = params.get("top_p", model_data['top_p'])
        max_tokens = params.get("max_tokens", 2048)

        cmd = f"""mlx_lm.generate \\
  --model {model_data['path']} \\
  --prompt "{prompt}" \\
  --max-tokens {max_tokens} \\
  --temp {temperature} \\
  --top-p {top_p}"""

        if system_prompt:
            cmd = cmd.replace(f'--prompt "{prompt}"', f'--system-prompt "{system_prompt}" --prompt "{prompt}"')  # noqa: E501

        # Execute
        self.logger.debug("Executing MLX command")
        result = subprocess.run(cmd, shell=True)

        if result.returncode != 0:
            self.logger.error(f"MLX execution failed with return code {result.returncode}")  # noqa: E501
            raise RuntimeError(f"Model execution failed with return code {result.returncode}")  # noqa: E501
        else:
            self.logger.info("Successfully executed MLX model")

    def view_conversation_history(self):
        """View conversation history for current project"""
        if not self.current_project or not self.current_memory:
            print(f"\n{Colors.BRIGHT_YELLOW}No project loaded. Please load a project first.{Colors.RESET}")  # noqa: E501
            input(f"\n{Colors.BRIGHT_CYAN}Press Enter to continue...{Colors.RESET}")  # noqa: E501
            return

        print(  # noqa: E501
                    f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}+==============================================================+{Colors.RESET}"  # noqa: E501
            )
        print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}|  CONVERSATION HISTORY{Colors.RESET}")  # noqa: E501
        print(  # noqa: E501
                    f"{Colors.BRIGHT_CYAN}{Colors.BOLD}+==============================================================+{Colors.RESET}\n"  # noqa: E501
            )

        conversations = self.current_memory.get_recent_conversations(20)

        if not conversations:
            print(f"{Colors.BRIGHT_YELLOW}No conversation history yet.{Colors.RESET}")  # noqa: E501
        else:
            for idx, conv in enumerate(conversations, 1):
                timestamp = conv.get("timestamp", "Unknown")
                print(f"\n{Colors.BRIGHT_WHITE}[{idx}] {timestamp}{Colors.RESET}")  # noqa: E501
                print(f"{Colors.BRIGHT_YELLOW}You: {Colors.WHITE}{conv.get('user', '')}{Colors.RESET}")  # noqa: E501
                print(f"{Colors.BRIGHT_CYAN}Assistant: {Colors.WHITE}{conv.get('assistant', '')[:200]}...{Colors.RESET}")  # noqa: E501
                print(f"{Colors.DIM}Model: {conv.get('model', 'Unknown')}{Colors.RESET}")  # noqa: E501

        if conversations and self._confirm(f"\n{Colors.BRIGHT_WHITE}Clear conversation history? [y/N]:{Colors.RESET}", default_yes=False):  # noqa: E501
            self.current_memory.clear_memory()

        input(f"\n{Colors.BRIGHT_CYAN}Press Enter to continue...{Colors.RESET}")  # noqa: E501

    def configure_web_search(self):
        """Configure web search integration"""
        print(  # noqa: E501
                    f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}+==============================================================+{Colors.RESET}"  # noqa: E501
            )
        print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}|  WEB SEARCH CONFIGURATION{Colors.RESET}")  # noqa: E501
        print(  # noqa: E501
                    f"{Colors.BRIGHT_CYAN}{Colors.BOLD}+==============================================================+{Colors.RESET}\n"  # noqa: E501
            )

        print(f"{Colors.BRIGHT_WHITE}Supported web search APIs:{Colors.RESET}\n")  # noqa: E501

        apis = list(WebSearchManager.SUPPORTED_APIS.items())
        for idx, (api_name, api_info) in enumerate(apis, 1):
            print(f"{Colors.BRIGHT_GREEN}[{idx}]{Colors.RESET} {api_info['name']}")  # noqa: E501
            print(f"    {Colors.CYAN}{api_info['description']}{Colors.RESET}\n")  # noqa: E501

        print(f"{Colors.BRIGHT_GREEN}[0]{Colors.RESET} Return to menu")

        choice = input(f"\n{Colors.BRIGHT_YELLOW}Select API to configure [0-{len(apis)}]: {Colors.RESET}").strip()  # noqa: E501

        if choice == "0":
            return

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(apis):
                api_name, api_info = apis[idx]
                api_key = input(f"\n{Colors.BRIGHT_WHITE}Enter API key for {api_info['name']}: {Colors.RESET}").strip()  # noqa: E501

                if api_key:
                    if self.websearch_manager.configure_api(api_name, api_key):
                        print(f"{Colors.BRIGHT_GREEN}{api_info['name']} configured successfully!{Colors.RESET}")  # noqa: E501
                else:
                    print(f"{Colors.BRIGHT_RED}API key cannot be empty!{Colors.RESET}")  # noqa: E501
            else:
                print(f"{Colors.BRIGHT_RED}Invalid selection!{Colors.RESET}")  # noqa: E501
        except ValueError:
            print(f"{Colors.BRIGHT_RED}Invalid input!{Colors.RESET}")  # noqa: E501

        input(f"\n{Colors.BRIGHT_CYAN}Press Enter to continue...{Colors.RESET}")  # noqa: E501

    def configure_providers(self):
        """Configure AI providers"""
        print(  # noqa: E501
                    f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}+==============================================================+{Colors.RESET}"  # noqa: E501
            )
        print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}|  PROVIDER CONFIGURATION{Colors.RESET}")  # noqa: E501
        print(  # noqa: E501
                    f"{Colors.BRIGHT_CYAN}{Colors.BOLD}+==============================================================+{Colors.RESET}\n"  # noqa: E501
            )

        print(f"{Colors.BRIGHT_WHITE}Supported providers:{Colors.RESET}\n")

        providers = list(ProviderManager.SUPPORTED_PROVIDERS.items())
        for idx, (provider_id, provider_info) in enumerate(providers, 1):
            api_required = "API key required" if provider_info['requires_api_key'] else "No API key needed"  # noqa: E501
            print(f"{Colors.BRIGHT_GREEN}[{idx}]{Colors.RESET} {provider_info['name']}")  # noqa: E501
            print(f"    {Colors.CYAN}{provider_info['description']}{Colors.RESET}")  # noqa: E501
            print(f"    {Colors.YELLOW}{api_required}{Colors.RESET}\n")

        print(f"{Colors.BRIGHT_GREEN}[0]{Colors.RESET} Return to menu")

        choice = input(f"\n{Colors.BRIGHT_YELLOW}Select provider to configure [0-{len(providers)}]: {Colors.RESET}").strip()  # noqa: E501

        if choice == "0":
            return

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(providers):
                provider_id, provider_info = providers[idx]

                if provider_info['requires_api_key']:
                    api_key = input(f"\n{Colors.BRIGHT_WHITE}Enter API key for {provider_info['name']}: {Colors.RESET}").strip()  # noqa: E501
                    if api_key:
                        if self.provider_manager.configure_provider(provider_id, api_key):  # noqa: E501
                            print(f"{Colors.BRIGHT_GREEN}{provider_info['name']} configured successfully!{Colors.RESET}")  # noqa: E501
                    else:
                        print(f"{Colors.BRIGHT_RED}API key cannot be empty!{Colors.RESET}")  # noqa: E501
                else:
                    if self.provider_manager.configure_provider(provider_id):
                        print(f"{Colors.BRIGHT_GREEN}{provider_info['name']} is ready to use!{Colors.RESET}")  # noqa: E501
            else:
                print(f"{Colors.BRIGHT_RED}Invalid selection!{Colors.RESET}")  # noqa: E501
        except ValueError:
            print(f"{Colors.BRIGHT_RED}Invalid input!{Colors.RESET}")  # noqa: E501

        input(f"\n{Colors.BRIGHT_CYAN}Press Enter to continue...{Colors.RESET}")  # noqa: E501

    def view_documentation(self):
        """View documentation (reused from original)"""
        docs_dir = self.models_dir

        docs = [
            ("HOW-TO-RUN-AI-ROUTER.md", "How to Run the AI Router", "Getting started, usage, troubleshooting"),  # noqa: E501
            ("BOT-PROJECT-QUICK-START.md", "Bot & Project Management", "Create bots and projects with custom configs"),  # noqa: E501
            ("SYSTEM-PROMPTS-QUICK-START.md", "System Prompts Quick Start", "Using and customizing system prompts"),  # noqa: E501
            ("2025-RESEARCH-SUMMARY.md", "2025 Research Summary", "Latest research findings and best practices"),  # noqa: E501
        ]

        # Filter existing docs
        existing_docs = []
        for filename, title, desc in docs:
            if (docs_dir / filename).exists():
                existing_docs.append((filename, title, desc))

        if not existing_docs:
            print(f"\n{Colors.BRIGHT_YELLOW}No documentation files found.{Colors.RESET}")  # noqa: E501
            input(f"\n{Colors.BRIGHT_CYAN}Press Enter to continue...{Colors.RESET}")  # noqa: E501
            return

        print(  # noqa: E501
                    f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}+==============================================================+{Colors.RESET}"  # noqa: E501
            )
        print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}|  DOCUMENTATION{Colors.RESET}")  # noqa: E501
        print(  # noqa: E501
                    f"{Colors.BRIGHT_CYAN}{Colors.BOLD}+==============================================================+{Colors.RESET}\n"  # noqa: E501
            )

        for idx, (filename, title, desc) in enumerate(existing_docs, 1):
            print(f"{Colors.BRIGHT_GREEN}[{idx}]{Colors.RESET} {title}")
            print(f"    {Colors.CYAN}{desc}{Colors.RESET}\n")

        print(f"{Colors.BRIGHT_GREEN}[0]{Colors.RESET} Return to menu")

        choice = input(f"\n{Colors.BRIGHT_YELLOW}Select document [0-{len(existing_docs)}]: {Colors.RESET}").strip()  # noqa: E501

        if choice != "0":
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(existing_docs):
                    filename, title, desc = existing_docs[idx]
                    doc_path = docs_dir / filename

                    with open(doc_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    print(f"\n{Colors.BRIGHT_CYAN}=== {title} ==={Colors.RESET}\n")  # noqa: E501
                    print(content[:2000])  # Show first 2000 chars
                    print(f"\n{Colors.DIM}[Content truncated for display]{Colors.RESET}")  # noqa: E501
            except Exception:
                pass

        input(f"\n{Colors.BRIGHT_CYAN}Press Enter to continue...{Colors.RESET}")  # noqa: E501

    def settings_menu(self):
        """Settings menu"""
        while True:
            print(  # noqa: E501
                    f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}+==============================================================+{Colors.RESET}"  # noqa: E501
            )
            print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}|  SETTINGS{Colors.RESET}")  # noqa: E501
            print(  # noqa: E501
                    f"{Colors.BRIGHT_CYAN}{Colors.BOLD}+==============================================================+{Colors.RESET}\n"  # noqa: E501
            )

            bypass_status = f"{Colors.BRIGHT_GREEN}ENABLED{Colors.RESET}" if self.bypass_mode else f"{Colors.BRIGHT_RED}DISABLED{Colors.RESET}"  # noqa: E501

            print(f"{Colors.BRIGHT_GREEN}[1]{Colors.RESET} Toggle Bypass Mode (Currently: {bypass_status})")  # noqa: E501
            print(f"{Colors.BRIGHT_GREEN}[2]{Colors.RESET} View Current Project Info")  # noqa: E501
            print(f"{Colors.BRIGHT_GREEN}[3]{Colors.RESET} Delete Project")
            print(f"{Colors.BRIGHT_GREEN}[0]{Colors.RESET} Return to main menu")  # noqa: E501

            choice = input(f"\n{Colors.BRIGHT_YELLOW}Enter choice: {Colors.RESET}").strip()  # noqa: E501

            if choice == "1":
                self.bypass_mode = not self.bypass_mode
                self._save_config()
                status = "enabled" if self.bypass_mode else "disabled"
                print(f"\n{Colors.BRIGHT_GREEN}Bypass mode {status}!{Colors.RESET}")  # noqa: E501
                input(f"\n{Colors.BRIGHT_CYAN}Press Enter to continue...{Colors.RESET}")  # noqa: E501
            elif choice == "2":
                if self.current_project:
                    config = self.project_manager.load_project(self.current_project)  # noqa: E501
                    if config:
                        print(f"\n{Colors.BRIGHT_WHITE}Current Project:{Colors.RESET}")  # noqa: E501
                        print(json.dumps(config, indent=2))
                else:
                    print(f"\n{Colors.BRIGHT_YELLOW}No project loaded.{Colors.RESET}")  # noqa: E501
                input(f"\n{Colors.BRIGHT_CYAN}Press Enter to continue...{Colors.RESET}")  # noqa: E501
            elif choice == "3":
                projects = self.project_manager.list_projects()
                if projects:
                    print(f"\n{Colors.BRIGHT_WHITE}Projects:{Colors.RESET}\n")
                    for idx, proj in enumerate(projects, 1):
                        print(f"{Colors.BRIGHT_GREEN}[{idx}]{Colors.RESET} {proj}")  # noqa: E501

                    del_choice = input(f"\n{Colors.BRIGHT_YELLOW}Delete project number (0 to cancel): {Colors.RESET}").strip()  # noqa: E501
                    try:
                        idx = int(del_choice) - 1
                        if 0 <= idx < len(projects):
                            proj_name = projects[idx]
                            if self._confirm(f"{Colors.BRIGHT_RED}Really delete '{proj_name}'? [y/N]:{Colors.RESET}", default_yes=False):  # noqa: E501
                                self.project_manager.delete_project(proj_name)
                                if self.current_project == proj_name:
                                    self.current_project = None
                                    self.current_memory = None
                    except Exception:
                        pass
                else:
                    print(f"\n{Colors.BRIGHT_YELLOW}No projects to delete.{Colors.RESET}")  # noqa: E501
                input(f"\n{Colors.BRIGHT_CYAN}Press Enter to continue...{Colors.RESET}")  # noqa: E501
            elif choice == "0":
                break


def main():
    """Main entry point"""
    try:
        # Initialize trace ID for this session
        set_trace_id()

        router = EnhancedAIRouter()
        router.main_menu()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.BRIGHT_YELLOW}Interrupted by user. Goodbye!{Colors.RESET}\n")  # noqa: E501
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.BRIGHT_RED}Error: {e}{Colors.RESET}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
