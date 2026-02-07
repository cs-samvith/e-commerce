# ============================================
# OPTION 1: CHEAPEST GKE CLUSTER
# Estimated Cost: $9-25/month
# ============================================
# Best for: Development, testing, learning
# NOT for: Production workloads
# ============================================

resource "google_container_cluster" "primary" {
  name     = "${var.cluster_name}-cheap"
  location = var.zone #"us-east1-b"  # Zonal cluster (free tier eligible!)

  # We can't create a cluster with no node pool defined, so we create the
  # smallest possible default node pool and immediately delete it.
  remove_default_node_pool = true
  initial_node_count       = 1

  # Network configuration
  network    = "default"
  subnetwork = "default"

  deletion_protection = false

  # Disable expensive features
  logging_service    = "none" # Save ~$10/month
  monitoring_service = "none" # Save ~$10/month

  # IP allocation policy for pods and services
  ip_allocation_policy {
    cluster_ipv4_cidr_block  = "" # Auto-assign
    services_ipv4_cidr_block = "" # Auto-assign
  }

  # Maintenance window (3 AM to minimize impact)
  maintenance_policy {
    daily_maintenance_window {
      start_time = "03:00"
    }
  }

  # Workload Identity (recommended security feature - free)
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  # Resource labels
  resource_labels = {
    environment = var.environment
    managed-by  = "terraform"
    cost-tier   = "cheap"
  }
}

# ============================================
# Cheap Node Pool - Spot VMs
# ============================================

resource "google_container_node_pool" "cheap_nodes" {
  name     = "c-node-pool"
  location = var.zone
  cluster  = google_container_cluster.primary.name

  # Autoscaling - scale down to 1 when idle
  autoscaling {
    min_node_count = 1 # Minimum to keep costs down
    max_node_count = 2 # Maximum for burst capacity
  }

  # Node configuration
  node_config {
    # SPOT VMs = 91% discount! (but can be preempted with 30s notice)
    spot = true

    # Smallest usable machine type
    machine_type = var.node_sku # 2 vCPU, 4GB RAM (~$9/month with spot pricing)

    # Minimal disk
    disk_size_gb = 20
    disk_type    = "pd-standard" # Standard HDD (cheapest)

    # Container-Optimized OS
    image_type = "COS_CONTAINERD"

    # OAuth scopes
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    # Labels
    labels = {
      environment = var.environment
      node-type   = "spot"
      cost-tier   = "cheap"
    }

    # Metadata
    metadata = {
      disable-legacy-endpoints = "true"
    }

    # Network tags (for firewall rules)
    tags = ["gke-node", "${var.cluster_name}-node"]

    # Workload Identity
    workload_metadata_config {
      mode = "GKE_METADATA"
    }

    # Shielded instance config (security)
    shielded_instance_config {
      enable_secure_boot          = true
      enable_integrity_monitoring = true
    }
  }

  # Node management
  management {
    auto_repair  = true
    auto_upgrade = true
  }

  # Upgrade settings
  upgrade_settings {
    max_surge       = 1
    max_unavailable = 0
  }
}

# ============================================
# Cost Information
# ============================================

output "cheap_cluster_cost_breakdown" {
  value = <<-EOT
  
  ╔════════════════════════════════════════════════════════════════╗
  ║              CHEAP CLUSTER - COST BREAKDOWN                     ║
  ╚════════════════════════════════════════════════════════════════╝
  
  Cluster Management Fee:    $0.00/month (covered by free tier)
  1x e2-medium Spot VM:      ~$9.00/month
  3x e2-medium Spot VMs:     ~$25.00/month (max autoscale)
  
  TOTAL: $9-25/month depending on load
  
  ╔════════════════════════════════════════════════════════════════╗
  ║                    FEATURES & TRADEOFFS                         ║
  ╚════════════════════════════════════════════════════════════════╝
  
  ✓ Spot VMs (91% discount vs regular VMs)
  ✓ Zonal cluster (free tier eligible)
  ✓ Autoscaling 1-3 nodes
  ✓ Minimal disk (10GB)
  ✓ Logging/monitoring disabled
  
  ⚠ Spot VMs can be preempted with 30s notice
  ⚠ No high availability (single zone)
  ⚠ Not suitable for production
  ⚠ Perfect for: dev, testing, demos, learning
  
  EOT
}