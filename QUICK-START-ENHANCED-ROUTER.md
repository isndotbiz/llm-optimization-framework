# AI Router MLX Enhanced - Quick Start Guide

**Status**: ✅ Complete and Ready to Use
**Server**: MLX on localhost:11434
**Models Available**: 6 total

---

## Overview

The AI Router MLX Enhanced is a comprehensive command-line tool for managing AI projects with multiple models, bot templates, and conversation memory. All menus support **numbered selection** for easy navigation.

---

## Quick Start

### 1. Start the Tool
```bash
cd ~/Workspace/llm-optimization-framework
python3 ai-router-mlx-enhanced.py
```

You'll see the main prompt:
```
mlx>
```

### 2. View Available Models (Numbered List)
```
mlx> models
```

Output:
```
Available Models (6 total):

  ✓ 1. qwen2.5-coder:7b
    2. qwen2.5-coder:32b
    3. qwen3:7b
    4. deepseek-r1:8b
    5. dolphin3:8b
    6. mistral:7b

Usage: select <number> or select <model_name>
```

### 3. Select a Model Using Numbers

**Option A: By Number** (Recommended)
```
mlx> select 1
✓ Model selected: qwen2.5-coder:7b
```

**Option B: By Name** (Still works)
```
mlx> select qwen3:7b
✓ Model selected: qwen3:7b
```

### 4. Ask the Model a Question
```
mlx> ask What is 2+2?
```

Model responds with the answer.

---

## Project Management

### Create a New Project
```
mlx> new

Project name: my-coding-project
Project description: A project for coding tasks
Select model: 1
Select bot template: 1
```

### View All Projects (Numbered List)
```
mlx> open

Available Projects:

  ► 1. my-coding-project
    2. another-project

Usage: open <number> or open <project_name>
```

### Open a Project Using Numbers
```
mlx> open 1
✓ Project opened: my-coding-project
```

### List Projects
```
mlx> list

Projects (2):

  ► my-coding-project
    another-project
```

### Delete a Project Using Numbers
```
mlx> delete

Available Projects:

  1. my-coding-project
  2. another-project

Usage: delete <number> or delete <project_name>

mlx> delete 2
Delete project 'another-project'? (y/n): y
```

---

## Bot Templates

### View All Bot Templates (Numbered List)
```
mlx> bots

Bot Templates:

  1. coder
     Specialized in coding, debugging, and architecture

  2. researcher
     Specializes in research and analysis

  3. writer
     Specializes in creative writing and content

  4. assistant
     General purpose AI assistant

  5. mathematician
     Specializes in math and logical reasoning

Usage: bot <number> or bot <template_name>
```

### Select a Bot Using Numbers
```
mlx> bot 1
✓ Using bot: coder
```

### View Bot Info
```
mlx> bot 3

Bot: Creative Writer
Description: Specializes in creative writing and content
Temperature: 0.9
```

---

## Conversation Features

### Start Interactive Chat
```
mlx> chat

Starting chat with qwen3:7b...
(Type 'exit' or 'quit' to return)

You: Explain machine learning
Assistant: [Response from model...]

You: exit
```

### View Conversation Memory
```
mlx> memory

Conversation History (5 messages):
[timestamp] User: Question 1
[timestamp] Assistant: Answer 1
...
```

### Clear History
```
mlx> clear
Clear conversation history? (y/n): y
✓ History cleared
```

---

## System Commands

### Get Help
```
mlx> help
```

Shows all available commands with descriptions.

### View System Status
```
mlx> status
```

Shows:
- Server status
- Available models
- Current project
- Current model
- Configuration directory

### Exit
```
mlx> exit
```
or
```
mlx> quit
```

---

## Command Reference

| Command | Purpose | Numbered Input |
|---------|---------|-----------------|
| `new` | Create new project | (in wizard) |
| `open <#/name>` | Open a project | ✅ Yes: `open 1` |
| `list` | List all projects | Shows numbers |
| `delete <#/name>` | Delete a project | ✅ Yes: `delete 1` |
| `info` | Show project details | N/A |
| `models` | List models | Shows numbers |
| `select <#/name>` | Select a model | ✅ Yes: `select 1` |
| `settings` | View model settings | N/A |
| `chat` | Interactive chat | N/A |
| `ask <question>` | Ask one-off question | N/A |
| `memory` | View conversation | N/A |
| `clear` | Clear history | N/A |
| `bots` | Show bot templates | Shows numbers |
| `bot <#/name>` | Select bot | ✅ Yes: `bot 1` |
| `status` | System status | N/A |
| `help` | Show help | N/A |
| `exit`/`quit` | Exit tool | N/A |

---

## Numbered Selection Examples

All of these work the same way - **type just the number**:

```bash
# Projects
mlx> open 1              # Opens first project
mlx> open my-project     # Still works by name
mlx> delete 2            # Deletes second project

# Models
mlx> select 3            # Selects third model
mlx> select qwen3:7b     # Still works by name

# Bots
mlx> bot 1               # Selects first bot
mlx> bot coder           # Still works by name
```

---

## Tips & Tricks

### 1. Quick Model Testing
```bash
mlx> select 1
mlx> ask What are your strengths?
```

### 2. Multi-Project Workflow
```bash
mlx> new                 # Create project 1
mlx> open 1             # Work on project 1
mlx> new                 # Create project 2
mlx> open 2             # Switch to project 2
```

### 3. Bot-Specific Projects
```bash
mlx> new                 # coding-project
  → select bot 1 (coder)
mlx> new                 # research-project
  → select bot 2 (researcher)
```

### 4. Command-Line Quick Check
```bash
python3 ai-router-mlx-enhanced.py --status    # System status
python3 ai-router-mlx-enhanced.py --list      # Show projects
python3 ai-router-mlx-enhanced.py --help      # Show help
```

---

## Configuration

Files are stored in:
```
~/.ai-router-mlx/
├── projects/          # Project configurations
├── memory/            # Conversation history
├── bots/              # Bot definitions
└── config.json        # System settings
```

---

## Troubleshooting

### "Server is not running"
Start the MLX server:
```bash
source ~/venv-mlx/bin/activate
python3 mlx-server.py
```

### "No models available"
Make sure the MLX server is running and models are downloaded:
```bash
curl http://localhost:11434/v1/models
```

### "Model not found"
Check available models:
```bash
mlx> models
```

Then use the correct number or name.

---

## Next Steps

1. **Create a project**: `new`
2. **Select a model**: `select 1`
3. **Ask a question**: `ask Your question here`
4. **Start chatting**: `chat`
5. **View history**: `memory`

Enjoy! 🚀
