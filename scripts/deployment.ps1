# deployment.ps1
# Set error action preference
$ErrorActionPreference = "Stop"

# Set your GCP project ID and other variables
$PROJECT_ID = "chatwithdata-451800"
$NAMESPACE = "nl-to-sql"

# Connect to your GKE cluster
Write-Host "Connecting to GKE cluster..."
gcloud container clusters get-credentials YOUR_CLUSTER_NAME --zone YOUR_ZONE --project $PROJECT_ID

# Create the namespace if it doesn't exist
Write-Host "Creating namespace if it doesn't exist..."
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Create secrets
Write-Host "Creating secrets..."
kubectl create secret generic app-secrets `
  --namespace=$NAMESPACE `
  --from-literal=gcp-project-id=$PROJECT_ID `
  --dry-run=client -o yaml | kubectl apply -f -

# Apply Kubernetes configurations
Write-Host "Applying Kubernetes configurations..."
kubectl apply -f kubernetes/configmap.yaml --validate=false
kubectl apply -f kubernetes/backend-deployment.yaml --validate=false
kubectl apply -f kubernetes/backend-service.yaml --validate=false
kubectl apply -f kubernetes/frontend-deployment.yaml --validate=false
kubectl apply -f kubernetes/frontend-service.yaml --validate=false
kubectl apply -f kubernetes/ingress.yaml --validate=false

# Wait for deployments to be ready
Write-Host "Waiting for deployments to be ready..."
kubectl rollout status deployment/backend -n $NAMESPACE
kubectl rollout status deployment/frontend -n $NAMESPACE

Write-Host "Deployment completed successfully!"
Write-Host "Getting external IP (this may take a minute)..."
kubectl get ingress -n $NAMESPACE