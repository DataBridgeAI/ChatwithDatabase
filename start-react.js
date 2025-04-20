#!/usr/bin/env node

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const readline = require('readline');
const http = require('http');

// Parse command line arguments
const args = process.argv.slice(2);
let openaiApiKey = null;
let googleCredentialsPath = null;

// Function to parse arguments
function parseArgs() {
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--openai-key' && i + 1 < args.length) {
      openaiApiKey = args[i + 1];
      i++;
    } else if (args[i] === '--google-credentials' && i + 1 < args.length) {
      googleCredentialsPath = args[i + 1];
      i++;
    }
  }
}

// Function to read Google credentials from file
function readGoogleCredentials() {
  if (!googleCredentialsPath) return null;
  
  try {
    const fullPath = path.resolve(googleCredentialsPath);
    if (!fs.existsSync(fullPath)) {
      console.error(`Google credentials file not found: ${fullPath}`);
      return null;
    }
    
    const credentials = JSON.parse(fs.readFileSync(fullPath, 'utf8'));
    return credentials;
  } catch (error) {
    console.error('Error reading Google credentials:', error.message);
    return null;
  }
}

// Function to send credentials to the backend
function sendCredentials(apiKey, googleCreds) {
  const data = JSON.stringify({
    openai_api_key: apiKey,
    google_credentials: googleCreds
  });
  
  const options = {
    hostname: 'localhost',
    port: 5001,
    path: '/api/credentials',
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Content-Length': data.length
    }
  };
  
  return new Promise((resolve, reject) => {
    const req = http.request(options, (res) => {
      let responseData = '';
      
      res.on('data', (chunk) => {
        responseData += chunk;
      });
      
      res.on('end', () => {
        try {
          const parsedData = JSON.parse(responseData);
          resolve(parsedData);
        } catch (e) {
          reject(new Error('Failed to parse response'));
        }
      });
    });
    
    req.on('error', (error) => {
      reject(error);
    });
    
    req.write(data);
    req.end();
  });
}

// Function to check if backend is running
function checkBackendStatus() {
  return new Promise((resolve) => {
    const req = http.get('http://localhost:5001/api/health', (res) => {
      if (res.statusCode === 200) {
        resolve(true);
      } else {
        resolve(false);
      }
    });
    
    req.on('error', () => {
      resolve(false);
    });
    
    req.end();
  });
}

// Function to start the backend
function startBackend() {
  console.log('Starting backend server...');
  
  const backend = spawn('python', ['src/app.py'], {
    stdio: 'inherit',
    detached: true
  });
  
  backend.on('error', (err) => {
    console.error('Failed to start backend:', err);
  });
  
  return backend;
}

// Function to start the React app
function startReactApp() {
  console.log('Starting React app...');
  
  const reactApp = spawn('npm', ['start'], {
    cwd: path.join(process.cwd(), 'frontend'),
    stdio: 'inherit'
  });
  
  reactApp.on('error', (err) => {
    console.error('Failed to start React app:', err);
  });
  
  return reactApp;
}

// Main function
async function main() {
  parseArgs();
  
  // Check if we need to prompt for credentials
  if (!openaiApiKey) {
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });
    
    openaiApiKey = await new Promise(resolve => {
      rl.question('Enter your OpenAI API key: ', (answer) => {
        resolve(answer.trim());
      });
    });
    
    rl.close();
  }
  
  // Read Google credentials
  const googleCredentials = readGoogleCredentials();
  
  // Check if backend is running
  const backendRunning = await checkBackendStatus();
  let backendProcess = null;
  
  if (!backendRunning) {
    backendProcess = startBackend();
    
    // Wait for backend to start
    console.log('Waiting for backend to start...');
    let attempts = 0;
    while (attempts < 10) {
      await new Promise(resolve => setTimeout(resolve, 1000));
      const status = await checkBackendStatus();
      if (status) break;
      attempts++;
    }
    
    if (attempts >= 10) {
      console.error('Backend failed to start within the timeout period');
      process.exit(1);
    }
  }
  
  // Send credentials to backend
  try {
    console.log('Sending credentials to backend...');
    const result = await sendCredentials(openaiApiKey, googleCredentials);
    console.log('Credentials response:', result);
    
    if (!result.success) {
      console.error('Failed to set credentials:', result.messages.join(', '));
      process.exit(1);
    }
  } catch (error) {
    console.error('Error sending credentials:', error.message);
    process.exit(1);
  }
  
  // Start React app
  const reactProcess = startReactApp();
  
  // Handle process termination
  process.on('SIGINT', () => {
    console.log('Shutting down...');
    if (reactProcess) reactProcess.kill();
    if (backendProcess) {
      process.kill(-backendProcess.pid);
    }
    process.exit(0);
  });
}

main().catch(error => {
  console.error('Error:', error);
  process.exit(1);
});
