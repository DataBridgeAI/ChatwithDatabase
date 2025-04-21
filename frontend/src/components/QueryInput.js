import React, { useState, useEffect, useCallback } from "react";
import { useAppContext } from "../context/AppContext";
import {
  validateQuery,
  findSimilarQuery,
  generateAndExecuteQuery,
  executeSqlQuery,
  getChatHistory,
} from "../api/api";

const QueryInput = () => {
  const {
    userQuery,
    setUserQuery,
    schema,
    projectId,
    datasetId,
    setGeneratedSql,
    setQueryResults,
    resetStates,
    setLoading,
    setError,
    setSimilarQuery,
    setPastSql,
    similarQuery,
    pastSql,
    setWaitingForChoice,
    setQueryExecutionTime,
    currentConversationId,
    setCurrentConversationId,
    setChatHistory,
    showVisualization,
    setShowVisualization
  } = useAppContext();

  const [showSimilarQuery, setShowSimilarQuery] = useState(false);
  const [useSuggested, setUseSuggested] = useState(null);
  const [animateIn, setAnimateIn] = useState(false);
  const [visualizeHovered, setVisualizeHovered] = useState(false);
  const [togglePulse, setTogglePulse] = useState(false);

  // Animation effect when component mounts
  useEffect(() => {
    setAnimateIn(true);
  }, []);

  // Pulse animation when toggle changes
  useEffect(() => {
    setTogglePulse(true);
    const timer = setTimeout(() => {
      setTogglePulse(false);
    }, 1500);
    return () => clearTimeout(timer);
  }, [showVisualization]);

  // Core execution logic from the original component
  const executeNewQuery = useCallback(async () => {
    try {
      const result = await generateAndExecuteQuery(
        userQuery,
        schema,
        projectId,
        datasetId,
        currentConversationId
      );

      if (result.error) {
        setError(result.error);
        if (result.generated_sql) {
          setGeneratedSql(result.generated_sql);
        }
      } else {
        setGeneratedSql(result.generated_sql);
        setQueryResults(result.results);
        setQueryExecutionTime(result.execution_time);
        
        // Update conversation ID if a new one was created
        if (result.conversation_id && !currentConversationId) {
          setCurrentConversationId(result.conversation_id);
          
          // Refresh chat history after query
          try {
            const historyResponse = await getChatHistory();
            if (historyResponse.success) {
              setChatHistory(historyResponse.conversations);
            }
          } catch (historyError) {
            console.error("Failed to refresh chat history:", historyError);
          }
        }
      }
    } catch (error) {
      setError(error.message || "An error occurred during query execution");
    } finally {
      setLoading(false);
    }
  }, [
    userQuery,
    schema,
    projectId,
    datasetId,
    currentConversationId,
    setError,
    setGeneratedSql,
    setQueryResults,
    setQueryExecutionTime,
    setLoading,
    setCurrentConversationId,
    setChatHistory,
  ]);

  // Logic for handling similar query suggestion
  const handleSuggestedQueryChoice = useCallback(async () => {
    if (useSuggested === "yes") {
      setLoading(true);
      setError(null);

      try {
        const result = await executeSqlQuery(pastSql, currentConversationId, userQuery);

        if (result.error) {
          setError(result.error);
        } else {
          setGeneratedSql(pastSql);
          setQueryResults(result.results);
          setQueryExecutionTime(result.execution_time);
          
          // Refresh chat history after query
          try {
            const historyResponse = await getChatHistory();
            if (historyResponse.success) {
              setChatHistory(historyResponse.conversations);
            }
          } catch (historyError) {
            console.error("Failed to refresh chat history:", historyError);
          }
        }
      } catch (error) {
        setError(error.message || "An error occurred during query execution");
      } finally {
        setLoading(false);
        setShowSimilarQuery(false);
        setWaitingForChoice(false);
        setUseSuggested(null);
      }
    } else if (useSuggested === "no") {
      setShowSimilarQuery(false);
      setWaitingForChoice(false);
      executeNewQuery();
      setUseSuggested(null);
    }
  }, [
    useSuggested,
    pastSql,
    currentConversationId,
    userQuery,
    setLoading,
    setError,
    setGeneratedSql,
    setQueryResults,
    setQueryExecutionTime,
    setShowSimilarQuery,
    setWaitingForChoice,
    executeNewQuery,
    setChatHistory,
  ]);

  useEffect(() => {
    if (useSuggested !== null) {
      handleSuggestedQueryChoice();
    }
  }, [useSuggested, handleSuggestedQueryChoice]);

  // Main query generation handler
  const handleGenerateQuery = async () => {
    // Reset all states to ensure a fresh start
    resetStates();
    
    // Clear any current conversation context
    setCurrentConversationId(null);
    
    // Reset suggestion states
    setShowSimilarQuery(false);
    setUseSuggested(null);
    
    setLoading(true);
    setError(null);

    if (!schema) {
      setError("Please load the BigQuery schema first!");
      setLoading(false);
      return;
    }

    try {
      // Validate the query
      const validationResult = await validateQuery(userQuery);
      if (validationResult.error) {
        setError(validationResult.error);
        setLoading(false);
        return;
      }

      // Always check for similar query first
      const similarResult = await findSimilarQuery(userQuery);
      if (similarResult.found) {
        setSimilarQuery(similarResult.similar_query);
        setPastSql(similarResult.past_sql);
        setWaitingForChoice(true);
        setShowSimilarQuery(true);
        setLoading(false);
        return;
      } else {
        // No similar query found, generate a new query
        setLoading(false);
        executeNewQuery();
      }
    } catch (error) {
      setError(error.message || "An error occurred");
      setLoading(false);
    }
  };

  const handleVisualizationToggle = () => {
    setShowVisualization(!showVisualization);
  };

  return (
    <div className={`transition-all duration-700 transform ${
      animateIn ? 'translate-y-0 opacity-100' : 'translate-y-12 opacity-0'
    }`}>
      <div className="glass p-6 rounded-xl shadow-lg border border-blue-500/20">
        <div className="flex items-center mb-4 text-blue-300">
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
          <h2 className="text-lg font-semibold bg-gradient-to-r from-blue-300 to-purple-300 bg-clip-text text-transparent">Chat with Your Data</h2>
        </div>
        
        <div className="relative">
          <textarea
            value={userQuery}
            onChange={(e) => setUserQuery(e.target.value)}
            className="glass-input w-full p-4 pl-10 pr-32 rounded-xl min-h-20 focus:outline-none shadow-lg resize-y text-blue-200"
            placeholder="Enter your question"
            onKeyDown={(e) => {
              if (e.key === 'Enter' && e.ctrlKey) {
                handleGenerateQuery();
              }
            }}
          />
          <div className="absolute left-3 top-3.5 text-blue-300">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>

          {/* Fixed Visualization Toggle */}
          <div 
            className={`absolute right-3 top-3 ${visualizeHovered ? 'opacity-100' : 'opacity-90'} transition-opacity`} 
            onMouseEnter={() => setVisualizeHovered(true)}
            onMouseLeave={() => setVisualizeHovered(false)}
          >
            <div className="viz-toggle-container flex items-center p-1 rounded-full backdrop-blur-sm transition-all">
              <button
                onClick={handleVisualizationToggle}
                className="relative flex items-center h-7 transition-all duration-300 overflow-hidden"
                aria-label={showVisualization ? "Turn off visualizations" : "Turn on visualizations"}
              >
                <div className="viz-toggle-slider flex items-center justify-between w-20 p-1 py-1 transition-transform duration-300 ease-in-out">
                  <div className={`viz-toggle-pill absolute h-5 w-9 rounded-full transition-transform duration-300 ${
                    showVisualization ? 'translate-x-10 active' : 'translate-x-0'
                  } ${togglePulse ? 'animate-pulse' : ''}`}></div>
                  
                  <span className={`viz-toggle-text text-xs font-medium px-1 transition-colors duration-300 ${
                    !showVisualization ? 'text-blue-200' : 'text-blue-400'
                  } z-10`}>Off</span>
                  <span className={`viz-toggle-text text-xs font-medium px-1 transition-colors duration-300 ${
                    showVisualization ? 'text-blue-200' : 'text-blue-400'
                  } z-10`}>On</span>
                </div>
              </button>
              
              <div className={`flex items-center ml-2 ${visualizeHovered ? 'opacity-100' : 'opacity-80'} transition-opacity`}>
                <svg className="w-4 h-4 text-blue-300 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                <span className="text-sm text-blue-300 font-medium">Visualize</span>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-4">
          <button
            className="w-full glass-button bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white py-3 px-6 rounded-lg disabled:opacity-50 flex items-center justify-center shadow-lg transition-all"
            onClick={handleGenerateQuery}
            disabled={!schema || showSimilarQuery || !userQuery.trim()}
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            Generate Query
          </button>
          
          <div className="text-center mt-2 text-xs text-blue-400">
            Press Ctrl+Enter to generate query
          </div>
        </div>
      </div>

      {/* Similar query suggestion modal */}
      {showSimilarQuery && (
        <div className="fixed inset-0 bg-blue-900/50 backdrop-blur-md flex items-center justify-center z-50">
          <div className="glass p-8 max-w-2xl w-full shadow-2xl slide-up border border-blue-400/30 rounded-xl">
            <div className="flex items-center mb-4 text-blue-300">
              <svg className="w-6 h-6 mr-2 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
              <h3 className="text-xl font-semibold bg-gradient-to-r from-blue-300 to-purple-300 bg-clip-text text-transparent">Similar Query Found</h3>
            </div>

            <div className="glass-light p-4 rounded-lg mb-4 text-blue-200">
              <p className="mb-1 text-sm text-blue-400">Previous Question:</p>
              <p className="italic">{similarQuery}</p>
            </div>

            <div>
              <h3 className="flex items-center text-blue-300 mb-2">
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                </svg>
                Suggested SQL:
              </h3>
              <pre className="glass-dark rounded-xl p-4 my-2 overflow-x-auto text-sm text-blue-200 border border-blue-500/20">
                <code>{pastSql}</code>
              </pre>
            </div>

            <div className="mt-6">
              <p className="mb-3 text-blue-300 flex items-center">
                <svg className="w-5 h-5 mr-2 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Would you like to use the suggested SQL query?
              </p>
              <div className="flex space-x-4">
                <button
                  className="flex-1 glass-button bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white py-3 px-4 rounded-lg shadow-lg transition-all flex items-center justify-center"
                  onClick={() => setUseSuggested("yes")}
                >
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Yes, Use This
                </button>
                <button
                  className="flex-1 glass-button border border-blue-400/30 text-blue-300 py-3 px-4 rounded-lg shadow-lg hover:bg-blue-500/10 transition-all flex items-center justify-center"
                  onClick={() => setUseSuggested("no")}
                >
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v3m0 0v3m0-3h3m-3 0H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  No, Generate New
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default QueryInput;