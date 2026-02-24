FROM python:3.12-slim

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

RUN pip install --upgrade pip

COPY . /app

ENV PYTHONPATH "${PYTHONPATH}:/app"

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 80