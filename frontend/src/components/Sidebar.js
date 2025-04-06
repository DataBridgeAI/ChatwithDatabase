import React, { useState } from "react";
import { useAppContext } from "../context/AppContext";
import { fetchSchema, setCredentialsPath } from "../api/api";

const Sidebar = () => {
  const {
    projectId,
    setProjectId,
    datasetId,
    setDatasetId,
    setSchema,
    setError,
  } = useAppContext();

  const [loading, setLoading] = useState(false);

  const handleLoadSchema = async () => {
    setLoading(true);
    setError(null);

    try {
      // First, set the credentials path
      const credResult = await setCredentialsPath(
        "/Users/sirigowda/Desktop/a.json"
      );
      console.log("Credentials path result:", credResult);

      if (credResult.success) {
        // Then fetch schema
        const response = await fetchSchema(projectId, datasetId);
        if (response.schema) {
          setSchema(response.schema);
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
    <div className="bg-gray-100 p-4 rounded-lg shadow">
      <h2 className="text-lg font-semibold mb-4">BigQuery Configuration</h2>

      <div className="mb-4">
        <label className="block text-sm font-medium mb-1">Project ID</label>
        <input
          type="text"
          value={projectId}
          onChange={(e) => setProjectId(e.target.value)}
          className="w-full p-2 border rounded"
          placeholder="your-gcp-project-id"
        />
      </div>

      <div className="mb-4">
        <label className="block text-sm font-medium mb-1">Dataset ID</label>
        <input
          type="text"
          value={datasetId}
          onChange={(e) => setDatasetId(e.target.value)}
          className="w-full p-2 border rounded"
          placeholder="your-dataset"
        />
      </div>

      <button
        className="w-full bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600 flex items-center justify-center"
        onClick={handleLoadSchema}
        disabled={loading}
      >
        {loading ? (
          <>
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
            Loading...
          </>
        ) : (
          <>📥 Load Schema</>
        )}
      </button>
    </div>
  );
};

export default Sidebar;
