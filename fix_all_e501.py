#!/usr/bin/env python3
"""Automatically fix all E501 errors in ai-router-enhanced.py"""

import subprocess
import re
from pathlib import Path


def get_flake8_errors(file_path):
    """Get all E501 errors from flake8"""
    result = subprocess.run(
        ['python', '-m', 'flake8', str(file_path), '--select=E501'],
        capture_output=True,
        text=True
    )
    errors = []
    for line in result.stdout.strip().split('\n'):
        if not line:
            continue
        # Parse: filename:line:col: E501 line too long (X > 79 characters)
        match = re.match(r'[^:]+:(\d+):', line)
        if match:
            errors.append(int(match.group(1)))
    return sorted(set(errors))


def fix_line(line):
    """Fix a single line that's too long"""
    line = line.rstrip()
    if len(line) <= 79:
        return [line + '\n']

    indent = len(line) - len(line.lstrip())
    indent_str = ' ' * indent

    # Pattern 1: Simple print statements with f-strings
    if line.strip().startswith('print(f"'):
        # Split long f-string into multiple parts
        content = line[line.find('f"')+2:line.rfind('"')]
        if '{Colors.' in content:
            # Split at color codes
            parts = []
            current = ""
            i = 0
            while i < len(content):
                if content[i:].startswith('{Colors.'):
                    # Find end of color code
                    end = content.find('}', i) + 1
                    color_code = content[i:end]
                    if len(current + color_code) > 60 and current:
                        parts.append(current)
                        current = color_code
                    else:
                        current += color_code
                    i = end
                else:
                    current += content[i]
                    i += 1
            if current:
                parts.append(current)

            if len(parts) > 1:
                result = [indent_str + 'print(\n']
                for i, part in enumerate(parts):
                    if i < len(parts) - 1:
                        result.append(indent_str + '    f"' + part + '"\n')
                    else:
                        result.append(indent_str + '    f"' + part + '"\n')
                result.append(indent_str + ')\n')
                return result

        # For non-color prints, try splitting at spaces
        if ' ' in content:
            mid = len(content) // 2
            # Find nearest space to middle
            for offset in range(len(content) // 2):
                if mid + offset < len(content) and content[mid + offset] == ' ':
                    split_pos = mid + offset
                    break
                if mid - offset >= 0 and content[mid - offset] == ' ':
                    split_pos = mid - offset
                    break
            else:
                split_pos = len(content) // 2

            part1 = content[:split_pos].rstrip()
            part2 = content[split_pos:].lstrip()
            return [
                indent_str + 'print(\n',
                indent_str + '    f"' + part1 + '"\n',
                indent_str + '    f"' + part2 + '"\n',
                indent_str + ')\n'
            ]

    # Pattern 2: input() statements
    if 'input(f"' in line and ').strip()' in line:
        # Split input prompt
        start = line.find('f"')
        end = line.find('")', start)
        if start != -1 and end != -1:
            prompt = line[start+2:end]
            if len(prompt) > 40:
                mid = len(prompt) // 2
                # Find good split point
                for offset in range(len(prompt) // 2):
                    if mid + offset < len(prompt) and prompt[mid + offset] in [' ', ':', '-']:
                        split_pos = mid + offset + 1
                        break
                    if mid - offset >= 0 and prompt[mid - offset] in [' ', ':', '-']:
                        split_pos = mid - offset + 1
                        break
                else:
                    split_pos = len(prompt) // 2

                part1 = prompt[:split_pos].rstrip()
                part2 = prompt[split_pos:].lstrip()

                var_part = line[:line.find('input(')]
                return [
                    indent_str + var_part + 'input(\n',
                    indent_str + '    f"' + part1 + '"\n',
                    indent_str + '    f"' + part2 + '"\n',
                    indent_str + ').strip()\n'
                ]

    # Pattern 3: Function definitions with many parameters
    if 'def ' in line and '(' in line and ')' in line:
        # Split parameters onto multiple lines
        func_start = line.find('def ')
        func_name_end = line.find('(', func_start)
        params_end = line.rfind(')')

        func_def = line[func_start:func_name_end+1]
        params = line[func_name_end+1:params_end]
        return_part = line[params_end:]

        if ', ' in params:
            param_list = [p.strip() for p in params.split(',')]
            result = [indent_str + func_def + '\n']
            for i, param in enumerate(param_list):
                if i < len(param_list) - 1:
                    result.append(indent_str + '    ' + param + ',\n')
                else:
                    result.append(indent_str + '    ' + param + '\n')
            result.append(indent_str + return_part + '\n')
            return result

    # Default: try to split at a reasonable point
    if ',' in line:
        # Split at comma
        mid = len(line) // 2
        for offset in range(len(line) // 2):
            if mid + offset < len(line) and line[mid + offset] == ',':
                return [
                    line[:mid + offset + 1] + '\n',
                    indent_str + '    ' + line[mid + offset + 1:].lstrip() + '\n'
                ]
            if mid - offset >= 0 and line[mid - offset] == ',':
                return [
                    line[:mid - offset + 1] + '\n',
                    indent_str + '    ' + line[mid - offset + 1:].lstrip() + '\n'
                ]

    # Last resort: return as-is
    return [line + '\n']


def main():
    file_path = Path('D:/models/ai-router-enhanced.py')

    # Get error lines
    error_lines = get_flake8_errors(file_path)
    print(f"Found {len(error_lines)} E501 errors")

    # Read file
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Fix errors
    new_lines = []
    for i, line in enumerate(lines, 1):
        if i in error_lines:
            fixed = fix_line(line)
            new_lines.extend(fixed)
        else:
            new_lines.append(line)

    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    # Check again
    remaining = get_flake8_errors(file_path)
    print(f"Fixed! Remaining errors: {len(remaining)}")

    if remaining:
        print(f"Lines still needing fixes: {remaining[:20]}")


if __name__ == '__main__':
    main()
