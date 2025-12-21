#!/usr/bin/env python3
"""
Simple MLX Server on port 11434
Ollama-compatible API for local MLX models

Usage:
    source ~/venv-mlx/bin/activate
    python3 mlx-server.py
"""

import json
import logging
import os
from pathlib import Path
from datetime import datetime
from flask import Flask, request, jsonify, Response
import mlx.core as mx
from mlx_lm import load, generate as mlx_generate

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Available local MLX models (in project mlx/ directory)
MLX_HOME = Path.cwd() / "mlx"
MODELS = {
    "qwen2.5-coder:7b": str(MLX_HOME / "qwen25-coder-7b"),
    "qwen2.5-coder:32b": str(MLX_HOME / "qwen25-coder-32b"),
    "qwen3:7b": str(MLX_HOME / "qwen3-7b"),
    "deepseek-r1:8b": str(MLX_HOME / "deepseek-r1-8b"),
    "dolphin3:8b": str(MLX_HOME / "dolphin3-8b"),
    "phi-4": str(MLX_HOME / "phi-4"),
    "mistral:7b": str(MLX_HOME / "mistral-7b"),
    # Aliases
    "qwen2.5-coder": str(MLX_HOME / "qwen25-coder-7b"),
    "qwen3": str(MLX_HOME / "qwen3-7b"),
    "deepseek-r1": str(MLX_HOME / "deepseek-r1-8b"),
    "dolphin3": str(MLX_HOME / "dolphin3-8b"),
    "phi4": str(MLX_HOME / "phi-4"),
    "mistral": str(MLX_HOME / "mistral-7b"),
}

# Model cache
model_cache = {}
current_model = None  # Track currently loaded model

app = Flask(__name__)

# CORS setup
@app.before_request
def handle_preflight():
    """Handle CORS preflight requests."""
    if request.method == "OPTIONS":
        response = Response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
        response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
        return response

@app.after_request
def add_cors_headers(response):
    """Add CORS headers to all responses."""
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
    return response

def get_model_path(model_name: str) -> str:
    """Get MLX model path from Ollama model name."""
    if model_name in MODELS:
        return MODELS[model_name]
    # Try without tag
    base = model_name.split(':')[0]
    if base in MODELS:
        return MODELS[base]
    raise ValueError(f"Model '{model_name}' not available")

def unload_all_models():
    """Unload all cached models to free GPU memory."""
    global model_cache, current_model
    if model_cache:
        logger.info(f"Unloading {len(model_cache)} cached models to free GPU memory")
        model_cache.clear()
        current_model = None
        mx.metal.clear_cache() if hasattr(mx, 'metal') else None

