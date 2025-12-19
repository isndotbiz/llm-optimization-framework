@echo off
REM Installation script for MCP Server
REM Run this to install required dependencies

echo ========================================
echo MCP Server Installation
echo ========================================
echo.

echo Installing Python dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo ========================================
echo Installation complete!
echo ========================================
echo.
echo To test the server, run:
echo   python test_mcp_server.py
echo.
echo To start the server, run:
echo   python mcp_server.py
echo.

pause
