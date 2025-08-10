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
- Do not create JSDocs
- Our components currently go in the ui/app folder, and the file naming convention is _name_of_component.js
- Never use innerHTML in combination with useRef, consider React state instead, it is more secure