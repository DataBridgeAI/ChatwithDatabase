import React, { useState } from 'react';
import { useAppContext } from '../context/AppContext';

const QueryResult = () => {
  const {
    queryResults,
    generatedSql,
    queryExecutionTime
  } = useAppContext();
  
  const [showSql, setShowSql] = useState(false);
  
  const downloadResults = async () => {
    try {
      const response = await fetch('http://localhost:5001/api/query/download', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ results: queryResults }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Download failed');
      }
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'query_results.json';
      document.body.appendChild(a);
      a.click();
      
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Download error:', error);
      alert('Failed to download results: ' + error.message);
    }
  };
  
  if (!queryResults) {
    return null;
  }
  
  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">🔍 Query Results</h2>
        <div className="flex items-center gap-4">
          <button
            onClick={downloadResults}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 flex items-center gap-2 shadow-sm transition-colors"
          >
            <span>📥</span>
            Download JSON
          </button>
          {queryExecutionTime > 0 && (
            <span className="text-sm text-gray-500">
              Execution time: {queryExecutionTime.toFixed(2)}s
            </span>
          )}
        </div>
      </div>
      
      <div className="mb-4">
        <button
          className="text-blue-500 hover:text-blue-700 flex items-center"
          onClick={() => setShowSql(!showSql)}
        >
          {showSql ? 'Hide' : 'View'} Generated SQL
          <svg
            className={`ml-1 w-4 h-4 transition-transform ${showSql ? 'rotate-180' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path>
          </svg>
        </button>
        
        {showSql && (
          <div className="mt-2 p-4 bg-gray-800 text-white rounded-md overflow-x-auto">
            <pre className="text-sm">{generatedSql}</pre>
          </div>
        )}
      </div>
      
      <div className="overflow-x-auto bg-white rounded-lg border shadow-sm">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              {queryResults.length > 0 && Object.keys(queryResults[0]).map((column, index) => (
                <th
                  key={index}
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  {column}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {queryResults.map((row, rowIndex) => (
              <tr key={rowIndex} className={rowIndex % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                {Object.values(row).map((value, cellIndex) => (
                  <td key={cellIndex} className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {value !== null ? String(value) : 'NULL'}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default QueryResult;
