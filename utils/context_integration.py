"""
Context Management Integration Methods for AIRouter
Add these methods to the AIRouter class in ai-router.py
"""

def context_mode(self):
    """Interactive context management"""
    while True:
        print(f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}╔══════════════════════════════════════════════════════════════╗{Colors.RESET}")
        print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}║  CONTEXT MANAGEMENT{Colors.RESET}")
        print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}╚══════════════════════════════════════════════════════════════╝{Colors.RESET}\n")

        # Show current context summary
        print(f"{Colors.BRIGHT_WHITE}Current Context:{Colors.RESET}\n")
        if self.context_manager.context_items:
            for idx, item in enumerate(self.context_manager.context_items, 1):
                type_icon = "📄" if item['type'] == 'file' else "📝"
                print(f"{type_icon} {Colors.BRIGHT_YELLOW}[{idx}]{Colors.RESET} {Colors.WHITE}{item['label']}{Colors.RESET}")
                print(f"    {Colors.CYAN}Type: {item['type']} | Tokens: {item['tokens']:,}{Colors.RESET}")
                if 'path' in item:
                    print(f"    {Colors.DIM}Path: {item['path']}{Colors.RESET}")
                print()

            total_tokens = self.context_manager.get_total_tokens()
            max_tokens = self.context_manager.max_tokens
            utilization = (total_tokens / max_tokens) * 100

            print(f"{Colors.BRIGHT_WHITE}Total: {Colors.BRIGHT_CYAN}{total_tokens:,}{Colors.RESET} / {Colors.BRIGHT_MAGENTA}{max_tokens:,}{Colors.RESET} tokens ({utilization:.1f}% used)\n")
        else:
            print(f"{Colors.DIM}No context loaded{Colors.RESET}\n")

        # Menu options
        print(f"{Colors.BRIGHT_GREEN}[1]{Colors.RESET} Add file(s) to context")
        print(f"{Colors.BRIGHT_GREEN}[2]{Colors.RESET} Add text to context")
        print(f"{Colors.BRIGHT_GREEN}[3]{Colors.RESET} Remove context item")
        print(f"{Colors.BRIGHT_GREEN}[4]{Colors.RESET} Clear all context")
        print(f"{Colors.BRIGHT_GREEN}[5]{Colors.RESET} Set token limit")
        print(f"{Colors.BRIGHT_GREEN}[6]{Colors.RESET} Execute with context")
        print(f"{Colors.BRIGHT_GREEN}[0]{Colors.RESET} Return to main menu\n")

        choice = input(f"{Colors.BRIGHT_YELLOW}Enter choice [0-6]: {Colors.RESET}").strip()

        if choice == "0":
            break
        elif choice == "1":
            self.add_files_to_context()
        elif choice == "2":
            self.add_text_to_context()
        elif choice == "3":
            self.remove_context_item()
        elif choice == "4":
            if self._confirm(f"\n{Colors.BRIGHT_YELLOW}Clear all context? [y/N]:{Colors.RESET}", default_yes=False):
                self.context_manager.clear_context()
                print(f"{Colors.BRIGHT_GREEN}Context cleared.{Colors.RESET}")
        elif choice == "5":
            self.set_token_limit()
        elif choice == "6":
            self.execute_with_context()
        else:
            print(f"{Colors.BRIGHT_RED}Invalid choice.{Colors.RESET}")

def add_files_to_context(self):
    """Add files to context interactively"""
    print(f"\n{Colors.BRIGHT_CYAN}Add Files to Context{Colors.RESET}\n")
    print(f"{Colors.WHITE}Enter file path(s) - one per line.{Colors.RESET}")
    print(f"{Colors.WHITE}Use absolute or relative paths.{Colors.RESET}")
    print(f"{Colors.DIM}(Press Enter on empty line to finish){Colors.RESET}\n")

    added_count = 0
    while True:
        file_path_str = input(f"{Colors.YELLOW}File path: {Colors.RESET}").strip()

        if not file_path_str:
            break

        try:
            file_path = Path(file_path_str)

            # Make absolute if relative
            if not file_path.is_absolute():
                file_path = (self.models_dir / file_path).resolve()

            # Optional label
            use_default = self._confirm(f"Use default label (filename)? [Y/n]: ", default_yes=True)
            label = None
            if not use_default:
                label = input(f"{Colors.YELLOW}Enter custom label: {Colors.RESET}").strip()
                if not label:
                    label = None

            # Add to context
            item = self.context_manager.add_file(file_path, label)
            print(f"{Colors.BRIGHT_GREEN}✓ Added: {item['label']} ({item['tokens']:,} tokens){Colors.RESET}\n")
            added_count += 1

        except Exception as e:
            print(f"{Colors.BRIGHT_RED}Error: {e}{Colors.RESET}\n")

    if added_count > 0:
        print(f"\n{Colors.BRIGHT_GREEN}Added {added_count} file(s) to context.{Colors.RESET}")

