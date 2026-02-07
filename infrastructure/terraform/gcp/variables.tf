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

variable "node_sku" {
  description = "Node Sku"
  type        = string
  default     = "e2-standard-2"
}
