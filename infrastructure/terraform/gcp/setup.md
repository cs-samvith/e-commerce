# 🚀 Terraform GCP Automation - Quick Setup

## Prerequisites
- Terraform installed
- gcloud CLI installed
- GCP account with billing enabled

---

## 1. Setup GCP Project

```bash
# Set project ID
PROJECT_ID="your-project-id"
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable container.googleapis.com
gcloud services enable compute.googleapis.com
gcloud services enable iam.googleapis.com
gcloud services enable storage.googleapis.com
```

---

## 2. Create Service Account

```bash
# Create service account
gcloud iam service-accounts create terraform-sa \
  --display-name="Terraform Service Account"

# Set service account email
SA_EMAIL="terraform-sa@${PROJECT_ID}.iam.gserviceaccount.com"
```

---

## 3. Grant Permissions

```bash
# Grant required roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/container.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/compute.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/storage.admin"
```

---

## 4. Create Service Account Key

```bash
# Create and download key
gcloud iam service-accounts keys create terraform-key.json \
  --iam-account=${SA_EMAIL}

# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/terraform-key.json"
```

---

## 5. Create GCS Bucket for State

```bash
# Create bucket
gsutil mb -p ${PROJECT_ID} -l US gs://${PROJECT_ID}-terraform-state

# Enable versioning
gsutil versioning set on gs://${PROJECT_ID}-terraform-state

# Grant service account access
gsutil iam ch serviceAccount:${SA_EMAIL}:roles/storage.objectAdmin \
  gs://${PROJECT_ID}-terraform-state
```

---

## 6. Initialize Terraform

```bash
# Initialize
terraform init

# Validate
terraform validate

# Plan
terraform plan

# Apply
terraform apply
```

---

## 7. For GitHub Actions (Optional)

### Setup Workload Identity

```bash
# Get project number
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")

# Create workload identity pool
gcloud iam workload-identity-pools create "github-pool" \
  --project="${PROJECT_ID}" \
  --location="global" \
  --display-name="GitHub Actions Pool"

# Create provider
gcloud iam workload-identity-pools providers create-oidc "github-provider" \
  --project="${PROJECT_ID}" \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --display-name="GitHub Provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
  --issuer-uri="https://token.actions.githubusercontent.com"

# Bind service account
gcloud iam service-accounts add-iam-policy-binding ${SA_EMAIL} \
  --project="${PROJECT_ID}" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/github-pool/attribute.repository/YOUR_ORG/YOUR_REPO"
```

### Add to GitHub Secrets

```
GCP_WORKLOAD_IDENTITY_PROVIDER=projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/providers/github-provider
GCP_SERVICE_ACCOUNT=terraform-sa@PROJECT_ID.iam.gserviceaccount.com
```

---

## 8. Verify Setup

```bash
# Test authentication
gcloud auth list

# Test terraform
terraform plan

# Check GCS bucket
gsutil ls gs://${PROJECT_ID}-terraform-state/
```

---

## 9. Common Commands

```bash
# Format code
terraform fmt

# Validate config
terraform validate

# Plan changes
terraform plan

# Apply changes
terraform apply

# Destroy resources
terraform destroy

# Check state
terraform state list

# Show outputs
terraform output
```

---

## 10. Troubleshooting

```bash
# Check quotas
gcloud compute project-info describe --project=$PROJECT_ID

# Check permissions
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:${SA_EMAIL}"

# Check APIs
gcloud services list --enabled --project=$PROJECT_ID

# View logs
gcloud logging read "resource.type=gke_cluster" --limit=50
```

---

## Quick Reference

**Required Roles:**
- `roles/container.admin` - GKE management
- `roles/compute.admin` - Compute resources
- `roles/iam.serviceAccountUser` - Service account usage
- `roles/storage.admin` - State storage

**Required APIs:**
- `container.googleapis.com` - GKE
- `compute.googleapis.com` - Compute Engine
- `iam.googleapis.com` - IAM
- `storage.googleapis.com` - Cloud Storage

**State Storage:**
- Bucket: `gs://PROJECT_ID-terraform-state`
- Versioning: Enabled
- Location: US (or your region)

---

## Done! ✅

Your Terraform + GCP automation is ready to use.