#!/usr/bin/env python3
"""
ModelSelector - Enhanced model selection with confidence scoring and preference learning
Part of AI Router - Intelligent Model Selection and Execution CLI
"""

from typing import Dict, List, Tuple, Optional
import json
from pathlib import Path
from collections import defaultdict


class ModelSelector:
    """Enhanced model selection with confidence scoring and learning"""

    def __init__(self, preferences_file: Path):
        self.preferences_file = preferences_file
        self.preferences = self._load_preferences()

        # Enhanced keyword patterns with weights
        self.patterns = {
            "coding": {
                "high": ["write code", "implement", "debug", "refactor", "optimize code",
                        "code review", "fix bug", "write function", "create class"],
                "medium": ["code", "function", "class", "algorithm", "programming",
                          "python", "javascript", "java", "c++", "rust", "api"],
                "low": ["software", "develop", "script", "program"]
            },
            "reasoning": {
                "high": ["solve", "analyze deeply", "logic", "prove", "deduce",
                        "complex problem", "mathematical proof", "reasoning"],
                "medium": ["think", "reason", "explain why", "problem solving",
                          "analyze", "deduce", "infer"],
                "low": ["understand", "clarify", "why"]
            },
            "creative": {
                "high": ["write story", "creative writing", "poem", "brainstorm",
                        "fiction", "narrative", "character"],
                "medium": ["creative", "imagine", "design", "innovative", "plot"],
                "low": ["idea", "suggestion"]
            },
            "research": {
                "high": ["research", "comprehensive analysis", "survey", "review literature",
                        "summarize", "compare"],
                "medium": ["investigate", "examine", "what is", "how does",
                          "explain", "overview"],
                "low": ["information", "learn about", "tell me about"]
            },
            "math": {
                "high": ["calculate", "mathematics", "equation", "theorem", "proof",
                        "solve equation", "mathematical"],
                "medium": ["math", "statistics", "probability", "formula"],
                "low": ["number", "compute"]
            }
        }

        # Default model mappings for categories
        self.category_model_map = {
            "coding": ["qwen3-coder-30b", "qwen25-coder-14b-mlx"],  # qwen25-coder-32b removed (file missing)
            "reasoning": ["phi4-14b", "ministral-3-14b", "deepseek-r1-14b", "phi4-14b-mlx"],
            "creative": ["gemma3-27b", "dolphin-mistral-24b", "gemma3-9b-mlx"],
            "research": ["llama33-70b", "ministral-3-14b", "qwen25-14b-mlx"],
            "math": ["phi4-14b", "ministral-3-14b", "deepseek-r1-14b", "phi4-14b-mlx"],
            "general": ["dolphin-llama31-8b", "qwen25-14b-mlx", "wizard-vicuna-13b"]
        }

    def analyze_prompt(self, prompt: str) -> Dict[str, float]:
        """Analyze prompt and return confidence scores for each category.

        Args:
            prompt: User's input prompt

        Returns:
            {"coding": 0.85, "reasoning": 0.3, ...}
        """
        prompt_lower = prompt.lower()
        scores = defaultdict(float)

        for category, patterns in self.patterns.items():
            # High confidence matches
            for pattern in patterns["high"]:
                if pattern in prompt_lower:
                    scores[category] += 0.5

            # Medium confidence matches
            for pattern in patterns["medium"]:
                if pattern in prompt_lower:
                    scores[category] += 0.3

            # Low confidence matches
            for pattern in patterns["low"]:
                if pattern in prompt_lower:
                    scores[category] += 0.1

        # Normalize scores to 0-1 range
        if scores:
            max_score = max(scores.values())
            normalized = {k: min(v / max_score, 1.0) for k, v in scores.items()}
        else:
            normalized = {}

        return normalized

    def select_model(self, prompt: str, available_models: Dict) -> Tuple[str, str, float]:
        """Select best model based on prompt analysis.

        Args:
            prompt: User's input prompt
            available_models: Dictionary of available models

        Returns:
            (model_id, category, confidence)
        """
        scores = self.analyze_prompt(prompt)

        if not scores:
            return self._get_default_model(available_models), "general", 0.5

        # Get highest scoring category
        best_category = max(scores, key=scores.get)
        confidence = scores[best_category]

        # Apply user preferences
        if best_category in self.preferences:
            preferred_model = self.preferences[best_category]
            if preferred_model in available_models:
                return preferred_model, best_category, confidence

        # Fall back to default category model
        model_id = self._get_model_for_category(best_category, available_models)
        if not model_id:
            model_id = self._get_default_model(available_models)

        return model_id, best_category, confidence

    def learn_preference(self, category: str, model_id: str):
        """Learn user preference for a category

        Args:
            category: Use case category (coding, reasoning, etc.)
            model_id: Model ID user prefers for this category
        """
        self.preferences[category] = model_id
        self._save_preferences()

    def get_recommendations(self, prompt: str, available_models: Dict, top_n: int = 3) -> List[Dict]:
        """Get top N model recommendations with confidence scores

        Args:
            prompt: User's input prompt
            available_models: Dictionary of available models
            top_n: Number of recommendations to return

        Returns:
            List of recommendation dictionaries with model_id, category, confidence
        """
        scores = self.analyze_prompt(prompt)

        if not scores:
            # No clear category detected, return general models
            default_model = self._get_default_model(available_models)
            return [{
                "model_id": default_model,
                "category": "general",
                "confidence": 0.5
            }]

        recommendations = []

        # Sort categories by confidence score
        sorted_categories = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        for category, confidence in sorted_categories[:top_n]:
            model_id = self._get_model_for_category(category, available_models)
            if model_id:
                recommendations.append({
                    "model_id": model_id,
                    "category": category,
                    "confidence": confidence
                })

        # Ensure we have at least one recommendation
        if not recommendations:
            default_model = self._get_default_model(available_models)
            recommendations.append({
                "model_id": default_model,
                "category": "general",
                "confidence": 0.5
            })

        return recommendations

    def _get_model_for_category(self, category: str, models: Dict) -> Optional[str]:
        """Get default model for category from available models

        Args:
            category: Use case category
            models: Dictionary of available models

        Returns:
            Model ID or None if no suitable model found
        """
        # Check if user has a preference
        if category in self.preferences:
            preferred = self.preferences[category]
            if preferred in models:
                return preferred

        # Fall back to default mapping
        if category in self.category_model_map:
            for model_id in self.category_model_map[category]:
                if model_id in models:
                    return model_id

        return None

    def _get_default_model(self, models: Dict) -> str:
        """Get a default model from available models

        Args:
            models: Dictionary of available models

        Returns:
            Model ID of first available model
        """
        if not models:
            raise ValueError("No models available")
        return list(models.keys())[0]

    def _load_preferences(self) -> Dict:
        """Load user preferences from JSON file

        Returns:
            Dictionary of preferences
        """
        if self.preferences_file.exists():
            try:
                with open(self.preferences_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                # If file is corrupted, return empty dict
                return {}
        return {}

    def _save_preferences(self):
        """Save preferences to JSON file"""
        try:
            # Create parent directory if it doesn't exist
            self.preferences_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.preferences_file, 'w', encoding='utf-8') as f:
                json.dump(self.preferences, indent=2, fp=f)
        except Exception as e:
            print(f"Warning: Could not save preferences: {e}")

    def get_explanation(self, category: str, confidence: float, prompt: str) -> str:
        """Generate explanation for why a model was selected

        Args:
            category: Selected category
            confidence: Confidence score
            prompt: Original prompt

        Returns:
            Human-readable explanation string
        """
        explanations = {
            "coding": "detected code-related keywords like 'function', 'debug', 'implement'",
            "reasoning": "detected reasoning keywords like 'solve', 'analyze', 'logic'",
            "creative": "detected creative keywords like 'story', 'write', 'imagine'",
            "research": "detected research keywords like 'explain', 'summarize', 'compare'",
            "math": "detected math keywords like 'calculate', 'equation', 'solve'",
            "general": "no specific category detected, using general-purpose model"
        }

        confidence_level = "high" if confidence >= 0.7 else "medium" if confidence >= 0.4 else "low"
        explanation = explanations.get(category, "matched general criteria")

        return f"Selected {category} model with {confidence_level} confidence ({confidence:.0%}) - {explanation}"
