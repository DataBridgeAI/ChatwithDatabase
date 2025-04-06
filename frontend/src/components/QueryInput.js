import React, { useState, useEffect, useCallback } from "react";
import { useAppContext } from "../context/AppContext";
import {
  validateQuery,
  findSimilarQuery,
  generateAndExecuteQuery,
  executeSqlQuery,
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
  } = useAppContext();

  const [, setStartTime] = useState(null);
  const [showSimilarQuery, setShowSimilarQuery] = useState(false);
  const [useSuggested, setUseSuggested] = useState(null);

  const executeNewQuery = useCallback(async () => {
    try {
      const result = await generateAndExecuteQuery(
        userQuery,
        schema,
        projectId,
        datasetId
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
      }
    } catch (error) {
      setError(error.message || "An error occurred during query execution");
    } finally {
      setLoading(false);
    }
  }, [userQuery, schema, projectId, datasetId, setError, setGeneratedSql, setQueryResults, setQueryExecutionTime, setLoading]);

  const handleSuggestedQueryChoice = useCallback(async () => {
    if (useSuggested === "yes") {
      setLoading(true);
      setError(null);

      try {
        const result = await executeSqlQuery(pastSql);

        if (result.error) {
          setError(result.error);
        } else {
          setGeneratedSql(pastSql);
          setQueryResults(result.results);
          setQueryExecutionTime(result.execution_time);
        }
      } catch (error) {
        setError(error.message || "An error occurred during query execution");
      } finally {
        setLoading(false);
        setShowSimilarQuery(false);
        setWaitingForChoice(false);
      }
    } else if (useSuggested === "no") {
      setShowSimilarQuery(false);
      setWaitingForChoice(false);
      executeNewQuery();
    }
  }, [
    useSuggested,
    pastSql,
    setLoading,
    setError,
    setGeneratedSql,
    setQueryResults,
    setQueryExecutionTime,
    setShowSimilarQuery,
    setWaitingForChoice,
    executeNewQuery,
  ]);

  useEffect(() => {
    if (useSuggested !== null) {
      handleSuggestedQueryChoice();
    }
  }, [useSuggested, handleSuggestedQueryChoice]);

  const handleGenerateQuery = async () => {
    resetStates();
    setStartTime(Date.now());
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

      // Look for similar query
      const similarResult = await findSimilarQuery(userQuery);
      if (similarResult.found) {
        setSimilarQuery(similarResult.similar_query);
        setPastSql(similarResult.past_sql);
        setWaitingForChoice(true);
        setShowSimilarQuery(true);
        setLoading(false);
        return;
      }

      // Generate and execute query
      await executeNewQuery();
    } catch (error) {
      setError(error.message || "An error occurred");
      setLoading(false);
    }
  };

  return (
    <div className="mb-6">
      <label className="block text-lg font-medium mb-2">
        Enter your question:
      </label>
      <textarea
        value={userQuery}
        onChange={(e) => setUserQuery(e.target.value)}
        className="w-full p-3 border rounded-lg min-h-20 mb-4"
        placeholder="e.g., Show top 10 artists based on popularity"
      />

      <button
        className="bg-blue-500 text-white py-2 px-6 rounded-lg hover:bg-blue-600 disabled:bg-blue-300 flex items-center"
        onClick={handleGenerateQuery}
        disabled={!schema || showSimilarQuery}
      >
        Generate & Execute Query
      </button>

      {showSimilarQuery && (
        <div className="mt-4 p-4 bg-gray-50 rounded-lg border">
          <h3 className="font-medium">Similar query found:</h3>
          <p className="my-2">{similarQuery}</p>
          <h3 className="font-medium mt-3">Suggested SQL:</h3>
          <pre className="bg-gray-100 p-2 rounded my-2 overflow-x-auto text-sm">
            <code>{pastSql}</code>
          </pre>

          <div className="mt-4">
            <p className="mb-2">
              Would you like to use the suggested SQL query instead of
              generating a new one?
            </p>
            <div className="flex space-x-4">
              <button
                className="bg-green-500 text-white py-1 px-4 rounded hover:bg-green-600"
                onClick={() => setUseSuggested("yes")}
              >
                Yes
              </button>
              <button
                className="bg-red-500 text-white py-1 px-4 rounded hover:bg-red-600"
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
