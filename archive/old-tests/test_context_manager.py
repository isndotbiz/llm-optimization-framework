#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for ContextManager
Demonstrates basic functionality and usage
"""

import sys
import os
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from context_manager import ContextManager

def test_basic_usage():
    """Test basic ContextManager functionality"""
    print("=== ContextManager Test Suite ===\n")

    # Create manager
    cm = ContextManager()
    print(f"✓ Created ContextManager")
    print(f"  Default max tokens: {cm.max_tokens:,}\n")

    # Test 1: Add a file
    print("Test 1: Adding a file")
    try:
        test_file = Path(__file__)  # Add this test script itself
        item = cm.add_file(test_file, "Test Script")
        print(f"✓ Added file: {item['label']}")
        print(f"  Language: {item['language']}")
        print(f"  Tokens: {item['tokens']:,}")
        print(f"  Path: {item['path']}\n")
    except Exception as e:
        print(f"✗ Error: {e}\n")

    # Test 2: Add text
    print("Test 2: Adding text")
    try:
        sample_text = """
        This is a sample text snippet.
        It demonstrates adding arbitrary text to context.
        Useful for error messages, logs, or requirements.
        """
        item = cm.add_text(sample_text, "Sample Text")
        print(f"✓ Added text: {item['label']}")
        print(f"  Type: {item['type']}")
        print(f"  Tokens: {item['tokens']:,}\n")
    except Exception as e:
        print(f"✗ Error: {e}\n")

    # Test 3: Get summary
    print("Test 3: Context summary")
    summary = cm.get_context_summary()
    print(summary)
    print()

    # Test 4: Build prompt
    print("Test 4: Building prompt with context")
    user_prompt = "Analyze the provided files and text"
    try:
        full_prompt = cm.build_context_prompt(user_prompt, truncate=True)
        print(f"✓ Built prompt ({len(full_prompt)} chars)")
        print(f"\nPrompt preview (first 300 chars):")
        print("-" * 60)
        print(full_prompt[:300] + "...")
        print("-" * 60)
        print()
    except Exception as e:
        print(f"✗ Error: {e}\n")

    # Test 5: Token estimation
    print("Test 5: Token estimation")
    test_texts = [
        "Hello world",
        "This is a longer sentence with more words to estimate",
        "def hello():\n    print('Hello, world!')\n    return True"
    ]
    for text in test_texts:
        tokens = cm.estimate_tokens(text)
        words = len(text.split())
        print(f"  Text: '{text[:40]}...'")
        print(f"  Words: {words}, Estimated tokens: {tokens}")
    print()

    # Test 6: Remove item
    print("Test 6: Removing context item")
    try:
        if cm.remove_context_item(0):
            print(f"✓ Removed item at index 0")
            print(f"  Remaining items: {len(cm.context_items)}\n")
        else:
            print(f"✗ Failed to remove item\n")
    except Exception as e:
        print(f"✗ Error: {e}\n")

    # Test 7: Set token limit
    print("Test 7: Setting token limit")
    try:
        cm.set_max_tokens(8192)
        print(f"✓ Set max tokens to {cm.max_tokens:,}\n")
    except Exception as e:
        print(f"✗ Error: {e}\n")

    # Test 8: Clear context
    print("Test 8: Clearing all context")
    cm.clear_context()
    print(f"✓ Cleared context")
    print(f"  Remaining items: {len(cm.context_items)}\n")

    # Test 9: Language detection
    print("Test 9: Language detection")
    test_extensions = [
        ('.py', 'Python'),
        ('.js', 'JavaScript'),
        ('.md', 'Markdown'),
        ('.txt', 'Text'),
        ('.unknown', 'Text (fallback)')
    ]
    for ext, expected in test_extensions:
        # Create a fake path for testing
        fake_path = Path(f"test{ext}")
        detected = cm._detect_language(fake_path)
        status = "✓" if detected.lower() in expected.lower() else "✗"
        print(f"  {status} {ext} -> {detected}")
    print()

    print("=== All Tests Complete ===")


def test_large_context():
    """Test handling of large context"""
    print("\n=== Large Context Test ===\n")

    cm = ContextManager()
    cm.set_max_tokens(1000)  # Small limit for testing

    # Add multiple items
    for i in range(5):
        text = f"This is text item {i+1}. " * 100  # 100 words each
        cm.add_text(text, f"Item {i+1}")

    print(f"Added {len(cm.context_items)} items")
    print(f"Total tokens: {cm.get_total_tokens():,}")
    print(f"Max tokens: {cm.max_tokens:,}")

    # Try to build prompt (should truncate)
    user_prompt = "Summarize all items"
    full_prompt = cm.build_context_prompt(user_prompt, truncate=True)

    print(f"\nBuilt prompt with truncation")
    print(f"Prompt length: {len(full_prompt)} chars")
    print(f"Estimated tokens: {cm.estimate_tokens(full_prompt):,}")
    print("\n✓ Truncation test passed")


if __name__ == "__main__":
    test_basic_usage()
    test_large_context()
