# Set your GCP project ID
$PROJECT_ID = "chatwithdata-451800"  # Replace with your actual project ID
$REGISTRY = "gcr.io/$PROJECT_ID"
$TAG = "latest"

# Build and push backend
Write-Host "Building backend image..."
Set-Location -Path src
docker build -t "$REGISTRY/backend:$TAG" .
docker push "$REGISTRY/backend:$TAG"
Set-Location -Path ..

# Build and push frontend
Write-Host "Building frontend image..."
Set-Location -Path frontend
docker build -t "$REGISTRY/frontend:$TAG" .
docker push "$REGISTRY/frontend:$TAG"
Set-Location -Path ..