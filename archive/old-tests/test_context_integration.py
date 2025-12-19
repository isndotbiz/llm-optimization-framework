#!/usr/bin/env python3
"""
Test script to verify context management integration
"""
from pathlib import Path
from context_manager import ContextManager

def test_context_manager():
    """Test ContextManager functionality"""
    print("Testing Context Manager Integration")
    print("=" * 60)

    cm = ContextManager()

    # Test 1: Add text context
    print("\n1. Testing text context addition...")
    item = cm.add_text("This is test context content.", "Test Context")
    print(f"   Added: {item['label']} ({item['tokens']} tokens)")
    assert item['type'] == 'text'
    assert item['tokens'] > 0
    print("   PASS")

    # Test 2: Token estimation
    print("\n2. Testing token estimation...")
    text = "Hello world this is a test"
    tokens = cm.estimate_tokens(text)
    print(f"   Estimated {tokens} tokens for text with {len(text.split())} words")
    assert tokens > 0
    print("   PASS")

    # Test 3: Build context prompt
    print("\n3. Testing context prompt building...")
    user_prompt = "What is in the context?"
    full_prompt = cm.build_context_prompt(user_prompt)
    print(f"   Built prompt with {len(full_prompt)} characters")
    assert "Test Context" in full_prompt
    assert user_prompt in full_prompt
    print("   PASS")

    # Test 4: Context summary
    print("\n4. Testing context summary...")
    summary = cm.get_context_summary()
    print("   Summary generated:")
    for line in summary.split('\n')[:5]:
        print(f"   {line}")
    print("   PASS")

    # Test 5: Token limit
    print("\n5. Testing token limit setting...")
    cm.set_max_tokens(8000)
    assert cm.max_tokens == 8000
    print(f"   Token limit set to {cm.max_tokens:,}")
    print("   PASS")

    # Test 6: Remove context
    print("\n6. Testing context removal...")
    result = cm.remove_context_item(0)
    assert result == True
    assert len(cm.context_items) == 0
    print("   Context item removed successfully")
    print("   PASS")

    # Test 7: File context (if test file exists)
    print("\n7. Testing file context addition...")
    test_file = Path("D:/models/context_manager.py")
    if test_file.exists():
        item = cm.add_file(test_file, "Context Manager Source")
        print(f"   Added: {item['label']} ({item['tokens']:,} tokens)")
        assert item['type'] == 'file'
        print("   PASS")
    else:
        print("   SKIPPED (test file not found)")

    # Test 8: Clear all context
    print("\n8. Testing context clearing...")
    cm.clear_context()
    assert len(cm.context_items) == 0
    print("   All context cleared")
    print("   PASS")

    print("\n" + "=" * 60)
    print("All tests PASSED!")
    print("\nContext Management Integration: READY TO USE")
    return True

if __name__ == "__main__":
    try:
        test_context_manager()
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
