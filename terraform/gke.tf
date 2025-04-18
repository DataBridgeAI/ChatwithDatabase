# Create a GKE cluster
resource "google_container_cluster" "primary" {
  name     = "${var.project_name}-gke-cluster"
  location = var.zone
  
  # We can't create a cluster with no node pool defined, so we create the smallest possible
  # default node pool and immediately delete it.
  remove_default_node_pool = true
  initial_node_count       = 1
  
  network    = google_compute_network.vpc.name
  subnetwork = google_compute_subnetwork.subnet.name
  
  # GKE uses the secondary ranges for pods and services
  ip_allocation_policy {
    cluster_secondary_range_name  = "pods"
    services_secondary_range_name = "services"
  }
  
  # Enable workload identity for secure access to GCP services
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }
}

# Create a separately managed node pool
resource "google_container_node_pool" "primary_nodes" {
  name       = "${var.project_name}-node-pool"
  location   = var.zone
  cluster    = google_container_cluster.primary.name
  node_count = var.node_count

  node_config {
    preemptible  = true
    machine_type = var.machine_type

    # Google recommended labels
    labels = {
      env = var.environment
    }

    # Google recommended metadata
    metadata = {
      disable-legacy-endpoints = "true"
    }
    
    # Set OAuth scopes for the nodes
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
    
    # Use workload identity
    workload_metadata_config {
      mode = "GKE_METADATA"
    }
  }
}