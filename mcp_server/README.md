# Haiven MCP Server

This directory contains a standalone Model Context Protocol (MCP) server for Haiven. This server exposes Haiven's prompt library as MCP tools, allowing external MCP clients to search for the prompts for the given search key.

## What's New: API Access Management UI

Haiven now includes a comprehensive web interface for managing API access:

- **API Access Page** (`/api-access`): A dedicated interface for generating temporary links that can be shared with external users
- **Temporary Link Generator**: Creates secure, time-limited URLs that automatically generate API keys when opened
- **API Key Generation Page** (`/generate-api-key`): Handles the automatic API key creation process when users access temporary links
- **Secure Key Display**: Shows API keys only once with copy functionality and security warnings

### Key Features:
- 🔗 **Temporary Link Generation**: Create secure links for API key distribution
- 🔑 **Automatic API Key Creation**: Users receive keys immediately upon link access
- 🔒 **Security-First Design**: Keys are displayed only once and must be copied securely
- 👥 **External User Support**: Easily share API access with team members and external collaborators
- 📋 **Copy-to-Clipboard**: One-click copying with visual feedback
- ⚠️ **Security Warnings**: Clear guidance on API key security best practices

## Local Setup

To run the MCP server locally, follow these steps:

1.  **Navigate to the `mcp_server` directory:**
    ```bash
    cd mcp_server
    ```

2.  **Install Poetry dependencies:**
    ```bash
    poetry install
    ```

3.  **Set environment variables:**
    The server requires several environment variables to function properly:
    
    **Required:**
    - `HAIVEN_API_BASE_URL`: URL of the main Haiven API
    - `HAIVEN_API_KEY`: API key for the server to access the main Haiven API
    
    ```bash
    export HAIVEN_API_BASE_URL="http://localhost:8080" # Or your Haiven API URL
    export HAIVEN_API_KEY="YOUR_HAIVEN_API_KEY" # Replace with your actual API key - generate from Haiven
    ```
    
    Alternatively, create a `.env` file in the `mcp_server` directory:
    ```
    HAIVEN_API_BASE_URL="http://localhost:8080"
    HAIVEN_API_KEY="YOUR_HAIVEN_API_KEY"
    ```

4.  **Run the server:**
    The server will listen on port 8080 by default.
    ```bash
    poetry run python mcp_server.py
    ```
    You should see output indicating the server is starting.

## Deployment to GCP Cloud Run
<USE BELOW COMMANDS JUST FOR TESTING DURING DEVELOPMENT. THIS NEEDS TO BE WRITTEN IN TERRAFORM.>
This section guides you through deploying the Haiven MCP Server to Google Cloud Run.

### Prerequisites

*   A Google Cloud Platform (GCP) project.
*   The `gcloud` CLI installed and authenticated.
*   Google Cloud Build API enabled.
*   Google Artifact Registry API enabled.

### 1. Authenticate with GCP & Set Project

Ensure your `gcloud` CLI is authenticated and configured for your project:

```bash
gcloud auth login
gcloud config set project YOUR_GCP_PROJECT_ID
```
(Replace `YOUR_GCP_PROJECT_ID` with your actual GCP project ID, e.g., `team-ai-7a96`).

### 2. Create Google Artifact Registry Repository

If you haven't already, create a Docker repository in Artifact Registry. This is where your Docker images will be stored.

```bash
gcloud artifacts repositories create haiven-mcp-server-repo \
  --repository-format=docker \
  --location=us-central1 \
  --description="Docker repository for Haiven MCP Server"
```
(You can change `us-central1` to your desired region).

### 3. Build and Push Docker Image

Navigate to the root of your `haiven` project (the directory containing the `mcp_server` folder) and build the Docker image using the `Dockerfile` located in `mcp_server/`.

```bash
gcloud builds submit mcp_server \
  --tag us-central1-docker.pkg.dev/YOUR_GCP_PROJECT_ID/haiven-mcp-server-repo/haiven-mcp-server
```
(Replace `YOUR_GCP_PROJECT_ID` with your actual GCP project ID).

### 4. Deploy to Cloud Run

Once the image is built and pushed, deploy it to Cloud Run. The server is configured to listen on port `8080`.

```bash
gcloud run deploy haiven-mcp-server \
  --image us-central1-docker.pkg.dev/YOUR_GCP_PROJECT_ID/haiven-mcp-server-repo/haiven-mcp-server \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --service-account SERVICE_ACCOUNT \
  --set-env-vars HAIVEN_API_BASE_URL="https://<haiven-base-url>/boba/",HAIVEN_API_KEY="YOUR_HAIVEN_API_KEY"
```
(Replace `YOUR_GCP_PROJECT_ID` and `YOUR_HAIVEN_API_KEY` with your actual values. Adjust `--region` if you used a different one for the Artifact Registry).

After successful deployment, the service URL will be displayed in the terminal.

## Usage

The Haiven MCP Server exposes the following tools to MCP-compatible clients:

### Available Tools

*   **Tool:** `search_prompts`
    *   **Description:** Search for prompts in Haiven's prompt library based on keywords
    *   **Input:** `search_key` (string) - Keywords to search for (e.g., "user-story", "testing", "architecture")
    *   **Returns:** JSON string containing matching prompts with their titles, descriptions, and content
    *   **Example:** `search_prompts("user story")` returns prompts related to user story creation and management

### Authentication

The MCP server requires only server-level authentication to access the main Haiven API:

#### Server API Key
The MCP server uses its own API key to authenticate with the main Haiven API:

- **`HAIVEN_API_KEY`**: Required for the server to access the main Haiven API's `/api/prompt-mcp` endpoint
- **No Client Authentication**: MCP clients can access the server without providing their own API keys
- **Simplified Setup**: Only requires configuring the server's API key, not individual client keys

