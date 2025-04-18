FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY . ./src/

# Copy related modules needed by the backend
COPY ../Model_validation/ ./Model_validation/
COPY ../PromptValidation/ ./PromptValidation/
COPY ../hyperparameterTuning/ ./hyperparameterTuning/

# Set environment variables
ENV PYTHONPATH=/app

# Expose the port your backend runs on
EXPOSE 5001

# Run the application
CMD ["python", "src/app.py"]