#!/usr/bin/env python3
"""Test script to verify all referenced files exist for ai-router-enhanced.py"""

import os
import re

print("="*80)
print("AI ROUTER ENHANCED - REFERENCED FILES CHECK")
print("="*80)

base_path = 'D:/models'

# Read the main script
with open(f'{base_path}/ai-router-enhanced.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract file references from the code
file_patterns = [
    (r'\.ai-router-preferences\.json', 'Preferences file'),
    (r'\.ai-router-sessions\.db', 'Sessions database'),
    (r'system-prompts/', 'System prompts directory'),
    (r'prompt-templates/', 'Prompt templates directory'),
    (r'context-templates/', 'Context templates directory'),
    (r'workflows/', 'Workflows directory'),
    (r'outputs/', 'Outputs directory'),
    (r'schema\.sql', 'Database schema'),
    (r'requirements\.txt', 'Requirements file'),
]

print("\n[TEST] File and Directory References")
print("-" * 80)

results = []

# Check each pattern
for pattern, description in file_patterns:
    # Find if pattern exists in code
    if re.search(pattern, content):
        # Determine actual path
        clean_pattern = pattern.replace('\\', '').replace(r'\\.', '.')

        if clean_pattern.endswith('/'):
            # Directory
            path = os.path.join(base_path, clean_pattern.rstrip('/'))
            exists = os.path.isdir(path)
            type_str = "DIR"
        else:
            # File
            path = os.path.join(base_path, clean_pattern)
            exists = os.path.isfile(path)
            type_str = "FILE"

        status = "EXISTS" if exists else "MISSING"
        print(f"[{status}] {type_str:4s} {description:30s} -> {clean_pattern}")
        results.append(exists)
    else:
        print(f"[SKIP] {description} - not referenced in code")

# Check for system prompt files
print("\n[TEST] System Prompt Files")
print("-" * 80)

system_prompts_dir = os.path.join(base_path, 'system-prompts')
if os.path.isdir(system_prompts_dir):
    prompt_files = [f for f in os.listdir(system_prompts_dir) if f.endswith('.txt')]
    if prompt_files:
        print(f"[PASS] Found {len(prompt_files)} system prompt files:")
        for pf in prompt_files[:5]:  # Show first 5
            print(f"       - {pf}")
        if len(prompt_files) > 5:
            print(f"       ... and {len(prompt_files) - 5} more")
    else:
        print("[WARNING] system-prompts directory exists but is empty")
else:
    print("[FAIL] system-prompts directory not found")

# Check for template directories
print("\n[TEST] Template Directories")
print("-" * 80)

template_dirs = ['prompt-templates', 'context-templates']
for td in template_dirs:
    td_path = os.path.join(base_path, td)
    if os.path.isdir(td_path):
        files = os.listdir(td_path)
        print(f"[EXISTS] {td:20s} ({len(files)} items)")
    else:
        print(f"[MISSING] {td}")

# Check workflow directory
print("\n[TEST] Workflow Directory")
print("-" * 80)

workflows_dir = os.path.join(base_path, 'workflows')
if os.path.isdir(workflows_dir):
    yaml_files = [f for f in os.listdir(workflows_dir) if f.endswith(('.yaml', '.yml'))]
    print(f"[EXISTS] workflows directory ({len(yaml_files)} YAML files)")
else:
    print("[MISSING] workflows directory")

# Summary
print("\n" + "="*80)
print("SUMMARY")
print("="*80)

critical_files = [
    ('schema.sql', os.path.join(base_path, 'schema.sql')),
    ('requirements.txt', os.path.join(base_path, 'requirements.txt')),
]

print("Critical Files:")
for name, path in critical_files:
    exists = os.path.isfile(path)
    status = "EXISTS" if exists else "MISSING"
    print(f"  [{status}] {name}")

print("\nOptional Directories:")
optional_dirs = [
    'system-prompts',
    'prompt-templates',
    'context-templates',
    'workflows',
    'outputs'
]

for dirname in optional_dirs:
    dirpath = os.path.join(base_path, dirname)
    exists = os.path.isdir(dirpath)
    status = "EXISTS" if exists else "MISSING"
    print(f"  [{status}] {dirname}/")

print("\nNOTE: Missing optional directories will be created at runtime if needed.")
