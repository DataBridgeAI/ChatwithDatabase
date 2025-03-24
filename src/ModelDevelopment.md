# README: Machine Learning Model Development and CI/CD Pipeline

## Overview
This project focuses on integrating Machine Learning (ML) model development within a Continuous Integration/Continuous Deployment (CI/CD) pipeline. It incorporates best practices in model validation, bias detection, sensitivity analysis, and experiment tracking to ensure robustness, fairness, and reproducibility.

## Scope of Implementation
Our project does **not** include training a completely new ML model from scratch. Instead, we focus on **fine-tuning a pre-trained model** and ensuring its effective deployment. Consequently, some aspects of the provided assignment guidelines, such as **extensive hyperparameter tuning** or **custom model training**, are not fully applicable. Below, we provide a breakdown of our implementation decisions and deviations.

---

## 1. Model Development and ML Code

### Implemented Components:

#### 1. Loading Data from Data Pipeline
- **BigQuery Integration**: 
  - Structured data retrieval through `database/query_executor.py`
  - Dynamic schema fetching and formatting via `database/schema.py`
  - Versioned data access ensuring consistency across model iterations
- **Schema Processing**:
  - Schema embeddings generation using Vertex AI's `textembedding-gecko@003`
  - Storage and retrieval through ChromaDB for efficient access
  - Schema-aware context management for query generation

#### 2. Model Selection and Fine-tuning
- **Base Model**: 
  - GPT-4 integration through LangChain framework
  - Configured for SQL generation with schema awareness
- **Fine-tuning Implementation**:
  - Custom prompt templates for SQL generation
  - Schema-aware query generation with context
  - Feedback incorporation through vector similarity search
- **Selection Process**:
  - Performance tracking via MLflow (`monitoring/mlflow_config.py`)
  - Automated validation through Cloud Composer DAGs
  - Continuous performance monitoring and logging

#### 3. Model Validation Process
- **Performance Metrics**:
  - Implementation in `Model_validation/model_validation.py`
  - Metrics include:
    - Query execution success rate
    - Precision, recall, and F1-score
    - Execution time and efficiency metrics
- **Validation Pipeline**:
  - Weekly automated validation through Cloud Composer DAG
  - Results storage in BigQuery for trend analysis
  - Automated notifications through Slack integration

#### 4. Bias Detection Through Data Slicing
- **Data Slicing Implementation**:
  - Query performance analysis across:
    - Query complexity levels
    - Different data domains
    - Usage patterns and contexts
- **Tools Used**:
  - Custom bias detection in `PromptValidation/prompt_monitor.py`
  - Integration with semantic search for relevance checking
  - Performance variation analysis across data segments

#### 5. Bias Checking and Reporting
- **Automated Checks**:
  - Continuous monitoring through CI/CD pipeline
  - Integration with GitHub Actions for validation
  - Real-time bias detection and alerting
- **Reporting System**:
  - MLflow tracking for bias metrics
  - BigQuery storage for historical analysis
  - Slack notifications for threshold violations
- **Mitigation Approach**:
  - Prompt template refinement
  - Context enhancement for biased scenarios
  - Continuous feedback incorporation

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
### Not Applicable:
- Since we use a **pre-trained model**, we do not perform hyperparameter tuning using techniques like **random search or grid search**.
- However, we ensure that **prompt engineering and feature selection** are optimized for best results.

---

## 3. Experiment Tracking and Results
### Implemented:
- **Tracking with MLflow**: We log **model versions, parameters, and results** for reproducibility.
- **Visualization of Results**: We generate confusion matrices and performance metric plots for comparison.

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
### Implemented:
- **Automated Model Training & Validation**:
  - Our **GitHub Actions workflow** triggers model validation on new code commits.
  - Runs **unit tests** to ensure functionality.
- **Automated Bias Detection**:
  - Model fairness checks are included in the pipeline.
  - Alerts are sent if bias exceeds a threshold.
- **Artifact Storage & Deployment**:
  - Validated models are **automatically pushed to Google Cloud Artifact Registry**.
  - Deployed to **Cloud Composer (Airflow DAGs)** for orchestration.
- **Notifications & Rollbacks**:
  - Alerts notify developers of failures.
  - If a model performs worse than a previous version, it is **automatically rolled back**.

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

