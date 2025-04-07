FROM apache/airflow:2.10.5

# Switch to airflow user
USER airflow

# Copy the requirements.txt file into the container
COPY requirements.txt /requirements.txt

# Install the required Python packages
RUN pip install --no-cache-dir -r /requirements.txt