#!/usr/bin/env python3
"""Test script to check imports and dependencies for ai-router-enhanced.py"""

import sys
import os

print("="*80)
print("AI ROUTER ENHANCED - RUNTIME IMPORTS TEST")
print("="*80)

# Test 1: Standard library imports
print("\n[TEST 1] Standard Library Imports")
print("-" * 80)
std_imports = [
    'os', 'sys', 'json', 'sqlite3', 'datetime', 'pathlib',
    'subprocess', 'shutil', 'logging', 're', 'time'
]

std_results = []
for module in std_imports:
    try:
        __import__(module)
        print(f"[PASS] {module}")
        std_results.append(True)
    except ImportError as e:
        print(f"[FAIL] {module}: {e}")
        std_results.append(False)

# Test 2: Third-party imports
print("\n[TEST 2] Third-Party Imports")
print("-" * 80)
third_party = {
    'requests': 'requests',
    'yaml': 'PyYAML',
    'anthropic': 'anthropic',
    'openai': 'openai',
    'google.generativeai': 'google-generativeai'
}

third_party_results = []
for module, package in third_party.items():
    try:
        __import__(module)
        print(f"[PASS] {module} ({package})")
        third_party_results.append(True)
    except ImportError as e:
        print(f"[FAIL] {module} ({package}): {e}")
        third_party_results.append(False)

# Test 3: Check if main script can be imported
print("\n[TEST 3] Main Script Import")
print("-" * 80)
try:
    sys.path.insert(0, 'D:/models')
    # Don't actually import to avoid running the script
    with open('D:/models/ai-router-enhanced.py', 'r', encoding='utf-8') as f:
        content = f.read()
        if 'class' in content and 'def' in content:
            print("[PASS] ai-router-enhanced.py structure valid")
            script_readable = True
        else:
            print("[FAIL] ai-router-enhanced.py structure invalid")
            script_readable = False
except Exception as e:
    print(f"[FAIL] ai-router-enhanced.py import check: {e}")
    script_readable = False

# Test 4: Check for required environment variables (not mandatory but good to know)
print("\n[TEST 4] Environment Variables")
print("-" * 80)
env_vars = [
    'ANTHROPIC_API_KEY',
    'OPENAI_API_KEY',
    'GEMINI_API_KEY'
]

for var in env_vars:
    if os.getenv(var):
        print(f"[SET] {var}")
    else:
        print(f"[NOT SET] {var} (optional)")

# Summary
print("\n" + "="*80)
print("SUMMARY")
print("="*80)
total_std = len(std_results)
passed_std = sum(std_results)
total_third = len(third_party_results)
passed_third = sum(third_party_results)

print(f"Standard Library: {passed_std}/{total_std} PASSED")
print(f"Third-Party: {passed_third}/{total_third} PASSED")
print(f"Script Structure: {'PASS' if script_readable else 'FAIL'}")

overall = all(std_results) and script_readable
print(f"\nOVERALL STATUS: {'PASS' if overall else 'FAIL'}")

if not all(third_party_results):
    print("\n[WARNING] Some third-party dependencies missing.")
    print("Run: pip install -r requirements.txt")

sys.exit(0 if overall else 1)
