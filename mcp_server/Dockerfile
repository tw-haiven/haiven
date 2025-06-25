# Use the official Python image as a base
FROM python:3.10-slim-buster

# Set environment variables
ENV PYTHONUNBUFFERED True
ENV PORT 8080

# Install Poetry
RUN pip install poetry

# Set the working directory in the container
WORKDIR /app

# Copy pyproject.toml and poetry.lock
COPY pyproject.toml poetry.lock ./

# Install the application's dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Copy the mcp_server.py file
COPY mcp_server.py ./

EXPOSE 8080

# Command to run the mcp_server.py application
CMD ["poetry", "run", "python", "mcp_server.py"]
