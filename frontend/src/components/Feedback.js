import React from 'react';
import { useAppContext } from '../context/AppContext';
import { submitFeedback } from '../api/api';

const Feedback = () => {
  const {
    userQuery,
    generatedSql,
    queryResults,
    feedbackSubmitted,
    setFeedbackSubmitted
  } = useAppContext();
  
  if (!queryResults || feedbackSubmitted) {
    return null;
  }
  
  const handleFeedback = async (isHelpful) => {
    try {
      const feedback = isHelpful ? '👍 Yes' : '👎 No';
      // Determine if execution was successful (no errors in the results)
      const executionSuccess = queryResults && queryResults.length > 0;
      
      await submitFeedback(userQuery, generatedSql, feedback, executionSuccess);
      setFeedbackSubmitted(true);
    } catch (error) {
      console.error('Error submitting feedback:', error);
    }
  };
  
  return (
    <div className="mt-6">
      {/* SQL query feedback */}
      <div className="p-4 bg-[#e8f0fe] rounded-lg border border-[#dadce0] shadow-sm">
        <h3 className="font-medium mb-3 text-[#1a73e8]">Was this SQL query helpful?</h3>
        <div className="flex space-x-4">
          <button
            className="bg-[#34a853] text-white py-2 px-4 rounded hover:bg-[#2d9149] flex items-center shadow-sm transition-colors"
            onClick={() => handleFeedback(true)}
          >
            👍 Yes
          </button>
          <button
            className="bg-[#d93025] text-white py-2 px-4 rounded hover:bg-[#c62b21] flex items-center shadow-sm transition-colors"
            onClick={() => handleFeedback(false)}
          >
            👎 No
          </button>
        </div>
      </div>
    </div>
  );
};

export default Feedback;