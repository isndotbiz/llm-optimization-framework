"""
Integration code for Model Comparison Mode
This file contains all the methods and changes needed for ai-router.py
"""

# ============================================================================
# STEP 1: Add this import at the top of ai-router.py (around line 24)
# ============================================================================
# from model_comparison import ModelComparison, ComparisonResult


# ============================================================================
# STEP 2: Add this initialization in AIRouter.__init__() (around line 413)
# ============================================================================
def init_model_comparison(self):
    """Add this code to AIRouter.__init__() after session_manager initialization"""
    # Initialize model comparison
    comparisons_dir = self.models_dir / "comparisons"
    self.model_comparison = ModelComparison(comparisons_dir)


# ============================================================================
# STEP 3: Add these helper methods to AIRouter class
# ============================================================================

def select_multiple_models(self, min_count: int = 2, max_count: int = 4):
    """
    Interactive multi-model selection

    Args:
        min_count: Minimum number of models to select
        max_count: Maximum number of models to select

    Returns:
        List of selected model_ids or None if cancelled
    """
    print(f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}╔══════════════════════════════════════════════════════════════╗{Colors.RESET}")
    print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}║  SELECT MODELS FOR COMPARISON{Colors.RESET}")
    print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}╚══════════════════════════════════════════════════════════════╝{Colors.RESET}\n")

    # Display available models with numbers
    model_list = list(self.models.items())
    for idx, (model_id, model_data) in enumerate(model_list, 1):
        print(f"{Colors.BRIGHT_YELLOW}[{idx}]{Colors.RESET} {Colors.BRIGHT_WHITE}{model_data['name']}{Colors.RESET}")
        print(f"    {Colors.CYAN}{model_id} - {model_data['use_case']}{Colors.RESET}")
        print(f"    {Colors.GREEN}{model_data['size']} | {model_data['speed']}{Colors.RESET}")
        print()

    # Get user selection
    print(f"{Colors.BRIGHT_WHITE}Select {min_count}-{max_count} models for comparison{Colors.RESET}")
    print(f"{Colors.DIM}Enter numbers separated by commas (e.g., 1,3,5) or 'back' to cancel{Colors.RESET}")

    selection = input(f"\n{Colors.BRIGHT_YELLOW}Your selection: {Colors.RESET}").strip()

    if selection.lower() == 'back':
        return None

    # Parse selection
    try:
        indices = [int(x.strip()) for x in selection.split(',')]

        # Validate count
        if len(indices) < min_count or len(indices) > max_count:
            print(f"{Colors.BRIGHT_RED}Error: Please select between {min_count} and {max_count} models.{Colors.RESET}")
            return None

        # Validate indices and collect model IDs
        selected_models = []
        for idx in indices:
            if idx < 1 or idx > len(model_list):
                print(f"{Colors.BRIGHT_RED}Error: Invalid model number: {idx}{Colors.RESET}")
                return None
            model_id, _ = model_list[idx - 1]
            if model_id in selected_models:
                print(f"{Colors.BRIGHT_RED}Error: Duplicate selection: {idx}{Colors.RESET}")
                return None
            selected_models.append(model_id)

        # Confirm selection
        print(f"\n{Colors.BRIGHT_GREEN}Selected models:{Colors.RESET}")
        for model_id in selected_models:
            print(f"  • {self.models[model_id]['name']}")

        return selected_models

    except ValueError:
        print(f"{Colors.BRIGHT_RED}Error: Invalid input. Use comma-separated numbers.{Colors.RESET}")
        return None


