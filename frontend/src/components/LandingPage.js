import React, { useState, useEffect } from "react";
import { useAppContext } from "../context/AppContext";
import { fetchSchema } from "../api/api";
import "../styles/glassmorphism.css";
// Import the logo image
import veltrixLogo from "../assets/veltrix-logo.png";

const LandingPage = ({ onNavigateToFrontPage }) => {
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
  const [animateIn, setAnimateIn] = useState(false);

  // Animation effect when component mounts
  useEffect(() => {
    setAnimateIn(true);
  }, []);

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
    <div className="flex flex-col items-center justify-center min-h-screen bg-glass-gradient px-4 overflow-hidden">
      {/* Background elements */}
      <div className="absolute inset-0 z-0">
        {/* Background gradient overlay */}
        <div className="bg-landing-gradient"></div>
        <div className="bg-texture"></div>
        
        {/* Abstract line patterns */}
        <div className="abstract-lines">
          <div className="line-h line-h-1"></div>
          <div className="line-h line-h-2"></div>
          <div className="line-h line-h-3"></div>
          <div className="line-h line-h-4"></div>
          <div className="line-v line-v-1"></div>
          <div className="line-v line-v-2"></div>
          <div className="line-v line-v-3"></div>
          <div className="line-v line-v-4"></div>
          <div className="line-d line-d-1"></div>
          <div className="line-d line-d-2"></div>
          <div className="line-d line-d-3"></div>
          <div className="line-d line-d-4"></div>
        </div>
        
        {/* Animated glow spots */}
        <div className="glow-spot-1"></div>
        <div className="glow-spot-2"></div>
        <div className="glow-spot-3"></div>
        <div className="glow-spot-4"></div>
        <div className="glow-spot-5"></div>
        
        {/* Animated particles effect */}
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
      
      {/* Back button to front page */}
      <div className="absolute top-4 left-4 z-20">
        <button
          className="glass-button rounded-full flex items-center justify-center px-3 py-1 text-blue-300 hover:text-blue-200 transition-colors"
          onClick={onNavigateToFrontPage}
        >
          <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Back
        </button>
      </div>
      
      <div 
        className={`w-full max-w-md p-8 glass-card mt-16 relative z-10 transition-all duration-1000 transform ${
          animateIn ? 'translate-y-0 opacity-100' : 'translate-y-12 opacity-0'
        }`}
      >
        <div className="p-6"> {/* Added inner padding container */}
          <div className="text-center mb-8">
            {/* Logo on top of the name */}
            <div className="flex flex-col items-center justify-center">
              <img 
                src={veltrixLogo} 
                alt="Veltrix Logo" 
                className="w-24 h-24 object-contain mb-4"
              />
              <h1 className="text-4xl font-bold bg-gradient-text">
                Veltrix
              </h1>
            </div>
            
            <p className="text-blue-200 mt-3 text-lg">
              Connect to your dataset and explore with natural language
            </p>
            <div className="w-16 h-1 bg-gradient-to-r from-blue-400 to-purple-500 mx-auto mt-4 rounded-full"></div>
          </div>

          <div className="space-y-6">
            <div className={`transition-all duration-700 delay-300 transform ${
              animateIn ? 'translate-x-0 opacity-100' : 'translate-x-12 opacity-0'
            }`}>
              <label className="block text-sm font-medium text-blue-200 mb-2 flex items-center">
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
                Project ID
              </label>
              <div className="relative">
                <input
                  type="text"
                  value={projectId}
                  onChange={(e) => setProjectId(e.target.value)}
                  className="glass-input w-full p-3 pl-10 rounded-lg focus:ring-2 focus:ring-blue-400 transition-all"
                  placeholder="your-gcp-project-id"
                />
                <div className="absolute left-3 top-3.5 text-blue-300">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                  </svg>
                </div>
              </div>
            </div>

            <div className={`transition-all duration-700 delay-500 transform ${
              animateIn ? 'translate-x-0 opacity-100' : 'translate-x-12 opacity-0'
            }`}>
              <label className="block text-sm font-medium text-blue-200 mb-2 flex items-center">
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
                </svg>
                Dataset ID
              </label>
              <div className="relative">
                <input
                  type="text"
                  value={datasetId}
                  onChange={(e) => setDatasetId(e.target.value)}
                  className="glass-input w-full p-3 pl-10 rounded-lg focus:ring-2 focus:ring-blue-400 transition-all"
                  placeholder="your-dataset"
                />
                <div className="absolute left-3 top-3.5 text-blue-300">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
                  </svg>
                </div>
              </div>
            </div>

            <div className={`transition-all duration-700 delay-700 transform ${
              animateIn ? 'translate-y-0 opacity-100' : 'translate-y-12 opacity-0'
            }`}>
              <button
                className="w-full glass-button bg-gradient-to-r from-blue-500 to-purple-500 text-white p-3 rounded-lg hover:from-blue-600 hover:to-purple-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50 transition-all shadow-lg"
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
                  <div className="flex items-center justify-center">
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                    Connect & Explore Data
                  </div>
                )}
              </button>
            </div>
          </div>
          
          <div className={`mt-6 text-center text-xs text-blue-300/80 transition-all duration-700 delay-900 transform ${
            animateIn ? 'translate-y-0 opacity-100' : 'translate-y-12 opacity-0'
          }`}>
            Powered by advanced natural language processing and data visualization
          </div>
        </div>
      </div>
      
      <footer className={`mt-8 text-center transition-all duration-1000 delay-1000 transform ${
        animateIn ? 'translate-y-0 opacity-100' : 'translate-y-12 opacity-0'
      }`}>
        <div className="glass-card-light p-3 px-6 rounded-full">
          <p className="text-blue-300 text-sm">Veltrix Dashboard &copy; 2025</p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;