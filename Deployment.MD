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
- [Troubleshooting](#troubleshooting)
- [Additional Resources](#additional-resources)

## Architecture Overview

Our application uses a microservices architecture with separate frontend and backend services deployed on Google Kubernetes Engine:

- **Frontend**: React application served via Nginx
- **Backend**: Python Flask API that integrates with OpenAI
- **Infrastructure**: Google Kubernetes Engine with autoscaling
- **Monitoring**: GCP monitoring and Slack notifications

![Architecture Diagram Placeholder]

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

1. **Required Accounts**:
   - Google Cloud Platform account
   - GitHub account (for CI/CD)
   - Slack workspace (for notifications)
   - OpenAI API key

2. **Required Tools**:
   ```bash
   # Install Google Cloud SDK
   curl https://sdk.cloud.google.com | bash
   
   # Install kubectl
   gcloud components install kubectl
   
   # Verify installations
   gcloud --version
   kubectl version
   ```

## Setting Up Your Environment

### GCP Configuration

1. **Authentication Setup**:
   ```bash
   # Login to Google Cloud
   gcloud auth login
   
   # Set your project
   gcloud config set project chatwithdata-451800
   ```

2. **Enable Required APIs**:
   ```bash
   gcloud services enable \
     container.googleapis.com \
     containerregistry.googleapis.com \
     compute.googleapis.com \
     iam.googleapis.com
   ```

3. **Create GKE Cluster**:
   ```bash
   gcloud container clusters create chat-cluster \
     --zone us-central1 \
     --num-nodes 2 \
     --machine-type e2-standard-2 \
     --enable-autoscaling \
     --min-nodes 2 \
     --max-nodes 6
   ```

4. **Configure kubectl**:
   ```bash
   gcloud container clusters get-credentials chat-cluster --zone us-central1
   ```

### Service Account Setup

1. **Create Service Account**:
   ```bash
   gcloud iam service-accounts create gke-deploy-sa \
     --display-name="GKE Deployment Service Account"
   ```

2. **Assign Roles**:
   ```bash
   gcloud projects add-iam-policy-binding chatwithdata-451800 \
     --member="serviceAccount:gke-deploy-sa@chatwithdata-451800.iam.gserviceaccount.com" \
     --role="roles/container.developer"
   
   gcloud projects add-iam-policy-binding chatwithdata-451800 \
     --member="serviceAccount:gke-deploy-sa@chatwithdata-451800.iam.gserviceaccount.com" \
     --role="roles/storage.admin"
   ```

3. **Create Key**:
   ```bash
   gcloud iam service-accounts keys create key.json \
     --iam-account=gke-deploy-sa@chatwithdata-451800.iam.gserviceaccount.com
   ```

### Secrets Management

1. **Create Kubernetes Secrets**:
   ```bash
   # Create OpenAI API key and Slack webhook secret
   kubectl create secret generic app-secrets \
     --from-literal=openai-api-key=YOUR_OPENAI_API_KEY \
     --from-literal=slack-webhook-url=YOUR_SLACK_WEBHOOK_URL
   
   # Create GCP credentials secret
   kubectl create secret generic gcp-credentials \
     --from-file=key.json=/path/to/your/service-account-key.json
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

