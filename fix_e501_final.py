#!/usr/bin/env python3
"""Final E501 fixer - processes file line by line"""

from pathlib import Path

# All the line numbers that need fixing (from flake8 output)
LONG_LINES = {
    242, 351, 580, 648, 804, 813, 947, 948, 953, 954, 956, 957, 958, 959,
    1018, 1026, 1039, 1048, 1050, 1079, 1084, 1087, 1089, 1093, 1094, 1095,
    1117, 1125, 1127, 1192, 1235, 1236, 1237, 1238, 1239, 1249, 1258, 1267,
    1276, 1277, 1278, 1282, 1293, 1315, 1324, 1334, 1339, 1351, 1365, 1368,
    1370, 1371, 1376, 1379, 1384, 1389, 1401, 1418, 1420, 1421, 1422, 1423,
    1424, 1425, 1426, 1427, 1432, 1433, 1448, 1449, 1450, 1469, 1477, 1478,
    1479, 1480, 1485, 1488, 1489, 1490, 1498, 1513, 1514, 1517, 1518, 1524,
    1527, 1528, 1535, 1547, 1553, 1559, 1572, 1578, 1584, 1591, 1593, 1595,
    1596, 1598, 1604, 1617, 1624, 1625, 1629, 1645, 1652, 1653, 1660, 1672,
    1682, 1686, 1687, 1688, 1689, 1691, 1694, 1703, 1710, 1714, 1715, 1719,
    1728, 1732, 1734, 1744, 1753, 1764, 1765, 1766, 1771, 1782, 1784, 1785,
    1787, 1790, 1800, 1807, 1808, 1809, 1810, 1820, 1832, 1845, 1857, 1859,
    1863, 1873, 1880, 1882, 1883, 1885, 1887, 1893, 1900, 1902, 1905, 1915,
    1917, 1922, 1930, 1945
}

def fix_line(line, line_num):
    """Smart line fixing"""
    if len(line.rstrip()) <= 79:
        return line

    indent = len(line) - len(line.lstrip())
    indent_str = ' ' * indent
    extra_indent = ' ' * (indent + 4)

    # For lines that are just slightly over, try simple string continuation
    if len(line.rstrip()) <= 95:
        # Try to split at a logical point
        content = line.strip()

        # If it's a simple string, just continue it
        if content.startswith('print(') or content.startswith('input('):
            # Find a good break point
            if ' - ' in content:
                return line  # Leave complex ones for manual fixing
            elif ': ' in content and content.count(':') == 1:
                idx = content.index(': ')
                if 40 < idx < len(content) - 20:
                    part1 = content[:idx+2]
                    part2 = content[idx+2:]
                    return (indent_str + part1 + '\n' +
                            extra_indent + part2 + '\n')

    return line  # Return unchanged if can't auto-fix


def main():
    file_path = Path('D:/models/ai-router-enhanced.py')

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    for i, line in enumerate(lines, 1):
        if i in LONG_LINES:
            fixed = fix_line(line, i)
            new_lines.append(fixed)
        else:
            new_lines.append(line)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    print("Processing complete")


if __name__ == '__main__':
    main()
