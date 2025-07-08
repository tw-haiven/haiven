# 🔧 MCP Server Troubleshooting Guide

## 🚨 Common Issues & Solutions

### **"cwd" Parameter Errors**

**Problem**: AI tool shows errors like "cwd not found", "invalid directory", or "path does not exist"

**Solutions**:

#### **1. Use Absolute Path (Most Common Fix)**
```json
{
  "mcpServers": {
    "haiven": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "/Users/yourname/path/to/haiven/mcp-server",  // ✅ Absolute path
      "env": {
        "HAIVEN_API_URL": "http://localhost:8080",
        "HAIVEN_DISABLE_AUTH": "true"
      }
    }
  }
}
```

#### **2. Get Your Current Directory**
```bash
# In the mcp-server directory, run:
pwd
# Copy the output and use it as your "cwd" value
```

#### **3. Windows Path Format**
```json
{
  "mcpServers": {
    "haiven": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "C:\\Users\\YourName\\path\\to\\haiven\\mcp-server",  // ✅ Windows format
      "env": {
        "HAIVEN_API_URL": "http://localhost:8080",
        "HAIVEN_DISABLE_AUTH": "true"
      }
    }
  }
}
```

#### **4. Alternative: Use Full Python Path**
If "cwd" doesn't work, use the full path to the Python script:
```json
{
  "mcpServers": {
    "haiven": {
      "command": "python",
      "args": ["/full/path/to/haiven/mcp-server/mcp_server.py"],  // ✅ Full path to script
      "env": {
        "HAIVEN_API_URL": "http://localhost:8080",
        "HAIVEN_DISABLE_AUTH": "true"
      }
    }
  }
}
```

#### **5. Alternative: Use Poetry Run**
```json
{
  "mcpServers": {
    "haiven": {
      "command": "poetry",
      "args": ["run", "python", "mcp_server.py"],
      "cwd": "/path/to/haiven/mcp-server",
      "env": {
        "HAIVEN_API_URL": "http://localhost:8080",
        "HAIVEN_DISABLE_AUTH": "true"
      }
    }
  }
}
```

#### **6. No "cwd" Version (Last Resort)**
Some MCP clients don't support "cwd" properly:
```json
{
  "mcpServers": {
    "haiven": {
      "command": "python",
      "args": ["/full/absolute/path/to/haiven/mcp-server/mcp_server.py"],
      "env": {
        "HAIVEN_API_URL": "http://localhost:8080",
        "HAIVEN_DISABLE_AUTH": "true"
      }
    }
  }
}
```

---

## 🧪 **Testing Your Configuration**

### **1. Verify Your Path**
```bash
# Check if the path exists
ls -la /path/to/your/mcp-server/
# Should show mcp_server.py file
```

### **2. Test Python Import**
```bash
# From your mcp-server directory
python -c "from mcp_server import HaivenMCPServer; print('✅ Import works')"
```

### **3. Test with Poetry**
```bash
# From your mcp-server directory
poetry run python -c "from mcp_server import HaivenMCPServer; print('✅ Poetry works')"
```

---

## 📱 **AI Tool Specific Issues**

### **Claude Desktop**
- **Config location**: `~/.config/claude/config.json` (Linux/Mac) or `%APPDATA%\Claude\config.json` (Windows)
- **Common issue**: Must restart Claude completely after config changes
- **Debug**: Check Claude's logs for specific error messages

### **VS Code**
- **Config location**: Settings → search for "mcp"
- **Common issue**: Extension-specific MCP configuration varies
- **Debug**: Check VS Code's developer console (Help → Toggle Developer Tools)

### **Cursor**
- **Config location**: `~/.cursor/config.json`
- **Common issue**: Similar to Claude Desktop
- **Debug**: Check Cursor's logs

---

## 🛠️ **Quick Fix Generator**

Run this script to generate a working config for your system:

```bash
# In your mcp-server directory
cat > generate_config.py << 'EOF'
import json
import os
from pathlib import Path

# Get current directory
current_dir = Path.cwd().absolute()
script_path = current_dir / "mcp_server.py"

# Check if files exist
if not script_path.exists():
    print("❌ mcp_server.py not found in current directory")
    exit(1)

# Generate config
config = {
    "mcpServers": {
        "haiven": {
            "command": "python",
            "args": [str(script_path)],  # Full path to script
            "env": {
                "HAIVEN_API_URL": "http://localhost:8080",
                "HAIVEN_DISABLE_AUTH": "true"
            }
        }
    }
}

# Alternative with cwd
config_with_cwd = {
    "mcpServers": {
        "haiven": {
            "command": "python", 
            "args": ["mcp_server.py"],
            "cwd": str(current_dir),
            "env": {
                "HAIVEN_API_URL": "http://localhost:8080",
                "HAIVEN_DISABLE_AUTH": "true"
            }
        }
    }
}

print("✅ Configuration with full path (recommended):")
print(json.dumps(config, indent=2))

print("\n✅ Configuration with cwd (if your tool supports it):")
print(json.dumps(config_with_cwd, indent=2))

print(f"\n📁 Current directory: {current_dir}")
print(f"📄 Script path: {script_path}")
EOF

python generate_config.py
```

---

## 🔍 **Debugging Steps**

### **1. Check AI Tool Logs**
- **Claude Desktop**: Check application logs/console
- **VS Code**: Help → Toggle Developer Tools → Console
- **Cursor**: Similar to VS Code

### **2. Test MCP Server Directly**
```bash
# Test server starts up
python mcp_server.py --help

# Test with environment
export HAIVEN_API_URL=http://localhost:8080
export HAIVEN_DISABLE_AUTH=true
python mcp_server.py
```

### **3. Verify Dependencies**
```bash
# Check Python version
python --version

# Check Poetry installation
poetry --version

# Check dependencies
poetry show
```

---

## 💡 **Quick Solutions by Error Message**

| Error Message | Solution |
|---------------|----------|
| "cwd not found" | Use absolute path |
| "No such file or directory" | Check path exists with `ls` |
| "Permission denied" | Check file permissions |
| "Command not found" | Use full path to Python |
| "Module not found" | Run `poetry install` |
| "Connection refused" | Start Haiven backend first |
| "Invalid JSON" | Validate JSON syntax |

---

## 🆘 **Still Having Issues?**

1. **Run the config generator** above to get a working config
2. **Check the specific error message** in your AI tool's logs
3. **Try the "no cwd" version** if path issues persist
4. **Verify Haiven backend is running** (`curl http://localhost:8080/health`)
5. **Share the exact error message** for more specific help

**Most common fix**: Use the absolute path to `mcp_server.py` instead of relying on "cwd"! 