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
        // Important: Reset useSuggested to null so it can be triggered again
        setUseSuggested(null);
      }
    } else if (useSuggested === "no") {
      // If user selects no, we need to continue with generating a new query
      setShowSimilarQuery(false);
      setWaitingForChoice(false);
      // Generate and execute a new query
      executeNewQuery();
      // Important: Reset useSuggested to null after handling
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
        // No similar query found, generate a new query but don't execute it immediately
        // Instead, we'll store it and execute only when user confirms
        setLoading(false);
        executeNewQuery();
      }
    } catch (error) {
      setError(error.message || "An error occurred");
      setLoading(false);
    }
  };

  const handleVisualizationToggle = (choice) => {
    setShowVisualization(choice === 'yes');
  };

  return (
    <div className="mb-6">
      <label className="block text-lg font-medium mb-2 text-[#202124]">
        Enter your question:
      </label>
      <textarea
        value={userQuery}
        onChange={(e) => setUserQuery(e.target.value)}
        className="w-full p-3 border border-[#dadce0] rounded-lg min-h-20 mb-4 focus:outline-none focus:ring-2 focus:ring-[#1a73e8] focus:border-transparent"
        placeholder="e.g., Show top 10 artists based on popularity"
      />

      <div className="flex items-center space-x-6">
        <button
          className="bg-[#1a73e8] text-white py-2 px-6 rounded-lg hover:bg-[#174ea6] disabled:bg-[#dadce0] flex items-center shadow-sm transition-colors"
          onClick={handleGenerateQuery}
          disabled={!schema || showSimilarQuery}
        >
          Generate Query
        </button>
        
        <div className="flex items-center">
          <span className="mr-3 text-[#202124]">Would you like to see visualizations?</span>
          <div className="flex space-x-2">
            <button
              className={`px-3 py-1 rounded transition-colors ${
                showVisualization 
                  ? 'bg-[#34a853] text-white' 
                  : 'bg-[#f8f9fa] text-[#5f6368] border border-[#dadce0]'
              }`}
              onClick={() => handleVisualizationToggle('yes')}
            >
              Yes
            </button>
            <button
              className={`px-3 py-1 rounded transition-colors ${
                !showVisualization 
                  ? 'bg-[#d93025] text-white' 
                  : 'bg-[#f8f9fa] text-[#5f6368] border border-[#dadce0]'
              }`}
              onClick={() => handleVisualizationToggle('no')}
            >
              No
            </button>
          </div>
        </div>
      </div>

      {showSimilarQuery && (
        <div className="mt-4 p-4 bg-[#e8f0fe] rounded-lg border border-[#dadce0]">
          <h3 className="font-medium text-[#1a73e8]">Similar query found:</h3>
          <p className="my-2 text-[#202124]">{similarQuery}</p>
          <h3 className="font-medium mt-3 text-[#1a73e8]">Suggested SQL:</h3>
          <pre className="bg-white p-2 rounded my-2 overflow-x-auto text-sm border border-[#dadce0] text-[#5f6368]">
            <code>{pastSql}</code>
          </pre>

          <div className="mt-4">
            <p className="mb-2 text-[#202124]">
              Would you like to use the suggested SQL query instead of
              generating a new one?
            </p>
            <div className="flex space-x-4">
              <button
                className="bg-[#34a853] text-white py-1 px-4 rounded hover:bg-[#2d9149] shadow-sm transition-colors"
                onClick={() => setUseSuggested("yes")}
              >
                Yes
              </button>
              <button
                className="bg-[#d93025] text-white py-1 px-4 rounded hover:bg-[#c62b21] shadow-sm transition-colors"
                onClick={() => setUseSuggested("no")}
              >
                No
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default QueryInput;