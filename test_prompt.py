import subprocess
import sys

# Simulate the fixed command building
prompt = "what is dns spoofing?"
model_path = "/mnt/d/models/organized/Dolphin3.0-Llama3.1-8B-Q6_K.gguf"
llama_cli_path = "/mnt/d/workspace/llama.cpp/build/bin/llama-cli"

cmd_args = [
    llama_cli_path,
    "-m", model_path,
    "-p", prompt,
    "-ngl", "999",
    "-n", "20",  # Just 20 tokens for testing
]

print(f"Testing prompt with special characters: '{prompt}'")
print(f"Command args: {cmd_args}\n")

# Test in WSL
cmd_args_wsl = ["wsl"] + cmd_args
result = subprocess.run(cmd_args_wsl, capture_output=True, text=True)

if result.returncode == 0:
    print("[OK] Executed successfully!")
    print("\nOutput (first 300 chars):")
    print(result.stdout[:300])
else:
    print(f"[ERROR] Failed with return code {result.returncode}")
    print(f"stderr: {result.stderr[:200]}")
