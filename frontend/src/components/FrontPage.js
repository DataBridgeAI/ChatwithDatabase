import React from 'react';
import '../styles/frontpage.css';

const FrontPage = () => {
  // Simple function to redirect to the landing page
  const handleGetStarted = () => {
    // Set a flag in localStorage that App.js will check
    localStorage.setItem('showLanding', 'true');
    window.location.reload();
  };

  return (
    <div className="frontpage">
      {/* Hero section */}
      <section className="frontpage-hero">
        {/* Enhanced decorative elements */}
        <div className="frontpage-blob blob-1"></div>
        <div className="frontpage-blob blob-2"></div>
        <div className="frontpage-blob blob-3"></div>
        
        <div className="geo-element geo-circle"></div>
        <div className="geo-element geo-square"></div>
        <div className="geo-element geo-dots"></div>
        
        <div className="frontpage-content">
          <h1 className="frontpage-title animate-fadeIn">Your BigQuery Data with Veltrix</h1>
          <h2 className="frontpage-subtitle animate-fadeIn delay-1">Ask questions in plain English and get instant SQL queries and visualizations</h2>
          <p className="frontpage-description animate-fadeIn delay-2">
            Veltrix transforms how you interact with your data. No more complex SQL queries—just ask questions naturally and get immediate insights through powerful visualizations and analysis. Built for data professionals who want to focus on insights, not query syntax.
          </p>
          <button 
            className="frontpage-button animate-fadeIn delay-3"
            onClick={handleGetStarted}
          >
            Get Started
            <svg className="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </button>
        </div>
      </section>
      
      {/* Features section */}
      <section className="frontpage-features">
        <div className="frontpage-content">
          <div className="features-grid">
            <div className="feature-card animate-fadeIn">
              <div className="feature-icon feature-icon-1">
                <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
              <h3 className="feature-title">Natural Language to SQL</h3>
              <p className="feature-description">Ask questions in plain English and get accurate SQL queries instantly. No technical expertise required. Spend more time analyzing results and less time writing complex queries.</p>
            </div>
            
            <div className="feature-card animate-fadeIn delay-1">
              <div className="feature-icon feature-icon-2">
                <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3 className="feature-title">Interactive Visualizations</h3>
              <p className="feature-description">Transform your query results into beautiful, interactive visualizations that reveal hidden insights in your data. Choose from multiple chart types to find the perfect visualization for your needs.</p>
            </div>
            
            <div className="feature-card animate-fadeIn delay-2">
              <div className="feature-icon feature-icon-3">
                <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
              </div>
              <h3 className="feature-title">Conversation History</h3>
              <p className="feature-description">Save and revisit your previous queries and analyses. Build on past insights to drive deeper understanding of your data and collaborate effectively with your team members.</p>
            </div>
          </div>
        </div>
      </section>
      
      {/* CTA section with enhanced design */}
      <section className="frontpage-cta">
        <div className="frontpage-content">
          <h2 className="cta-title animate-fadeIn">Ready to transform your data experience?</h2>
          <p className="cta-description animate-fadeIn delay-1">
            Get started with Veltrix today and unlock the full potential of your data.
          </p>
          <button 
            className="cta-button animate-fadeIn delay-2"
            onClick={handleGetStarted}
          >
            Start Now
            <svg className="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </button>
        </div>
      </section>
      
      {/* Footer */}
      <footer className="frontpage-footer">
        <div className="footer-content">
          <div className="footer-logo">Veltrix</div>
          <div className="footer-links">
            <button className="footer-link">About</button>
            <button className="footer-link">Features</button>
            <button className="footer-link">Pricing</button>
            <button className="footer-link">Contact</button>
          </div>
          <div className="footer-copyright">
            © 2025 Veltrix. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
};

export default FrontPage;