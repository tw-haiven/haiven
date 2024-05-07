# Stage 1: Build environment
FROM python:3.11-slim as python-builder

WORKDIR /app

# Install build dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy only pyproject.toml and poetry.lock files first to leverage Docker cache
COPY ./backend/pyproject.toml poetry.lock* ./

# Install the application's dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

######## NODE DEPENDENCIES ##############

FROM node:22-alpine AS node-deps 
RUN apk add --no-cache libc6-compat
RUN apk add --update python3 make g++ && rm -rf /var/cache/apk/*
WORKDIR /app

# COPY package.json yarn.lock ./
# RUN  yarn --frozen-lockfile
COPY package.json ./
RUN yarn install --production

######## NEXt BUILD ########
FROM node:22-alpine AS node-builder
WORKDIR /app
COPY --from=node-deps /app/node_modules ./node_modules
COPY . .

ENV NEXT_TELEMETRY_DISABLED 1

RUN yarn build
RUN rm -rf ./.next/cache

######### RUN #############
FROM nikolaik/python-nodejs:python3.11-nodejs22-slim as runner

WORKDIR /app

# PYTHON
COPY --from=python-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY ./backend /app/backend

# NODE
ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

COPY --from=node-builder /app/.next ./.next
COPY --from=node-builder /app/node_modules ./node_modules
COPY --from=node-builder /app/package.json ./package.json

# START

EXPOSE 3000

ENV PORT 3000

CMD python -u backend/main.py & yarn start
