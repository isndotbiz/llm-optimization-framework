#!/usr/bin/env python3
"""Validate all model paths exist and are accessible"""

import sys
from pathlib import Path

# Import the ModelDatabase
sys.path.insert(0, str(Path(__file__).parent))

# Define models directly (copy from ai-router.py)
RTX3090_MODELS = {
    "qwen3-coder-30b": {
        "name": "Qwen3 Coder 30B Q4_K_M",
        "path": "/mnt/d/models/organized/Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf",
        "framework": "llama.cpp"
    },
    "phi4-14b": {
        "name": "Phi-4 Reasoning Plus 14B Q6_K",
        "path": "/mnt/d/models/organized/microsoft_Phi-4-reasoning-plus-Q6_K.gguf",
        "framework": "llama.cpp"
    },
    "gemma3-27b": {
        "name": "Gemma 3 27B Q2_K (Abliterated)",
        "path": "/mnt/d/models/organized/mlabonne_gemma-3-27b-it-abliterated-Q2_K.gguf",
        "framework": "llama.cpp"
    },
    "ministral-3-14b": {
        "name": "Ministral-3 14B Reasoning Q5_K_M",
        "path": "/mnt/d/models/organized/Ministral-3-14B-Reasoning-2512-Q5_K_M.gguf",
        "framework": "llama.cpp"
    },
    "deepseek-r1-14b": {
        "name": "DeepSeek R1 Distill Qwen 14B Q5_K_M",
        "path": "/mnt/d/models/organized/DeepSeek-R1-Distill-Qwen-14B-Q5_K_M.gguf",
        "framework": "llama.cpp"
    },
    "llama33-70b": {
        "name": "Llama 3.3 70B Instruct IQ2_S (Abliterated)",
        "path": "/mnt/d/models/organized/Llama-3.3-70B-Instruct-abliterated-IQ2_S.gguf",
        "framework": "llama.cpp"
    },
    "dolphin-llama31-8b": {
        "name": "Dolphin 3.0 Llama 3.1 8B Q6_K",
        "path": "/mnt/d/models/organized/Dolphin3.0-Llama3.1-8B-Q6_K.gguf",
        "framework": "llama.cpp"
    },
    "dolphin-mistral-24b": {
        "name": "Dolphin Mistral 24B Venice Q4_K_M",
        "path": "/mnt/d/models/organized/cognitivecomputations_Dolphin-Mistral-24B-Venice-Edition-Q4_K_M.gguf",
        "framework": "llama.cpp"
    },
    "wizard-vicuna-13b": {
        "name": "Wizard Vicuna 13B Uncensored Q4_0",
        "path": "/mnt/d/models/organized/Wizard-Vicuna-13B-Uncensored-Q4_0.gguf",
        "framework": "llama.cpp"
    }
}

def validate_models():
    """Validate all model paths exist"""
    print("=" * 80)
    print("MODEL PATH VALIDATION REPORT")
    print("=" * 80)
    print()

    missing_models = []
    found_models = []

    for model_id, model_data in RTX3090_MODELS.items():
        wsl_path = model_data["path"]
        # Convert WSL path to Windows path
        windows_path = wsl_path.replace("/mnt/d/", "D:/")

        exists = Path(windows_path).exists()
        status = "[OK]    " if exists else "[MISSING]"

        print(f"{status} {model_id}")
        print(f"    Name: {model_data['name']}")
        print(f"    WSL Path: {wsl_path}")
        print(f"    Windows Path: {windows_path}")
        print()

        if exists:
            found_models.append(model_id)
        else:
            missing_models.append((model_id, windows_path))

    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total Models: {len(RTX3090_MODELS)}")
    print(f"Found: {len(found_models)}")
    print(f"Missing: {len(missing_models)}")
    print()

    if missing_models:
        print("MISSING MODELS:")
        for model_id, path in missing_models:
            print(f"  - {model_id}: {path}")
        print()
        print("ACTION REQUIRED: These model files need to be added or paths updated in ai-router.py")
        return False
    else:
        print("[OK] All model files found!")
        return True

if __name__ == "__main__":
    success = validate_models()
    sys.exit(0 if success else 1)
