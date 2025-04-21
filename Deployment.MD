# Cloud Deployment Guide
This document outlines the deployment process for our application on Google Cloud Platform (GCP) using Google Kubernetes Engine (GKE).
## 1. Deployment Service
### Google Kubernetes Engine (GKE)
Our application is deployed using GKE with the following components:
- **Frontend Deployment**: React application served via Nginx  - 2 replicas for high availability
  - Resource limits: 500m CPU, 1Gi Memory  - Resource requests: 250m CPU, 512Mi Memory
- **Backend Deployment**: Python Flask API
  - 2 replicas for high availability  - Resource limits: 500m CPU
  - Includes mounted GCP credentials for service authentication
## 2. Deployment Automation
Our deployment process is fully automated using GitHub Actions workflow (`.github/workflows/gke-deploy.yml`). The automation handles:
### Continuous Integration- Runs Python tests with coverage reporting
- Validates model performance- Executes prompt validation checks
### Continuous Deployment
- Builds Docker images for frontend and backend- Pushes images to Google Container Registry (GCR)
- Updates Kubernetes deployments with new images- Creates/updates Kubernetes secrets
- Monitors deployment status via Slack notifications
## 3. Step-by-Step Replication Guide
### Prerequisites1. Install required tools:
   ```bash   # Install Google Cloud SDK
   curl https://sdk.cloud.google.com | bash   
   # Install kubectl   gcloud components install kubectl
   ```
2. Configure GCP authentication:   ```bash
   gcloud auth login   gcloud config set project chatwithdata-451800
   ```
### Environment Setup
1. Enable required GCP APIs:   ```bash
   gcloud services enable \     container.googleapis.com \
     containerregistry.googleapis.com   ```
2. Create GKE cluster:
   ```bash   gcloud container clusters create chat-cluster \
     --zone us-central1 \     --num-nodes 2 \
     --machine-type e2-standard-2   ```
3. Configure kubectl:
   ```bash   gcloud container clusters get-credentials chat-cluster --zone us-central1
   ```
### Repository Setup
1. Fork/clone the repository:   ```bash
   git clone <repository-url>   cd <repository-name>
   ```
2. Configure GitHub Secrets:   - `GCP_CREDENTIALS`: Service account JSON key
   - `OPENAI_API_KEY`: OpenAI API key   - `SLACK_WEBHOOK`: Slack webhook URL for notifications
### Deployment Process
1. Trigger deployment:
   ```bash   git push origin deployment-div
   ```   This will automatically:
   - Run tests   - Build Docker images
   - Deploy to GKE
2. Verify deployment:   ```bash
   # Check pod status   kubectl get pods
      # Check services
   kubectl get services   
   # View logs   kubectl logs deployment/frontend
   kubectl logs deployment/backend   ```
3. Access the application:
   ```bash   # Get the external IP
   kubectl get service frontend-service   ```
   Access the application at `http://<EXTERNAL-IP>`
### Monitoring and Verification
1. Check deployment status:   - Monitor GitHub Actions workflow
   - Check Slack notifications   - View GKE dashboard in Google Cloud Console
2. Verify functionality:
   - Test API endpoints   - Confirm frontend accessibility
   - Validate model inference
3. Monitor logs:   ```bash
   # Stream logs   kubectl logs -f deployment/backend
   ```
### Troubleshooting
1. Pod issues:   ```bash
   kubectl describe pod <pod-name>   ```
2. Service issues:
   ```bash   kubectl describe service frontend-service
   kubectl describe service backend-service   ```
3. Common fixes:
   - Check pod logs for errors   - Verify secret configuration
   - Confirm resource limits   - Check network policies
## Additional Resources
- [GKE Documentation](https://cloud.google.com/kubernetes-engine/docs)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- Project-specific documentation in `src/README.md`

















































































