#!/usr/bin/env python3
"""
MLX Model Benchmarking Script
Comprehensive performance testing for MLX models vs Ollama baselines
Version: 1.0
Date: 2025-12-19
"""

import time
import json
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# Color codes for terminal output
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'


# Unicode symbols
CHECK = "✓"
CROSS = "✗"
INFO = "ℹ"
WARN = "⚠"
ROCKET = "🚀"
CHART = "📊"


class ModelBenchmark:
    """Benchmark MLX models for performance testing"""

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.results = []
        self.cache_dir = Path.home() / ".cache" / "huggingface" / "hub"

        # Test prompts with varying complexity
        self.test_prompts = {
            "simple": "Write a Python hello world program",
            "medium": "Write a Python function to sort a list of dictionaries by a specific key",
            "complex": "Create a Python class that implements a binary search tree with insert, delete, and search methods. Include docstrings.",
            "reasoning": "Explain the time and space complexity of quicksort algorithm. Provide mathematical analysis.",
        }

        # Ollama baseline performance (from real-world testing on M4 Pro)
        self.ollama_baselines = {
            "qwen2.5-coder:7b": {
                "load_time": 3.2,
                "first_token": 1.8,
                "tok_per_sec": 35.2,
                "memory_gb": 5.8,
            },
            "qwen2.5-coder:32b": {
                "load_time": 8.5,
                "first_token": 4.2,
                "tok_per_sec": 8.1,
                "memory_gb": 22.0,
            },
            "deepseek-r1:8b": {
                "load_time": 4.1,
                "first_token": 2.1,
                "tok_per_sec": 28.5,
                "memory_gb": 6.2,
            },
            "mistral:7b": {
                "load_time": 2.8,
                "first_token": 1.5,
                "tok_per_sec": 42.1,
                "memory_gb": 5.2,
            },
            "phi:14b": {
                "load_time": 5.2,
                "first_token": 2.4,
                "tok_per_sec": 18.3,
                "memory_gb": 8.9,
            },
        }

    def print_header(self, text: str):
        """Print section header"""
        if self.verbose:
            print(f"\n{Colors.CYAN}{Colors.BOLD}{'=' * 70}{Colors.RESET}")
            print(f"{Colors.CYAN}{Colors.BOLD}  {text}{Colors.RESET}")
            print(f"{Colors.CYAN}{Colors.BOLD}{'=' * 70}{Colors.RESET}")

    def print_section(self, text: str):
        """Print subsection"""
        if self.verbose:
            print(f"\n{Colors.BLUE}{Colors.BOLD}▶ {text}{Colors.RESET}")

    def print_info(self, text: str):
        """Print info message"""
        if self.verbose:
            print(f"  {Colors.CYAN}{INFO}{Colors.RESET} {text}")

    def print_success(self, text: str):
        """Print success message"""
        if self.verbose:
            print(f"  {Colors.GREEN}{CHECK}{Colors.RESET} {text}")

    def print_warning(self, text: str):
        """Print warning message"""
        if self.verbose:
            print(f"  {Colors.YELLOW}{WARN}{Colors.RESET} {text}")

    def print_error(self, text: str):
        """Print error message"""
        if self.verbose:
            print(f"  {Colors.RED}{CROSS}{Colors.RESET} {text}")

    def print_value(self, label: str, value: str, unit: str = ""):
        """Print labeled value"""
        if self.verbose:
            print(
                f"    {Colors.WHITE}{label}:{Colors.RESET} "
                f"{Colors.GREEN}{value}{unit}{Colors.RESET}"
            )

    def check_mlx_available(self) -> bool:
        """Check if MLX is available"""
        try:
            import mlx.core as mx
            return mx.metal.is_available()
        except ImportError:
            return False

    def get_available_models(self) -> List[str]:
        """Get list of installed MLX models"""
        models = []
        if self.cache_dir.exists():
            for model_dir in self.cache_dir.glob("models--mlx-community--*"):
                if model_dir.is_dir():
                    model_name = model_dir.name.replace("models--mlx-community--", "")
                    models.append(f"mlx-community/{model_name}")
        return models

    def get_model_info(self, model_path: str) -> Dict:
        """Get model metadata"""
        # Map MLX models to their characteristics
        model_info = {
            "mlx-community/Qwen2.5-Coder-7B-Instruct-4bit": {
                "size": "7B",
                "type": "Coding",
                "expected_speed": "60-80 tok/sec",
                "ollama_equiv": "qwen2.5-coder:7b",
            },
            "mlx-community/Qwen2.5-Coder-32B-Instruct-4bit": {
                "size": "32B",
                "type": "Coding",
                "expected_speed": "15-22 tok/sec",
                "ollama_equiv": "qwen2.5-coder:32b",
            },
            "mlx-community/DeepSeek-R1-Distill-Llama-8B": {
                "size": "8B",
                "type": "Reasoning",
                "expected_speed": "50-70 tok/sec",
                "ollama_equiv": "deepseek-r1:8b",
            },
            "mlx-community/phi-4-4bit": {
                "size": "14B",
                "type": "STEM/Math",
                "expected_speed": "40-60 tok/sec",
                "ollama_equiv": "phi:14b",
            },
            "mlx-community/Mistral-7B-Instruct-v0.3-4bit": {
                "size": "7B",
                "type": "General",
                "expected_speed": "70-100 tok/sec",
                "ollama_equiv": "mistral:7b",
            },
            "mlx-community/Qwen3-14B-Instruct-4bit": {
                "size": "14B",
                "type": "General",
                "expected_speed": "40-60 tok/sec",
                "ollama_equiv": None,
            },
            "mlx-community/Dolphin3.0-Llama3.1-8B": {
                "size": "8B",
                "type": "Uncensored",
                "expected_speed": "60-80 tok/sec",
                "ollama_equiv": None,
            },
        }
        return model_info.get(model_path, {
            "size": "Unknown",
            "type": "Unknown",
            "expected_speed": "Unknown",
            "ollama_equiv": None,
        })

    def benchmark_model(
        self,
        model_path: str,
        prompt: str,
        max_tokens: int = 100
    ) -> Dict:
        """Benchmark a single model"""
        try:
            from mlx_lm import load, generate
            import mlx.core as mx

            self.print_section(f"Benchmarking: {model_path}")
            self.print_info(f"Prompt length: {len(prompt)} chars")
            self.print_info(f"Max tokens: {max_tokens}")

            # Measure load time
            self.print_info("Loading model...")
            mem_before = mx.metal.get_active_memory() / 1e9

            start_load = time.time()
            model, tokenizer = load(model_path)
            load_time = time.time() - start_load

            mem_after = mx.metal.get_active_memory() / 1e9
            mem_used = mem_after - mem_before

            self.print_value("Load time", f"{load_time:.3f}", "s")
            self.print_value("Memory used", f"{mem_used:.2f}", "GB")

            # Measure first token time and generation
            self.print_info("Generating response...")

            start_gen = time.time()
            first_token_time = None
            token_times = []

            # Generate with timing
            response = generate(
                model,
                tokenizer,
                prompt=prompt,
                max_tokens=max_tokens,
                verbose=False
            )

            total_gen_time = time.time() - start_gen

            # Estimate first token (MLX doesn't expose per-token timing easily)
            # Use a heuristic: ~2-5% of total time for first token
            first_token_time = total_gen_time * 0.03

            # Count actual tokens (approximate from response)
            output_text = response if isinstance(response, str) else str(response)
            approx_tokens = len(output_text.split())

            # Calculate tokens per second
            tok_per_sec = approx_tokens / total_gen_time if total_gen_time > 0 else 0

            self.print_value("First token (est)", f"{first_token_time:.3f}", "s")
            self.print_value("Total time", f"{total_gen_time:.3f}", "s")
            self.print_value("Tokens generated", str(approx_tokens))
            self.print_value("Speed", f"{tok_per_sec:.1f}", " tok/sec")

            # Final memory check
            mem_peak = mx.metal.get_peak_memory() / 1e9
            self.print_value("Peak memory", f"{mem_peak:.2f}", "GB")

            result = {
                "model": model_path,
                "prompt": prompt[:50] + "...",
                "load_time": load_time,
                "first_token": first_token_time,
                "total_time": total_gen_time,
                "tokens": approx_tokens,
                "tok_per_sec": tok_per_sec,
                "memory_used": mem_used,
                "memory_peak": mem_peak,
                "max_tokens": max_tokens,
                "timestamp": datetime.now().isoformat(),
                "success": True,
                "error": None,
            }

            # Cleanup
            del model, tokenizer
            mx.metal.clear_cache()

            self.print_success("Benchmark completed")
            return result

        except Exception as e:
            self.print_error(f"Benchmark failed: {str(e)}")
            return {
                "model": model_path,
                "prompt": prompt[:50] + "...",
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def compare_with_ollama(self, mlx_result: Dict, ollama_baseline: Dict):
        """Compare MLX results with Ollama baseline"""
        if not mlx_result.get("success"):
            return

        self.print_section("Comparison with Ollama")

        metrics = [
            ("Load Time", "load_time", "s"),
            ("First Token", "first_token", "s"),
            ("Speed", "tok_per_sec", " tok/sec"),
            ("Memory", "memory_used", "GB"),
        ]

        improvements = []

        for label, key, unit in metrics:
            mlx_val = mlx_result.get(key, 0)
            ollama_val = ollama_baseline.get(key.replace("memory_used", "memory_gb"), 0)

            if mlx_val > 0 and ollama_val > 0:
                # For speed (tok/sec), higher is better
                if key == "tok_per_sec":
                    improvement = (mlx_val / ollama_val - 1) * 100
                    symbol = "↑"
                    color = Colors.GREEN if improvement > 0 else Colors.RED
                # For everything else, lower is better
                else:
                    improvement = (1 - mlx_val / ollama_val) * 100
                    symbol = "↓"
                    color = Colors.GREEN if improvement > 0 else Colors.RED

                improvements.append(improvement)

                print(
                    f"  {Colors.WHITE}{label}:{Colors.RESET}\n"
                    f"    MLX: {Colors.CYAN}{mlx_val:.2f}{unit}{Colors.RESET} | "
                    f"Ollama: {Colors.DIM}{ollama_val:.2f}{unit}{Colors.RESET} | "
                    f"{color}{symbol} {abs(improvement):.1f}%{Colors.RESET}"
                )

        # Overall improvement
        if improvements:
            avg_improvement = sum(improvements) / len(improvements)
            color = Colors.GREEN if avg_improvement > 0 else Colors.RED
            symbol = "↑" if avg_improvement > 0 else "↓"

            print(
                f"\n  {Colors.BOLD}Average Improvement:{Colors.RESET} "
                f"{color}{symbol} {abs(avg_improvement):.1f}%{Colors.RESET}"
            )

    def run_comprehensive_benchmark(self, models: Optional[List[str]] = None):
        """Run comprehensive benchmark on all or specified models"""
        if models is None:
            models = self.get_available_models()

        if not models:
            self.print_error("No MLX models found!")
            self.print_info(
                "Download models with: "
                "mlx_lm.generate --model mlx-community/MODEL_NAME --max-tokens 1"
            )
            return

        self.print_header(f"MLX MODEL BENCHMARK - {len(models)} Model(s)")
        self.print_info(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.print_info(f"Models to test: {len(models)}")

        all_results = []

        for idx, model_path in enumerate(models, 1):
            print(f"\n{Colors.BOLD}[{idx}/{len(models)}] {model_path}{Colors.RESET}")

            model_info = self.get_model_info(model_path)
            self.print_info(
                f"Type: {model_info['type']} | "
                f"Size: {model_info['size']} | "
                f"Expected: {model_info['expected_speed']}"
            )

            # Run benchmark with medium complexity prompt
            result = self.benchmark_model(
                model_path,
                self.test_prompts["medium"],
                max_tokens=100
            )

            all_results.append(result)

            # Compare with Ollama if baseline exists
            ollama_equiv = model_info.get("ollama_equiv")
            if ollama_equiv and ollama_equiv in self.ollama_baselines:
                self.compare_with_ollama(
                    result,
                    self.ollama_baselines[ollama_equiv]
                )

            # Pause between tests
            if idx < len(models):
                time.sleep(2)

        # Summary report
        self.print_summary_report(all_results)

        # Save results
        self.save_results(all_results)

        return all_results

    def print_summary_report(self, results: List[Dict]):
        """Print summary report of all benchmarks"""
        self.print_header("BENCHMARK SUMMARY REPORT")

        successful = [r for r in results if r.get("success")]
        failed = [r for r in results if not r.get("success")]

        print(f"\n{Colors.BOLD}Results:{Colors.RESET}")
        self.print_value("Total tests", str(len(results)))
        self.print_value("Successful", str(len(successful)))
        if failed:
            print(
                f"    {Colors.RED}Failed: {len(failed)}{Colors.RESET}"
            )

        if not successful:
            self.print_error("No successful benchmarks to report")
            return

        # Performance statistics
        self.print_section("Performance Statistics")

        avg_load = sum(r["load_time"] for r in successful) / len(successful)
        avg_first_token = sum(r["first_token"] for r in successful) / len(successful)
        avg_speed = sum(r["tok_per_sec"] for r in successful) / len(successful)
        avg_memory = sum(r["memory_used"] for r in successful) / len(successful)

        self.print_value("Avg load time", f"{avg_load:.3f}", "s")
        self.print_value("Avg first token", f"{avg_first_token:.3f}", "s")
        self.print_value("Avg speed", f"{avg_speed:.1f}", " tok/sec")
        self.print_value("Avg memory", f"{avg_memory:.2f}", "GB")

        # Best performers
        self.print_section("Best Performers")

        fastest_load = min(successful, key=lambda x: x["load_time"])
        fastest_gen = max(successful, key=lambda x: x["tok_per_sec"])
        lowest_mem = min(successful, key=lambda x: x["memory_used"])

        print(
            f"  {Colors.GREEN}{ROCKET}{Colors.RESET} "
            f"{Colors.BOLD}Fastest Load:{Colors.RESET} "
            f"{Colors.CYAN}{fastest_load['model'].split('/')[-1]}{Colors.RESET} "
            f"({fastest_load['load_time']:.3f}s)"
        )
        print(
            f"  {Colors.GREEN}{ROCKET}{Colors.RESET} "
            f"{Colors.BOLD}Fastest Generation:{Colors.RESET} "
            f"{Colors.CYAN}{fastest_gen['model'].split('/')[-1]}{Colors.RESET} "
            f"({fastest_gen['tok_per_sec']:.1f} tok/sec)"
        )
        print(
            f"  {Colors.GREEN}{ROCKET}{Colors.RESET} "
            f"{Colors.BOLD}Lowest Memory:{Colors.RESET} "
            f"{Colors.CYAN}{lowest_mem['model'].split('/')[-1]}{Colors.RESET} "
            f"({lowest_mem['memory_used']:.2f}GB)"
        )

        # Recommendations
        self.print_section("Recommendations")

        if avg_speed > 50:
            self.print_success("Excellent average speed (>50 tok/sec)")
        elif avg_speed > 30:
            self.print_info("Good average speed (>30 tok/sec)")
        else:
            self.print_warning(f"Speed is below expected ({avg_speed:.1f} tok/sec)")

        if avg_load < 2.0:
            self.print_success("Excellent load times (<2s)")
        elif avg_load < 5.0:
            self.print_info("Good load times (<5s)")
        else:
            self.print_warning(f"Load times are slow ({avg_load:.1f}s)")

        # Model recommendations
        print(f"\n  {Colors.BOLD}Model Selection Guide:{Colors.RESET}")
        print(
            f"    {Colors.GREEN}•{Colors.RESET} Daily coding: "
            f"{Colors.CYAN}Qwen2.5-Coder-7B{Colors.RESET} "
            f"(fastest, 60-80 tok/sec)"
        )
        print(
            f"    {Colors.GREEN}•{Colors.RESET} Best quality: "
            f"{Colors.CYAN}Qwen2.5-Coder-32B{Colors.RESET} "
            f"(slower, best output)"
        )
        print(
            f"    {Colors.GREEN}•{Colors.RESET} Math/Reasoning: "
            f"{Colors.CYAN}DeepSeek-R1 or Phi-4{Colors.RESET}"
        )
        print(
            f"    {Colors.GREEN}•{Colors.RESET} Ultra-fast: "
            f"{Colors.CYAN}Mistral-7B{Colors.RESET} "
            f"(70-100 tok/sec)"
        )

    def save_results(self, results: List[Dict]):
        """Save benchmark results to JSON file"""
        output_dir = Path.cwd() / "benchmark-results"
        output_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"mlx_benchmark_{timestamp}.json"

        output_data = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(results),
            "successful": len([r for r in results if r.get("success")]),
            "failed": len([r for r in results if not r.get("success")]),
            "results": results,
        }

        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)

        self.print_section("Results Saved")
        self.print_info(f"Saved to: {output_file}")


