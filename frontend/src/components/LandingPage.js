// frontend/src/components/LandingPage.js
import React, { useState } from "react";
import { useAppContext } from "../context/AppContext";
import { fetchSchema } from "../api/api";

const LandingPage = () => {
  const {
    projectId,
    setProjectId,
    datasetId,
    setDatasetId,
    setSchema,
    setIsSchemaLoaded,
    setError,
  } = useAppContext();

  const [loading, setLoading] = useState(false);
  // Removed the credentials state

  const handleLoadSchema = async () => {
    if (!projectId.trim() || !datasetId.trim()) {
      setError("Please enter both Project ID and Dataset ID");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetchSchema(projectId, datasetId);
      if (response.schema) {
        setSchema(response.schema);
        setIsSchemaLoaded(true); // This will trigger navigation to the chat page
      } else if (response.error) {
        setError(response.error);
      }
    } catch (error) {
      setError(error.message || "Failed to load schema");
      console.error("Error loading schema:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-[#f8f9fa] px-4">
      {/* Decorative top header */}
      <div className="absolute top-0 left-0 right-0 h-16 bg-[#1a73e8]"></div>
      
      <div className="w-full max-w-md p-8 bg-white rounded-lg shadow-lg border border-[#dadce0] mt-16 relative z-10">
        <div className="text-center mb-8">
          <div className="w-20 h-20 bg-[#1a73e8] rounded-full flex items-center justify-center mx-auto -mt-16 shadow-md">
            <span className="text-3xl text-white">📊</span>
          </div>
          <h1 className="text-3xl font-bold text-[#1a73e8] mt-4">BigQuery Analytics</h1>
          <p className="text-[#5f6368] mt-2">
            Connect to your BigQuery dataset to get started
          </p>
        </div>

        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-[#202124] mb-1">
              Project ID
            </label>
            <input
              type="text"
              value={projectId}
              onChange={(e) => setProjectId(e.target.value)}
              className="w-full p-3 border border-[#dadce0] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1a73e8] focus:border-transparent transition-all"
              placeholder="your-gcp-project-id"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-[#202124] mb-1">
              Dataset ID
            </label>
            <input
              type="text"
              value={datasetId}
              onChange={(e) => setDatasetId(e.target.value)}
              className="w-full p-3 border border-[#dadce0] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1a73e8] focus:border-transparent transition-all"
              placeholder="your-dataset"
            />
          </div>

          {/* Error message display */}
          {setError && (
            <div className="bg-[#fce8e6] text-[#d93025] p-3 rounded-lg text-sm hidden">
              Error message would appear here
            </div>
          )}

          <button
            className="w-full bg-[#1a73e8] text-white p-3 rounded-lg hover:bg-[#174ea6] focus:outline-none focus:ring-2 focus:ring-[#1a73e8] focus:ring-opacity-50 transition-colors shadow-sm"
            onClick={handleLoadSchema}
            disabled={loading}
          >
            {loading ? (
              <div className="flex items-center justify-center">
                <svg
                  className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  ></circle>
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
                Loading Schema...
              </div>
            ) : (
              "Connect & Load Schema"
            )}
          </button>
        </div>
      </div>
      
      <footer className="mt-8 text-center text-[#5f6368] text-sm">
        <p>BigQuery Analytics Dashboard &copy; 2025</p>
      </footer>
    </div>
  );
};

export default LandingPage;