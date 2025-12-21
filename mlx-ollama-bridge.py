#!/usr/bin/env python3
"""
MLX-Ollama Bridge
=================

Provides Ollama-compatible API endpoints (localhost:11434) that route
requests to local MLX models instead of Ollama. This allows seamless
migration from Ollama to MLX while maintaining API compatibility.

Features:
- Drop-in replacement for Ollama API
- Full support for /api/generate, /api/chat, /api/tags endpoints
- Automatic model name mapping (Ollama format -> MLX format)
- Streaming and non-streaming responses
- Comprehensive error handling and logging
- Can run alongside Ollama on different port

Usage:
    # Default port 11434 (replaces Ollama)
    python mlx-ollama-bridge.py

    # Custom port (run alongside Ollama)
    python mlx-ollama-bridge.py --port 11435

    # With verbose logging
    python mlx-ollama-bridge.py --verbose

Requirements:
    pip install flask mlx-lm
"""

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Generator
from datetime import datetime

try:
    from flask import Flask, request, Response, jsonify, stream_with_context
    import mlx.core as mx
    from mlx_lm import load, generate
except ImportError as e:
    print(f"ERROR: Missing required dependencies: {e}")
    print("\nPlease install required packages:")
    print("  pip install flask mlx-lm")
    sys.exit(1)


# ============================================================================
# Configuration and Constants
# ============================================================================

DEFAULT_PORT = 11434
DEFAULT_HOST = "0.0.0.0"
MLX_MODELS_DIR = Path.home() / "workspace" / "mlx"

# Model name mapping: Ollama format -> Local MLX model path
MODEL_MAPPINGS = {
    # Qwen Coder models (local MLX)
    "qwen2.5-coder:7b": "mlx/qwen25-coder-7b",
    "qwen2.5-coder": "mlx/qwen25-coder-7b",
    "qwen2.5-coder:32b": "mlx/qwen25-coder-32b",
    "qwen2.5-coder:latest": "mlx/qwen25-coder-7b",

    # Qwen general models (local MLX)
    "qwen3:7b": "mlx/qwen3-7b",
    "qwen3": "mlx/qwen3-7b",
    "qwen3:latest": "mlx/qwen3-7b",

    # Reasoning models (local MLX)
    "deepseek-r1:8b": "mlx/deepseek-r1-8b",
    "deepseek-r1": "mlx/deepseek-r1-8b",
    "deepseek-r1:latest": "mlx/deepseek-r1-8b",

    # Instruction models (local MLX)
    "phi-4": "mlx/phi-4",
    "phi4": "mlx/phi-4",
    "phi-4:14b": "mlx/phi-4",
    "phi-4:latest": "mlx/phi-4",

    # Fast models (local MLX)
    "mistral": "mlx/mistral-7b",
    "mistral:7b": "mlx/mistral-7b",
    "mistral:latest": "mlx/mistral-7b",
}


# ============================================================================
# Logging Configuration
# ============================================================================

