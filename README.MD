# Getting Started

## Setup Virtual Environment
1. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
2. Activate the virtual environment:
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

## Install Dependencies
3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Authenticate & Configure Google Cloud
4. Follow these steps to set up Google Cloud authentication and configuration:
   a. Install the [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
   b. Authenticate with Google Cloud:
      ```bash
      gcloud auth application-default login
      ```
   c. Set the project ID:
      ```bash
      gcloud config set project PROJECT_ID
      ```
   d. Verify authentication:
      ```bash
      gcloud auth list
      ```
   e. Verify project configuration:
      ```bash
      gcloud config list
      ```
      **Steps d & e are important to ensure the correct account and project are set.**
   
   f. Set up environment variables:
      ```bash
      export GOOGLE_APPLICATION_CREDENTIALS="path_to_service_account_json"
      export OPEN_AI_API_KEY="api_key"
      ```

## Running the Application
5. Start the application:
   ```bash
   streamlit run app.py
   ```
