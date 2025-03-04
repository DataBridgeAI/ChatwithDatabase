# Data Pipeline

## Overview
This repository contains a structured data pipeline implemented using Apache Airflow for orchestrating data processing workflows. The pipeline covers data acquisition, preprocessing, testing, logging, version control, and monitoring to ensure high-quality data processing and reproducibility.

## Key Features
- **Data Acquisition**: Acquire database schema information, embeddings for queries, and feedback data from ChromaDB.
- **Data Preprocessing**: Convert natural language queries into embeddings.
- **Pipeline Orchestration**: Uses Apache Airflow to manage workflow execution.
- **Testing Modules**: Includes unit tests for data transformations using pytest.
- **Data Versioning**: Implements DVC for tracking dataset changes.
- **Logging and Monitoring**: Uses Airflow logging and Python's logging module for tracking.
- **Anomaly Detection**: Identifies missing values and data inconsistencies.

## 1. Data Acquisition
The SQL chatbot operates on organizational data stored in BigQuery, where users execute queries to retrieve relevant information. Unlike RAG-based systems, our chatbot directly translates natural language queries into SQL without requiring external document retrieval.
Since our use case does not involve data ingestion or ETL processes, our data pipeline focuses on three key workflows: <br>
**1. Schema Extraction:** <br>
Extracts metadata (table names, column names, data types, etc.) from BigQuery. <br>
Ensures that the chatbot understands the database structure to generate accurate SQL queries. <br>
**2. Schema Embeddings Generation:** <br>
Converts extracted schema information into vector embeddings.<br>
Enhances query generation by allowing semantic understanding of database structure.<br>
**3. Feedback Processing:** <br>
Collects user feedback on query results <br>
Adjusts future query generation by leveraging historical feedback for continuous improvement.<br>
Stores feedback data using ChromaDB for retrieval during query refinement.<br>

Since the pipeline does not involve direct data acquisition from APIs or external sources, our focus is on schema understanding, embeddings, and iterative feedback integration to enhance SQL generation accuracy.  

## 3. TestModules
To ensure the robustness and reliability of our SQL chatbot pipeline, we implement unit tests using pytest and unittest. These tests cover critical components such as schema extraction, embeddings generation, and feedback processing.
We have unit tests using pytest or unittest for: <br>
Schema extraction integrity. <br>
Embeddings generation correctness. <br>
Feedback processing (validating correct storage and retrieval). <br>
These tests help maintain accuracy, reliability, and adaptability in our chatbot pipeline

## 4. Pipeline Orchestration
The pipeline orchestration is handled by Apache Airflow to manage the workflow, automate tasks, and ensure proper execution. Our approach relies on file-based storage (ChromaDB for storing embeddings) and modular task dependencies to manage data flow between tasks. <br>
1. DAG 1: Schema Extraction <br>
Extract the schema of the database (e.g., table names, columns, and types) from BigQuery.
A task in the DAG will use BigQuery’s Python client to pull the schema data. This can be stored in a local or cloud-based file or a database for subsequent tasks to use.
2. DAG 2: Schema Embeddings <br>
Generate embeddings for schema schema information into embeddings.
Implementation: After schema extraction, this task will process the schemainto vector embeddings using VertexAIEmbeddings.

1. Local Setup (Using Docker for Airflow)
For local development, Docker Compose is the easiest way to run Airflow.

Step 1: Install Docker and Docker Compose
Install Docker: Download & Install Docker
Install Docker Compose (if not included in Docker Desktop)
pip install docker-compose
Step 2: Clone the Official Airflow Docker Repository
Run the following command to get Airflow’s Docker Compose setup:
git clone https://github.com/apache/airflow.git
cd airflow
Step 3: Create an .env File for Airflow Configuration
In the airflow directory, create a .env file to store environment variables:
echo -e "AIRFLOW_UID=$(id -u)\nAIRFLOW_GID=0" > .env
Step 4: Initialize Airflow Database
Run the following command to set up the Airflow metadata database:
docker-compose up airflow-init
Step 6: Start Airflow
Once the initialization is done, start the Airflow services:
docker-compose up -d
This will start services like:
Web Server (http://localhost:8080)
Scheduler
Workers
Metadata Database

2. Cloud Setup (Using Google Cloud Composer)
Google Cloud Composer is a managed Airflow service.
Step 1: Enable Required GCP Services
Run these commands to enable services:
gcloud services enable composer.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable aiplatform.googleapis.com
Step 2: Create a Cloud Composer Environment
Run the following command to create a Cloud Composer 2 environment:
gcloud composer environments create my-airflow-env \
    --location=us-east1 \
    --image-version=composer-2-airflow-2 \
    --env-variables GOOGLE_APPLICATION_CREDENTIALS=/home/airflow/gcs/data/yourgcpkey.json
Step 3: Deploy DAGs to Cloud Composer
Once the environment is ready, upload your DAGs:
gsutil cp dags/my_dag.py gs://my-airflow-bucket/dags/
Step 4: Verify DAGs in Cloud Composer
Open Google Cloud Console → Composer.
Click on your Airflow Environment.
Open Airflow UI.
Ensure the DAGs appear and are in an "idle" state.
Step 5: Deploy Python Packages for DAGs
If your DAGs require extra Python packages (e.g., google-cloud-bigquery), install them:
gcloud composer environments update my-airflow-env \
    --update-pypi-packages google-cloud-bigquery==3.10.0


## 5. DVC
DVC is primarily used for versioning static datasets, but it’s not suitable for our SQL chatbot for these reasons:

Data-Independent Use Case: The chatbot queries live data from BigQuery rather than relying on static datasets. There’s no need to version the dynamic data as it is always up-to-date.

BigQuery as the Source of Truth: Our chatbot works directly with BigQuery, which constantly evolves. There's no local dataset that requires version tracking.

No Data Transformation: The chatbot doesn’t generate or transform datasets but dynamically creates SQL queries based on user input, making DVC unnecessary.

In conclusion, since the chatbot doesn't depend on static datasets or transformations, DVC doesn't provide value in this scenario. The focus is on querying live data from BigQuery and processing user feedback.

## Exclusions
This project does not include bias detection, data slicing for subgroup analysis, or bias mitigation techniques, as these are not relevant to the scope of manufacturing data analytics.

## Project Structure
```
/Project Repo
├── Data-Pipeline/
│   ├── dags/               # Apache Airflow DAG definitions
│   ├── scripts/            # Python scripts for data processing
│   ├── tests/              # Unit and integration tests
│   ├── logs/               # Log files
│   ├── requirements.txt    # Requirements for project
│   └── README.md           # This file
```

### Running the Pipeline
Start Airflow:
```bash
airflow standalone
```
Trigger DAG:
```bash
airflow dags trigger manufacturing_data_pipeline
```
Start Streamlit app:
```bash
streamlit run app.py
```

## Reproducibility
- All data changes are tracked using DVC.
- The project follows modular design for easy updates.
- Detailed setup instructions ensure anyone can replicate the pipeline.

## Error Handling & Logging
- Logs are stored in `logs/` and monitored via Airflow.
- Errors in data acquisition and transformation trigger alerts.

## Testing
Run unit tests:
```bash
pytest tests/
```

## Data Pipeline Process

1. **Schema Extraction**: Extracts table and column metadata from BigQuery
2. **Schema Formatting**: Processes schema into a format optimized for OpenAI prompts
3. **Example Collection**: Gathers example NL-SQL pairs for evaluation and fine-tuning
4. **Prompt Engineering**: Creates and tests different prompt templates
5. **Evaluation**: Measures the quality of generated SQL
