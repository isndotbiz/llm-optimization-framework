# AI Router Enhanced v2.0 - Quick Start Guide

## Overview

AI Router Enhanced is a complete AI project management system that extends the original AI Router with powerful features for managing projects, bots, multi-provider support, web search, and conversation memory.

## New Features in v2.0

### 1. Project Management System
- Create dedicated projects with individual configurations
- Each project stored in `D:\models\projects\{project_name}/`
- Project structure:
  - `config.json` - Project configuration
  - `memory.json` - Conversation history
  - `data/` - Folder for web search results, PDFs, etc.

### 2. Bot Management System
- Load bot templates from `D:\models\bots/`
- Available bot templates:
  - **Coding Expert** - Advanced coding, code review, architecture
  - **Research Assistant** - Research and analysis tasks
  - **Creative Writer** - Creative writing and storytelling
  - **Reasoning Expert** - Complex reasoning and problem solving
  - **Fast Assistant** - Quick general tasks
- Create specialized projects from templates with one command

### 3. Full Parameter Configuration
Configure per project:
- **Temperature**: 0.0-2.0 (creativity level)
- **Top P**: 0.0-1.0 (nucleus sampling)
- **Top K**: 0-200 (token selection limit)
- **Max Tokens**: 1-32768 (response length)
- **Context Limit**: 1-100 messages or unlimited (-1)
- **Presence Penalty**: -2.0 to 2.0
- **Frequency Penalty**: -2.0 to 2.0
- **Reasoning Effort**: none/low/medium/high (future support)

### 4. Multi-Provider Support
Supported providers:
- **llama.cpp** - Local model execution (default, no API key)
- **Ollama** - Local model execution (no API key)
- **OpenRouter** - Multi-model API access (requires API key)
- **OpenAI** - GPT models (requires API key)
- **Claude** - Anthropic Claude (requires API key)

### 5. Web Search Integration
- **Brave Search API** - Web search results
- **Perplexity API** - AI-powered search and answers
- Enable/disable per project
- Store API keys securely in configuration

### 6. Memory System
- Conversation history saved per project
- View recent conversations
- Clear memory when needed
- Timestamps and model tracking

### 7. System Prompt Management
- View current system prompt
- Edit/customize prompts per project
- Warning when model doesn't support system prompts
- Save custom prompts with project

## Quick Start

### Installation

1. Ensure you have Python 3.7+ installed
2. The enhanced router is located at: `D:\models\ai-router-enhanced.py`
3. Run: `python D:\models\ai-router-enhanced.py`

### First Time Setup

```bash
# Run the enhanced router
python D:\models\ai-router-enhanced.py

# You'll see the main menu with 12 options
```

### Creating Your First Project

1. Select **[1] Create New Project**
2. Enter project name (e.g., "coding-project")
3. Enter project title (e.g., "My Coding Assistant")
4. Select a model from the list
5. Configure parameters (or press Enter for defaults)
6. Project is created and ready to use!

### Creating a Bot from Template

1. Select **[3] Create Specialized Bot**
2. Browse available bot templates
3. Select a template (e.g., "Coding Expert")
4. Enter project name
5. Bot project is created with optimized settings!

### Running a Chat Session

1. Load a project (menu option 2)
2. Select **[6] Run Chat Session**
3. Start chatting!
4. Type 'exit' or 'quit' to end session
5. Conversation history is automatically saved

## Main Menu Options

```
[1]  Create New Project          - Start a new AI project
[2]  Load Existing Project       - Open a saved project
[3]  Create Specialized Bot      - Use a bot template
[4]  View/Edit System Prompt     - Customize system prompt
[5]  Configure Parameters        - Adjust model parameters
[6]  Run Chat Session           - Start interactive chat
[7]  View Conversation History   - Review past conversations
[8]  Configure Web Search        - Setup Brave/Perplexity
[9]  Configure Providers         - Setup API keys
[10] View Documentation          - Read guides
[11] Settings                    - Bypass mode, delete projects
[12] Exit                        - Quit application
```

## Project Configuration Example

```json
{
  "title": "Coding Expert Assistant",
  "created": "2025-12-08T19:30:00",
  "modified": "2025-12-08T19:30:00",
  "model": "qwen3-coder-30b",
  "provider": "llama-cpp",
  "system_prompt": "You are an expert software engineer...",
  "parameters": {
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 40,
    "max_tokens": 4096,
    "context_limit": 50,
    "presence_penalty": 0.0,
    "frequency_penalty": 0.3
  },
  "web_search": {
    "enabled": false
  },
  "reasoning_effort": "none"
}
```

