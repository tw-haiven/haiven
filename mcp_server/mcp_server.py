# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
#!/usr/bin/env python3
import os
import json
import httpx
from mcp.server.fastmcp import FastMCP, Context

# Config
HAIVEN_API_BASE_URL = os.getenv("HAIVEN_API_BASE_URL")
HAIVEN_API_KEY = os.getenv("HAIVEN_API_KEY")

# Initialize FastMCP (still no .app in 1.9.4)
mcp = FastMCP(
    "Haiven", port=8081, host="0.0.0.0"
)  # Runs on port 8080 by default in cloud run. For local testing, we can change it to any other port.


@mcp.tool()
async def search_prompts(search_key: str, ctx: Context) -> str:
    try:
        if not HAIVEN_API_KEY:
            return "Error: HAIVEN_API_KEY is required to use mcp server"

        url = f"{HAIVEN_API_BASE_URL}/api/prompt-mcp"
        headers = {
            "Authorization": f"Bearer {HAIVEN_API_KEY}",
            "Content-Type": "application/json",
        }
        params = {"search_key": search_key}

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return json.dumps(response.json(), indent=2)

    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    mcp.run(
        transport="sse",
    )
