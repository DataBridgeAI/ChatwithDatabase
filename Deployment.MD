# Cloud Deployment Guide
This document outlines the deployment process for our application on Google Cloud Platform (GCP) using Google Kubernetes Engine (GKE).

## 1. Deployment Service

### Google Kubernetes Engine (GKE)
Our application is deployed using GKE with the following components:

#### Frontend Deployment
- React application served via Nginx
- 2 replicas for high availability
- Resource configuration:
  - Requests: 250m CPU, 512Mi Memory
  - Limits: 500m CPU, 1Gi Memory

#### Backend Deployment
- Python Flask API
- 2 replicas for high availability
- Resource limits: 500m CPU
- Includes mounted GCP credentials for service authentication

#### Load Balancing Configuration
- **Internal Load Balancing**:
  - Service type: ClusterIP for internal communication
  - Backend services communicate through internal DNS
  - Automatic health checks and pod distribution
  
- **External Load Balancing**:
  - Service type: LoadBalancer
  - Cloud Load Balancer automatically provisioned
  - SSL termination at load balancer level
  - Session affinity: Client IP-based
  - Health checks every 30 seconds
  - Automatic failover to healthy pods

## 2. Deployment Automation

Our deployment process is fully automated using GitHub Actions workflow (`.github/workflows/gke-deploy.yml`).

### Continuous Integration
- Runs Python tests with coverage reporting
- Validates model performance
- Executes prompt validation checks

### Continuous Deployment
- Builds Docker images for frontend and backend
- Pushes images to Google Container Registry (GCR)
- Updates Kubernetes deployments with new images
- Creates/updates Kubernetes secrets
- Monitors deployment status via Slack notifications

## 3. Connection to Repository

### GitHub Integration
- Automated deployments triggered on push to `deployment-div` branch
- GitHub Actions workflow configured for CI/CD pipeline
- Secrets managed through GitHub Secrets:
  - `GCP_CREDENTIALS`
  - `OPENAI_API_KEY`
  - `SLACK_WEBHOOK`

### Monitoring and Logging
- Cloud Monitoring for metrics collection
- Cloud Logging for centralized logs
- Slack notifications for deployment status

## 4. Step-by-Step Replication Guide

### Prerequisites
1. Install required tools:
   ```bash
   # Install Google Cloud SDK
   curl https://sdk.cloud.google.com | bash
   
   # Install kubectl
   gcloud components install kubectl
   ```

2. Configure GCP authentication:
   ```bash
   gcloud auth login
   gcloud config set project chatwithdata-451800
   ```

### Environment Setup
1. Enable required GCP APIs:
   ```bash
   gcloud services enable \
     container.googleapis.com \
     containerregistry.googleapis.com
   ```

2. Create GKE cluster:
   ```bash
   gcloud container clusters create chat-cluster \
     --zone us-central1 \
     --num-nodes 2 \
     --machine-type e2-standard-2
   ```

3. Configure kubectl:
   ```bash
   gcloud container clusters get-credentials chat-cluster --zone us-central1
   ```

### Repository Setup
1. Fork/clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. Configure GitHub Secrets:
   - `GCP_CREDENTIALS`: Service account JSON key
   - `OPENAI_API_KEY`: OpenAI API key
   - `SLACK_WEBHOOK`: Slack webhook URL for notifications

### Deployment Process
1. Trigger deployment:
   ```bash
   git push origin deployment-div
   ```
   This will automatically:
   - Run tests
   - Build Docker images
   - Deploy to GKE

2. Verify deployment:
   ```bash
   # Check pod status
   kubectl get pods
   
   # Check services
   kubectl get services
   
   # View logs
   kubectl logs deployment/frontend
   kubectl logs deployment/backend
   ```

3. Access the application:
   ```bash
   # Get the external IP
   kubectl get service frontend-service
   ```
# Comprehensive Cloud Deployment Guide

This guide provides detailed instructions for deploying our chat application on Google Cloud Platform (GCP) using Google Kubernetes Engine (GKE).

