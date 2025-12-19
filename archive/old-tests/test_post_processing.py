#!/usr/bin/env python3
"""
Test script for Response Post-Processing integration
"""

import sys
from pathlib import Path
from datetime import datetime

# Add models dir to path
sys.path.insert(0, str(Path(__file__).parent))

from response_processor import ResponseProcessor

def test_response_processor():
    """Test basic ResponseProcessor functionality"""

    print("Testing Response Post-Processing Integration...\n")

    # Initialize processor
    output_dir = Path("D:/models/outputs")
    processor = ResponseProcessor(output_dir)

    # Test response text with code blocks
    test_response = """
Here's a simple Python example:

```python
def hello_world():
    print("Hello, World!")
    return True

if __name__ == "__main__":
    hello_world()
```

And here's some JavaScript:

```javascript
function greet(name) {
    console.log(`Hello, ${name}!`);
}

greet("World");
```

That's all!
"""

    # Test 1: Get statistics
    print("Test 1: Get Statistics")
    stats = processor.get_statistics(test_response)
    print(f"  Characters: {stats['char_count']}")
    print(f"  Words: {stats['word_count']}")
    print(f"  Lines: {stats['line_count']}")
    print(f"  Code blocks: {stats['code_blocks']}")
    assert stats['code_blocks'] == 2, "Should find 2 code blocks"
    print("  [OK] PASSED\n")

    # Test 2: Extract code blocks
    print("Test 2: Extract Code Blocks")
    code_blocks = processor.extract_code_blocks(test_response)
    print(f"  Found {len(code_blocks)} code blocks")
    for i, block in enumerate(code_blocks):
        print(f"    {i+1}. {block['language']} ({len(block['code'])} chars)")
    assert len(code_blocks) == 2, "Should extract 2 code blocks"
    assert code_blocks[0]['language'] == 'python', "First block should be Python"
    assert code_blocks[1]['language'] == 'javascript', "Second block should be JavaScript"
    print("  [OK] PASSED\n")

    # Test 3: Save response
    print("Test 3: Save Response to File")
    metadata = {
        "Test": "Integration Test",
        "Timestamp": datetime.now().isoformat()
    }
    filepath = processor.save_response(
        test_response,
        filename="test_post_processing_integration",
        model_name="Test Model",
        metadata=metadata
    )
    print(f"  Saved to: {filepath}")
    assert filepath.exists(), "File should exist"
    print("  [OK] PASSED\n")

    # Test 4: Format as markdown
    print("Test 4: Format as Markdown")
    md_content = processor.format_as_markdown(
        test_response,
        model_name="Test Model",
        metadata=metadata
    )
    assert "# AI Router Response" in md_content, "Should have markdown header"
    assert "**Model:**" in md_content, "Should include model name"
    print("  [OK] PASSED\n")

    # Test 5: Save code blocks
    print("Test 5: Save Code Blocks")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    saved_files = processor.save_code_blocks(test_response, f"test_code_{timestamp}")
    print(f"  Saved {len(saved_files)} code files:")
    for fp in saved_files:
        print(f"    - {fp.name}")
    assert len(saved_files) == 2, "Should save 2 code files"
    print("  [OK] PASSED\n")

    # Test 6: List saved responses
    print("Test 6: List Saved Responses")
    recent_files = processor.list_saved_responses(limit=5)
    print(f"  Found {len(recent_files)} recent response files")
    for i, fp in enumerate(recent_files[:3], 1):
        print(f"    {i}. {fp.name}")
    print("  [OK] PASSED\n")

    # Test 7: Clipboard (optional - may fail if no display)
    print("Test 7: Copy to Clipboard")
    try:
        success = processor.copy_to_clipboard("Test clipboard content")
        if success:
            print("  [OK] Clipboard copy PASSED")
        else:
            print("  [WARN] Clipboard not available (pyperclip issue)")
    except Exception as e:
        print(f"  [WARN] Clipboard test skipped: {e}")

    print("\n" + "="*60)
    print("ALL TESTS PASSED!")
    print("="*60)
    print("\nResponse Post-Processing integration is working correctly.")
    print(f"Output directory: {output_dir}")
    print(f"Files created during testing:")
    print(f"  - {filepath.name}")
    for fp in saved_files:
        print(f"  - {fp.name}")

if __name__ == "__main__":
    try:
        test_response_processor()
    except AssertionError as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
