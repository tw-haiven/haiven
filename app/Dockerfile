# Stage 1: Build environment
FROM python:3.10-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        && rm -rf /var/lib/apt/lists/*

# Copy only requirements files first to leverage Docker cache
COPY requirements.txt .

# Install the application's dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Production environment
FROM python:3.10-slim

WORKDIR /app

# Copy the installed application dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY . /app

EXPOSE 8080

CMD ["python", "-u", "main.py"]