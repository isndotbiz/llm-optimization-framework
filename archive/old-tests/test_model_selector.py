#!/usr/bin/env python3
"""
Test script for ModelSelector enhancements
Demonstrates confidence scoring and preference learning
"""

from pathlib import Path
from model_selector import ModelSelector
import platform
import sys
import importlib.util

# Import ModelDatabase from ai-router.py
spec = importlib.util.spec_from_file_location("ai_router", "D:/models/ai-router.py")
ai_router = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ai_router)
ModelDatabase = ai_router.ModelDatabase

# Get platform models
models = ModelDatabase.get_platform_models()

# Initialize model selector with test preferences file
selector = ModelSelector(Path("D:/models/.test-preferences.json"))

# Test prompts with different use cases
test_prompts = [
    "Write a Python function to calculate fibonacci numbers",
    "Solve this complex math equation: 2x^2 + 5x - 3 = 0",
    "Write a creative short story about a robot learning to feel emotions",
    "Research and explain how quantum computing works",
    "Debug this Python code that's throwing an IndexError"
]

print("="*70)
print("SMART MODEL SELECTION - CONFIDENCE SCORING TEST")
print("="*70)

for i, prompt in enumerate(test_prompts, 1):
    print(f"\n\n{'='*70}")
    print(f"TEST {i}: {prompt}")
    print('='*70)

    # Analyze prompt
    scores = selector.analyze_prompt(prompt)
    print(f"\nConfidence Scores:")
    for category, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
        bar = "█" * int(score * 20)
        empty = "░" * (20 - int(score * 20))
        print(f"  {category:12s}: {bar}{empty} {score:.0%}")

    # Select model
    model_id, category, confidence = selector.select_model(prompt, models)
    model_data = models[model_id]

    print(f"\n✓ Selected Model: {model_data['name']}")
    print(f"  Category: {category}")
    print(f"  Confidence: {confidence:.0%}")

    # Get explanation
    explanation = selector.get_explanation(category, confidence, prompt)
    print(f"  Explanation: {explanation}")

    # Get top 3 recommendations
    recommendations = selector.get_recommendations(prompt, models, top_n=3)
    print(f"\n  Top 3 Recommendations:")
    for j, rec in enumerate(recommendations, 1):
        rec_model = models[rec['model_id']]
        print(f"    {j}. {rec_model['name'][:40]:40s} ({rec['category']:10s}) - {rec['confidence']:.0%}")

print(f"\n\n{'='*70}")
print("Testing Preference Learning")
print('='*70)

# Save a preference
print("\nSaving preference: coding -> qwen25-coder-32b")
selector.learn_preference("coding", "qwen25-coder-32b")
print("✓ Preference saved")

# Test that preference is used
coding_prompt = "Implement a binary search algorithm in Python"
model_id, category, confidence = selector.select_model(coding_prompt, models)
print(f"\nTest prompt: {coding_prompt}")
print(f"Selected model: {models[model_id]['name']}")
print(f"Category: {category}")
print(f"Using learned preference: {'YES' if model_id == 'qwen25-coder-32b' else 'NO'}")

# Load preferences
print(f"\nCurrent preferences: {selector.preferences}")

print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70)
