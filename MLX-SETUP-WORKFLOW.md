# MLX Setup Workflow Diagram

## Installation Flow

```
┌─────────────────────────────────────────────────────────────┐
│                  ./setup-mlx-macbook.sh                     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: Pre-flight Checks                                  │
│  ──────────────────────────────────────────────────────────│
│  ✓ Verify macOS                                            │
│  ✓ Check Apple Silicon (M1/M2/M3/M4)                       │
│  ✓ Validate Python 3.9+                                    │
│  ✓ Check disk space (10GB+)                                │
│  ✓ Check RAM (16GB+ recommended)                           │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 2: Virtual Environment Setup                          │
│  ──────────────────────────────────────────────────────────│
│  ✓ Create ~/venv-mlx                                       │
│  ✓ Activate environment                                     │
│  ✓ Upgrade pip to latest                                   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 3: Package Installation                               │
│  ──────────────────────────────────────────────────────────│
│  ✓ Install mlx (core framework)                            │
│  ✓ Install mlx-lm (language models)                        │
│  ✓ Install numpy, transformers                             │
│  ✓ Install huggingface-hub                                 │
│  ✓ Install sentencepiece, tiktoken                         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 4: Directory Structure                                │
│  ──────────────────────────────────────────────────────────│
│  ✓ Create ~/workspace/                                     │
│  ✓ Create ~/workspace/mlx/ (models)                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 5: Shell Configuration                                │
│  ──────────────────────────────────────────────────────────│
│  ✓ Backup existing .zshrc/.bashrc                          │
│  ✓ Add environment variables                               │
│  ✓ Add aliases (mlx-activate, mlx-status, etc.)            │
│  ✓ Add helper functions (mlx-models, mlx-validate)         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 6: Validation                                         │
│  ──────────────────────────────────────────────────────────│
│  ✓ Run setup_mlx_environment.py --validate                 │
│  ✓ Test MLX imports                                        │
│  ✓ Verify Metal GPU support                                │
│  ✓ Check all dependencies                                  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  ✓ Installation Complete!                                   │
└─────────────────────────────────────────────────────────────┘
```

## Validation Flow

```
┌─────────────────────────────────────────────────────────────┐
│     python3 setup_mlx_environment.py --validate             │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
        ▼                                       ▼
┌──────────────────┐                  ┌──────────────────┐
│ System Info      │                  │ MLX Core         │
│ ───────────────  │                  │ ───────────────  │
│ • OS & Arch      │                  │ • Import test    │
│ • Python version │                  │ • Version check  │
│ • RAM            │                  │ • Array ops      │
└──────────────────┘                  └──────────────────┘
        │                                       │
        └───────────────────┬───────────────────┘
                            ▼
        ┌───────────────────┴───────────────────┐
        │                                       │
        ▼                                       ▼
┌──────────────────┐                  ┌──────────────────┐
│ Metal GPU        │                  │ mlx-lm           │
│ ───────────────  │                  │ ───────────────  │
│ • Device detect  │                  │ • Import test    │
│ • GPU compute    │                  │ • API check      │
└──────────────────┘                  └──────────────────┘
        │                                       │
        └───────────────────┬───────────────────┘
                            ▼
                  ┌──────────────────┐
                  │ Dependencies     │
                  │ ───────────────  │
                  │ • NumPy          │
                  │ • Transformers   │
                  │ • HF Hub         │
                  └──────────────────┘
                            │
                            ▼
                  ┌──────────────────┐
                  │ Summary Report   │
                  │ ───────────────  │
                  │ Checks: X/Y      │
                  │ Errors: N        │
                  │ Warnings: M      │
                  └──────────────────┘
```

## Usage Flow (Daily)

```
┌─────────────────────────────────────────────────────────────┐
│                   Start New Terminal                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                  ┌──────────────────┐
                  │  mlx-activate    │
                  └──────────────────┘
                            │
                            ▼
        ┌───────────────────┴───────────────────┐
        │                                       │
        ▼                                       ▼
┌──────────────────┐                  ┌──────────────────┐
│ Check Status     │                  │ Start Coding     │
│                  │                  │                  │
│ mlx-status       │                  │ mlx-chat-qwen7b  │
└──────────────────┘                  └──────────────────┘
        │                                       │
        │                                       ▼
        │                             ┌──────────────────┐
        │                             │ Interactive Chat │
        │                             │                  │
        │                             │ • Ask questions  │
        │                             │ • Get code       │
        │                             │ • Debug issues   │
        │                             └──────────────────┘
        ▼
┌──────────────────┐
│ Quick Generation │
│                  │
│ mlx-qwen7b       │
│ --prompt "..."   │
└──────────────────┘
```

