# Junie Guidelines
**Backend tech stack**
- Our backend is in Python and in the app/ subfolder. The app needs to be started from that directory.
- We can instead run the backend tests from the root directory, using  `poetry run build` and `poetry run app`.
- The backend tests are in app/tests/
- When running tests or the application, the virtual environment in app/.venv first needs to be activated
- We're using constructor dependency injections to make our code more testable. Pass dependencies in via constructors, do not initialise them inside a class.
- When we wrap up a backend change, make sure to remind me to start up the whole application, to make sure that it's all well-integrated.
**Frontend tech stack**
- Our frontend is in JavaScript, React, Next, in the ui/ subfolder, code in ui/src/, tests in ui/src/__tests__. Make sure to navigate into the ui/ subfolder before executing yarn tasks.
- We're using Next in "client only" mode, NO server-side features, because we're distributing the frontend code as static resources that call a Python API for data
- We're using the "prettier" library for formatting

- **Testing Instructions**
- Make sure the test can be run without pre-requisites - tests should always set up and clean up their own test data
- Tests should be fast, ideally under 100ms each
- Tests should be isolated, no shared state between tests
- use `poetry run test` from the `haiven` folder to test the backend code.
- use `cd ui && yarn test && cd ..` to test frontend code

**Coding Instructions**
- ALWAYS Start with a test, then write the code to make it pass
- Use descriptive names for functions and variables, so that the code is self-documenting
- Use type hints for function parameters and return types
- Use docstrings to explain the purpose of functions and classes
- Use comments to explain complex logic, but avoid obvious comments
- Use consistent naming conventions, e.g. snake_case for functions and variables, CamelCase for classes
- before committing, run pre-commit hooks to check for formatting and linting issues
- Use git commit messages that are descriptive and follow the format: "type(scope): description" (e.g. "feat(ui): add new button component")
- NEVER FORCE PUSH to remote repositories automatically.
- 
**RULES IMPORTED FROM CURSOR**

## Tests
When I am not just asking a question, but we're building a new feature, then I would like you to always use TDD:
1. write a test first
2. run (or let me run) the test first so it can go red (fail)
and ONLY then
3. write the implementation
4. run the test again to see if it passes

## Ask me before making decisions like choosing a technology or framework

## Help me always get to the next "runnable" step that I can commit, remind me to make commits when we get to a point that is a working state

## Backend
- Our backend is in Python and in the app/ subfolder. The app needs to be started from that directory.
- The backend tests are in app/tests/
- When running tests or the application, the virtual environment in app/.venv first needs to be activated
- We're using constructor dependency injections to make our code more testable. Pass dependencies in via constructors, do not initialise them inside of a class.
- When we wrap up a backend change, make sure to remind me to start up the whole application, to make sure that it's all well-integrated.

## Frontend
- Our frontend is in JavaScript, React, Next, in the ui/ subfolder, code in ui/src/, tests in ui/src/__tests__. Make sure to navigate into the ui/ subfolder before executing yarn tasks.
- We're using Next in "client only" mode, NO server-side features, because we're distributing the frontend code as static resources that call a Python API for data
- We're using vitest for testing
- We're using the "prettier" library for formatting
- Always use remix icons for icons
- We are using yarn
- Do not create JSDocs
- Our components currently go in the ui/app folder, and the file naming convention is _name_of_component.js