#!/usr/bin/env python3
"""Test script to validate llama.cpp model loading in WSL"""

import subprocess
import os
from pathlib import Path

def is_wsl():
    """Detect if running in WSL"""
    try:
        with open('/proc/version', 'r') as f:
            return 'microsoft' in f.read().lower()
    except Exception:
        return False

def test_model_loading():
    """Test if we can find and validate models"""
    print("Testing AI Router Model Loading\n")
    print(f"Running in WSL: {is_wsl()}")
    print(f"Platform: {os.__name__}\n")

    # Test paths
    model_paths = [
        "/mnt/d/models/organized/Dolphin3.0-Llama3.1-8B-Q6_K.gguf",
        "/mnt/d/models/organized/Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf"
    ]

    llama_cpp_paths = [
        "/mnt/d/workspace/llama.cpp/build/bin/llama-cli",
        "~/llama.cpp/build/bin/llama-cli",
        "llama-cli"
    ]

    # Test model files
    print("=" * 60)
    print("TESTING MODEL FILES")
    print("=" * 60)
    for model_path in model_paths:
        check_cmd = f'wsl test -f "{model_path}" && echo "exists"'
        result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)
        status = "[OK] FOUND" if "exists" in result.stdout else "[NO] NOT FOUND"
        print(f"{status}: {model_path}")

    # Test llama.cpp binary
    print("\n" + "=" * 60)
    print("TESTING LLAMA.CPP BINARY")
    print("=" * 60)

    for path in llama_cpp_paths:
        if path == "llama-cli":
            check_cmd = 'wsl which llama-cli'
            result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)
            status = "[OK] FOUND" if result.returncode == 0 else "[NO] NOT FOUND"
            print(f"{status}: {path} (in PATH)")
        else:
            check_cmd = f'wsl test -f "{path}" && echo "exists"'
            result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)
            status = "[OK] FOUND" if "exists" in result.stdout else "[NO] NOT FOUND"
            print(f"{status}: {path}")

    # Test llama-cli version
    print("\n" + "=" * 60)
    print("TESTING LLAMA.CPP VERSION")
    print("=" * 60)
    try:
        result = subprocess.run('wsl /mnt/d/workspace/llama.cpp/build/bin/llama-cli --version',
                              shell=True, capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"[OK] llama-cli version check successful:")
            print(result.stdout[:200])
        else:
            print(f"[NO] llama-cli version check failed:")
            print(result.stderr[:200])
    except Exception as e:
        print(f"[NO] Error testing llama-cli: {e}")

    # Test a simple model run
    print("\n" + "=" * 60)
    print("TESTING MODEL EXECUTION")
    print("=" * 60)

    model_path = "/mnt/d/models/organized/Dolphin3.0-Llama3.1-8B-Q6_K.gguf"
    prompt = "Hello"

    cmd = f'wsl bash -c "/mnt/d/workspace/llama.cpp/build/bin/llama-cli -m {model_path} -p \\"{prompt}\\" -n 10 -ngl 999"'

    print(f"Running command (limited to 10 tokens for test)...")
    print(f"Model: {model_path}")
    print(f"Prompt: {prompt}\n")

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print("[OK] Model loaded and executed successfully!")
            print(f"\nOutput (first 500 chars):\n{result.stdout[:500]}")
        else:
            print(f"[NO] Model execution failed with return code {result.returncode}")
            print(f"Error:\n{result.stderr[:500]}")
    except subprocess.TimeoutExpired:
        print("[NO] Model execution timed out")
    except Exception as e:
        print(f"[NO] Error: {e}")

if __name__ == "__main__":
    test_model_loading()
