import React from 'react';
import { useAppContext } from '../context/AppContext';
import QueryInput from './QueryInput';
import Feedback from './Feedback';
import TabContainer from './TabContainer';
import ChatHistory from './ChatHistory';

const ChatPage = () => {
  const { schema, loading, error, projectId, datasetId } = useAppContext();
  
  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      <header className="bg-[#1a73e8] shadow-md">
        <div className="w-full px-4 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-white">📊 BigQuery Analytics Dashboard</h1>
            <div className="text-white bg-[#174ea6] px-3 py-1 rounded text-sm">
              {projectId} / {datasetId}
            </div>
          </div>
        </div>
      </header>
      
      <main className="flex-grow flex bg-[#f8f9fa]">
        {/* Left Sidebar for Chat History */}
        <div className="w-64 bg-white border-r border-[#dadce0] overflow-y-auto flex-shrink-0">
          <ChatHistory />
        </div>
        
        {/* Main Content Area */}
        <div className="flex-grow overflow-y-auto">
          <div className="max-w-3xl mx-auto px-4 sm:px-6 py-6">
            <QueryInput />
            
            {loading && (
              <div className="flex justify-center items-center py-10">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-[#1a73e8]"></div>
              </div>
            )}
            
            {error && (
              <div className="bg-[#fce8e6] border border-[#d93025] text-[#d93025] px-4 py-3 rounded-lg mb-6">
                <p><strong>Error:</strong> {error}</p>
              </div>
            )}
            
            {/* TabContainer for results and visualization */}
            <TabContainer />
            <Feedback />
          </div>
        </div>
        
        {/* Right Sidebar for Schema Overview */}
        <div className="w-72 bg-white border-l border-[#dadce0] overflow-y-auto flex-shrink-0">
          <div className="p-4">
            <h2 className="text-lg font-semibold mb-4 text-[#202124]">Schema Overview</h2>
            {schema ? (
              <div className="bg-[#f8f9fa] rounded-lg p-3 text-sm font-mono overflow-auto max-h-screen border border-[#dadce0]">
                <pre className="whitespace-pre-wrap text-[#5f6368]">{schema}</pre>
              </div>
            ) : (
              <p className="text-[#5f6368]">No schema loaded yet.</p>
            )}
          </div>
        </div>
      </main>
      
      <footer className="bg-white border-t border-[#dadce0]">
        <div className="w-full px-4 py-3">
          <p className="text-center text-[#5f6368] text-sm">
            BigQuery Analytics Dashboard &copy; 2025
          </p>
        </div>
      </footer>
    </div>
  );
};

export default ChatPage;