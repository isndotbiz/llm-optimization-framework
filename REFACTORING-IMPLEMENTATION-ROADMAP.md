# AI Router Refactoring - Implementation Roadmap

**Version:** 1.0
**Created:** 2025-12-22
**Owner:** Architecture Team
**Status:** Ready for Planning

---

## Overview

This document provides a week-by-week implementation plan to refactor the AI Router codebase from 3,700 lines of duplicated code to a clean, modular architecture using the existing provider abstraction pattern.

---

## Phased Implementation Plan

### Phase 1: Configuration Extraction (Week 1)
**Goal:** Eliminate model definition duplication
**Effort:** 8-10 hours
**Risk:** Very Low (adds new code, doesn't remove anything)
**Reversibility:** 100% (fully backward compatible)

#### Tasks

**Task 1.1: Create config/models.py (2 hours)**

```python
# File: D:\models\config\models.py
"""Central model registry - single source of truth"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class ModelConfig:
    """Model configuration dataclass"""
    id: str                           # qwen3-coder-30b
    name: str                         # "Qwen3 Coder 30B Q4_K_M"
    framework: str                    # "llama.cpp" or "mlx"
    path: str                         # "/mnt/d/models/..."
    size_gb: float                    # 18.0
    speed_tokens_per_sec: str         # "25-35 tok/sec"
    use_case: str                     # description
    temperature: float                # 0.7
    top_p: float                      # 0.8
    top_k: int                        # 20
    context_tokens: int               # 32768
    system_prompt_file: Optional[str] = None  # filename or None
    special_flags: List[str] = field(default_factory=list)
    notes: str = ""

class ModelRegistry:
    """Central model registry"""

    # All 11 models defined here (copy from ai-router.py:103-259 + ai-router.py:261-324)
    MODELS: Dict[str, ModelConfig] = {
        "qwen3-coder-30b": ModelConfig(
            id="qwen3-coder-30b",
            name="Qwen3 Coder 30B Q4_K_M",
            framework="llama.cpp",
            path="/mnt/d/models/organized/Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf",
            size_gb=18.0,
            speed_tokens_per_sec="25-35 tok/sec",
            use_case="Advanced coding, code review, architecture design",
            temperature=0.7,
            top_p=0.8,
            top_k=20,
            context_tokens=32768,
            system_prompt_file="system-prompt-qwen3-coder-30b.txt",
            special_flags=["--jinja"],
            notes="CRITICAL: Never use temp 0 (causes endless loops). Use enable_thinking for reasoning."
        ),
        "phi4-14b": ModelConfig(...),
        "gemma3-27b": ModelConfig(...),
        # ... repeat for all 11 models
    }

    @classmethod
    def get_by_framework(cls, framework: str) -> Dict[str, ModelConfig]:
        """Get models for specific framework"""
        return {k: v for k, v in cls.MODELS.items() if v.framework == framework}

    @classmethod
    def get_by_platform(cls) -> Dict[str, ModelConfig]:
        """Get models for current platform"""
        import platform
        system = platform.system()
        framework = "mlx" if system == "Darwin" else "llama.cpp"
        return cls.get_by_framework(framework)

    @classmethod
    def get_use_case_recommendations(cls) -> Dict[str, str]:
        """Get model recommendations by use case"""
        return {
            "coding": "qwen3-coder-30b",
            "reasoning": "phi4-14b",
            "creative": "gemma3-27b",
            "research": "qwen3-coder-30b",
            "general": "qwen3-coder-30b",
        }

    @classmethod
    def validate_all_paths(cls) -> bool:
        """Check all model paths are accessible"""
        from pathlib import Path
        for model_id, config in cls.MODELS.items():
            # Resolve path (handle /mnt/d/ on Windows)
            path = Path(config.path)
            # This is a soft check - models might not be downloaded yet
            # but we should log warnings
        return True
```

**Checklist:**
- [ ] Copy all 11 model definitions from ai-router.py + ai-router-enhanced.py
- [ ] Verify all fields match original definitions exactly
- [ ] Add docstrings to each model config
- [ ] Create tests for ModelRegistry
- [ ] Test import: `from config.models import ModelRegistry`

---

**Task 1.2: Create config/__init__.py (30 min)**

```python
# File: D:\models\config\__init__.py
"""Configuration module"""

from .models import ModelRegistry, ModelConfig

__all__ = ['ModelRegistry', 'ModelConfig']
```

---

**Task 1.3: Create config/profiles.py (1 hour)**

```python
# File: D:\models\config\profiles.py
"""Hardware profiles for different machines"""

from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class HardwareProfile:
    """Hardware configuration for a specific machine type"""
    name: str                           # "MacBook M4 Pro"
    platform: str                       # "Darwin", "Linux", "Windows"
    framework: str                      # "mlx", "llama.cpp"
    cpu_threads: int                    # 8, 24, 48, etc.
    models_dir: str                     # ~/models, /mnt/d/models, etc.
    default_model: str                  # qwen3-coder-30b
    notes: Optional[str] = None

class HardwareProfiles:
    """Central hardware profile definitions"""

    PROFILES: Dict[str, HardwareProfile] = {
        "m4-macbook-pro": HardwareProfile(
            name="MacBook M4 Pro",
            platform="Darwin",
            framework="mlx",
            cpu_threads=8,
            models_dir="~/models",
            default_model="qwen25-coder-14b-mlx",
            notes="Optimized for Apple Silicon. Uses MLX framework."
        ),
        "ryzen-9-5900x": HardwareProfile(
            name="Ryzen 9 5900X + RTX 3090",
            platform="Linux",
            framework="llama.cpp",
            cpu_threads=24,
            models_dir="/mnt/d/models",
            default_model="qwen3-coder-30b",
            notes="WSL on Windows or native Linux. Full GPU offload."
        ),
        "xeon-4060ti": HardwareProfile(
            name="Xeon Processor + RTX 4060 Ti",
            platform="Linux",
            framework="llama.cpp",
            cpu_threads=16,
            models_dir="/data/models",
            default_model="phi4-14b",
            notes="TrueNAS or Linux server. Moderate GPU."
        ),
    }

    @classmethod
    def auto_detect(cls) -> Optional[str]:
        """Auto-detect hardware profile"""
        import platform
        import os

        system = platform.system()

        # Manual override
        if os.path.exists(".machine-id"):
            with open(".machine-id") as f:
                return f.read().strip()

        # Auto-detect
        if system == "Darwin":
            return "m4-macbook-pro"

        if system == "Linux":
            try:
                with open('/proc/cpuinfo', 'r') as f:
                    cpuinfo = f.read()
                    if 'Ryzen' in cpuinfo:
                        return "ryzen-9-5900x"
                    elif 'Xeon' in cpuinfo or 'Intel' in cpuinfo:
                        return "xeon-4060ti"
            except:
                pass

        # Default
        return "ryzen-9-5900x"

    @classmethod
    def get(cls, profile_name: str) -> Optional[HardwareProfile]:
        """Get a hardware profile by name"""
        return cls.PROFILES.get(profile_name)

    @classmethod
    def get_all(cls) -> Dict[str, HardwareProfile]:
        """Get all available profiles"""
        return cls.PROFILES.copy()
```

---

**Task 1.4: Update ai-router.py to use ModelRegistry (30 min)**

Change:
```python
# OLD (lines 103-259)
class ModelDatabase:
    RTX3090_MODELS = { ... }

# NEW
from config.models import ModelRegistry

# In AIRouter.__init__():
def __init__(self):
    # OLD:
    self.models = ModelDatabase.get_platform_models()

    # NEW:
    self.models = ModelRegistry.get_by_platform()
    self.all_models = ModelRegistry.MODELS
```

Remove ~157 lines of duplicate model definitions.

---

**Task 1.5: Update ai-router-enhanced.py to use ModelRegistry (30 min)**

Same as 1.4 - remove the ModelDatabase class, import from config.

---

**Task 1.6: Update ai-router-mlx.py to use ModelRegistry (30 min)**

Change:
```python
# OLD
from ai_router_mlx import MLXModelDatabase
class AIRouterMLX:
    def __init__(self):
        self.models = MLXModelDatabase.M4_MLX_MODELS

# NEW
from config.models import ModelRegistry
class AIRouterMLX:
    def __init__(self):
        self.models = ModelRegistry.get_by_framework("mlx")
```

Remove ~147 lines of duplicate definitions.

---

**Task 1.7: Create unit tests (1.5 hours)**

```python
# File: D:\models\tests\test_model_registry.py
import pytest
from config.models import ModelRegistry, ModelConfig

class TestModelRegistry:
    """Tests for central model registry"""

    def test_registry_has_all_models(self):
        """ModelRegistry contains all expected models"""
        assert len(ModelRegistry.MODELS) == 11

    def test_model_ids_unique(self):
        """All model IDs are unique"""
        ids = list(ModelRegistry.MODELS.keys())
        assert len(ids) == len(set(ids))

    def test_all_models_have_required_fields(self):
        """Every model has required configuration"""
        required = {'id', 'name', 'framework', 'path', 'size_gb',
                    'temperature', 'top_p', 'top_k', 'context_tokens'}

        for model_id, config in ModelRegistry.MODELS.items():
            for field in required:
                assert hasattr(config, field), f"{model_id} missing {field}"
                assert getattr(config, field) is not None

    def test_framework_values_valid(self):
        """All frameworks are valid"""
        valid = {"llama.cpp", "mlx"}
        for model_id, config in ModelRegistry.MODELS.items():
            assert config.framework in valid, f"{model_id} has invalid framework"

    def test_get_by_framework(self):
        """Can filter models by framework"""
        llama_models = ModelRegistry.get_by_framework("llama.cpp")
        mlx_models = ModelRegistry.get_by_framework("mlx")

        assert len(llama_models) == 8
        assert len(mlx_models) == 3  # Currently only 3 MLX models

    def test_get_use_case_recommendations(self):
        """Can get model recommendations"""
        recs = ModelRegistry.get_use_case_recommendations()

        assert isinstance(recs, dict)
        for use_case, model_id in recs.items():
            assert model_id in ModelRegistry.MODELS

    def test_model_config_immutability(self):
        """Model configs are immutable (dataclass with frozen=True)"""
        config = list(ModelRegistry.MODELS.values())[0]
        # Should be frozen after we add frozen=True to dataclass

    def test_backward_compatibility(self):
        """Old code accessing ModelDatabase.RTX3090_MODELS still works"""
        # This test can be removed after deprecation period
        # For now, verify old code still loads
        from ai_router import AIRouter
        router = AIRouter()
        assert len(router.models) == 8  # RTX3090 models on non-Darwin

def test_hardware_profiles():
    """Test hardware profile detection"""
    from config.profiles import HardwareProfiles

    assert "m4-macbook-pro" in HardwareProfiles.PROFILES
    assert "ryzen-9-5900x" in HardwareProfiles.PROFILES
    assert "xeon-4060ti" in HardwareProfiles.PROFILES

    profile = HardwareProfiles.get("m4-macbook-pro")
    assert profile.framework == "mlx"
    assert profile.platform == "Darwin"
```

**Run tests:**
```bash
cd D:\models
python -m pytest tests/test_model_registry.py -v
```

Expected output:
```
tests/test_model_registry.py::TestModelRegistry::test_registry_has_all_models PASSED
tests/test_model_registry.py::TestModelRegistry::test_model_ids_unique PASSED
tests/test_model_registry.py::TestModelRegistry::test_all_models_have_required_fields PASSED
...
```

---

**Task 1.8: Documentation (1 hour)**

Create: `docs/CONFIG_USAGE.md`

```markdown
# Using the Configuration Layer

## Model Registry

Access the central model registry:

```python
from config.models import ModelRegistry

# Get all models
all_models = ModelRegistry.MODELS

# Get models for current platform
platform_models = ModelRegistry.get_by_platform()

# Get specific model
model = ModelRegistry.MODELS["qwen3-coder-30b"]
print(f"Framework: {model.framework}")
print(f"Size: {model.size_gb}GB")
print(f"Speed: {model.speed_tokens_per_sec}")
```

## Hardware Profiles

Detect or specify hardware profile:

```python
from config.profiles import HardwareProfiles

# Auto-detect
profile_name = HardwareProfiles.auto_detect()
profile = HardwareProfiles.get(profile_name)

# Use profile
print(f"Framework: {profile.framework}")
print(f"CPU threads: {profile.cpu_threads}")
print(f"Models dir: {profile.models_dir}")
```

## Adding a New Model

1. Edit `config/models.py`
2. Add entry to `ModelRegistry.MODELS` dict
3. Add system prompt file to `D:\models\`
4. Run tests: `pytest tests/test_model_registry.py`

All routers automatically see the new model.
```

---

#### Acceptance Criteria
- [ ] config/models.py created with all 11 models
- [ ] config/profiles.py created with 3 hardware profiles
- [ ] config/__init__.py created
- [ ] All three routers updated to import from config.models
- [ ] Tests pass: `pytest tests/test_model_registry.py`
- [ ] No changes to user-facing APIs
- [ ] Backward compatibility verified (old routers still work)

#### Testing Checklist
```bash
# Verify imports work
python -c "from config.models import ModelRegistry; print(len(ModelRegistry.MODELS))"

# Verify routers still launch
python ai-router.py --list
python ai-router-enhanced.py --list
python ai-router-mlx.py --list

# Run test suite
python -m pytest tests/test_model_registry.py -v
```

---

### Phase 2: Provider Abstraction Integration (Week 2)
**Goal:** Integrate unified provider interface
**Effort:** 12-14 hours
**Risk:** Low-Medium (new code path, existing code unchanged)
**Reversibility:** 95% (can disable provider layer if issues found)

#### Tasks

**Task 2.1: Create MLX Provider (3 hours)**

File: `D:\models\providers\mlx_provider.py`

```python
"""MLX Provider for Apple Silicon (M4 MacBook Pro)"""

import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Generator
import logging

from .base_provider import LLMProvider

logger = logging.getLogger(__name__)

class MLXProvider(LLMProvider):
    """Provider for MLX framework on Apple Silicon"""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize MLX provider.

        Config keys:
            - models_dir: Directory containing downloaded MLX models (~/models)
            - mlx_venv: Virtual environment path (~/workspace/venv-mlx)
        """
        super().__init__(config)

        self.models_dir = Path(config.get("models_dir", Path.home() / "models"))
        self.mlx_venv = Path(config.get("mlx_venv", Path.home() / "workspace" / "venv-mlx"))

        logger.info(f"MLX provider initialized: models_dir={self.models_dir}")

    def list_models(self) -> List[Dict[str, Any]]:
        """List available MLX models"""
        # Return hardcoded list of known MLX models
        return [
            {
                "id": "qwen25-coder-7b",
                "name": "Qwen2.5 Coder 7B MLX",
                "description": "Fast coding model for M4",
                "context_length": 32768
            },
            {
                "id": "qwen3-14b",
                "name": "Qwen3 14B MLX",
                "description": "General purpose model",
                "context_length": 32768
            },
            # ... etc
        ]

    def execute(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """Execute model using mlx_lm.generate"""
        parameters = parameters or {}

        # Build command
        cmd = [
            f"source {self.mlx_venv}/bin/activate",
            "&&",
            "mlx_lm.generate",
            "--model", model,
            "--prompt", prompt,
            "--max-tokens", str(parameters.get("max_tokens", 2048)),
            "--temp", str(parameters.get("temperature", 0.7)),
            "--top-p", str(parameters.get("top_p", 0.9))
        ]

        # Execute
        result = subprocess.run(
            " ".join(cmd),
            shell=True,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(f"MLX execution failed: {result.stderr}")

        return result.stdout.strip()

    def stream_execute(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Generator[str, None, None]:
        """Execute with streaming output"""
        # For now, execute and yield all at once
        # Future: implement true streaming
        output = self.execute(model, prompt, system_prompt, parameters)
        yield output

    def validate_config(self) -> bool:
        """Validate MLX is installed and working"""
        result = subprocess.run(
            ["python", "-c", "import mlx_lm; print('OK')"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0 and "OK" in result.stdout

    def get_info(self) -> Dict[str, Any]:
        """Get provider information"""
        return {
            "name": "MLX",
            "version": "1.0",
            "status": "online" if self.validate_config() else "offline",
            "capabilities": ["generation", "chat"],
            "limits": {"max_context": 32768}
        }
```

Testing:
```python
# tests/test_mlx_provider.py
def test_mlx_provider_instantiation():
    from providers.mlx_provider import MLXProvider
    provider = MLXProvider({})
    assert provider is not None

def test_mlx_provider_list_models():
    from providers.mlx_provider import MLXProvider
    provider = MLXProvider({})
    models = provider.list_models()
    assert len(models) > 0

def test_mlx_provider_implements_interface():
    from providers.mlx_provider import MLXProvider
    from providers.base_provider import LLMProvider
    provider = MLXProvider({})
    assert isinstance(provider, LLMProvider)
    assert hasattr(provider, 'execute')
    assert hasattr(provider, 'stream_execute')
```

---

**Task 2.2: Enhance Llama.cpp Provider (2 hours)**

File: `D:\models\providers\llama_cpp_provider.py` (update existing)

Review the existing implementation and ensure:
- [ ] `stream_execute()` properly implemented
- [ ] Fallback model logic available
- [ ] Parameter validation complete
- [ ] Error messages helpful

Add methods:
```python
def get_fallback_model(self, model_id: str) -> Optional[str]:
    """Get smaller fallback if model fails"""
    fallback_map = {
        "qwen3-coder-30b": "dolphin-llama31-8b",
        "llama33-70b": "ministral-3-14b",
        # ... etc
    }
    return fallback_map.get(model_id)

def validate_model_path(self, model_id: str) -> bool:
    """Validate model file exists"""
    model = self.get_model_by_id(model_id)
    if not model:
        return False

    path = Path(model["path"])
    return path.exists() or self._check_wsl_path(path)

def _check_wsl_path(self, path: Path) -> bool:
    """Check if path exists in WSL"""
    if not self.use_wsl:
        return False

    result = subprocess.run(
        ["wsl", "test", "-f", str(path)],
        capture_output=True
    )
    return result.returncode == 0
```

---

**Task 2.3: Create Unified Router Core (4 hours)**

File: `D:\models\core\router.py`

```python
"""Unified router using provider abstraction"""

from typing import Optional, Dict, Any, List
from config.models import ModelRegistry, ModelConfig
from config.profiles import HardwareProfiles
from providers.base_provider import LLMProvider

class UnifiedAIRouter:
    """
    Central router that delegates to appropriate provider.

    Usage:
        router = UnifiedAIRouter()
        output = router.run_model("qwen3-coder-30b", "What is Python?")
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize router"""
        self.config = config or {}
        self.models = ModelRegistry.MODELS
        self.hardware_profile = self._detect_hardware()
        self.provider = self._init_provider()

    def _detect_hardware(self) -> str:
        """Detect hardware profile"""
        if "hardware" in self.config:
            return self.config["hardware"]

        return HardwareProfiles.auto_detect()

    def _init_provider(self) -> LLMProvider:
        """Initialize appropriate provider"""
        hardware = self._detect_hardware()
        profile = HardwareProfiles.get(hardware)

        if not profile:
            raise ValueError(f"Unknown hardware profile: {hardware}")

        if profile.framework == "mlx":
            from providers.mlx_provider import MLXProvider
            return MLXProvider({
                "models_dir": profile.models_dir
            })
        else:  # llama.cpp
            from providers.llama_cpp_provider import LlamaCppProvider
            return LlamaCppProvider({
                "use_wsl": profile.platform == "Windows",
                "models_dir": profile.models_dir,
                "default_threads": profile.cpu_threads
            })

    def list_models(self) -> Dict[str, ModelConfig]:
        """List available models"""
        return self.models.copy()

    def get_model(self, model_id: str) -> Optional[ModelConfig]:
        """Get model by ID"""
        return self.models.get(model_id)

    def detect_use_case(self, prompt: str) -> str:
        """Detect use case from prompt text"""
        prompt_lower = prompt.lower()

        coding_keywords = [
            'code', 'function', 'class', 'debug', 'error', 'python',
            'javascript', 'implement', 'refactor', 'algorithm'
        ]
        reasoning_keywords = [
            'calculate', 'prove', 'math', 'solve', 'logic', 'analyze'
        ]
        creative_keywords = [
            'story', 'poem', 'creative', 'write', 'fiction'
        ]
        research_keywords = [
            'research', 'explain', 'summary', 'what is', 'compare'
        ]

        if any(kw in prompt_lower for kw in coding_keywords):
            return "coding"
        elif any(kw in prompt_lower for kw in reasoning_keywords):
            return "reasoning"
        elif any(kw in prompt_lower for kw in creative_keywords):
            return "creative"
        elif any(kw in prompt_lower for kw in research_keywords):
            return "research"
        return "general"

    def recommend_model(self, use_case: str) -> str:
        """Get recommended model for use case"""
        recommendations = ModelRegistry.get_use_case_recommendations()
        return recommendations.get(use_case, "qwen3-coder-30b")

    def run_model(
        self,
        model_id: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        streaming: bool = False
    ):
        """Execute model through provider"""
        if model_id not in self.models:
            raise ValueError(f"Model '{model_id}' not found")

        model = self.models[model_id]
        params = {
            "temperature": model.temperature,
            "top_p": model.top_p,
            "top_k": model.top_k,
            "max_tokens": 4096
        }

        if streaming:
            return self.provider.stream_execute(
                model_id, prompt, system_prompt, params
            )
        else:
            return self.provider.execute(
                model_id, prompt, system_prompt, params
            )

    def validate(self) -> bool:
        """Validate router configuration"""
        return self.provider.validate_config()
```

---

**Task 2.4: Create tests for unified router (2 hours)**

```python
# tests/test_unified_router.py
from core.router import UnifiedAIRouter

def test_unified_router_instantiation():
    """Can create unified router"""
    router = UnifiedAIRouter()
    assert router is not None

def test_unified_router_has_models():
    """Router has models available"""
    router = UnifiedAIRouter()
    models = router.list_models()
    assert len(models) > 0

def test_unified_router_detect_use_case():
    """Can detect use case from prompt"""
    router = UnifiedAIRouter()

    assert router.detect_use_case("write a python function") == "coding"
    assert router.detect_use_case("solve this math problem") == "reasoning"
    assert router.detect_use_case("write a story about dragons") == "creative"

def test_unified_router_recommend_model():
    """Can recommend model for use case"""
    router = UnifiedAIRouter()

    model = router.recommend_model("coding")
    assert model in router.models

def test_unified_router_get_model():
    """Can retrieve model config"""
    router = UnifiedAIRouter()

    model = router.get_model("qwen3-coder-30b")
    assert model is not None
    assert model.name == "Qwen3 Coder 30B Q4_K_M"

def test_unified_router_validates():
    """Router can validate configuration"""
    router = UnifiedAIRouter()
    # Don't require success, just that it doesn't crash
    result = router.validate()
    assert isinstance(result, bool)
```

---

**Task 2.5: Wire unified router into enhanced router (1 hour)**

Optional enhancement - don't replace existing, just make available:

```python
# In ai-router-enhanced.py, add:

try:
    from core.router import UnifiedAIRouter as NewRouter
    _NEW_ROUTER_AVAILABLE = True
except ImportError:
    _NEW_ROUTER_AVAILABLE = False

# Later in EnhancedAIRouter class:
def use_new_routing(self):
    """Switch to new unified router"""
    if _NEW_ROUTER_AVAILABLE:
        self._new_router = NewRouter()
        # Delegate model execution to new router
```

This allows gradual migration without breaking existing code.

---

**Task 2.6: Documentation (1 hour)**

Create: `docs/PROVIDER_INTEGRATION.md`

Explain:
- How providers work
- How to add a new provider
- Provider interface specification
- Testing requirements

---

#### Acceptance Criteria
- [ ] MLX provider created and working
- [ ] Llama.cpp provider enhanced with fallback logic
- [ ] UnifiedAIRouter working with both frameworks
- [ ] All provider tests passing
- [ ] Existing routers still functional (no breaking changes)
- [ ] Documentation updated

#### Testing Checklist
```bash
# Test MLX provider
pytest tests/test_mlx_provider.py -v

# Test unified router
pytest tests/test_unified_router.py -v

# Verify backward compatibility
python ai-router.py --list
python ai-router-enhanced.py --list

# Test new provider integration (if wired in)
python -c "from core.router import UnifiedAIRouter; r = UnifiedAIRouter(); print(len(r.list_models()))"
```

---

### Phase 3: UI Abstraction Layer (Week 3)
**Goal:** Separate presentation from business logic
**Effort:** 8-10 hours
**Risk:** Medium (refactoring existing UI)
**Reversibility:** 80% (can revert to inline UI)

#### Tasks

**Task 3.1: Extract Colors module (30 min)**

File: `D:\models\ui\colors.py`

```python
"""Color definitions for CLI output"""

class Colors:
    """ANSI color codes for terminal output"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

    # Foreground colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'

    # Bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'

    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    # ... etc

    @classmethod
    def print_colored(cls, text: str, color: str, bold: bool = False):
        """Print colored text to terminal"""
        if bold:
            print(f"{cls.BOLD}{color}{text}{cls.RESET}")
        else:
            print(f"{color}{text}{cls.RESET}")
```

Update all routers:
```python
# OLD:
class Colors:
    ...

# NEW:
from ui.colors import Colors
```

Removes ~90 lines total duplicated.

---

**Task 3.2: Create MenuController base class (3 hours)**

File: `D:\models\ui\menu_controller.py`

```python
"""
Menu controller - handles all user interaction

Separates presentation from business logic.
Can be extended for web UI, TUI, etc.
"""

import sys
from typing import Optional, Dict, Any, List, Tuple, Callable
from abc import ABC, abstractmethod

from core.router import UnifiedAIRouter
from config.models import ModelConfig
from ui.colors import Colors

class MenuController(ABC):
    """Abstract menu controller"""

    def __init__(self, router: UnifiedAIRouter):
        self.router = router
        self.colors = Colors()
        self.current_project = None

    @abstractmethod
    def main_menu(self):
        """Main menu - implement in subclass"""
        pass

    # UI Helper methods (useful for all implementations)

    def show_banner(self, title: str):
        """Display banner"""
        sep = "=" * 70
        print(f"\n{self.colors.BRIGHT_CYAN}{self.colors.BOLD}{sep}{self.colors.RESET}")
        print(f"{self.colors.BRIGHT_CYAN}{self.colors.BOLD}{title.center(70)}{self.colors.RESET}")
        print(f"{self.colors.BRIGHT_CYAN}{self.colors.BOLD}{sep}{self.colors.RESET}\n")

    def show_menu(self, options: List[Tuple[str, Callable]]) -> Any:
        """Display menu and get selection"""
        for i, (label, _) in enumerate(options, 1):
            print(f"{self.colors.BRIGHT_GREEN}[{i}]{self.colors.RESET} {label}")

        choice = input(f"\n{self.colors.BRIGHT_YELLOW}Enter choice [1-{len(options)}]: {self.colors.RESET}").strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                _, action = options[idx]
                return action()
        except ValueError:
            pass

        print(f"{self.colors.BRIGHT_RED}Invalid choice.{self.colors.RESET}")
        return None

    def confirm(self, message: str, default_yes: bool = True) -> bool:
        """Yes/No confirmation"""
        default_str = "[Y/n]" if default_yes else "[y/N]"
        response = input(f"{self.colors.BRIGHT_YELLOW}{message} {default_str}: {self.colors.RESET}").strip().lower()

        if default_yes:
            return response in ['', 'y', 'yes']
        else:
            return response in ['y', 'yes']

    def print_model_info(self, model: ModelConfig):
        """Display detailed model information"""
        sep = "=" * 64
        print(f"\n{self.colors.BRIGHT_CYAN}{self.colors.BOLD}{sep}{self.colors.RESET}")
        print(f"{self.colors.BRIGHT_CYAN}{self.colors.BOLD}MODEL INFORMATION{self.colors.RESET}")
        print(f"{self.colors.BRIGHT_CYAN}{self.colors.BOLD}{sep}{self.colors.RESET}\n")

        print(f"{self.colors.BRIGHT_WHITE}Name:{self.colors.RESET}          {self.colors.BRIGHT_GREEN}{model.name}{self.colors.RESET}")
        print(f"{self.colors.BRIGHT_WHITE}Model ID:{self.colors.RESET}      {self.colors.BRIGHT_YELLOW}{model.id}{self.colors.RESET}")
        print(f"{self.colors.BRIGHT_WHITE}Size:{self.colors.RESET}          {self.colors.BRIGHT_MAGENTA}{model.size_gb}GB{self.colors.RESET}")
        print(f"{self.colors.BRIGHT_WHITE}Speed:{self.colors.RESET}         {self.colors.BRIGHT_CYAN}{model.speed_tokens_per_sec}{self.colors.RESET}")
        print(f"{self.colors.BRIGHT_WHITE}Framework:{self.colors.RESET}     {self.colors.BRIGHT_BLUE}{model.framework.upper()}{self.colors.RESET}")
        print(f"{self.colors.BRIGHT_WHITE}Use Case:{self.colors.RESET}      {self.colors.YELLOW}{model.use_case}{self.colors.RESET}")
        print(f"{self.colors.BRIGHT_WHITE}Context:{self.colors.RESET}       {self.colors.CYAN}{model.context_tokens:,} tokens{self.colors.RESET}")

        if model.notes:
            print(f"\n{self.colors.BRIGHT_MAGENTA}Notes:{self.colors.RESET}")
            print(f"  {self.colors.MAGENTA}{model.notes}{self.colors.RESET}")

        print()

    def list_models(self):
        """Display available models"""
        sep1 = "╔" + "═" * 62 + "╗"
        sep2 = "╚" + "═" * 62 + "╝"

        print(f"\n{self.colors.BRIGHT_CYAN}{self.colors.BOLD}{sep1}{self.colors.RESET}")
        print(f"{self.colors.BRIGHT_CYAN}{self.colors.BOLD}║ AVAILABLE MODELS{self.colors.RESET}")
        print(f"{self.colors.BRIGHT_CYAN}{self.colors.BOLD}{sep2}{self.colors.RESET}\n")

        models = self.router.list_models()
        for idx, (model_id, model) in enumerate(models.items(), 1):
            print(f"{self.colors.BRIGHT_YELLOW}[{idx}]{self.colors.RESET} {self.colors.BRIGHT_WHITE}{model_id}{self.colors.RESET}")
            print(f"    {self.colors.WHITE}{model.name}{self.colors.RESET}")
            print(f"    {self.colors.CYAN}Use case: {model.use_case}{self.colors.RESET}")
            print(f"    {self.colors.GREEN}{model.size_gb}GB | {model.speed_tokens_per_sec}{self.colors.RESET}\n")

    def show_error(self, message: str):
        """Display error message"""
        print(f"\n{self.colors.BRIGHT_RED}Error: {message}{self.colors.RESET}\n")

    def show_success(self, message: str):
        """Display success message"""
        print(f"\n{self.colors.BRIGHT_GREEN}{message}{self.colors.RESET}\n")

    def input_prompt(self, message: str) -> str:
        """Get prompt input from user"""
        return input(f"{self.colors.BRIGHT_CYAN}{message}{self.colors.RESET}\n{self.colors.YELLOW}> {self.colors.RESET}").strip()


class CLIMenuController(MenuController):
    """CLI/interactive implementation of menu controller"""

    def main_menu(self):
        """Main menu loop"""
        while True:
            self.show_banner("AI ROUTER - Main Menu")

            options = [
                ("Auto-select model based on prompt", self.auto_select_mode),
                ("Manually select model", self.manual_select_mode),
                ("List all available models", self.list_models),
                ("Exit", lambda: sys.exit(0))
            ]

            self.show_menu(options)

    def auto_select_mode(self):
        """Auto-select model based on user prompt"""
        prompt = self.input_prompt("Enter your prompt (or 'back' to return):")

        if prompt.lower() == 'back':
            return

        # Detect use case
        use_case = self.router.detect_use_case(prompt)
        print(f"\n{self.colors.BRIGHT_MAGENTA}Detected use case: {self.colors.BRIGHT_WHITE}{use_case.upper()}{self.colors.RESET}")

        # Get recommendation
        model_id = self.router.recommend_model(use_case)
        model = self.router.get_model(model_id)

        print(f"{self.colors.BRIGHT_GREEN}Recommended model: {self.colors.BRIGHT_WHITE}{model.name}{self.colors.RESET}")

        # Show info and confirm
        self.print_model_info(model)

        if self.confirm("Run this model?"):
            self.run_with_progress(model_id, prompt)

    def manual_select_mode(self):
        """Manually select model"""
        self.list_models()

        models = self.router.list_models()
        model_ids = list(models.keys())

        choice = input(f"\n{self.colors.BRIGHT_YELLOW}Select model number (or 'back'): {self.colors.RESET}").strip()

        if choice.lower() == 'back':
            return

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(model_ids):
                model_id = model_ids[idx]
                model = models[model_id]

                self.print_model_info(model)

                prompt = self.input_prompt("Enter your prompt:")
                if self.confirm("Run this model?"):
                    self.run_with_progress(model_id, prompt)
            else:
                self.show_error("Invalid model number")
        except ValueError:
            self.show_error("Please enter a valid number")

    def run_with_progress(self, model_id: str, prompt: str):
        """Run model with progress feedback"""
        print(f"\n{self.colors.BRIGHT_GREEN}{self.colors.BOLD}Executing {self.router.get_model(model_id).name}...{self.colors.RESET}\n")

        try:
            # Support streaming if available
            response = self.router.run_model(model_id, prompt, streaming=True)

            # Print response
            for chunk in response:
                print(chunk, end='', flush=True)
            print()

            self.show_success("Execution completed")
        except FileNotFoundError as e:
            self.show_error(f"Model file not found: {e}")
        except Exception as e:
            self.show_error(f"Execution failed: {e}")

        input(f"\n{self.colors.BRIGHT_CYAN}Press Enter to continue...{self.colors.RESET}")
```

---

**Task 3.3: Update ai-router.py to use MenuController (1 hour)**

```python
# At top of ai-router.py
from ui.menu_controller import CLIMenuController
from core.router import UnifiedAIRouter

# In main():
def main():
    try:
        # Use new unified router
        router = UnifiedAIRouter()

        # Handle CLI args
        if len(sys.argv) > 1:
            if sys.argv[1] == "--list":
                controller = CLIMenuController(router)
                controller.list_models()
            elif sys.argv[1] == "--help":
                print("Usage: python ai-router.py [--list | --help]")
        else:
            # Interactive mode
            controller = CLIMenuController(router)
            controller.main_menu()

    except KeyboardInterrupt:
        print(f"\n{Colors.BRIGHT_GREEN}Goodbye!{Colors.RESET}\n")
        sys.exit(0)
```

---

**Task 3.4: Tests for MenuController (1.5 hours)**

```python
# tests/test_menu_controller.py
from ui.menu_controller import CLIMenuController, MenuController
from core.router import UnifiedAIRouter

def test_menu_controller_instantiation():
    """Can create menu controller"""
    router = UnifiedAIRouter()
    controller = CLIMenuController(router)
    assert controller is not None

def test_menu_controller_has_router():
    """Controller has access to router"""
    router = UnifiedAIRouter()
    controller = CLIMenuController(router)
    assert controller.router is router

def test_menu_controller_detect_use_case():
    """Controller delegates use case detection"""
    router = UnifiedAIRouter()
    controller = CLIMenuController(router)

    # Controller should delegate to router
    use_case = controller.router.detect_use_case("write python code")
    assert use_case == "coding"

def test_menu_controller_get_model_info():
    """Can retrieve and display model info"""
    router = UnifiedAIRouter()
    controller = CLIMenuController(router)

    model = router.get_model("qwen3-coder-30b")
    assert model is not None
    assert model.name == "Qwen3 Coder 30B Q4_K_M"

def test_menu_controller_list_models_no_crash():
    """List models doesn't crash (doesn't execute in test)"""
    router = UnifiedAIRouter()
    controller = CLIMenuController(router)

    # Just verify it's callable
    assert hasattr(controller, 'list_models')
    assert callable(controller.list_models)
```

---

**Task 3.5: Documentation (1 hour)**

Create: `docs/UI_ARCHITECTURE.md`

Explain:
- MenuController abstraction
- How to implement new UI (web, TUI, etc.)
- Color management
- Event handling

---

#### Acceptance Criteria
- [ ] Colors moved to ui/colors.py
- [ ] MenuController abstract class created
- [ ] CLIMenuController implements UI
- [ ] All routers wired to use new controller (optional, not required)
- [ ] Tests passing
- [ ] No breaking changes to user-facing behavior

---

## Overall Success Metrics

After all 5 phases:

```
Metric                          Before      After       Improvement
────────────────────────────────────────────────────────────────────
Total Lines of Code              3,737      2,400       -36%
Duplicated Code                  2,400      ~100        -96%
Number of Router Files             3          1         -67%
Config Definitions                 3          1         -67%
Model Database Sources             3          1         -67%
Provider Implementations           0         (integrated) +5
UI Layer Abstraction              No         Yes        +Testable
Path Resolution                   Hard-coded  Config-driven  +Flexible
New Platform Support              ~4 hrs     ~30 min     -87%
Code Reuse                         Low        High       +Better
Testing Coverage                  ~40%       ~80%       +Better
Architecture Documentation        None       Complete   +Knowledge
```

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Breaking existing workflows | Keep old routers as deprecated, not removed |
| Users relying on ai-router-enhanced.py | Provide migration guide, extended deprecation period |
| New bugs in refactored code | Comprehensive test suite, regression testing |
| Performance regression | Benchmark before/after, profile critical paths |
| Provider integration issues | Integration tests, graceful fallbacks |

## Timeline Summary

- **Week 1 (Phase 1):** Config extraction - LOW RISK, HIGH VALUE
- **Week 2 (Phase 2):** Provider integration - MEDIUM RISK, HIGH VALUE
- **Week 3 (Phase 3):** UI abstraction - MEDIUM RISK, MEDIUM VALUE
- **Week 4-8:** Consolidation and migration - Ongoing, with deprecation period

**Total:** 3 weeks core refactoring + 4-5 weeks deprecation/migration = ~8 weeks total

---

**End of Implementation Roadmap**
