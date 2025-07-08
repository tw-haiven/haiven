# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
#!/usr/bin/env python3
"""
Quick developer setup script for local Haiven MCP development
"""

import sys
import json
import subprocess
from pathlib import Path


def print_header():
    """Print developer header."""
    print("🛠️  " + "=" * 50)
    print("    Haiven MCP Local Development Setup")
    print("=" * 53)
    print()


def check_haiven_backend():
    """Check if Haiven backend is running locally."""
    print("🔍 Checking local Haiven backend...")

    try:
        import requests

        response = requests.get("http://localhost:8080/health", timeout=5)
        if response.status_code == 200:
            print("✅ Haiven backend is running at http://localhost:8080")
            return True
        else:
            print(f"⚠️  Haiven backend responded with status {response.status_code}")
            return False
    except ImportError:
        print("⚠️  'requests' not installed, skipping backend check")
        return True  # Assume it's running
    except Exception as e:
        print(f"❌ Haiven backend not running: {e}")
        print("   Start it with: cd app && source .venv/bin/activate && python dev.py")
        return False


def setup_environment():
    """Setup development environment variables."""
    print("\n🔧 Setting up development environment...")

    env_file = Path(".env")
    env_content = """# Haiven MCP Development Environment
HAIVEN_API_URL=http://localhost:8080
HAIVEN_DISABLE_AUTH=true
"""

    with open(env_file, "w") as f:
        f.write(env_content)

    print(f"✅ Created .env file: {env_file.absolute()}")
    return env_file


def install_dependencies():
    """Install MCP server dependencies."""
    print("\n📦 Installing MCP server dependencies...")

    try:
        subprocess.run(["poetry", "install"], check=True, capture_output=True)
        print("✅ Dependencies installed with Poetry")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False
    except FileNotFoundError:
        print("❌ Poetry not found. Install with: pip install poetry")
        return False

    return True


def test_mcp_server():
    """Test MCP server functionality."""
    print("\n🧪 Testing MCP server...")

    test_code = """
import os
import asyncio
import sys

# Set environment variables
os.environ['HAIVEN_API_URL'] = 'http://localhost:8080'
os.environ['HAIVEN_DISABLE_AUTH'] = 'true'

try:
    from mcp_server import HaivenMCPServer
    print('✅ MCP server imports successfully')
    
    async def test():
        server = HaivenMCPServer()
        try:
            result = await server.handle_get_prompts()
            print(f'✅ Found {len(result)} prompts')
            if result:
                print(f'✅ First prompt: {result[0].get("id", "unknown")}')
        except Exception as e:
            print(f'⚠️  Could not fetch prompts: {e}')
    
    asyncio.run(test())
    print('✅ MCP server test completed')

except Exception as e:
    print(f'❌ MCP server test failed: {e}')
    sys.exit(1)
"""

    try:
        result = subprocess.run(
            ["poetry", "run", "python", "-c", test_code],
            capture_output=True,
            text=True,
            timeout=30,
        )

        print(result.stdout)
        if result.stderr:
            print("Warnings:", result.stderr)

        if result.returncode == 0:
            print("✅ MCP server test passed!")
            return True
        else:
            print("❌ MCP server test failed")
            return False

    except subprocess.TimeoutExpired:
        print("❌ MCP server test timed out")
        return False
    except Exception as e:
        print(f"❌ MCP server test error: {e}")
        return False


def create_ai_tool_config():
    """Create sample AI tool configuration."""
    print("\n📋 Creating AI tool configuration examples...")

    current_dir = Path.cwd().absolute()

    # Claude Desktop config (using absolute path to avoid cwd issues)
    claude_config = {
        "mcpServers": {
            "haiven-dev": {
                "command": "python",
                "args": [str(current_dir / "mcp_server.py")],
                "env": {
                    "HAIVEN_API_URL": "http://localhost:8080",
                    "HAIVEN_DISABLE_AUTH": "true",
                },
            }
        }
    }

    # Claude Desktop config with cwd (fallback)
    claude_config_cwd = {
        "mcpServers": {
            "haiven-dev": {
                "command": "python",
                "args": ["mcp_server.py"],
                "cwd": str(current_dir),
                "env": {
                    "HAIVEN_API_URL": "http://localhost:8080",
                    "HAIVEN_DISABLE_AUTH": "true",
                },
            }
        }
    }

    # VS Code config (using absolute path)
    vscode_config = {
        "mcp.servers": {
            "haiven-dev": {
                "command": "python",
                "args": [str(current_dir / "mcp_server.py")],
                "env": {
                    "HAIVEN_API_URL": "http://localhost:8080",
                    "HAIVEN_DISABLE_AUTH": "true",
                },
            }
        }
    }

    # Write example configs
    with open("claude-desktop-config.json", "w") as f:
        json.dump(claude_config, f, indent=2)

    with open("claude-desktop-config-cwd.json", "w") as f:
        json.dump(claude_config_cwd, f, indent=2)

    with open("vscode-config.json", "w") as f:
        json.dump(vscode_config, f, indent=2)

    print("✅ Created configuration examples:")
    print("   - claude-desktop-config.json (absolute path - recommended)")
    print("   - claude-desktop-config-cwd.json (with cwd - fallback)")
    print("   - vscode-config.json (absolute path)")
    print()
    print("📋 To use these configs:")
    print("   Claude Desktop: Copy to ~/.config/claude/config.json")
    print("   VS Code: Add to your settings.json")
    print("   Cursor: Copy to ~/.cursor/config.json")
    print()
    print("💡 If you get 'cwd' errors, use the absolute path versions first!")


def print_next_steps():
    """Print what to do next."""
    print("\n🎉 Development setup complete!")
    print("=" * 40)
    print()
    print("Quick test:")
    print("1. 📱 Configure your AI tool (see config files created above)")
    print("2. 🔄 Restart your AI tool")
    print("3. 💬 Ask: 'What Haiven prompts are available?'")
    print()
    print("Development commands:")
    print("   # Load environment and run server")
    print("   source .env && poetry run python mcp_server.py")
    print()
    print("   # Quick test without AI tool")
    print(
        "   source .env && poetry run python -c 'from mcp_server import HaivenMCPServer; print(\"OK\")'"
    )
    print()
    print("   # Test API connectivity")
    print("   curl http://localhost:8080/api/prompts")
    print()
    print("🛠️  Happy local development!")


def main():
    """Main setup process."""
    print_header()

    try:
        # Check if Haiven backend is running
        if not check_haiven_backend():
            print("\n⚠️  Setup will continue, but make sure to start Haiven backend:")
            print("   cd app && source .venv/bin/activate && python dev.py")
            print()

        # Setup environment
        setup_environment()

        # Install dependencies
        if not install_dependencies():
            print("\n❌ Failed to install dependencies. Please run manually:")
            print("   poetry install")
            return

        # Test MCP server
        if not test_mcp_server():
            print("\n⚠️  MCP server tests failed, but setup continues...")

        # Create AI tool configs
        create_ai_tool_config()

        # Print next steps
        print_next_steps()

    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
