# README: Machine Learning Model Development and CI/CD Pipeline

## Overview
This project focuses on integrating Machine Learning (ML) model development within a Continuous Integration/Continuous Deployment (CI/CD) pipeline. It incorporates best practices in model validation, bias detection, sensitivity analysis, and experiment tracking to ensure robustness, fairness, and reproducibility.

## Scope of Implementation
Our project does **not** include training a completely new ML model from scratch. Instead, we focus on **fine-tuning a pre-trained model** and ensuring its effective deployment. Consequently, some aspects of the provided assignment guidelines, such as **extensive hyperparameter tuning** or **custom model training**, are not fully applicable. Below, we provide a breakdown of our implementation decisions and deviations.

---

## 1. Model Development and ML Code

Our implementation focuses on developing a natural language to SQL generation system using GPT-4 through LangChain, with emphasis on prompt engineering, validation, and version control. Key aspects include:

### Implemented Components:

#### 1. Loading Data from Data Pipeline
- **BigQuery Schema Management**: 
  - Schema extraction and versioning via `database/schema.py`
  - Dynamic table metadata retrieval through BigQuery API
  - Automated schema updates using Cloud Composer DAGs
- **Schema Processing Pipeline**:
  - Vector embeddings generation using Vertex AI's `textembedding-gecko@003`
  - Efficient storage and retrieval through ChromaDB collections
  - Schema-aware context management for enhanced query accuracy

#### 2. Model Selection and Fine-tuning
- **LLM Integration**: 
  - GPT-4 implementation through LangChain framework in `ai/llm.py`
  - Configurable model parameters (temperature, top_p) for SQL generation
  - Context-aware query generation with schema understanding
- **Prompt Engineering**:
  - Versioned prompt templates stored in GCS bucket (`sql-prompts-store`)
  - Template validation through `PromptValidation/prompt_validator.py`
  - Dynamic prompt enhancement based on feedback
- **Performance Optimization**:
  - Query success tracking via MLflow in `monitoring/mlflow_config.py`
  - Automated validation through Cloud Composer DAGs
  - Real-time performance monitoring and logging

#### 3. Model Validation Process
- **Validation Pipeline**:
  - Implementation in `Model_validation/model_validation.py`
  - Metrics tracking:
    - SQL query execution success rate
    - Semantic accuracy and relevance scores
    - Response time and efficiency metrics
- **Continuous Validation**:
  - Automated testing through GitHub Actions
  - Integration with BigQuery for result verification
  - Slack notifications for validation status

#### 4. Bias Detection Through Data Slicing
- **Query Analysis**:
  - Performance evaluation across:
    - Query complexity categories
    - Schema coverage and table relationships
    - User interaction patterns
- **Monitoring Tools**:
  - Bias detection implementation in `PromptValidation/prompt_monitor.py`
  - Query relevance checking through semantic search
  - Performance analysis across different query types

#### 5. Prompt Version Control and Storage
- **Version Management**:
  - Prompt templates stored in GCS bucket instead of Artifact Registry
  - Version tracking through timestamp-based IDs
  - Metadata storage for each prompt version
- **Storage Implementation**:
  - GCS bucket management in `PromptValidation/prompt_validator.py`
  - Version history maintenance
  - Automated backup and recovery mechanisms

### Implementation Details:
- **Core Technologies**:
  - LangChain for GPT-4 integration
  - MLflow for experiment tracking
  - ChromaDB for embedding storage
  - Cloud Composer for orchestration
- **Monitoring Setup**:
  - Query performance tracking
  - User feedback collection
  - Automated validation workflows

### Code Structure:
```
project/
├── src/
│   ├── ai/
│   │   └── llm.py                    # LLM integration
│   ├── database/
│   │   ├── query_executor.py         # BigQuery interaction
│   │   └── schema.py                 # Schema management
│   ├── monitoring/
│   │   └── mlflow_config.py          # Experiment tracking
│   └── feedback/
│       └── vector_search.py          # Feedback processing
├── DataPipeline/
│   ├── dags/
│   │   ├── model_validation_dag.py   # Validation workflow
│   │   └── schema_embeddings.py      # Schema processing
│   └── scripts/
│       └── schema_embeddings_processor.py
└── Model_validation/
    └── model_validation.py           # Validation logic
```

