#!/usr/bin/env python3
"""
MLX Environment Setup and Validation Script

This script handles Python-side setup and validation for MLX:
- Verifies MLX installation
- Tests Metal GPU support
- Validates compute capabilities
- Downloads test models if needed
- Runs performance benchmarks

Usage:
    python3 setup_mlx_environment.py --validate
    python3 setup_mlx_environment.py --benchmark
    python3 setup_mlx_environment.py --install-models
"""

import sys
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class Colors:
    """ANSI color codes for terminal output"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    CYAN = '\033[36m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_RED = '\033[91m'


class MLXValidator:
    """Validates MLX installation and environment"""

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.success_count = 0
        self.total_checks = 0

    def print_header(self, text: str) -> None:
        """Print a formatted header"""
        if not self.verbose:
            return
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 64}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BLUE}  {text}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 64}{Colors.RESET}\n")

    def print_success(self, text: str) -> None:
        """Print success message"""
        if self.verbose:
            print(f"{Colors.GREEN}✓{Colors.RESET} {text}")
        self.success_count += 1

    def print_error(self, text: str) -> None:
        """Print error message"""
        if self.verbose:
            print(f"{Colors.RED}✗{Colors.RESET} {text}")
        self.errors.append(text)

    def print_warning(self, text: str) -> None:
        """Print warning message"""
        if self.verbose:
            print(f"{Colors.YELLOW}⚠{Colors.RESET} {text}")
        self.warnings.append(text)

    def print_info(self, text: str) -> None:
        """Print info message"""
        if self.verbose:
            print(f"{Colors.CYAN}ℹ{Colors.RESET} {text}")

    def print_step(self, text: str) -> None:
        """Print step message"""
        if self.verbose:
            print(f"\n{Colors.BOLD}→ {text}{Colors.RESET}")

    def check_import(self, module_name: str, import_path: str) -> bool:
        """Check if a module can be imported"""
        self.total_checks += 1
        try:
            __import__(import_path)
            self.print_success(f"{module_name} imported successfully")
            return True
        except ImportError as e:
            self.print_error(f"Failed to import {module_name}: {e}")
            return False

    def check_mlx_core(self) -> bool:
        """Validate MLX core installation"""
        self.print_step("Checking MLX Core")

        if not self.check_import("MLX core", "mlx.core"):
            return False

        try:
            import mlx.core as mx

            # Check version
            version = getattr(mx, '__version__', 'unknown')
            self.print_info(f"MLX version: {version}")

            # Check default device
            device = mx.default_device()
            self.print_info(f"Default device: {device}")

            # Test basic operation
            self.total_checks += 1
            arr = mx.array([1, 2, 3, 4])
            result = mx.sum(arr)
            if result.item() == 10:
                self.print_success("Basic MLX operations working")
            else:
                self.print_error(f"MLX computation incorrect: expected 10, got {result.item()}")
                return False

            return True

        except Exception as e:
            self.print_error(f"MLX core validation failed: {e}")
            return False

    def check_metal_support(self) -> bool:
        """Check Metal GPU support"""
        self.print_step("Checking Metal GPU Support")

        try:
            import mlx.core as mx

            # Check if Metal is available
            self.total_checks += 1
            device = mx.default_device()
            device_str = str(device)

            if 'gpu' in device_str.lower() or 'metal' in device_str.lower():
                self.print_success(f"Metal GPU detected: {device}")
            else:
                self.print_warning(f"GPU not detected. Device: {device}")
                self.print_info("MLX will use CPU fallback (slower)")

            # Test GPU computation
            self.total_checks += 1
            try:
                # Create a larger array to ensure GPU usage
                arr = mx.random.normal(shape=(1000, 1000))
                result = mx.sum(arr * arr)
                mx.eval(result)  # Force evaluation
                self.print_success("GPU computation test passed")
            except Exception as e:
                self.print_warning(f"GPU computation test failed: {e}")

            return True

        except Exception as e:
            self.print_error(f"Metal support check failed: {e}")
            return False

    def check_mlx_lm(self) -> bool:
        """Validate mlx-lm installation"""
        self.print_step("Checking mlx-lm")

        if not self.check_import("mlx-lm", "mlx_lm"):
            return False

        try:
            import mlx_lm

            # Check for key functions
            self.total_checks += 1
            if hasattr(mlx_lm, 'load'):
                self.print_success("mlx-lm.load available")
            else:
                self.print_warning("mlx-lm.load not found")

            self.total_checks += 1
            if hasattr(mlx_lm, 'generate'):
                self.print_success("mlx-lm.generate available")
            else:
                self.print_warning("mlx-lm.generate not found")

            return True

        except Exception as e:
            self.print_error(f"mlx-lm validation failed: {e}")
            return False

    def check_dependencies(self) -> bool:
        """Check required dependencies"""
        self.print_step("Checking Dependencies")

        dependencies = [
            ("NumPy", "numpy"),
            ("Transformers", "transformers"),
            ("Hugging Face Hub", "huggingface_hub"),
        ]

        all_ok = True
        for name, module in dependencies:
            if not self.check_import(name, module):
                all_ok = False

        return all_ok

    def check_system_info(self) -> None:
        """Display system information"""
        self.print_step("System Information")

        try:
            import platform
            import mlx.core as mx

            self.print_info(f"OS: {platform.system()} {platform.release()}")
            self.print_info(f"Architecture: {platform.machine()}")
            self.print_info(f"Python: {sys.version.split()[0]}")
            self.print_info(f"MLX Version: {getattr(mx, '__version__', 'unknown')}")
            self.print_info(f"Device: {mx.default_device()}")

            # Check memory
            try:
                import subprocess
                result = subprocess.run(
                    ['sysctl', 'hw.memsize'],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    mem_bytes = int(result.stdout.split(':')[1].strip())
                    mem_gb = mem_bytes / (1024 ** 3)
                    self.print_info(f"Total RAM: {mem_gb:.1f} GB")
            except:
                pass

        except Exception as e:
            self.print_warning(f"Could not gather system info: {e}")

    def run_performance_test(self) -> Optional[float]:
        """Run a simple performance test"""
        self.print_step("Running Performance Test")

        try:
            import mlx.core as mx
            import time

            # Matrix multiplication benchmark
            size = 2048
            self.print_info(f"Testing {size}x{size} matrix multiplication...")

            # Warmup
            a = mx.random.normal(shape=(size, size))
            b = mx.random.normal(shape=(size, size))
            _ = mx.matmul(a, b)
            mx.eval(_)

            # Actual benchmark
            iterations = 10
            start_time = time.time()

            for _ in range(iterations):
                a = mx.random.normal(shape=(size, size))
                b = mx.random.normal(shape=(size, size))
                c = mx.matmul(a, b)
                mx.eval(c)

            elapsed = time.time() - start_time
            avg_time = elapsed / iterations

            self.print_success(f"Average time: {avg_time * 1000:.2f}ms per iteration")
            self.print_info(f"Performance: {(2 * size**3) / (avg_time * 1e9):.2f} GFLOPS")

            return avg_time

        except Exception as e:
            self.print_error(f"Performance test failed: {e}")
            return None

    def validate_all(self) -> bool:
        """Run all validation checks"""
        self.print_header("MLX Environment Validation")

        # Run checks
        self.check_system_info()
        core_ok = self.check_mlx_core()
        metal_ok = self.check_metal_support()
        lm_ok = self.check_mlx_lm()
        deps_ok = self.check_dependencies()

        # Print summary
        self.print_header("Validation Summary")

        print(f"{Colors.BOLD}Results:{Colors.RESET}")
        print(f"  Checks passed: {Colors.GREEN}{self.success_count}/{self.total_checks}{Colors.RESET}")

        if self.errors:
            print(f"\n{Colors.RED}{Colors.BOLD}Errors ({len(self.errors)}):{Colors.RESET}")
            for error in self.errors:
                print(f"  {Colors.RED}•{Colors.RESET} {error}")

        if self.warnings:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}Warnings ({len(self.warnings)}):{Colors.RESET}")
            for warning in self.warnings:
                print(f"  {Colors.YELLOW}•{Colors.RESET} {warning}")

        # Overall status
        print()
        all_critical_ok = core_ok and lm_ok and deps_ok

        if all_critical_ok and not self.errors:
            print(f"{Colors.BRIGHT_GREEN}{Colors.BOLD}✓ MLX environment is fully functional!{Colors.RESET}")
            return True
        elif all_critical_ok:
            print(f"{Colors.YELLOW}{Colors.BOLD}⚠ MLX environment functional with warnings{Colors.RESET}")
            return True
        else:
            print(f"{Colors.BRIGHT_RED}{Colors.BOLD}✗ MLX environment has errors{Colors.RESET}")
            print(f"\n{Colors.YELLOW}Fix the errors above and run validation again.{Colors.RESET}")
            return False


class MLXModelManager:
    """Manage MLX model downloads and setup"""

    RECOMMENDED_MODELS = {
        "qwen25-coder-7b": {
            "name": "Qwen2.5 Coder 7B",
            "path": "mlx-community/Qwen2.5-Coder-7B-Instruct-4bit",
            "size": "4.5GB",
            "description": "Fast coding model (60-80 tok/sec)",
        },
        "deepseek-r1-8b": {
            "name": "DeepSeek-R1 8B",
            "path": "mlx-community/DeepSeek-R1-Distill-Llama-8B",
            "size": "4.5GB",
            "description": "Reasoning specialist (50-70 tok/sec)",
        },
        "phi4-14b": {
            "name": "Phi-4 14B",
            "path": "mlx-community/phi-4-4bit",
            "size": "8-9GB",
            "description": "Math and coding (40-60 tok/sec)",
        },
    }

    def __init__(self, models_path: Optional[Path] = None):
        self.models_path = models_path or Path.home() / "workspace" / "mlx"
        self.models_path.mkdir(parents=True, exist_ok=True)

    def list_models(self) -> None:
        """List recommended models"""
        print(f"\n{Colors.BOLD}Recommended MLX Models:{Colors.RESET}\n")

        for key, info in self.RECOMMENDED_MODELS.items():
            print(f"{Colors.CYAN}{info['name']}{Colors.RESET}")
            print(f"  ID: {key}")
            print(f"  Path: {info['path']}")
            print(f"  Size: {info['size']}")
            print(f"  Description: {info['description']}")
            print()

    def download_model(self, model_id: str) -> bool:
        """Download a model using mlx-lm"""
        if model_id not in self.RECOMMENDED_MODELS:
            print(f"{Colors.RED}Unknown model ID: {model_id}{Colors.RESET}")
            return False

        model_info = self.RECOMMENDED_MODELS[model_id]
        print(f"\n{Colors.BOLD}Downloading {model_info['name']}...{Colors.RESET}")
        print(f"Size: {model_info['size']}")
        print(f"This may take several minutes...\n")

        try:
            # Use huggingface-cli to download
            subprocess.run(
                [
                    "huggingface-cli",
                    "download",
                    model_info["path"],
                    "--local-dir",
                    str(self.models_path / model_id),
                ],
                check=True,
            )
            print(f"{Colors.GREEN}✓ Download complete!{Colors.RESET}")
            return True

        except subprocess.CalledProcessError as e:
            print(f"{Colors.RED}✗ Download failed: {e}{Colors.RESET}")
            return False
        except FileNotFoundError:
            print(f"{Colors.RED}✗ huggingface-cli not found{Colors.RESET}")
            print(f"Install with: pip install huggingface-hub[cli]")
            return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="MLX Environment Setup and Validation"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Run full validation suite"
    )
    parser.add_argument(
        "--benchmark",
        action="store_true",
        help="Run performance benchmark"
    )
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="List recommended models"
    )
    parser.add_argument(
        "--download-model",
        type=str,
        metavar="MODEL_ID",
        help="Download a recommended model"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Minimal output"
    )

    args = parser.parse_args()

    # Default to validation if no args
    if not any([args.validate, args.benchmark, args.list_models, args.download_model]):
        args.validate = True

    validator = MLXValidator(verbose=not args.quiet)

    # Run requested operations
    if args.validate:
        success = validator.validate_all()
        sys.exit(0 if success else 1)

    if args.benchmark:
        validator.print_header("MLX Performance Benchmark")
        validator.check_system_info()
        validator.run_performance_test()

    if args.list_models:
        manager = MLXModelManager()
        manager.list_models()

    if args.download_model:
        manager = MLXModelManager()
        success = manager.download_model(args.download_model)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
