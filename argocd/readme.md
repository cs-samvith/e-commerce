# **Complete CI/CD Pipeline Summary**

Here's a comprehensive overview of your end-to-end automated deployment pipeline:

---

## **Architecture Overview**

```
Developer Push → GitHub Actions → Docker Hub → ArgoCD Image Updater → Git Commit → ArgoCD → GKE Cluster
```

---

## **Components & Their Roles**

### **1. GitHub Repository**
**Location:** `https://github.com/cs-samvith/e-commerce`

**Contains:**
- `/services/` - Application source code (frontend, product, user services)
- `/kubernetes/02-services/` - Kubernetes manifests (deployment.yaml, service.yaml, kustomization.yaml)
- `/.github/workflows/` - GitHub Actions CI pipeline

**Role:** Source of truth for both application code and infrastructure config

---

### **2. GitHub Actions (CI Pipeline)**
**File:** `.github/workflows/build-push.yml`

**Triggers:** On push to `main` branch

**What it does:**
1. Checks out code
2. Builds Docker images for each service
3. Tags images with:
   - Short SHA (7 chars): `abc123d`
   - `latest` tag
4. Pushes to Docker Hub

**Output:** 
```
docker.io/samvidocker/ecommerce-frontend-service:abc123d
docker.io/samvidocker/ecommerce-product-service:abc123d
docker.io/samvidocker/ecommerce-user-service:abc123d
```

**Key Point:** CI pipeline does NOT update Kubernetes manifests - that's Image Updater's job!

---

### **3. Docker Hub**
**URL:** `https://hub.docker.com/u/samvidocker`

**Role:** Container registry that stores your Docker images

**Images:**
- `ecommerce-frontend-service`
- `ecommerce-product-service`
- `ecommerce-user-service`

**Note:** Using 30-minute polling interval to avoid rate limits (200 pulls per 6 hours on free tier)

---

### **4. ArgoCD Image Updater**
**Location:** Running in `argocd` namespace on GKE

**What it does:**
1. **Polls Docker Hub** every 30 minutes
2. **Checks for new tags** matching regex `^[a-f0-9]{7}$`
3. **Finds latest tag** (most recent 7-char SHA)
4. **Updates `kustomization.yaml`** in Git:
   ```yaml
   images:
     - name: docker.io/samvidocker/ecommerce-frontend-service
       newTag: abc123d  # ← Updates this
   ```
5. **Commits to GitHub** with message like "Update frontend-service to abc123d"

**Configuration:**
- Git credentials: `git-creds` secret (GitHub token)
- Docker Hub credentials: `dockerhub-pull-secret` secret
- Config: `argocd-image-updater-config` ConfigMap

**Key Point:** Maintains GitOps - Git remains single source of truth

---

### **5. ArgoCD (CD Platform)**
**Location:** Running in `argocd` namespace on GKE

**What it does:**
1. **Watches Git repository** for changes
2. **Detects** when Image Updater commits new tag
3. **Syncs automatically** (every 3 minutes or on Git change)
4. **Applies Kustomize manifests** to cluster
5. **Deploys new version** of the service

**Applications Managed:**
- `frontend-service` → `ecommerce` namespace
- `product-service` → `ecommerce` namespace
- `user-service` → `ecommerce` namespace

**Sync Policy:**
- Automated: Yes
- Self-heal: Yes (reverts manual cluster changes)
- Prune: Yes (removes resources deleted from Git)

**Key Point:** Ensures cluster state matches Git exactly (GitOps principle)

---

### **6. Google Kubernetes Engine (GKE)**
**Cluster:** Your GKE cluster

**Namespaces:**
- `argocd` - ArgoCD and Image Updater
- `ecommerce` - Your application services

**Running Services:**
- frontend-service (2 replicas)
- product-service (replicas)
- user-service (replicas)

**Key Point:** The actual runtime environment for your applications

---

## **Complete Flow Diagram**

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: Developer Pushes Code                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ GitHub Repository (cs-samvith/e-commerce)                        │
│ - /services/frontend-service/                                    │
│ - /kubernetes/02-services/frontend-service/                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: GitHub Actions CI Pipeline                              │
│ - Build Docker image                                             │
│ - Tag with SHORT_SHA (abc123d)                                   │
│ - Tag with 'latest'                                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Docker Hub (samvidocker/ecommerce-frontend-service)             │
│ Tags: abc123d, latest                                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: ArgoCD Image Updater (polls every 30 min)               │
│ 1. Query Docker Hub API for new tags                            │
│ 2. Filter tags matching ^[a-f0-9]{7}$                           │
│ 3. Find latest tag: abc123d                                      │
│ 4. Compare with current tag in Git                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ (if new tag found)
┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: Image Updater Updates Git                               │
│ - Updates kustomization.yaml: newTag: abc123d                   │
│ - Commits: "Update frontend-service to abc123d"                 │
│ - Pushes to main branch                                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ GitHub Repository (updated)                                      │
│ kubernetes/02-services/frontend-service/kustomization.yaml       │
│ images:                                                          │
│   - name: docker.io/samvidocker/ecommerce-frontend-service      │
│     newTag: abc123d  ← UPDATED                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 5: ArgoCD Detects Git Change                               │
│ - Polls Git every 3 minutes                                      │
│ - Detects new commit                                             │
│ - Determines cluster is out of sync                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 6: ArgoCD Syncs to Cluster                                 │
│ 1. Runs 'kubectl kustomize' on manifests                        │
│ 2. Applies resulting YAML to GKE                                │
│ 3. Kubernetes performs rolling update                            │
│ 4. Old pods terminated, new pods created                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ GKE Cluster (ecommerce namespace)                               │
│ frontend-service: abc123d (2 replicas running)                   │
│ - Pods with new image running                                    │
│ - Service routes traffic to new pods                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## **Timeline Example**

