# Repository Guidelines

## Project Structure & Module Organization
- `ai-router.py` and `ai-router-enhanced.py`: CLI entry points; use the enhanced version for full project/bot/workflow features, or the basic router for minimal runs.
- `utils/`: core modules (`workflow_engine`, `session_manager`, `template_manager`, `batch_processor`, `analytics_dashboard`, `model_selector`, etc.). Import directly from repo root.
- `providers/`: adapters for OpenAI/OpenRouter/Claude/Ollama/llama.cpp with optional deps in `providers/requirements.txt`; MCP helpers live in `mcp_tools/`.
- Assets: `bots/` (agent presets), `workflows/` (YAML pipelines), `prompt-templates/` and `context-templates/` (prompt scaffolds), `prompt_templates/` (test/sample vars). Use clear, hyphenated filenames.
- Tests: active suites in `tests/`; historical reference in `archive/old-tests/`. Runtime artifacts (`logs/`, `outputs/`, `.ai-router-*.db`, model files in `organized/`/`gguf/`) should stay untracked.

## Build, Run, and Development Commands
```bash
python -m venv venv && source venv/bin/activate
pip install -r providers/requirements.txt -r mcp_tools/requirements.txt  # add extras as needed
python ai-router-enhanced.py    # full CLI
python ai-router.py             # legacy/basic
./start-router.sh               # WSL shortcut
python -m unittest discover -s tests -p "test_*.py"      # core tests
python -m unittest mcp_tools.test_mcp_server             # MCP tools
```
Keep your working directory at the repo root so imports resolve (`utils` sits alongside entry points).

## Coding Style & Naming Conventions
- PEP8 with 4-space indents; snake_case for functions/variables, PascalCase for classes, UPPER_SNAKE for constants.
- Add type hints and concise docstrings (see `utils/workflow_engine.py`, `utils/session_manager.py` for patterns).
- YAML/JSON ids should be lowercase with hyphens or underscores; align keys with the workflow engine schema (`name`, `steps`, `config`, `variables`, `depends_on`).
- Prefer `logging_config.setup_logging` over ad-hoc prints; avoid logging secrets or full prompts.

## Testing Guidelines
- Use `unittest` with `test_*.py` filenames and `Test*` classes; isolate state with temp dirs/SQLite files and clean up in `tearDown`.
- Mock model execution (see workflow tests) instead of calling real models; never rely on files in `organized/` or `gguf/`.
- When adding templates/workflows, include a load/execute test to verify YAML parsing and variable substitution.

## Commit & Pull Request Guidelines
- Commit messages use short imperative summaries, sentence case, no trailing period (e.g., `Add AI Router Enhanced v2.0 and fix Unicode issues in both versions`).
- PRs should include purpose, key files touched, test commands run, and any new configs/templates added. Attach logs or screenshots only when they clarify CLI behavior.
- Keep docs in sync (`DEVELOPER_GUIDE.md`, `workflow_implementation_guide.md`, `USER_GUIDE.md`), and exclude large models, DBs, and log/output artifacts from commits.