def add_text_to_context(self):
    """Add text to context interactively"""
    print(f"\n{Colors.BRIGHT_CYAN}Add Text to Context{Colors.RESET}\n")

    label = input(f"{Colors.YELLOW}Enter label for this text: {Colors.RESET}").strip()
    if not label:
        print(f"{Colors.BRIGHT_RED}Label is required.{Colors.RESET}")
        return

    print(f"\n{Colors.WHITE}Enter text content (press Ctrl+D or Ctrl+Z when done):{Colors.RESET}\n")

    try:
        # Read multi-line input
        lines = []
        while True:
            try:
                line = input()
                lines.append(line)
            except EOFError:
                break

        text = "\n".join(lines)

        if text.strip():
            item = self.context_manager.add_text(text, label)
            print(f"\n{Colors.BRIGHT_GREEN}✓ Added text: {item['label']} ({item['tokens']:,} tokens){Colors.RESET}")
        else:
            print(f"\n{Colors.BRIGHT_YELLOW}No text entered.{Colors.RESET}")

    except Exception as e:
        print(f"\n{Colors.BRIGHT_RED}Error: {e}{Colors.RESET}")

def remove_context_item(self):
    """Remove a context item by index"""
    if not self.context_manager.context_items:
        print(f"\n{Colors.BRIGHT_YELLOW}No context items to remove.{Colors.RESET}")
        return

    print(f"\n{Colors.BRIGHT_CYAN}Remove Context Item{Colors.RESET}\n")

    for idx, item in enumerate(self.context_manager.context_items, 1):
        print(f"{Colors.BRIGHT_YELLOW}[{idx}]{Colors.RESET} {item['label']}")

    try:
        choice = input(f"\n{Colors.YELLOW}Enter item number to remove [1-{len(self.context_manager.context_items)}]: {Colors.RESET}").strip()
        idx = int(choice) - 1

        if 0 <= idx < len(self.context_manager.context_items):
            item = self.context_manager.context_items[idx]
            if self.context_manager.remove_context_item(idx):
                print(f"{Colors.BRIGHT_GREEN}✓ Removed: {item['label']}{Colors.RESET}")
            else:
                print(f"{Colors.BRIGHT_RED}Failed to remove item.{Colors.RESET}")
        else:
            print(f"{Colors.BRIGHT_RED}Invalid item number.{Colors.RESET}")

    except ValueError:
        print(f"{Colors.BRIGHT_RED}Invalid input.{Colors.RESET}")

def set_token_limit(self):
    """Set maximum token limit for context"""
    print(f"\n{Colors.BRIGHT_CYAN}Set Token Limit{Colors.RESET}\n")
    print(f"{Colors.WHITE}Current limit: {Colors.BRIGHT_CYAN}{self.context_manager.max_tokens:,}{Colors.RESET} tokens\n")

    try:
        new_limit = input(f"{Colors.YELLOW}Enter new token limit: {Colors.RESET}").strip()
        new_limit = int(new_limit)

        if new_limit > 0:
            self.context_manager.set_max_tokens(new_limit)
            print(f"{Colors.BRIGHT_GREEN}✓ Token limit set to {new_limit:,}{Colors.RESET}")
        else:
            print(f"{Colors.BRIGHT_RED}Token limit must be positive.{Colors.RESET}")

    except ValueError:
        print(f"{Colors.BRIGHT_RED}Invalid number.{Colors.RESET}")

def execute_with_context(self):
    """Execute model with loaded context"""
    if not self.context_manager.context_items:
        print(f"\n{Colors.BRIGHT_YELLOW}No context loaded. Add files or text first.{Colors.RESET}")
        return

    print(f"\n{Colors.BRIGHT_CYAN}Execute with Context{Colors.RESET}\n")

    # Get user prompt
    print(f"{Colors.WHITE}Enter your prompt/question:{Colors.RESET}")
    user_prompt = input(f"{Colors.YELLOW}> {Colors.RESET}").strip()

    if not user_prompt:
        print(f"{Colors.BRIGHT_RED}Prompt is required.{Colors.RESET}")
        return

    # Build prompt with context
    try:
        full_prompt = self.context_manager.build_context_prompt(user_prompt, truncate=True)

        # Show prompt preview
        print(f"\n{Colors.BRIGHT_WHITE}Generated prompt preview (first 500 chars):{Colors.RESET}")
        print(f"{Colors.DIM}{full_prompt[:500]}...{Colors.RESET}\n")

        # Detect use case
        use_case = ModelDatabase.detect_use_case(user_prompt)
        print(f"{Colors.BRIGHT_MAGENTA}Detected use case: {Colors.BRIGHT_WHITE}{use_case.upper()}{Colors.RESET}")

        # Recommend model
        model_id, model_data = ModelDatabase.recommend_model(use_case, self.models)
        print(f"{Colors.BRIGHT_GREEN}Recommended model: {Colors.BRIGHT_WHITE}{model_data['name']}{Colors.RESET}\n")

        # Show model info
        self.print_model_info(model_id, model_data)

        # Ask if user wants to run
        if self._confirm(f"\n{Colors.BRIGHT_YELLOW}Run this model with context? [Y/n]:{Colors.RESET}", default_yes=True):
            self.run_model(model_id, model_data, full_prompt)

    except Exception as e:
        print(f"{Colors.BRIGHT_RED}Error building prompt: {e}{Colors.RESET}")
