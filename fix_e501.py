#!/usr/bin/env python3
"""Script to fix all E501 line too long errors in ai-router-enhanced.py"""

import re
from pathlib import Path


def fix_long_line(line: str, line_num: int, indent: str) -> list:
    """Fix a long line by intelligently splitting it"""
    line = line.rstrip()

    # If line is a print statement with f-string
    if 'print(' in line and 'f"' in line:
        # Extract the content
        match = re.match(r'(\s*)print\((f"[^"]*")\)', line)
        if match and len(line) > 79:
            spaces, content = match.groups()
            # Split f-string intelligently
            parts = []
            current = ""
            in_color = False

            for char in content[2:-1]:  # Skip f" and "
                current += char
                if char == '{':
                    in_color = True
                elif char == '}':
                    in_color = False
                elif char == ' ' and not in_color and len(current) > 35:
                    parts.append(current.rstrip())
                    current = ""

            if current:
                parts.append(current)

            if len(parts) > 1:
                result = [f'{spaces}print(\n']
                for i, part in enumerate(parts):
                    if i == len(parts) - 1:
                        result.append(f'{spaces}    f"{part}"\n')
                    else:
                        result.append(f'{spaces}    f"{part}"\n')
                result.append(f'{spaces})\n')
                return result

    # If line has Colors constants, split after them
    if '{Colors.' in line and len(line) > 79:
        # Try to split after color codes
        parts = re.split(r'(\{Colors\.[^}]+\})', line)
        if len(parts) > 3:
            # Reconstruct with line breaks
            result = []
            current_line = ""
            for part in parts:
                if len(current_line + part) > 75 and current_line:
                    result.append(current_line + '"\n')
                    current_line = indent + '    f"'
                current_line += part
            if current_line:
                result.append(current_line)
            if len(result) > 1:
                return [r + '\n' for r in result]

    # Default: wrap in parentheses if it's an assignment or function call
    if '=' in line or '(' in line:
        # Try simple parenthetical wrap
        if len(line) > 79:
            mid = len(line) // 2
            # Find a good break point near middle
            for offset in range(20):
                for pos in [mid + offset, mid - offset]:
                    if 0 < pos < len(line) and line[pos] in [' ', ',', '+']:
                        return [
                            line[:pos+1].rstrip() + '\n',
                            indent + '    ' + line[pos+1:].lstrip() + '\n'
                        ]

    return [line + '\n']


def main():
    file_path = Path('D:/models/ai-router-enhanced.py')

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    for i, line in enumerate(lines, 1):
        # Get indentation
        indent = len(line) - len(line.lstrip())
        indent_str = line[:indent]

        if len(line.rstrip()) <= 79:
            new_lines.append(line)
        else:
            # Try to fix the line
            fixed = fix_long_line(line, i, indent_str)
            if len(fixed) == 1 and fixed[0] == line + '\n':
                # Couldn't fix automatically, just keep original
                new_lines.append(line)
            else:
                new_lines.extend(fixed)

    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    print("File fixed - please review changes")


if __name__ == '__main__':
    main()
