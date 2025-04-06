# Use Python 3.9 slim image as base
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY src/requirements.txt requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir flask flask-cors

# Copy the application code
COPY src/ /app/src/

# Create necessary directories
RUN mkdir -p /app/src/feedback_db /app/retrieved_chroma

# Set environment variables
ENV PYTHONPATH=/app
ENV GOOGLE_APPLICATION_CREDENTIALS="/app/src/config/gcpconnectkey.json"
ENV FLASK_APP="/app/src/app.py"
ENV FLASK_ENV="production"

# Expose Flask port
EXPOSE 5000

# Set healthcheck
HEALTHCHECK CMD curl --fail http://localhost:5000/api/health || exit 1

# Run Flask
CMD ["python", "src/app.py"]