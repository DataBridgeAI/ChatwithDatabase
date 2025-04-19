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
      <div className="p-4 glass-dark rounded-lg border-2 border-blue-500/30 shadow-lg">
        <h3 className="font-medium mb-3 text-blue-300">Was this SQL query helpful?</h3>
        <div className="flex space-x-4">
          <button
            className="bg-green-600 text-white py-2 px-4 rounded-full hover:bg-green-700 flex items-center shadow-lg transition-colors border-2 border-green-500/60"
            onClick={() => handleFeedback(true)}
          >
            👍 Yes
          </button>
          <button
            className="bg-red-600 text-white py-2 px-4 rounded-full hover:bg-red-700 flex items-center shadow-lg transition-colors border-2 border-red-500/60"
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