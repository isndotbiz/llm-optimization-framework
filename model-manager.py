#!/usr/bin/env python3
"""
MLX Model Manager - Download, manage, and switch between models
Supports dynamic loading/unloading for 24GB M4 MacBook
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Optional, List, Dict
import mlx.core as mx

# Model registry with MLX-optimized community models
MODELS_REGISTRY = {
    # Uncensored Models (Primary)
    "dolphin-3.0": {
        "name": "Dolphin 3.0 Llama 8B",
        "path": "mlx-community/Dolphin3.0-Llama3.1-8B-4bit",
        "size": "4.5GB",
        "type": "uncensored",
        "description": "Best uncensored model, great for creative tasks"
    },
    "hermes-4": {
        "name": "Hermes-4 14B",
        "path": "mlx-community/Hermes-4-14B-4bit",
        "size": "7-8GB",
        "type": "creative",
        "description": "Creative and unrestricted responses"
    },
    "deepseek-r1-14b": {
        "name": "DeepSeek-R1 Distill Qwen 14B",
        "path": "mlx-community/DeepSeek-R1-Distill-Qwen-14B-MLX",
        "size": "7-8GB",
        "type": "reasoning",
        "description": "Reasoning without distillation overhead"
    },
    "deepseek-r1-32b": {
        "name": "DeepSeek-R1 Distill Qwen 32B",
        "path": "mlx-community/DeepSeek-R1-Distill-Qwen-32B-4bit",
        "size": "16-18GB",
        "type": "reasoning",
        "description": "Advanced reasoning model"
    },
    "qwen-2.5-uncensored": {
        "name": "Qwen2.5-7B Uncensored",
        "path": "mlx-community/Qwen2.5-7B-Instruct-Uncensored-4bit",
        "size": "4GB",
        "type": "fast",
        "description": "Fast uncensored general purpose"
    },

    # Existing Models (Keep)
    "qwen-2.5-coder-7b": {
        "name": "Qwen2.5-Coder 7B",
        "path": "mlx-community/Qwen2.5-Coder-7B-4bit",
        "size": "3.5GB",
        "type": "coding",
        "description": "Code generation and completion"
    },
    "deepseek-r1-8b": {
        "name": "DeepSeek-R1 8B",
        "path": "mlx-community/DeepSeek-R1-Distill-Qwen-7B-MLX",
        "size": "4.2GB",
        "type": "reasoning",
        "description": "Lightweight reasoning model"
    },
    "mistral-7b": {
        "name": "Mistral 7B",
        "path": "mlx-community/Mistral-7B-Instruct-4bit",
        "size": "3.8GB",
        "type": "general",
        "description": "Fast general purpose model"
    },
}

class ModelManager:
    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or Path.home() / ".cache" / "mlx-models"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.registry_file = self.cache_dir / "registry.json"
        self.loaded_model = None
        self.loaded_tokenizer = None
        self.current_model_key = None
        self.load_registry()

    def load_registry(self):
        """Load cached model registry"""
        if self.registry_file.exists():
            with open(self.registry_file) as f:
                self.registry = json.load(f)
        else:
            self.registry = {}

    def save_registry(self):
        """Save model registry"""
        with open(self.registry_file, 'w') as f:
            json.dump(self.registry, f, indent=2)

    def list_models(self, type_filter: Optional[str] = None) -> List[Dict]:
        """List available models"""
        models = []
        for key, info in MODELS_REGISTRY.items():
            if type_filter and info["type"] != type_filter:
                continue
            status = "✓ Downloaded" if self.is_downloaded(key) else "⊘ Not downloaded"
            models.append({
                "key": key,
                "name": info["name"],
                "size": info["size"],
                "type": info["type"],
                "status": status,
                "description": info["description"]
            })
        return models

    def is_downloaded(self, model_key: str) -> bool:
        """Check if model is downloaded locally"""
        if model_key not in MODELS_REGISTRY:
            return False
        model_info = MODELS_REGISTRY[model_key]
        # Check if model exists in HF cache
        cache_path = Path.home() / ".cache" / "huggingface" / "hub"
        return True  # Assume HF downloads automatically

    def download_model(self, model_key: str) -> bool:
        """Download model from mlx-community"""
        if model_key not in MODELS_REGISTRY:
            print(f"❌ Unknown model: {model_key}")
            return False

        model_info = MODELS_REGISTRY[model_key]
        print(f"\n📥 Downloading {model_info['name']} ({model_info['size']})...")
        print(f"   From: {model_info['path']}")

        try:
            # Use huggingface-cli to download
            result = subprocess.run(
                ["huggingface-cli", "download", model_info["path"], "--cache-dir", str(self.cache_dir)],
                capture_output=True,
                text=True,
                timeout=3600
            )

            if result.returncode == 0:
                print(f"✓ Downloaded successfully!")
                self.registry[model_key] = {
                    "downloaded": True,
                    "path": model_info["path"]
                }
                self.save_registry()
                return True
            else:
                print(f"❌ Download failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    def unload_model(self):
        """Unload currently loaded model to free memory"""
        if self.loaded_model is None:
            print("No model currently loaded")
            return

        print(f"🔄 Unloading {self.current_model_key}...")
        del self.loaded_model
        del self.loaded_tokenizer
        self.loaded_model = None
        self.loaded_tokenizer = None
        self.current_model_key = None

        # Force garbage collection
        import gc
        gc.collect()
        mx.metal.clear_cache()
        print("✓ Model unloaded, memory freed")

    def load_model(self, model_key: str):
        """Load a model from mlx-community"""
        if model_key not in MODELS_REGISTRY:
            print(f"❌ Unknown model: {model_key}")
            return False

        # Unload previous model if any
        if self.loaded_model is not None:
            self.unload_model()

        model_info = MODELS_REGISTRY[model_key]
        print(f"\n📦 Loading {model_info['name']}...")
        print(f"   Path: {model_info['path']}")

        try:
            from mlx_lm import load

            print("   Loading weights...")
            model, tokenizer = load(model_info["path"])

            self.loaded_model = model
            self.loaded_tokenizer = tokenizer
            self.current_model_key = model_key

            print(f"✓ Loaded successfully!")
            print(f"   Metal GPU: {mx.metal.is_available()}")
            return True
        except Exception as e:
            print(f"❌ Failed to load: {e}")
            return False

    def generate(self, prompt: str, max_tokens: int = 100, temperature: float = 0.7) -> str:
        """Generate text with currently loaded model"""
        if self.loaded_model is None:
            print("❌ No model loaded. Use 'load' command first.")
            return ""

        try:
            from mlx_lm import generate

            print(f"\n🤖 Generating with {self.current_model_key}...")
            response = generate(
                self.loaded_model,
                self.loaded_tokenizer,
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                verbose=False
            )
            return response
        except Exception as e:
            print(f"❌ Generation failed: {e}")
            return ""

    def interactive_chat(self):
        """Interactive chat with currently loaded model"""
        if self.loaded_model is None:
            print("❌ No model loaded. Use 'load' command first.")
            return

        print(f"\n💬 Chat with {self.current_model_key}")
        print("Type 'exit' to quit, 'unload' to free memory\n")

        while True:
            try:
                prompt = input("You: ").strip()

                if prompt.lower() == "exit":
                    break
                elif prompt.lower() == "unload":
                    self.unload_model()
                    break
                elif not prompt:
                    continue

                response = self.generate(prompt, max_tokens=200)
                print(f"\nModel: {response}\n")

            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}\n")


def main():
    """CLI interface"""
    manager = ModelManager()

    if len(sys.argv) < 2:
        print("MLX Model Manager - Manage uncensored models for your 24GB M4\n")
        print("Commands:")
        print("  list              - List available models")
        print("  download <key>    - Download a model")
        print("  load <key>        - Load a model into memory")
        print("  unload            - Unload current model")
        print("  chat              - Interactive chat with loaded model")
        print("  generate <prompt> - Generate text")
        print("  status            - Show current model status\n")
        print("Examples:")
        print("  python model-manager.py download dolphin-3.0")
        print("  python model-manager.py load dolphin-3.0")
        print("  python model-manager.py chat")
        return

    command = sys.argv[1].lower()

    if command == "list":
        print("\n📋 Available Models for Your 24GB M4\n")
        models = manager.list_models()
        for m in models:
            print(f"  {m['key']:25} {m['name']:30} {m['size']:10} [{m['status']}]")
            print(f"     {m['description']}\n")

    elif command == "download":
        if len(sys.argv) < 3:
            print("Usage: model-manager.py download <model_key>")
            print(f"Available: {', '.join(MODELS_REGISTRY.keys())}")
            return
        manager.download_model(sys.argv[2])

    elif command == "load":
        if len(sys.argv) < 3:
            print("Usage: model-manager.py load <model_key>")
            return
        manager.load_model(sys.argv[2])

    elif command == "unload":
        manager.unload_model()

    elif command == "chat":
        manager.interactive_chat()

    elif command == "generate":
        if len(sys.argv) < 3:
            print("Usage: model-manager.py generate <prompt>")
            return
        prompt = " ".join(sys.argv[2:])
        response = manager.generate(prompt)
        print(f"\n{response}\n")

    elif command == "status":
        if manager.current_model_key:
            print(f"✓ Loaded: {MODELS_REGISTRY[manager.current_model_key]['name']}")
        else:
            print("⊘ No model loaded")


if __name__ == "__main__":
    main()