Let's trace a single deployment:

| Time | Event | Component | Action |
|------|-------|-----------|--------|
| **10:00 AM** | Developer pushes code | GitHub | Code committed to `main` |
| **10:01 AM** | Build starts | GitHub Actions | Builds Docker image |
| **10:03 AM** | Image pushed | Docker Hub | Image tagged as `abc123d` available |
| **10:30 AM** | Poll cycle | Image Updater | Checks Docker Hub, finds new tag `abc123d` |
| **10:31 AM** | Git updated | Image Updater | Commits new tag to Git: `newTag: abc123d` |
| **10:32 AM** | Change detected | ArgoCD | Detects Git commit, marks app as "OutOfSync" |
| **10:32 AM** | Sync triggered | ArgoCD | Applies new manifest to cluster |
| **10:33 AM** | Rolling update | Kubernetes | Creates new pods with `abc123d` image |
| **10:34 AM** | Deployment complete | GKE | New version running, old pods terminated |

**Total time: ~34 minutes** (mostly waiting for Image Updater's 30-min poll)

---

## **Key Files in Your Repository**

### **CI/CD Configuration:**
```
.github/workflows/build-push.yml          # GitHub Actions build pipeline
```

### **Kubernetes Manifests:**
```
kubernetes/02-services/
├── frontend-service/
│   ├── deployment.yaml                   # Pod spec, replicas, image
│   ├── service.yaml                      # LoadBalancer/ClusterIP
│   └── kustomization.yaml                # Image tag (updated by Image Updater)
├── product-service/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── kustomization.yaml
└── user-service/
    ├── deployment.yaml
    ├── service.yaml
    └── kustomization.yaml
```

### **ArgoCD Applications:**
```
argocd/applications/
├── frontend-service.yaml                 # ArgoCD Application CRD
├── product-service.yaml
└── user-service.yaml
```

---

## **Kubernetes Secrets & ConfigMaps**

### **In `argocd` namespace:**

**Secrets:**
- `git-creds` - GitHub token for Image Updater to commit
- `dockerhub-pull-secret` - Docker Hub credentials for rate limit

**ConfigMaps:**
- `argocd-image-updater-config` - Git user, Docker registry config

---

## **Key Principles**

### **1. GitOps**
- Git is the **single source of truth**
- Cluster state always matches Git
- All changes go through Git (no manual kubectl apply)

### **2. Separation of Concerns**
- **CI (GitHub Actions)**: Builds images
- **Image Updater**: Updates manifests
- **ArgoCD**: Deploys to cluster
- Each component has one job

### **3. Automation**
- Developer only commits code
- Everything else is automatic
- No manual intervention needed

### **4. Auditability**
- Every deployment has a Git commit
- Full history of what was deployed when
- Easy rollback (revert Git commit)

---

## **Monitoring & Troubleshooting**

### **Check CI Pipeline:**
```bash
# View GitHub Actions in browser
# https://github.com/cs-samvith/e-commerce/actions
```

### **Check Image Updater:**
```bash
kubectl logs -n argocd -l app.kubernetes.io/name=argocd-image-updater -f
```

### **Check ArgoCD:**
```bash
# CLI
argocd app list
argocd app get frontend-service

# UI
kubectl port-forward svc/argocd-server -n argocd 8080:443
# Access: https://localhost:8080
```

### **Check Deployments:**
```bash
kubectl get deployments -n ecommerce
kubectl get pods -n ecommerce
kubectl describe deployment frontend-service -n ecommerce
```

---

## **Advantages of This Setup**

✅ **Fully Automated** - Push code → Deployed in ~30 minutes  
✅ **GitOps** - Cluster state always matches Git  
✅ **Auditable** - Every deployment has a Git commit  
✅ **Rollback Easy** - Revert Git commit to rollback  
✅ **No Manual Steps** - No kubectl apply needed  
✅ **Scalable** - Add new services easily  
✅ **Declarative** - Infrastructure as code  

---

## **What Happens When...**

### **Scenario 1: You push new code**
1. GitHub Actions builds new image with new SHA tag
2. Image Updater detects it (within 30 min)
3. Updates Git with new tag
4. ArgoCD syncs to cluster (within 3 min)
5. Rolling update deploys new version

### **Scenario 2: Someone manually changes cluster**
1. ArgoCD detects drift (self-heal enabled)
2. Automatically reverts to Git state
3. Cluster matches Git again

### **Scenario 3: You need to rollback**
```bash
git revert <commit-hash>
git push
# ArgoCD automatically deploys previous version
```

### **Scenario 4: You add a new service**
1. Add service code to `/services/new-service/`
2. Add to GitHub Actions matrix
3. Create Kubernetes manifests in `/kubernetes/02-services/new-service/`
4. Create ArgoCD Application YAML
5. Done! Fully automated from now on

---

This is a **production-grade GitOps pipeline** following best practices! 🎉