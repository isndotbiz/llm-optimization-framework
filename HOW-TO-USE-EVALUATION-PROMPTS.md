# How to Use the Code Evaluation Prompts

This guide explains how to use the evaluation prompts with different LLMs to analyze your AI Router code.

## Quick Start

You have three prompt templates:
1. **PROMPT-FOR-CODEX-GEMINI.txt** - Contains 3 versions (Quick, Comprehensive, Minimal)
2. **CODE-QUALITY-EVALUATION-PROMPT.md** - Detailed structured analysis
3. **[This file]** - Usage guide

## Step-by-Step Usage

### Step 1: Choose Your Version

**Use QUICK VERSION if:**
- You want results in 2-5 minutes
- You have limited LLM budget/tokens
- You want the top issues and tools only
- Quick decision-making is priority

**Use COMPREHENSIVE VERSION if:**
- You want detailed analysis
- You're building a long-term quality strategy
- You want specific implementation guides
- You need justification for tool selection
- You're presenting to stakeholders

**Use MINIMAL VERSION if:**
- You're in a hurry
- You want just the essential takeaways
- You need a quick team sync
- You're exploring feasibility

### Step 2: Append Your Code

Each prompt template says to paste your code. Here's how:

**Option A: Direct Copy-Paste**
```
1. Copy the prompt template
2. Go to your LLM (Codex, Gemini, Claude, ChatGPT, etc.)
3. Paste the prompt
4. Paste each Python file content below the "CODE INPUT" section
5. Submit
```

**Option B: Code Summary (for token efficiency)**
Instead of full file content, paste just:
```
File: ai-router.py
Lines: 1200+
Key Classes: Colors, ModelDatabase, AIRouter
Key Methods: run_model(), interactive_mode(), list_models()
Dependencies: subprocess, pathlib, platform, logging_config
External Calls: subprocess.run(), file I/O, user input
Special Features: CLI with model selection, color output, system detection
Potential Issues: subprocess calls, file paths, exception handling

[Repeat for other 4 files]
```

This is more token-efficient while still providing context.

### Step 3: Adjust for Your LLM

Different LLMs work better with slight adjustments:

#### For OpenAI Codex / ChatGPT:
- Include the COMPREHENSIVE version
- Codex/ChatGPT are very thorough
- They'll provide detailed tool configurations
- They like structured output
- Token limit: 4K (GPT-3.5) to 128K (GPT-4 turbo)

```
Use: COMPREHENSIVE VERSION
Add: "Format your response as a structured report with clear sections"
```

#### For Google Gemini:
- Include the QUICK VERSION initially
- Gemini handles long context well
- Very good at tool recommendations
- Ask for specific tool install commands
- Token limit: Up to 2M tokens

```
Use: QUICK VERSION or COMPREHENSIVE VERSION
Add: "Provide exact 'pip install' commands for each tool"
```

#### For Claude (Anthropic):
- Include the COMPREHENSIVE VERSION
- Claude excels at detailed analysis
- Very good at security issues
- Excellent phased implementations
- Token limit: 100K (Claude 3 Haiku) to 200K (Claude 3 Opus)

```
Use: COMPREHENSIVE VERSION
Add: "Include specific code examples showing each issue"
```

#### For Llama 2 / Open Source LLMs:
- Use the MINIMAL VERSION
- May need simpler formatting
- Better with explicit structure
- May need examples for each issue type
- Token limit: Varies (7B, 13B, 70B variants)

```
Use: MINIMAL VERSION
Add: "Provide exactly 5 critical issues with code examples"
```

#### For Copilot / GitHub Models:
- Use QUICK VERSION
- GitHub models understand GitHub Actions well
- Good for CI/CD configuration recommendations
- Token limit: Typically 4K-100K depending on tier

```
Use: QUICK VERSION
Add: "Include GitHub Actions workflow examples"
```

## Using with Multiple LLMs (Cross-Validation)

For best results, use multiple LLMs and compare:

```
LLM 1 (Codex): Run COMPREHENSIVE VERSION -> Get detailed analysis
LLM 2 (Gemini): Run QUICK VERSION -> Get concise tool recommendations
LLM 3 (Claude): Run COMPREHENSIVE VERSION -> Get security-focused analysis

Then:
- Compare tool recommendations
- Look for consensus on top 5 tools
- Note disagreements and why
- Use differences to make informed decisions
```

## Modifying Prompts for Specific Needs

### If you want SECURITY FOCUS:
Add to any prompt:
```
PRIORITY FOCUS: Security vulnerabilities (OWASP Top 10)
Weight security issues 10x in severity calculation.
For command injection risks in subprocess calls, provide:
1. Exact vulnerable code
2. Exploit scenario
3. Fixed code with subprocess.run(..., check=True, shell=False)
```

