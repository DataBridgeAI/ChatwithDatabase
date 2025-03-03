## Getting Started

### Prerequisites
- OpenAI API Key
- Google Cloud Account with billing enabled (if using GCP resources like BigQuery or Cloud Composer)
- Python 3.10+
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) (for GCP-related resources)
- MySQL database

## Setup Instructions

### 1. Environment Setup

#### Create a Virtual Environment
```bash
python -m venv venv
```

#### Activate the Virtual Environment
- On macOS/Linux:
  ```bash
  source venv/bin/activate
  ```
- On Windows:
  ```bash
  venv\Scripts\activate
  ```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. API Keys and Configuration

#### Required API Keys
1. Create a `.env` file in the project root with the following variables:
   ```
   OPENAI_API_KEY="your-openai-api-key"
   GOOGLE_APPLICATION_CREDENTIALS="path/to/your/service-account-key.json"
   ```

2. For OpenAI API:
   - Visit the [OpenAI API Key Page](https://platform.openai.com/account/api-keys)
   - Create an API key and add it to your `.env` file as `OPENAI_API_KEY`

> **IMPORTANT:** Never commit your `.env` file or any files containing API keys to version control!

### 3. Database Setup

1. Ensure you have a MySQL database with manufacturing data.
2. The application expects the following database structure:
   - Tables for customers, orders, products, and other manufacturing entities.
   - Proper foreign key relationships between tables.
3. You can configure the database connection in the application's sidebar:
   - Host (default: localhost)
   - User (default: root)
   - Password
   - Database name (default: manufacturing)

### 4. Google Cloud Setup (for Production/Cloud Deployment)

#### Authentication and Configuration
1. Install the [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
2. Authenticate with Google Cloud:
   ```bash
   gcloud auth application-default login
   ```
3. Set your project ID:
   ```bash
   gcloud config set project YOUR_PROJECT_ID
   ```
4. Verify authentication:
   ```bash
   gcloud auth list
   ```
5. Verify project configuration:
   ```bash
   gcloud config list
   ```

#### Create Service Account Credentials
1. In the Google Cloud Console, navigate to IAM & Admin > Service Accounts
2. Create a new service account with the following roles:
   - BigQuery Admin
   - Storage Admin
   - Vertex AI User
3. Create and download a JSON key for this service account
4. Store the JSON key file securely and reference it in your `.env` file

### 5. Running the Application

Start the Streamlit application:
```bash
streamlit run app.py
```

## Application Features

### Natural Language Queries
- Transform English questions into SQL queries using OpenAI's GPT model
- Example: "Show customer IDs and addresses for customers who ordered product ID 50"

### Data Visualization
The dashboard supports various visualization types:
- Bar charts
- Line charts
- Pie charts
- Sunburst diagrams
- Scatter plots
- Histograms
- Data summaries

### Feedback and Improvement
- Provide feedback on query results (👍 or 👎)
- Automatic query correction based on negative feedback
- Continuous improvement through Retrieval-Augmented Generation (RAG)

### Safety Features
- Input validation to prevent harmful or inappropriate queries
- SQL safety checks to prevent destructive operations
- Context-relevant query filtering

## ChromaDB Feedback Storage
The application uses ChromaDB to store and retrieve feedback:
- Feedback is stored in a local persistent database (`./feedback_db`)
- Historical feedback improves future query generation
- Relevant examples are retrieved using semantic search

## GCP Pipeline Reproduction Instructions

To reproduce this data pipeline on a different GCP environment:

### Step 1: Set Up GCP Services and Resources

#### Enable Required APIs
- BigQuery API
- Cloud Composer API
- Vertex AI API

#### Create Cloud Storage Bucket
```bash
export BUCKET_NAME=your-bucket-name
gcloud storage buckets create gs://$BUCKET_NAME --project YOUR_PROJECT_ID --location=REGION
gsutil mkdir gs://$BUCKET_NAME/data
```

#### Create BigQuery Dataset
```bash
export DATASET_NAME=your-dataset-name
bq --location=REGION mk --dataset YOUR_PROJECT_ID:$DATASET_NAME
```

### Step 2: Configure Airflow with Cloud Composer

1. Create a Cloud Composer environment in the same region as other resources
2. Update GitHub workflows to match your GCP environment (Project, Bucket, etc.)
3. Configure environment variables in Composer:
   - Import variables from the provided environment file through the Airflow UI
4. Install Python package dependencies from `requirements.txt`

### Step 3: CI/CD Pipeline with GitHub Actions

1. Configure GitHub repository secrets for GCP authentication
2. Use the provided workflow files:
   - `gcp-upload.yaml`: Handles uploading code to GCS
   - `python-tests.yaml`: Handles unit testing and linting

### Step 4: Testing and Monitoring

1. Trigger pipeline execution through the Composer/Airflow UI
2. Verify data processing in BigQuery
3. Monitor logs in the Composer environment
4. Configure email alerts by updating the environment variable in Composer

## Troubleshooting

### Common Issues

1. **OpenAI API Key Not Found**: Verify that your `.env` file contains a valid `OPENAI_API_KEY`.

2. **Database Connection Errors**: Check database credentials and ensure the MySQL server is running.

3. **ChromaDB Errors**: Make sure the application has write permissions to create the `./feedback_db` directory.

4. **Visualization Errors**: Ensure that the selected columns for visualization are appropriate for the chart type.

5. **Authentication Errors**: Verify that your service account has the necessary permissions and the `GOOGLE_APPLICATION_CREDENTIALS` environment variable points to the correct JSON key file.

6. **Missing APIs**: Ensure all required APIs are enabled in your GCP project.

7. **Region Consistency**: Make sure all resources are created in the same or compatible regions.

## Required Dependencies

The application requires the following Python packages:
- streamlit
- mysql-connector-python
- pandas
- plotly
- openai
- langchain
- python-dotenv
- chromadb
- sentence-transformers
- uuid
