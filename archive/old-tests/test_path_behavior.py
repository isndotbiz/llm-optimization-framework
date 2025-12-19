#!/usr/bin/env python3
"""
Test pathlib.Path behavior in WSL with Windows paths.
This helps debug why the documentation menu says "no files found".
"""

import pathlib
import os
import sys
from pathlib import Path

def test_path_variants():
    """Test different path representations."""
    
    print("=" * 70)
    print("PATH BEHAVIOR TEST FOR WSL")
    print("=" * 70)
    print()
    
    # Get system info
    print("System Information:")
    print(f"  Platform: {sys.platform}")
    print(f"  OS: {os.name}")
    print(f"  CWD: {os.getcwd()}")
    print()
    
    # Test paths
    test_cases = [
        ("D:/models", "Windows-style path with forward slashes"),
        ("D:\models", "Windows-style path with backslashes"),
        ("/d/models", "WSL mount with /d prefix"),
        ("/mnt/d/models", "WSL mount with /mnt/d prefix"),
    ]
    
    print("Path Resolution Tests:")
    print("-" * 70)
    
    for path_str, description in test_cases:
        print(f"\nTest: {description}")
        print(f"  Input: {path_str!r}")
        
        try:
            p = Path(path_str)
            print(f"  Path object: {p}")
            print(f"  Resolved: {p.resolve()}")
            print(f"  Exists: {p.exists()}")
            print(f"  Is directory: {p.is_dir()}")
            print(f"  Is file: {p.is_file()}")
            
            if p.exists() and p.is_dir():
                items = list(p.iterdir())
                print(f"  Contents: {len(items)} items found")
                print(f"  First 3 items:")
                for item in items[:3]:
                    print(f"    - {item.name}")
            else:
                print(f"  WARNING: Path does not exist or is not a directory")
                
        except Exception as e:
            print(f"  ERROR: {type(e).__name__}: {e}")
    
    print()
    print("=" * 70)
    print("RECOMMENDATION")
    print("=" * 70)
    
    # Test which path actually works
    working_paths = []
    for path_str, description in test_cases:
        try:
            p = Path(path_str)
            if p.exists() and p.is_dir():
                working_paths.append((path_str, description))
        except:
            pass
    
    if working_paths:
        print("\nWorking paths:")
        for path_str, description in working_paths:
            print(f"  [OK] {path_str!r} - {description}")
            
        print("\nRecommendation:")
        print(f"  Use: {working_paths[0][0]!r}")
        print("  This is the most reliable path for file discovery.")
    else:
        print("\nNo working paths found!")
    
    print()

if __name__ == "__main__":
    test_path_variants()
