#!/usr/bin/env python3
"""
AI Router MLX Enhanced - Complete AI Project Management System
Features: Projects, Bots, Multi-Provider, Memory, Web Search, Advanced Settings
Works with MLX Server on localhost:11434
Version: 1.0
"""

import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict


# ============================================================================
# ANSI Colors
# ============================================================================
class Colors:
    """ANSI color codes for terminal output"""
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
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'


# ============================================================================
# Configuration
# ============================================================================
MLX_SERVER_URL = "http://localhost:11434"
API_ENDPOINT = f"{MLX_SERVER_URL}/v1/chat/completions"
MODELS_ENDPOINT = f"{MLX_SERVER_URL}/v1/models"
CONFIG_DIR = Path.home() / ".ai-router-mlx"
PROJECTS_DIR = CONFIG_DIR / "projects"
MEMORY_DIR = CONFIG_DIR / "memory"
BOTS_DIR = CONFIG_DIR / "bots"
CONFIG_FILE = CONFIG_DIR / "config.json"


# ============================================================================
# Bot Templates
# ============================================================================
BOT_TEMPLATES = {
    "coder": {
        "name": "Code Expert",
        "description": "Specialized in coding, debugging, and architecture",
        "system_prompt": "You are an expert programmer. Provide clear, well-structured code solutions with explanations.",
        "temperature": 0.7,
        "top_p": 0.9,
        "max_tokens": 2048,
    },
    "researcher": {
        "name": "Research Assistant",
        "description": "Specializes in research and analysis",
        "system_prompt": "You are a research assistant. Provide detailed, well-sourced analysis and insights.",
        "temperature": 0.5,
        "top_p": 0.8,
        "max_tokens": 2048,
    },
    "writer": {
        "name": "Creative Writer",
        "description": "Specializes in creative writing and content",
        "system_prompt": "You are a creative writer. Write engaging, well-structured content with style and flair.",
        "temperature": 0.9,
        "top_p": 0.95,
        "max_tokens": 2048,
    },
    "assistant": {
        "name": "General Assistant",
        "description": "General purpose AI assistant",
        "system_prompt": "You are a helpful AI assistant. Provide clear, accurate, and helpful responses.",
        "temperature": 0.7,
        "top_p": 0.9,
        "max_tokens": 2048,
    },
    "mathematician": {
        "name": "Math & Reasoning",
        "description": "Specializes in mathematics and logical reasoning",
        "system_prompt": "You are a mathematics and reasoning expert. Solve problems step-by-step with clear explanations.",
        "temperature": 0.5,
        "top_p": 0.8,
        "max_tokens": 2048,
    },
}


# ============================================================================
# Data Classes
# ============================================================================
@dataclass
class ConversationMessage:
    """Single conversation message"""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: str
    model: str


@dataclass
class ProjectConfig:
    """Project configuration"""
    name: str
    description: str
    bot_template: str
    selected_model: str
    created_at: str
    updated_at: str


