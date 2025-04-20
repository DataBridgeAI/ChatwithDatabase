# BigQuery Analytics Dashboard

This application provides a user-friendly interface to interact with BigQuery data using natural language queries that are translated into SQL.

## Project Structure

The project is organized into two main parts:

1. **Backend**: A Flask API that handles database connections, query generation, and execution
2. **Frontend**: A React application that provides the user interface

## Requirements

- Python 3.8+
- Node.js 16+
- Google Cloud Platform account with BigQuery access

## Setup

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows: `venv\Scripts\activate`
   - On macOS/Linux: `source venv/bin/activate`

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Set up Google Cloud credentials:
   ```
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/credentials.json"
   ```

6. Run the Flask server:
   ```
   python app.py
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm start
   ```

4. The application will be available at `http://localhost:3000`

## Usage

1. Enter your BigQuery project ID and dataset ID in the sidebar
2. Click "Load Schema" to fetch the database schema
3. Type a natural language query in the text area
4. Click "Generate & Execute Query" to process your request
5. View the results in the table
6. Optionally, provide feedback and visualize the data

## Features

- Natural language to SQL conversion
- Schema visualization
- SQL query generation
- Query execution and results display
- Similar query suggestions
- Interactive data visualization
- User feedback collection
- Query execution metrics

## Troubleshooting

- If you encounter CORS issues, ensure that the Flask backend is running and CORS is properly configured
- Check that your Google Cloud credentials are properly set up and have access to the specified project and dataset
- For visualization issues, ensure that the data types in your query results match the expected types for the selected chart

## License

This project is licensed under the MIT License - see the LICENSE file for details.