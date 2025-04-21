import React, { useState, useEffect } from 'react';
import { useAppContext } from '../context/AppContext';
import QueryInput from './QueryInput';
import Feedback from './Feedback';
import TabContainer from './TabContainer';
import ChatHistory from './ChatHistory';
import FloatingNewChatButton from './FloatingNewChatButton';
import '../styles/glassmorphism.css';
// Import the logo image
import veltrixLogo from "../assets/veltrix-logo.png";

const ChatPage = ({ onNavigateBack }) => {
  const { schema, loading, error, projectId, datasetId } = useAppContext();
  const [showHistory, setShowHistory] = useState(true);
  const [showSchema, setShowSchema] = useState(true);
  const [animateIn, setAnimateIn] = useState(false);
  
  // Animation effect when component mounts
  useEffect(() => {
    setAnimateIn(true);
  }, []);

  // Handle browser back button
  useEffect(() => {
    const handleBackButton = (event) => {
      // Listen for popstate (browser back button)
      if (onNavigateBack) {
        onNavigateBack();
      }
    };

    window.addEventListener('popstate', handleBackButton);
    
    return () => {
      window.removeEventListener('popstate', handleBackButton);
    };
  }, [onNavigateBack]);

  return (
    <div className="flex flex-col min-h-screen bg-glass-gradient relative overflow-hidden">
      {/* Background with enhanced visual elements */}
      <div className="absolute inset-0 z-0">
        {/* Background gradient overlay */}
        <div className="bg-chat-gradient"></div>
        
        {/* Add subtle noise texture for depth */}
        <div className="bg-texture"></div>
        
        {/* Abstract line patterns */}
        <div className="abstract-lines">
          {/* Horizontal lines */}
          <div className="line-h line-h-1"></div>
          <div className="line-h line-h-2"></div>
          <div className="line-h line-h-3"></div>
          <div className="line-h line-h-4"></div>
          
          {/* Vertical lines */}
          <div className="line-v line-v-1"></div>
          <div className="line-v line-v-2"></div>
          <div className="line-v line-v-3"></div>
          <div className="line-v line-v-4"></div>
          
          {/* Diagonal lines */}
          <div className="line-d line-d-1"></div>
          <div className="line-d line-d-2"></div>
          <div className="line-d line-d-3"></div>
          <div className="line-d line-d-4"></div>
        </div>
        
        {/* Animated background glow spots - enhanced with varied colors */}
        <div className="glow-spot-1"></div>
        <div className="glow-spot-2"></div>
        <div className="glow-spot-3"></div>
        <div className="glow-spot-4"></div>
        <div className="glow-spot-5"></div>
        
        {/* Animated particles effect - enhanced with more particles and colors */}
        <div className="absolute top-0 left-0 w-full h-full overflow-hidden">
          <div className="particle particle-1"></div>
          <div className="particle particle-2"></div>
          <div className="particle particle-3"></div>
          <div className="particle particle-4"></div>
          <div className="particle particle-5"></div>
          <div className="particle particle-6"></div>
          <div className="particle particle-7"></div>
        </div>
      </div>
      
      <header className="glass-card border-b border-blue-500/20 shadow-lg z-10 transition-all duration-500 transform backdrop-blur-lg">
        <div className="w-full px-6 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-4">
              <button 
                className="rounded-full p-2 glass-button flex items-center justify-center w-10 h-10 text-blue-300 hover:text-blue-200 transition-colors"
                onClick={() => setShowHistory(!showHistory)}
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
              <div className="flex items-center space-x-3">
                <button 
                  className="glass-button rounded-full flex items-center justify-center px-3 py-1 text-blue-300 hover:text-blue-200 transition-colors"
                  onClick={onNavigateBack}
                >
                  <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                  </svg>
                  Back
                </button>
                <div className="w-10 h-10 glass-glow rounded-full flex items-center justify-center shadow-lg pulse-glow">
                  {/* Replace the emoji with the Veltrix logo */}
                  <img src={veltrixLogo} alt="Veltrix Logo" width={28} height={28} />
                </div>
                <h1 className="text-2xl font-bold bg-gradient-text">Veltrix</h1>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="glass-card-light px-4 py-2 rounded-full text-sm text-blue-200 flex items-center space-x-2">
                <svg className="w-4 h-4 text-blue-300" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>{projectId} / {datasetId}</span>
              </div>
              <button 
                className="rounded-full p-2 glass-button flex items-center justify-center w-10 h-10 text-blue-300 hover:text-blue-200 transition-colors"
                onClick={() => setShowSchema(!showSchema)}
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </header>
      
      <main className="flex-grow flex overflow-hidden z-10 relative chat-page-main-content">
        {/* Left Sidebar for Chat History */}
        <div 
          className={`${
            showHistory ? 'w-72' : 'w-0'
          } glass-card-dark border-r border-blue-500/20 overflow-y-auto flex-shrink-0 shadow-lg z-0 transition-all duration-500 ease-in-out backdrop-blur-lg`}
        >
          {showHistory && <ChatHistory />}
        </div>
        
        {/* Main Content Area */}
        <div className={`flex-grow overflow-y-auto transition-all duration-500 ease-in-out ${
          animateIn ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'
        }`}>
          <div className="max-w-3xl mx-auto px-4 sm:px-6 py-6">
            <div className="mb-6">
              <QueryInput />
            </div>
            
            {loading && (
              <div className="flex justify-center items-center py-10">
                <div className="relative w-16 h-16">
                  <div className="absolute top-0 left-0 w-full h-full border-4 border-blue-400 rounded-full opacity-30 animate-ping"></div>
                  <div className="absolute top-2 left-2 w-12 h-12 border-4 border-t-4 border-blue-500 rounded-full animate-spin"></div>
                </div>
              </div>
            )}
            
            {error && (
              <div className="glass-card-dark bg-red-900/30 border-2 border-red-500/50 text-red-300 px-6 py-4 rounded-xl mb-6 shadow-lg">
                <div className="flex items-center">
                  <svg className="w-6 h-6 mr-3 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <p><strong>Error:</strong> {error}</p>
                </div>
              </div>
            )}
            
            {/* TabContainer for results and visualization */}
            <TabContainer />
            <Feedback />
          </div>
        </div>
        
        {/* Right Sidebar for Schema Overview */}
        <div 
          className={`${
            showSchema ? 'w-80' : 'w-0'
          } glass-card border-l border-blue-500/20 overflow-y-auto flex-shrink-0 shadow-lg z-0 transition-all duration-500 ease-in-out backdrop-blur-lg`}
        >
          {showSchema && (
            <div className="p-4">
              <div className="flex items-center mb-4 text-blue-300">
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
                </svg>
                <h2 className="text-lg font-semibold bg-gradient-text">Schema Overview</h2>
              </div>
              {schema ? (
                <div className="glass-card-dark rounded-xl p-4 text-sm font-mono overflow-auto max-h-screen text-blue-200 border border-blue-500/20">
                  <pre className="whitespace-pre-wrap">{schema}</pre>
                </div>
              ) : (
                <p className="text-blue-400 flex items-center">
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  No schema loaded yet.
                </p>
              )}
            </div>
          )}
        </div>
      </main>
      
      <footer className="glass-card border-t border-blue-500/20 shadow-lg z-10 backdrop-blur-lg">
        <div className="w-full px-4 py-3">
          <div className="flex justify-between items-center">
            <div className="text-blue-400 text-sm flex items-center">
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              <span>Powered by Natural Language Processing</span>
            </div>
            <p className="text-center text-blue-400 text-sm">
              Veltrix &copy; 2025
            </p>
          </div>
        </div>
      </footer>
      
      {/* Floating Full-Width New Chat Button */}
      <FloatingNewChatButton />
    </div>
  );
};

export default ChatPage;