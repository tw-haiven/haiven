# Stage 0: Frontend build
FROM node:22.18.0-alpine AS node-builder
RUN apk add --no-cache libc6-compat
RUN apk add --update python3 make g++ && rm -rf /var/cache/apk/*
WORKDIR /ui

COPY ./ui .

# RUN  yarn --frozen-lockfile
RUN yarn install --production

ENV NEXT_TELEMETRY_DISABLED 1

RUN yarn build

# Stage 1: Backend build environment
FROM python:3.12-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy only pyproject.toml and poetry.lock files first to leverage Docker cache
COPY ./app/pyproject.toml ./app/poetry.lock* ./

# Install the application's dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Stage 2: Production environment
FROM python:3.12-slim

# Create a non-root user
RUN addgroup --system --gid 999 appgroup \
    && adduser --system --uid 999 --ingroup appgroup appuser

WORKDIR /app

# Copy the installed application dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY ./app /app
COPY --from=node-builder /ui/out /app/resources/static/out

# Ensure proper permissions for the app user
RUN chown -R appuser:appgroup /app
USER appuser

EXPOSE 8080

CMD ["python", "-u", "main.py"]