# Repository Guidelines

## Project Structure & Module Organization
- Root PowerShell utilities manage local GGUF models: `organize-models.ps1` builds the catalog and `run-model.ps1` / `run-in-wsl.ps1` execute models.
- Models live under `organized/` (hardlinks/copies normalized for llama.cpp), GPU-specific drops under `rtx4060ti-16gb/`, and raw Ollama cache under `gguf/`.
- `model-registry.json` is the single source of truth for model metadata (indexes, paths, quantization, best-for notes). Keep paths aligned to `D:\models\...` and WSL mounts (`/mnt/d/models/...`).

## Build, Test, and Development Commands
- Refresh registry and organized links: `pwsh .\organize-models.ps1`.
- List models and metadata: `pwsh .\run-model.ps1 -ListModels` (PowerShell wrapper) or `pwsh .\run-in-wsl.ps1 -ListModels` (WSL-first).
- Run a prompt via llama.cpp in WSL: `pwsh .\run-model.ps1 -ModelName "Llama" -Prompt "Hello" -ContextSize 4096 -MaxTokens 512`.
- Run directly in WSL for speed/tuning: `pwsh .\run-in-wsl.ps1 -ModelName "Qwen" -Interactive -TopK 40 -TopP 0.95`.
- If llama.cpp is missing, `run-model.ps1` bootstraps it inside WSL; allow the script to complete before retrying.

## Coding Style & Naming Conventions
- PowerShell with 4-space indentation; use PascalCase for parameters/variables, and descriptive names (`$ModelRegistry`, `$ContextSize`).
- Emit user-facing output with `Write-Host` and consistent emoji/color cues already used in scripts.
- JSON keys follow lower_snake_case; keep registry entries minimal and consistent (`size_gb`, `path_wsl`, `best_for`).
- Keep Windows and WSL paths in sync; prefer hardlinks in `organized/` to avoid redundant copies.

## Testing Guidelines
- After edits, run `organize-models.ps1` and confirm it regenerates `model-registry.json` without errors and lists expected counts.
- Validate runners by listing models, then executing a small prompt per GPU target:  
  - `pwsh .\run-model.ps1 -ModelName "Dolphin" -Prompt "ping"`  
  - `pwsh .\run-in-wsl.ps1 -ModelName "Qwen" -Prompt "ping"`  
- Ensure WSL can see model paths (`wsl bash -c "test -f /mnt/d/models/organized/<file>.gguf"`).

## Commit & Pull Request Guidelines
- Use imperative, scoped subjects (e.g., `Update registry paths`, `Improve WSL runner defaults`) and keep commits small.
- Document what changed, why, and which commands you ran for validation; include hardware context if relevant (3090 vs 4060 Ti).
- Avoid committing model binaries; only track registry updates, scripts, and lightweight docs. Provide sample outputs or screenshots only when they clarify a change.

## Security & Configuration Tips
- Verify large-file operations (hardlinks vs copies) before moving/deleting models to prevent accidental data loss.
- Do not embed API keys or external endpoints; scripts assume local execution with no network access beyond git/llama.cpp cloning when approved.
