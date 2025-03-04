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

3. **Schema Embeddings DAG (`schema_embeddings_dag`)**
   - Creates embeddings for schema metadata using Vertex AI’s `textembedding-gecko@003` model.
   - Stores embeddings in a ChromaDB instance.
   - Saves the ChromaDB instance to GCS for efficient retrieval.
   - Sends notifications via Slack upon successful execution.

## Workflow:
1. **Schema Extraction:** The `extract_bigquery_schema` DAG retrieves table schemas from BigQuery, processes them for natural language prompts, and stores them in GCS.
2. **Feedback Processing:** The `feedback_embeddings_dag` extracts user feedback, converts it into embeddings, and archives the embeddings for retrieval.
3. **Schema Embeddings:** The `schema_embeddings_dag` generates embeddings for table schemas to facilitate SQL query generation.
4. **Notifications:** Each DAG includes a Slack notification task to inform users of the pipeline’s execution status.

This modular approach ensures a scalable and efficient pipeline, supporting AI-driven SQL generation and query interpretation.

