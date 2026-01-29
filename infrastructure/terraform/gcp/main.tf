# ============================================
# Terraform Configuration for GCP
# Project: plucky-current-275920
# ============================================

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 7.0"
    }
  }
}

# ============================================
# GCP Provider Configuration
# ============================================

provider "google" {
  project = var.project_id
  region  = var.region
}

# ============================================
# Variables
# ============================================

variable "project_id" {
  description = "GCP Project ID"
  type        = string
  default     = "plucky-current-275920"
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-east5"
}

variable "zone" {
  description = "GCP Zone"
  type        = string
  default     = "us-east5-c"
}

variable "cluster_name" {
  description = "GKE Cluster Name"
  type        = string
  default     = "mygkecluster"
}


variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

# ============================================
# Outputs
# ============================================

output "project_id" {
  value       = var.project_id
  description = "The GCP Project ID"
}

output "cluster_name" {
  value       = google_container_cluster.primary.name
  description = "GKE Cluster Name"
}

output "cluster_endpoint" {
  value       = google_container_cluster.primary.endpoint
  description = "GKE Cluster Endpoint"
  sensitive   = true
}

output "kubectl_command" {
  value       = "gcloud container clusters get-credentials ${google_container_cluster.primary.name} --zone=${var.zone} --project=${var.project_id}"
  description = "Command to configure kubectl"
}