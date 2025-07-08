#!/usr/bin/env python3
"""
Haiven MCP Server

This server provides access to Haiven's prompts API through the Model Context Protocol (MCP).
It allows AI assistants to discover and execute prompts from your Haiven instance.
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    TextContent,
    Tool,
)
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PromptExecutionParams(BaseModel):
    """Parameters for executing a prompt."""

    userinput: str = Field(..., description="User input for the prompt")
    promptid: Optional[str] = Field(None, description="ID of the prompt to execute")
    chatSessionId: Optional[str] = Field(
        None, description="Chat session ID for conversation continuity"
    )
    contexts: Optional[List[str]] = Field(
        None, description="List of context identifiers"
    )
    document: Optional[List[str]] = Field(
        None, description="List of document identifiers"
    )
    json_output: bool = Field(False, description="Whether to return JSON output")
    userContext: Optional[str] = Field(None, description="Additional user context")


class HaivenMCPServer:
    """MCP Server for Haiven Prompts API."""

    def __init__(
        self,
        base_url: str = "http://localhost:8080",
        session_cookie: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.server = Server("haiven-prompts")

        # Setup authentication
        headers = {"Content-Type": "application/json"}
        cookies = {}

        if session_cookie:
            # Use session cookie for authentication (from browser session)
            cookies["session"] = session_cookie
            logger.info("Using session cookie authentication")
        elif api_key:
            # Use API key authentication (if implemented)
            headers["Authorization"] = f"Bearer {api_key}"
            logger.info("Using API key authentication")
        else:
            # Check if auth is disabled
            logger.warning(
                "No authentication provided. Ensure AUTH_SWITCHED_OFF=true on Haiven server"
            )

        self.client = httpx.AsyncClient(timeout=60.0, headers=headers, cookies=cookies)

        # Register tool handlers using new decorator API
        self._register_handlers()

    def _register_handlers(self):
        """Register MCP tool handlers using the new decorator API."""

        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List available tools."""
            return [
                Tool(
                    name="get_prompts",
                    description="Get all available prompts with their metadata and follow-ups",
                    inputSchema={"type": "object", "properties": {}, "required": []},
                ),
                Tool(
                    name="execute_prompt",
                    description="Execute a specific prompt with user input and optional parameters",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "userinput": {
                                "type": "string",
                                "description": "User input for the prompt",
                            },
                            "promptid": {
                                "type": "string",
                                "description": "ID of the prompt to execute (optional)",
                            },
                            "chatSessionId": {
                                "type": "string",
                                "description": "Chat session ID for conversation continuity (optional)",
                            },
                            "contexts": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of context identifiers (optional)",
                            },
                            "document": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of document identifiers (optional)",
                            },
                            "json_output": {
                                "type": "boolean",
                                "description": "Whether to return JSON output (default: false)",
                            },
                            "userContext": {
                                "type": "string",
                                "description": "Additional user context (optional)",
                            },
                        },
                        "required": ["userinput"],
                    },
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls."""
            if name == "get_prompts":
                return await self._get_prompts()
            elif name == "execute_prompt":
                return await self._execute_prompt(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")

    async def _get_prompts(self) -> List[TextContent]:
        """Get all available prompts."""
        try:
            response = await self.client.get(f"{self.base_url}/api/prompts")
            response.raise_for_status()

            prompts_data = response.json()

            # Format the response for better readability
            formatted_response = {
                "prompts": prompts_data,
                "total_count": len(prompts_data)
                if isinstance(prompts_data, list)
                else 0,
            }

            return [
                TextContent(type="text", text=json.dumps(formatted_response, indent=2))
            ]
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error from Haiven API: {e.response.status_code} - {e.response.text}"
            logger.error(error_msg)
            return [TextContent(type="text", text=f"Error: {error_msg}")]
        except Exception as e:
            error_msg = f"Error fetching prompts: {str(e)}"
            logger.error(error_msg)
            return [TextContent(type="text", text=f"Error: {error_msg}")]

    async def _execute_prompt(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute a prompt with given parameters."""
        try:
            # Validate parameters
            params = PromptExecutionParams(**arguments)

            # Prepare request data
            request_data = {"userinput": params.userinput, "json": params.json_output}

            # Add optional parameters if provided
            if params.promptid:
                request_data["promptid"] = params.promptid
            if params.chatSessionId:
                request_data["chatSessionId"] = params.chatSessionId
            if params.contexts:
                request_data["contexts"] = params.contexts
            if params.document:
                request_data["document"] = params.document
            if params.userContext:
                request_data["userContext"] = params.userContext

            # Make API call
            response = await self.client.post(
                f"{self.base_url}/api/prompt",
                json=request_data,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()

            # Handle streaming response
            if response.headers.get("content-type", "").startswith("text/plain"):
                # Streaming response
                content = response.text
                return [TextContent(type="text", text=content)]
            else:
                # JSON response
                result = response.json()
                return [TextContent(type="text", text=json.dumps(result, indent=2))]

        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error from Haiven API: {e.response.status_code} - {e.response.text}"
            logger.error(error_msg)
            return [TextContent(type="text", text=f"Error: {error_msg}")]
        except Exception as e:
            error_msg = f"Error executing prompt: {str(e)}"
            logger.error(error_msg)
            return [TextContent(type="text", text=f"Error: {error_msg}")]

    async def run(self):
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream, write_stream, self.server.create_initialization_options()
            )


async def main():
    """Main entry point."""
    import sys

    # Parse command line arguments and environment variables
    base_url = os.getenv("HAIVEN_API_URL", "http://localhost:8080")
    session_cookie = os.getenv("HAIVEN_SESSION_COOKIE")
    api_key = os.getenv("HAIVEN_API_KEY")

    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    if len(sys.argv) > 2:
        session_cookie = sys.argv[2]

    logger.info("Starting Haiven MCP Server")
    logger.info(f"API URL: {base_url}")

    # Authentication info (don't log sensitive data)
    if session_cookie:
        logger.info("Authentication: Session cookie provided")
    elif api_key:
        logger.info("Authentication: API key provided")
    else:
        logger.info("Authentication: None (requires AUTH_SWITCHED_OFF=true)")

    server = HaivenMCPServer(base_url, session_cookie, api_key)
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
