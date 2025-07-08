#!/bin/bash

# Start Haiven MCP Server
# This script starts the independent MCP server for Haiven prompts API

set -e

# Configuration
HAIVEN_API_URL=${HAIVEN_API_URL:-"http://localhost:8000"}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "================================================"
echo "Starting Haiven MCP Server"
echo "================================================"
echo "API URL: $HAIVEN_API_URL"
echo "Server directory: $SCRIPT_DIR"
echo "================================================"

# Check if we're in the correct directory
if [[ ! -f "$SCRIPT_DIR/mcp_server.py" ]]; then
    echo "Error: mcp_server.py not found in $SCRIPT_DIR"
    echo "Please run this script from the mcp-server directory"
    exit 1
fi

# Check if poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "Error: Poetry is not installed. Please install Poetry first."
    echo "Visit: https://python-poetry.org/docs/#installation"
    exit 1
fi

# Check if virtual environment exists and dependencies are installed
if [[ ! -d "$SCRIPT_DIR/.venv" ]]; then
    echo "Virtual environment not found. Installing dependencies..."
    cd "$SCRIPT_DIR"
    poetry install
fi

# Check if MCP dependencies are installed
cd "$SCRIPT_DIR"
if ! poetry run python -c "import mcp" 2>/dev/null; then
    echo "MCP dependencies not found. Installing..."
    poetry install
fi

# Export environment variables
export HAIVEN_API_URL="$HAIVEN_API_URL"

# Check for authentication configuration
if [[ -z "$HAIVEN_SESSION_COOKIE" && -z "$HAIVEN_API_KEY" ]]; then
    echo ""
    echo "⚠️  WARNING: No authentication configured!"
    echo ""
    echo "Haiven APIs are protected by OKTA authentication by default."
    echo "You have three options:"
    echo ""
    echo "1. Development mode (recommended for testing):"
    echo "   Set AUTH_SWITCHED_OFF=true on your Haiven server"
    echo ""
    echo "2. Session cookie authentication:"
    echo "   export HAIVEN_SESSION_COOKIE=\"your_session_cookie\""
    echo "   See AUTHENTICATION.md for detailed instructions"
    echo ""
    echo "3. API key authentication (if available):"
    echo "   export HAIVEN_API_KEY=\"your_api_key\""
    echo ""
    echo "Press Enter to continue anyway, or Ctrl+C to exit..."
    read -r
fi

# Start the MCP server
echo "Starting MCP server..."
poetry run python mcp_server.py "$HAIVEN_API_URL" 