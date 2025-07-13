# Project Structure

This document outlines the structure of the Haiven project, which consists of a Python backend and a Next.js frontend.

## Root Directory Structure

```
.
├── app/                    # Python backend application
├── ui/                     # Next.js frontend application
├── cli/                    # Command-line interface tools
├── devscripts/            # Development scripts
├── docs/                  # Project documentation
└── various config files   # Configuration files for different tools
```

## Backend (app/)

The backend is a Python application with the following structure:

```
app/
├── api/                   # API endpoints and routes
├── config/               # Configuration management
├── embeddings/           # Embedding-related functionality
├── knowledge/            # Knowledge management system
├── llms/                # LLM integration and configuration
├── prompts/             # Prompt templates and management
├── resources/           # Static resources
├── tests/               # Backend tests
├── .venv/               # Python virtual environment
├── app.py               # Main application entry point
├── config_service.py    # Configuration service
├── knowledge_manager.py # Knowledge management system
├── logger.py           # Logging configuration
├── main.py             # Application initialization
└── server.py           # Server configuration
```

Key backend features:
- Uses constructor dependency injection for testability
- Tests are located in app/tests/
- Virtual environment must be activated before running tests or the application
- Configuration is managed through config.yaml

## Frontend (ui/)

The frontend is a Next.js application with the following structure:

```
ui/
├── src/                 # Source code
│   ├── app/            # React components
│   └── __tests__/      # Frontend tests
├── public/             # Static assets
├── .next/              # Next.js build output
└── various config files # Configuration for Next.js, TypeScript, etc.
```

Key frontend features:
- Built with Next.js in "client only" mode
- Uses React for UI components
- Vitest for testing
- Prettier for code formatting
- Remix icons for iconography
- Yarn for package management
- Components are stored in ui/app/ with naming convention _name_of_component.js

## Development Guidelines

1. Backend:
   - Always activate the virtual environment before running tests or the application
   - Follow constructor dependency injection pattern
   - Write tests in app/tests/
   - Test the full application integration after backend changes

2. Frontend:
   - Navigate to ui/ directory before running yarn tasks
   - Use Remix icons for all icons
   - Follow the component naming convention
   - Use Prettier for code formatting

3. General:
   - Make commits at working states
   - Follow TDD approach for new features
   - Test changes thoroughly before committing 