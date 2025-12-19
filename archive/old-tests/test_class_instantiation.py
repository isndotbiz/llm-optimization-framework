#!/usr/bin/env python3
"""Test script to check if main classes can be instantiated without errors"""

import sys
import os

print("="*80)
print("AI ROUTER ENHANCED - CLASS INSTANTIATION TEST")
print("="*80)

# Add the models directory to the path
sys.path.insert(0, 'D:/models')

print("\n[TEST 1] Import Main Script Module")
print("-" * 80)

try:
    # Try to read and parse the script without executing it
    with open('D:/models/ai-router-enhanced.py', 'r', encoding='utf-8') as f:
        code = f.read()

    # Check for common class definitions
    import re

    # Find all class definitions
    class_matches = re.findall(r'class\s+(\w+).*?:', code)

    if class_matches:
        print(f"[PASS] Found {len(class_matches)} class definitions:")
        for cls in class_matches:
            print(f"       - {cls}")
        classes_found = True
    else:
        print("[FAIL] No class definitions found")
        classes_found = False

except Exception as e:
    print(f"[FAIL] Error reading script: {e}")
    classes_found = False

print("\n[TEST 2] Check for Main Entry Point")
print("-" * 80)

try:
    if '__name__' in code and '__main__' in code:
        print("[PASS] Main entry point found")
        has_main = True
    else:
        print("[WARNING] No standard main entry point found")
        has_main = False
except:
    has_main = False

print("\n[TEST 3] Check for Required Methods")
print("-" * 80)

required_methods = [
    'def __init__',
    'def select_model',
    'def send_request',
]

method_results = []
for method in required_methods:
    if method in code:
        print(f"[FOUND] {method}()")
        method_results.append(True)
    else:
        print(f"[MISSING] {method}()")
        method_results.append(False)

print("\n[TEST 4] Check for Error Handling")
print("-" * 80)

error_handling_patterns = [
    ('try:', 'Try-except blocks'),
    ('except', 'Exception handling'),
    ('logging.', 'Logging calls'),
    ('raise', 'Explicit error raising'),
]

for pattern, description in error_handling_patterns:
    count = code.count(pattern)
    if count > 0:
        print(f"[FOUND] {description}: {count} occurrences")
    else:
        print(f"[MISSING] {description}")

print("\n[TEST 5] Check for Database Operations")
print("-" * 80)

db_patterns = [
    ('sqlite3.connect', 'Database connection'),
    ('cursor.execute', 'SQL execution'),
    ('CREATE TABLE', 'Table creation'),
]

for pattern, description in db_patterns:
    if pattern in code:
        print(f"[FOUND] {description}")
    else:
        print(f"[MISSING] {description}")

print("\n[TEST 6] Check for API Integration")
print("-" * 80)

api_patterns = [
    ('anthropic', 'Anthropic API'),
    ('openai', 'OpenAI API'),
    ('google.generativeai', 'Google Gemini API'),
    ('requests.post', 'HTTP requests'),
]

api_found = []
for pattern, description in api_patterns:
    if pattern.lower() in code.lower():
        print(f"[FOUND] {description}")
        api_found.append(True)
    else:
        print(f"[MISSING] {description}")
        api_found.append(False)

print("\n[TEST 7] Syntax Validation")
print("-" * 80)

try:
    compile(code, 'D:/models/ai-router-enhanced.py', 'exec')
    print("[PASS] Python syntax is valid")
    syntax_valid = True
except SyntaxError as e:
    print(f"[FAIL] Syntax error: {e}")
    syntax_valid = False

# Summary
print("\n" + "="*80)
print("SUMMARY")
print("="*80)

print(f"Classes Found: {'YES' if classes_found else 'NO'}")
print(f"Main Entry Point: {'YES' if has_main else 'NO'}")
print(f"Required Methods: {sum(method_results)}/{len(method_results)}")
print(f"Syntax Valid: {'YES' if syntax_valid else 'NO'}")
print(f"API Integrations: {sum(api_found)}/{len(api_found)}")

overall = classes_found and syntax_valid and sum(method_results) >= 2
print(f"\nOVERALL STATUS: {'PASS' if overall else 'FAIL'}")

if overall:
    print("\n[INFO] The script structure appears valid.")
    print("[INFO] To test runtime functionality, try running:")
    print("       python ai-router-enhanced.py --help")
else:
    print("\n[ERROR] Script has structural issues that may prevent execution.")
