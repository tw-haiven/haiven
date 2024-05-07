# Stage 0: Frontend build
FROM node:22-alpine AS node-deps
RUN apk add --no-cache libc6-compat
RUN apk add --update python3 make g++ && rm -rf /var/cache/apk/*
WORKDIR /ui

# COPY package.json yarn.lock ./
# RUN  yarn --frozen-lockfile
COPY ./ui/package.json ./
RUN yarn install --production

##################
FROM node:22-alpine AS node-builder
WORKDIR /ui
COPY --from=node-deps /ui/node_modules ./node_modules
COPY ./ui .

ENV NEXT_TELEMETRY_DISABLED 1

RUN yarn build
RUN rm -rf ./.next/cache

# Stage 1: Backend build environment
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
COPY ./app/pyproject.toml ./app/poetry.lock* ./

# Install the application's dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Stage 2: Production environment
FROM python:3.11-slim

WORKDIR /app

# Copy the installed application dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY ./app /app
COPY --from=node-builder /ui/out /app/resources/static/out

EXPOSE 8080

CMD ["python", "-u", "main.py"]