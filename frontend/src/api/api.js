// API service for BigQuery Analytics
const API_BASE_URL = "http://localhost:5001/api";

// Store credentials in memory for the session
let credentials = {
  openai_api_key: null,
  google_credentials: null,
};

// Set credentials in memory
export const setCredentials = (openaiApiKey, googleCredentials) => {
  if (openaiApiKey) credentials.openai_api_key = openaiApiKey;
  if (googleCredentials) credentials.google_credentials = googleCredentials;
};

// Add this function alongside your other API functions
export const setCredentialsPath = async (credentialsPath) => {
  try {
    const response = await fetch(`${API_BASE_URL}/set-credentials-path`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        credentials_path: credentialsPath
      }),
    });

    return await response.json();
  } catch (error) {
    console.error("Error setting credentials path:", error);
    throw error;
  }
};

// Send credentials to the backend
export const sendCredentials = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/credentials`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        openai_api_key: credentials.openai_api_key,
        google_credentials: credentials.google_credentials,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || "Failed to set credentials");
    }

    return await response.json();
  } catch (error) {
    console.error("Error setting credentials:", error);
    throw error;
  }
};

export const fetchSchema = async (projectId, datasetId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/schema`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        project_id: projectId,
        dataset_id: datasetId,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || "Failed to fetch schema");
    }

    return await response.json();
  } catch (error) {
    console.error("Error fetching schema:", error);
    throw error;
  }
};

export const validateQuery = async (query) => {
  try {
    const response = await fetch(`${API_BASE_URL}/query/validate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        query,
      }),
    });

    return await response.json();
  } catch (error) {
    console.error("Error validating query:", error);
    throw error;
  }
};

export const findSimilarQuery = async (query) => {
  try {
    const response = await fetch(`${API_BASE_URL}/query/similar`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        query,
      }),
    });

    return await response.json();
  } catch (error) {
    console.error("Error finding similar query:", error);
    throw error;
  }
};

export const generateAndExecuteQuery = async (
  query,
  schema,
  projectId,
  datasetId
) => {
  try {
    const response = await fetch(`${API_BASE_URL}/query/generate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        query,
        schema,
        project_id: projectId,
        dataset_id: datasetId,
      }),
    });

    return await response.json();
  } catch (error) {
    console.error("Error generating and executing query:", error);
    throw error;
  }
};

export const executeSqlQuery = async (sql) => {
  try {
    const response = await fetch(`${API_BASE_URL}/query/execute`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        sql,
      }),
    });

    return await response.json();
  } catch (error) {
    console.error("Error executing SQL query:", error);
    throw error;
  }
};

export const submitFeedback = async (
  query,
  sql,
  feedback,
  executionSuccess
) => {
  try {
    const response = await fetch(`${API_BASE_URL}/feedback`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        query,
        sql,
        feedback,
        execution_success: executionSuccess,
      }),
    });

    return await response.json();
  } catch (error) {
    console.error("Error submitting feedback:", error);
    throw error;
  }
};

export const checkHealth = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    return await response.json();
  } catch (error) {
    console.error("Error checking API health:", error);
    throw error;
  }
};