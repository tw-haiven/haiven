# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
                    name="get_prompt_text",
                    description="Get the prompt text content by prompt ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt_id": {
                                "type": "string",
                                "description": "ID of the prompt to retrieve text for",
                            }
                        },
                        "required": ["prompt_id"],
                    },
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls."""
            if name == "get_prompts":
                return await self._get_prompts()
            elif name == "get_prompt_text":
                return await self._get_prompt_text(arguments)
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

    async def _get_prompt_text(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Get prompt text content by prompt ID."""
        try:
            prompt_id = arguments.get("prompt_id")
            if not prompt_id:
                return [TextContent(type="text", text="Error: prompt_id is required")]

            # Call the Haiven API to get the prompt with content
            response = await self.client.get(
                f"{self.base_url}/api/download-prompt?prompt_id={prompt_id}"
            )
            response.raise_for_status()

            prompt_data = response.json()

            # Handle case where prompt is not found
            if not prompt_data:
                return [
                    TextContent(
                        type="text",
                        text=f"Error: Prompt with ID '{prompt_id}' not found",
                    )
                ]

            # If the response is a list (array of prompts), get the first one
            if isinstance(prompt_data, list):
                if len(prompt_data) == 0:
                    return [
                        TextContent(
                            type="text",
                            text=f"Error: Prompt with ID '{prompt_id}' not found",
                        )
                    ]
                prompt_data = prompt_data[0]

            # Format the response for better readability
            formatted_response = {
                "prompt_id": prompt_data.get("identifier", prompt_id),
                "title": prompt_data.get("title", "Unknown"),
                "description": prompt_data.get("help_prompt_description", ""),
                "categories": prompt_data.get("categories", []),
                "content": prompt_data.get("content", "No content available"),
                "type": prompt_data.get("type", "chat"),
                "follow_ups": prompt_data.get("follow_ups", []),
            }

            return [
                TextContent(type="text", text=json.dumps(formatted_response, indent=2))
            ]
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error from Haiven API: {e.response.status_code} - {e.response.text}"
            logger.error(error_msg)
            return [TextContent(type="text", text=f"Error: {error_msg}")]
        except Exception as e:
            error_msg = f"Error fetching prompt text: {str(e)}"
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
