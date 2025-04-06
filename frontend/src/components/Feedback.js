import React from 'react';
import { useAppContext } from '../context/AppContext';
import { submitFeedback } from '../api/api';

const Feedback = () => {
  const {
    userQuery,
    generatedSql,
    queryResults,
    feedbackSubmitted,
    setFeedbackSubmitted,
    setShowVisualization
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
  
  const handleVisualizationToggle = (choice) => {
    setShowVisualization(choice === 'yes');
  };
  
  return (
    <div className="mt-6 space-y-6">
      <div className="p-4 bg-gray-50 rounded-lg border">
        <h3 className="font-medium mb-3">Was this SQL query helpful?</h3>
        <div className="flex space-x-4">
          <button
            className="bg-green-500 text-white py-2 px-4 rounded hover:bg-green-600 flex items-center"
            onClick={() => handleFeedback(true)}
          >
            👍 Yes
          </button>
          <button
            className="bg-red-500 text-white py-2 px-4 rounded hover:bg-red-600 flex items-center"
            onClick={() => handleFeedback(false)}
          >
            👎 No
          </button>
        </div>
      </div>
      
      <div className="p-4 bg-gray-50 rounded-lg border">
        <h3 className="font-medium mb-3">Would you like to see visualizations?</h3>
        <div className="flex space-x-4">
          <button
            className="bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600"
            onClick={() => handleVisualizationToggle('yes')}
          >
            Yes
          </button>
          <button
            className="bg-gray-500 text-white py-2 px-4 rounded hover:bg-gray-600"
            onClick={() => handleVisualizationToggle('no')}
          >
            No
          </button>
        </div>
      </div>
    </div>
  );
};

export default Feedback;