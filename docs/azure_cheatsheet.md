# Azure Cheat Sheet

## Purpose

This cheat sheet summarizes the Azure services, commands, and talking points used in the manual deployment of the `azure-mlops-platform` FastAPI inference service.

All commands below are historical references or representative examples. They are included for documentation and interview preparation, not for execution now.

## Core Services

| Service | Definition | Role in This Project |
| --- | --- | --- |
| Resource Group | Logical Azure container for related resources | Held the full temporary deployment so everything could be deleted together |
| Azure Container Registry (ACR) | Private container image registry | Stored `acrazuremlopsplatform.azurecr.io/azure-mlops-platform-api:v1` |
| Docker image | Packaged application runtime artifact | Contained FastAPI code and `iris_model.joblib` |
| Managed Identity | Azure-managed service identity | Allowed the runtime to access ACR without stored credentials |
| `AcrPull` role | Built-in Azure RBAC role for image pull access | Granted least-privilege pull rights on ACR |
| Container Apps Environment | Managed hosting boundary for container apps | Provided the runtime environment for the service |
| Container App | Serverless containerized application endpoint | Hosted the public FastAPI inference API |

## Resource Inventory

| Item | Value |
| --- | --- |
| Region | `francecentral` |
| Resource Group | `rg-azure-mlops-platform-dev` |
| ACR | `acrazuremlopsplatform` |
| Image | `acrazuremlopsplatform.azurecr.io/azure-mlops-platform-api:v1` |
| Managed Identity | `id-azure-mlops-api-dev` |
| Container Apps Environment | `cae-azure-mlops-platform-dev` |
| Container App | `ca-azure-mlops-api-dev` |

## What Each Service Did

- `Resource Group`: provided one deletion boundary for the entire exercise.
- `ACR`: stored the private image that Azure Container Apps pulled at runtime.
- `Docker image`: packaged application code plus the trained model artifact.
- `Managed Identity`: removed the need for ACR username/password usage.
- `AcrPull`: authorized the Container App runtime to pull from ACR.
- `Container Apps Environment`: hosted the app platform context.
- `Container App`: exposed `/docs`, `/health`, `/model-info`, and `/predict` over HTTPS.

## Useful Azure CLI Commands

### Resource Group

Historical example:

```bash
az group create --name rg-azure-mlops-platform-dev --location francecentral
```

Cleanup:

```bash
az group delete --name rg-azure-mlops-platform-dev --yes --no-wait
```

Verification:

```bash
az group exists --name rg-azure-mlops-platform-dev
```

Expected result after cleanup:

```text
false
```

### Azure Container Registry

Historical example:

```bash
az acr create \
  --resource-group rg-azure-mlops-platform-dev \
  --name acrazuremlopsplatform \
  --sku Basic
```

Representative inspection examples:

```bash
az acr show --name acrazuremlopsplatform --resource-group rg-azure-mlops-platform-dev
az acr repository list --name acrazuremlopsplatform
```

### Docker Build, Tag, and Push

Historical examples:

```bash
docker build -t azure-mlops-platform-api:v1 .
docker tag azure-mlops-platform-api:v1 acrazuremlopsplatform.azurecr.io/azure-mlops-platform-api:v1
docker push acrazuremlopsplatform.azurecr.io/azure-mlops-platform-api:v1
```

### Managed Identity

Representative example:

```bash
az identity create \
  --resource-group rg-azure-mlops-platform-dev \
  --name id-azure-mlops-api-dev \
  --location francecentral
```

### `AcrPull` Role Assignment

Representative example:

```bash
az role assignment create \
  --assignee <managed-identity-principal-id> \
  --role AcrPull \
  --scope <acr-resource-id>
```

### Container Apps Environment

Historical example:

```bash
az containerapp env create \
  --name cae-azure-mlops-platform-dev \
  --resource-group rg-azure-mlops-platform-dev \
  --location francecentral
```

### Container App Deployment

Representative example:

```bash
az containerapp create \
  --name ca-azure-mlops-api-dev \
  --resource-group rg-azure-mlops-platform-dev \
  --environment cae-azure-mlops-platform-dev \
  --image acrazuremlopsplatform.azurecr.io/azure-mlops-platform-api:v1 \
  --target-port 8000 \
  --ingress external \
  --registry-server acrazuremlopsplatform.azurecr.io \
  --user-assigned <managed-identity-resource-id> \
  --registry-identity <managed-identity-resource-id>
```

### Container App Inspection

Representative examples:

```bash
az containerapp show --name ca-azure-mlops-api-dev --resource-group rg-azure-mlops-platform-dev
az containerapp logs show --name ca-azure-mlops-api-dev --resource-group rg-azure-mlops-platform-dev --follow
```

## Common Troubleshooting Commands

Representative examples:

```bash
az account show
az acr show --name acrazuremlopsplatform --resource-group rg-azure-mlops-platform-dev
az identity show --name id-azure-mlops-api-dev --resource-group rg-azure-mlops-platform-dev
az containerapp show --name ca-azure-mlops-api-dev --resource-group rg-azure-mlops-platform-dev
az containerapp logs show --name ca-azure-mlops-api-dev --resource-group rg-azure-mlops-platform-dev --follow
```

Use them to check:

- active subscription context
- registry existence and properties
- managed identity existence
- container app configuration
- application startup and runtime logs

## API Validation Quick Reference

Validated outcomes:

- `GET /health` returned `200`
- `GET /model-info` returned `model_exists: true`
- `POST /predict` returned prediction `setosa`

Representative test examples:

```bash
curl https://<container-app-fqdn>/health
curl https://<container-app-fqdn>/model-info
curl -X POST https://<container-app-fqdn>/predict \
  -H "Content-Type: application/json" \
  -d '{
    "sepal_length": 5.1,
    "sepal_width": 3.5,
    "petal_length": 1.4,
    "petal_width": 0.2
  }'
```

## Interview Preparation Notes

- ACR is the private image store; it does not run the application.
- Container Apps runs the application; it pulls the image from ACR.
- Managed Identity plus `AcrPull` is stronger than storing ACR credentials in scripts.
- The Resource Group is the cost and lifecycle boundary.
- The model had to be packaged into the image so the API could serve inference immediately at startup.
- A successful deployment is not enough; the service must also pass health, metadata, and prediction checks.