def load_mlx_model(model_path: str):
    """Load MLX model, unloading others if needed to manage GPU memory."""
    global current_model, model_cache

    # If a different model is already loaded, unload it first
    if current_model != model_path and model_cache:
        unload_all_models()

    if model_path not in model_cache:
        logger.info(f"Loading model: {model_path}")
        try:
            model, tokenizer = load(model_path)
            model_cache[model_path] = (model, tokenizer)
            current_model = model_path
            logger.info(f"Loaded: {model_path}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise

    return model_cache[model_path]

@app.route('/api/tags', methods=['GET'])
def list_models():
    """List available models (Ollama-compatible)."""
    models = []
    seen = set()
    for ollama_name, mlx_path in MODELS.items():
        if ':' in ollama_name and ollama_name not in seen:  # Only include models with version tags
            seen.add(ollama_name)
            models.append({
                "name": ollama_name,
                "modified_at": datetime.now().isoformat() + "Z",
                "size": 4500000000,  # Approximate
                "digest": f"mlx:{mlx_path}",
                "details": {
                    "format": "mlx",
                    "family": "qwen" if "qwen" in ollama_name else "other",
                }
            })
    logger.info(f"Listing {len(models)} models")
    return jsonify({"models": models})

@app.route('/api/generate', methods=['POST'])
def generate():
    """Generate text completion (Ollama-compatible)."""
    try:
        data = request.json
        model_name = data.get('model')
        prompt = data.get('prompt', '')
        stream = data.get('stream', False)
        options = data.get('options', {})

        logger.info(f"Generate request: model={model_name}")
        logger.info(f"Available models: {list(MODELS.keys())}")

        if not model_name:
            return jsonify({"error": "model required"}), 400
        if not prompt:
            return jsonify({"error": "prompt required"}), 400

        # Get and load model
        try:
            model_path = get_model_path(model_name)
        except ValueError as e:
            logger.error(f"Model error: {e}")
            return jsonify({"error": str(e)}), 400

        model, tokenizer = load_mlx_model(model_path)

        # Generate
        logger.info(f"Generating with {model_name}")
        response = mlx_generate(
            model,
            tokenizer,
            prompt=prompt,
            max_tokens=options.get('num_predict', 512)
        )

        return jsonify({
            "model": model_name,
            "created_at": datetime.now().isoformat() + "Z",
            "response": response,
            "done": True,
        })

    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat completion (Ollama-compatible)."""
    try:
        data = request.json
        model_name = data.get('model')
        messages = data.get('messages', [])
        options = data.get('options', {})

        if not model_name:
            return jsonify({"error": "model required"}), 400

        # Build prompt from messages using proper chat template format
        # Format: <|im_start|>role\ncontent\n<|im_end|>\n
        prompt = ""
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            prompt += f"<|im_start|>{role}\n{content}\n<|im_end|>\n"

        # Add assistant prompt continuation for proper response generation
        prompt += "<|im_start|>assistant\n"

        # Get and load model
        model_path = get_model_path(model_name)
        model, tokenizer = load_mlx_model(model_path)

        # Generate
        logger.info(f"Chat with {model_name}")
        response = mlx_generate(
            model,
            tokenizer,
            prompt=prompt,
            max_tokens=options.get('num_predict', 512)
        )

        return jsonify({
            "model": model_name,
            "created_at": datetime.now().isoformat() + "Z",
            "message": {
                "role": "assistant",
                "content": response
            },
            "done": True,
        })

    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/version', methods=['GET'])
def version():
    """Get version info."""
    return jsonify({
        "version": "mlx-server/1.0",
        "mlx_version": mx.__version__
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint for BoltAI."""
    return jsonify({"status": "ok"})

@app.route('/', methods=['GET'])
def root():
    """Root endpoint."""
    return jsonify({"status": "ok", "version": "mlx-server/1.0"})

@app.route('/v1/models', methods=['GET'])
def openai_list_models():
    """List models in OpenAI-compatible format for Raycast/BoltAI."""
    models = []
    seen = set()
    for ollama_name, mlx_path in MODELS.items():
        if ':' in ollama_name and ollama_name not in seen:
            seen.add(ollama_name)
            models.append({
                "id": ollama_name,
                "object": "model",
                "created": int(datetime.now().timestamp()),
                "owned_by": "mlx-local"
            })
    logger.info(f"Listing {len(models)} models (OpenAI format)")
    return jsonify({
        "object": "list",
        "data": models
    })

@app.route('/v1/chat/completions', methods=['POST'])
def openai_chat_completions():
    """Chat completions in OpenAI-compatible format for Raycast/BoltAI."""
    try:
        data = request.json
        model_name = data.get('model')
        messages = data.get('messages', [])
        max_tokens = data.get('max_tokens', 512)
        stream = data.get('stream', False)

        if not model_name:
            return jsonify({"error": {"message": "model required"}}), 400
        if not messages:
            return jsonify({"error": {"message": "messages required"}}), 400

        logger.info(f"OpenAI chat request: model={model_name}, messages={len(messages)}, stream={stream}")

        # Get and load model
        try:
            model_path = get_model_path(model_name)
        except ValueError as e:
            logger.error(f"Model error: {e}")
            return jsonify({"error": {"message": str(e)}}), 404

        model, tokenizer = load_mlx_model(model_path)

        # Build prompt from messages using proper chat template format
        # Format: <|im_start|>role\ncontent\n<|im_end|>\n
        prompt = ""
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            prompt += f"<|im_start|>{role}\n{content}\n<|im_end|>\n"

        # Add assistant prompt continuation for proper response generation
        prompt += "<|im_start|>assistant\n"

        # Generate
        logger.info(f"Generating with {model_name} (max_tokens={max_tokens})")
        response_text = mlx_generate(
            model,
            tokenizer,
            prompt=prompt,
            max_tokens=max_tokens
        )
        logger.info(f"Generated {len(response_text)} chars from {model_name}")

        # Handle streaming vs non-streaming
        if stream:
            # Return streaming response
            def generate_stream():
                completion_id = f"chatcmpl-{int(datetime.now().timestamp())}"
                # Send the full response as one stream event for simplicity
                yield f"data: {json.dumps({
                    'id': completion_id,
                    'object': 'chat.completion.chunk',
                    'created': int(datetime.now().timestamp()),
                    'model': model_name,
                    'choices': [{
                        'index': 0,
                        'delta': {'content': response_text},
                        'finish_reason': None
                    }]
                })}\n\n"
                # Send done message
                yield f"data: {json.dumps({
                    'id': completion_id,
                    'object': 'chat.completion.chunk',
                    'created': int(datetime.now().timestamp()),
                    'model': model_name,
                    'choices': [{
                        'index': 0,
                        'delta': {},
                        'finish_reason': 'stop'
                    }]
                })}\n\n"
                yield "data: [DONE]\n\n"

            return Response(generate_stream(), mimetype='text/event-stream')
        else:
            # Return complete response
            return jsonify({
                "id": f"chatcmpl-{int(datetime.now().timestamp())}",
                "object": "chat.completion",
                "created": int(datetime.now().timestamp()),
                "model": model_name,
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response_text
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0
                }
            })

    except Exception as e:
        logger.error(f"Error in chat completions: {e}", exc_info=True)
        return jsonify({"error": {"message": str(e)}}), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("MLX Server (Ollama-compatible)")
    print("="*60)
    print(f"MLX Version: {mx.__version__}")
    print(f"Metal GPU: {mx.metal.is_available()}")
    print(f"Models: {len([m for m in MODELS.keys() if ':' in m])}")
    print("="*60)
    print("\nAvailable models:")
    for name in sorted([m for m in MODELS.keys() if ':' in m]):
        print(f"  • {name}")
    print("\nOllama-compatible endpoints:")
    print("  GET  http://localhost:11434/api/tags")
    print("  POST http://localhost:11434/api/generate")
    print("  POST http://localhost:11434/api/chat")
    print("\nOpenAI-compatible endpoints (for Raycast/BoltAI):")
    print("  GET  http://localhost:11434/v1/models")
    print("  POST http://localhost:11434/v1/chat/completions")
    print("\nListening on http://0.0.0.0:11434 with CORS enabled")
    print("="*60 + "\n")

    app.run(host='0.0.0.0', port=11434, debug=False)
