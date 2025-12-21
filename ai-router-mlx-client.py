#!/usr/bin/env python3
"""
AI Router MLX Client - Command-line interface to MLX Server
Connects to running MLX server on localhost:11434
"""

import sys
import json
import requests
from pathlib import Path
from typing import Optional, List, Dict

# Configuration
MLX_SERVER_URL = "http://localhost:11434"
API_ENDPOINT = f"{MLX_SERVER_URL}/v1/chat/completions"
MODELS_ENDPOINT = f"{MLX_SERVER_URL}/v1/models"


class Colors:
    """ANSI color codes"""
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


class MLXClient:
    """Client for communicating with MLX Server"""

    def __init__(self):
        """Initialize MLX client"""
        self.server_url = MLX_SERVER_URL
        self.available_models = []
        self.current_model = None
        self.conversation_history = []

    def check_server(self) -> bool:
        """Check if MLX server is running"""
        try:
            response = requests.get(MODELS_ENDPOINT, timeout=2)
            return response.status_code == 200
        except requests.ConnectionError:
            return False
        except Exception as e:
            print(f"{Colors.BRIGHT_RED}Error checking server: {e}{Colors.RESET}")
            return False

    def fetch_models(self) -> List[str]:
        """Fetch available models from MLX server"""
        try:
            response = requests.get(MODELS_ENDPOINT, timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.available_models = [model['id'] for model in data.get('data', [])]
                return self.available_models
            else:
                print(f"{Colors.BRIGHT_RED}Error fetching models: {response.status_code}{Colors.RESET}")
                return []
        except requests.ConnectionError:
            print(f"{Colors.BRIGHT_RED}Cannot connect to MLX Server at {self.server_url}{Colors.RESET}")
            print(f"{Colors.YELLOW}Make sure MLX server is running:{Colors.RESET}")
            print(f"  {Colors.GREEN}source ~/venv-mlx/bin/activate && python3 mlx-server.py{Colors.RESET}\n")
            return []
        except Exception as e:
            print(f"{Colors.BRIGHT_RED}Error: {e}{Colors.RESET}")
            return []

    def send_message(self, prompt: str, model: Optional[str] = None, max_tokens: int = 512) -> Optional[str]:
        """Send message to MLX server and get response"""
        if not model:
            model = self.current_model
        if not model:
            print(f"{Colors.BRIGHT_RED}No model selected. Use 'select' command first.{Colors.RESET}")
            return None

        try:
            # Add to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": prompt
            })

            payload = {
                "model": model,
                "messages": self.conversation_history,
                "max_tokens": max_tokens,
                "stream": False
            }

            response = requests.post(API_ENDPOINT, json=payload, timeout=60)

            if response.status_code == 200:
                data = response.json()
                assistant_message = data['choices'][0]['message']['content']

                # Add to conversation history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": assistant_message
                })

                return assistant_message
            else:
                print(f"{Colors.BRIGHT_RED}Error: {response.status_code}{Colors.RESET}")
                if response.text:
                    print(f"{Colors.YELLOW}{response.text}{Colors.RESET}")
                return None

        except requests.Timeout:
            print(f"{Colors.BRIGHT_RED}Request timeout. Model may be slow or overloaded.{Colors.RESET}")
            return None
        except Exception as e:
            print(f"{Colors.BRIGHT_RED}Error: {e}{Colors.RESET}")
            return None

    def print_banner(self):
        """Print application banner"""
        print(f"""
{Colors.BRIGHT_CYAN}╔════════════════════════════════════════════════════════════╗{Colors.RESET}
{Colors.BRIGHT_CYAN}║{Colors.RESET}     {Colors.BOLD}AI Router MLX Client{Colors.RESET} - MLX Server Command-Line
{Colors.BRIGHT_CYAN}║{Colors.RESET}     Connected to: {Colors.GREEN}{self.server_url}{Colors.RESET}
{Colors.BRIGHT_CYAN}╚════════════════════════════════════════════════════════════╝{Colors.RESET}
""")

    def print_help(self):
        """Print help message"""
        print(f"""
{Colors.BRIGHT_WHITE}Commands:{Colors.RESET}
  {Colors.GREEN}list{Colors.RESET}              List all available models
  {Colors.GREEN}select <model>{Colors.RESET}     Select a model (e.g., 'select qwen3:7b')
  {Colors.GREEN}info{Colors.RESET}              Show selected model info
  {Colors.GREEN}chat{Colors.RESET}              Start interactive chat
  {Colors.GREEN}ask <question>{Colors.RESET}    Ask a one-off question
  {Colors.GREEN}clear{Colors.RESET}             Clear conversation history
  {Colors.GREEN}help{Colors.RESET}              Show this help message
  {Colors.GREEN}exit/quit{Colors.RESET}         Exit the program

{Colors.BRIGHT_WHITE}Examples:{Colors.RESET}
  {Colors.CYAN}> select qwen3:7b{Colors.RESET}
  {Colors.CYAN}> ask What is 2+2?{Colors.RESET}
  {Colors.CYAN}> chat{Colors.RESET}
  {Colors.CYAN}> list{Colors.RESET}
""")

    def list_models(self):
        """List all available models"""
        if not self.available_models:
            print(f"{Colors.YELLOW}Fetching models...{Colors.RESET}")
            models = self.fetch_models()
            if not models:
                print(f"{Colors.BRIGHT_RED}No models available{Colors.RESET}")
                return

        print(f"\n{Colors.BRIGHT_WHITE}Available Models ({len(self.available_models)} total):{Colors.RESET}\n")
        for i, model in enumerate(self.available_models, 1):
            marker = f"{Colors.GREEN}✓{Colors.RESET}" if model == self.current_model else " "
            print(f"  {marker} {Colors.CYAN}{i}.{Colors.RESET} {Colors.WHITE}{model}{Colors.RESET}")
        print()

    def select_model(self, model_name: str) -> bool:
        """Select a model"""
        if not self.available_models:
            self.fetch_models()

        if model_name in self.available_models:
            self.current_model = model_name
            self.conversation_history = []  # Reset history when switching models
            print(f"{Colors.GREEN}✓{Colors.RESET} Model selected: {Colors.BRIGHT_WHITE}{model_name}{Colors.RESET}\n")
            return True
        else:
            print(f"{Colors.BRIGHT_RED}✗ Model not found: {model_name}{Colors.RESET}")
            print(f"{Colors.YELLOW}Available models: {', '.join(self.available_models)}{Colors.RESET}\n")
            return False

    def interactive_chat(self):
        """Start interactive chat session"""
        if not self.current_model:
            print(f"{Colors.BRIGHT_RED}No model selected. Use 'select' command first.{Colors.RESET}\n")
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
                else:
                    print(f"{Colors.BRIGHT_RED}No response received{Colors.RESET}\n")

            except KeyboardInterrupt:
                print(f"\n{Colors.BRIGHT_YELLOW}Chat ended.{Colors.RESET}\n")
                break

    def interactive_mode(self):
        """Main interactive mode"""
        self.print_banner()

        # Check server
        if not self.check_server():
            print(f"{Colors.BRIGHT_RED}✗ MLX Server is not running!{Colors.RESET}\n")
            print(f"{Colors.YELLOW}Start it with:{Colors.RESET}")
            print(f"  {Colors.GREEN}source ~/venv-mlx/bin/activate && python3 mlx-server.py{Colors.RESET}\n")
            return

        print(f"{Colors.GREEN}✓ Connected to MLX Server{Colors.RESET}\n")

        # Fetch models
        print(f"{Colors.YELLOW}Loading available models...{Colors.RESET}")
        self.fetch_models()
        if self.available_models:
            print(f"{Colors.GREEN}✓ Found {len(self.available_models)} models{Colors.RESET}\n")
        else:
            print(f"{Colors.BRIGHT_RED}✗ No models found{Colors.RESET}\n")
            return

        self.print_help()

        # Main loop
        while True:
            try:
                user_input = input(f"{Colors.BRIGHT_CYAN}mlx> {Colors.RESET}").strip()

                if not user_input:
                    continue

                # Parse command
                parts = user_input.split(maxsplit=1)
                command = parts[0].lower()
                args = parts[1] if len(parts) > 1 else ""

                if command in ['exit', 'quit']:
                    print(f"\n{Colors.BRIGHT_YELLOW}Goodbye!{Colors.RESET}\n")
                    break

                elif command == 'help':
                    self.print_help()

                elif command == 'list':
                    self.list_models()

                elif command == 'select':
                    if args:
                        self.select_model(args)
                    else:
                        print(f"{Colors.BRIGHT_RED}Usage: select <model_name>{Colors.RESET}\n")

                elif command == 'info':
                    if self.current_model:
                        print(f"\n{Colors.BRIGHT_WHITE}Current Model:{Colors.RESET} {Colors.GREEN}{self.current_model}{Colors.RESET}")
                        print(f"{Colors.BRIGHT_WHITE}Conversation History:{Colors.RESET} {len(self.conversation_history)} messages\n")
                    else:
                        print(f"{Colors.BRIGHT_RED}No model selected{Colors.RESET}\n")

                elif command == 'chat':
                    self.interactive_chat()

                elif command == 'ask':
                    if args:
                        if not self.current_model:
                            print(f"{Colors.BRIGHT_RED}No model selected. Use 'select' command first.{Colors.RESET}\n")
                        else:
                            print(f"{Colors.BRIGHT_BLUE}Thinking...{Colors.RESET}")
                            response = self.send_message(args)
                            if response:
                                print(f"{Colors.GREEN}✓{Colors.RESET} {response}\n")
                    else:
                        print(f"{Colors.BRIGHT_RED}Usage: ask <question>{Colors.RESET}\n")

                elif command == 'clear':
                    self.conversation_history = []
                    print(f"{Colors.GREEN}✓ Conversation history cleared{Colors.RESET}\n")

                else:
                    print(f"{Colors.BRIGHT_RED}Unknown command: {command}{Colors.RESET}")
                    print(f"{Colors.YELLOW}Type 'help' for available commands{Colors.RESET}\n")

            except KeyboardInterrupt:
                print(f"\n\n{Colors.BRIGHT_YELLOW}Interrupted. Goodbye!{Colors.RESET}\n")
                break
            except Exception as e:
                print(f"{Colors.BRIGHT_RED}Error: {e}{Colors.RESET}\n")


def main():
    """Main entry point"""
    client = MLXClient()

    if len(sys.argv) > 1:
        if sys.argv[1] == "--help":
            client.print_banner()
            client.print_help()
        elif sys.argv[1] == "--list":
            client.print_banner()
            client.list_models()
        elif sys.argv[1] == "--ask" and len(sys.argv) > 2:
            client.print_banner()
            if client.check_server():
                client.fetch_models()
                if client.available_models:
                    client.select_model(client.available_models[0])
                    prompt = " ".join(sys.argv[2:])
                    print(f"{Colors.BRIGHT_BLUE}Thinking...{Colors.RESET}")
                    response = client.send_message(prompt)
                    if response:
                        print(f"\n{Colors.GREEN}Response:{Colors.RESET}\n{response}\n")
        else:
            print(f"{Colors.BRIGHT_RED}Unknown argument{Colors.RESET}")
            print(f"Use: {Colors.GREEN}python3 ai-router-mlx-client.py --help{Colors.RESET}\n")
    else:
        client.interactive_mode()


if __name__ == "__main__":
    main()
