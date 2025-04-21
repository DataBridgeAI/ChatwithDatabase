// API service for BigQuery Analytics
const API_BASE_URL = window._env_?.REACT_APP_API_URL || 'http://34.10.210.167/api';

if (!API_BASE_URL) {
  throw new Error('API URL is not configured');
}

export { API_BASE_URL };


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
      throw new Error(error.error || "I couldn't connect to your dataset. Please check your credentials and try again.");
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
    throw new Error("I'm having trouble understanding your question. Could you try phrasing it differently?");
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
    throw new Error("I encountered an issue while checking for similar questions you've asked before.");
  }
};

export const generateAndExecuteQuery = async (
  query,
  schema,
  projectId,
  datasetId,
  conversationId = null
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
        conversation_id: conversationId,
      }),
    });

    return await response.json();
  } catch (error) {
    console.error("Error generating and executing query:", error);
    throw new Error("I'm having trouble processing your question right now. Let's try a different approach.");
  }
};

export const executeSqlQuery = async (sql, conversationId = null, userQuery = null) => {
  try {
    const response = await fetch(`${API_BASE_URL}/query/execute`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        sql,
        conversation_id: conversationId,
        user_query: userQuery
      }),
    });

    return await response.json();
  } catch (error) {
    console.error("Error executing SQL query:", error);
    throw new Error("I wasn't able to run that SQL query. There might be an issue with the syntax or the data.");
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
    throw new Error("I couldn't save your feedback. Please try again in a moment.");
  }
};

export const getChatHistory = async (userId = null, limit = 5) => {
  try {
    const url = new URL(`${API_BASE_URL}/chat/history`);
    if (userId) url.searchParams.append('user_id', userId);
    url.searchParams.append('limit', limit);
    
    const response = await fetch(url);
    const data = await response.json();
    
    // Even if there's a 500 error, we still get JSON back with success: false
    return {
      success: data.success || false,
      conversations: data.conversations || [],
      error: data.error
    };
  } catch (error) {
    console.error("Error fetching chat history:", error);
    // Return a sensible default
    return {
      success: false,
      conversations: [],
      error: "I couldn't retrieve your chat history right now. Please try again later."
    };
  }
};

export const getConversation = async (conversationId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/chat/conversation/${conversationId}`);
    const data = await response.json();
    
    return {
      success: data.success || false,
      details: data.details || {},
      messages: data.messages || [],
      error: data.error
    };
  } catch (error) {
    console.error("Error fetching conversation:", error);
    return {
      success: false,
      details: {},
      messages: [],
      error: "I couldn't load that conversation right now. The server might be temporarily unavailable."
    };
  }
};

export const checkHealth = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    return await response.json();
  } catch (error) {
    console.error("Error checking API health:", error);
    throw new Error("I'm having trouble connecting to the server. Please check your connection and try again.");
  }
};