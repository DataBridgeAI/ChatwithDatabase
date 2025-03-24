# Machine Learning Model Development and CI/CD Pipeline

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
  - Automated daily schema updates using Cloud Composer DAG (`extract_bigquery_schema`)
  - Schema metadata extraction from RetailDataset tables:
    - Customers
    - OrderItems
    - Orders
    - ProductReviews
    - Products
  - Dynamic table metadata retrieval through BigQuery API for real-time schema updates

- **Schema Processing Pipeline**:
  - Vector embeddings generation using two distinct approaches:
    1. Schema embeddings via Vertex AI's `textembedding-gecko@003` model
       - Processes table and column metadata
       - Generates semantic descriptions for database structure
       - Stores embeddings in GCS bucket (`bigquery-embeddings-store`)
    2. Feedback embeddings via `sentence-transformers` (`all-MiniLM-L6-v2`)
       - Processes user queries and feedback
       - Stores in ChromaDB for efficient retrieval
       - Archives to GCS bucket (`feedback-questions-embeddings-store`)

- **Data Pipeline Orchestration**:
  - Three primary Airflow DAGs:
    1. `extract_bigquery_schema`: Daily schema extraction and processing
    2. `schema_embeddings_dag`: Schema embedding generation
    3. `feedback_embeddings_dag`: User feedback processing (6-hour intervals)
  - Automated notifications via Slack for pipeline status updates
  - Error handling and retry mechanisms for pipeline reliability

- **Schema-Aware Context Management**:
  - Real-time schema context integration through `check_query_relevance` function in `promptfilter/semantic_search.py`
  - Semantic search capabilities using cosine similarity to validate query relevance against schema embeddings
  - Threshold-based relevance checking (default similarity threshold: 0.75)
  - Schema embeddings stored and retrieved from GCS bucket (`bigquery-embeddings-store`)

#### 2. Model Selection and Fine-tuning
- **LLM Integration**: 
  - GPT-4 implementation through LangChain framework in `ai/llm.py`
  - Model configuration:
    - Base model: "gpt-4"
    - Default temperature: 0.3
  - Integration via ChatOpenAI from LangChain
- **Prompt Engineering**:
  - Versioned prompt templates stored in GCS bucket (`sql-prompts-store`)
  - Template validation through `PromptValidation/prompt_validator.py`
- **Hyperparameter Configuration**:
  - Tunable parameters:
    - temperature
    - top_p
    - frequency_penalty
    - presence_penalty
  - Parameter testing through grid search in `hyperparameterTuning/hyperparametertuner.py`
  - Performance evaluation based on BigQuery execution success

#### 3. Model Validation Process
- **Validation Pipeline**:
  - Implementation in `Model_validation/model_validation.py`
  - Metrics tracking:
    - Precision, recall, and F1 scores for SQL generation
    - Total samples processed
    - Correct vs. incorrect predictions count
  - Data collection through BigQuery tables:
    - Generated SQL storage
    - Correct SQL reference
    - User feedback tracking

- **Continuous Validation**:
  - Automated testing through GitHub Actions:
    - Semantic search tests
    - Model validation tests
    - Coverage reporting

- **Automated Scheduling**:
  - Weekly validation runs via Airflow DAG (`model_validation_weekly`)
  - Scheduled for midnight every Sunday
  - Components:
    - Model validation execution
    - Results storage in BigQuery
    - Slack notifications for completion status

- **Performance Monitoring**:
  - Metrics stored in BigQuery table (`Model_Performance_Metrics`):
    - Timestamp tracking
    - Precision metrics
    - Recall metrics
    - F1 scores
    - Sample counts
  - Automated error handling and logging

#### 4. Bias Detection Through Data Slicing
- **Content Analysis**:
  - Implemented in `query_checks/content_checker.py`:
    - Sensitivity detection for topics like religion, gender, race
    - Harmful content detection (terrorism, violence)
    - Modular detection system with fallback patterns
    - Integration with Detoxify model when available

- **Bias Detection Pipeline**:
  - Implemented in `PromptValidation/bias_check.py`:
    - Automated checking of generated SQL queries for potential bias
    - Integration with CI/CD pipeline through GitHub Actions
    - Bias categories monitored:
      - Gender bias
      - Racial bias
      - Age bias

- **Detection Methods**:
  - Primary detection through `PromptValidator` class:
    - Pattern-based detection using regex patterns
    - Bias patterns for gender: `\b(male|female|men|women|gender)\b`
    - Bias patterns for race: `\b(race|ethnic|white|black|asian)\b`
    - Bias patterns for age: `\b(young|old|age|elderly)\b`
  - Secondary detection through Detoxify:
    - Toxicity threshold: > 0.7
    - Identity attack threshold: > 0.5
    - Insult threshold: > 0.5

- **Monitoring and Validation**:
  - Continuous monitoring through `prompt_monitor.py`
  - Automated bias checks in CI/CD pipeline
  - Threshold-based prompt updates when bias detected
  - Integration with GitHub Actions workflow for automated testing

