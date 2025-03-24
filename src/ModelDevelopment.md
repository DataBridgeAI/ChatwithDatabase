# README: Machine Learning Model Development and CI/CD Pipeline

## Overview
This project focuses on integrating Machine Learning (ML) model development within a Continuous Integration/Continuous Deployment (CI/CD) pipeline. It incorporates best practices in model validation, bias detection, sensitivity analysis, and experiment tracking to ensure robustness, fairness, and reproducibility.

## Scope of Implementation
Our project does **not** include training a completely new ML model from scratch. Instead, we focus on **fine-tuning a pre-trained model** and ensuring its effective deployment. Consequently, some aspects of the provided assignment guidelines, such as **extensive hyperparameter tuning** or **custom model training**, are not fully applicable. Below, we provide a breakdown of our implementation decisions and deviations.

---

## 1. Model Development and ML Code
### Implemented:
- **Loading Data from Data Pipeline**: We retrieve structured data from our pre-built data pipeline which connects to BigQuery,  ensuring consistency and proper version control. This pipeline dynamically fetches and formats BigQuery schema information and provides table structure for prompt engineering and validation
- **Fine-tuning a Pre-trained Model**: GPT-4 was used through Langchain integration to fine-tune GPT-4 LLM for better efficiency and performance. We have fine-tuned the pre-trained model by:- <br>
- Custom prompt templates for SQL generation
  - Schema-aware query generation with context
  -
- **Model Validation**: We implement **performance metrics** (e.g., accuracy, precision, recall) using test datasets to evaluate the model.
- **Model Bias Detection**: Our pipeline includes **data slicing** techniques to detect performance variations across different subgroups.
- **Artifact Storage**: We store the validated model in **Google Cloud Artifact Registry**, ensuring versioning and future retraining capabilities.

### Not Applicable:
- **Training a New Model from Scratch**: Since we use **GPT-4 embeddings**, full-fledged model training is unnecessary.
- **Extensive Hyperparameter Tuning**: Our approach does not require grid search or Bayesian optimization since we rely on a pre-trained model.

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

