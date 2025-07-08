# 🚀 Haiven MCP Setup Guide for End Users

**For Business Analysts, Product Managers, and other non-technical users**

This guide shows you how to connect **any MCP-compatible AI tool** to your organization's **Haiven AI** system, so you can use Haiven's prompts directly from your favorite AI tools.

## 📋 **What You'll Need**

- **An MCP-compatible AI tool** installed on your computer:
  - Claude Desktop, VS Code (with AI extensions), Cursor, Zed, etc.
- **Access to your organization's Haiven system** (the web version)
- **15-20 minutes** for setup

## 🎯 **What This Gives You**

After setup, you can:
- ✅ Use Haiven prompts directly from your AI tool
- ✅ Execute prompts with your own input
- ✅ Get all Haiven's AI capabilities without switching apps
- ✅ Keep your conversation context while using Haiven tools

---

## 📦 **Step 1: Download the MCP Server**

### Option A: Download from Your IT Team (Recommended)
Ask your IT team for the "Haiven MCP Server" - they should provide you with a folder containing the setup files.

### Option B: Download from GitHub (If IT allows)
1. Go to your organization's Haiven repository
2. Download the `mcp-server` folder
3. Save it somewhere easy to find (like `Downloads/haiven-mcp-server`)

---

## 🔑 **Step 2: Get Your API Key**

1. **Open Haiven in your browser** (the web version your organization uses)
2. **Login** with your work credentials (OKTA/SSO)
3. **Click "API Keys"** in the top navigation menu
4. **Click "Generate New API Key"**
5. **Fill out the form:**
   - Name: "AI Tool Integration"
   - Expiration: 365 days (or your preference)
6. **Copy the generated key** - ⚠️ **Save it immediately!** You won't see it again
7. **Store it safely** (password manager recommended)

---

## 💻 **Step 3: Install Python (If Not Already Installed)**

### Check if Python is installed:
1. **Press Windows Key + R** (Windows) or **Cmd + Space** (Mac)
2. **Type:** `cmd` (Windows) or `Terminal` (Mac)
3. **Type:** `python --version`
4. If you see a version number like `Python 3.11.x`, you're good!

### If Python is not installed:
- **Windows:** Download from [python.org](https://python.org) - choose "Add to PATH" during installation
- **Mac:** Python is usually pre-installed, or use [python.org](https://python.org)

---

## 🛠️ **Step 4: Setup the MCP Server**

1. **Open Terminal/Command Prompt**
2. **Navigate to your MCP server folder:**
   ```bash
   cd Downloads/haiven-mcp-server  # Adjust path as needed
   ```

3. **Install dependencies:**
   ```bash
   pip install poetry
   poetry install
   ```

4. **Test the installation:**
   ```bash
   poetry run python mcp_server.py --help
   ```

---

## 🔧 **Step 5: Configure Your AI Tool**

### **Claude Desktop**
1. **Find Claude Desktop's config file:**
   - **Windows:** `%APPDATA%\Claude\config.json`
   - **Mac:** `~/Library/Application Support/Claude/config.json`
   - **Linux:** `~/.config/claude/config.json`

2. **Create the config file if it doesn't exist** (just an empty file named `config.json`)

3. **Edit the config file** and add this content:

```json
{
  "mcpServers": {
    "haiven": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "/full/path/to/your/haiven-mcp-server",
      "env": {
        "HAIVEN_API_URL": "https://your-haiven-server.com",
        "HAIVEN_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

### **VS Code with AI Extensions**
1. **Open VS Code Settings** (Ctrl+, or Cmd+,)
2. **Search for "mcp"** or check your AI extension's configuration
3. **Add MCP server configuration:**

```json
{
  "mcp.servers": {
    "haiven": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "/full/path/to/your/haiven-mcp-server",
      "env": {
        "HAIVEN_API_URL": "https://your-haiven-server.com",
        "HAIVEN_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

### **Cursor**
1. **Find Cursor's config file:**
   - **Windows:** `%APPDATA%\Cursor\config.json`
   - **Mac:** `~/Library/Application Support/Cursor/config.json`
   - **Linux:** `~/.config/cursor/config.json`

2. **Add the same MCP server configuration as Claude Desktop**

### **Other AI Tools**
Check your tool's documentation for MCP server configuration. Look for:
- "MCP servers" or "Model Context Protocol"
- "External tools" or "Integrations"
- Settings for adding custom servers

4. **Update the placeholders:**
   - Replace `/full/path/to/your/haiven-mcp-server` with the actual path
   - Replace `https://your-haiven-server.com` with your organization's Haiven URL
   - Replace `your_api_key_here` with the API key you copied

### 💡 **Example Configuration:**
```json
{
  "mcpServers": {
    "haiven": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "C:/Users/YourName/Downloads/haiven-mcp-server",
      "env": {
        "HAIVEN_API_URL": "https://haiven.your-company.com",
        "HAIVEN_API_KEY": "hv_example_api_key_12345"
      }
    }
  }
}
```

---

## 🚀 **Step 6: Start Your AI Tool**

1. **Close your AI tool** completely (if it was open)
2. **Restart your AI tool**
3. **Look for the MCP connection indicator** - you should see "haiven" connected

---

## ✅ **Step 7: Test It Out**

In your AI tool, try asking:

> "What Haiven prompts are available?"

or

> "Execute a Haiven prompt to help me analyze user feedback"

You should see your AI tool accessing your Haiven system and showing available prompts!

---

## 🆘 **Troubleshooting**

### "MCP server not connecting"
- ✅ Check that Python is installed: `python --version`
- ✅ Check that the file path in config.json is correct
- ✅ Check that your API key is valid (test in Haiven web interface)

### "Authentication failed"
- ✅ Generate a new API key from Haiven web interface
- ✅ Make sure the API key is correctly copied (no extra spaces)
- ✅ Confirm your Haiven URL is correct

### "Command not found"
- ✅ Make sure you installed Poetry: `pip install poetry`
- ✅ Try using full path to Python in the config
- ✅ Check that you ran `poetry install` in the correct folder

### "Python not found"
- ✅ Install Python from [python.org](https://python.org)
- ✅ Make sure "Add to PATH" was checked during installation
- ✅ Restart your computer after Python installation

---

## 📞 **Getting Help**

If you're stuck:

1. **Ask your IT team** - they can help with the technical setup
2. **Check with your Haiven administrator** - they can verify your API key
3. **Check your AI tool's documentation** - for MCP server setup specifics
4. **Share this guide** with your IT team - they'll know what to do

---

## 🔄 **Maintenance**

### API Key Renewal
- API keys expire (usually after 1 year)
- You'll get notifications in Haiven when they're about to expire
- Generate a new key and update your AI tool's config

### Updates
- Your IT team will let you know when there are updates
- Usually just involves replacing the MCP server files

---

## 🎉 **You're All Set!**

Now you can use Haiven's powerful AI prompts directly from your favorite AI tool! 

**Pro Tips:**
- Start with asking "What prompts are available?" to explore
- Use specific prompts for your domain (product analysis, user research, etc.)
- The integration remembers your conversation context
- You can still use your AI tool's regular features alongside Haiven

**Happy AI-powered work! 🚀** 