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
      // Simple timestamp formatting
      return date.toLocaleString();
    } catch (error) {
      return 'Unknown time';
    }
  };

  if (loadingHistory) {
    return (
      <div className="p-4">
        <h2 className="text-lg font-semibold mb-4 text-[#202124]">Recent Conversations</h2>
        <div className="flex justify-center">
          <div className="animate-spin rounded-full h-6 w-6 border-t-2 border-b-2 border-[#1a73e8]"></div>
        </div>
      </div>
    );
  }

  if (errorMessage) {
    return (
      <div className="p-4">
        <h2 className="text-lg font-semibold mb-4 text-[#202124]">Recent Conversations</h2>
        <div className="bg-[#fce8e6] border border-[#d93025] text-[#d93025] px-4 py-3 rounded-lg">
          <p>{errorMessage}</p>
        </div>
      </div>
    );
  }

  if (!chatHistory || chatHistory.length === 0) {
    return (
      <div className="p-4">
        <h2 className="text-lg font-semibold mb-4 text-[#202124]">Recent Conversations</h2>
        <p className="text-[#5f6368]">No recent conversations found. Start by asking a question.</p>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      <div className="p-4 border-b border-[#dadce0] bg-[#e8f0fe]">
        <h2 className="text-lg font-semibold text-[#1a73e8]">
          Recent Conversations ({chatHistory.length})
        </h2>
      </div>
      
      <div className="flex-grow overflow-y-auto">
        <div className="divide-y divide-[#dadce0]">
          {chatHistory.map((conversation, index) => (
            <div 
              key={conversation.id || index} 
              onClick={() => handleConversationClick(conversation.id)}
              className={`p-4 cursor-pointer hover:bg-[#e8f0fe] transition duration-150 ${
                currentConversationId === conversation.id 
                ? 'bg-[#e8f0fe] border-l-4 border-[#1a73e8]' 
                : ''
              }`}
            >
              <p className="font-medium text-[#202124] truncate">
                {conversation.user_query || `Conversation ${index + 1}`}
              </p>
              <div className="mt-1 flex justify-between items-center">
                <p className="text-xs text-[#5f6368] truncate">
                  {conversation.project_id || 'Unknown'}
                </p>
                <p className="text-xs text-[#5f6368]">
                  {formatTimestamp(conversation.timestamp)}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ChatHistory;