### Note on Model Storage:
Instead of using Artifact Registry, our implementation focuses on:
- Storing model configurations and prompt templates in version control
- Tracking experiments and versions through MLflow
- Maintaining model performance metrics in BigQuery
- Using Cloud Composer for orchestration and deployment

---
## 2. Hyperparameter Tuning
To optimize the quality and reliability of SQL query generation using the GPT-4 model via LangChain, we performed **hyperparameter tuning** on key model parameters. The tuning process helps identify the best configuration that balances **accuracy**, **performance**, and **consistency**.

## Parameters Tuned:
- **temperature**: Controls the randomness of the output.
- **top_p**: Limits token selection to a subset with the highest cumulative probability.
- **frequency_penalty**: Penalizes repeated terms to reduce redundancy.
- **presence_penalty**: Encourages the inclusion of new or diverse content.

## How It Works:
A grid search is performed across combinations of the above parameters. For each combination:
1. A natural language query is converted into SQL using the model.
2. The generated SQL is executed on BigQuery.
3. Success/failure and execution time are recorded.
4. Results are saved in a CSV (`tuning_results.csv`) for analysis.

## Analysis:
A companion script generates visualizations including:
- Success vs. failure rates by configuration
- Execution time distribution
- Pairwise parameter plots
- Correlation matrix
- Top-performing configurations

These insights help select the most effective model settings for consistent and correct SQL generation.

---

## 3. Experiment Tracking and Results

Our experiment tracking system leverages MLflow to comprehensively monitor and analyze the SQL generation model's performance. The implementation spans across multiple components:

### MLflow Implementation Details:

#### 1. Query Execution Tracking
- **Core Implementation**: `monitoring/mlflow_config.py`
  - Tracks execution metrics through `QueryTracker` class
  - Logs comprehensive query execution details including:
    - Execution times (BigQuery and total processing)
    - Query complexity metrics
    - Success/failure status
    - User feedback

#### 2. Tracked Metrics
- **Performance Metrics**:
  - BigQuery execution time
  - Total processing time (including LLM)
  - Query and SQL lengths
  - Result row and column counts
- **Complexity Analysis**:
  - Table count in queries
  - Join operations count
  - WHERE conditions count
- **Query Categorization**:
  - Query type (select, aggregate, join, etc.)
  - Complexity levels (simple, moderate, complex)
  - Performance categories (fast, medium, slow)

#### 3. Experiment Organization
- **Structure**:
  - Experiment Name: "sql_execution_tracking"
  - Run Names: Timestamped query executions (`query_exec_YYYYMMDD_HHMMSS`)
  - Environment tags for development/production tracking
- **Parameter Tracking**:
  - Model: gpt-4
  - Temperature: 0.3
  - Additional metadata from query execution

#### 4. Detailed Logging
- **Query Details**:
  - Original user query
  - Generated SQL (formatted)
  - Error messages (if any)
- **Performance Tags**:
  - Query status (success/error)
  - Performance category
  - Query complexity
  - Query type

### Integration Points
- **Application Integration**: 
  - `src/app.py` initializes tracking for each user interaction
  - Real-time logging of query execution metrics
  - Automatic tracking of query success/failure

### Key Insights from MLflow Tracking
- Performance patterns across different query complexities
- Correlation between query types and execution times
- Success rate analysis for various query categories
- Impact of query complexity on overall performance

---

## 4. Model Sensitivity Analysis
### Implemented:
- **Feature Importance Analysis**: Using **SHAP (SHapley Additive Explanations)** to understand which features impact predictions the most.
- **Hyperparameter Sensitivity (Limited)**: Since we fine-tune an existing model, we analyze how changes in prompt structure affect performance.

---

## 5. Model Bias Detection
### Implemented:
- **Slicing Data for Fairness Analysis**: We evaluate model performance across different subgroups (e.g., gender, region, age groups).
- **Bias Mitigation Strategies**: If bias is detected, we adjust the dataset distribution or tweak model decision thresholds.
- **Bias Documentation**: We maintain reports to track fairness improvements over time.

---

## 6. CI/CD Pipeline Automation

To ensure the reliability, accuracy, and fairness of SQL query generation, we have implemented a CI/CD pipeline using GitHub Actions. This pipeline automates various tasks related to semantic search validation, prompt validation, and database connectivity checks before deploying any changes.

