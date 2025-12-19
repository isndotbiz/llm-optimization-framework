#!/usr/bin/env python3
"""
Comprehensive guide for proper path detection in cross-platform environments.
Use this as a reference for fixing the "no files found" issue.
"""

import os
import sys
from pathlib import Path

class PathDetector:
    """Detects and resolves paths across Windows/WSL/Linux environments."""
    
    @staticmethod
    def get_platform_info():
        """Get current platform information."""
        return {
            'platform': sys.platform,
            'os_name': os.name,
            'is_windows': sys.platform == 'win32' and os.name == 'nt',
            'is_wsl': sys.platform == 'linux' and os.path.exists('/proc/version') and 'microsoft' in open('/proc/version').read().lower(),
            'is_linux': sys.platform == 'linux' and not os.path.exists('/proc/version'),
        }
    
    @staticmethod
    def find_models_directory():
        """Find the models directory regardless of OS/WSL configuration."""
        
        # Try Windows paths first
        windows_paths = [
            Path("D:/models"),
            Path("D:\models"),
            Path(os.path.expanduser("~/models")),
        ]
        
        # Try WSL/Linux paths
        linux_paths = [
            Path("/d/models"),
            Path("/mnt/d/models"),
            Path("/wsl/d/models"),
        ]
        
        # On Windows, try Windows paths first
        if sys.platform == 'win32':
            paths_to_try = windows_paths + linux_paths
        else:
            paths_to_try = linux_paths + windows_paths
        
        for path in paths_to_try:
            try:
                if path.exists() and path.is_dir():
                    return path.resolve()
            except Exception as e:
                pass
        
        return None
    
    @staticmethod
    def list_files(directory_path):
        """List files in a directory with error handling."""
        try:
            path = Path(directory_path)
            if not path.exists():
                return f"ERROR: Path does not exist: {path.resolve()}"
            
            if not path.is_dir():
                return f"ERROR: Path is not a directory: {path.resolve()}"
            
            items = list(path.iterdir())
            return items
            
        except Exception as e:
            return f"ERROR: {type(e).__name__}: {e}"

def main():
    print("=" * 70)
    print("COMPREHENSIVE PATH DETECTION GUIDE")
    print("=" * 70)
    print()
    
    # Show platform info
    info = PathDetector.get_platform_info()
    print("Detected Platform:")
    print(f"  sys.platform: {info['platform']}")
    print(f"  os.name: {info['os_name']}")
    print(f"  Is Windows: {info['is_windows']}")
    print(f"  Is WSL: {info['is_wsl']}")
    print(f"  Is Linux: {info['is_linux']}")
    print()
    
    # Try to find models directory
    print("Searching for models directory...")
    models_dir = PathDetector.find_models_directory()
    print()
    
    if models_dir:
        print(f"Found: {models_dir}")
        print()
        
        # List contents
        print("Directory Contents:")
        items = PathDetector.list_files(models_dir)
        
        if isinstance(items, str):
            print(f"  {items}")
        else:
            print(f"  Total items: {len(items)}")
            print()
            print("  First 10 items:")
            for item in items[:10]:
                item_type = "[DIR]" if item.is_dir() else "[FILE]"
                print(f"    {item_type} {item.name}")
    else:
        print("ERROR: Could not find models directory!")
        print()
        print("Diagnostic Info:")
        print("  - Tried Windows paths: D:/models, D:\models, ~/models")
        print("  - Tried WSL paths: /d/models, /mnt/d/models, /wsl/d/models")
        print("  - None of these paths exist or are accessible")
    
    print()
    print("=" * 70)
    print("CODE EXAMPLE: How to fix 'no files found' errors")
    print("=" * 70)
    print()
    print("def get_models_path():")
    print("    import sys")
    print("    from pathlib import Path")
    print()
    print("    candidates = [")
    print("        Path('D:/models'),")
    print("        Path('D:\\models'),")
    print("        Path('/d/models'),")
    print("        Path('/mnt/d/models'),")
    print("    ]")
    print()
    print("    for path in candidates:")
    print("        if path.exists() and path.is_dir():")
    print("            return path.resolve()")
    print()
    print("    raise FileNotFoundError('Models directory not found')")
    print()

if __name__ == "__main__":
    main()
