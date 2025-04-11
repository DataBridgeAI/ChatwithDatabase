import React from 'react';
import { AppProvider, useAppContext } from './context/AppContext';
import LandingPage from './components/LandingPage';
import ChatPage from './components/ChatPage';

const AppContent = () => {
  const { isSchemaLoaded, error } = useAppContext();
  
  // Render the landing page if schema is not loaded, otherwise render the chat page
  return (
    <div>
      {error && (
        <div className="fixed top-4 left-1/2 transform -translate-x-1/2 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg shadow-lg z-50 max-w-md">
          <p><strong>Error:</strong> {error}</p>
        </div>
      )}
      
      {isSchemaLoaded ? <ChatPage /> : <LandingPage />}
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