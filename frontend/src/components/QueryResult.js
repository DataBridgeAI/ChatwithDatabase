import React, { useState } from 'react';
import { useAppContext } from '../context/AppContext';
import { API_BASE_URL } from '../api/api';

const QueryResult = () => {
  const {
    queryResults,
    generatedSql,
    queryExecutionTime
  } = useAppContext();
  
  const [showSql, setShowSql] = useState(true);
  
  const downloadResults = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/query/download`, {
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
    <div className="fade-in">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold text-blue-300">🔍 Query Results</h2>
        <div className="flex items-center gap-4">
          <button
            onClick={downloadResults}
            className="px-4 py-2 bg-blue-600 text-white rounded-full hover:bg-blue-700 flex items-center gap-2 shadow-lg transition-all border-2 border-blue-400"
          >
            <span>📥</span>
            Download JSON
          </button>
          {queryExecutionTime > 0 && (
            <span className="text-sm text-blue-400">
              Execution time: {queryExecutionTime.toFixed(2)}s
            </span>
          )}
        </div>
      </div>
      
      <div className="mb-6">
        <button
          className="text-blue-400 hover:text-blue-300 flex items-center transition-colors"
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
          <div className="mt-3 glass-dark rounded-xl overflow-hidden shadow-lg border-2 border-blue-500/30">
            <pre className="p-4 text-blue-200 font-mono text-sm overflow-x-auto">{generatedSql}</pre>
          </div>
        )}
      </div>
      
      <div className="glass rounded-xl overflow-hidden shadow-lg border-2 border-blue-500/30 glow-border">
        <table className="min-w-full">
          <thead>
            <tr className="bg-blue-800/30 border-b border-blue-500/30">
              {queryResults.length > 0 && Object.keys(queryResults[0]).map((column, index) => (
                <th
                  key={index}
                  className="px-6 py-3 text-left text-xs font-medium text-blue-300 uppercase tracking-wider"
                >
                  {column}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {queryResults.map((row, rowIndex) => (
              <tr 
                key={rowIndex} 
                className={`${rowIndex % 2 === 0 
                  ? 'bg-blue-900/20' 
                  : 'bg-blue-800/20'
                } transition-colors hover:bg-blue-700/30`}
              >
                {Object.values(row).map((value, cellIndex) => (
                  <td key={cellIndex} className="px-6 py-4 whitespace-nowrap text-sm text-blue-200">
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