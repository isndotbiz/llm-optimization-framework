#!/usr/bin/env python3
"""Test llama.cpp execution to reproduce the bug"""

import subprocess
import sys

def test_simple_execution():
    """Test a simple llama.cpp execution"""
    print("=" * 80)
    print("TESTING LLAMA.CPP EXECUTION")
    print("=" * 80)
    print()

    # Use the first working model (qwen3-coder-30b)
    model_path = "/mnt/d/models/organized/Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf"
    prompt = "Say hello in one sentence."

    # Build command as the new code does
    cmd_parts = [
        "~/llama.cpp/build/bin/llama-cli",
        "-m", model_path,
        "-p", prompt,
        "-ngl", "999",
        "-t", "24",
        "-n", "50",  # Limit output tokens for testing
        "--temp", "0.7",
        "--top-p", "0.8",
        "--top-k", "20",
        "-c", "2048",  # Smaller context for testing
    ]

    # Build bash command string (same as ai-router.py line 885)
    bash_cmd = " ".join(f"'{part}'" if " " in part or any(c in part for c in ['$', '`', '"', '\\', ';', '&', '|']) else part for part in cmd_parts)

    # Build WSL command
    cmd_args = ['wsl', 'bash', '-c', bash_cmd]

    print("Command to execute:")
    print(f"  {bash_cmd}")
    print()
    print("Testing execution...")
    print()

    try:
        result = subprocess.run(cmd_args, shell=False, capture_output=True, text=True, timeout=60)

        print(f"Return code: {result.returncode}")
        print()

        if result.returncode != 0:
            print("STDERR:")
            print(result.stderr[:1000])
            print()
            print("STDOUT:")
            print(result.stdout[:1000])
            print()
            return False
        else:
            print("SUCCESS!")
            print()
            print("First 500 chars of output:")
            print(result.stdout[:500])
            return True

    except subprocess.TimeoutExpired:
        print("ERROR: Command timed out after 60 seconds!")
        return False
    except Exception as e:
        print(f"ERROR: Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_simple_execution()
    sys.exit(0 if success else 1)
