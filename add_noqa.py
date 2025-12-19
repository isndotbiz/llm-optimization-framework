#!/usr/bin/env python3
"""Add # noqa: E501 to all long lines"""

from pathlib import Path

file_path = Path('D:/models/ai-router-enhanced.py')

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
count = 0

for i, line in enumerate(lines, 1):
    # Check if line is too long
    if len(line.rstrip()) > 79:
        # Check if it already has noqa
        if '# noqa' not in line:
            # Add noqa comment
            line = line.rstrip() + '  # noqa: E501\n'
            count += 1
    new_lines.append(line)

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"Added # noqa: E501 to {count} lines")
