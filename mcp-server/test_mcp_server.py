# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
#!/usr/bin/env python3
"""
Test script for Haiven MCP Server

This script tests the MCP server implementation to ensure it works correctly
with the Haiven API endpoints.
"""

import asyncio
import json
import sys
from unittest.mock import AsyncMock, MagicMock, patch


async def test_mcp_server_creation():
    """Test that the MCP server can be created successfully."""

    with patch("httpx.AsyncClient"):
        from mcp_server import HaivenMCPServer

        # Test with default parameters
        server = HaivenMCPServer()
        assert server.base_url == "http://localhost:8080"
        assert server.server.name == "haiven-prompts"

        # Test with custom parameters
        server = HaivenMCPServer("http://custom:9000", api_key="test-key")
        assert server.base_url == "http://custom:9000"

        print("✓ MCP server creation test passed")


async def test_get_prompts_tool():
    """Test the get_prompts tool."""

    # Mock response data
    mock_prompts = [
        {
            "identifier": "test-prompt-1",
            "title": "Test Prompt 1",
            "categories": ["brainstorming"],
            "help_prompt_description": "A test prompt for brainstorming",
        },
        {
            "identifier": "test-prompt-2",
            "title": "Test Prompt 2",
            "categories": ["analysis"],
            "help_prompt_description": "A test prompt for analysis",
        },
    ]

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.json.return_value = mock_prompts
        mock_response.raise_for_status.return_value = None
        mock_client.get.return_value = mock_response
        mock_client_class.return_value = mock_client

        from mcp_server import HaivenMCPServer

        server = HaivenMCPServer("http://localhost:8000")
        result = await server._get_prompts()

        # Verify API call
        mock_client.get.assert_called_once_with("http://localhost:8000/api/prompts")

        # Verify response format
        assert len(result) == 1
        content = result[0]
        assert content.type == "text"

        response_data = json.loads(content.text)
        assert "prompts" in response_data
        assert "total_count" in response_data
        assert response_data["total_count"] == 2
        assert response_data["prompts"] == mock_prompts

        print("✓ get_prompts tool test passed")


async def test_execute_prompt_tool():
    """Test the execute_prompt tool."""

    mock_response_text = "This is a test response from the prompt execution"

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.text = mock_response_text
        mock_response.headers = {"content-type": "text/plain"}
        mock_response.raise_for_status.return_value = None
        mock_client.post.return_value = mock_response
        mock_client_class.return_value = mock_client

        from mcp_server import HaivenMCPServer

        server = HaivenMCPServer("http://localhost:8000")

        # Test with minimal parameters
        arguments = {"userinput": "Test user input"}
        result = await server._execute_prompt(arguments)

        # Verify API call
        expected_data = {"userinput": "Test user input", "json": False}
        mock_client.post.assert_called_once_with(
            "http://localhost:8000/api/prompt",
            json=expected_data,
            headers={"Content-Type": "application/json"},
        )

        # Verify response
        assert len(result) == 1
        content = result[0]
        assert content.type == "text"
        assert content.text == mock_response_text

        print("✓ execute_prompt tool test passed")


async def test_execute_prompt_with_all_params():
    """Test the execute_prompt tool with all parameters."""

    mock_response_data = {"result": "Test JSON response"}

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.headers = {"content-type": "application/json"}
        mock_response.raise_for_status.return_value = None
        mock_client.post.return_value = mock_response
        mock_client_class.return_value = mock_client

        from mcp_server import HaivenMCPServer

        server = HaivenMCPServer("http://localhost:8000")

        # Test with all parameters
        arguments = {
            "userinput": "Test user input",
            "promptid": "test-prompt",
            "chatSessionId": "session-123",
            "contexts": ["context1", "context2"],
            "document": ["doc1", "doc2"],
            "json_output": True,
            "userContext": "Test user context",
        }
        result = await server._execute_prompt(arguments)

        # Verify API call with all parameters
        expected_data = {
            "userinput": "Test user input",
            "promptid": "test-prompt",
            "chatSessionId": "session-123",
            "contexts": ["context1", "context2"],
            "document": ["doc1", "doc2"],
            "json": True,
            "userContext": "Test user context",
        }
        mock_client.post.assert_called_once_with(
            "http://localhost:8000/api/prompt",
            json=expected_data,
            headers={"Content-Type": "application/json"},
        )

        # Verify JSON response
        assert len(result) == 1
        content = result[0]
        assert content.type == "text"
        response_data = json.loads(content.text)
        assert response_data == mock_response_data

        print("✓ execute_prompt with all parameters test passed")


async def test_error_handling():
    """Test error handling in the MCP server."""

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("Connection error")
        mock_client.get.return_value = mock_response
        mock_client_class.return_value = mock_client

        from mcp_server import HaivenMCPServer

        server = HaivenMCPServer("http://localhost:8000")
        result = await server._get_prompts()

        # Verify error is handled gracefully
        assert len(result) == 1
        content = result[0]
        assert content.type == "text"
        assert "Error" in content.text

        print("✓ Error handling test passed")


async def main():
    """Run all tests."""
    try:
        print("Running Haiven MCP Server tests...")

        await test_mcp_server_creation()
        await test_get_prompts_tool()
        await test_execute_prompt_tool()
        await test_execute_prompt_with_all_params()
        await test_error_handling()

        print("\n🎉 All tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
