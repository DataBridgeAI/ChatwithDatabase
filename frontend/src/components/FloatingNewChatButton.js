import React from 'react';
import { useAppContext } from '../context/AppContext';

const FloatingNewChatButton = () => {
  const { 
    resetStates,
    setUserQuery,
    setCurrentConversationId,
  } = useAppContext();

  // Function to handle starting a new chat
  const handleNewChat = () => {
    // Reset all states for a fresh start
    resetStates();
    
    // Clear the user query
    setUserQuery('');
    
    // Clear current conversation ID to ensure we're starting fresh
    setCurrentConversationId(null);
    
    // Scroll to the top of the page to focus on input
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="floating-button-container">
      <div className="max-w-3xl mx-auto px-4 sm:px-6">
        <button
          onClick={handleNewChat}
          className="floating-new-chat-button w-full py-3 rounded-lg shadow-xl hover:shadow-2xl transition-all"
          aria-label="Start a new chat"
          title="Start a new chat"
        >
          <div className="flex items-center justify-center">
            <svg 
              className="w-5 h-5 text-blue-300 mr-2 transition-colors" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24" 
              xmlns="http://www.w3.org/2000/svg"
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={2} 
                d="M12 6v6m0 0v6m0-6h6m-6 0H6"
              />
            </svg>
            <span className="text-blue-300 font-medium">New Chat</span>
          </div>
        </button>
      </div>
    </div>
  );
};

export default FloatingNewChatButton;