## Table of Contents
- [Architecture Overview](#architecture-overview)
- [Infrastructure Components](#infrastructure-components)
- [Prerequisites](#prerequisites)
- [Setting Up Your Environment](#setting-up-your-environment)
- [Deployment Process](#deployment-process)
- [CI/CD Pipeline](#cicd-pipeline)
- [Kubernetes Resource Configuration](#kubernetes-resource-configuration)
- [Verification and Testing](#verification-and-testing)
- [Scaling and Performance](#scaling-and-performance)
- [Monitoring](#monitoring)
- [Model Monitoring and Retraining](#model-monitoring-and-retraining)
- [Troubleshooting](#troubleshooting)
- [Video Demonstration](#video-demonstration)
- [Additional Resources](#additional-resources)

## Architecture Overview

Our application uses a microservices architecture with separate frontend and backend services deployed on Google Kubernetes Engine:

- **Frontend**: React application served via Nginx
- **Backend**: Python Flask API that integrates with OpenAI
- **Infrastructure**: Google Kubernetes Engine with autoscaling
- **Monitoring**: GCP monitoring and Slack notifications

### System Architecture Diagram
![MLOps Architecture](/src/assets/architecture_mlops.png)

The architecture consists of four key layers:
1. **User Interaction Layer**: Handles frontend, authentication, and data visualization
2. **Backend Processing Layer**: Manages query processing, AI operations (GPT-4/LangChain), and SQL generation
3. **Data Pipeline Layer**: Orchestrates data workflows using Apache Airflow for schema management and model operations
4. **Infrastructure Layer**: Provides foundational services through GKE, BigQuery, Vertex AI, and CI/CD pipelines

## Infrastructure Components

### Frontend Components
- **Deployment**: 2 replicas for high availability
- **Resource Allocation**:
  - Requests: 250m CPU, 512Mi Memory
  - Limits: 500m CPU, 1Gi Memory
- **Image**: `gcr.io/chatwithdata-451800/chatapp-ui:latest`
- **Container Port**: 80
- **Environment Variables**: Configured with API URL and API keys

### Backend Components
- **Deployment**: 2 replicas for high availability
- **Resource Allocation**:
  - Requests: 250m CPU
  - Limits: 500m CPU
- **Image**: `gcr.io/chatwithdata-451800/chatapp-api:latest`
- **Container Port**: 5001
- **Secrets**: OpenAI API key, GCP credentials, Slack webhook
- **Environment Variables**: Configured for API integration

### Networking
- **Frontend Service**: LoadBalancer type with external IP
- **Backend Service**: ClusterIP type for internal communication
- **Backend Config**: Health checks, connection draining, and session affinity

### Autoscaling
- **Frontend HPA**:
  - Min Replicas: 2
  - Max Replicas: 10
  - Target CPU Utilization: 50%
  - Scale Down: Max 1 pod per minute with 120s window
  - Scale Up: Max 2 pods per minute with 60s window

- **Backend HPA**:
  - Min Replicas: 2
  - Max Replicas: 10
  - Target CPU Utilization: 50%
  - Scale Down: Max 1 pod per minute with 120s window
  - Scale Up: Max 2 pods per minute with 60s window

## Prerequisites

### 1. Required Tools and Versions
- Google Cloud SDK (v400.0.0 or later)
- kubectl (v1.25.0 or later)
- Docker (v20.10.0 or later)
- Git (v2.30.0 or later)
- Node.js (v16.x or later) for frontend development
- Python (v3.9 or later) for backend development

### 2. Access Requirements
- Google Cloud Platform Account with:
  - Owner or Editor role
  - Billing enabled
  - Following APIs activated:
    - Container Registry API
    - Kubernetes Engine API
    - Cloud Build API
    - Secret Manager API

### 3. Required Credentials
- GCP Service Account with:
  - Kubernetes Engine Admin
  - Storage Admin
  - Secret Manager Admin
  - Service Account User
- OpenAI API key
- Slack Webhook URL (for notifications)

### 4. Local Environment Variables
```bash
# Required Environment Variables
export PROJECT_ID="chatwithdata-451800"
export REGION="us-central1"
export CLUSTER_NAME="chatapp-cluster"
export GITHUB_REPO="your-repo-name"
```

## Setting Up Your Environment

### 1. GCP Project Configuration
```bash
# Login to Google Cloud
gcloud auth login

# Set project and region
gcloud config set project ${PROJECT_ID}
gcloud config set compute/region ${REGION}

# Enable required APIs
gcloud services enable \
  container.googleapis.com \
  containerregistry.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com
```

### 2. Kubernetes Cluster Setup
```bash
# Create GKE cluster
gcloud container clusters create ${CLUSTER_NAME} \
  --region ${REGION} \
  --num-nodes 3 \
  --machine-type e2-standard-2 \
  --enable-autoscaling \
  --min-nodes 3 \
  --max-nodes 6

# Get cluster credentials
gcloud container clusters get-credentials ${CLUSTER_NAME} \
  --region ${REGION}
```

### 3. Container Registry Setup
```bash
# Configure Docker authentication
gcloud auth configure-docker

# Grant required permissions
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member serviceAccount:${SERVICE_ACCOUNT} \
  --role roles/storage.admin
```

### 4. Secret Management Setup
```bash
# Create Kubernetes secrets
kubectl create secret generic app-secrets \
  --from-literal=openai-api-key=${OPENAI_API_KEY} \
  --from-literal=slack-webhook-url=${SLACK_WEBHOOK_URL}

# Create service account key secret
kubectl create secret generic gcp-credentials \
  --from-file=key.json=/path/to/service-account-key.json
```

### 5. Development Environment Setup

#### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create environment file
cat << EOF > .env
REACT_APP_API_URL=http://localhost:5001
EOF
```

#### Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Create environment file
cat << EOF > .env
OPENAI_API_KEY=${OPENAI_API_KEY}
GOOGLE_APPLICATION_CREDENTIALS=path/to/key.json
EOF
```

### 6. Verification Steps
```bash
# Verify GCP configuration
gcloud config list

# Verify kubectl configuration
kubectl config current-context

# Verify cluster access
kubectl get nodes

# Test Docker configuration
docker pull gcr.io/google-samples/hello-app:1.0
```

## Deployment Process

### Manual Deployment

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. **Deploy Kubernetes Resources**:
   ```bash
   # Apply all configuration files
   kubectl apply -f k8s/
   ```

   Or apply individual files:
   ```bash
   kubectl apply -f k8s/backend-config.yaml
   kubectl apply -f k8s/backend-deployment.yaml
   kubectl apply -f k8s/backend-hpa.yaml
   kubectl apply -f k8s/frontend-deployment.yaml
   kubectl apply -f k8s/frontend-hpa.yaml
   kubectl apply -f k8s/services.yaml
   ```

## CI/CD Pipeline

Our deployment process is fully automated using GitHub Actions. The workflow is defined in `.github/workflows/gke-deploy.yml`.

### Workflow Components

1. **Continuous Integration**:
   - Runs Python tests with coverage reporting
   - Validates model performance
   - Executes prompt validation checks

2. **Continuous Deployment**:
   - Builds Docker images for frontend and backend
   - Pushes images to Google Container Registry (GCR)
   - Updates Kubernetes deployments with new images
   - Creates/updates Kubernetes secrets
   - Monitors deployment status via Slack notifications

### GitHub Secrets Setup

1. **Configure GitHub Secrets**:
   - `GCP_CREDENTIALS`: Service account JSON key (content of key.json)
   - `OPENAI_API_KEY`: OpenAI API key
   - `SLACK_WEBHOOK`: Slack webhook URL for notifications

2. **Trigger Deployment**:
   - Push to the `deployment-div` branch
   ```bash
   git push origin deployment-div
   ```
   - GitHub Actions workflow will automatically run

## Kubernetes Resource Configuration

### Backend Config (backend-config.yaml)
```yaml
apiVersion: cloud.google.com/v1
kind: BackendConfig
metadata:
  name: my-backendconfig
spec:
  healthCheck:
    checkIntervalSec: 15
    timeoutSec: 5
    healthyThreshold: 2
    unhealthyThreshold: 2
    type: HTTP
    requestPath: /health
  connectionDraining:
    drainingTimeoutSec: 60
  sessionAffinity:
    affinityType: GENERATED_COOKIE
    affinityCookieTtlSec: 3600
```

### Backend Deployment (backend-deployment.yaml)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: gcr.io/chatwithdata-451800/chatapp-api:latest
        ports:
        - containerPort: 5001
        resources:
          requests:
            cpu: "250m"
          limits:
            cpu: "500m"
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: openai-api-key
        - name: GOOGLE_APPLICATION_CREDENTIALS
          value: "/var/secrets/google/key.json"
        - name: SLACK_WEBHOOK_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: slack-webhook-url
        volumeMounts:
        - name: google-cloud-key
          mountPath: /var/secrets/google
          readOnly: true
      volumes:
      - name: google-cloud-key
        secret:
          secretName: gcp-credentials
```

### Backend HPA (backend-hpa.yaml)
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 50
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 120
      policies:
        - type: Pods
          value: 1
          periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
        - type: Pods
          value: 2
          periodSeconds: 60
```

### Services (services.yaml)
```yaml
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
  annotations:
    cloud.google.com/neg: '{"ingress": true}'
    cloud.google.com/backend-config: '{"default": "my-backendconfig"}'
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 80
  selector:
    app: frontend
---
apiVersion: v1
kind: Service
metadata:
  name: backend-service
  annotations:
    cloud.google.com/neg: '{"ingress": true}'
spec:
  selector:
    app: backend
  ports:
    - name: http
      protocol: TCP
      port: 5001
      targetPort: 5001
  type: ClusterIP
```

## Verification and Testing

1. **Check Deployment Status**:
   ```bash
   # Check pod status
   kubectl get pods
   
   # Check services
   kubectl get services
   
   # View deployments
   kubectl get deployments
   ```

2. **Access the Application**:
   ```bash
   # Get the external IP
   kubectl get service frontend-service
   ```
   Access the application at `http://<EXTERNAL-IP>`

### Monitoring and Verification
1. Check deployment status:
   - Monitor GitHub Actions workflow
   - Check Slack notifications
   - View GKE dashboard in Google Cloud Console

2. Verify functionality:
   - Test API endpoints
   - Confirm frontend accessibility
   - Validate model inference

3. Monitor logs:
   ```bash
   # Stream logs
   kubectl logs -f deployment/backend
   ```

### Troubleshooting
1. Pod issues:
   ```bash
   kubectl describe pod <pod-name>
   ```

2. Service issues:
   ```bash
   kubectl describe service frontend-service
   kubectl describe service backend-service
   ```

3. Common fixes:
   - Check pod logs for errors
   - Verify secret configuration
   - Confirm resource limits
   - Check network policies

## Additional Resources
- [GKE Documentation](https://cloud.google.com/kubernetes-engine/docs)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Cloud Load Balancing Documentation](https://cloud.google.com/load-balancing/docs)

3. **Test API Endpoints**:
   ```bash
   # Test backend API health endpoint
   curl http://<EXTERNAL-IP>/api/health
   ```

## Scaling and Performance

### Current Scaling Configuration

Our application is configured with Horizontal Pod Autoscalers (HPAs) that automatically adjust the number of pods based on CPU utilization:

1. **Frontend Scaling**:
   - Scales between 2-10 pods
   - Targets 50% CPU utilization
   - Adds up to 2 pods per minute
   - Removes 1 pod per minute after 120s stable period

2. **Backend Scaling**:
   - Scales between 2-10 pods
   - Targets 50% CPU utilization
   - Adds up to 2 pods per minute
   - Removes 1 pod per minute after 120s stable period

### Performance Monitoring

Monitor scaling behavior with:
```bash
# Check HPA status
kubectl get hpa

# Monitor CPU usage
kubectl top pods
```

## Monitoring

1. **View Logs**:
   ```bash
   # Stream frontend logs
   kubectl logs -f deployment/frontend
   
   # Stream backend logs
   kubectl logs -f deployment/backend
   ```

2. **Deployment Status**:
   ```bash
   # Check deployment status
   kubectl rollout status deployment/frontend
   kubectl rollout status deployment/backend
   ```

3. **Resource Usage**:
   ```bash
   # Check pod resource usage
   kubectl top pods
   
   # Check node resource usage
   kubectl top nodes
   ```

4. **Slack Notifications**:
   - Deployment events
   - Error alerts
   - Scaling events

5. **Google Cloud Monitoring Integration**:
   - Implemented via `GCPMonitoring` class from `src/monitoring_utils.py`
   - Provides comprehensive application monitoring:
     ```python
     # Example from app.py
     monitor.log_event("Query validation passed", severity="INFO")
     monitor.log_event("Query validation failed", severity="ERROR")
     ```
   - Metrics tracked:
     - Query execution success/failure rates
     - API response times
     - System performance metrics
     - Resource utilization
   - Custom dashboards in Google Cloud Console for:
     - Application performance
     - System health
     - Error tracking
   - Alert policies configured for:
     - Error rate thresholds
     - Performance degradation
     - Resource utilization warnings

   ### Cloud Monitoring Visualizations
   These are some of the cloud monitoring visuals for tracking database or API query performance metrics with visualization of execution times, query volume, and related logs to help identify performance issues or anomalies:

   ![](/src/assets/gcloudmonitoring_1.jpg)
   ![](/src/assets/gcloudmonitoring_2.jpg)

## Model Monitoring and Retraining

### 1. Automated Monitoring System

Our monitoring system leverages both MLflow and GCP's monitoring capabilities to track model performance and trigger retraining when necessary.

#### MLflow Implementation
The core monitoring logic is implemented in `src/monitoring/mlflow_config.py` through the `QueryTracker` class. This system:
- Tracks query execution metrics including processing times, complexity scores, and success rates
- Maintains experiment versioning and parameter tracking
- Stores performance metrics for historical analysis
- Enables A/B testing of different prompt versions

#### GCP Monitoring Integration
Implemented via `src/monitoring_utils.py`, our GCP monitoring:
- Provides real-time performance tracking through custom metrics
- Integrates with Cloud Monitoring for visualization
- Manages alert policies for performance degradation
- Maintains audit logs for compliance

### 2. Prompt Learning System

Our prompt learning system, implemented in `PromptValidation/prompt_monitor.py`, continuously improves prompt performance through:

#### Feedback Analysis Pipeline
The feedback analysis system (`feedback/feedback_manager.py`):
- Collects and processes user feedback
- Analyzes query patterns and failure modes
- Maintains a feedback database for continuous learning
- Generates improvement suggestions

#### Automated Detection Systems
Pattern recognition is handled by `promptfilter/semantic_search.py`, which:
- Identifies common failure patterns
- Detects schema changes
- Analyzes query complexity
- Monitors for potential biases

### 3. Vector Embeddings System

Our dual embedding approach (`src/embeddings/`) uses:
1. Schema embeddings via Vertex AI
2. Feedback embeddings via sentence-transformers

This system enables:
- Semantic understanding of database structure
- Efficient query similarity matching
- Historical pattern analysis
- Continuous learning from user interactions

### 4. Performance Monitoring

The monitoring dashboard (`src/monitoring/dashboard.py`) provides:
- Real-time performance metrics
- Historical trend analysis
- Resource utilization tracking
- Alert management

### 5. Bias Detection and Mitigation

Implemented in `PromptValidation/bias_checker.py`, our system:
- Performs automated bias detection
- Implements content filtering
- Maintains fairness metrics
- Provides mitigation strategies

### 6. Continuous Improvement Pipeline

Our improvement pipeline (`DataPipeline/dags/prompt_learning_dag.py`):
- Runs daily analysis of performance metrics
- Generates optimization recommendations
- Updates prompt templates automatically
- Maintains version control of prompts

### 7. Validation and Testing

The validation system (`src/validation/`) ensures:
- Semantic accuracy of generated queries
- Performance benchmarking
- Security compliance
- Resource optimization

For detailed implementation examples and configuration options, refer to the respective source files in our codebase.

## Troubleshooting

### Common Issues and Solutions

1. **Pods Not Starting**:
   ```bash
   # Check pod details
   kubectl describe pod <pod-name>
   ```
   Look for errors in the Events section at the bottom

2. **Service Unavailable**:
   ```bash
   # Check service details
   kubectl describe service frontend-service
   ```
   Verify selector matches pod labels

3. **Image Pull Errors**:
   - Verify GCP credentials are correctly configured
   - Check image path in deployment files
   - Try pulling the image manually:
     ```bash
     gcloud auth configure-docker
     docker pull gcr.io/chatwithdata-451800/chatapp-api:latest
     ```

4. **Application Errors**:
   ```bash
   # Check application logs
   kubectl logs -f deployment/backend
   ```
   Look for application-specific error messages

5. **Scaling Issues**:
   ```bash
   # Check HPA details
   kubectl describe hpa backend-hpa
   ```
   Look for events and status conditions

6. **Secret Errors**:
   ```bash
   # Verify secrets exist
   kubectl get secrets
   ```
   Ensure secret names match those referenced in deployments

### Recovery Procedures

1. **Rollback Deployment**:
   ```bash
   kubectl rollout undo deployment/backend
   ```

2. **Restart Pods**:
   ```bash
   kubectl rollout restart deployment/backend
   ```

3. **Scale Manually**:
   ```bash
   kubectl scale deployment/backend --replicas=3
   ```

## Video Demonstration

### Deployment Walkthrough Video
Watch our comprehensive deployment walkthrough: [Deployment Demo Video](https://drive.google.com/file/d/1OaEGRmYXp21n4vjQHc4T1E_A-K1mrI5f/view?usp=sharing)

The video covers:

1. **Deployment Process**
   - Kubernetes cluster setup
   - Secret configuration
   - Pipeline trigger
   - Deployment verification

2. **Validation Steps**
   - Health checks
   - Testing
   - Monitoring setup
   - Log verification

