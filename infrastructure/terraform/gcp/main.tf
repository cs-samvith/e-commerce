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

  backend "gcs" {
    bucket = "plucky-current-275920-terraform-state"
    prefix = "gke-cluster"
  }

}

# ============================================
# GCP Provider Configuration
# ============================================

provider "google" {
  project = var.project_id
  region  = var.region
}