# ============================================================================
# Project Manager
# ============================================================================
class ProjectManager:
    """Manages AI projects"""

    def __init__(self):
        """Initialize project manager"""
        PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    def create_project(self, name: str, description: str, bot_template: str, model: str) -> bool:
        """Create new project"""
        project_file = PROJECTS_DIR / f"{name}.json"

        if project_file.exists():
            print(f"{Colors.BRIGHT_RED}✗ Project '{name}' already exists{Colors.RESET}")
            return False

        config = {
            "name": name,
            "description": description,
            "bot_template": bot_template,
            "selected_model": model,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        try:
            with open(project_file, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"{Colors.GREEN}✓ Project '{name}' created{Colors.RESET}")
            return True
        except Exception as e:
            print(f"{Colors.BRIGHT_RED}✗ Error: {e}{Colors.RESET}")
            return False

    def list_projects(self) -> List[str]:
        """List all projects"""
        try:
            projects = [f.stem for f in PROJECTS_DIR.glob("*.json")]
            return sorted(projects)
        except Exception:
            return []

    def load_project(self, name: str) -> Optional[Dict[str, Any]]:
        """Load project configuration"""
        project_file = PROJECTS_DIR / f"{name}.json"

        if not project_file.exists():
            print(f"{Colors.BRIGHT_RED}✗ Project '{name}' not found{Colors.RESET}")
            return None

        try:
            with open(project_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"{Colors.BRIGHT_RED}✗ Error loading project: {e}{Colors.RESET}")
            return None

    def save_project(self, name: str, config: Dict[str, Any]) -> bool:
        """Save project configuration"""
        project_file = PROJECTS_DIR / f"{name}.json"

        try:
            config["updated_at"] = datetime.now().isoformat()
            with open(project_file, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            print(f"{Colors.BRIGHT_RED}✗ Error: {e}{Colors.RESET}")
            return False

    def delete_project(self, name: str) -> bool:
        """Delete project"""
        project_file = PROJECTS_DIR / f"{name}.json"
        memory_file = MEMORY_DIR / f"{name}.json"

        try:
            if project_file.exists():
                project_file.unlink()
            if memory_file.exists():
                memory_file.unlink()
            print(f"{Colors.GREEN}✓ Project '{name}' deleted{Colors.RESET}")
            return True
        except Exception as e:
            print(f"{Colors.BRIGHT_RED}✗ Error: {e}{Colors.RESET}")
            return False


# ============================================================================
# Memory Manager
# ============================================================================
class MemoryManager:
    """Manages conversation memory per project"""

    def __init__(self):
        """Initialize memory manager"""
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    def add_conversation(self, project_name: str, user_msg: str, assistant_msg: str, model: str):
        """Add conversation to memory"""
        memory_file = MEMORY_DIR / f"{project_name}.json"

        try:
            if memory_file.exists():
                with open(memory_file, 'r') as f:
                    memory = json.load(f)
            else:
                memory = {"conversations": []}

            memory["conversations"].append({
                "user": user_msg,
                "assistant": assistant_msg,
                "model": model,
                "timestamp": datetime.now().isoformat()
            })

            with open(memory_file, 'w') as f:
                json.dump(memory, f, indent=2)
        except Exception as e:
            print(f"{Colors.BRIGHT_RED}✗ Error saving memory: {e}{Colors.RESET}")

    def get_memory(self, project_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversations"""
        memory_file = MEMORY_DIR / f"{project_name}.json"

        if not memory_file.exists():
            return []

        try:
            with open(memory_file, 'r') as f:
                memory = json.load(f)
            return memory["conversations"][-limit:]
        except Exception:
            return []

    def clear_memory(self, project_name: str) -> bool:
        """Clear conversation memory"""
        memory_file = MEMORY_DIR / f"{project_name}.json"

        try:
            if memory_file.exists():
                memory_file.unlink()
            return True
        except Exception:
            return False


# ============================================================================
# Configuration Manager
# ============================================================================
class ConfigManager:
    """Manages API keys and provider configuration"""

    def __init__(self):
        """Initialize config manager"""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration"""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {"providers": {}, "default_provider": "mlx"}

    def _save_config(self):
        """Save configuration"""
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"{Colors.BRIGHT_RED}✗ Error saving config: {e}{Colors.RESET}")

    def set_provider_key(self, provider: str, api_key: str):
        """Set API key for provider"""
        if "providers" not in self.config:
            self.config["providers"] = {}
        self.config["providers"][provider] = {"api_key": api_key}
        self._save_config()
        print(f"{Colors.GREEN}✓ API key saved for {provider}{Colors.RESET}")

    def get_provider_key(self, provider: str) -> Optional[str]:
        """Get API key for provider"""
        try:
            return self.config["providers"][provider]["api_key"]
        except KeyError:
            return None


# ============================================================================
# Web Search Integration
# ============================================================================
class WebSearchTool:
    """Web search integration"""

    @staticmethod
    def search(query: str, num_results: int = 5) -> List[Dict[str, str]]:
        """Search the web (stub implementation)"""
        # Note: Full implementation would use actual search API
        # For now, returning empty to show structure
        return []

    @staticmethod
    def get_search_results_summary(results: List[Dict[str, str]]) -> str:
        """Summarize search results"""
        if not results:
            return "No search results found."

        summary = "Search Results:\n"
        for i, result in enumerate(results, 1):
            summary += f"\n{i}. {result.get('title', 'No title')}\n"
            summary += f"   {result.get('snippet', 'No snippet')}\n"
        return summary


# ============================================================================
# MLX Client
# ============================================================================
class MLXClient:
    """Client for MLX Server with enhanced features"""

    def __init__(self):
        """Initialize client"""
        self.server_url = MLX_SERVER_URL
        self.available_models = []
        self.current_project = None
        self.current_model = None
        self.conversation_history = []

        self.projects = ProjectManager()
        self.memory = MemoryManager()
        self.config = ConfigManager()
        self.search = WebSearchTool()

    def check_server(self) -> bool:
        """Check if MLX server is running"""
        try:
            response = requests.get(MODELS_ENDPOINT, timeout=2)
            return response.status_code == 200
        except Exception:
            return False

    def fetch_models(self) -> List[str]:
        """Fetch available models from MLX server"""
        try:
            response = requests.get(MODELS_ENDPOINT, timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.available_models = [model['id'] for model in data.get('data', [])]
                return self.available_models
            return []
        except Exception:
            return []

    def send_message(self, prompt: str, model: Optional[str] = None, max_tokens: int = 512) -> Optional[str]:
        """Send message to MLX server"""
        if not model:
            model = self.current_model
        if not model:
            print(f"{Colors.BRIGHT_RED}✗ No model selected{Colors.RESET}")
            return None

        try:
            self.conversation_history.append({"role": "user", "content": prompt})

            payload = {
                "model": model,
                "messages": self.conversation_history,
                "max_tokens": max_tokens,
                "stream": False
            }

            response = requests.post(API_ENDPOINT, json=payload, timeout=60)

            if response.status_code == 200:
                data = response.json()
                assistant_msg = data['choices'][0]['message']['content']
                self.conversation_history.append({"role": "assistant", "content": assistant_msg})

                if self.current_project:
                    self.memory.add_conversation(self.current_project, prompt, assistant_msg, model)

                return assistant_msg
            return None

        except Exception as e:
            print(f"{Colors.BRIGHT_RED}✗ Error: {e}{Colors.RESET}")
            return None

    # ========================================================================
    # Banner & Help
    # ========================================================================
    def print_banner(self):
        """Print application banner"""
        print(f"""
{Colors.BRIGHT_CYAN}╔════════════════════════════════════════════════════════════╗{Colors.RESET}
{Colors.BRIGHT_CYAN}║{Colors.RESET}     {Colors.BOLD}AI Router MLX Enhanced{Colors.RESET}
{Colors.BRIGHT_CYAN}║{Colors.RESET}     Complete AI Project Management System
{Colors.BRIGHT_CYAN}║{Colors.RESET}     MLX Server: {Colors.GREEN}{self.server_url}{Colors.RESET}
{Colors.BRIGHT_CYAN}╚════════════════════════════════════════════════════════════╝{Colors.RESET}
""")

    def print_help(self):
        """Print help message"""
        print(f"""
{Colors.BRIGHT_WHITE}PROJECT COMMANDS:{Colors.RESET}
  {Colors.GREEN}new{Colors.RESET}              Create new project
  {Colors.GREEN}open <name>{Colors.RESET}      Open existing project
  {Colors.GREEN}list{Colors.RESET}             List all projects
  {Colors.GREEN}delete <name>{Colors.RESET}    Delete project
  {Colors.GREEN}info{Colors.RESET}             Show project info

{Colors.BRIGHT_WHITE}MODEL COMMANDS:{Colors.RESET}
  {Colors.GREEN}models{Colors.RESET}           List available models
  {Colors.GREEN}select <model>{Colors.RESET}   Select a model
  {Colors.GREEN}settings{Colors.RESET}         Configure model settings

{Colors.BRIGHT_WHITE}CONVERSATION COMMANDS:{Colors.RESET}
  {Colors.GREEN}chat{Colors.RESET}             Start interactive chat
  {Colors.GREEN}ask <question>{Colors.RESET}   Ask a question
  {Colors.GREEN}memory{Colors.RESET}           View conversation history
  {Colors.GREEN}clear{Colors.RESET}            Clear conversation

{Colors.BRIGHT_WHITE}BOT COMMANDS:{Colors.RESET}
  {Colors.GREEN}bots{Colors.RESET}             List bot templates
  {Colors.GREEN}bot <name>{Colors.RESET}       Load bot template

{Colors.BRIGHT_WHITE}SYSTEM COMMANDS:{Colors.RESET}
  {Colors.GREEN}help{Colors.RESET}             Show this help
  {Colors.GREEN}status{Colors.RESET}           Show system status
  {Colors.GREEN}exit/quit{Colors.RESET}        Exit program
""")

    # ========================================================================
    # Project Management UI
    # ========================================================================
    def create_new_project(self):
        """Create new project interactively"""
        print(f"\n{Colors.BRIGHT_WHITE}Create New Project{Colors.RESET}\n")

        name = input(f"{Colors.CYAN}Project name:{Colors.RESET} ").strip()
        if not name:
            print(f"{Colors.BRIGHT_RED}✗ Project name required{Colors.RESET}\n")
            return

        description = input(f"{Colors.CYAN}Description:{Colors.RESET} ").strip()

        print(f"\n{Colors.BRIGHT_WHITE}Available Bot Templates:{Colors.RESET}\n")
        templates = list(BOT_TEMPLATES.items())
        for i, (key, bot) in enumerate(templates, 1):
            print(f"  {Colors.GREEN}{i}.{Colors.RESET} {Colors.CYAN}{key}{Colors.RESET}: {bot['description']}")

        template_choice = input(f"\n{Colors.CYAN}Select bot template (1-{len(templates)}):{Colors.RESET} ").strip()
        try:
            template = templates[int(template_choice) - 1][0]
        except (ValueError, IndexError):
            template = "assistant"

        if not self.available_models:
            self.fetch_models()

        print(f"\n{Colors.BRIGHT_WHITE}Available Models:{Colors.RESET}\n")
        for i, model in enumerate(self.available_models, 1):
            print(f"  {Colors.GREEN}{i}.{Colors.RESET} {Colors.CYAN}{model}{Colors.RESET}")

        model_choice = input(f"\n{Colors.CYAN}Select model (1-{len(self.available_models)}):{Colors.RESET} ").strip()
        try:
            model = self.available_models[int(model_choice) - 1]
        except (ValueError, IndexError):
            model = self.available_models[0] if self.available_models else None

        if not model:
            print(f"{Colors.BRIGHT_RED}✗ No models available{Colors.RESET}\n")
            return

        self.projects.create_project(name, description, template, model)
        print(f"{Colors.GREEN}✓ Project '{name}' created{Colors.RESET}\n")

    def open_project(self, name: str):
        """Open existing project"""
        project = self.projects.load_project(name)
        if not project:
            return

        self.current_project = name
        self.current_model = project["selected_model"]
        self.conversation_history = []

        # Load conversation history
        memory = self.memory.get_memory(name, limit=20)
        for msg in memory:
            self.conversation_history.append({
                "role": "user",
                "content": msg["user"]
            })
            self.conversation_history.append({
                "role": "assistant",
                "content": msg["assistant"]
            })

        print(f"\n{Colors.GREEN}✓ Project '{name}' opened{Colors.RESET}")
        print(f"{Colors.CYAN}Bot: {project['bot_template']}{Colors.RESET}")
        print(f"{Colors.CYAN}Model: {project['selected_model']}{Colors.RESET}")
        print(f"{Colors.CYAN}History: {len(memory)} conversations{Colors.RESET}\n")

    def show_project_info(self):
        """Show current project info"""
        if not self.current_project:
            print(f"{Colors.BRIGHT_RED}✗ No project open{Colors.RESET}\n")
            return

        project = self.projects.load_project(self.current_project)
        if not project:
            return

        print(f"\n{Colors.BRIGHT_WHITE}Project: {project['name']}{Colors.RESET}")
        print(f"{Colors.CYAN}Description: {project['description']}{Colors.RESET}")
        print(f"{Colors.CYAN}Bot: {project['bot_template']}{Colors.RESET}")
        print(f"{Colors.CYAN}Model: {project['selected_model']}{Colors.RESET}")
        print(f"{Colors.CYAN}Created: {project['created_at']}{Colors.RESET}")
        print(f"{Colors.CYAN}Updated: {project['updated_at']}{Colors.RESET}\n")

    # ========================================================================
    # Chat Interface
    # ========================================================================
    def interactive_chat(self):
        """Start interactive chat"""
        if not self.current_project:
            print(f"{Colors.BRIGHT_RED}✗ No project open{Colors.RESET}\n")
            return

        if not self.current_model:
            print(f"{Colors.BRIGHT_RED}✗ No model selected{Colors.RESET}\n")
            return

        print(f"{Colors.BRIGHT_GREEN}Starting chat with {self.current_model}...{Colors.RESET}")
        print(f"{Colors.DIM}(Type 'exit' or 'quit' to return){Colors.RESET}\n")

        while True:
            try:
                prompt = input(f"{Colors.CYAN}You:{Colors.RESET} ").strip()
                if not prompt:
                    continue
                if prompt.lower() in ['exit', 'quit']:
                    break

                print(f"{Colors.BRIGHT_BLUE}Thinking...{Colors.RESET}")
                response = self.send_message(prompt)

                if response:
                    print(f"{Colors.GREEN}Assistant:{Colors.RESET} {response}\n")

            except KeyboardInterrupt:
                print(f"\n{Colors.BRIGHT_YELLOW}Chat ended.{Colors.RESET}\n")
                break

    def show_memory(self):
        """Show conversation memory"""
        if not self.current_project:
            print(f"{Colors.BRIGHT_RED}✗ No project open{Colors.RESET}\n")
            return

        memory = self.memory.get_memory(self.current_project)
        if not memory:
            print(f"{Colors.YELLOW}No conversation history{Colors.RESET}\n")
            return

        print(f"\n{Colors.BRIGHT_WHITE}Conversation History ({len(memory)} messages){Colors.RESET}\n")
        for i, msg in enumerate(memory, 1):
            print(f"{Colors.CYAN}[{i}] {msg['timestamp']}{Colors.RESET}")
            print(f"  {Colors.GREEN}User:{Colors.RESET} {msg['user'][:100]}...")
            print(f"  {Colors.YELLOW}Model:{Colors.RESET} {msg['assistant'][:100]}...")
            print()

    def show_status(self):
        """Show system status"""
        server_status = "🟢 Online" if self.check_server() else "🔴 Offline"
        project_status = self.current_project if self.current_project else "None"
        model_status = self.current_model if self.current_model else "None"

        print(f"\n{Colors.BRIGHT_WHITE}System Status{Colors.RESET}")
        print(f"{Colors.CYAN}Server:{Colors.RESET} {server_status}")
        print(f"{Colors.CYAN}Models Available:{Colors.RESET} {len(self.available_models)}")
        print(f"{Colors.CYAN}Current Project:{Colors.RESET} {project_status}")
        print(f"{Colors.CYAN}Current Model:{Colors.RESET} {model_status}")
        print(f"{Colors.CYAN}Config Dir:{Colors.RESET} {CONFIG_DIR}\n")

    # ========================================================================
    # Main Loop
    # ========================================================================
    def interactive_mode(self):
        """Main interactive mode"""
        self.print_banner()

        if not self.check_server():
            print(f"{Colors.BRIGHT_RED}✗ MLX Server not running!{Colors.RESET}\n")
            print(f"{Colors.YELLOW}Start it with:{Colors.RESET}")
            print(f"  {Colors.GREEN}source ~/venv-mlx/bin/activate && python3 mlx-server.py{Colors.RESET}\n")
            return

        print(f"{Colors.GREEN}✓ Connected to MLX Server{Colors.RESET}\n")

        print(f"{Colors.YELLOW}Loading models...{Colors.RESET}")
        self.fetch_models()
        print(f"{Colors.GREEN}✓ Found {len(self.available_models)} models{Colors.RESET}\n")

        self.print_help()

        while True:
            try:
                project_indicator = f"[{self.current_project}] " if self.current_project else ""
                user_input = input(f"{Colors.BRIGHT_CYAN}{project_indicator}mlx> {Colors.RESET}").strip()

                if not user_input:
                    continue

                parts = user_input.split(maxsplit=1)
                command = parts[0].lower()
                args = parts[1] if len(parts) > 1 else ""

                # Project Commands
                if command == 'new':
                    self.create_new_project()
                elif command == 'open':
                    if args:
                        projects = self.projects.list_projects()
                        try:
                            project_num = int(args)
                            if 1 <= project_num <= len(projects):
                                self.open_project(projects[project_num - 1])
                            else:
                                print(f"{Colors.BRIGHT_RED}✗ Invalid project number{Colors.RESET}\n")
                        except ValueError:
                            self.open_project(args)
                    else:
                        projects = self.projects.list_projects()
                        if projects:
                            print(f"\n{Colors.BRIGHT_WHITE}Available Projects:{Colors.RESET}\n")
                            for i, p in enumerate(projects, 1):
                                marker = f"{Colors.GREEN}►{Colors.RESET}" if p == self.current_project else " "
                                print(f"  {marker} {Colors.GREEN}{i}.{Colors.RESET} {Colors.CYAN}{p}{Colors.RESET}")
                            print(f"\n{Colors.YELLOW}Usage: open <number> or open <project_name>{Colors.RESET}\n")
                        else:
                            print(f"{Colors.YELLOW}No projects found{Colors.RESET}\n")

                elif command == 'list':
                    projects = self.projects.list_projects()
                    if projects:
                        print(f"\n{Colors.BRIGHT_WHITE}Projects ({len(projects)}):{Colors.RESET}")
                        for i, p in enumerate(projects, 1):
                            marker = f"{Colors.GREEN}►{Colors.RESET}" if p == self.current_project else " "
                            print(f"  {marker} {Colors.CYAN}{p}{Colors.RESET}")
                        print()
                    else:
                        print(f"{Colors.YELLOW}No projects found{Colors.RESET}\n")

                elif command == 'delete':
                    if args:
                        projects = self.projects.list_projects()
                        project_name = args
                        try:
                            project_num = int(args)
                            if 1 <= project_num <= len(projects):
                                project_name = projects[project_num - 1]
                            else:
                                print(f"{Colors.BRIGHT_RED}✗ Invalid project number{Colors.RESET}\n")
                                project_name = None
                        except ValueError:
                            pass

                        if project_name:
                            confirm = input(f"Delete project '{project_name}'? (y/n): ").strip().lower()
                            if confirm == 'y':
                                self.projects.delete_project(project_name)
                            print()
                    else:
                        projects = self.projects.list_projects()
                        if projects:
                            print(f"\n{Colors.BRIGHT_WHITE}Available Projects:{Colors.RESET}\n")
                            for i, p in enumerate(projects, 1):
                                print(f"  {Colors.GREEN}{i}.{Colors.RESET} {Colors.CYAN}{p}{Colors.RESET}")
                            print(f"\n{Colors.YELLOW}Usage: delete <number> or delete <project_name>{Colors.RESET}\n")
                        else:
                            print(f"{Colors.YELLOW}No projects found{Colors.RESET}\n")

                elif command == 'info':
                    self.show_project_info()

                # Model Commands
                elif command == 'models':
                    print(f"\n{Colors.BRIGHT_WHITE}Available Models ({len(self.available_models)}):{Colors.RESET}\n")
                    for i, model in enumerate(self.available_models, 1):
                        marker = f"{Colors.GREEN}✓{Colors.RESET}" if model == self.current_model else " "
                        print(f"  {marker} {Colors.CYAN}{i}.{Colors.RESET} {model}")
                    print()

                elif command == 'select':
                    if args:
                        try:
                            model_num = int(args)
                            if 1 <= model_num <= len(self.available_models):
                                self.current_model = self.available_models[model_num - 1]
                                print(f"{Colors.GREEN}✓ Model selected: {self.current_model}{Colors.RESET}\n")
                            else:
                                print(f"{Colors.BRIGHT_RED}✗ Invalid model number{Colors.RESET}\n")
                        except ValueError:
                            if args in self.available_models:
                                self.current_model = args
                                print(f"{Colors.GREEN}✓ Model selected: {args}{Colors.RESET}\n")
                            else:
                                print(f"{Colors.BRIGHT_RED}✗ Model not found{Colors.RESET}\n")
                    else:
                        print(f"\n{Colors.BRIGHT_WHITE}Available Models:{Colors.RESET}\n")
                        for i, model in enumerate(self.available_models, 1):
                            marker = f"{Colors.GREEN}✓{Colors.RESET}" if model == self.current_model else " "
                            print(f"  {marker} {Colors.GREEN}{i}.{Colors.RESET} {Colors.CYAN}{model}{Colors.RESET}")
                        print(f"\n{Colors.YELLOW}Usage: select <number> or select <model_name>{Colors.RESET}\n")

                elif command == 'settings':
                    if self.current_model:
                        print(f"\n{Colors.BRIGHT_WHITE}Model Settings for {self.current_model}{Colors.RESET}")
                        print(f"{Colors.CYAN}Temperature: 0.7{Colors.RESET}")
                        print(f"{Colors.CYAN}Top P: 0.9{Colors.RESET}")
                        print(f"{Colors.CYAN}Max Tokens: 2048{Colors.RESET}\n")
                    else:
                        print(f"{Colors.BRIGHT_RED}✗ No model selected{Colors.RESET}\n")

                # Conversation Commands
                elif command == 'chat':
                    self.interactive_chat()

                elif command == 'ask':
                    if args:
                        if not self.current_model:
                            print(f"{Colors.BRIGHT_RED}✗ No model selected{Colors.RESET}\n")
                        else:
                            print(f"{Colors.BRIGHT_BLUE}Thinking...{Colors.RESET}")
                            response = self.send_message(args)
                            if response:
                                print(f"{Colors.GREEN}✓{Colors.RESET} {response}\n")
                    else:
                        print(f"{Colors.BRIGHT_RED}Usage: ask <question>{Colors.RESET}\n")

                elif command == 'memory':
                    self.show_memory()

                elif command == 'clear':
                    if self.current_project:
                        confirm = input("Clear conversation history? (y/n): ").strip().lower()
                        if confirm == 'y':
                            self.memory.clear_memory(self.current_project)
                            self.conversation_history = []
                            print(f"{Colors.GREEN}✓ History cleared{Colors.RESET}\n")
                    else:
                        print(f"{Colors.BRIGHT_RED}✗ No project open{Colors.RESET}\n")

                # Bot Commands
                elif command == 'bots':
                    print(f"\n{Colors.BRIGHT_WHITE}Bot Templates:{Colors.RESET}\n")
                    bots = list(BOT_TEMPLATES.items())
                    for i, (key, bot) in enumerate(bots, 1):
                        print(f"  {Colors.GREEN}{i}.{Colors.RESET} {Colors.CYAN}{key}{Colors.RESET}")
                        print(f"     {bot['description']}\n")
                    print(f"{Colors.YELLOW}Usage: bot <number> or bot <template_name>{Colors.RESET}\n")

                elif command == 'bot':
                    if args:
                        bots = list(BOT_TEMPLATES.items())
                        bot_name = args
                        try:
                            bot_num = int(args)
                            if 1 <= bot_num <= len(bots):
                                bot_name = bots[bot_num - 1][0]
                            else:
                                print(f"{Colors.BRIGHT_RED}✗ Invalid bot number{Colors.RESET}\n")
                                bot_name = None
                        except ValueError:
                            pass

                        if bot_name and bot_name in BOT_TEMPLATES:
                            bot = BOT_TEMPLATES[bot_name]
                            print(f"\n{Colors.BRIGHT_WHITE}Bot: {bot['name']}{Colors.RESET}")
                            print(f"{Colors.CYAN}Description: {bot['description']}{Colors.RESET}")
                            print(f"{Colors.CYAN}Temperature: {bot['temperature']}{Colors.RESET}\n")
                        elif bot_name:
                            print(f"{Colors.BRIGHT_RED}✗ Bot not found{Colors.RESET}\n")
                    else:
                        bots = list(BOT_TEMPLATES.items())
                        print(f"\n{Colors.BRIGHT_WHITE}Bot Templates:{Colors.RESET}\n")
                        for i, (key, bot) in enumerate(bots, 1):
                            print(f"  {Colors.GREEN}{i}.{Colors.RESET} {Colors.CYAN}{key}{Colors.RESET} - {bot['description']}")
                        print(f"\n{Colors.YELLOW}Usage: bot <number> or bot <template_name>{Colors.RESET}\n")

                # System Commands
                elif command == 'help':
                    self.print_help()

                elif command == 'status':
                    self.show_status()

                elif command in ['exit', 'quit']:
                    print(f"\n{Colors.BRIGHT_YELLOW}Goodbye!{Colors.RESET}\n")
                    break

                else:
                    print(f"{Colors.BRIGHT_RED}Unknown command: {command}{Colors.RESET}")
                    print(f"Type '{Colors.GREEN}help{Colors.RESET}' for available commands\n")

            except KeyboardInterrupt:
                print(f"\n\n{Colors.BRIGHT_YELLOW}Interrupted. Goodbye!{Colors.RESET}\n")
                break
            except Exception as e:
                print(f"{Colors.BRIGHT_RED}Error: {e}{Colors.RESET}\n")


# ============================================================================
# Main Entry Point
# ============================================================================
def main():
    """Main entry point"""
    client = MLXClient()

    if len(sys.argv) > 1:
        if sys.argv[1] == "--help":
            client.print_banner()
            client.print_help()
        elif sys.argv[1] == "--status":
            client.print_banner()
            client.show_status()
        elif sys.argv[1] == "--list":
            client.print_banner()
            projects = client.projects.list_projects()
            if projects:
                print(f"{Colors.BRIGHT_WHITE}Projects:{Colors.RESET}")
                for p in projects:
                    print(f"  {Colors.CYAN}• {p}{Colors.RESET}")
            else:
                print(f"{Colors.YELLOW}No projects found{Colors.RESET}")
            print()
        else:
            print(f"{Colors.BRIGHT_RED}Unknown argument{Colors.RESET}\n")
            print(f"Usage: {Colors.GREEN}python3 ai-router-mlx-enhanced.py [--help|--status|--list]{Colors.RESET}\n")
    else:
        client.interactive_mode()


if __name__ == "__main__":
    main()
