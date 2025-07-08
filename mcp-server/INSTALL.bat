@echo off
echo.
echo ========================================
echo   Haiven MCP Server Quick Install
echo   for AI Tools Integration
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python from https://python.org
    echo Make sure to check "Add to PATH" during installation
    pause
    exit /b 1
)

echo ✅ Python found
echo.

REM Run the Python installer
echo Starting easy installer...
python easy_install.py

echo.
echo Installation complete! 
echo Please restart your AI tool (Claude Desktop, VS Code, Cursor, etc.) to see the changes.
pause 