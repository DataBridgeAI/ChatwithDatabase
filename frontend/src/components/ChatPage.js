import React from 'react';
import { useAppContext } from '../context/AppContext';
import QueryInput from './QueryInput';
import Feedback from './Feedback';
import TabContainer from './TabContainer';

const ChatPage = () => {
  const { schema, loading, error, projectId, datasetId } = useAppContext();
  
  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-blue-600">📊 BigQuery Analytics Dashboard</h1>
            <div className="text-sm text-gray-500">
              {projectId} / {datasetId}
            </div>
          </div>
        </div>
      </header>
      
      <main className="flex-grow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          {/* Schema Overview */}
          {schema && (
            <div className="mb-6">
              <details className="bg-white rounded-lg shadow-sm">
                <summary className="px-4 py-3 cursor-pointer font-medium">
                  Schema Overview
                </summary>
                <div className="px-4 py-3 border-t">
                  <pre className="text-sm whitespace-pre-wrap">{schema}</pre>
                </div>
              </details>
            </div>
          )}
          
          <QueryInput />
          
          {loading && (
            <div className="flex justify-center items-center py-10">
              <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
            </div>
          )}
          
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
              <p><strong>Error:</strong> {error}</p>
            </div>
          )}
          
          {/* TabContainer instead of directly showing QueryResult and Visualization */}
          <TabContainer />
          <Feedback />
        </div>
      </main>
      
      <footer className="bg-white border-t">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
          <p className="text-center text-gray-500 text-sm">
            BigQuery Analytics Dashboard &copy; 2025
          </p>
        </div>
      </footer>
    </div>
  );
};

export default ChatPage;