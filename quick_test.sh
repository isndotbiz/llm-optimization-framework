#!/bin/bash
# Quick test of the fixed router
(
  echo "2"      # Load Existing Project
  echo "1"      # Select "Ask" project
  echo "6"      # Run Chat Session
  echo "what is dns spoofing?"
  echo "exit"
  echo ""
) | timeout 120 python ai-router-enhanced.py 2>&1 | grep -A 30 "Assistant\|Error\|Successfully"
