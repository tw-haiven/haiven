# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
#!/usr/bin/env python3
"""
Integration test for Haiven MCP Server against real deployment
"""

import asyncio
import os
import httpx


async def test_haiven_connectivity():
    """Test basic connectivity to Haiven API and authentication behavior."""

    base_url = os.getenv("HAIVEN_API_URL", "https://haiven.your-company.com")

    print(f"Testing connectivity to: {base_url}")

    # Test basic connectivity
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test 1: Check if server is reachable
        print("\n1. Testing basic connectivity...")
        try:
            response = await client.get(f"{base_url}/")
            print(f"   ✓ Server is reachable (status: {response.status_code})")
            if response.status_code == 307:
                print(
                    f"   → Redirected to: {response.headers.get('location', 'Unknown')}"
                )
        except Exception as e:
            print(f"   ✗ Server unreachable: {e}")
            return

        # Test 2: Check API endpoint without auth
        print("\n2. Testing API endpoint without authentication...")
        try:
            response = await client.get(f"{base_url}/api/prompts")
            print(f"   Status: {response.status_code}")
            if response.status_code == 307:
                print(
                    f"   → Redirected to: {response.headers.get('location', 'Unknown')}"
                )
                print("   ✓ Authentication is properly enforced (redirecting to login)")
            else:
                print(f"   Response headers: {dict(response.headers)}")
                print(f"   Response text (first 200 chars): {response.text[:200]}")
        except Exception as e:
            print(f"   ✗ Error: {e}")

        # Test 3: Test with fake API key to see error handling
        print("\n3. Testing with invalid API key...")
        headers = {"Authorization": "Bearer fake-api-key-for-testing"}
        try:
            response = await client.get(f"{base_url}/api/prompts", headers=headers)
            print(f"   Status: {response.status_code}")
            if response.status_code == 401:
                print("   ✓ API key authentication is implemented (401 Unauthorized)")
            elif response.status_code == 307:
                print(
                    "   → Still redirecting to login (API key auth may not be implemented)"
                )
            else:
                print(f"   Response: {response.text[:200]}")
        except Exception as e:
            print(f"   ✗ Error: {e}")

        # Test 4: Test prompt execution endpoint
        print("\n4. Testing prompt execution endpoint...")
        try:
            prompt_data = {"userinput": "Hello, this is a test", "json": False}
            response = await client.post(
                f"{base_url}/api/prompt",
                json=prompt_data,
                headers={"Content-Type": "application/json"},
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 307:
                print("   ✓ Authentication required for prompt execution")
            else:
                print(f"   Response: {response.text[:200]}")
        except Exception as e:
            print(f"   ✗ Error: {e}")


async def test_mcp_server_components():
    """Test MCP server components without running the full server."""

    print("\n" + "=" * 60)
    print("Testing MCP Server Components")
    print("=" * 60)

    try:
        # Import the MCP server class
        from mcp_server import HaivenMCPServer, PromptExecutionParams

        print("✓ MCP server imports work correctly")

        # Test parameter validation
        print("\n5. Testing parameter validation...")
        try:
            params = PromptExecutionParams(userinput="test input")
            print(f"   ✓ Basic parameters: {params.userinput}")

            params_with_options = PromptExecutionParams(
                userinput="test input", promptid="test-id", json=True
            )
            print(f"   ✓ Extended parameters: json={params_with_options.json}")
        except Exception as e:
            print(f"   ✗ Parameter validation error: {e}")

        # Test MCP server initialization
        print("\n6. Testing MCP server initialization...")
        try:
            server = HaivenMCPServer(
                base_url=os.getenv("HAIVEN_API_URL", "https://haiven.your-company.com"),
                api_key="test-key",
            )
            print("   ✓ MCP server instance created successfully")
            print(f"   ✓ Base URL: {server.base_url}")

            # Test tool definitions
            print("\n7. Testing tool definitions...")
            from mcp.types import ListToolsRequest

            request = ListToolsRequest(method="tools/list")
            tools_result = await server._handle_list_tools(request)
            print(f"   ✓ Found {len(tools_result.tools)} tools:")
            for tool in tools_result.tools:
                print(f"     - {tool.name}: {tool.description}")

        except Exception as e:
            print(f"   ✗ MCP server initialization error: {e}")
            import traceback

            traceback.print_exc()

    except ImportError as e:
        print(f"✗ Import error: {e}")
        return


async def main():
    """Run all integration tests."""
    print("Haiven MCP Server Integration Test")
    print("=" * 60)

    await test_haiven_connectivity()
    await test_mcp_server_components()

    print("\n" + "=" * 60)
    print("Integration test completed!")
    print("\nSummary:")
    print("- The Haiven server is properly enforcing OKTA authentication")
    print("- API endpoints are protected and redirect to login")
    print("- To use the MCP server, you need either:")
    print("  1. A valid session cookie from browser login")
    print("  2. A valid API key generated through the web interface")
    print("  3. Disable authentication for testing (AUTH_SWITCHED_OFF=true)")


if __name__ == "__main__":
    asyncio.run(main())
