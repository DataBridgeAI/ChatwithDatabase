## Getting Started

### Prerequisites
- Google Cloud Account with billing enabled
- Python 3.10+
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
- OpenAI API key (for AI-powered data processing)

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

### 2. Google Cloud Setup

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
4. Store the JSON key file securely

### 3. Configure API Keys and Environment Variables

Create a `.env` file in the project root with the following variables:
```
GOOGLE_APPLICATION_CREDENTIALS="path/to/your/service-account-key.json"
OPEN_AI_API_KEY="your-openai-api-key"
BUCKET_NAME="your-gcs-bucket-name"
DATASET_NAME="your-bigquery-dataset-name"
PROJECT_ID="your-gcp-project-id"
```

> **IMPORTANT:** Never commit your `.env` file or any files containing API keys to version control!

### 4. GCP Resources Setup

#### Enable Required APIs
Enable the following APIs in Google Cloud Console:
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

### 5. Cloud Composer (Airflow) Configuration

1. Create a Cloud Composer environment through Google Cloud Console
2. Import Airflow variables from the provided environment file:
   - Navigate to Composer → Airflow UI → Admin → Variables → Import Variables
   - Upload the environment file

### 6. Running the Application

Start the Streamlit application:
```bash
streamlit run app.py
```

## Pipeline Reproduction Instructions

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

1. **Authentication Errors**: Verify that your service account has the necessary permissions and the `GOOGLE_APPLICATION_CREDENTIALS` environment variable points to the correct JSON key file.

2. **Missing APIs**: Ensure all required APIs are enabled in your GCP project.

3. **Region Consistency**: Make sure all resources are created in the same or compatible regions.

