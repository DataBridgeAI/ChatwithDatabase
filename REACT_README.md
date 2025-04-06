# Running the React Frontend with Credentials

This guide explains how to run the React frontend with OpenAI API key and Google credentials provided via the terminal.

## Prerequisites

- Node.js installed
- Python installed
- OpenAI API key
- Google Cloud credentials JSON file

## Running the React App

You can run the React frontend with credentials using the provided script:

```bash
./start-react.js --openai-key YOUR_OPENAI_API_KEY --google-credentials path/to/your/google-credentials.json
```

### Options

- `--openai-key`: Your OpenAI API key
- `--google-credentials`: Path to your Google credentials JSON file

If you don't provide these options, the script will prompt you for the OpenAI API key.

## How It Works

The script:

1. Starts the backend server if it's not already running
2. Sends your credentials to the backend
3. Starts the React frontend

## Troubleshooting

If you encounter the "Failed to fetch" error when loading schema:

1. Make sure the backend server is running on port 5001
2. Check that your credentials are valid
3. Verify that your Google credentials have access to BigQuery

## Manual Setup

If you prefer to set up manually:

1. Start the backend server:
   ```bash
   python src/app.py
   ```

2. In another terminal, send your credentials to the backend:
   ```bash
   curl -X POST http://localhost:5001/api/credentials \
     -H "Content-Type: application/json" \
     -d '{"openai_api_key": "YOUR_OPENAI_API_KEY", "google_credentials": CONTENTS_OF_YOUR_GOOGLE_CREDENTIALS_JSON}'
   ```

3. Start the React frontend:
   ```bash
   cd frontend
   npm start
   ```
