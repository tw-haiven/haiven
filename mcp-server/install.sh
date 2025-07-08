#!/bin/bash

echo ""
echo "========================================"
echo "  Haiven MCP Server Quick Install"
echo "  for AI Tools Integration"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Python is not installed"
    echo "Please install Python from https://python.org"
    echo "or use your system package manager:"
    echo "  macOS: brew install python"
    echo "  Ubuntu: sudo apt install python3"
    exit 1
fi

# Use python3 if available, otherwise python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

echo "✅ Python found"
echo ""

# Run the Python installer
echo "Starting easy installer..."
$PYTHON_CMD easy_install.py

echo ""
echo "Installation complete!"
echo "Please restart your AI tool (Claude Desktop, VS Code, Cursor, etc.) to see the changes."

# Wait for user input on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    read -p "Press any key to continue..."
fi 