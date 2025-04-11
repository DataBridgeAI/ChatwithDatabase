import React, { useState } from "react";
import { useAppContext } from "../context/AppContext";
import { fetchSchema, setCredentialsPath } from "../api/api";

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
  const [credentials, setCredentials] = useState("/Users/sirigowda/Desktop/a.json");

  const handleLoadSchema = async () => {
    if (!projectId.trim() || !datasetId.trim()) {
      setError("Please enter both Project ID and Dataset ID");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // First, set the credentials path
      const credResult = await setCredentialsPath(credentials);
      console.log("Credentials path result:", credResult);

      if (credResult.success) {
        // Then fetch schema
        const response = await fetchSchema(projectId, datasetId);
        if (response.schema) {
          setSchema(response.schema);
          setIsSchemaLoaded(true); // This will trigger navigation to the chat page
        } else if (response.error) {
          setError(response.error);
        }
      } else {
        setError(credResult.error || "Failed to set credentials path");
      }
    } catch (error) {
      setError(error.message || "Failed to load schema");
      console.error("Error loading schema:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50 px-4">
      <div className="w-full max-w-md p-8 bg-white rounded-lg shadow-lg">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-blue-600">📊 BigQuery Analytics</h1>
          <p className="text-gray-600 mt-2">
            Connect to your BigQuery dataset to get started
          </p>
        </div>

        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Project ID
            </label>
            <input
              type="text"
              value={projectId}
              onChange={(e) => setProjectId(e.target.value)}
              className="w-full p-3 border rounded-lg focus:ring-blue-500 focus:border-blue-500"
              placeholder="your-gcp-project-id"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Dataset ID
            </label>
            <input
              type="text"
              value={datasetId}
              onChange={(e) => setDatasetId(e.target.value)}
              className="w-full p-3 border rounded-lg focus:ring-blue-500 focus:border-blue-500"
              placeholder="your-dataset"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Credentials Path
            </label>
            <input
              type="text"
              value={credentials}
              onChange={(e) => setCredentials(e.target.value)}
              className="w-full p-3 border rounded-lg focus:ring-blue-500 focus:border-blue-500"
              placeholder="/path/to/credentials.json"
            />
          </div>

          <button
            className="w-full bg-blue-600 text-white p-3 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50 transition-colors"
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
    </div>
  );
};

export default LandingPage;