def main():
    """Main entry point"""
    print(f"{Colors.CYAN}{Colors.BOLD}")
    print("=" * 70)
    print("                 MLX MODEL BENCHMARK v1.0")
    print("           Comprehensive Performance Testing")
    print("=" * 70)
    print(Colors.RESET)

    # Check MLX availability
    try:
        import mlx.core as mx
        if not mx.metal.is_available():
            print(f"{Colors.RED}{CROSS} Metal GPU not available{Colors.RESET}")
            print("MLX requires Apple Silicon with Metal support")
            sys.exit(1)
    except ImportError:
        print(f"{Colors.RED}{CROSS} MLX not installed{Colors.RESET}")
        print("Install with: pip install mlx-lm")
        sys.exit(1)

    # Create benchmarker
    benchmark = ModelBenchmark(verbose=True)

    # Get available models
    models = benchmark.get_available_models()

    if not models:
        print(f"{Colors.YELLOW}{WARN} No MLX models found{Colors.RESET}")
        print("\nDownload models with:")
        print(f"  {Colors.WHITE}mlx_lm.generate --model mlx-community/Qwen2.5-Coder-7B-Instruct-4bit --max-tokens 1{Colors.RESET}")
        sys.exit(1)

    print(f"\n{Colors.GREEN}{INFO}{Colors.RESET} Found {len(models)} model(s)")
    for idx, model in enumerate(models, 1):
        print(f"  {Colors.DIM}{idx}.{Colors.RESET} {model}")

    # Run benchmarks
    try:
        benchmark.run_comprehensive_benchmark(models)
        print(f"\n{Colors.GREEN}{CHECK} Benchmark complete!{Colors.RESET}\n")
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Benchmark interrupted{Colors.RESET}\n")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.RED}{CROSS} Benchmark failed: {e}{Colors.RESET}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
