# Overview

This project aims to develop an LLM-powered chatbot to generate SQL queries based on user input questions. The system will be built using Google Cloud Platform (GCP) and will incorporate MLOps best practices, including monitoring and CI/CD pipelines, to ensure robust and efficient operation.

This repository hosts the data pipeline designed to process data in BigQuery. The pipeline is responsible for creating and managing a retail dataset, which includes the following tables:
- **Customers**
- **OrderItems**
- **Orders**
- **ProductReviews**
- **Products**

# Data Pipeline - Key Components and Workflow

The data pipeline is implemented using Apache Airflow to orchestrate tasks that extract, transform, and load (ETL) data into BigQuery. It includes several DAGs (Directed Acyclic Graphs) to automate schema extraction, feedback processing, and embedding generation for enhanced query interpretation.

## Key Components:
1. **Schema Extraction DAG (`extract_bigquery_schema`)**
   - Extracts table schemas from BigQuery.
   - Saves schema files to Google Cloud Storage (GCS) for further processing.
   - Validates the schema extraction process.
   - Sends notifications via Slack upon successful execution.
   ![Logo](assets/extract_bigquery_schema_graph.png)

2. **Feedback Embeddings DAG (`feedback_embeddings_dag`)**
   - Extracts user feedback data from BigQuery.
   - Generates embeddings for feedback questions using `sentence-transformers`.
   - Stores processed data and embeddings in GCS for downstream use.
   - Archives and uploads a ChromaDB store of embeddings.
   - Sends notifications via Slack upon successful execution.
   ![Logo](assets/Feedback_embeddings_graph.png)

3. **Schema Embeddings DAG (`schema_embeddings_dag`)**
   - Creates embeddings for schema metadata using Vertex AI’s `textembedding-gecko@003` model.
   - Stores embeddings in a ChromaDB instance.
   - Saves the ChromaDB instance to GCS for efficient retrieval.
   - Sends notifications via Slack upon successful execution.
   ![Logo](assets/schema_embeddings_graph.png)

## Workflow:
1. **Schema Extraction:** The `extract_bigquery_schema` DAG retrieves table schemas from BigQuery, processes them for natural language prompts, and stores them in GCS.
2. **Feedback Processing:** The `feedback_embeddings_dag` extracts user feedback, converts it into embeddings, and archives the embeddings for retrieval.
3. **Schema Embeddings:** The `schema_embeddings_dag` generates embeddings for table schemas to facilitate SQL query generation.
4. **Notifications:** Each DAG includes a Slack notification task to inform users of the pipeline’s execution status.

This modular approach ensures a scalable and efficient pipeline, supporting AI-driven SQL generation and query interpretation.



# Instructions to Reproduce

To reproduce this data pipeline on Google Cloud Platform (GCP), follow these instructions:

## Prerequisites
- **Google Cloud Account:** Make sure you have an active Google Cloud account.
- **Project Setup:** Create a new GCP project or use an existing one. Note down the `PROJECT_ID`.
- **Billing Enabled:** Ensure billing is enabled for your project.
- **Google Cloud SDK:** Install the Google Cloud SDK to interact with GCP resources.
- **Python 3.x:** Ensure Python 3.10 or later is installed.

## Step 1: Set Up GCP Services and Resources
### 1.1 Enable Required APIs
Go to GCP Console and enable the following APIs:
- BigQuery
- Cloud Composer
- VertexAI

### 1.2 Set up BigQuery Datasets
Create the necessary datasets in BigQuery:
```sh
DATASET_ID="RetailDataset"
BQ_DATASET="Feedback_Dataset"
```

### 1.3 Set Up Cloud Storage Buckets
Create the required Cloud Storage buckets:
```sh
BUCKET_NAME="bigquery-schema-store"
GCS_BUCKET="feedback-questions-embeddings-store"
BUCKET_NAME="bigquery-embeddings-store"
```

Create a Cloud Storage bucket to store data and pipeline artifacts:
```sh
export BUCKET_NAME=<your-bucket-name>
gcloud storage buckets create gs://$BUCKET_NAME --project $PROJECT_ID --location=<region>
```
Ensure the region aligns with your Composer environment or use a multi-region bucket.

Create directories within the bucket:
```sh
gsutil mkdir gs://$BUCKET_NAME/data
```

## Step 2: Configure Airflow with Cloud Composer
### 2.1 Create a Cloud Composer Environment
- Go to the Cloud Composer page in the GCP Console.
- Create a new Composer environment, select Python 3 as the runtime, and use the same region as the other resources.
- Note the Composer Environment Name and GCS Bucket associated with Composer.

### 2.2 Upload DAGs and Scripts
- Update the GitHub workflows to match your GCP environment (Project, Bucket, etc.).
- The workflow will handle uploading the files to GCS automatically.

### 2.3 Install Python Dependencies
- Update the `requirements.txt` file with the necessary dependencies.
- Install the dependencies in Composer by specifying the path to `requirements.txt` in the Composer environment configuration.

## Step 3: CI/CD Pipeline Setup with GitHub Actions
### 3.1 GitHub Actions Workflow
The `airflow-ci.yml` workflow will:
- Run tests
- Upload DAGs and scripts to GCS only after test runs pass

## Step 4: Testing the Pipeline
### 4.1 Trigger the Pipeline
- Trigger the DAGs via the Composer UI or let them run as per the defined schedule.

### 4.2 Verify Data in Buckets
- After successful DAG runs, check your buckets for generated embeddings and schema data to confirm processing.

### 4.3 Logs and Debugging
- Monitor logs from Airflow in the Composer environment for debugging. Logs are available for each task within the DAG.

### 4.4 Alerts and Notifications
- Configure Slack notifications in Composer:
  - Set the **Connection ID**: `slack_webhook`
  - **Connection Type**: `HTTP`
  - **Host**: `https://hooks.slack.com/services/`
  - **Password**: Full Slack webhook URL

## Alternative: Running Locally
To run the Airflow pipeline locally using Docker, follow these steps:
```sh
docker compose build
docker compose up airflow-init
docker compose up
```

Following these steps will ensure a smooth deployment of the data pipeline on GCP and local environments.