#### How to Generate the Server API Key:

1. **Access the API Access page:** Navigate to the "API Access" section in the Haiven web interface
2. **Generate temporary link:** Click "Generate Temporary Link" to create a secure, time-limited URL
3. **Create API key:** Open the temporary link in your browser to automatically generate your API key
4. **Configure server:** Use this API key as the `HAIVEN_API_KEY` environment variable for the MCP server

### Integration with Development Tools

This MCP server is designed to work with:
- **Cursor IDE**: Primary integration for accessing Haiven prompts directly in your development environment
- **Other MCP Clients**: Any application that supports the Model Context Protocol
- **Custom Integrations**: Build your own tools using the MCP protocol

You can interact with this server using any MCP-compatible client, with Cursor IDE being the primary supported environment.


## Complete Workflow: From API Key Generation to Cursor Integration

This section covers the complete end-to-end workflow for generating API keys through the Haiven UI and configuring the MCP server in Cursor.

### Step 1: Generate API Keys via Haiven UI

The Haiven web interface provides a streamlined way to generate API keys for external users:

#### Option A: Direct API Key Generation (for your own use)
1. **Access the API Access page:** Navigate to the "API Access" section in the Haiven web interface
2. **Generate temporary link:** Click "Generate Temporary Link" to create a secure, time-limited URL
3. **Use the link:** Open the temporary link in your browser to automatically generate your API key
4. **Save the key:** Copy and securely store the API key as it will only be displayed once

#### Option B: Share API Access with External Users
1. **Navigate to API Access:** In the Haiven UI, go to the API Access management page
2. **Generate temporary link:** Create a temporary link that can be shared with external users
3. **Share the link:** Send the temporary link to the intended user via secure communication
4. **User generates key:** The external user opens the link and receives their unique API key
5. **Key usage:** The generated API key can be used for programmatic access to Haiven services

### Step 2: Test API Access

Before configuring the MCP server, verify that your API key works:

```bash
# Test the API key with a simple request
curl -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     "https://your-haiven-instance.com/boba/api/prompt-mcp?search_key=test"
```

### Step 3: Configure MCP Server

Once you have a valid API key, set up the MCP server with your credentials:

```bash
# Set environment variables
export HAIVEN_API_BASE_URL="https://your-haiven-instance.com/boba/"
export HAIVEN_API_KEY="your-generated-api-key"

# Or create a .env file in the mcp_server directory
echo "HAIVEN_API_BASE_URL=https://your-haiven-instance.com/boba/" > .env
echo "HAIVEN_API_KEY=your-generated-api-key" >> .env
```

### Step 4: Configure Cursor IDE

To use the Haiven MCP Server in Cursor, you need to configure it in your Cursor settings:

#### Method 1: Local MCP Server Configuration

1. **Open Cursor Settings:** Go to `Cursor` > `Settings` > `Features` > `Rules for AI`

2. **Add MCP Server Configuration:** Add the following configuration to your `cursor-composer.json` or in the MCP settings:

```json
{
  "mcpServers": {
    "haiven": {
      "command": "python",
      "args": ["/path/to/haiven/mcp_server/mcp_server.py"],
      "env": {
        "HAIVEN_API_BASE_URL": "https://your-haiven-instance.com/boba/",
        "HAIVEN_API_KEY": "your-haiven-api-key"
      }
    }
  }
}
```

#### Method 2: Cloud Run MCP Server Configuration

If you've deployed the MCP server to Google Cloud Run:

```json
{
  "mcpServers": {
    "haiven": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-fetch", "https://your-mcp-server-url.run.app"],
      "env": {
        "HAIVEN_API_BASE_URL": "https://your-haiven-instance.com/boba/",
        "HAIVEN_API_KEY": "your-generated-api-key"
      }
    }
  }
}
```

#### Method 3: Using Docker Configuration

```json
{
  "mcpServers": {
    "haiven": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "-e", "HAIVEN_API_BASE_URL=https://your-haiven-instance.com/boba/",
        "-e", "HAIVEN_API_KEY=your-generated-api-key",
        "us-central1-docker.pkg.dev/YOUR_GCP_PROJECT_ID/haiven-mcp-server-repo/haiven-mcp-server"
      ]
    }
  }
}
```

### Step 5: Using Haiven MCP Tools in Cursor

Once configured, you can use the Haiven MCP tools in Cursor:

#### Available Tools
- **`search_prompts`**: Search for prompts in Haiven's prompt library
  - **Input**: `search_key` (string) - Keywords to search for
  - **Returns**: JSON string containing matching prompts

#### Example Usage
```
/search_prompts user-story
```

This will search Haiven's prompt library for prompts related to "user-story" and return relevant prompts that you can use in your development workflow.

### Step 6: Verify Integration

1. **Restart Cursor** after adding the MCP server configuration
2. **Test the integration** by using the `/search_prompts` command
3. **Check logs** if you encounter issues - both in Cursor's developer tools and the MCP server logs

### Troubleshooting

#### Common Issues:

1. **Authentication Errors**
   - Verify your API key is correct and hasn't expired
   - Ensure the `HAIVEN_API_BASE_URL` includes the correct protocol (https://) and path (/boba/)

2. **Connection Issues**
   - Check that the Haiven instance is accessible from your network
   - Verify firewall settings allow outbound connections

3. **MCP Server Not Starting**
   - Check Python dependencies are installed: `poetry install`
   - Verify environment variables are set correctly
   - Check server logs for specific error messages

4. **Cursor Not Recognizing MCP Server**
   - Ensure the configuration file is in the correct location
   - Restart Cursor after making configuration changes
   - Check Cursor's developer console for MCP-related errors

## Configure in MCP Server