def comparison_mode(self):
    """Interactive model comparison (A/B testing)"""
    print(f"\n{Colors.BRIGHT_CYAN}╔══════════════════════════════════════════════════════════════╗{Colors.RESET}")
    print(f"{Colors.BRIGHT_CYAN}║  MODEL COMPARISON MODE (A/B Testing) ║{Colors.RESET}")
    print(f"{Colors.BRIGHT_CYAN}╚══════════════════════════════════════════════════════════════╝{Colors.RESET}\n")

    print(f"{Colors.BRIGHT_WHITE}Compare 2-4 models side-by-side with the same prompt{Colors.RESET}")
    print(f"{Colors.DIM}Useful for evaluating model performance, speed, and quality{Colors.RESET}\n")

    # Step 1: Get prompt
    prompt = input(f"{Colors.BRIGHT_YELLOW}Enter prompt to test (or 'back' to cancel): {Colors.RESET}").strip()

    if prompt.lower() == 'back' or not prompt:
        return

    # Step 2: Select 2-4 models
    selected_model_ids = self.select_multiple_models(min_count=2, max_count=4)

    if not selected_model_ids:
        return

    # Step 3: Run all models sequentially
    print(f"\n{Colors.BRIGHT_YELLOW}{Colors.BOLD}Running comparison...{Colors.RESET}")
    print(f"{Colors.DIM}This may take a few minutes depending on model sizes{Colors.RESET}\n")

    model_responses = []

    for idx, model_id in enumerate(selected_model_ids, 1):
        model_data = self.models[model_id]

        print(f"{Colors.BRIGHT_CYAN}[{idx}/{len(selected_model_ids)}] Testing {model_data['name']}...{Colors.RESET}")

        # Run the model
        start_time = time.time()
        response = self.run_model(model_id, model_data, prompt)

        if response:
            # Collect response data
            model_responses.append({
                'model_id': model_id,
                'model_name': model_data['name'],
                'response': response.text,
                'tokens_input': response.tokens_input or 0,
                'tokens_output': response.tokens_output or 0,
                'duration': response.duration_seconds or 0.0
            })

            print(f"{Colors.BRIGHT_GREEN}✓ Complete ({response.duration_seconds:.2f}s){Colors.RESET}\n")
        else:
            print(f"{Colors.BRIGHT_RED}✗ Failed{Colors.RESET}\n")

    if len(model_responses) < 2:
        print(f"{Colors.BRIGHT_RED}Error: Need at least 2 successful responses for comparison.{Colors.RESET}")
        input(f"\n{Colors.BRIGHT_CYAN}Press Enter to continue...{Colors.RESET}")
        return

    # Step 4: Create comparison result
    comparison = self.model_comparison.create_comparison(prompt, model_responses)

    # Step 5: Display comparison
    print(f"\n{Colors.BRIGHT_GREEN}{Colors.BOLD}Comparison Complete!{Colors.RESET}\n")

    # Display side-by-side results
    self.model_comparison.display_comparison(comparison, colors=Colors)

    # Display performance table
    self.model_comparison.display_comparison_table(comparison, colors=Colors)

    # Step 6: Post-comparison menu
    while True:
        print(f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}═══════════════════════════════════════════════════════════════{Colors.RESET}")
        print(f"{Colors.BRIGHT_WHITE}What would you like to do?{Colors.RESET}\n")
        print(f"{Colors.BRIGHT_GREEN}[1]{Colors.RESET} Export comparison (JSON)")
        print(f"{Colors.BRIGHT_GREEN}[2]{Colors.RESET} Export comparison (Markdown)")
        print(f"{Colors.BRIGHT_GREEN}[3]{Colors.RESET} Save to database")
        print(f"{Colors.BRIGHT_GREEN}[4]{Colors.RESET} Run another comparison")
        print(f"{Colors.BRIGHT_GREEN}[0]{Colors.RESET} Back to main menu")
        print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}═══════════════════════════════════════════════════════════════{Colors.RESET}")

        choice = input(f"\n{Colors.BRIGHT_YELLOW}Enter choice [0-4]: {Colors.RESET}").strip()

        if choice == "1":
            # Export as JSON
            try:
                filepath = self.model_comparison.export_comparison(comparison, format='json')
                print(f"\n{Colors.BRIGHT_GREEN}✓ Exported to: {Colors.WHITE}{filepath}{Colors.RESET}")
            except Exception as e:
                print(f"{Colors.BRIGHT_RED}Error exporting: {e}{Colors.RESET}")

        elif choice == "2":
            # Export as Markdown
            try:
                filepath = self.model_comparison.export_comparison(comparison, format='markdown')
                print(f"\n{Colors.BRIGHT_GREEN}✓ Exported to: {Colors.WHITE}{filepath}{Colors.RESET}")
            except Exception as e:
                print(f"{Colors.BRIGHT_RED}Error exporting: {e}{Colors.RESET}")

        elif choice == "3":
            # Save to database
            try:
                self.model_comparison.save_comparison_to_db(comparison, self.session_manager)
                print(f"\n{Colors.BRIGHT_GREEN}✓ Saved to database{Colors.RESET}")
            except Exception as e:
                print(f"{Colors.BRIGHT_RED}Error saving: {e}{Colors.RESET}")

        elif choice == "4":
            # Run another comparison
            return self.comparison_mode()

        elif choice == "0":
            # Return to main menu
            return

        else:
            print(f"{Colors.BRIGHT_RED}Invalid choice. Please try again.{Colors.RESET}")


