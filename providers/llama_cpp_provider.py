"""
Llama.cpp Provider
Execute models via llama.cpp in WSL or native Linux
"""

import subprocess
import platform
from pathlib import Path
from typing import Dict, List, Optional, Any, Generator
import json
import os

from .base_provider import LLMProvider, logger


def is_wsl():
    """Detect if running in WSL (Windows Subsystem for Linux)"""
    try:
        with open('/proc/version', 'r') as f:
            return 'microsoft' in f.read().lower()
    except:
        return False


class LlamaCppProvider(LLMProvider):
    """
    Provider for llama.cpp execution.

    Supports:
    - Local GGUF models
    - WSL execution on Windows
    - Native Linux/macOS execution
    - Full parameter customization
    - System prompts
    - Streaming responses
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize llama.cpp provider.

        Config keys:
            - llama_cpp_path: Path to llama.cpp binary (default: ~/llama.cpp/build/bin/llama-cli)
            - models_dir: Directory containing GGUF models
            - use_wsl: Force WSL mode (auto-detected by default)
            - default_threads: Number of CPU threads (default: 24)
            - default_gpu_layers: Number of GPU layers (default: 999 for full offload)
        """
        super().__init__(config)

        # Detect platform
        self.platform = platform.system()
        self.use_wsl = config.get('use_wsl', is_wsl() or self.platform == "Windows")

        # Set paths
        self.llama_cpp_path = config.get(
            'llama_cpp_path',
            '~/llama.cpp/build/bin/llama-cli'
        )

        # Models directory
        if 'models_dir' in config:
            self.models_dir = Path(config['models_dir'])
        elif self.use_wsl or self.platform == "Windows":
            self.models_dir = Path("/mnt/d/models/organized")
        else:
            self.models_dir = Path.home() / "models"

        # Default parameters
        self.default_threads = config.get('default_threads', 24)
        self.default_gpu_layers = config.get('default_gpu_layers', 999)

        logger.info(f"Llama.cpp provider initialized: WSL={self.use_wsl}, models_dir={self.models_dir}")

    def list_models(self) -> List[Dict[str, Any]]:
        """
        List all available GGUF models in models directory.

        Returns:
            List of model dictionaries with metadata
        """
        models = []

        if not self.models_dir.exists():
            logger.warning(f"Models directory not found: {self.models_dir}")
            return models

        # Find all .gguf files
        for model_file in self.models_dir.glob("*.gguf"):
            try:
                # Get file size
                size_bytes = model_file.stat().st_size
                size_gb = size_bytes / (1024**3)

                # Extract model name
                name = model_file.stem

                models.append({
                    "id": name,
                    "name": name,
                    "path": str(model_file),
                    "size": f"{size_gb:.1f}GB",
                    "size_bytes": size_bytes,
                    "description": f"Local GGUF model: {name}",
                    "context_length": 32768,  # Default, can be overridden
                    "framework": "llama.cpp"
                })
            except Exception as e:
                logger.warning(f"Error reading model {model_file}: {e}")

        logger.info(f"Found {len(models)} GGUF models")
        return sorted(models, key=lambda x: x['name'])

    def execute(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Execute model and return complete response.

        Args:
            model: Model path or identifier
            prompt: User prompt
            system_prompt: Optional system prompt
            parameters: Execution parameters

        Returns:
            Complete model response
        """
        # Build command
        cmd = self._build_command(model, prompt, system_prompt, parameters, stream=False)

        logger.info(f"Executing llama.cpp command")
        logger.debug(f"Command: {cmd}")

        # Execute
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=parameters.get('timeout', 600) if parameters else 600
            )

            if result.returncode != 0:
                error_msg = f"llama.cpp execution failed: {result.stderr}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)

            return result.stdout

        except subprocess.TimeoutExpired:
            raise RuntimeError("Model execution timed out")
        except Exception as e:
            raise RuntimeError(f"Execution error: {str(e)}")

    def stream_execute(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Generator[str, None, None]:
        """
        Execute model with streaming response.

        Args:
            model: Model path or identifier
            prompt: User prompt
            system_prompt: Optional system prompt
            parameters: Execution parameters

        Yields:
            Response chunks as they are generated
        """
        # Build command
        cmd = self._build_command(model, prompt, system_prompt, parameters, stream=True)

        logger.info(f"Executing llama.cpp command (streaming)")
        logger.debug(f"Command: {cmd}")

        # Execute with streaming
        try:
            process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )

            # Stream output line by line
            for line in process.stdout:
                yield line

            # Wait for completion
            process.wait()

            if process.returncode != 0:
                error_msg = process.stderr.read() if process.stderr else "Unknown error"
                logger.error(f"llama.cpp execution failed: {error_msg}")
                raise RuntimeError(f"Execution failed: {error_msg}")

        except Exception as e:
            raise RuntimeError(f"Streaming execution error: {str(e)}")

    def _build_command(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        stream: bool = False
    ) -> str:
        """
        Build llama.cpp command with optimal parameters.

        Args:
            model: Model path or identifier
            prompt: User prompt
            system_prompt: Optional system prompt
            parameters: Execution parameters
            stream: Enable streaming output

        Returns:
            Complete command string
        """
        params = parameters or {}

        # Resolve model path
        model_path = self._resolve_model_path(model)

        # Extract parameters with defaults
        temperature = params.get('temperature', 0.7)
        top_p = params.get('top_p', 0.9)
        top_k = params.get('top_k', 40)
        context = params.get('context', 32768)
        max_tokens = params.get('max_tokens', 2048)
        threads = params.get('threads', self.default_threads)
        gpu_layers = params.get('gpu_layers', self.default_gpu_layers)
        batch_size = params.get('batch_size', 512)
        ubatch_size = params.get('ubatch_size', 512)

        # Special flags
        special_flags = params.get('special_flags', [])
        if isinstance(special_flags, str):
            special_flags = [special_flags]

        # Build base command
        cmd_parts = [
            f"{self.llama_cpp_path}",
            f"-m '{model_path}'",
            f"-p '{prompt}'",
            f"-ngl {gpu_layers}",
            f"-t {threads}",
            f"-b {batch_size}",
            f"-ub {ubatch_size}",
            f"-fa 1",  # Flash Attention
            "--cache-type-k q8_0",
            "--cache-type-v q8_0",
            f"--temp {temperature}",
            f"--top-p {top_p}",
            f"--top-k {top_k}",
            f"-c {context}",
            f"-n {max_tokens}",
            "-ptc 10",
            "--verbose-prompt",
            "--log-colors auto",
            "--mlock"
        ]

        # Add system prompt if provided
        if system_prompt:
            cmd_parts.insert(2, f"--system-prompt '{system_prompt}'")

        # Add special flags
        for flag in special_flags:
            if flag and flag not in cmd_parts:
                cmd_parts.append(flag)

        # Join command
        cmd = " \\\n  ".join(cmd_parts)

        # Wrap in WSL if needed
        if self.use_wsl and self.platform == "Windows":
            cmd = f'wsl bash -c "{cmd}"'

        return cmd

    def _resolve_model_path(self, model: str) -> str:
        """
        Resolve model identifier to full path.

        Args:
            model: Model path or identifier

        Returns:
            Full path to model file
        """
        # If absolute path, use as-is
        if os.path.isabs(model) or model.startswith('/mnt/'):
            return model

        # If relative path with .gguf, search in models_dir
        if model.endswith('.gguf'):
            model_path = self.models_dir / model
            if model_path.exists():
                return str(model_path)

        # Search for model by name
        for ext in ['.gguf', '-Q4_K_M.gguf', '-Q6_K.gguf', '-Q5_K_M.gguf']:
            model_path = self.models_dir / f"{model}{ext}"
            if model_path.exists():
                return str(model_path)

        # Return as-is and let llama.cpp handle the error
        logger.warning(f"Model not found: {model}, using as-is")
        return model

    def validate_config(self) -> bool:
        """
        Validate llama.cpp configuration.

        Returns:
            True if llama.cpp is accessible and models directory exists
        """
        try:
            # Check llama.cpp binary
            test_cmd = f"{self.llama_cpp_path} --help"
            if self.use_wsl and self.platform == "Windows":
                test_cmd = f'wsl bash -c "{test_cmd}"'

            result = subprocess.run(
                test_cmd,
                shell=True,
                capture_output=True,
                timeout=5
            )

            if result.returncode != 0:
                logger.error(f"llama.cpp binary not accessible: {self.llama_cpp_path}")
                return False

            # Check models directory
            if not self.models_dir.exists():
                logger.error(f"Models directory not found: {self.models_dir}")
                return False

            logger.info("llama.cpp configuration validated successfully")
            return True

        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False

    def get_info(self) -> Dict[str, Any]:
        """
        Get llama.cpp provider information.

        Returns:
            Provider metadata and status
        """
        # Count available models
        models = self.list_models()

        return {
            "name": "llama.cpp",
            "version": "unknown",  # Could parse from --help
            "status": "online" if self.validate_config() else "offline",
            "platform": self.platform,
            "use_wsl": self.use_wsl,
            "llama_cpp_path": self.llama_cpp_path,
            "models_dir": str(self.models_dir),
            "available_models": len(models),
            "capabilities": [
                "streaming",
                "system_prompts",
                "local_execution",
                "gpu_offload",
                "flash_attention",
                "kv_cache_quantization"
            ],
            "limits": {
                "max_context": 262144,  # Ministral-3 max
                "gpu_memory": "depends_on_hardware"
            }
        }

    def normalize_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize parameters for llama.cpp.

        Maps common parameter names to llama.cpp equivalents.
        """
        normalized = {}

        # Temperature
        if 'temp' in parameters:
            normalized['temperature'] = parameters['temp']
        elif 'temperature' in parameters:
            normalized['temperature'] = parameters['temperature']

        # Top-p
        if 'top_p' in parameters:
            normalized['top_p'] = parameters['top_p']
        elif 'nucleus_sampling' in parameters:
            normalized['top_p'] = parameters['nucleus_sampling']

        # Top-k
        if 'top_k' in parameters:
            normalized['top_k'] = parameters['top_k']

        # Context length
        if 'context_length' in parameters:
            normalized['context'] = parameters['context_length']
        elif 'context' in parameters:
            normalized['context'] = parameters['context']
        elif 'ctx_size' in parameters:
            normalized['context'] = parameters['ctx_size']

        # Max tokens
        if 'max_length' in parameters:
            normalized['max_tokens'] = parameters['max_length']
        elif 'max_tokens' in parameters:
            normalized['max_tokens'] = parameters['max_tokens']

        # Copy other parameters as-is
        for key, value in parameters.items():
            if key not in ['temp', 'nucleus_sampling', 'context_length', 'ctx_size', 'max_length']:
                if key not in normalized:
                    normalized[key] = value

        return normalized
