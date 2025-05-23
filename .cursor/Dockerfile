# Use Node 22.6 as base image
FROM node:22.6

# Install Python 3, pip, and system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install yarn (should already be included in node image, but ensure it's available)
RUN npm install -g yarn

# Install Poetry
RUN pip3 install poetry

# Configure Poetry to not create virtual environments (since we're in a container)
RUN poetry config virtualenvs.create false