## Bot Template Structure

Bot templates are JSON files in `D:\models\bots/`:

```json
{
  "bot_name": "coding-expert",
  "title": "Coding Expert Bot",
  "description": "Specialized for advanced coding tasks",
  "specialization": "coding",
  "provider": "llama-cpp",
  "model": "qwen3-coder-30b",
  "system_prompt": "You are an expert software engineer...",
  "default_parameters": {
    "temperature": 0.7,
    "top_p": 0.9,
    "max_tokens": 4096
  }
}
```

## Project Directory Structure

```
D:\models\projects\
├── coding-project\
│   ├── config.json       # Project configuration
│   ├── memory.json       # Conversation history
│   └── data\             # Additional data files
├── research-project\
│   ├── config.json
│   ├── memory.json
│   └── data\
└── ...
```

## Advanced Features

### Web Search Integration

1. Menu option **[8] Configure Web Search**
2. Select Brave or Perplexity
3. Enter API key
4. Enable in project configuration
5. Search results stored in project's `data/` folder

### Provider Configuration

1. Menu option **[9] Configure Providers**
2. Select provider (OpenRouter, OpenAI, Claude, etc.)
3. Enter API key if required
4. Provider is now available for projects

### Bypass Mode

- Enable via **[11] Settings**
- Auto-accepts all confirmation prompts
- Useful for automation
- Shows "AUTO-YES MODE ACTIVE" banner when enabled

### Conversation Memory

- Automatically saves all conversations
- View with menu option **[7]**
- Shows timestamps, user prompts, responses
- Can clear memory when needed

## Model Support

### RTX 3090 Models (11 models)
- Qwen3 Coder 30B
- Qwen2.5 Coder 32B
- Phi-4 14B
- Gemma 3 27B
- Ministral-3 14B
- DeepSeek R1 14B
- Llama 3.3 70B
- Dolphin Llama 3.1 8B
- Dolphin Mistral 24B
- Wizard Vicuna 13B

### MacBook M4 Models (4 models)
- Qwen2.5 14B (MLX)
- Qwen2.5 Coder 14B (MLX)
- Phi-4 14B (MLX)
- Gemma-3 9B (MLX)

## Tips & Best Practices

1. **Project Organization**
   - Create separate projects for different use cases
   - Use descriptive project names
   - Utilize bot templates for quick setup

2. **Parameter Tuning**
   - Start with defaults
   - Adjust temperature for creativity
   - Use lower temperature (0.3-0.5) for code
   - Use higher temperature (0.8-1.2) for creative writing

3. **System Prompts**
   - Customize for your specific needs
   - Be specific about output format
   - Include examples when helpful
   - Remember: Gemma models don't support system prompts

4. **Memory Management**
   - Review conversation history regularly
   - Clear memory for fresh context
   - Export important conversations

5. **Provider Selection**
   - Use llama.cpp for local models (free)
   - Use OpenRouter for variety (paid)
   - Use OpenAI/Claude for specific capabilities (paid)

## Troubleshooting

### Project Not Loading
- Check if `config.json` exists in project folder
- Verify JSON syntax is valid
- Check file permissions

### Model Not Found
- Ensure model ID matches available models
- Check if model file exists at specified path
- Verify framework (llama.cpp vs MLX)

### Web Search Not Working
- Verify API key is configured
- Check API key is valid
- Ensure web search is enabled in project config

### Parameters Not Applied
- Save project after changing parameters
- Reload project to apply changes
- Check parameter values are in valid ranges

## Comparison: Original vs Enhanced

| Feature | Original | Enhanced |
|---------|----------|----------|
| Projects | No | Yes (unlimited) |
| Bot Templates | No | Yes (5 included) |
| Memory | No | Yes (per project) |
| Providers | llama.cpp only | 5 providers |
| Web Search | No | Yes (2 APIs) |
| System Prompts | File-based | Customizable per project |
| Parameters | Command-line | Interactive config |
| History | No | Yes (saved) |

## Next Steps

1. Create your first project
2. Try a bot template
3. Customize system prompts
4. Experiment with parameters
5. Configure web search (optional)
6. Set up external providers (optional)

## Support & Documentation

- Original AI Router: `D:\models\ai-router.py`
- Enhanced Router: `D:\models\ai-router-enhanced.py`
- Bot Templates: `D:\models\bots/`
- Projects: `D:\models\projects/`
- Documentation: Menu option [10]

---

**Version**: 2.0
**Date**: 2025-12-08
**Compatibility**: Windows, WSL, macOS, Linux
