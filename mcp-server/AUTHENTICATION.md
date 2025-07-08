# Haiven MCP Server Authentication Guide

This guide explains how to configure authentication for the Haiven MCP server when connecting to OKTA-protected Haiven instances.

## Overview

Haiven uses OKTA for authentication by default. The MCP server needs to authenticate when making API calls to Haiven. There are three authentication methods available:

## Method 1: Development Mode (Recommended for Testing)

**When to use**: Local development, testing, non-production environments

**Setup**:
1. Set `AUTH_SWITCHED_OFF=true` in your Haiven server environment
2. Restart your Haiven server
3. Configure MCP server without authentication:

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

**Pros**: Simple setup, no authentication hassles
**Cons**: Security risk, only suitable for development

## Method 2: Session Cookie Authentication (Recommended for Production)

**When to use**: Production environments, shared Haiven instances

**Setup**:

### Step 1: Get Your Session Cookie

1. **Log in to Haiven**:
   - Open your browser
   - Navigate to your Haiven instance
   - Complete the OKTA authentication flow
   - Ensure you can access Haiven successfully

2. **Extract the session cookie**:

   **Chrome/Edge**:
   - Press F12 to open Developer Tools
   - Go to the "Application" tab
   - In the left sidebar, expand "Storage" → "Cookies"
   - Click on your Haiven domain (e.g., `https://haiven.yourcompany.com`)
   - Find the cookie named `session`
   - Copy the **Value** (not the entire cookie)

   **Firefox**:
   - Press F12 to open Developer Tools
   - Go to the "Storage" tab
   - In the left sidebar, expand "Cookies"
   - Click on your Haiven domain
   - Find the cookie named `session`
   - Copy the **Value**

   **Safari**:
   - Enable Developer menu: Safari → Preferences → Advanced → "Show Develop menu"
   - Press Cmd+Option+I to open Web Inspector
   - Go to "Storage" tab
   - Select "Cookies" → your Haiven domain
   - Find `session` cookie and copy its value

### Step 2: Configure MCP Server

**Environment Variable** (Recommended):
```bash
export HAIVEN_SESSION_COOKIE="your_copied_session_value"
```

**Configuration File**:
```json
{
  "mcpServers": {
    "haiven-prompts": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "/path/to/haiven/mcp-server",
      "env": {
        "HAIVEN_API_URL": "https://haiven.yourcompany.com",
        "HAIVEN_SESSION_COOKIE": "your_copied_session_value"
      }
    }
  }
}
```

### Step 3: Test Authentication

```bash
# Test the connection
cd mcp-server
python test_setup.py
```

**Important Notes**:
- Session cookies expire (typically after 1 week)
- You'll need to refresh the cookie when it expires
- Keep your session cookie secure - it provides full access to your Haiven account

## Method 3: API Key Authentication

**When to use**: Production environments, automated systems, headless deployments

**Setup**:

### Step 1: Generate an API Key

1. **Log in to Haiven**:
   - Open your browser and navigate to your Haiven instance
   - Complete the OKTA authentication flow
   - Go to "API Keys" section in the web interface

2. **Create a new API key**:
   - Click "Generate New API Key"
   - Provide a descriptive name (e.g., "MCP Server", "CI/CD Pipeline")
   - The API key will be valid for 24 hours from generation
   - **Important**: Copy the API key immediately - it will only be shown once

### Step 2: Configure MCP Server

**Environment Variable** (Recommended):
```bash
export HAIVEN_API_KEY="your_generated_api_key"
```

**Configuration File**:
```json
{
  "mcpServers": {
    "haiven-prompts": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "/path/to/haiven/mcp-server",
      "env": {
        "HAIVEN_API_URL": "https://haiven.yourcompany.com",
        "HAIVEN_API_KEY": "your_generated_api_key"
      }
    }
  }
}
```

### Step 3: Test Authentication

```bash
# Test the connection
cd mcp-server
python test_setup.py
```

**Important Notes**:
- API keys are valid for 24 hours for enhanced security
- You'll need to generate a new key when the current one expires
- API keys provide the same access level as your user account
- Keep your API key secure - treat it like a password

## Troubleshooting Authentication

### Common Issues

**401 Unauthorized**:
- **Session cookies**: Check if your session cookie is valid, try logging in again
- **API keys**: Check if your API key is valid and not expired (24-hour limit)
- Generate a fresh session cookie or API key

**403 Forbidden**:
- Your user might not have access to the required APIs
- Contact your Haiven administrator

**Connection Refused**:
- Check if Haiven server is running
- Verify the API URL is correct
- Check network connectivity

**Session Expired**:
- Session cookies typically expire after 1 week
- API keys expire after 24 hours
- Extract a new session cookie from your browser or generate a new API key
- Some organizations have shorter session timeouts

### Testing Authentication

**Test without MCP server**:
```bash
# Test with session cookie
curl -H "Cookie: session=your_session_cookie" \
     http://localhost:8000/api/prompts

# Test with API key
curl -H "Authorization: Bearer <YOUR_API_KEY>" \
     http://localhost:8000/api/prompts
```

**Test with development mode**:
```bash
# On Haiven server
export AUTH_SWITCHED_OFF=true

# Test without authentication
curl http://localhost:8000/api/prompts
```

### Security Best Practices

1. **Never commit session cookies to version control**
2. **Use environment variables for sensitive data**
3. **Rotate session cookies regularly**
4. **Use development mode only for local testing**
5. **Monitor for authentication failures in logs**

### Automation and CI/CD

For automated deployments, consider:

1. **Service accounts**: Request dedicated service accounts from your OKTA admin
2. **Session refresh**: Implement automated session cookie refresh
3. **Health checks**: Monitor authentication status
4. **Fallback**: Have a plan for authentication failures

## Getting Help

If you're having authentication issues:

1. Check the [troubleshooting section](README.md#troubleshooting)
2. Verify your OKTA permissions with your admin
3. Test authentication manually in your browser first
4. Check MCP server logs for detailed error messages

For security concerns or questions about API keys, contact your Haiven administrator or the Thoughtworks team. 