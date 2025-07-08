#!/bin/bash

echo "🛠️  Quick Haiven MCP Development Setup"
echo "======================================"
echo ""

# Check if we're in the right directory
if [ ! -f "mcp_server.py" ]; then
    echo "❌ Run this script from the mcp-server directory"
    exit 1
fi

echo "1. 📦 Installing dependencies..."
poetry install

echo ""
echo "2. 🔧 Setting up environment..."
cat > .env << EOF
# Haiven MCP Development Environment
HAIVEN_API_URL=http://localhost:8080
HAIVEN_DISABLE_AUTH=true
EOF

echo "✅ Created .env file"
echo ""

echo "3. 🧪 Testing MCP server..."
export HAIVEN_API_URL=http://localhost:8080
export HAIVEN_DISABLE_AUTH=true

if poetry run python -c "from mcp_server import HaivenMCPServer; print('✅ MCP server imports OK')" 2>/dev/null; then
    echo "✅ MCP server test passed"
else
    echo "⚠️  MCP server test failed (but setup continues...)"
fi

echo ""
echo "4. 📋 Creating AI tool configs..."

# Current directory for config
CURRENT_DIR=$(pwd)

# Claude Desktop config (using absolute path to avoid cwd issues)
cat > claude-desktop-config.json << EOF
{
  "mcpServers": {
    "haiven-dev": {
      "command": "python",
      "args": ["$CURRENT_DIR/mcp_server.py"],
      "env": {
        "HAIVEN_API_URL": "http://localhost:8080",
        "HAIVEN_DISABLE_AUTH": "true"
      }
    }
  }
}
EOF

# Also create version with cwd for tools that support it
cat > claude-desktop-config-with-cwd.json << EOF
{
  "mcpServers": {
    "haiven-dev": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "$CURRENT_DIR",
      "env": {
        "HAIVEN_API_URL": "http://localhost:8080",
        "HAIVEN_DISABLE_AUTH": "true"
      }
    }
  }
}
EOF

echo "✅ Created claude-desktop-config.json (absolute path - recommended)"
echo "✅ Created claude-desktop-config-with-cwd.json (fallback)"

echo ""
echo "🎉 Development setup complete!"
echo "=============================="
echo ""
echo "Next steps:"
echo "1. Start Haiven backend: cd app && source .venv/bin/activate && python dev.py"
echo "2. Copy claude-desktop-config.json to ~/.config/claude/config.json"
echo "3. Restart your AI tool"
echo "4. Ask: 'What Haiven prompts are available?'"
echo ""
echo "💡 If you get 'cwd' errors, use claude-desktop-config.json (absolute path)"
echo "   If that doesn't work, try claude-desktop-config-with-cwd.json"
echo ""
echo "Quick test: source .env && poetry run python -c 'from mcp_server import HaivenMCPServer; print(\"OK\")'"
echo ""
echo "🛠️  Happy local development!" 