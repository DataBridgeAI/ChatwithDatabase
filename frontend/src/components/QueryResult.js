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
  const [isDownloading, setIsDownloading] = useState(false);
  
  const downloadResults = async () => {
    try {
      setIsDownloading(true);
      
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
      
      // Show success animation
      setTimeout(() => setIsDownloading(false), 1000);
    } catch (error) {
      console.error('Download error:', error);
      alert('Failed to download results: ' + error.message);
      setIsDownloading(false);
    }
  };
  
  if (!queryResults) {
    return null;
  }
  
  return (
    <div className="fade-in">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold bg-gradient-text">Query Results</h2>
        <div className="flex items-center gap-4">
          <button
            onClick={downloadResults}
            disabled={isDownloading}
            className="glass-button px-5 py-2.5 rounded-lg flex items-center gap-2 shadow-lg transition-all hover:bg-blue-600/20 relative overflow-hidden group"
          >
            <div className="relative z-10 flex items-center">
              {isDownloading ? (
                <svg className="animate-spin w-5 h-5 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              ) : (
                <svg className="w-5 h-5 mr-2 transition-all group-hover:-translate-y-1 group-hover:translate-x-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
              )}
              <span className="font-medium">
                {isDownloading ? 'Downloading...' : 'Download JSON'}
              </span>
            </div>
            <span className="absolute w-full h-full top-0 left-0 bg-gradient-to-r from-blue-500/10 via-blue-500/20 to-purple-500/10 -translate-x-full group-hover:translate-x-0 transition-transform duration-300"></span>
          </button>
          {queryExecutionTime > 0 && (
            <div className="glass-card-light px-3 py-1.5 rounded-full text-sm flex items-center space-x-1.5 shadow-md">
              <svg className="w-4 h-4 text-blue-300" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="font-medium text-blue-300">{queryExecutionTime.toFixed(2)}s</span>
            </div>
          )}
        </div>
      </div>
      
      <div className="mb-6">
        {/* Slimmer, more elegant SQL toggle button */}
        <button
          className="inline-flex items-center text-blue-300 hover:text-blue-200 text-sm py-1 px-2 rounded transition-colors border border-transparent hover:border-blue-500/20 hover:bg-blue-500/5"
          onClick={() => setShowSql(!showSql)}
        >
          <svg className="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
          </svg>
          <span>{showSql ? 'Hide' : 'View'} SQL</span>
          <svg
            className={`ml-1.5 w-3.5 h-3.5 transition-transform ${showSql ? 'rotate-180' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path>
          </svg>
        </button>
        
        {showSql && (
          <div className="mt-3 glass-card-dark rounded-xl overflow-hidden shadow-lg border border-blue-500/20">
            <div className="flex items-center justify-between px-4 py-2 border-b border-blue-500/20 bg-blue-500/10">
              <div className="flex items-center">
                <svg className="w-4 h-4 mr-2 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                </svg>
                <span className="text-xs font-medium text-blue-300">SQL Query</span>
              </div>
              <button 
                className="text-blue-400 hover:text-blue-300 p-1 rounded-md hover:bg-blue-500/10 transition-colors"
                onClick={() => {
                  navigator.clipboard.writeText(generatedSql);
                }}
                title="Copy to clipboard"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
                </svg>
              </button>
            </div>
            <pre className="p-4 text-blue-200 font-mono text-sm overflow-x-auto">{generatedSql}</pre>
          </div>
        )}
      </div>
      
      {/* Table container with both horizontal and vertical scrolling */}
      <div className="glass-card rounded-xl overflow-hidden shadow-lg border border-blue-500/20 pulse-subtle">
        <div className="max-h-[500px] overflow-auto"> {/* Set a fixed height and enable scrolling */}
          <table className="min-w-full">
            <thead className="sticky top-0 z-10"> {/* Make the header sticky */}
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
                      {value !== null ? String(value) : 
                        <span className="text-blue-400 italic">NULL</span>
                      }
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      
      {/* Pagination info if there are many results */}
      {queryResults.length > 50 && (
        <div className="mt-4 flex items-center justify-center text-blue-400 text-sm">
          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Showing all {queryResults.length} results. Scroll to see more.
        </div>
      )}
    </div>
  );
};

export default QueryResult;