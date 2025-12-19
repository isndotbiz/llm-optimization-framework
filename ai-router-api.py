#!/usr/bin/env python3
"""
TrueNAS AI Router - REST API Only Mode
No interactive menu - just API server
"""

import sys
import os
from pathlib import Path

# Add models directory to path
sys.path.insert(0, '/mnt/models')

from ai_router_truenas_production import ProductionAIRouter

if __name__ == "__main__":
    print("\n" + "="*80)
    print("TrueNAS AI Router - API Server Mode")
    print("="*80)
    print("\n📡 Starting REST API Server...")
    print("🌐 API Available at: http://10.0.0.89:5000")
    print("   - GET  /api/health    → Check GPU status")
    print("   - GET  /api/models    → List available models")
    print("   - GET  /api/projects  → List projects")
    print("\n⏹️  Press Ctrl+C to stop server\n")

    router = ProductionAIRouter()
    router.start_api_server()
