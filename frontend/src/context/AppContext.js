import React, { createContext, useState, useContext, useEffect } from 'react';
import { getChatHistory } from '../api/api';

const AppContext = createContext();

export const useAppContext = () => useContext(AppContext);

export const AppProvider = ({ children }) => {
  // Application state
  const [isSchemaLoaded, setIsSchemaLoaded] = useState(false);
  
  // Configuration state
  const [projectId, setProjectId] = useState('');
  const [datasetId, setDatasetId] = useState('');
  const [schema, setSchema] = useState(null);
  
  // Query state
  const [userQuery, setUserQuery] = useState('');  // Set to empty string instead of default question
  const [generatedSql, setGeneratedSql] = useState('');
  const [queryResults, setQueryResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Visualization state
  const [showVisualization, setShowVisualization] = useState(false);
  
  // Suggested query state
  const [similarQuery, setSimilarQuery] = useState(null);
  const [pastSql, setPastSql] = useState(null);
  const [showingSuggestion, setShowingSuggestion] = useState(false);
  const [waitingForChoice, setWaitingForChoice] = useState(false);
  
  // Feedback state
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);
  
  // Execution timing
  const [queryExecutionTime, setQueryExecutionTime] = useState(0);
  
  // Chat history state
  const [chatHistory, setChatHistory] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [currentConversationId, setCurrentConversationId] = useState(null);
  
  // Fetch chat history on component mount
  useEffect(() => {
    const fetchChatHistory = async () => {
      if (isSchemaLoaded) {
        setLoadingHistory(true);
        try {
          const response = await getChatHistory();
          if (response.success) {
            setChatHistory(response.conversations);
          }
        } catch (error) {
          console.error("Failed to fetch chat history:", error);
        } finally {
          setLoadingHistory(false);
        }
      }
    };
    
    fetchChatHistory();
  }, [isSchemaLoaded]);
  
  const resetStates = () => {
    setQueryResults(null);
    setGeneratedSql('');
    setFeedbackSubmitted(false);
    setShowVisualization(false);
    setSimilarQuery(null);
    setPastSql(null);
    setShowingSuggestion(false);
    setWaitingForChoice(false);
    setError(null);
  };

  const value = {
    // Application state
    isSchemaLoaded, setIsSchemaLoaded,
    
    // Configuration
    projectId, setProjectId,
    datasetId, setDatasetId,
    schema, setSchema,
    
    // Query
    userQuery, setUserQuery,
    generatedSql, setGeneratedSql,
    queryResults, setQueryResults,
    loading, setLoading,
    error, setError,
    
    // Visualization
    showVisualization, setShowVisualization,
    
    // Suggested query
    similarQuery, setSimilarQuery,
    pastSql, setPastSql,
    showingSuggestion, setShowingSuggestion,
    waitingForChoice, setWaitingForChoice,
    
    // Feedback
    feedbackSubmitted, setFeedbackSubmitted,
    
    // Timing
    queryExecutionTime, setQueryExecutionTime,
    
    // Chat history
    chatHistory, setChatHistory,
    loadingHistory, setLoadingHistory,
    currentConversationId, setCurrentConversationId,
    
    // Helpers
    resetStates
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};