def setup_logging(verbose: bool = False):
    """Configure logging with appropriate level and format."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger('mlx-ollama-bridge')


# ============================================================================
# MLX Model Manager
# ============================================================================

class MLXModelManager:
    """Manages loading and caching of MLX models."""

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.loaded_models: Dict[str, Any] = {}
        self.model_cache_dir = MLX_MODELS_DIR

    def get_mlx_model_path(self, ollama_model: str) -> str:
        """
        Convert Ollama model name to MLX model path.

        Args:
            ollama_model: Ollama-style model name

        Returns:
            MLX model path (HuggingFace format or local path)
        """
        # Check if exact match in mappings
        if ollama_model in MODEL_MAPPINGS:
            return MODEL_MAPPINGS[ollama_model]

        # Try to extract base name
        base_name = ollama_model.split(':')[0]
        if base_name in MODEL_MAPPINGS:
            return MODEL_MAPPINGS[base_name]

        # If no mapping, assume it's already an MLX path
        self.logger.warning(
            f"No mapping found for '{ollama_model}', using as-is"
        )
        return ollama_model

    def load_model(self, model_path: str) -> tuple:
        """
        Load MLX model and tokenizer.

        Args:
            model_path: MLX model path

        Returns:
            Tuple of (model, tokenizer)
        """
        if model_path in self.loaded_models:
            self.logger.debug(f"Using cached model: {model_path}")
            return self.loaded_models[model_path]

        self.logger.info(f"Loading MLX model: {model_path}")
        try:
            model, tokenizer = load(model_path)
            self.loaded_models[model_path] = (model, tokenizer)
            self.logger.info(f"Successfully loaded: {model_path}")
            return model, tokenizer
        except Exception as e:
            self.logger.error(f"Failed to load model '{model_path}': {e}")
            raise

    def list_available_models(self) -> List[Dict[str, Any]]:
        """
        List all available MLX models.

        Returns:
            List of model metadata dictionaries
        """
        models = []

        # Add all mapped models
        for ollama_name, mlx_path in MODEL_MAPPINGS.items():
            # Estimate size based on model name
            size_gb = 4.5  # Default
            if "32b" in ollama_name.lower():
                size_gb = 18.0
            elif "14b" in ollama_name.lower():
                size_gb = 9.0
            elif "7b" in ollama_name.lower():
                size_gb = 4.5

            models.append({
                "name": ollama_name,
                "modified_at": datetime.now().isoformat() + "Z",
                "size": int(size_gb * 1024 * 1024 * 1024),
                "digest": f"mlx:{mlx_path}",
                "details": {
                    "format": "mlx",
                    "family": "qwen" if "qwen" in ollama_name else "other",
                    "parameter_size": mlx_path.split('-')[-1] if '-' in mlx_path else "unknown",
                    "quantization_level": "4bit"
                }
            })

        return models

    def unload_model(self, model_path: str):
        """Unload model from cache to free memory."""
        if model_path in self.loaded_models:
            del self.loaded_models[model_path]
            mx.metal.clear_cache()
            self.logger.info(f"Unloaded model: {model_path}")


# ============================================================================
# Flask Application
# ============================================================================

def create_app(logger: logging.Logger) -> Flask:
    """Create and configure Flask application."""
    app = Flask(__name__)
    model_manager = MLXModelManager(logger)

    # ========================================================================
    # API Endpoints
    # ========================================================================

    @app.route('/api/version', methods=['GET'])
    def version():
        """Return version information (Ollama-compatible)."""
        return jsonify({
            "version": "0.1.0-mlx-bridge"
        })

    @app.route('/api/tags', methods=['GET'])
    def list_models():
        """List all available models (Ollama-compatible)."""
        try:
            models = model_manager.list_available_models()
            return jsonify({"models": models})
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route('/api/generate', methods=['POST'])
    def generate_completion():
        """
        Generate completion endpoint (Ollama-compatible).

        Request body:
            {
                "model": "qwen2.5-coder:7b",
                "prompt": "Write a hello world in Python",
                "stream": false,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "num_predict": 512
                }
            }
        """
        try:
            data = request.json
            ollama_model = data.get('model')
            prompt = data.get('prompt', '')
            stream = data.get('stream', False)
            options = data.get('options', {})
            system_prompt = data.get('system', None)

            if not ollama_model:
                return jsonify({"error": "model is required"}), 400
            if not prompt:
                return jsonify({"error": "prompt is required"}), 400

            # Convert model name
            mlx_model_path = model_manager.get_mlx_model_path(ollama_model)

            # Load model
            model, tokenizer = model_manager.load_model(mlx_model_path)

            # Build full prompt with system message
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"System: {system_prompt}\n\nUser: {prompt}"

            # Extract parameters
            temperature = options.get('temperature', 0.7)
            top_p = options.get('top_p', 0.9)
            max_tokens = options.get('num_predict', 512)

            logger.info(
                f"Generate request: model={ollama_model}, "
                f"stream={stream}, temp={temperature}"
            )

            if stream:
                return Response(
                    stream_with_context(
                        generate_stream(
                            model, tokenizer, full_prompt,
                            temperature, top_p, max_tokens, ollama_model
                        )
                    ),
                    content_type='application/x-ndjson'
                )
            else:
                # Non-streaming response
                start_time = time.time()
                response_text = generate(
                    model, tokenizer, prompt=full_prompt,
                    temp=temperature, top_p=top_p, max_tokens=max_tokens,
                    verbose=False
                )
                elapsed_time = time.time() - start_time

                return jsonify({
                    "model": ollama_model,
                    "created_at": datetime.now().isoformat() + "Z",
                    "response": response_text,
                    "done": True,
                    "total_duration": int(elapsed_time * 1e9),
                    "eval_count": len(response_text.split())
                })

        except Exception as e:
            logger.error(f"Generate error: {e}", exc_info=True)
            return jsonify({"error": str(e)}), 500

    @app.route('/api/chat', methods=['POST'])
    def chat_completion():
        """
        Chat completion endpoint (Ollama-compatible).

        Request body:
            {
                "model": "qwen2.5-coder:7b",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant"},
                    {"role": "user", "content": "Hello!"}
                ],
                "stream": false
            }
        """
        try:
            data = request.json
            ollama_model = data.get('model')
            messages = data.get('messages', [])
            stream = data.get('stream', False)
            options = data.get('options', {})

            if not ollama_model:
                return jsonify({"error": "model is required"}), 400
            if not messages:
                return jsonify({"error": "messages is required"}), 400

            # Convert model name
            mlx_model_path = model_manager.get_mlx_model_path(ollama_model)

            # Load model
            model, tokenizer = model_manager.load_model(mlx_model_path)

            # Convert messages to prompt
            prompt = build_chat_prompt(messages)

            # Extract parameters
            temperature = options.get('temperature', 0.7)
            top_p = options.get('top_p', 0.9)
            max_tokens = options.get('num_predict', 512)

            logger.info(
                f"Chat request: model={ollama_model}, "
                f"messages={len(messages)}, stream={stream}"
            )

            if stream:
                return Response(
                    stream_with_context(
                        generate_chat_stream(
                            model, tokenizer, prompt,
                            temperature, top_p, max_tokens, ollama_model
                        )
                    ),
                    content_type='application/x-ndjson'
                )
            else:
                # Non-streaming response
                start_time = time.time()
                response_text = generate(
                    model, tokenizer, prompt=prompt,
                    temp=temperature, top_p=top_p, max_tokens=max_tokens,
                    verbose=False
                )
                elapsed_time = time.time() - start_time

                return jsonify({
                    "model": ollama_model,
                    "created_at": datetime.now().isoformat() + "Z",
                    "message": {
                        "role": "assistant",
                        "content": response_text
                    },
                    "done": True,
                    "total_duration": int(elapsed_time * 1e9),
                    "eval_count": len(response_text.split())
                })

        except Exception as e:
            logger.error(f"Chat error: {e}", exc_info=True)
            return jsonify({"error": str(e)}), 500

    @app.route('/api/pull', methods=['POST'])
    def pull_model():
        """Pull model endpoint (not implemented for MLX)."""
        data = request.json
        model = data.get('name')
        logger.warning(f"Pull request for '{model}' - not implemented for MLX")
        return jsonify({
            "error": "Model pulling not supported. Models must be pre-downloaded."
        }), 501

    @app.route('/api/delete', methods=['DELETE'])
    def delete_model():
        """Delete model endpoint."""
        data = request.json
        model = data.get('name')
        try:
            mlx_model_path = model_manager.get_mlx_model_path(model)
            model_manager.unload_model(mlx_model_path)
            return jsonify({"status": "success"})
        except Exception as e:
            logger.error(f"Delete error: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint."""
        return jsonify({
            "status": "healthy",
            "service": "mlx-ollama-bridge",
            "loaded_models": len(model_manager.loaded_models)
        })

    # ========================================================================
    # Helper Functions
    # ========================================================================

    def build_chat_prompt(messages: List[Dict[str, str]]) -> str:
        """Convert chat messages to a single prompt string."""
        prompt_parts = []
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')

            if role == 'system':
                prompt_parts.append(f"System: {content}")
            elif role == 'user':
                prompt_parts.append(f"User: {content}")
            elif role == 'assistant':
                prompt_parts.append(f"Assistant: {content}")

        return "\n\n".join(prompt_parts)

    def generate_stream(
        model, tokenizer, prompt: str,
        temperature: float, top_p: float, max_tokens: int,
        model_name: str
    ) -> Generator[str, None, None]:
        """Generate streaming response for /api/generate endpoint."""
        try:
            # MLX doesn't support native streaming, so we'll chunk the response
            response_text = generate(
                model, tokenizer, prompt=prompt,
                temp=temperature, top_p=top_p, max_tokens=max_tokens,
                verbose=False
            )

            # Stream in chunks
            chunk_size = 10  # words per chunk
            words = response_text.split()

            for i in range(0, len(words), chunk_size):
                chunk = ' '.join(words[i:i+chunk_size])
                if i + chunk_size < len(words):
                    chunk += ' '

                yield json.dumps({
                    "model": model_name,
                    "created_at": datetime.now().isoformat() + "Z",
                    "response": chunk,
                    "done": False
                }) + "\n"

            # Final chunk
            yield json.dumps({
                "model": model_name,
                "created_at": datetime.now().isoformat() + "Z",
                "response": "",
                "done": True
            }) + "\n"

        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield json.dumps({"error": str(e)}) + "\n"

    def generate_chat_stream(
        model, tokenizer, prompt: str,
        temperature: float, top_p: float, max_tokens: int,
        model_name: str
    ) -> Generator[str, None, None]:
        """Generate streaming response for /api/chat endpoint."""
        try:
            response_text = generate(
                model, tokenizer, prompt=prompt,
                temp=temperature, top_p=top_p, max_tokens=max_tokens,
                verbose=False
            )

            # Stream in chunks
            chunk_size = 10
            words = response_text.split()

            for i in range(0, len(words), chunk_size):
                chunk = ' '.join(words[i:i+chunk_size])
                if i + chunk_size < len(words):
                    chunk += ' '

                yield json.dumps({
                    "model": model_name,
                    "created_at": datetime.now().isoformat() + "Z",
                    "message": {
                        "role": "assistant",
                        "content": chunk
                    },
                    "done": False
                }) + "\n"

            # Final chunk
            yield json.dumps({
                "model": model_name,
                "created_at": datetime.now().isoformat() + "Z",
                "message": {
                    "role": "assistant",
                    "content": ""
                },
                "done": True
            }) + "\n"

        except Exception as e:
            logger.error(f"Chat streaming error: {e}")
            yield json.dumps({"error": str(e)}) + "\n"

    return app


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='MLX-Ollama Bridge - Ollama-compatible API for MLX models',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run on default port 11434 (replaces Ollama)
  python mlx-ollama-bridge.py

  # Run on custom port (alongside Ollama)
  python mlx-ollama-bridge.py --port 11435

  # Enable verbose logging
  python mlx-ollama-bridge.py --verbose

  # Custom host and port
  python mlx-ollama-bridge.py --host 0.0.0.0 --port 8080
        """
    )

    parser.add_argument(
        '--host',
        default=DEFAULT_HOST,
        help=f'Host to bind to (default: {DEFAULT_HOST})'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=DEFAULT_PORT,
        help=f'Port to listen on (default: {DEFAULT_PORT})'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    # Setup logging
    logger = setup_logging(args.verbose)

    # Print banner
    print("=" * 70)
    print("MLX-Ollama Bridge v0.1.0")
    print("Ollama-compatible API for MLX models")
    print("=" * 70)
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print(f"API URL: http://{args.host}:{args.port}")
    print(f"Models directory: {MLX_MODELS_DIR}")
    print(f"Verbose logging: {args.verbose}")
    print("=" * 70)
    print("\nEndpoints:")
    print(f"  - GET  http://{args.host}:{args.port}/api/version")
    print(f"  - GET  http://{args.host}:{args.port}/api/tags")
    print(f"  - POST http://{args.host}:{args.port}/api/generate")
    print(f"  - POST http://{args.host}:{args.port}/api/chat")
    print(f"  - GET  http://{args.host}:{args.port}/health")
    print("=" * 70)
    print("\nPress Ctrl+C to stop\n")

    # Create and run app
    try:
        app = create_app(logger)
        app.run(
            host=args.host,
            port=args.port,
            debug=args.verbose,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n\nShutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
