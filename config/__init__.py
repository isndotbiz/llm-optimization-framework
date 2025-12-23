"""
Config package - Central configuration module for AI Router

This package provides centralized model configuration to eliminate duplication
across all router implementations.
"""

from config.models import ModelDatabase

__all__ = ['ModelDatabase']