# ============================================================================
# STEP 4: Update interactive_mode() menu display (around line 589)
# ============================================================================
def updated_interactive_mode_menu():
    """
    Replace the menu section in interactive_mode() with this:

    Update line ~589 to add new menu option before "Exit"
    """
    menu_text = """
    print(f"{Colors.BRIGHT_GREEN}[1]{Colors.RESET} 🎯 Auto-select model based on prompt")
    print(f"{Colors.BRIGHT_GREEN}[2]{Colors.RESET} 📋 Browse & select from all models")
    print(f"{Colors.BRIGHT_GREEN}[3]{Colors.RESET} 📎 Context Management (Load files/text)")
    print(f"{Colors.BRIGHT_GREEN}[4]{Colors.RESET} 📜 Session Management (History & Resume)")
    print(f"{Colors.BRIGHT_GREEN}[5]{Colors.RESET} 💬 View system prompt examples")
    print(f"{Colors.BRIGHT_GREEN}[6]{Colors.RESET} ⚙️ View optimal parameters guide")
    print(f"{Colors.BRIGHT_GREEN}[7]{Colors.RESET} 📚 View documentation guides")
    print(f"{Colors.BRIGHT_GREEN}[8]{Colors.RESET} 🔄 Model Comparison Mode (A/B Testing)")  # NEW

    # Bypass mode toggle option
    bypass_status = f"{Colors.BRIGHT_GREEN}ON{Colors.RESET}" if self.bypass_mode else f"{Colors.BRIGHT_RED}OFF{Colors.RESET}"
    print(f"{Colors.BRIGHT_GREEN}[9]{Colors.RESET} 🔓 Toggle Auto-Yes Mode (Currently: {bypass_status})")

    print(f"{Colors.BRIGHT_GREEN}[0]{Colors.RESET} 🚪 Exit")
    """
    return menu_text


# ============================================================================
# STEP 5: Update interactive_mode() menu handler (around line 600)
# ============================================================================
def updated_interactive_mode_handler():
    """
    Update the choice handler in interactive_mode() to include:

    Add this after the choice == "7" handler:
    """
    handler_code = """
    elif choice == "8":
        self.comparison_mode()
    elif choice == "9":
        self.toggle_bypass_mode()
    elif choice == "0":
        print(f"\\n{Colors.BRIGHT_GREEN}Goodbye!{Colors.RESET}\\n")
        sys.exit(0)
    """
    return handler_code


# ============================================================================
# Example Usage
# ============================================================================
if __name__ == "__main__":
    print("""
    INTEGRATION INSTRUCTIONS FOR AI-ROUTER.PY
    ==========================================

    1. Add import at top of file (line ~24):
       from model_comparison import ModelComparison, ComparisonResult

    2. Add initialization in __init__() (after line 413):
       # Initialize model comparison
       comparisons_dir = self.models_dir / "comparisons"
       self.model_comparison = ModelComparison(comparisons_dir)

    3. Add two new methods to AIRouter class:
       - select_multiple_models()
       - comparison_mode()
       (Copy from this file)

    4. Update interactive_mode() menu (line ~589):
       Add: print(f"{Colors.BRIGHT_GREEN}[8]{Colors.RESET} 🔄 Model Comparison Mode (A/B Testing)")

    5. Update interactive_mode() handler (line ~600):
       Add: elif choice == "8":
                self.comparison_mode()

       Also update other numbers:
       - [8] becomes [9] (Toggle Auto-Yes)
       - [9] becomes [0] (Exit)

    6. Database schema is ready in: comparison_schema.sql
       (Can be used to extend the session database if needed)

    All code is ready in this file!
    """)
