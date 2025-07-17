# ADR 5: Create MCP Server for AI Tool Integration

*This ADR was generated using the Haiven ADR prompt and reflects a thorough analysis of requirements, codebase usage, cost, and technical fit as of July 2025.* 

## Context

We need a way for users to access Haiven's AI prompts and capabilities from within their preferred AI development tools (Claude Desktop, VS Code, Cursor, etc.) without having to switch between applications.

Our requirements:

- Enable seamless integration of Haiven prompts with popular AI tools
- Support multiple AI applications using a standardized protocol
- Maintain authentication and security for API access
- Provide a lightweight, user-friendly installation experience
- Allow users to discover and execute Haiven prompts from their AI tools
- Support both development and production environments

The Model Context Protocol (MCP) has emerged as a standardized way for AI applications to connect to external tools and services. Many popular AI tools now support MCP servers.

## Options Considered

### Option 1: Do Nothing - Users Continue Using Web UI Only

#### Consequences
✅ Pros:
- No additional development effort required
- Single interface to maintain
- Full control over user experience

❌ Cons:
- Users must switch between AI tools and Haiven web interface
- Loses conversation context when switching between applications
- Higher friction for adoption in development workflows
- Cannot leverage AI tools' native capabilities (code editing, project context, etc.)

### Option 2: Build Custom Integrations for Each AI Tool

#### Consequences
✅ Pros:
- Tailored experience for each AI tool
- Maximum feature integration with each platform

❌ Cons:
- Significant development and maintenance overhead
- Need to learn different APIs and protocols for each tool
- Fragmented user experience across tools
- High risk of integrations breaking with tool updates

### Option 3: Create MCP Server (Chosen)

#### Consequences
✅ Pros:
- Single implementation works across all MCP-compatible AI tools
- Standardized protocol reduces maintenance burden
- Lightweight bridge that communicates via HTTP APIs
- Users can access Haiven prompts within their existing workflows
- Maintains conversation context within AI tools
- Easy to distribute and install
- Supports both development and production environments

❌ Cons:
- Additional component to maintain and distribute
- Dependency on MCP protocol adoption by AI tools
- Users need to configure their AI tools to use the MCP server
- Potential authentication complexity for enterprise deployments

## Decision

Option 3: Create an MCP Server for Haiven

We will implement a standalone MCP server that:
- Provides two main tools: `get_prompts` and `get_prompt_content`
- Communicates with Haiven via HTTP API calls
- Supports multiple authentication methods (session cookies, API keys, development mode)
- Can be easily installed and configured by end users
- Works with Claude Desktop, VS Code, Cursor, and other MCP-compatible tools

## Repository Structure Decision

### Additional Context
The MCP server serves a fundamentally different user base than the main Haiven application:
- **Main Haiven Repository**: Targets developers and organizations who deploy, customize, or contribute to the Haiven platform
- **MCP Server**: Targets end users who want to integrate existing Haiven instances with their AI development tools

### Repository Options Considered

#### Option A: Keep MCP Server in Main Repository
✅ Pros:
- Coordinated releases and API compatibility
- Single source of truth for all Haiven components
- Easier integration testing during development

❌ Cons:
- End users must download entire Haiven codebase for MCP integration
- Confusing for users who only want AI tool integration
- Mixed audience (developers vs end users) in same repository
- Heavyweight installation process (navigate to subdirectory, etc.)

#### Option B: Move MCP Server to Separate Repository (Recommended)
✅ Pros:
- **Clear user separation**: End users get focused, lightweight repository
- **Simplified installation**: Direct download and setup without navigating main codebase
- **Better discoverability**: Users can find and star MCP integration specifically
- **Independent versioning**: MCP server updates don't require main application releases
- **Focused documentation**: All guides target AI tool integration use case
- **Package distribution**: Can be published to PyPI as `haiven-mcp-server`

❌ Cons:
- **Coordination overhead**: Need to ensure API compatibility across repositories
- **Testing complexity**: Integration tests span multiple repositories
- **Duplicate maintenance**: Separate CI/CD, issue tracking, and governance

### Decision
Create MCP server as a separate repository.

**Rationale**: The MCP server is architecturally independent and serves a distinct user base. End users seeking AI tool integration should not need to navigate developer-focused repository structure or download unnecessary codebase components.

## Consequences

### Implementation
- MCP server is architecturally independent of main Haiven application
- Uses MCP protocol library and HTTP client
- Includes comprehensive documentation and setup guides
- Provides installation scripts for different operating systems

### User Experience
- Users can ask "What Haiven prompts are available?" directly in their AI tool
- Prompts can be executed without leaving the AI tool context
- Maintains conversation history while using Haiven capabilities
- Reduces friction for adoption in development workflows

### Distribution and Maintenance
- Separate packaging and distribution from main Haiven application
- Independent release cycles for MCP server updates
- Clear separation between platform development and AI tool integration
- **Migration to separate repository**: Provides focused experience for end users
- **Simplified distribution**: Can be published to package managers (PyPI)
- **Targeted documentation**: All setup guides focus on AI tool integration use case

### Trade-offs
- Additional component increases overall system complexity
- Users need to perform one-time setup and configuration
- Requires coordination between MCP server and API changes across repositories
- Success depends on continued MCP protocol adoption by AI tools
- **Repository separation**: Reduces complexity for end users but increases coordination overhead for developers

This decision enables Haiven to integrate seamlessly into users' existing AI-powered development workflows while maintaining architectural independence and ease of maintenance. 