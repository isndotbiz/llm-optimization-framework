# AI Router Enhanced v2.0 - User Guide

**Complete End-User Documentation**

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Navigation Tutorial](#navigation-tutorial)
3. [Feature Walkthroughs](#feature-walkthroughs)
4. [Common Workflows](#common-workflows)
5. [Tips and Best Practices](#tips-and-best-practices)
6. [Keyboard Shortcuts](#keyboard-shortcuts)
7. [Frequently Asked Questions](#frequently-asked-questions)

---

## Getting Started

### First Launch

When you first launch AI Router Enhanced, you'll see the main menu:

```bash
python ai-router.py
```

The application will:
1. Initialize the database (if needed)
2. Detect your platform (Windows/WSL/macOS/Linux)
3. Scan for available models
4. Display the main menu

### Your First Session

Let's create your first AI conversation:

**Step 1: Start a new session**
```
Select: [1] Start New Session
```

**Step 2: Choose a model**
```
Available Models:
[1] qwen3-coder-30b      - Best for coding (94% HumanEval)
[2] phi4-14b             - Best for math/reasoning (85% AIME)
[3] gemma3-27b           - Best for creative writing
[4] qwen25-14b           - Best for general use

Enter choice: 1
```

**Step 3: Set a title (optional)**
```
Session title (or press Enter for auto-title): My first coding session
```

**Step 4: Start chatting**
```
You: Write a Python function to calculate Fibonacci numbers

[Model generates response]

You: Now optimize it with memoization

[Model generates improved version]

You: exit
Session saved! ID: abc123...
```

---

## Navigation Tutorial

### Main Menu Structure

```
╔═══════════════════════════════════════╗
║       AI ROUTER MAIN MENU             ║
╠═══════════════════════════════════════╣
║ [1] 💬 Start New Session             ║  ← Create new conversation
║ [2] 📖 Resume Session                 ║  ← Continue existing conversation
║ [3] 📋 Use Template                   ║  ← Use pre-made prompt templates
║ [4] ⚖️  Compare Models                 ║  ← A/B test multiple models
║ [5] 📦 Batch Processing               ║  ← Process multiple prompts
║ [6] 📊 Analytics Dashboard            ║  ← View usage statistics
║ [7] 📝 Manage Templates               ║  ← Create/edit templates
║ [8] 🎯 Smart Model Selection          ║  ← AI-powered model recommendation
║ [9] ⚙️  Configure Settings             ║  ← App settings and preferences
║ [0] 🚪 Exit                           ║  ← Exit application
╚═══════════════════════════════════════╝
```

### Session Menu (During Conversation)

When you're in an active session, you have access to:

```
Active Session: "My coding project"
Model: qwen3-coder-30b | Messages: 12 | Tokens: 4,521

Commands:
  /help          - Show this help
  /save          - Save and continue
  /tags          - Add tags to session
  /bookmark      - Bookmark this session
  /context       - Add file/URL context
  /export        - Export conversation
  /switch        - Switch to different model
  /clear         - Clear conversation history
  exit/quit      - Save and exit session

Your prompt:
```

---

## Feature Walkthroughs

### Feature 1: Session Management

**Purpose**: Manage conversation history across multiple sessions

**How to Use**:

1. **Create a new session**
   ```
   Menu > [1] Start New Session
   Choose model > Enter title > Start chatting
   ```

2. **Resume an existing session**
   ```
   Menu > [2] Resume Session

   Recent Sessions:
   [1] My coding project (qwen3-coder-30b) - 2 hours ago - 12 messages
   [2] Math homework (phi4-14b) - 1 day ago - 8 messages
   [3] Story writing (gemma3-27b) - 3 days ago - 15 messages

   Enter choice: 1
   ```

3. **Search sessions**
   ```
   Menu > [2] Resume Session > [s] Search

   Enter search query: python flask

   Found 3 sessions:
   [1] Flask API development (6 days ago)
   [2] Python web frameworks comparison (2 weeks ago)
   [3] Flask deployment guide (1 month ago)
   ```

4. **Filter by tags**
   ```
   Menu > [2] Resume Session > [t] Filter by tag

   Available tags: coding, math, creative, research, debug

   Enter tag: coding

   Sessions with tag 'coding': 23 found
   ```

**Advanced Tips**:
- Use descriptive titles for easy searching later
- Add tags during or after conversation with `/tags` command
- Bookmark important sessions with `/bookmark`
- Export sessions before major edits with `/export`

---

### Feature 2: Prompt Templates

**Purpose**: Reusable prompt structures with variable substitution

**Built-in Templates**:

1. **Code Review** - Analyze code for bugs and improvements
2. **Research Summary** - Summarize academic papers or articles
3. **Creative Story** - Generate stories with specific parameters
4. **Debug Assistant** - Help debug code with stack traces
5. **Explain Like I'm 5** - Simplify complex topics

**How to Use a Template**:

```
Menu > [3] Use Template

Available Templates:
[1] Code Review
[2] Research Summary
[3] Creative Story
[4] Debug Assistant
[5] Explain Like I'm 5
[c] Create new template

Enter choice: 1

─────────────────────────────────────────
Code Review Template
─────────────────────────────────────────

Fill in the following variables:

Language: Python
Code (paste below, end with Ctrl+D):
def calculate_average(numbers):
    return sum(numbers) / len(numbers)
^D

Focus areas (performance/security/style): performance, security

─────────────────────────────────────────
Rendering template...

System Prompt: You are an expert code reviewer...
User Prompt: Please review this Python code...

Execute with model:
[1] qwen3-coder-30b (recommended)
[2] phi4-14b
[s] Skip and save rendered prompt

Choice: 1

[Model executes review...]
```

**Creating Custom Templates**:

```
Menu > [7] Manage Templates > [c] Create new

Template name: API Testing
Description: Generate API test cases

Variables (one per line, format: name|description|default):
endpoint|API endpoint URL|/api/v1/users
method|HTTP method|GET
auth_type|Authentication type|Bearer token

System prompt:
You are an API testing expert. Generate comprehensive test cases for REST APIs.

User prompt:
Generate test cases for {{method}} {{endpoint}} with {{auth_type}} authentication.
Include: happy path, error cases, edge cases, security tests.

Save template? (y/n): y
Template saved: D:\models\prompt-templates\api-testing.yaml
```

---

### Feature 3: Model Comparison (A/B Testing)

**Purpose**: Compare responses from multiple models side-by-side

**How to Use**:

```
Menu > [4] Compare Models

Select Model A:
[1] qwen3-coder-30b
[2] phi4-14b
[3] gemma3-27b
Choice: 1

Select Model B:
[1] phi4-14b
[2] gemma3-27b
[3] qwen25-14b
Choice: 2

Enter prompt: Explain the P vs NP problem in simple terms

─────────────────────────────────────────
Executing on both models...

╔══════════════════════════════════════════════╗
║         MODEL A: qwen3-coder-30b            ║
╚══════════════════════════════════════════════╝

[Response A - 2.3 seconds, 247 tokens]
The P vs NP problem asks whether every problem whose solution
can be quickly verified can also be quickly solved...

╔══════════════════════════════════════════════╗
║         MODEL B: phi4-14b                   ║
╚══════════════════════════════════════════════╝

[Response B - 1.8 seconds, 312 tokens]
P vs NP is one of the most important unsolved problems
in computer science. P represents problems that can be...

─────────────────────────────────────────────

Which response did you prefer?
[A] Model A (qwen3-coder-30b)
[B] Model B (phi4-14b)
[T] Tie
[S] Skip voting

Choice: B

Preference saved! This helps improve model recommendations.

Export comparison? (y/n): y
Saved to: outputs/comparison_2025-12-08_15-30-45.json
```

**Comparison Metrics**:
- Response time
- Token count
- Clarity rating (manual vote)
- Accuracy (for factual queries)
- Cost (for cloud models)

---

### Feature 4: Batch Processing

**Purpose**: Process multiple prompts automatically with progress tracking

**How to Use**:

**Step 1: Create prompts file**
```
# prompts.txt
Explain quantum entanglement
What is the theory of relativity?
How do neural networks work?
Describe photosynthesis
Explain DNA replication
```

**Step 2: Start batch job**
```
Menu > [5] Batch Processing > [n] New batch job

Prompts source:
[1] Load from file
[2] Enter manually
[3] Import from CSV

Choice: 1

File path: D:\prompts\prompts.txt
Loaded: 5 prompts

Select model:
[1] qwen25-14b (recommended for mixed topics)
[2] phi4-14b (best for technical)
[3] gemma3-27b (best for creative)

Choice: 1

Processing settings:
- Delay between prompts: 2 seconds
- Max retries on error: 3
- Save checkpoint every: 5 prompts

Start batch processing? (y/n): y

─────────────────────────────────────────────
Processing batch: 5 prompts
Model: qwen25-14b
Started: 2025-12-08 15:45:00
─────────────────────────────────────────────

[1/5] ████████████████████████████████  Complete (2.1s)
[2/5] ████████████████████████████████  Complete (3.4s)
[3/5] ████████████████████████████████  Complete (2.8s)
[4/5] ████████████████████████████████  Complete (2.5s)
[5/5] ████████████████████████████████  Complete (3.1s)

─────────────────────────────────────────────
Batch complete!
Total time: 13.9s
Success rate: 100% (5/5)
Avg response time: 2.78s
Total tokens: 1,247
Results saved: outputs/batch_12345678.json
─────────────────────────────────────────────
```

**Step 3: View results**
```
Menu > [5] Batch Processing > [r] View recent jobs

Recent Batch Jobs:
[1] batch_12345678 - Complete (5/5) - 2 minutes ago
[2] batch_87654321 - Complete (10/10) - 1 hour ago
[3] batch_11223344 - Failed (7/10) - 2 days ago

Enter job ID: 12345678

Batch Job: batch_12345678
Status: Complete
Started: 2025-12-08 15:45:00
Completed: 2025-12-08 15:45:14
Duration: 13.9 seconds
Success: 5/5 (100%)

Individual results:
[1] Explain quantum entanglement - ✓ Success (247 tokens, 2.1s)
[2] What is the theory of relativity? - ✓ Success (312 tokens, 3.4s)
[3] How do neural networks work? - ✓ Success (289 tokens, 2.8s)
...

[e] Export results
[v] View individual response
[d] Delete job
[b] Back

Choice: v

Enter result number: 1

Prompt: Explain quantum entanglement

Response:
Quantum entanglement is a phenomenon where two or more particles
become correlated in such a way that the quantum state of each
particle cannot be described independently...

[Full response shown]
```

---

### Feature 5: Analytics Dashboard

**Purpose**: Track usage, performance, and costs

**How to Use**:

```
Menu > [6] Analytics Dashboard

╔════════════════════════════════════════════╗
║        📊 ANALYTICS DASHBOARD              ║
╚════════════════════════════════════════════╝

[1] Usage Overview (last 30 days)
[2] Model Performance Comparison
[3] Cost Analysis (cloud APIs)
[4] Session Statistics
[5] Custom Date Range
[6] Export Report
[0] Back to main menu

Choice: 1

───────────────────────────────────────────────
📈 USAGE OVERVIEW - Last 30 Days
───────────────────────────────────────────────

Total Sessions: 147
Total Messages: 2,341
Total Tokens: 1,234,567
Active Days: 28/30
Avg Messages/Day: 78

📅 DAILY ACTIVITY
Dec 1  ████████████░░░░░░░░  64 messages
Dec 2  ████████████████░░░░  85 messages
Dec 3  ██████████░░░░░░░░░░  52 messages
...
Dec 8  ████████████████████  102 messages (today)

🏆 TOP MODELS
1. qwen3-coder-30b     66 sessions (45%)
2. phi4-14b            32 sessions (22%)
3. gemma3-27b          28 sessions (19%)
4. qwen25-14b          21 sessions (14%)

📊 SESSION CATEGORIES
Coding:     89 sessions (61%)
Math:       24 sessions (16%)
Creative:   19 sessions (13%)
Research:   15 sessions (10%)

[Press Enter to continue...]
```

---

## Common Workflows

### Workflow 1: Code Development Assistant

**Scenario**: You're building a Python web app and need coding help

```
Step 1: Start session with coding model
Menu > [1] New Session > qwen3-coder-30b

Step 2: Add project context
You: /context
Context type: [1] Directory
Path: D:\projects\my-flask-app
Indexed: 47 Python files (12,445 lines)

Step 3: Ask for help
You: Review my user authentication code in auth.py and suggest improvements

[Model analyzes with full project context]

Step 4: Iterate
You: Implement the password hashing suggestion you mentioned

[Model provides updated code]

Step 5: Tag and bookmark
You: /tags
Tags: python, flask, authentication, security

You: /bookmark
Bookmarked: My Flask App Development

Step 6: Export for reference
You: /export
Format: [1] Markdown
Saved: conversations/flask-auth-improvements.md
```

### Workflow 2: Research Paper Analysis

**Scenario**: You need to understand and summarize a complex research paper

```
Step 1: Use research template
Menu > [3] Use Template > [2] Research Summary

Step 2: Provide PDF
PDF path: D:\papers\transformer-architecture.pdf
Extracted: 12 pages, 8,547 words

Variables:
- Focus: Architecture and attention mechanism
- Summary length: 500 words
- Technical level: Intermediate

Step 3: Execute with reasoning model
Model: [2] phi4-14b (best for analysis)

[Model generates detailed summary]

Step 4: Follow-up questions
You: Explain the multi-head attention mechanism in detail

You: How does this compare to RNNs?

Step 5: Save session with tags
You: /tags
Tags: ml, research, transformers, papers

You: /save
Session saved and continuing...
```

### Workflow 3: Creative Writing Project

**Scenario**: Writing a sci-fi short story with AI assistance

```
Step 1: Start with creative model
Menu > [1] New Session > gemma3-27b (abliterated, creative)

Step 2: Set up story parameters
You: I want to write a sci-fi story about first contact with aliens.
     The story should be 2000 words, serious tone, focus on the
     linguistic challenges of communication.

[Model generates story outline]

Step 3: Develop sections iteratively
You: Expand section 2 - the first communication attempt

You: Make the alien perspective more alien - avoid humanization

You: Add more sensory details to the spacecraft description

Step 4: Get alternative versions
You: Generate 3 different endings for this story

Step 5: Compare and refine
Menu > [4] Compare Models
Model A: gemma3-27b (current)
Model B: qwen25-14b (alternative perspective)
Prompt: [paste story] Generate a twist ending

[Compare both endings and choose preferred]
```

---

## Tips and Best Practices

### Model Selection Tips

**For Coding Tasks**:
- ✅ Use `qwen3-coder-30b` or `qwen25-coder-32b` for production code
- ✅ Use `phi4-14b` for algorithmic problems and optimization
- ✅ Add `/context` with your entire codebase for better suggestions
- ❌ Avoid creative models (gemma3, creative writing focus)

**For Math and Reasoning**:
- ✅ Use `phi4-14b` (85% AIME performance)
- ✅ Use `ministral-3-14b` for complex multi-step reasoning
- ✅ Use `deepseek-r1-14b` for chain-of-thought problems
- ❌ Avoid fast models (dolphin-8b) for complex calculations

**For Creative Writing**:
- ✅ Use `gemma3-27b` (abliterated, 128K context)
- ✅ Higher temperature (0.8-0.9) for more creativity
- ✅ Use longer contexts for better consistency
- ❌ Avoid coding models (too structured/rigid)

**For General Use**:
- ✅ Use `qwen25-14b` (balanced)
- ✅ Use `llama33-70b` for complex multi-domain tasks
- ✅ Start with smart model selection for recommendations

### Performance Tips

**Faster Responses**:
- Use smaller models: `dolphin-8b`, `wizard-vicuna-13b`
- Reduce max_tokens parameter
- Use Q4_K_M quantization instead of Q6_K
- WSL instead of Windows (45-60% faster)

**Better Quality**:
- Use larger models: `llama33-70b`, `qwen3-coder-30b`
- Higher quantization: Q6_K, Q8_0
- Add relevant context with `/context`
- Use templates for structured prompts

**Cost Optimization (Cloud Models)**:
- Use local models when possible (free)
- Check analytics before expensive operations
- Batch process instead of interactive sessions
- Use cheaper models for drafts, expensive for finals

### Session Management Tips

**Organization**:
- Use descriptive session titles
- Add tags immediately after creation
- Bookmark important sessions
- Export before making major changes

**Searching**:
- Use specific keywords in titles
- Tag by project, topic, and type
- Search by date range for recent work
- Filter by model for consistency

**Cleanup**:
- Regularly export and archive old sessions
- Delete failed or test sessions
- Merge related sessions when practical

---

## Keyboard Shortcuts

### Global Shortcuts (Main Menu)

| Shortcut | Action |
|----------|--------|
| `1-9` | Select menu option |
| `0` | Exit application |
| `Ctrl+C` | Cancel current operation (safe) |
| `Ctrl+D` | Exit (same as option 0) |

### Session Shortcuts (During Conversation)

| Shortcut | Action |
|----------|--------|
| `/help` | Show available commands |
| `/save` | Save session and continue |
| `/exit` | Save and exit session |
| `/tags` | Add/edit session tags |
| `/bookmark` | Bookmark current session |
| `/context` | Add file/URL/code context |
| `/export` | Export conversation |
| `/switch` | Switch to different model |
| `/clear` | Clear conversation history |
| `/stats` | Show session statistics |
| `Ctrl+C` | Cancel current generation |

### Template Editor Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+S` | Save template |
| `Ctrl+Q` | Quit without saving |
| `Ctrl+V` | Preview rendered template |
| `Ctrl+T` | Test with sample variables |

### Batch Processing Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+P` | Pause batch job |
| `Ctrl+R` | Resume paused job |
| `Ctrl+S` | Save checkpoint |
| `Ctrl+C` | Cancel batch (saves progress) |

---

## Frequently Asked Questions

### General Questions

**Q1: What's the difference between AI Router v1.0 and v2.0 Enhanced?**

A: Version 2.0 adds:
- Persistent session management with SQLite
- Prompt template system with variables
- Model comparison (A/B testing)
- Batch processing with checkpoints
- Analytics dashboard
- Context injection from files/URLs
- Workflow automation
- And 20+ other major features

See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for complete list.

**Q2: Can I use this without a GPU?**

A: Yes! You can:
- Use cloud-only mode (OpenRouter, OpenAI, Claude)
- Use Ollama with CPU inference (slower)
- Use M4 MacBook with Metal acceleration
- Rent GPU via cloud services

**Q3: How much does it cost to use cloud models?**

A: Costs vary by provider:
- OpenRouter: $0.01 - $5 per million tokens
- OpenAI GPT-4: ~$30 per million tokens
- Claude: $3 - $15 per million tokens
- Local models: FREE (only hardware costs)

Track costs in real-time with Analytics Dashboard.

**Q4: Can I use multiple models in one session?**

A: Yes! Use the `/switch` command during a session:
```
You: /switch
New model: [2] phi4-14b
Switched! Previous: qwen3-coder-30b → New: phi4-14b
```

**Q5: Where is my data stored?**

A: All data is stored locally:
- Sessions: `.ai-router-sessions.db` (SQLite)
- Templates: `prompt-templates/` folder
- Exports: `outputs/` folder
- Logs: `logs/` folder

No cloud sync (unless you enable it).

### Feature-Specific Questions

**Q6: How do templates work with variables?**

A: Templates use Jinja2 syntax:
```yaml
user_prompt: |
  Analyze this {{language}} code:
  {{code}}

  Focus on: {{focus_areas}}
```

When you use the template, you fill in the variables:
- `language`: Python
- `code`: [your code]
- `focus_areas`: performance, security

**Q7: Can I create my own templates?**

A: Absolutely! See section on Creating Custom Templates above, or use:
```
Menu > [7] Manage Templates > [c] Create new
```

**Q8: What's the maximum context length?**

A: Depends on model:
- Most models: 16K - 32K tokens
- Large context: 128K - 256K tokens (gemma3-27b, ministral-3-14b)
- Cloud models: up to 200K tokens (Claude, GPT-4)

Check model details in MODEL_REFERENCE_GUIDE.md

**Q9: How does smart model selection work?**

A: The system uses:
1. Keyword analysis of your prompt
2. Your past preferences (learned from comparisons)
3. Model capabilities database
4. Current system resources

Example:
```
Prompt: "Optimize this Python sorting algorithm"
Recommended: qwen3-coder-30b (coding keywords detected)

Prompt: "Prove the Pythagorean theorem"
Recommended: phi4-14b (math keywords detected)
```

**Q10: Can I export conversations?**

A: Yes, in multiple formats:
- JSON (machine-readable)
- Markdown (human-readable)
- HTML (web-friendly)
- PDF (print-ready, requires deps)

Use `/export` during session or from Analytics > Session Statistics.

### Technical Questions

**Q11: Why is WSL faster than Windows for local models?**

A: WSL provides:
- Better CUDA driver integration
- Lower overhead for GPU calls
- Optimized memory management
- 45-60% performance improvement

**Q12: How do I update to the latest version?**

A: Pull latest changes:
```bash
git pull origin main
pip install -r requirements.txt --upgrade
python session_db_setup.py  # Migrate database if needed
```

**Q13: Can I use this with my own fine-tuned models?**

A: Yes! Add to ModelDatabase in `ai-router.py`:
```python
"my-custom-model": {
    "name": "My Custom Model",
    "path": "/path/to/model.gguf",
    "size": "8GB",
    "speed": "40 tok/sec",
    "use_case": "My specific use case",
    ...
}
```

**Q14: How do I backup my sessions?**

A: Copy the database file:
```bash
# Backup
cp .ai-router-sessions.db backups/sessions-2025-12-08.db

# Restore
cp backups/sessions-2025-12-08.db .ai-router-sessions.db
```

Or use the export feature:
```
Analytics > [6] Export Report > [a] All sessions
```

**Q15: What if I run out of disk space?**

A: Free up space by:
1. Deleting old batch jobs: `Menu > [5] > [d] Delete old jobs`
2. Archiving old sessions: `Analytics > [4] > [a] Archive old`
3. Clearing exports: `rm -rf outputs/old/*`
4. Optimizing database: `python session_db_setup.py --vacuum`

### Troubleshooting Questions

**Q16: Model not loading / CUDA out of memory**

A: Try:
- Use smaller quantization (Q4_K_M instead of Q6_K)
- Reduce batch size in model config
- Close other GPU applications
- Use a smaller model

**Q17: Slow response times**

A: Check:
- GPU utilization: `nvidia-smi`
- Using WSL instead of Windows?
- Optimal parameters configured?
- Background processes consuming GPU?

Run benchmark: `python benchmark_features.py`

**Q18: Template variables not rendering**

A: Ensure:
- Variable names match exactly (case-sensitive)
- Variables have default values in metadata
- Using proper Jinja2 syntax: `{{variable}}` not `{variable}`

**Q19: Database locked error**

A: This means another process is using the database:
- Close any other AI Router instances
- Check for zombie processes: `ps aux | grep ai-router`
- Wait 30 seconds and retry

**Q20: Can't connect to cloud APIs**

A: Verify:
- API keys set correctly: `echo $OPENROUTER_API_KEY`
- Internet connection working
- API status: Check provider status pages
- Firewall not blocking requests

### Advanced Questions

**Q21: Can I run batch jobs in the background?**

A: Yes! Use the `-b` flag:
```bash
python ai-router.py --batch prompts.txt --model qwen25-14b --background

# Check progress:
python ai-router.py --batch-status

# View results:
python ai-router.py --batch-results [job_id]
```

**Q22: How do I integrate this into my own application?**

A: See DEVELOPER_GUIDE.md and API_REFERENCE.md for:
- Python API usage
- REST API server mode
- WebSocket streaming
- Custom integrations

**Q23: Can I use this for production applications?**

A: Yes, with considerations:
- Use cloud models for reliability
- Implement rate limiting
- Add error handling
- Monitor costs with analytics
- Set up automated backups

See DEVELOPER_GUIDE.md for production deployment tips.

**Q24: How do I contribute new features?**

A: See [CONTRIBUTING.md](README-ENHANCED.md#contributing-guidelines):
1. Fork repository
2. Create feature branch
3. Implement with tests
4. Submit pull request

**Q25: Where can I get help?**

A: Multiple channels:
1. Documentation (you're reading it!)
2. GitHub Issues for bugs
3. GitHub Discussions for questions
4. Discord community
5. Email support

---

## Video Tutorials

> **Coming Soon**: Video tutorials will be added to our YouTube channel

Planned tutorials:
1. Getting Started (10 min)
2. Advanced Session Management (15 min)
3. Creating Custom Templates (12 min)
4. Batch Processing Masterclass (20 min)
5. Analytics and Cost Optimization (18 min)

Subscribe at: [YouTube Channel](https://youtube.com/yourchannelhere)

---

## Quick Reference Card

Print this page for easy reference:

```
═══════════════════════════════════════════════════════════
AI ROUTER ENHANCED v2.0 - QUICK REFERENCE
═══════════════════════════════════════════════════════════

MAIN MENU
  [1] New Session    [6] Analytics
  [2] Resume         [7] Templates
  [3] Template       [8] Smart Select
  [4] Compare        [9] Settings
  [5] Batch          [0] Exit

SESSION COMMANDS
  /help      - Show commands
  /save      - Save & continue
  /exit      - Save & quit
  /tags      - Add tags
  /bookmark  - Bookmark session
  /context   - Add context
  /export    - Export conversation
  /switch    - Change model
  /clear     - Clear history
  /stats     - Show stats

BEST MODELS FOR:
  Coding     - qwen3-coder-30b (94% HumanEval)
  Math       - phi4-14b (85% AIME)
  Creative   - gemma3-27b (128K context)
  General    - qwen25-14b (balanced)
  Fast       - dolphin-8b (65 tok/sec)
  Research   - llama33-70b (70B params)

FILE LOCATIONS
  Database:  .ai-router-sessions.db
  Templates: prompt-templates/
  Exports:   outputs/
  Logs:      logs/

SUPPORT
  Docs:      D:\models\docs\
  Issues:    github.com/yourrepo/issues
  Discord:   discord.gg/yourserver
  Email:     support@yourproject.com
═══════════════════════════════════════════════════════════
```

---

**[⬆ Back to Top](#ai-router-enhanced-v20---user-guide)**

For more information, see:
- [README-ENHANCED.md](README-ENHANCED.md) - Project overview
- [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) - Technical documentation
- [FEATURE_DOCUMENTATION.md](FEATURE_DOCUMENTATION.md) - Detailed feature docs
- [API_REFERENCE.md](API_REFERENCE.md) - Complete API reference

Last updated: December 8, 2025
