    def template_mode(self):
        """Interactive template selection and usage"""
        print(f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}╔══════════════════════════════════════════════════════════════╗{Colors.RESET}")
        print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}║  PROMPT TEMPLATES LIBRARY{Colors.RESET}")
        print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}╚══════════════════════════════════════════════════════════════╝{Colors.RESET}\n")

        # Get all templates
        all_templates = self.template_manager.list_templates()
        if not all_templates:
            print(f"{Colors.BRIGHT_RED}No templates found in the library!{Colors.RESET}")
            print(f"{Colors.YELLOW}Templates should be placed in: {self.template_manager.templates_dir}{Colors.RESET}\n")
            input(f"{Colors.BRIGHT_CYAN}Press Enter to return...{Colors.RESET}")
            return

        # Browse by category
        categories = self.template_manager.get_categories()

        print(f"{Colors.BRIGHT_WHITE}Available Categories:{Colors.RESET}\n")
        for idx, category in enumerate(categories, 1):
            # Count templates in category
            cat_templates = [t for t in all_templates if t.get('category') == category]
            print(f"{Colors.BRIGHT_GREEN}[{idx}]{Colors.RESET} {Colors.BRIGHT_WHITE}{category.capitalize()}{Colors.RESET} ({len(cat_templates)} templates)")

        print(f"{Colors.BRIGHT_GREEN}[{len(categories) + 1}]{Colors.RESET} {Colors.WHITE}View all templates{Colors.RESET}")
        print(f"{Colors.BRIGHT_GREEN}[0]{Colors.RESET} {Colors.WHITE}Return to main menu{Colors.RESET}\n")

        choice = input(f"{Colors.BRIGHT_YELLOW}Select category [0-{len(categories) + 1}]: {Colors.RESET}").strip()

        if choice == "0":
            return

        # Filter templates by category
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(categories):
                selected_category = categories[idx]
                templates = [t for t in all_templates if t.get('category') == selected_category]
            elif idx == len(categories):
                templates = all_templates
            else:
                print(f"{Colors.BRIGHT_RED}Invalid selection.{Colors.RESET}")
                return
        except ValueError:
            print(f"{Colors.BRIGHT_RED}Invalid input.{Colors.RESET}")
            return

        # Display templates
        print(f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}Templates:{Colors.RESET}\n")
        for idx, template_info in enumerate(templates, 1):
            print(f"{Colors.BRIGHT_GREEN}[{idx}]{Colors.RESET} {Colors.BRIGHT_WHITE}{template_info['name']}{Colors.RESET}")
            print(f"    {Colors.CYAN}{template_info['description']}{Colors.RESET}")

            # Show recommended models
            if template_info.get('recommended_models'):
                models_str = ', '.join(template_info['recommended_models'][:3])
                print(f"    {Colors.DIM}Recommended: {models_str}{Colors.RESET}")
            print()

        print(f"{Colors.BRIGHT_GREEN}[0]{Colors.RESET} {Colors.WHITE}Go back{Colors.RESET}\n")

        # Select template
        choice = input(f"{Colors.BRIGHT_YELLOW}Select template [0-{len(templates)}]: {Colors.RESET}").strip()

        if choice == "0":
            return

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(templates):
                selected_template_info = templates[idx]
                template_id = selected_template_info['id']
                template = self.template_manager.get_template(template_id)

                if not template:
                    print(f"{Colors.BRIGHT_RED}Failed to load template.{Colors.RESET}")
                    return

                # Display template details
                print(f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}Template: {selected_template_info['name']}{Colors.RESET}\n")
                print(f"{Colors.WHITE}{selected_template_info['description']}{Colors.RESET}\n")

                # Get required variables
                variables = template.get_required_variables()
                variable_values = {}

                if variables:
                    print(f"{Colors.BRIGHT_WHITE}Please provide values for template variables:{Colors.RESET}\n")

                    for var in variables:
                        var_name = var.get('name')
                        var_desc = var.get('description', '')
                        var_required = var.get('required', False)
                        var_default = var.get('default', '')

                        # Prompt for variable
                        if var_default:
                            prompt_str = f"{Colors.YELLOW}{var_name}{Colors.RESET} ({var_desc}) [{var_default}]: "
                        else:
                            required_marker = f"{Colors.RED}*{Colors.RESET}" if var_required else ""
                            prompt_str = f"{Colors.YELLOW}{var_name}{required_marker}{Colors.RESET} ({var_desc}): "

                        value = input(prompt_str).strip()

                        # Use default if empty
                        if not value and var_default:
                            value = var_default

                        # Check if required
                        if var_required and not value:
                            print(f"{Colors.BRIGHT_RED}Error: {var_name} is required.{Colors.RESET}")
                            return

                        variable_values[var_name] = value

                # Render template
                rendered = template.render(variable_values)
                system_prompt = rendered.get('system_prompt', '')
                user_prompt = rendered.get('user_prompt', '')

                # Display rendered prompts
                print(f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}Rendered Prompt:{Colors.RESET}\n")
                if system_prompt:
                    print(f"{Colors.BRIGHT_GREEN}System Prompt:{Colors.RESET}")
                    print(f"{Colors.DIM}{system_prompt}{Colors.RESET}\n")

                if user_prompt:
                    print(f"{Colors.BRIGHT_GREEN}User Prompt:{Colors.RESET}")
                    print(f"{Colors.WHITE}{user_prompt}{Colors.RESET}\n")

                # Recommend model based on template
                recommended_models = selected_template_info.get('recommended_models', [])
                model_id = None
                model_data = None

                if recommended_models:
                    # Try to find first available recommended model
                    for rec_model in recommended_models:
                        if rec_model in self.models:
                            model_id = rec_model
                            model_data = self.models[model_id]
                            break

                # Fallback to auto-detection if no recommended model found
                if not model_id:
                    use_case = ModelDatabase.detect_use_case(user_prompt)
                    model_id, model_data = ModelDatabase.recommend_model(use_case, self.models)

                print(f"{Colors.BRIGHT_GREEN}Recommended model: {Colors.BRIGHT_WHITE}{model_data['name']}{Colors.RESET}\n")

                # Ask if user wants to run
                if self._confirm(f"{Colors.BRIGHT_YELLOW}Run this template with recommended model? [Y/n]:{Colors.RESET}", default_yes=True):
                    # Use the full prompt (system + user combined for models without system prompt support)
                    if model_data.get('system_prompt') is None:
                        # Model doesn't support system prompts, combine them
                        full_prompt = f"{system_prompt}\n\n{user_prompt}" if system_prompt else user_prompt
                    else:
                        full_prompt = user_prompt

                    self.run_model(model_id, model_data, full_prompt)
            else:
                print(f"{Colors.BRIGHT_RED}Invalid selection.{Colors.RESET}")
        except ValueError:
            print(f"{Colors.BRIGHT_RED}Invalid input.{Colors.RESET}")
