# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
#!/usr/bin/env python3
"""
Generate working MCP configuration for your system
Fixes common "cwd" path issues
"""

import json
import sys
from pathlib import Path


def main():
    print("🔧 MCP Configuration Generator")
    print("=" * 35)
    print()

    # Get current directory
    current_dir = Path.cwd().absolute()
    script_path = current_dir / "mcp_server.py"

    print(f"📁 Current directory: {current_dir}")
    print("📄 Looking for: mcp_server.py")

    # Check if files exist
    if not script_path.exists():
        print("❌ mcp_server.py not found in current directory")
        print("   Make sure you're running this from the mcp-server directory")
        sys.exit(1)

    print("✅ mcp_server.py found")
    print()

    # Ask for configuration type
    print("🎯 What type of setup?")
    print("1. Local development (auth disabled)")
    print("2. Remote server (with API key)")

    choice = input("Enter choice (1 or 2): ").strip()

    if choice == "1":
        # Local development
        haiven_url = "http://localhost:8080"
        use_auth = False
        api_key = None
        print("✅ Local development configuration")
    elif choice == "2":
        # Remote server
        haiven_url = input("Enter Haiven server URL: ").strip()
        if not haiven_url.startswith(("http://", "https://")):
            print("❌ Please enter a complete URL starting with http:// or https://")
            sys.exit(1)

        api_key = input("Enter API key: ").strip()
        if len(api_key) < 10:
            print("❌ Please enter a valid API key")
            sys.exit(1)

        use_auth = True
        print("✅ Remote server configuration")
    else:
        print("❌ Invalid choice")
        sys.exit(1)

    print()

    # Generate configurations
    print("📋 Generated Configurations:")
    print("=" * 30)

    # 1. Configuration with full path (most reliable)
    config_fullpath = {
        "mcpServers": {
            "haiven": {
                "command": "python",
                "args": [str(script_path)],
                "env": {"HAIVEN_API_URL": haiven_url},
            }
        }
    }

    if use_auth:
        config_fullpath["mcpServers"]["haiven"]["env"]["HAIVEN_API_KEY"] = api_key
    else:
        config_fullpath["mcpServers"]["haiven"]["env"]["HAIVEN_DISABLE_AUTH"] = "true"

    print("\n✅ Option 1: Full path (RECOMMENDED - most reliable)")
    print(json.dumps(config_fullpath, indent=2))

    # 2. Configuration with cwd (if supported)
    config_cwd = {
        "mcpServers": {
            "haiven": {
                "command": "python",
                "args": ["mcp_server.py"],
                "cwd": str(current_dir),
                "env": {"HAIVEN_API_URL": haiven_url},
            }
        }
    }

    if use_auth:
        config_cwd["mcpServers"]["haiven"]["env"]["HAIVEN_API_KEY"] = api_key
    else:
        config_cwd["mcpServers"]["haiven"]["env"]["HAIVEN_DISABLE_AUTH"] = "true"

    print("\n✅ Option 2: With cwd (if your AI tool supports it)")
    print(json.dumps(config_cwd, indent=2))

    # 3. Configuration with Poetry
    config_poetry = {
        "mcpServers": {
            "haiven": {
                "command": "poetry",
                "args": ["run", "python", "mcp_server.py"],
                "cwd": str(current_dir),
                "env": {"HAIVEN_API_URL": haiven_url},
            }
        }
    }

    if use_auth:
        config_poetry["mcpServers"]["haiven"]["env"]["HAIVEN_API_KEY"] = api_key
    else:
        config_poetry["mcpServers"]["haiven"]["env"]["HAIVEN_DISABLE_AUTH"] = "true"

    print("\n✅ Option 3: With Poetry (if you prefer)")
    print(json.dumps(config_poetry, indent=2))

    # Write to files
    with open("mcp-config-fullpath.json", "w") as f:
        json.dump(config_fullpath, f, indent=2)

    with open("mcp-config-cwd.json", "w") as f:
        json.dump(config_cwd, f, indent=2)

    with open("mcp-config-poetry.json", "w") as f:
        json.dump(config_poetry, f, indent=2)

    print("\n📁 Configuration files created:")
    print("   - mcp-config-fullpath.json (recommended)")
    print("   - mcp-config-cwd.json")
    print("   - mcp-config-poetry.json")
    print()

    print("📋 How to use:")
    print("1. Copy the content from one of the options above")
    print("2. Paste it into your AI tool's MCP configuration")
    print("3. Restart your AI tool")
    print("4. Test: Ask 'What Haiven prompts are available?'")
    print()

    print("📱 Configuration locations:")
    print("   Claude Desktop: ~/.config/claude/config.json")
    print("   VS Code: Settings → search for 'mcp'")
    print("   Cursor: ~/.cursor/config.json")
    print()

    print("🎯 Start with Option 1 (full path) - it's the most reliable!")


if __name__ == "__main__":
    main()
