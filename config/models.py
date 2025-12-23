"""
Central Model Configuration Module

This module contains the ModelDatabase class that serves as the single source
of truth for all AI model configurations across the AI Router ecosystem.

This is a centralized configuration to eliminate duplication across multiple
router implementations (ai-router.py, ai-router-enhanced.py, ai-router-mlx.py).

All model definitions, parameters, paths, and system prompts are maintained
here and imported by all router implementations.

Author: AI Router System
Date: 2025-12-22
Version: 1.0
"""

import platform


class ModelDatabase:
    """Comprehensive model database with 2025 research-optimized settings

    This is the single source of truth for all model configurations.
    Contains settings for RTX 3090 (GGUF/llama.cpp) and M4 MacBook (MLX) variants.

    All three routers import this class:
    - ai-router.py (primary CLI)
    - ai-router-enhanced.py (advanced features)
    - ai-router-mlx.py (MLX-specific - may have its own specialized classes)
    """

    # RTX 3090 Models (WSL)
    RTX3090_MODELS = {
        "qwen3-coder-30b": {
            "name": "Qwen3 Coder 30B Q4_K_M",
            "path": (
                "/mnt/d/models/organized/"
                "Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf"
            ),
            "size": "18GB",
            "speed": "25-35 tok/sec",
            "use_case": (
                "Advanced coding, code review, architecture design"
            ),
            "temperature": 0.7,
            "top_p": 0.8,
            "top_k": 20,
            "context": 32768,
            "special_flags": ["--jinja"],
            "system_prompt": "system-prompt-qwen3-coder-30b.txt",
            "notes": (
                "CRITICAL: Never use temp 0 (causes endless loops). "
                "Use enable_thinking for reasoning."
            ),
            "framework": "llama.cpp"
        },
        "phi4-14b": {
            "name": "Phi-4 Reasoning Plus 14B Q6_K",
            "path": (
                "/mnt/d/models/organized/"
                "microsoft_Phi-4-reasoning-plus-Q6_K.gguf"
            ),
            "size": "12GB",
            "speed": "35-55 tok/sec",
            "use_case": "Math, reasoning, STEM, logical analysis",
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "context": 16384,
            "special_flags": ["--jinja"],
            "system_prompt": "system-prompt-phi4-14b.txt",
            "notes": (
                "CRITICAL: Requires --jinja flag. "
                "DO NOT use 'think step-by-step' prompts."
            ),
            "framework": "llama.cpp"
        },
        "gemma3-27b": {
            "name": "Gemma 3 27B Q2_K (Abliterated)",
            "path": (
                "/mnt/d/models/organized/"
                "mlabonne_gemma-3-27b-it-abliterated-Q2_K.gguf"
            ),
            "size": "10GB",
            "speed": "25-40 tok/sec",
            "use_case": "Uncensored chat, creative writing, research",
            "temperature": 0.9,
            "top_p": 0.9,
            "top_k": 40,
            "context": 128000,
            "special_flags": [],
            "system_prompt": None,
            "notes": (
                "NO system prompt support. 128K context. "
                "Uncensored/abliterated variant."
            ),
            "framework": "llama.cpp"
        },
        "ministral-3-14b": {
            "name": "Ministral-3 14B Reasoning Q5_K_M",
            "path": (
                "/mnt/d/models/organized/"
                "Ministral-3-14B-Reasoning-2512-Q5_K_M.gguf"
            ),
            "size": "9GB",
            "speed": "35-50 tok/sec",
            "use_case": "Complex reasoning, problem solving, analysis",
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "context": 262144,
            "special_flags": [],
            "system_prompt": "system-prompt-ministral-3-14b.txt",
            "notes": (
                "256K context window. "
                "Excellent for long-context reasoning."
            ),
            "framework": "llama.cpp"
        },
        "deepseek-r1-14b": {
            "name": "DeepSeek R1 Distill Qwen 14B Q5_K_M",
            "path": (
                "/mnt/d/models/organized/"
                "DeepSeek-R1-Distill-Qwen-14B-Q5_K_M.gguf"
            ),
            "size": "10GB",
            "speed": "30-50 tok/sec",
            "use_case": "Advanced reasoning, research, complex analysis",
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "context": 32768,
            "special_flags": [],
            "system_prompt": "system-prompt-deepseek-r1.txt",
            "notes": (
                "DeepSeek R1 distilled to Qwen. "
                "Excellent reasoning capabilities."
            ),
            "framework": "llama.cpp"
        },
        "llama33-70b": {
            "name": "Llama 3.3 70B Instruct IQ2_S (Abliterated)",
            "path": (
                "/mnt/d/models/organized/"
                "Llama-3.3-70B-Instruct-abliterated-IQ2_S.gguf"
            ),
            "size": "21GB",
            "speed": "15-25 tok/sec",
            "use_case": "Large-scale reasoning, research, uncensored tasks",
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "context": 131072,
            "special_flags": [],
            "system_prompt": "system-prompt-llama33-70b.txt",
            "notes": (
                "Largest model available. "
                "Excellent for complex tasks. Uncensored."
            ),
            "framework": "llama.cpp"
        },
        "dolphin-llama31-8b": {
            "name": "Dolphin 3.0 Llama 3.1 8B Q6_K",
            "path": "/mnt/d/models/organized/Dolphin3.0-Llama3.1-8B-Q6_K.gguf",
            "size": "6GB",
            "speed": "45-65 tok/sec",
            "use_case": (
                "Fast general tasks, uncensored chat, quick assistance"
            ),
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "context": 32768,
            "special_flags": [],
            "system_prompt": "system-prompt-dolphin-8b.txt",
            "notes": "Fastest model. Uncensored variant of Llama 3.1 8B.",
            "framework": "llama.cpp"
        },
        "dolphin-mistral-24b": {
            "name": "Dolphin Mistral 24B Venice Q4_K_M",
            "path": (
                "/mnt/d/models/organized/"
                "cognitivecomputations_Dolphin-Mistral-24B-Venice-"
                "Edition-Q4_K_M.gguf"
            ),
            "size": "14GB",
            "speed": "25-40 tok/sec",
            "use_case": "Uncensored chat, creative tasks, roleplay",
            "temperature": 0.8,
            "top_p": 0.9,
            "top_k": 40,
            "context": 32768,
            "special_flags": [],
            "system_prompt": None,
            "notes": (
                "Venice Edition: Completely uncensored. "
                "No system prompt support."
            ),
            "framework": "llama.cpp"
        },
        "wizard-vicuna-13b": {
            "name": "Wizard Vicuna 13B Uncensored Q4_0",
            "path": "/mnt/d/models/organized/Wizard-Vicuna-13B-Uncensored-Q4_0.gguf",  # noqa: E501
            "size": "7GB",
            "speed": "35-50 tok/sec",
            "use_case": "General uncensored chat, creative writing",
            "temperature": 0.8,
            "top_p": 0.9,
            "top_k": 40,
            "context": 8192,
            "special_flags": [],
            "system_prompt": "system-prompt-wizard-vicuna.txt",
            "notes": "Classic uncensored model. Smaller context window.",
            "framework": "llama.cpp"
        }
    }

    # MacBook M4 Pro Models (MLX)
    M4_MODELS = {
        "qwen25-14b-mlx": {
            "name": "Qwen2.5 14B Instruct Q5_K_M (MLX)",
            "path": "~/models/qwen25-14b",
            "size": "11GB",
            "speed": "50-70 tok/sec",
            "use_case": "General purpose, research, chat",
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "context": 32768,
            "special_flags": [],
            "system_prompt": "system-prompt-qwen25-14b.txt",
            "notes": (
                "Best daily driver for M4. "
                "Use MLX for 2-3x speedup vs llama.cpp."
            ),
            "framework": "mlx"
        },
        "qwen25-coder-14b-mlx": {
            "name": "Qwen2.5 Coder 14B Q4_K_M (MLX)",
            "path": "~/models/qwen25-coder-14b",
            "size": "8GB",
            "speed": "50-75 tok/sec",
            "use_case": "Coding, debugging, technical tasks",
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "context": 32768,
            "special_flags": [],
            "system_prompt": "system-prompt-qwen25-coder-14b.txt",
            "notes": "Best coding model for M4.",
            "framework": "mlx"
        },
        "phi4-14b-mlx": {
            "name": "Phi-4 14B Q6_K (MLX)",
            "path": "~/models/phi4-14b",
            "size": "12GB",
            "speed": "60-75 tok/sec",
            "use_case": "Math, reasoning, STEM tasks",
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "context": 16384,
            "special_flags": [],
            "system_prompt": "system-prompt-phi4-14b.txt",
            "notes": "Excellent for reasoning on M4.",
            "framework": "mlx"
        },
        "gemma3-9b-mlx": {
            "name": "Gemma-3 9B Q6_K (MLX)",
            "path": "~/models/gemma3-9b",
            "size": "8GB",
            "speed": "85-110 tok/sec",
            "use_case": "Fast responses, chat, general queries",
            "temperature": 0.9,
            "top_p": 0.9,
            "top_k": 40,
            "context": 128000,
            "special_flags": [],
            "system_prompt": None,
            "notes": "Speed champion on M4. NO system prompt support.",
            "framework": "mlx"
        }
    }

    @classmethod
    def get_platform_models(cls):
        """Return models appropriate for current platform"""
        system = platform.system()
        if system == "Darwin":  # macOS
            return cls.M4_MODELS
        else:  # Windows/WSL - RTX 3090
            return cls.RTX3090_MODELS

    @classmethod
    def get_all_models(cls):
        """Return all available models"""
        all_models = {}
        all_models.update(cls.RTX3090_MODELS)
        all_models.update(cls.M4_MODELS)
        return all_models
