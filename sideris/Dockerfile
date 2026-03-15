FROM python:3.12-slim

# 1. System dependencies
RUN apt-get update && apt-get install -y \
    libcairo2-dev \
    libpango1.0-dev \
    libffi-dev \
    libgtk-3-0 \
    libglib2.0-0 \
    libxml2-dev \
    libxslt1-dev \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2. Pip installs
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copy code and pythonpath
COPY . .
ENV PYTHONPATH="/app"

EXPOSE 8624
