# 🚀 Haiven MCP Server

**Connect ANY MCP-compatible AI tool to your organization's Haiven AI system**

This lets you use Haiven's powerful AI prompts directly from your favorite AI tools - no more switching between apps!

## 🎯 **Compatible AI Tools**

This MCP server works with:
- **Claude Desktop** - Anthropic's desktop app
- **VS Code** - With AI extensions (Claude, Codeium, etc.)
- **Cursor** - AI-powered code editor
- **Zed** - Modern code editor with AI features
- **Any MCP-compatible tool** - Following the Model Context Protocol standard

## 🚀 **Quick Start for End Users**

### **Option 1: Super Easy (Recommended)**
1. **Download** this folder to your computer
2. **Double-click** the installer for your system:
   - **Windows**: `INSTALL.bat`
   - **Mac/Linux**: `install.sh`
3. **Follow the prompts** - it will ask for:
   - Your Haiven server URL
   - Your API key (get this from Haiven's "API Keys" page)
4. **Configure your AI tool** (see setup guides below)
5. **Test it**: Ask your AI tool "What Haiven prompts are available?"

### **Option 2: Manual Setup**
If you prefer step-by-step instructions, see: [USER_SETUP_GUIDE.md](USER_SETUP_GUIDE.md)

### **Option 3: Developer Setup (Local Development)**
For developers testing against local Haiven instances:
- **Quick setup**: `./dev_setup.sh` (Mac/Linux) or `python dev_setup.py` (All platforms)
- **Full guide**: [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)

## ⚙️ **Configuration for Different AI Tools**

### **Claude Desktop**
Config file: `~/.config/claude/config.json` (or equivalent for your OS)
```json
{
  "mcpServers": {
    "haiven": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "/path/to/haiven-mcp-server",
      "env": {
        "HAIVEN_API_URL": "https://your-haiven-server.com",
        "HAIVEN_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

### **VS Code with AI Extensions**
Add to your VS Code settings or extension configuration:
```json
{
  "mcp.servers": {
    "haiven": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "/path/to/haiven-mcp-server",
      "env": {
        "HAIVEN_API_URL": "https://your-haiven-server.com",
        "HAIVEN_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

### **Cursor**
Config file: `~/.cursor/config.json`
```json
{
  "mcpServers": {
    "haiven": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "/path/to/haiven-mcp-server",
      "env": {
        "HAIVEN_API_URL": "https://your-haiven-server.com",
        "HAIVEN_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

### **Windsurf**
**Note**: Windsurf doesn't support the `cwd` parameter, so you must use absolute paths.

See `config_examples/windsurf_config_template.json` for a complete example.

Config in Windsurf: `Plugins` → `Manage plugins` → `View raw config`

### **Other MCP-Compatible Tools**
Check your tool's documentation for MCP server configuration. The general pattern is:
- **Command**: `python mcp_server.py`
- **Environment**: Set `HAIVEN_API_URL` and `HAIVEN_API_KEY`
- **Working Directory**: Path to this MCP server folder

## 🔑 **Getting Your API Key**

1. Open Haiven in your browser
2. Login with your work credentials
3. Click "API Keys" in the navigation
4. Click "Generate New API Key"
5. Copy the key immediately (you won't see it again!)

## 🆘 **Need Help?**

- **End Users**: See [USER_SETUP_GUIDE.md](USER_SETUP_GUIDE.md) for detailed setup instructions
- **Developers**: See [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) for local development setup
- **IT Teams**: See [TECHNICAL_GUIDE.md](TECHNICAL_GUIDE.md) for deployment details
- **Troubleshooting**: Check the appropriate guide for common issues
- **Can't find your API key?** Ask your Haiven administrator

## 🔧 **For IT Teams**

This MCP server:
- ✅ Uses standard MCP protocol (JSON-RPC 2.0 over stdin/stdout)
- ✅ Supports API key authentication
- ✅ No data stored locally - all queries go to your Haiven server
- ✅ Works with **any MCP-compatible AI tool**

### **Deployment Options**
- **Individual install**: Users run installer on their machines
- **Centralized**: Deploy via software distribution systems
- **Docker**: Container available for enterprise deployment

## 📋 **System Requirements**

- **Python 3.8+** (most computers have this)
- **Any MCP-compatible AI tool** (Claude Desktop, VS Code, Cursor, etc.)
- **Haiven API key** (from your organization's Haiven system)

## 🎉 **What Users Get**

After setup, users can:
- 💬 Ask their AI tool: "What Haiven prompts are available?"
- 🚀 Execute prompts: "Use Haiven to analyze this user feedback"
- 📊 Get all Haiven capabilities directly in their favorite AI tool
- 🔄 Keep their conversation context while using Haiven tools

---

**Ready to connect your team to Haiven AI? Works with any MCP-compatible tool! 🚀**

## Overview

This MCP server provides a bridge between AI applications (IDEs, editors, AI assistants) and the Haiven AI prompts API. It enables seamless integration with tools like Claude Desktop, VS Code with MCP extensions, and other AI-powered development environments.

## Features

- **Standalone Service**: Independent from the main Haiven application
- **Standard MCP Protocol**: Uses JSON-RPC 2.0 over stdin/stdout
- **Two Main Tools**:
  - `get_prompts`: Retrieve all available prompts with metadata
  - `execute_prompt`: Execute prompts with user input and parameters
- **Comprehensive Error Handling**: Robust error handling and logging
- **Easy Configuration**: Simple setup and deployment

## Installation

### Prerequisites

- Python 3.11 or higher
- Poetry (for dependency management)
- Access to a running Haiven API instance

### Setup

1. Clone or navigate to the MCP server directory:
```bash
cd mcp-server
```

2. Install dependencies:
```bash
poetry install
```

3. Activate the virtual environment:
```bash
poetry shell
```

## Usage

### Running the Server

#### Basic Usage
```bash
python mcp_server.py
```

#### With Custom API URL
```bash
python mcp_server.py http://your-haiven-instance:8000
```

#### Using Poetry Script
```bash
poetry run haiven-mcp-server
```

### Environment Variables

- `HAIVEN_API_URL`: Base URL of the Haiven API (default: `http://localhost:8000`)
- `HAIVEN_SESSION_COOKIE`: Session cookie from authenticated browser session (optional)
- `HAIVEN_API_KEY`: API key for authentication (optional, if implemented)

### Environment Configuration Files

You can use environment files to manage different configurations:

1. **Copy the example configuration**:
   ```bash
   cp config_examples/environment.env.example .env
   ```

2. **Edit `.env` with your settings**:
   ```bash
   HAIVEN_API_URL=https://haiven.your-company.com
   HAIVEN_API_KEY=your_api_key_here
   ```

3. **Load the environment**:
   ```bash
   # Load environment and run server
   source .env && python mcp_server.py
   
   # Or for tests
   source .env && python test_integration.py
   ```

**Different environment files for different deployments**:
- `.env.local` - Local development (http://localhost:8080)
- `.env.staging` - Staging environment  
- `.env.production` - Production environment

### Authentication

⚠️ **Important**: Haiven APIs are protected by OKTA authentication by default.

📖 **See [AUTHENTICATION.md](AUTHENTICATION.md) for comprehensive authentication setup instructions.**

**Quick Setup Options**:

1. **Development Mode**: Set `AUTH_SWITCHED_OFF=true` on your Haiven server
2. **Session Cookie**: Extract session cookie from browser after logging in
3. **API Key**: Use server-generated API keys for programmatic access

**Environment Variables**:
```bash
export HAIVEN_SESSION_COOKIE="your_session_cookie"
# OR
export HAIVEN_API_KEY="your_api_key"
```

### API Key Authentication

API keys provide secure programmatic access without browser sessions:

#### Generating API Keys

API keys are generated securely through the authenticated web interface:

**Steps to Generate an API Key:**
1. Login to Haiven (OKTA authentication required)
2. Navigate to the "API Keys" page in the header navigation
3. Click "Generate New API Key"
4. Fill in the key name and expiration period
5. Copy the generated key securely (shown only once)

**Security Features:**
- ✅ OKTA authentication required
- ✅ Users can only manage their own keys
- ✅ Keys are shown only once after generation
- ✅ Automatic expiration management
- ✅ Usage tracking and monitoring

#### Using API Keys

1. **Set the environment variable**:
   ```bash
   export HAIVEN_API_KEY="your_api_key_here"
   ```

2. **Start the MCP server**:
   ```bash
   ./start_server.sh
   ```

3. **In AI tool configurations**, add the environment variable:
   ```json
   {
     "env": {
       "HAIVEN_API_URL": "http://localhost:8000",
               "HAIVEN_API_KEY": "your_api_key_here"
     }
   }
   ```

#### API Key Security

- **Secure Storage**: Store API keys in environment variables or secure configuration files
- **Expiration**: Keys expire after 365 days by default (configurable during generation)
- **Rotation**: Generate new keys and revoke old ones regularly through the web interface
- **Monitoring**: Key usage is tracked and logged automatically

## Configuration for AI Tools

### Claude Desktop

Add the following to your Claude Desktop configuration file (`~/.config/claude-desktop/config.json`):

```json
{
  "mcpServers": {
    "haiven-prompts": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "/path/to/haiven/mcp-server",
      "env": {
        "HAIVEN_API_URL": "http://localhost:8000"
      }
    }
  }
}
```

### VS Code with MCP Extension

1. Install an MCP extension for VS Code
2. Add to your VS Code settings:
```json
{
  "mcp.servers": {
    "haiven-prompts": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "/path/to/haiven/mcp-server"
    }
  }
}
```

### Cursor IDE

Add to your Cursor configuration:
```json
{
  "mcp.servers": {
    "haiven-prompts": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "/path/to/haiven/mcp-server"
    }
  }
}
```

## API Tools

### get_prompts

Retrieves all available prompts with their metadata and follow-ups.

**Parameters**: None

**Returns**: JSON object with prompts array and total count

**Example**:
```json
{
  "prompts": [
    {
      "identifier": "brainstorm-ideas",
      "title": "Brainstorm Ideas",
      "categories": ["brainstorming"],
      "help_prompt_description": "Generate creative ideas for any topic",
      "follow_ups": [...]
    }
  ],
  "total_count": 1
}
```

### execute_prompt

Executes a specific prompt with user input and optional parameters.

**Parameters**:
- `userinput` (required): User input for the prompt
- `promptid` (optional): ID of the prompt to execute
- `chatSessionId` (optional): Chat session ID for continuity
- `contexts` (optional): Array of context identifiers
- `document` (optional): Array of document identifiers
- `json` (optional): Whether to return JSON output
- `userContext` (optional): Additional user context

**Returns**: The result of the prompt execution

**Example**:
```json
{
  "userinput": "Help me brainstorm app ideas",
  "promptid": "brainstorm-ideas",
  "contexts": ["mobile-dev"],
  "json": false
}
```

## Testing

Run the test suite:
```bash
poetry run pytest
```

Or run the custom test script:
```bash
python test_mcp_server.py
```

## Development

### Project Structure

```
mcp-server/
├── mcp_server.py          # Main MCP server implementation
├── test_mcp_server.py     # Test suite
├── pyproject.toml         # Poetry configuration
├── README.md              # This file
└── examples/              # Example configurations
```

### Making Changes

1. Make your changes to the code
2. Run tests: `poetry run pytest`
3. Update documentation as needed
4. Test with actual AI tools

### Debugging

Enable debug logging:
```bash
PYTHONPATH=. python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from mcp_server import main
import asyncio
asyncio.run(main())
"
```

## Deployment

### As a System Service

Create a systemd service file (`/etc/systemd/system/haiven-mcp.service`):

```ini
[Unit]
Description=Haiven MCP Server
After=network.target

[Service]
Type=simple
User=haiven
WorkingDirectory=/path/to/haiven/mcp-server
Environment=HAIVEN_API_URL=http://localhost:8000
ExecStart=/path/to/haiven/mcp-server/.venv/bin/python mcp_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable haiven-mcp.service
sudo systemctl start haiven-mcp.service
```

### Using Docker

Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install --only=main

COPY mcp_server.py ./

CMD ["poetry", "run", "python", "mcp_server.py"]
```

## Troubleshooting

### Common Issues

1. **MCP Server Not Starting**
   - Check Python version (3.11+)
   - Verify dependencies: `poetry install`
   - Ensure Haiven API is running

2. **Authentication Errors (401/403)**
   - **Development**: Set `AUTH_SWITCHED_OFF=true` on Haiven server
   - **Production**: Ensure session cookie is valid and not expired
   - **Session expired**: Re-extract session cookie from browser
   - **OKTA issues**: Log in to Haiven manually first

3. **Connection Errors**
   - Verify Haiven API URL
   - Check network connectivity
   - Confirm API endpoints are accessible: `curl http://localhost:8000/api/prompts`

4. **Tool Not Found**
   - Verify MCP server configuration in AI tool
   - Check server logs for errors
   - Ensure server is running and responsive

5. **Session Cookie Issues**
   - Cookie format: Copy only the VALUE, not the entire cookie string
   - Browser sessions: Ensure you're logged in to Haiven
   - Expiry: Session cookies typically expire in 1 week

### Getting Help

- Check the logs for error messages
- Verify your configuration matches the examples
- Test the Haiven API directly with curl
- Review the MCP specification at https://modelcontextprotocol.io/

## License

This project is licensed under the same terms as the main Haiven project.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request 