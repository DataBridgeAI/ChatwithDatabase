import React, { useEffect, useState } from 'react';
import { useAppContext } from '../context/AppContext';
import { getChatHistory, getConversation } from '../api/api';

const ChatHistory = () => {
  const { 
    chatHistory, 
    setChatHistory, 
    loadingHistory, 
    setLoadingHistory,
    setUserQuery,
    setGeneratedSql,
    setQueryResults,
    currentConversationId,
    setCurrentConversationId,
    setProjectId,
    setDatasetId,
    setError
  } = useAppContext();
  
  const [errorMessage, setErrorMessage] = useState(null);
  const [animateIn, setAnimateIn] = useState(false);

  // Animation effect when component mounts
  useEffect(() => {
    setAnimateIn(true);
  }, []);

  // Fetch chat history when component mounts
  useEffect(() => {
    const fetchHistory = async () => {
      setLoadingHistory(true);
      setErrorMessage(null);
      
      try {
        // Request exactly 5 conversations
        const response = await getChatHistory(null, 5);
        
        if (response.success) {
          setChatHistory(response.conversations || []);
        } else if (response.error) {
          setErrorMessage(`Error loading chat history: ${response.error}`);
          console.error("Chat history error:", response.error);
        }
      } catch (error) {
        setErrorMessage("Failed to load chat history. Please try again later.");
        console.error("Failed to fetch chat history:", error);
      } finally {
        setLoadingHistory(false);
      }
    };

    fetchHistory();
  }, [setChatHistory, setLoadingHistory]);

  const handleConversationClick = async (conversationId) => {
    try {
      setLoadingHistory(true);
      setError(null);
      setErrorMessage(null);
      
      const response = await getConversation(conversationId);
      
      if (response.success) {
        // Set the current conversation id
        setCurrentConversationId(conversationId);
        
        // Set project and dataset from the conversation
        if (response.details) {
          const { project_id, dataset_id } = response.details;
          setProjectId(project_id || '');
          setDatasetId(dataset_id || '');
        }
        
        // Get the last message from the conversation
        if (response.messages && response.messages.length > 0) {
          const lastMessage = response.messages[response.messages.length - 1];
          
          // Set the UI with the last message data
          setUserQuery(lastMessage.user_query || '');
          setGeneratedSql(lastMessage.generated_sql || '');
          
          // Set the results if they exist
          if (lastMessage.results) {
            try {
              const results = typeof lastMessage.results === 'string' 
                ? JSON.parse(lastMessage.results) 
                : lastMessage.results;
              setQueryResults(results);
            } catch (e) {
              console.error("Error parsing results:", e);
            }
          }
        }
      } else {
        setErrorMessage(`Error loading conversation: ${response.error || 'Unknown error'}`);
      }
    } catch (error) {
      setErrorMessage("Failed to load conversation. Please try again later.");
      console.error("Error loading conversation:", error);
    } finally {
      setLoadingHistory(false);
    }
  };

  // Format the timestamp for display
  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'Unknown time';
    
    try {
      const date = new Date(timestamp);
      
      // Get today's date
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      
      // Get yesterday's date
      const yesterday = new Date(today);
      yesterday.setDate(yesterday.getDate() - 1);
      
      // Format date based on when it occurred
      if (date >= today) {
        return `Today, ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
      } else if (date >= yesterday) {
        return `Yesterday, ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
      } else {
        return date.toLocaleDateString([], { month: 'short', day: 'numeric' }) + 
               ` at ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
      }
    } catch (error) {
      return 'Unknown time';
    }
  };

  // Get a suitable icon for the conversation type
  const getConversationIcon = (query) => {
    const query_lower = (query || '').toLowerCase();
    
    if (query_lower.includes('top') || query_lower.includes('rank') || query_lower.includes('highest')) {
      return (
        <svg className="w-5 h-5 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
        </svg>
      );
    } else if (query_lower.includes('count') || query_lower.includes('how many') || query_lower.includes('total')) {
      return (
        <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
        </svg>
      );
    } else if (query_lower.includes('average') || query_lower.includes('mean') || query_lower.includes('median')) {
      return (
        <svg className="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      );
    } else if (query_lower.includes('find') || query_lower.includes('where') || query_lower.includes('search')) {
      return (
        <svg className="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      );
    } else {
      return (
        <svg className="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      );
    }
  };

  // Truncate text with ellipsis if too long
  const truncateText = (text, maxLength) => {
    if (!text) return '';
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
  };

  if (loadingHistory) {
    return (
      <div className="p-6">
        <div className="flex items-center mb-4">
          <svg className="w-5 h-5 mr-2 animate-pulse text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h2 className="text-lg font-semibold bg-gradient-to-r from-blue-300 to-purple-300 bg-clip-text text-transparent">Recent Conversations</h2>
        </div>
        <div className="flex justify-center items-center h-48">
          <div className="relative w-12 h-12">
            <div className="absolute top-0 left-0 w-full h-full border-4 border-blue-400/20 rounded-full"></div>
            <div className="absolute top-0 left-0 w-full h-full border-4 border-t-4 border-blue-400 rounded-full animate-spin"></div>
          </div>
        </div>
      </div>
    );
  }

  if (errorMessage) {
    return (
      <div className="p-6">
        <div className="flex items-center mb-4">
          <svg className="w-5 h-5 mr-2 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h2 className="text-lg font-semibold bg-gradient-to-r from-blue-300 to-purple-300 bg-clip-text text-transparent">Recent Conversations</h2>
        </div>
        <div className="glass-card-dark bg-red-900/20 border border-red-400/50 text-red-300 px-4 py-3 rounded-xl">
          <div className="flex items-center">
            <svg className="w-5 h-5 mr-2 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p>{errorMessage}</p>
          </div>
        </div>
      </div>
    );
  }

  if (!chatHistory || chatHistory.length === 0) {
    return (
      <div className="p-6">
        <div className="flex items-center mb-4">
          <svg className="w-5 h-5 mr-2 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
          <h2 className="text-lg font-semibold bg-gradient-to-r from-blue-300 to-purple-300 bg-clip-text text-transparent">Recent Conversations</h2>
        </div>
        <div className="glass-card-light p-6 rounded-xl text-center">
          <svg className="w-12 h-12 mx-auto mb-3 text-blue-400/50" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
          <p className="text-blue-300">No recent conversations found.</p>
          <p className="text-blue-400 text-sm mt-2">Start by asking a question above.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      <div className="p-4 border-b border-blue-500/20 bg-blue-500/10">
        <div className="flex items-center">
          <svg className="w-5 h-5 mr-2 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
          <h2 className="text-lg font-semibold bg-gradient-to-r from-blue-300 to-purple-300 bg-clip-text text-transparent">
            Recent Conversations
          </h2>
        </div>
      </div>
      
      <div className="flex-grow overflow-y-auto">
        <div className={`space-y-2 p-3 transition-all duration-700 transform ${
          animateIn ? 'translate-y-0 opacity-100' : 'translate-y-12 opacity-0'
        }`}>
          {chatHistory.map((conversation, index) => (
            <div 
              key={conversation.id || index} 
              onClick={() => handleConversationClick(conversation.id)}
              className={`glass-card-light p-3 rounded-lg cursor-pointer transition-all hover:translate-x-1 ${
                currentConversationId === conversation.id 
                ? 'border-l-4 border-blue-500 bg-blue-500/10' 
                : 'border-l-4 border-transparent'
              }`}
            >
              <div className="flex items-start">
                <div className="flex-shrink-0 mt-1">
                  {getConversationIcon(conversation.user_query)}
                </div>
                <div className="ml-3 flex-1 min-w-0">
                  <p className="font-medium text-white truncate">
                    {truncateText(conversation.user_query || `Conversation ${index + 1}`, 40)}
                  </p>
                  <div className="mt-1 flex justify-between items-center">
                    <p className="text-xs text-blue-300 truncate max-w-[120px]">
                      {conversation.project_id || 'Unknown'}
                    </p>
                    <p className="text-xs text-blue-400 flex items-center">
                      <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      {formatTimestamp(conversation.timestamp)}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
      
      {/* Footer with hint */}
      <div className="p-3 border-t border-blue-500/20 bg-blue-500/5">
        <div className="text-center text-xs text-blue-400 flex items-center justify-center">
          <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Click on a conversation to reload it
        </div>
      </div>
    </div>
  );
};

export default ChatHistory;