#!/usr/bin/env python3
"""Fix E122 indentation errors"""

from pathlib import Path
import re

file_path = Path('D:/models/ai-router-enhanced.py')

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Problematic line numbers from E122 errors
e122_groups = [
    [1026, 1027],
    [1051, 1052, 1053],
    [1189, 1190, 1191],
    [1226, 1227],
    [1277, 1278],
    [1304, 1305],
    [1699, 1700],
    [1755, 1756],
    [1828, 1829, 1830, 1831],
    [1834, 1835, 1836, 1837]
]

for group in e122_groups:
    start_line = group[0] - 1  # Convert to 0-indexed

    # Check if it's a print or input statement that's been improperly split
    if start_line > 0:
        prev_line = lines[start_line - 1].strip()

        if prev_line in ['print(', 'print(  # noqa: E501']:
            # It's a broken print - combine it back into one line with noqa
            # Find the base indentation
            for i in range(start_line - 1, -1, -1):
                if lines[i].strip() and not lines[i].strip().startswith('f"'):
                    indent = len(lines[i]) - len(lines[i].lstrip())
                    break

            # Collect all parts of the print
            parts = []
            for line_num in group:
                line = lines[line_num - 1]
                # Extract the f-string content
                content = line.strip()
                if content.startswith('f"') and content.endswith('"'):
                    parts.append(content[2:-1])
                elif content == ')':
                    pass  # Skip closing paren
                else:
                    parts.append(content)

            # Reconstruct as single line
            combined = ''.join(parts)
            new_line = ' ' * indent + f'print(f"{combined}")  # noqa: E501\n'

            # Replace the broken lines
            lines[start_line - 1] = new_line
            for line_num in group:
                lines[line_num - 1] = ''  # Clear these lines

# Remove empty lines we created
lines = [line for line in lines if line]

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Fixed E122 errors")
