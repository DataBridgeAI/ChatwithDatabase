import React, { createContext, useState, useContext } from 'react';

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
  const [userQuery, setUserQuery] = useState('Show top 10 artists based on popularity');
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
    
    // Helpers
    resetStates
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};