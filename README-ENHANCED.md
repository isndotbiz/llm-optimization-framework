# AI Router Enhanced v2.0

**Intelligent Multi-Model AI Orchestration System**

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/yourusername/ai-router-enhanced)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20WSL%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](https://github.com/yourusername/ai-router-enhanced)
[![Python](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## Overview

AI Router Enhanced is a production-ready, feature-complete AI project management system that intelligently routes requests to local and cloud AI models. Built on extensive 2025 research, it provides enterprise-grade conversation management, advanced analytics, batch processing, and workflow automation.

### Key Value Propositions

- **Unified Interface**: Single CLI for 15+ local models and 100+ cloud APIs
- **Smart Selection**: AI-powered model selection based on task requirements
- **Advanced Analytics**: Track performance, costs, and usage patterns
- **Workflow Automation**: Chain prompts into multi-step AI workflows
- **Session Management**: Persistent conversation history with SQLite backend
- **Template System**: Reusable prompt templates with variable substitution
- **Batch Processing**: Process multiple prompts with checkpointing and retry logic
- **Cost Optimization**: Track and optimize API costs across providers
- **Cross-Platform**: Windows, WSL, macOS, and Linux support

---

## Features at a Glance

### Core Features

| Feature | Description | Status |
|---------|-------------|--------|
| **Session Management** | SQLite-based conversation history with full CRUD operations | ✅ Production |
| **Prompt Templates** | YAML + Jinja2 template system with variable substitution | ✅ Production |
| **Model Comparison** | A/B test responses from multiple models side-by-side | ✅ Production |
| **Response Processing** | Automatic formatting, syntax highlighting, and export | ✅ Production |
| **Batch Processing** | Process hundreds of prompts with progress tracking | ✅ Production |
| **Smart Selection** | ML-based model recommendation with preference learning | ✅ Production |
| **Analytics Dashboard** | Performance metrics, usage stats, and cost tracking | ✅ Production |
| **Context Management** | Inject files, URLs, and code into conversations | ✅ Production |
| **Workflow Engine** | YAML-based prompt chaining with conditional logic | ✅ Production |

### Enhanced Capabilities

- **14 Local Models**: RTX 3090 (10 models) + M4 Pro (4 models)
- **5 Model Providers**: llama.cpp, Ollama, OpenRouter, OpenAI, Claude
- **100+ Cloud Models**: Access via OpenRouter, OpenAI, Anthropic
- **Multi-Format Export**: JSON, Markdown, HTML, PDF
- **Advanced Search**: Full-text search across conversation history
- **Tag System**: Organize sessions with custom tags
- **Bookmarks**: Mark and retrieve important conversations
- **Performance Tracking**: Tokens/sec, latency, and quality metrics

---

## Quick Start Guide

Get up and running in 5 simple steps:

### Step 1: Prerequisites

```bash
# Required
- Python 3.7+
- Git

# Optional (for local models)
- NVIDIA GPU with 8GB+ VRAM (RTX 3090 recommended)
- WSL 2 (Windows users, for 45-60% better performance)
- llama.cpp (for local GGUF models)
- Ollama (alternative local model runtime)
```

### Step 2: Installation

```bash
# Clone repository
cd D:\models  # Or your preferred directory

# Install Python dependencies
pip install -r requirements.txt

# Install optional dependencies (for enhanced features)
pip install jinja2 pyyaml matplotlib plotly  # Templates, analytics, visualization
pip install pdfplumber pypdf2  # PDF context injection
```

### Step 3: Initialize Database

```bash
# Run database setup script
python session_db_setup.py

# This creates .ai-router-sessions.db with the following tables:
# - sessions (conversation sessions)
# - messages (individual messages)
# - session_tags (tag associations)
# - bookmarks (starred conversations)
# - analytics (performance metrics)
```

### Step 4: Configure Models

```bash
# For local models (llama.cpp)
# Ensure models are in D:\models\organized\ (or ~/models/ on macOS)

# For cloud APIs, set environment variables:
export OPENROUTER_API_KEY="sk-or-..."
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."

# Or configure via menu: Menu > Configure Providers
```

### Step 5: Launch AI Router

```bash
# Start the application
python ai-router.py

# You'll see the main menu:
# [1] Start New Session
# [2] Resume Session
# [3] Use Template
# [4] Compare Models (A/B Test)
# [5] Batch Processing
# [6] Analytics Dashboard
# [7] Manage Templates
# [8] Smart Model Selection
# [9] Configure Settings
# [0] Exit
```

---

## System Requirements

### Minimum Requirements

- **OS**: Windows 10/11, macOS 10.14+, Ubuntu 18.04+
- **RAM**: 8GB (16GB recommended)
- **Storage**: 20GB free space
- **Python**: 3.7 or higher

### Recommended for Local Models

- **GPU**: NVIDIA RTX 3060 12GB or better (RTX 3090 24GB optimal)
- **RAM**: 32GB
- **Storage**: 100GB SSD
- **CPU**: 8+ cores (Ryzen 9 / Core i9 recommended)

### Cloud-Only Setup (No GPU Required)

- **RAM**: 8GB
- **Storage**: 5GB
- **Internet**: Stable connection for API calls

---

## Installation Instructions

### Full Installation (Local + Cloud)

```bash
# 1. Clone repository
git clone https://github.com/yourusername/ai-router-enhanced.git
cd ai-router-enhanced

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Install llama.cpp (WSL/Linux/macOS)
cd ~
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make LLAMA_CUBLAS=1  # For NVIDIA GPU
# Or: make LLAMA_METAL=1  # For Apple Silicon

# 4. Install Ollama (optional)
# Visit https://ollama.ai/download

# 5. Download models
# RTX 3090 models: See MODEL_REFERENCE_GUIDE.md
# M4 Pro models: See MACBOOK-M4-OPTIMIZATION-GUIDE.md

# 6. Initialize database
python session_db_setup.py

# 7. Configure API keys
export OPENROUTER_API_KEY="your-key-here"
export OPENAI_API_KEY="your-key-here"
export ANTHROPIC_API_KEY="your-key-here"

# 8. Launch
python ai-router.py
```

### Cloud-Only Installation (No Local Models)

```bash
# 1. Clone repository
git clone https://github.com/yourusername/ai-router-enhanced.git
cd ai-router-enhanced

# 2. Install dependencies (minimal)
pip install requests pyyaml jinja2

# 3. Initialize database
python session_db_setup.py

# 4. Configure API keys
export OPENROUTER_API_KEY="sk-or-..."

# 5. Launch
python ai-router.py
```

---

## Basic Usage Examples

### Example 1: Start a Simple Session

```python
# Launch AI Router
python ai-router.py

# Select: [1] Start New Session
# Choose model: [1] qwen3-coder-30b (or any available model)
# Enter prompt: "Explain how transformers work in 200 words"

# Model responds with explanation
# Continue conversation or type 'exit' to save and quit
```

### Example 2: Use a Template

```python
# Select: [3] Use Template
# Choose template: [2] Code Review Template
# Fill variables:
#   - language: Python
#   - code_snippet: [paste your code]
#   - focus_area: Performance

# Template renders and executes with context
# Response includes code analysis and suggestions
```

### Example 3: Compare Models (A/B Test)

```python
# Select: [4] Compare Models
# Choose Model A: [1] qwen3-coder-30b
# Choose Model B: [5] phi4-14b
# Enter prompt: "Solve: What is the integral of x^2 * sin(x)?"

# Both models respond side-by-side
# Compare quality, speed, and accuracy
# Vote for preferred response (learns your preferences)
```

### Example 4: Batch Processing

```python
# Create prompts file: batch_prompts.txt
# Line 1: Explain quantum entanglement
# Line 2: What is machine learning?
# Line 3: How do neural networks work?

# Select: [5] Batch Processing
# Load file: batch_prompts.txt
# Choose model: [1] qwen25-14b
# Processing starts with progress bar

# Results saved to: outputs/batch_results_[timestamp].json
# View analytics: tokens used, avg time, success rate
```

### Example 5: Analytics Dashboard

```python
# Select: [6] Analytics Dashboard
# View options:
#   [1] Usage Overview (last 30 days)
#   [2] Model Performance Comparison
#   [3] Cost Analysis (API usage)
#   [4] Session Statistics
#   [5] Export Report (CSV/JSON/HTML)

# Example output:
# Total Sessions: 147
# Total Messages: 2,341
# Total Tokens: 1.2M
# Avg Response Time: 2.3s
# Most Used Model: qwen3-coder-30b (45% of sessions)
# Total Cost: $12.34 (cloud APIs only)
```

---

## Feature Comparison Table

### AI Router v1.0 vs v2.0 Enhanced

| Feature | v1.0 (Original) | v2.0 (Enhanced) | Improvement |
|---------|-----------------|-----------------|-------------|
| **Session Management** | None | Full SQLite backend | ✅ Complete |
| **Conversation History** | Temporary | Persistent with search | ✅ Complete |
| **Prompt Templates** | None | YAML + Jinja2 system | ✅ Complete |
| **Model Comparison** | Manual | Side-by-side A/B testing | ✅ Complete |
| **Batch Processing** | None | Multi-prompt with checkpoints | ✅ Complete |
| **Model Selection** | Manual | AI-powered recommendation | ✅ Complete |
| **Analytics** | None | Full dashboard + export | ✅ Complete |
| **Response Processing** | Raw text | Formatted + highlighted | ✅ Complete |
| **Context Injection** | None | Files, URLs, code snippets | ✅ Complete |
| **Workflow Automation** | None | YAML-based chaining | ✅ Complete |
| **Export Formats** | None | JSON, MD, HTML, PDF | ✅ Complete |
| **Performance Tracking** | None | Tokens/sec, latency, quality | ✅ Complete |
| **Cost Tracking** | None | Per-model, per-session | ✅ Complete |
| **Tag System** | None | Custom tags + filters | ✅ Complete |
| **Bookmarks** | None | Star important sessions | ✅ Complete |
| **Search** | None | Full-text across history | ✅ Complete |

---

## Screenshots / ASCII Art

### Main Menu

```
╔════════════════════════════════════════════════════════════════════════════════╗
║                                                                                ║
║                         🤖  AI ROUTER CLI v2.0  🤖                            ║
║                                                                                ║
║           Intelligent Model Selection & Execution Framework                   ║
║              Enhanced Edition - Production Ready v2.0                         ║
║                                                                                ║
╚════════════════════════════════════════════════════════════════════════════════╝

Platform: Windows / WSL
Models: 15 local + 100+ cloud
Sessions: 147 | Messages: 2,341

──────────────────────────────────────────────────────────────────────────────────
 MAIN MENU
──────────────────────────────────────────────────────────────────────────────────

 [1] 💬 Start New Session          [6] 📊 Analytics Dashboard
 [2] 📖 Resume Session              [7] 📝 Manage Templates
 [3] 📋 Use Template                [8] 🎯 Smart Model Selection
 [4] ⚖️  Compare Models (A/B)        [9] ⚙️  Configure Settings
 [5] 📦 Batch Processing            [0] 🚪 Exit

──────────────────────────────────────────────────────────────────────────────────
Enter your choice (0-9):
```

### Analytics Dashboard Example

```
╔════════════════════════════════════════════════════════════════════════════════╗
║                          📊 ANALYTICS DASHBOARD                                ║
╚════════════════════════════════════════════════════════════════════════════════╝

📈 USAGE OVERVIEW (Last 30 Days)
──────────────────────────────────────────────────────────────────────────────────
Total Sessions:              147
Total Messages:            2,341
Total Tokens:          1,234,567
Average Tokens/Message:      527
Active Days:                  28 / 30

🏆 TOP MODELS
──────────────────────────────────────────────────────────────────────────────────
1. qwen3-coder-30b          66 sessions  (45%)  ████████████████████░░░░
2. phi4-14b                 32 sessions  (22%)  ██████████░░░░░░░░░░░░░░
3. gemma3-27b               28 sessions  (19%)  ████████░░░░░░░░░░░░░░░░
4. qwen25-14b               21 sessions  (14%)  ██████░░░░░░░░░░░░░░░░░░

💰 COST ANALYSIS (Cloud APIs Only)
──────────────────────────────────────────────────────────────────────────────────
OpenRouter:               $8.45
OpenAI:                   $3.12
Claude:                   $0.77
Total:                   $12.34

⚡ PERFORMANCE METRICS
──────────────────────────────────────────────────────────────────────────────────
Avg Response Time:         2.3s
Avg Tokens/Second:          38
Fastest Model:        dolphin-8b (65 tok/s)
Slowest Model:      llama33-70b (22 tok/s)
```

---

## Troubleshooting Section

### Common Issues and Solutions

#### Issue 1: Database Not Found

**Error**: `FileNotFoundError: .ai-router-sessions.db not found`

**Solution**:
```bash
# Run database initialization
python session_db_setup.py

# Verify creation
ls -la .ai-router-sessions.db
```

#### Issue 2: Model Not Loading (WSL)

**Error**: `CUDA out of memory` or `Model failed to load`

**Solution**:
```bash
# Check VRAM usage
nvidia-smi

# Reduce batch size in ai-router.py
# Change: -b 2048 → -b 1024

# Or use smaller quantization
# Q4_K_M instead of Q6_K
```

#### Issue 3: Template Variables Not Rendering

**Error**: `UndefinedError: 'variable_name' is undefined`

**Solution**:
```yaml
# Add default values in template YAML:
metadata:
  variables:
    - name: variable_name
      default: "default value"
      description: "What this variable does"
```

#### Issue 4: Slow Response Times

**Symptom**: Models responding slower than expected

**Solution**:
```bash
# 1. Check GPU utilization
nvidia-smi

# 2. Verify optimal parameters (WSL)
# Ensure using: -ngl 99 -t 24 -b 2048 --no-ppl

# 3. Check Windows vs WSL
# WSL llama.cpp is 45-60% faster than Windows

# 4. Monitor with performance script
python benchmark_features.py
```

#### Issue 5: API Key Errors

**Error**: `401 Unauthorized` or `Invalid API key`

**Solution**:
```bash
# Set environment variables permanently
# Windows PowerShell:
[Environment]::SetEnvironmentVariable("OPENROUTER_API_KEY", "sk-or-...", "User")

# WSL/Linux/macOS:
echo 'export OPENROUTER_API_KEY="sk-or-..."' >> ~/.bashrc
source ~/.bashrc

# Verify
echo $OPENROUTER_API_KEY
```

---

## Contributing Guidelines

We welcome contributions! Here's how to get started:

### How to Contribute

1. **Fork the Repository**
   ```bash
   git clone https://github.com/yourusername/ai-router-enhanced.git
   cd ai-router-enhanced
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Follow code style guidelines (see DEVELOPER_GUIDE.md)
   - Add tests for new features
   - Update documentation

3. **Test Your Changes**
   ```bash
   # Run test suite
   python -m pytest tests/

   # Run integration tests
   python test_integration.py

   # Validate code style
   flake8 *.py
   ```

4. **Submit Pull Request**
   - Write clear commit messages
   - Reference related issues
   - Include before/after examples

### Code Style

- **Python**: Follow PEP 8
- **Type Hints**: Use for all function signatures
- **Docstrings**: Google-style for all public methods
- **Comments**: Explain "why", not "what"

### Feature Requests

Open an issue with:
- Clear description of feature
- Use cases / examples
- Implementation suggestions (optional)

---

## License and Credits

### License

MIT License - See [LICENSE](LICENSE) file for details

### Credits

**Development Team**
- Lead Developer: [Your Name]
- Contributors: See [CONTRIBUTORS.md](CONTRIBUTORS.md)

**Built With**
- Python 3.x
- SQLite
- llama.cpp by Georgi Gerganov
- Jinja2 Template Engine
- PyYAML
- Rich (terminal formatting)
- Matplotlib & Plotly (analytics visualization)

**Research Sources**
- 2025 LLM Optimization Research (see MODEL_REFERENCE_GUIDE.md)
- OpenAI, Anthropic, Meta, Alibaba Cloud official documentation
- Community benchmarks: SWE-bench, HumanEval, AIME, MMLU

**Special Thanks**
- r/LocalLLaMA community
- HuggingFace community
- llama.cpp contributors
- All open-source model creators

---

## Related Documentation

- **[USER_GUIDE.md](USER_GUIDE.md)** - Comprehensive end-user guide
- **[DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)** - Technical architecture and API reference
- **[FEATURE_DOCUMENTATION.md](FEATURE_DOCUMENTATION.md)** - Detailed feature documentation
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - One-page cheat sheet
- **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** - Upgrade from v1.0 to v2.0
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and updates
- **[API_REFERENCE.md](API_REFERENCE.md)** - Complete API documentation

---

## Support and Community

### Getting Help

1. **Documentation**: Check the guides above first
2. **Issues**: [GitHub Issues](https://github.com/yourusername/ai-router-enhanced/issues)
3. **Discussions**: [GitHub Discussions](https://github.com/yourusername/ai-router-enhanced/discussions)
4. **Email**: support@yourproject.com

### Community Resources

- **Discord**: [Join our Discord](https://discord.gg/yourserver)
- **Reddit**: r/AIRouterEnhanced
- **Twitter**: @AIRouterProject

---

## Roadmap

### v2.1 (Planned - Q1 2025)

- [ ] Web UI (Flask/FastAPI dashboard)
- [ ] Voice input/output (Whisper integration)
- [ ] Image generation support (DALL-E, Stable Diffusion)
- [ ] Multi-modal conversations (vision models)
- [ ] Team collaboration features

### v2.2 (Planned - Q2 2025)

- [ ] Cloud sync (optional)
- [ ] Mobile companion app
- [ ] Plugin marketplace
- [ ] Advanced RAG with vector databases
- [ ] Auto-tuning system

### Long-Term Vision

- Enterprise features (SSO, audit logs)
- Cost optimization AI
- Model fine-tuning integration
- Distributed processing
- Custom model hosting

---

## Version Information

- **Current Version**: 2.0.0
- **Release Date**: December 8, 2025
- **Status**: Production Ready
- **Compatibility**: Python 3.7+
- **Platform Support**: Windows, WSL, macOS, Linux

---

**Star ⭐ this repository if you find it useful!**

[⬆ Back to Top](#ai-router-enhanced-v20)
