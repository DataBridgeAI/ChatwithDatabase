# Use a stable Airflow image with Python 3.9
FROM apache/airflow:2.6.1-python3.9

# Switch to root to install dependencies
USER airflow

# Copy the requirements.txt file into the Docker container
COPY requirements.txt /requirements.txt

# Install the dependencies
RUN pip install --no-cache-dir -r /requirements.txt

# # Switch back to airflow user
# USER airflow
