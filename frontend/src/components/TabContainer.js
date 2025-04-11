import React, { useState, useEffect } from 'react';
import { useAppContext } from '../context/AppContext';
import QueryResult from './QueryResult';
import Visualization from './Visualization';

const TabContainer = () => {
  const { queryResults, showVisualization } = useAppContext();
  const [activeTab, setActiveTab] = useState('results');
  
  // Switch to results tab by default when new results come in
  useEffect(() => {
    if (queryResults) {
      setActiveTab('results');
    }
  }, [queryResults]);
  
  // Switch to visualization tab when visualization is toggled on
  useEffect(() => {
    if (showVisualization) {
      setActiveTab('visualization');
    } else {
      setActiveTab('results');
    }
  }, [showVisualization]);
  
  if (!queryResults) {
    return null;
  }
  
  return (
    <div className="mt-6">
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('results')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'results'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Query Results
          </button>
          
          {showVisualization && (
            <button
              onClick={() => setActiveTab('visualization')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'visualization'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Visualization
            </button>
          )}
        </nav>
      </div>
      
      <div className="py-4">
        {activeTab === 'results' && <QueryResult />}
        {activeTab === 'visualization' && showVisualization && <Visualization />}
      </div>
    </div>
  );
};

export default TabContainer;