# 🛠️ Developer Guide: Local Haiven MCP Setup

**For developers testing against local Haiven instances**

This guide shows how to quickly set up the MCP server for local development with authentication disabled.

💡 **Super Quick Setup**: Run `./dev_setup.sh` (Mac/Linux) or `python dev_setup.py` (All platforms) to automate most of this process!

## 🚀 **Quick Start (5 minutes)**

### **1. Start Local Haiven Backend**
```bash
# In the main haiven directory
cd app
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
python dev.py
```

Your local Haiven should be running at `http://localhost:8080`

### **2. Setup MCP Server for Local Development**
```bash
# In the mcp-server directory
cd mcp-server
poetry install
```

### **3. Configure for Local Development**
Create a `.env` file in the `mcp-server` directory:
```bash
# .env file for local development
HAIVEN_API_URL=http://localhost:8080
HAIVEN_DISABLE_AUTH=true
```

### **4. Test the MCP Server**
```bash
# Test basic functionality
poetry run python -c "
import os
os.environ['HAIVEN_API_URL'] = 'http://localhost:8080'
os.environ['HAIVEN_DISABLE_AUTH'] = 'true'
from mcp_server import HaivenMCPServer
print('✅ MCP server imports successfully')
"
```

### **5. Configure Your AI Tool**
**Claude Desktop example** (`~/.config/claude/config.json`):
```json
{
  "mcpServers": {
    "haiven-dev": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "/path/to/haiven/mcp-server",
      "env": {
        "HAIVEN_API_URL": "http://localhost:8080",
        "HAIVEN_DISABLE_AUTH": "true"
      }
    }
  }
}
```

**VS Code example** (settings.json):
```json
{
  "mcp.servers": {
    "haiven-dev": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "/path/to/haiven/mcp-server",
      "env": {
        "HAIVEN_API_URL": "http://localhost:8080",
        "HAIVEN_DISABLE_AUTH": "true"
      }
    }
  }
}
```

### **6. Test in Your AI Tool**
Restart your AI tool and ask:
> "What Haiven prompts are available?"

You should see prompts from your local Haiven instance!

---

## 🔧 **Development Workflow**

### **Starting Development Session**
```bash
# Terminal 1: Start Haiven backend
cd app && source .venv/bin/activate && python dev.py

# Terminal 2: Test MCP server (optional)
cd mcp-server && poetry run python mcp_server.py --help
```

### **Quick Testing Without AI Tool**
```bash
# Direct test of MCP server
cd mcp-server
export HAIVEN_API_URL="http://localhost:8080"
export HAIVEN_DISABLE_AUTH="true"
poetry run python -c "
import asyncio
from mcp_server import HaivenMCPServer

async def test():
    server = HaivenMCPServer()
    result = await server.handle_get_prompts()
    print('Available prompts:', len(result))
    print('First prompt:', result[0] if result else 'No prompts found')

asyncio.run(test())
"
```

### **Testing Different Scenarios**
```bash
# Test with authentication enabled (requires API key)
export HAIVEN_API_URL="http://localhost:8080"
export HAIVEN_API_KEY="your-dev-api-key"
unset HAIVEN_DISABLE_AUTH

# Test against remote instance
export HAIVEN_API_URL="https://your-remote-haiven.com"
export HAIVEN_API_KEY="your-remote-api-key"
```

---

## 🧪 **Testing & Debugging**

### **Enable Debug Logging**
```bash
export PYTHONPATH=.
export HAIVEN_API_URL="http://localhost:8080"
export HAIVEN_DISABLE_AUTH="true"
poetry run python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from mcp_server import HaivenMCPServer
print('Debug logging enabled')
"
```

### **Test API Connectivity**
```bash
# Quick connectivity test
curl http://localhost:8080/api/prompts
```

### **Test Authentication (when enabled)**
```bash
# Test API key authentication
curl -H "Authorization: Bearer \$HAIVEN_API_KEY" http://localhost:8080/api/prompts
```

---

## 🚨 **Common Issues & Solutions**

### **"Connection refused" errors**
```bash
# Check if Haiven backend is running
curl http://localhost:8080/health

# Check logs
cd app && tail -f logs/haiven.log
```

### **"No prompts found"**
```bash
# Check if prompts are loaded in your local instance
curl http://localhost:8080/api/prompts | jq '.[0].id'
```

### **MCP server not connecting**
```bash
# Test basic import
poetry run python -c "from mcp_server import HaivenMCPServer; print('OK')"

# Test with environment variables
env HAIVEN_API_URL=http://localhost:8080 HAIVEN_DISABLE_AUTH=true poetry run python mcp_server.py
```

---

## 🎯 **Development Tips**

### **Multiple Environment Setup**
Create different config files for different environments:

```bash
# dev.env
HAIVEN_API_URL=http://localhost:8080
HAIVEN_DISABLE_AUTH=true

# staging.env  
HAIVEN_API_URL=https://staging.haiven.com
HAIVEN_API_KEY=staging-api-key

# prod.env
HAIVEN_API_URL=https://prod.haiven.com
HAIVEN_API_KEY=prod-api-key
```

Load with:
```bash
# Load environment
source dev.env && poetry run python mcp_server.py
```

### **Rapid Iteration**
```bash
# Watch for changes and restart (if using watchdog)
poetry run watchmedo auto-restart --pattern="*.py" poetry run python mcp_server.py
```

### **Integration Testing**
```bash
# Test against real deployment
export HAIVEN_API_URL="https://haiven.your-company.com"
export HAIVEN_API_KEY="your-real-api-key"
poetry run python test_integration.py
```

---

## 🔄 **Switching Between Configurations**

### **Quick Config Switch**
```bash
# Local development
export HAIVEN_API_URL="http://localhost:8080" && export HAIVEN_DISABLE_AUTH="true"

# Remote testing  
export HAIVEN_API_URL="https://your-remote.com" && export HAIVEN_API_KEY="your-key" && unset HAIVEN_DISABLE_AUTH
```

### **AI Tool Config for Development**
You can have multiple MCP servers configured:
```json
{
  "mcpServers": {
    "haiven-local": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "/path/to/mcp-server",
      "env": {
        "HAIVEN_API_URL": "http://localhost:8080",
        "HAIVEN_DISABLE_AUTH": "true"
      }
    },
    "haiven-staging": {
      "command": "python", 
      "args": ["mcp_server.py"],
      "cwd": "/path/to/mcp-server",
      "env": {
        "HAIVEN_API_URL": "https://staging.haiven.com",
        "HAIVEN_API_KEY": "staging-key"
      }
    }
  }
}
```

---

## 📋 **Development Checklist**

- [ ] ✅ Local Haiven backend running (`python dev.py`)
- [ ] ✅ MCP server dependencies installed (`poetry install`)
- [ ] ✅ Environment variables set (`HAIVEN_API_URL`, `HAIVEN_DISABLE_AUTH`)
- [ ] ✅ AI tool configured with local MCP server
- [ ] ✅ Basic connectivity tested (`curl http://localhost:8080/api/prompts`)
- [ ] ✅ MCP server responds to prompts query
- [ ] ✅ Can execute prompts through AI tool

**Happy local development! 🚀** 