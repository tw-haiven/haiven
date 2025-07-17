# Haiven Development Guidelines

## Project Structure
- **Backend**: Python in `app/` subfolder - ALL backend commands run from `haiven/` directory
- **Frontend**: React/Next.js in `ui/` subfolder - navigate to `ui/` before yarn commands  
- **Tests**: Backend `app/tests/`, Frontend `ui/src/__tests__`
- **Virtual env**: `app/.venv` must be activated before running tests/app

### Running Application
```bash
# Backend (from haiven/ directory)
poetry run init
poetry run app

# Frontend 
cd ui && yarn copy              # Build UI
cd ui && yarn dev               # Hot reload (optional)
```

### Testing
```bash
poetry run test                 # Backend tests (from haiven)
cd ui && yarn test && cd ..     # Frontend tests
```

## TDD Workflow (MANDATORY)
**Always follow this sequence when building features:**
1. Write test first
2. Run test to see it fail (RED)
3. Write minimal code to pass
4. Run test to see it pass (GREEN)
5. Refactor while keeping tests green

## Pre-commit Hooks
```bash
pre-commit install              # Setup hooks
pre-commit run --all-files      # Run all hooks
```

## Code Standards

### Backend (Python)
- Use constructor dependency injection (pass deps via constructors)
- Use type hints for parameters and return types
- snake_case for functions/variables, PascalCase for classes
- Keep functions under 20 lines

### Frontend (React/Next.js)
- Components in `ui/app/` with naming `_component_name.js`
- Use Remix icons exclusively
- Next.js in "client only" mode (NO server-side features)
- Use pre-commit hooks to fix formatting issues after changes 
- No JSDocs

## Git Workflow
- Commit format: `type(scope): description` (e.g., `feat(ui): add chat component`)
- **NEVER FORCE PUSH** to remote repositories
- **ENFORCE** running pre-commit hooks before committing
- After backend changes: remind to start full application for integration testing

## Key Commands
```bash
# Poetry commands (from haiven/)
poetry run init                 # Install backend dependencies
poetry run app                  # Run backend
poetry run test                 # Run tests for backend

# Frontend commands (from ui/)
yarn install                    # Install dependencies  
yarn copy                       # Build UI code
yarn dev                        # Development server
yarn test                       # Run tests
```

## Environment
- Copy appropriate `.env` template: `app/.env.azure.template` → `app/.env`
- Set `AUTH_SWITCHED_OFF=true` for development
- Knowledge packs: clone `haiven-sample-knowledge-pack` or `haiven-tw-demo-knowledge-pack`

## Integration Notes
- Frontend connects to backend API on localhost:8080
- After backend changes, always test full application integration
- Use `poetry run pytest -m 'not integration' tests/` for unit tests only