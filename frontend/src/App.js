import React, { useState, useEffect } from 'react';
import { AppProvider, useAppContext } from './context/AppContext';
import FrontPage from './components/FrontPage';
import LandingPage from './components/LandingPage';
import ChatPage from './components/ChatPage';

const AppContent = () => {
  const { 
    isSchemaLoaded, 
    setIsSchemaLoaded, 
    error, 
    setSchema, 
    setProjectId,
    setDatasetId,
    setError
  } = useAppContext();

  // New state to track if we should show the front page or the app
  const [showFrontPage, setShowFrontPage] = useState(true);
  
  // Check localStorage on mount to see if we should show the landing page
  useEffect(() => {
    const shouldShowLanding = localStorage.getItem('showLanding');
    if (shouldShowLanding === 'true') {
      setShowFrontPage(false);
      // Clean up localStorage to prevent it affecting future visits
      localStorage.removeItem('showLanding');
    }
  }, []);
  
  // Handler to navigate back to front page
  const handleNavigateToFrontPage = () => {
    setShowFrontPage(true);
    // Reset app state
    setIsSchemaLoaded(false);
    setSchema(null);
    setError(null);
    setProjectId('');
    setDatasetId('');
  };
  
  // Handle navigation back to landing page from chat page
  const handleNavigateToLanding = () => {
    // Reset schema and navigation state
    setIsSchemaLoaded(false);
    setSchema(null);
    setError(null);
    // Clear other state if needed
    setProjectId('');
    setDatasetId('');
  };

  // If showing the front page, render it
  if (showFrontPage) {
    return <FrontPage />;
  }

  // Otherwise, show the application (landing page or chat page)
  return (
    <div className="bg-glass-gradient">
      {/* Background glow spots */}
      <div className="glow-spot-1"></div>
      <div className="glow-spot-2"></div>
      <div className="glow-spot-3"></div>
      <div className="glow-spot-4"></div>
      <div className="glow-spot-5"></div>
      
      {error && (
        <div className="fixed top-4 left-1/2 transform -translate-x-1/2 glass-card border border-red-400/50 text-red-300 px-4 py-3 rounded-lg shadow-lg z-50 max-w-md animate-fadeSlideUp">
          <div className="flex items-center">
            <svg className="w-5 h-5 mr-2 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p><strong>Error:</strong> {error}</p>
          </div>
        </div>
      )}
      
      {isSchemaLoaded ? (
        <ChatPage onNavigateBack={handleNavigateToLanding} /> 
      ) : (
        <LandingPage onNavigateToFrontPage={handleNavigateToFrontPage} />
      )}
    </div>
  );
};

const App = () => {
  return (
    <AppProvider>
      <AppContent />
    </AppProvider>
  );
};

export default App;