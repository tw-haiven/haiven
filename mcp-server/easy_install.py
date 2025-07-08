#!/usr/bin/env python3
"""
Haiven MCP Server Easy Installer
For non-technical users who want to connect Claude Desktop to Haiven
"""

import os
import sys
import json
import platform
import subprocess
from pathlib import Path


def print_header():
    """Print a friendly header."""
    print("🚀 " + "=" * 60)
    print("    Haiven MCP Server Easy Installer")
    print("    Connecting AI Tools to Haiven AI")
    print("=" * 62)
    print()


def check_python():
    """Check if Python is properly installed."""
    print("🐍 Checking Python installation...")

    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required. You have:", sys.version)
        print("   Please install Python from: https://python.org")
        return False

    print(f"✅ Python {version.major}.{version.minor}.{version.micro} found")
    return True


def install_dependencies():
    """Install required dependencies."""
    print("\n📦 Installing dependencies...")

    try:
        # Check if poetry is available
        subprocess.run(["poetry", "--version"], check=True, capture_output=True)
        print("✅ Poetry found")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("📦 Installing Poetry...")
        subprocess.run([sys.executable, "-m", "pip", "install", "poetry"], check=True)
        print("✅ Poetry installed")

    # Install project dependencies
    print("📦 Installing MCP server dependencies...")
    subprocess.run(["poetry", "install"], check=True)
    print("✅ Dependencies installed")


def get_user_input():
    """Get configuration from user."""
    print("\n🔧 Configuration Setup")
    print("=" * 40)

    # Get Haiven URL
    print("\n1. Haiven Server URL")
    print("   This is the web address where you access Haiven")
    print("   Example: https://haiven.your-company.com")

    while True:
        haiven_url = input("\n   Enter your Haiven URL: ").strip()
        if haiven_url.startswith(("http://", "https://")):
            break
        print("   ❌ Please enter a complete URL starting with http:// or https://")

    # Get API Key
    print("\n2. API Key")
    print("   You should have generated this from Haiven's 'API Keys' page")
    print("   ⚠️  If you haven't done this yet:")
    print("      1. Open Haiven in your browser")
    print("      2. Login with your work credentials")
    print("      3. Click 'API Keys' in the navigation")
    print("      4. Generate a new key")

    while True:
        api_key = input("\n   Enter your API Key: ").strip()
        if len(api_key) > 10:  # Basic validation
            break
        print("   ❌ Please enter a valid API key")

    return haiven_url, api_key


def find_claude_config_path():
    """Find Claude Desktop configuration file path."""
    system = platform.system()

    if system == "Windows":
        config_path = Path(os.environ["APPDATA"]) / "Claude" / "config.json"
    elif system == "Darwin":  # macOS
        config_path = (
            Path.home() / "Library" / "Application Support" / "Claude" / "config.json"
        )
    else:  # Linux
        config_path = Path.home() / ".config" / "claude" / "config.json"

    return config_path


def create_claude_config(haiven_url, api_key):
    """Create or update Claude Desktop configuration."""
    print("\n🔧 Setting up Claude Desktop integration...")
    print("   (For other AI tools, see the USER_SETUP_GUIDE.md)")

    config_path = find_claude_config_path()
    current_dir = Path.cwd().absolute()

    # Create config directory if it doesn't exist
    config_path.parent.mkdir(parents=True, exist_ok=True)

    # Load existing config or create new one
    if config_path.exists():
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
        except json.JSONDecodeError:
            config = {}
    else:
        config = {}

    # Ensure mcpServers section exists
    if "mcpServers" not in config:
        config["mcpServers"] = {}

    # Add Haiven MCP server configuration
    config["mcpServers"]["haiven"] = {
        "command": "python",
        "args": ["mcp_server.py"],
        "cwd": str(current_dir),
        "env": {"HAIVEN_API_URL": haiven_url, "HAIVEN_API_KEY": api_key},
    }

    # Write config file
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

    print(f"✅ Claude Desktop configured: {config_path}")
    print("   For other AI tools, copy this config to the appropriate location:")
    print("   VS Code: Add to your VS Code settings under 'mcp.servers'")
    print("   Cursor: ~/.cursor/config.json")
    print("   Other: Check your AI tool's MCP documentation")
    return config_path


def test_installation(haiven_url, api_key):
    """Test the MCP server installation."""
    print("\n🧪 Testing installation...")

    # Set environment variables
    env = os.environ.copy()
    env["HAIVEN_API_URL"] = haiven_url
    env["HAIVEN_API_KEY"] = api_key

    try:
        # Test basic import
        result = subprocess.run(
            [
                "poetry",
                "run",
                "python",
                "-c",
                "from mcp_server import HaivenMCPServer; print('✅ MCP server imports work')",
            ],
            capture_output=True,
            text=True,
            env=env,
            timeout=10,
        )

        if result.returncode == 0:
            print("✅ MCP server installation successful")
            return True
        else:
            print(f"❌ Import test failed: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("❌ Test timed out")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def print_next_steps():
    """Print instructions for what to do next."""
    print("\n🎉 Installation Complete!")
    print("=" * 40)
    print()
    print("Next steps:")
    print(
        "1. 🔄 Restart your AI tool completely (Claude Desktop, VS Code, Cursor, etc.)"
    )
    print("2. 📱 Look for 'haiven' in the MCP servers list")
    print("3. 💬 Try asking: 'What Haiven prompts are available?'")
    print()
    print("Troubleshooting:")
    print("- If your AI tool doesn't connect, restart it again")
    print("- Check that your API key is valid in Haiven web interface")
    print("- Make sure your AI tool supports MCP and is updated to the latest version")
    print()
    print("🆘 Need help? Share this output with your IT team!")


def main():
    """Main installation process."""
    print_header()

    try:
        # Check prerequisites
        if not check_python():
            sys.exit(1)

        # Install dependencies
        install_dependencies()

        # Get user configuration
        haiven_url, api_key = get_user_input()

        # Configure Claude Desktop
        create_claude_config(haiven_url, api_key)

        # Test installation
        if test_installation(haiven_url, api_key):
            print_next_steps()
        else:
            print("\n⚠️  Installation completed but tests failed.")
            print("The configuration should still work, but double-check your:")
            print("- Haiven URL")
            print("- API Key")
            print("- Internet connection")

    except KeyboardInterrupt:
        print("\n\n❌ Installation cancelled by user")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Installation failed: {e}")
        print("Try running this installer as administrator/with sudo")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please share this error with your IT team")
        sys.exit(1)


if __name__ == "__main__":
    main()
