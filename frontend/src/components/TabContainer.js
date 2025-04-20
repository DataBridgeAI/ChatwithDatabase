import React, { useState, useEffect } from 'react';
import { useAppContext } from '../context/AppContext';
import QueryResult from './QueryResult';
import Visualization from './Visualization';

const TabContainer = () => {
  const { queryResults, showVisualization } = useAppContext();
  const [activeTab, setActiveTab] = useState('results');
  const [animateIn, setAnimateIn] = useState(false);
  
  // Animation effect when component mounts
  useEffect(() => {
    setAnimateIn(true);
  }, []);
  
  // Switch to results tab by default when new results come in
  useEffect(() => {
    if (queryResults) {
      setActiveTab('results');
    }
  }, [queryResults]);
  
  // Switch to visualization tab when visualization is toggled on
  useEffect(() => {
    if (showVisualization && queryResults) {
      setActiveTab('visualization');
    } else {
      setActiveTab('results');
    }
  }, [showVisualization, queryResults]);
  
  if (!queryResults) {
    return null;
  }
  
  return (
    <div className={`mt-6 transition-all duration-700 transform ${
      animateIn ? 'translate-y-0 opacity-100' : 'translate-y-12 opacity-0'
    }`}>
      <div className="glass-card rounded-xl shadow-lg overflow-hidden">
        <div className="border-b border-blue-500/20">
          <div className="flex">
            <button
              onClick={() => setActiveTab('results')}
              className={`relative py-4 px-6 font-medium text-sm transition-all focus:outline-none ${
                activeTab === 'results'
                  ? 'text-blue-300'
                  : 'text-blue-400 hover:text-blue-300'
              }`}
            >
              <div className="flex items-center">
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                </svg>
                Query Results
              </div>
              {activeTab === 'results' && (
                <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-blue-400 to-purple-400"></div>
              )}
            </button>
            
            {showVisualization && (
              <button
                onClick={() => setActiveTab('visualization')}
                className={`relative py-4 px-6 font-medium text-sm transition-all focus:outline-none ${
                  activeTab === 'visualization'
                    ? 'text-blue-300'
                    : 'text-blue-400 hover:text-blue-300'
                }`}
              >
                <div className="flex items-center">
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  Visualization
                </div>
                {activeTab === 'visualization' && (
                  <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-blue-400 to-purple-400"></div>
                )}
              </button>
            )}
          </div>
        </div>
        
        <div className="p-6">
          {activeTab === 'results' && <QueryResult />}
          {activeTab === 'visualization' && showVisualization && <Visualization />}
        </div>
      </div>
    </div>
  );
};

export default TabContainer;