### 1. CI/CD for Semantic Search and Model Validation
Semantic search is used to determine if a user's input query is relevant to the dataset stored in Google BigQuery. This is crucial for filtering out irrelevant or harmful queries before passing them to the SQL query generator. Additionally, model validation is performed to ensure the accuracy and relevance of model-generated queries.

- **Semantic Search Tests**: The CI/CD pipeline runs tests to validate whether a user’s input query is relevant to the dataset. This prevents incorrect, misleading, or irrelevant queries from being processed.
- **Model Validation Tests**: The model's performance is evaluated based on specific metrics, including precision, recall, and F1-score, which are essential for assessing the accuracy and effectiveness of the generated SQL queries.
  - **Evaluation Metrics**: The pipeline fetches data on generated SQL, correct SQL, and feedback from BigQuery.
  - **Precision, Recall, and F1-Score Calculation**: The model's predictions are compared against the ground truth (correct SQL queries), and metrics are computed using `sklearn`'s `precision_score`, `recall_score`, and `f1_score`.
  - **Metrics Storage**: After evaluation, the computed metrics are stored in a BigQuery table, allowing for easy tracking and analysis over time.
  - **Continuous Monitoring**: The metrics are updated regularly to evaluate the model's performance and ensure that it is improving or at least maintaining a consistent level of quality.

### 2. Automated Prompt Validation and Bias Detection
- **Prompt Validation**: The CI/CD pipeline runs unit tests to ensure the natural language prompts are correctly structured and converted into syntactically correct SQL queries. This ensures query correctness before execution and improves user experience.
- **Bias Detection**: The pipeline checks the model's output for potential bias by testing against various data slices.
- **Notification**: After the prompt validation and bias detection tests, the pipeline sends notifications to inform the team about test results.

### 3. Google Cloud BigQuery Connectivity Checks
- The pipeline checks for connectivity to BigQuery and verifies that authentication credentials are properly set up.
- It ensures the required dataset and tables are available for querying.
- Prevents failures related to misconfigured credentials, missing datasets, or API access issues.
- Ensures seamless interaction between the application and BigQuery, reducing downtime.

### 4. Model and User Query Relevance Validation
This CI/CD pipeline validates the relevance of user queries and checks for semantic accuracy using a model. The pipeline tests whether the generated SQL queries make sense within the context of the dataset.
- The pipeline performs **semantic search validation** to ensure that the user's query matches the dataset.
- **Model validation tests** are performed to confirm that the system correctly interprets user input and generates accurate SQL queries.
- Ensures the SQL generation is based on valid, relevant queries.
- Helps maintain consistent query quality and accuracy by ensuring model performance is up to standards.

---

## 7. Code Implementation
### Implemented:
- **Containerized Model Code (Docker-based Deployment)**: Ensures **reproducibility and scalability**.
- **Data Retrieval from Pre-processed Pipeline**: Ensures consistency across training runs.
- **Model Fine-tuning & Selection Logic**: Compares model variants and selects the best-performing one.
- **Bias Checking Code**: Generates **bias reports** for transparent evaluation.
- **Automated Model Registry Updates**: Version control is handled via **Google Cloud Registry**.

### Not Applicable:
- **Custom Model Training Implementation**: We do not train a model from scratch; instead, we fine-tune an existing one.
- **Hyperparameter Tuning Optimization**: Since we use pre-trained embeddings, extensive tuning is unnecessary.

---

## Summary of Key Deviations
| Assignment Requirement | Implemented? | Reason |
|------------------------|-------------|--------|
| Training a New Model from Scratch | ❌ | We fine-tune a pre-trained GPT-4 model instead. |
| Hyperparameter Tuning | ❌ | Not needed due to pre-trained embeddings. |
| CI/CD Pipeline for Model Training | ✅ | Automatically validates, detects bias, and pushes models. |
| Bias Detection & Mitigation | ✅ | Data slicing, metric tracking, and fairness reports are implemented. |
| Model Artifact Registry | ✅ | Google Cloud Artifact Registry used for version control. |

---

## Conclusion
This project ensures **efficient model fine-tuning**, **bias detection**, and **CI/CD automation** while leveraging **pre-trained embeddings**. While certain assignment elements (e.g., custom model training and hyperparameter tuning) are not applicable, our implementation focuses on **robust validation, fairness, and deployment automation** in a real-world setting.

