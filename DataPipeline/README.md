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

## Data Acquisition
The SQL chatbot operates on organizational data stored in BigQuery, where users execute queries to retrieve relevant information. Unlike RAG-based systems, our chatbot directly translates natural language queries into SQL without requiring external document retrieval.
Since our use case does not involve data ingestion or ETL processes, our data pipeline focuses on three key workflows:
**1. Schema Extraction:**
Extracts metadata (table names, column names, data types, etc.) from BigQuery.
Ensures that the chatbot understands the database structure to generate accurate SQL queries.
**2. Schema Embeddings Generation:**
Converts extracted schema information into vector embeddings.
Enhances query generation by allowing semantic understanding of database structure.
**3. Feedback Processing:**
Collects user feedback on query results
Adjusts future query generation by leveraging historical feedback for continuous improvement.
Stores feedback data using ChromaDB for retrieval during query refinement.

Since the pipeline does not involve direct data acquisition from APIs or external sources, our focus is on schema understanding, embeddings, and iterative feedback integration to enhance SQL generation accuracy.  


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
