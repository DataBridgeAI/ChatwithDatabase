provider "google" {
  project = var.project_id
  region  = var.region
}

# Enable required APIs
resource "google_project_service" "services" {
  for_each = toset([
    "container.googleapis.com",    # GKE
    "composer.googleapis.com",     # Cloud Composer
    "artifactregistry.googleapis.com", # Artifact Registry
    "monitoring.googleapis.com",   # Cloud Monitoring
    "logging.googleapis.com",      # Cloud Logging
    "cloudbuild.googleapis.com"    # Cloud Build
  ])
  
  service            = each.key
  disable_on_destroy = false
}

# Create a VPC network
resource "google_compute_network" "vpc" {
  name                    = "${var.project_name}-vpc"
  auto_create_subnetworks = false
  depends_on              = [google_project_service.services]
}

# Create subnets
resource "google_compute_subnetwork" "subnet" {
  name          = "${var.project_name}-subnet"
  region        = var.region
  network       = google_compute_network.vpc.name
  ip_cidr_range = "10.0.0.0/16"
  
  # Secondary IP ranges for GKE pods and services
  secondary_ip_range {
    range_name    = "pods"
    ip_cidr_range = "10.1.0.0/16"
  }
  
  secondary_ip_range {
    range_name    = "services"
    ip_cidr_range = "10.2.0.0/16"
  }
}

# Create a static IP for the ingress
resource "google_compute_global_address" "ingress_ip" {
  name = "${var.project_name}-ingress-ip"
}

# Output important values
output "vpc_name" {
  value = google_compute_network.vpc.name
}

output "subnet_name" {
  value = google_compute_subnetwork.subnet.name
}

output "ingress_ip" {
  value = google_compute_global_address.ingress_ip.address
}