## File Structure After Installation

```
~/
├── venv-mlx/                     # Python virtual environment
│   ├── bin/
│   │   ├── python3              # Python interpreter
│   │   ├── pip                  # Package installer
│   │   └── mlx_lm               # MLX CLI tools
│   ├── lib/
│   │   └── python3.x/
│   │       └── site-packages/
│   │           ├── mlx/         # MLX package
│   │           ├── mlx_lm/      # MLX language models
│   │           ├── numpy/       # NumPy
│   │           └── transformers/ # Transformers
│   └── ...
│
├── workspace/
│   ├── llm-optimization-framework/  # This repo
│   │   ├── setup-mlx-macbook.sh    # Setup script
│   │   ├── setup_mlx_environment.py # Validation script
│   │   ├── ai-router-mlx.py        # AI Router
│   │   └── ...
│   └── mlx/                         # Models directory
│       ├── qwen25-coder-7b/
│       ├── qwen25-coder-32b/
│       ├── deepseek-r1-8b/
│       └── phi4-14b/
│
└── .zshrc (or .bashrc)              # Shell config with aliases
```

## Component Relationships

```
┌─────────────────────────────────────────────────────────────┐
│                      MacBook Hardware                       │
│  ┌────────────────────────────────────────────────────────┐│
│  │  Apple Silicon (M1/M2/M3/M4) + Metal GPU              ││
│  └────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      macOS System                           │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Python Virtual Environment                 │
│                       ~/venv-mlx                            │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
        ▼                                       ▼
┌──────────────────┐                  ┌──────────────────┐
│  MLX Framework   │                  │  mlx-lm          │
│                  │◄─────────────────┤                  │
│  • Core ops      │                  │  • Model loading │
│  • Metal backend │                  │  • Inference     │
│  • Arrays        │                  │  • Generation    │
└──────────────────┘                  └──────────────────┘
        │                                       │
        └───────────────────┬───────────────────┘
                            ▼
        ┌───────────────────────────────────────┐
        │                                       │
        ▼                                       ▼
┌──────────────────┐                  ┌──────────────────┐
│  Local Models    │                  │  AI Router       │
│                  │                  │                  │
│  ~/workspace/mlx │                  │  ai-router-mlx.py│
└──────────────────┘                  └──────────────────┘
```

## Error Handling Flow

```
                    ┌──────────────┐
                    │ Error Occurs │
                    └──────────────┘
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
        ▼                                       ▼
┌──────────────────┐                  ┌──────────────────┐
│ Pre-flight Error │                  │ Installation     │
│                  │                  │ Error            │
│ • System check   │                  │                  │
│ • Display issue  │                  │ • Package fail   │
│ • Suggest fix    │                  │ • Retry logic    │
│ • Exit cleanly   │                  │ • Show error     │
└──────────────────┘                  └──────────────────┘
        │                                       │
        └───────────────────┬───────────────────┘
                            ▼
                  ┌──────────────────┐
                  │ User Action      │
                  │                  │
                  │ • Read message   │
                  │ • Fix issue      │
                  │ • Re-run script  │
                  └──────────────────┘
                            │
                            ▼
                  ┌──────────────────┐
                  │ Success!         │
                  └──────────────────┘
```

## Performance Comparison

```
                    Ollama vs MLX Performance

    100 │
        │                                    ┌─── MLX (80 tok/sec)
     80 │                               ┌────┘
        │                          ┌────┘
     60 │                     ┌────┘
        │                ┌────┘
     40 │           ┌────┘
        │      ┌────┘           ┌─── Ollama (30 tok/sec)
     20 │ ─────┘            ┌───┘
        │              ┌────┘
      0 └──────────────┴──────────────────────────────
        Load    First   Gen 1K   Gen 2K   Gen 4K
               Token   tokens   tokens   tokens

        MLX:    3-4x faster across all metrics
        Memory: 2-3GB (MLX) vs 4-6GB (Ollama)
```

## Quick Reference

### Installation
```bash
./setup-mlx-macbook.sh
```

### Validation
```bash
python3 setup_mlx_environment.py --validate
```

### Daily Use
```bash
mlx-activate
mlx-chat-qwen7b
```

### Troubleshooting
```bash
mlx-status
mlx-validate
```

## Documentation Map

- **This File**: Visual workflow and diagrams
- **MLX-QUICK-START.md**: One-page reference
- **MLX-SETUP-README.md**: Complete documentation
- **MACBOOK-MLX-SETUP-GUIDE.md**: Manual setup guide
- **setup-mlx-macbook.sh**: Main installation script
- **setup_mlx_environment.py**: Validation script
