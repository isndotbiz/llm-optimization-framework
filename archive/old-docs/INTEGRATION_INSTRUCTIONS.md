# Response Post-Processing Integration Instructions

## Files Created

1. **D:\models\response_processor.py** - Complete ResponseProcessor class
2. **D:\models\outputs\** - Directory for saved responses (auto-created)
3. **D:\models\post_processing_methods.txt** - Post-processing methods to add to AIRouter

## Integration Steps for ai-router.py

### Step 1: Import (ALREADY DONE)
The import statement has been added at line 19:
```python
from response_processor import ResponseProcessor
```

### Step 2: Initialize in AIRouter.__init__ (ALREADY DONE)
Added at lines 386-392:
```python
# Initialize response processor
self.output_dir = self.models_dir / "outputs"
self.response_processor = ResponseProcessor(self.output_dir)

# Store last response for post-processing
self.last_response = None
self.last_model_name = None
```

### Step 3: Add Post-Processing Methods
**INSERT LOCATION**: After `parse_llama_output` method (around line 710), BEFORE `run_model` method

Copy the entire contents of `post_processing_methods.txt` and insert at that location.

The methods to add are:
- `post_process_response()` - Main interactive menu
- `_save_response_to_file()` - Save response helper
- `_extract_and_save_code_blocks()` - Extract code blocks helper
- `_show_statistics()` - Show stats helper
- `_copy_to_clipboard()` - Clipboard helper
- `_export_as_markdown()` - Markdown export helper
- `_list_saved_responses()` - List saved files helper

### Step 4: Update run_model to Store Response
**LOCATION**: In `run_model()` method (around line 712+)

**FIND** (around line 719-726):
```python
if model_data['framework'] == 'mlx':
    response = self.run_mlx_model(model_id, model_data, prompt)
else:
    response = self.run_llamacpp_model(model_id, model_data, prompt)

if response:
    response.duration_seconds = time.time() - start_time

return response
```

**REPLACE WITH**:
```python
if model_data['framework'] == 'mlx':
    response = self.run_mlx_model(model_id, model_data, prompt)
else:
    response = self.run_llamacpp_model(model_id, model_data, prompt)

if response:
    response.duration_seconds = time.time() - start_time

    # Store for post-processing
    if hasattr(response, 'text') and response.text:
        self.last_response = response.text
        self.last_model_name = model_data['name']

        # Ask if user wants to post-process
        if self._confirm(f"\n{Colors.BRIGHT_CYAN}Post-process this response? [y/N]:{Colors.RESET}", default_yes=False):
            self.post_process_response(response.text, model_data['name'])

return response
```

### Step 5: Add Menu Option for Post-Processing Last Response
**LOCATION**: In `interactive_mode()` method (around line 530-565)

**FIND** the menu options section:
```python
print(f"{Colors.BRIGHT_GREEN}[5]{Colors.RESET} 📚 View documentation guides")

# Bypass mode toggle option
bypass_status = f"{Colors.BRIGHT_GREEN}ON{Colors.RESET}" if self.bypass_mode else f"{Colors.BRIGHT_RED}OFF{Colors.RESET}"
print(f"{Colors.BRIGHT_GREEN}[6]{Colors.RESET} 🔓 Toggle Auto-Yes Mode (Currently: {bypass_status})")

print(f"{Colors.BRIGHT_GREEN}[7]{Colors.RESET} 🚪 Exit")
```

**REPLACE WITH**:
```python
print(f"{Colors.BRIGHT_GREEN}[5]{Colors.RESET} 📚 View documentation guides")

# Bypass mode toggle option
bypass_status = f"{Colors.BRIGHT_GREEN}ON{Colors.RESET}" if self.bypass_mode else f"{Colors.BRIGHT_RED}OFF{Colors.RESET}"
print(f"{Colors.BRIGHT_GREEN}[6]{Colors.RESET} 🔓 Toggle Auto-Yes Mode (Currently: {bypass_status})")

# Post-processing option
post_process_status = f"{Colors.GREEN}available{Colors.RESET}" if self.last_response else f"{Colors.DIM}none{Colors.RESET}"
print(f"{Colors.BRIGHT_GREEN}[7]{Colors.RESET} ⚙️  Post-process last response (Status: {post_process_status})")

print(f"{Colors.BRIGHT_GREEN}[8]{Colors.RESET} 🚪 Exit")
```

**AND UPDATE** the menu prompt:
```python
choice = input(f"\n{Colors.BRIGHT_YELLOW}Enter choice [1-8]: {Colors.RESET}").strip()
```

**AND ADD** the handler in the if/elif chain:
```python
elif choice == "6":
    self.toggle_bypass_mode()
elif choice == "7":
    self.post_process_response()
elif choice == "8":
    print(f"\n{Colors.BRIGHT_GREEN}Goodbye!{Colors.RESET}\n")
    sys.exit(0)
```

## Optional: Add pyperclip to requirements

Create or update `requirements.txt`:
```
pyperclip  # Optional: For clipboard functionality
```

## Testing

1. Run the AI Router: `python ai-router.py`
2. Generate a response from any model
3. When prompted, choose to post-process
4. Test all menu options:
   - Save to file
   - Extract code blocks (test with a code response)
   - Show statistics
   - Copy to clipboard (if pyperclip installed)
   - Export as markdown
   - List saved responses
5. Check that files are created in `D:\models\outputs\`
6. Test the main menu option [7] to post-process last response

## Example Saved Response Format

```
================================================================================
AI ROUTER - MODEL RESPONSE
================================================================================
Generated: 2025-12-08 15:30:45
Model: Qwen3 Coder 30B Q4_K_M
================================================================================

[Response text here...]
```

## Example Markdown Export Format

```markdown
# AI Router Response

**Generated:** 2025-12-08 15:30:45
**Model:** Qwen3 Coder 30B Q4_K_M

---

## Response

[Response text here...]
```
