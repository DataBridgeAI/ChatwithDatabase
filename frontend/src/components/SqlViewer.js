import React, { useState } from 'react';
import { useAppContext } from '../context/AppContext';
import { executeSqlQuery } from '../api/api';

const SqlViewer = () => {
  const {
    generatedSql,
    setQueryResults,
    setError,
    setLoading,
    setQueryExecutionTime
  } = useAppContext();
  
  const [isEditing, setIsEditing] = useState(false);
  const [editedSql, setEditedSql] = useState('');
  
  if (!generatedSql) {
    return null;
  }
  
  const handleEditClick = () => {
    setIsEditing(true);
    setEditedSql(generatedSql);
  };
  
  const handleCancelEdit = () => {
    setIsEditing(false);
  };
  
  const handleExecuteEdited = async () => {
    if (!editedSql.trim()) {
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const result = await executeSqlQuery(editedSql);
      
      if (result.error) {
        setError(result.error);
      } else {
        setQueryResults(result.results);
        setQueryExecutionTime(result.execution_time);
      }
    } catch (error) {
      setError(error.message || 'An error occurred during SQL execution');
    } finally {
      setLoading(false);
      setIsEditing(false);
    }
  };
  
  const handleCopyToClipboard = () => {
    navigator.clipboard.writeText(generatedSql)
      .then(() => {
        // You could add a temporary success message here
        console.log('SQL copied to clipboard');
      })
      .catch(err => {
        console.error('Failed to copy SQL: ', err);
      });
  };
  
  return (
    <div className="mt-4">
      <div className="flex justify-between items-center mb-2">
        <h3 className="text-lg font-medium">Generated SQL</h3>
        <div className="flex space-x-2">
          {!isEditing && (
            <>
              <button
                className="text-blue-500 hover:text-blue-700 text-sm"
                onClick={handleEditClick}
              >
                Edit
              </button>
              <button
                className="text-blue-500 hover:text-blue-700 text-sm"
                onClick={handleCopyToClipboard}
              >
                Copy
              </button>
            </>
          )}
        </div>
      </div>
      
      {isEditing ? (
        <div className="space-y-2">
          <textarea
            className="w-full h-64 p-4 font-mono text-sm bg-gray-800 text-white rounded-md"
            value={editedSql}
            onChange={(e) => setEditedSql(e.target.value)}
          />
          <div className="flex space-x-2">
            <button
              className="bg-blue-500 text-white py-1 px-4 rounded hover:bg-blue-600"
              onClick={handleExecuteEdited}
            >
              Execute
            </button>
            <button
              className="bg-gray-500 text-white py-1 px-4 rounded hover:bg-gray-600"
              onClick={handleCancelEdit}
            >
              Cancel
            </button>
          </div>
        </div>
      ) : (
        <div className="p-4 bg-gray-800 text-white rounded-md overflow-x-auto">
          <pre className="text-sm font-mono">{generatedSql}</pre>
        </div>
      )}
    </div>
  );
};

export default SqlViewer;