- **Testing Framework**:
  - Comprehensive test suite in `PromptValidation/tests/test_bias_check.py`
  - Mock-based testing for SQL generation
  - Validation against predefined test queries
  - Integration with CI/CD pipeline for automated testing

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
│   ├── promptfilter/
│   │   └── semantic_search.py        # Query relevance checking
│   ├── query_checks/
│   │   └── content_checker.py        # Content analysis and filtering
│   └── monitoring/
│       └── mlflow_config.py          # Experiment tracking
├── Model_validation/
│   ├── model_validation.py           # Core validation logic
│   └── tests/
│       └── test_model_validation.py  # Validation tests
├── PromptValidation/
│   ├── prompt_validator.py           # Template validation
│   ├── bias_check.py                # Bias detection
│   ├── prompt_monitor.py            # Continuous monitoring
│   └── tests/
│       └── test_bias_check.py       # Bias detection tests
├── DataPipeline/
│   └── dags/
│       └── model_validation_dag.py   # Validation workflow
└── hyperparameterTuning/
    └── hyperparametertuner.py       # Parameter optimization
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

### MLflow Experiment Visualization

#### Experiment Overview
![MLflow Overview](/src/assets/Overview.png)
The overview dashboard shows the experiment summary, including total runs, active runs, and experiment metadata. This provides a high-level view of our model's testing and validation progress.

#### Run Details and Metrics
![MLflow Runs UI](/src/assets/mlrunsUI.png)
The runs interface displays individual query executions with their corresponding metrics, parameters, and tags. Each run represents a single query processing instance, allowing us to track performance over time.

#### Model Performance Metrics
![Model Metrics](/src/assets/model_metrics.png)
Detailed performance metrics visualization showing:
- Query execution times
- Success rates across different query types
- Complexity distribution
- Performance trends

#### Artifact Tracking
![Artifact Details](/src/assets/artifact.png)
The artifact view shows detailed logs and query information stored for each run, including:
- Generated SQL queries
- Execution logs
- Error messages (if any)
- Query validation results

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

Our model bias detection framework implements a multi-layered approach to identify and mitigate potential biases in SQL query generation. The system combines pattern-based detection with advanced content analysis to ensure fair and unbiased query processing.

### Primary Detection System
The core bias detection is implemented through the `PromptValidator` class in `PromptValidation/prompt_validator.py`. This system employs regex-based pattern matching to identify potential biases in three key categories:

1. **Gender Bias Detection**
   - Monitors SQL queries for gender-specific terms and conditions
   - Uses pattern matching for terms like "male", "female", "men", "women"
   - Flags queries that might lead to gender-based discrimination in data analysis

2. **Racial Bias Detection**
   - Identifies potentially discriminatory conditions based on race or ethnicity
   - Monitors for terms related to racial or ethnic categorization
   - Ensures fair representation across different demographic groups

3. **Age-Based Bias Detection**
   - Checks for age-related discrimination in queries
   - Monitors terms like "young", "old", "elderly"
   - Prevents unfair filtering or segregation based on age groups

### Secondary Content Analysis
The secondary layer of bias detection is implemented in `query_checks/content_checker.py`, which provides:

1. **Sensitivity Analysis**
   - Detects sensitive topics including religion, gender, and race
   - Implements modular detection patterns for different sensitivity categories
   - Provides fallback patterns for comprehensive coverage

2. **Toxicity Detection**
   - Integration with the Detoxify model for advanced content analysis
   - Threshold-based detection:
     - Toxicity: > 0.7
     - Identity attacks: > 0.5
     - Insults: > 0.5

### Continuous Monitoring and Validation
The bias detection pipeline is integrated into our CI/CD workflow through:

1. **Automated Testing**
   - Continuous monitoring via `prompt_monitor.py`
   - Integration with GitHub Actions for automated checks
   - Comprehensive test suite in `test_bias_check.py`

2. **Validation Process**
   - Each generated SQL query undergoes bias checking
   - Results are logged and tracked for analysis
   - Threshold-based alerts trigger review processes

3. **Reporting and Documentation**
   - Automated generation of bias detection reports
   - Tracking of bias patterns over time
   - Documentation of mitigation strategies and their effectiveness

### Integration Points
The bias detection system is integrated at multiple points in the query generation pipeline:

1. **Pre-Generation Checks**
   - User input validation
   - Context sensitivity analysis
   - Pattern-based screening

2. **Post-Generation Validation**
   - Generated SQL analysis
   - Comprehensive bias detection
   - Performance impact assessment

This multi-layered approach ensures that our SQL generation system maintains high standards of fairness and neutrality while delivering accurate and efficient query results.

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

## Conclusion
This project ensures **efficient model fine-tuning**, **bias detection**, and **CI/CD automation** while leveraging **pre-trained embeddings**. While certain assignment elements (e.g., custom model training and hyperparameter tuning) are not applicable, our implementation focuses on **robust validation, fairness, and deployment automation** in a real-world setting.