### If you want PERFORMANCE FOCUS:
Add to any prompt:
```
PRIORITY FOCUS: Performance and optimization
Analyze for:
- N+1 query patterns
- Inefficient loops
- Memory bloat
- Unnecessary subprocess calls
- String concatenation inefficiencies
```

### If you want TYPE SAFETY FOCUS:
Add to any prompt:
```
PRIORITY FOCUS: Type safety and type hints
Current type hint coverage estimate: [X]%
Target type hint coverage: 100%
Recommend tools for:
- Static type checking (mypy)
- Type hint generation tools
- Runtime type checking options
```

### If you want TESTABILITY FOCUS:
Add to any prompt:
```
PRIORITY FOCUS: Test coverage and testability
For each identified issue, also provide:
- Unit test that would catch this issue
- Mock structure needed
- Test fixture requirements
- Pytest configuration needed
```

## Expected Outputs and What They Mean

### Good Sign - You'll See:
- OK: 5-20 specific issues with line numbers
- OK: 8-12 tool recommendations with install commands
- OK: Phase 1 that takes 1-2 days
- OK: Specific GitHub Actions workflows
- OK: Concrete code examples of both problems and fixes

### Red Flag - Watch Out For:
- Avoid: Vague recommendations ("use better error handling")
- Avoid: Tools without install commands
- Avoid: Generic security advice
- Avoid: Overly complex roadmap (Phase 1 should be <2 days)
- Avoid: No code examples

## Post-Analysis: Acting on Results

### Immediately Do:
1. Create a `.pre-commit-config.yaml` with Phase 1 tools
2. Run all Phase 1 tools locally to generate baseline report
3. Create GitHub issue for each critical security issue
4. Run Phase 1 tools in CI/CD pipeline

### This Sprint:
1. Install Phase 1 tools on all developer machines
2. Fix critical issues identified
3. Set up GitHub Actions for automated checks

### Next Sprint:
1. Install Phase 2 tools
2. Fix high-priority issues
3. Integrate Phase 2 tools into CI/CD

## Example: Running with Gemini

```
1. Go to https://gemini.google.com (or your API)

2. Paste the COMPREHENSIVE VERSION prompt

3. Add your code files below "CODE INPUT"

4. Modify the prompt to add:

"I'm using these 5 Python files in production for an AI Router.
Priority order for me:
1. Security (prevent vulnerabilities)
2. Type safety (catch bugs early)
3. Performance (optimize execution)
4. Maintainability (improve code quality)

For each recommended tool, I need:
- Exact pip install command
- Configuration file example (.toml or .yaml)
- How to integrate with GitHub Actions
- Expected time to set up (in hours)"

5. Submit and wait for response

6. Response should include:
   - 8-12 tools with exact install commands
   - Phased implementation (3-4 phases, each 1-3 days)
   - Top 5-10 specific code issues with line numbers
   - GitHub Actions workflow example
   - Pre-commit hook configuration
```

## Troubleshooting

### If LLM Returns Generic Advice:
-> Add: "Provide 10 specific code examples from the provided files"

### If LLM Misses Security Issues:
-> Try Claude specifically: "Analyze for command injection in subprocess.run() calls"

### If Tool Recommendations Seem Outdated:
-> Add: "As of 2025, what are the current best tools for Python code quality?"

### If Output is Too Long:
-> Use MINIMAL VERSION or ask LLM to "Provide only the top 5 critical issues"

### If Output is Too Short:
-> Use COMPREHENSIVE VERSION or ask for "More detail on each recommended tool"

## Comparing Results Across LLMs

Create a comparison spreadsheet:

| Tool | Gemini | Codex | Claude | Recommended |
|------|--------|-------|--------|-------------|
| mypy | Yes (8/10) | Yes (9/10) | Yes (9/10) | YES - consensus |
| pylint | Yes (7/10) | Yes (8/10) | No | YES - 2/3 recommend |
| bandit | Yes (9/10) | No | Yes (10/10) | YES - security focus |
| pytest | No | Yes (7/10) | Yes (8/10) | YES - testing |

**Recommendation**: If 2+ LLMs recommend it, include it in your Phase 1.

## Final Checklist Before Running

- [ ] Choose one prompt version (or multiple for comparison)
- [ ] Select your LLM(s)
- [ ] Have all 5 Python files ready
- [ ] Decide if you want full code or code summary
- [ ] Add any specific focus areas (security, performance, etc.)
- [ ] Set expectations for output (detail level, format, length)
- [ ] Have GitHub Actions YAML template ready to receive recommendations
- [ ] Plan next steps before running analysis

## Next Steps After Analysis

1. **Week 1**: Install Phase 1 tools, run on codebase, fix critical issues
2. **Week 2**: Install Phase 2 tools, integrate with CI/CD
3. **Week 3+**: Install Phase 3 tools, build comprehensive quality dashboard

Estimated total time to full implementation: 2-4 weeks depending on codebase size and team size.
