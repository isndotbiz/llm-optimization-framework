#!/usr/bin/env python3
"""
Diagnostic script to identify path detection issues.
Helps determine why the documentation menu reports "no files found".
"""

import os
import sys
from pathlib import Path
import subprocess

def diagnose():
    print("=" * 70)
    print("ENVIRONMENT DIAGNOSIS")
    print("=" * 70)
    print()
    
    # Environment variables related to paths
    print("Environment Variables:")
    path_vars = ['PATH', 'PYTHONPATH', 'WSLENV', 'WSL_DISTRO_NAME', 'WSL_INTEROP']
    for var in path_vars:
        val = os.environ.get(var)
        if val:
            print(f"  {var}: {val[:80]}...")
        else:
            print(f"  {var}: (not set)")
    print()
    
    # Check if running under WSL
    print("WSL Detection:")
    try:
        with open('/proc/version', 'r') as f:
            proc_version = f.read()
            is_wsl = 'microsoft' in proc_version.lower() or 'wsl' in proc_version.lower()
            print(f"  /proc/version check: {'WSL detected' if is_wsl else 'Native Windows'}")
    except:
        print(f"  /proc/version check: Not in WSL (Windows)")
    
    # Check platform
    print(f"  sys.platform: {sys.platform}")
    print(f"  os.name: {os.name}")
    print()
    
    # Test path handling
    print("Path Handling Test:")
    print("-" * 70)
    
    # Current directory
    cwd = os.getcwd()
    print(f"  Current directory: {cwd}")
    
    # Try to detect the base path
    if 'd:' in cwd.lower():
        print(f"  Running from: Windows drive D:")
    
    # Check if common WSL paths exist
    print()
    print("WSL Path Availability:")
    wsl_paths = [
        "/d/models",
        "/mnt/d/models",
        "/wsl/d/models",
    ]
    for wsl_path in wsl_paths:
        exists = Path(wsl_path).exists()
        print(f"  {wsl_path}: {'EXISTS' if exists else 'NOT FOUND'}")
    print()
    
    # Path detection strategy
    print("=" * 70)
    print("PATH DETECTION STRATEGY")
    print("=" * 70)
    print()
    print("For file discovery, use this strategy:")
    print("  1. Check os.name and sys.platform")
    print("  2. If Windows (os.name == 'nt', sys.platform == 'win32'):")
    print("     - Use Windows paths like 'D:/models' or D:\models")
    print("  3. If Linux/WSL (os.name == 'posix'):")
    print("     - Try '/d/models' first (native WSL mount)")
    print("     - Fall back to '/mnt/d/models' if needed")
    print("  4. Always use Path.resolve() and Path.exists() to verify")
    print()

if __name__ == "__main__":
    diagnose()
