FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app

# Expose the port your backend runs on
EXPOSE 5001

# Run the application
CMD ["python", "app.py"]
