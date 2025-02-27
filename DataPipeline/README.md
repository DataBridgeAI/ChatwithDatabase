# NL to SQL Chatbot - Data Pipeline

This repository contains the data pipeline components for a natural language to SQL conversion chatbot that uses OpenAI models and connects to BigQuery.

## Overview

The data pipeline extracts schema metadata from BigQuery, formats it for optimal prompting, and prepares the environment for natural language to SQL conversion. The pipeline is orchestrated using Apache Airflow and version controlled with DVC.

## Prerequisites

- Google Cloud Platform account with BigQuery access
- Python 3.8+
- Apache Airflow
- DVC for data versioning
- OpenAI API key

## Project Structure

```
/Project Repo
├── Data-Pipeline/
│   ├── dags/               # Apache Airflow DAG definitions
│   ├── data/               # Storage for schema and example data
│   │   ├── raw/            # Raw data
│   │   ├── processed/      # Processed data
│   │   └── schema/         # Extracted schema information
│   ├── scripts/            # Python scripts for data processing
│   ├── tests/              # Unit and integration tests
│   ├── logs/               # Log files
│   ├── dvc.yaml            # DVC pipeline definition
│   └── README.md           # This file
```

## Data Pipeline Process

1. **Schema Extraction**: Extracts table and column metadata from BigQuery
2. **Schema Formatting**: Processes schema into a format optimized for OpenAI prompts
3. **Example Collection**: Gathers example NL-SQL pairs for evaluation and fine-tuning
4. **Prompt Engineering**: Creates and tests different prompt templates
5. **Evaluation**: Measures the quality of generated SQL

## Setup Instructions

### 1. Environment Setup

Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure GCP Credentials

```bash
gcloud auth application-default login
export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/service-account-key.json"
```

### 3. Initialize DVC

```bash
dvc init
dvc remote add -d myremote gs://your-bucket-name/dvc-storage
```

### 4. Set Configuration

Create a `config.yaml` file with the following content:

```yaml
project_id: your-gcp-project-id
dataset_id: your-bigquery-dataset
bucket_name: your-gcs-bucket
openai_api_key: your-openai-api-key
```

### 5. Run the Pipeline

```bash
dvc repro
```

## Airflow Setup

1. Set environment variables for Airflow:

```bash
export AIRFLOW_HOME=$(pwd)/airflow
export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/service-account-key.json"
```

2. Initialize Airflow database:

```bash
airflow db init
airflow users create \
    --username admin \
    --password admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com
```

3. Start Airflow services:

```bash
airflow webserver -p 8080 &
airflow scheduler &
```

4. Set up Airflow variables:

```bash
airflow variables set gcp_project_id your-gcp-project-id
airflow variables set bigquery_dataset_id your-bigquery-dataset
airflow variables set gcs_bucket your-gcs-bucket
```

## Testing

Run tests with:

```bash
pytest tests/
```

## Logging

Logs are stored in the `logs/` directory. You can view them with:

```bash
less logs/schema_processor.log
```

## Contributing

Please follow these steps for contributing:
1. Create a new branch for your feature
2. Add tests for your changes
3. Ensure all tests pass
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.