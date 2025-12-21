#!/usr/bin/env python3
"""
MLX Performance Benchmark Script
Tests model loading and inference speed with Metal GPU acceleration
"""

import time
import mlx.core as mx
from mlx_lm import load, generate

def benchmark_model(model_path: str, prompt: str = "def fibonacci(n):", max_tokens: int = 100):
    """Benchmark a single MLX model"""
    print(f"\n{'='*80}")
    print(f"Benchmarking: {model_path}")
    print(f"{'='*80}")

    # Metal GPU check
    print(f"Metal GPU Available: {mx.metal.is_available()}")
    print(f"MLX Version: {mx.__version__}")

    # Load model
    print("\n[1/3] Loading model...")
    start_load = time.time()
    model, tokenizer = load(model_path)
    load_time = time.time() - start_load
    print(f"✓ Model loaded in {load_time:.2f}s")

    # Warm up (first inference is slower)
    print("\n[2/3] Warming up GPU...")
    start_warmup = time.time()
    _ = generate(model, tokenizer, prompt=prompt, max_tokens=10, verbose=False)
    warmup_time = time.time() - start_warmup
    print(f"✓ Warmup completed in {warmup_time:.2f}s")

    # Benchmark inference
    print(f"\n[3/3] Generating {max_tokens} tokens...")
    start_gen = time.time()
    response = generate(model, tokenizer, prompt=prompt, max_tokens=max_tokens, verbose=True)
    gen_time = time.time() - start_gen

    # Calculate metrics
    tokens_per_sec = max_tokens / gen_time if gen_time > 0 else 0

    print(f"\n{'='*80}")
    print("RESULTS:")
    print(f"{'='*80}")
    print(f"Load Time:        {load_time:.2f}s")
    print(f"Warmup Time:      {warmup_time:.2f}s")
    print(f"Generation Time:  {gen_time:.2f}s")
    print(f"Tokens Generated: {max_tokens}")
    print(f"Speed:            {tokens_per_sec:.2f} tokens/sec")
    print(f"{'='*80}\n")

    return {
        "model": model_path,
        "load_time": load_time,
        "warmup_time": warmup_time,
        "generation_time": gen_time,
        "tokens": max_tokens,
        "tokens_per_sec": tokens_per_sec
    }

if __name__ == "__main__":
    # Test with qwen3-7b (smallest model for quick benchmark)
    model_path = "mlx/qwen3-7b"

    print("MLX Performance Benchmark")
    print(f"Model: {model_path}")
    print(f"Platform: Apple Silicon with Metal GPU\n")

    results = benchmark_model(
        model_path=model_path,
        prompt="def fibonacci(n):",
        max_tokens=100
    )

    print("\nBenchmark Complete!")
    print(f"Summary: Loaded in {results['load_time']:.2f}s, generated at {results['tokens_per_sec']:.2f} tok/s")
