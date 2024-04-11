# Stage 1: Build environment
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy only pyproject.toml and poetry.lock files first to leverage Docker cache
COPY pyproject.toml poetry.lock* ./

# Install the application's dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Stage 2: Production environment
FROM python:3.11-slim

WORKDIR /app

# Copy the installed application dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY . /app

EXPOSE 8080

CMD ["python", "-u", "main.py"]