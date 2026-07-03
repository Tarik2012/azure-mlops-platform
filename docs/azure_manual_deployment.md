# Azure Manual Deployment Record

## Overview

This document records the successful manual Azure deployment of the FastAPI inference service for the `azure-mlops-platform` repository. The deployment was completed as a controlled development exercise to validate that the locally trained Iris model could be packaged in Docker, stored in Azure Container Registry (ACR), deployed to Azure Container Apps, and exposed through a public HTTPS endpoint.

This is a historical deployment record. It is not an instruction to recreate resources now. All Azure resources described here were deleted after validation.

## Architecture Summary

The deployed solution used a containerized FastAPI service backed by a pre-trained model artifact stored inside the container image. Azure Container Apps hosted the runtime, Azure Container Registry stored the private image, and a user-assigned Managed Identity with the `AcrPull` role allowed the running application to pull the image without registry username/password credentials.

## Prerequisites

The manual deployment assumed the following were already in place locally:

- A working Python project with data ingestion, validation, preprocessing, training, tests, and FastAPI inference endpoints.
- A trained model artifact at `models/iris_model.joblib`.
- A working Dockerfile that copies the model into the image.
- Azure CLI and Docker available on the operator workstation.
- Sufficient Azure permissions to create and delete resource groups, identities, container registry resources, and container apps.

## Resource Names

The validated deployment used the following resource inventory:

| Resource Type | Name | Notes |
| --- | --- | --- |
| GitHub repository | `Tarik2012/azure-mlops-platform` | Source repository used for the project |
| Azure region | `francecentral` | Final validated region |
| Resource Group | `rg-azure-mlops-platform-dev` | Temporary development scope for all Azure resources |
| Azure Container Registry | `acrazuremlopsplatform` | Private registry for the API image |
| Docker image | `acrazuremlopsplatform.azurecr.io/azure-mlops-platform-api:v1` | Image deployed to Azure |
| Managed Identity | `id-azure-mlops-api-dev` | User-assigned identity for registry access |
| Role assignment | `AcrPull` | Granted to the Managed Identity on ACR |
| Container Apps Environment | `cae-azure-mlops-platform-dev` | Managed hosting environment |
| Container App | `ca-azure-mlops-api-dev` | Public FastAPI inference service |

## Command Handling Convention

- Commands in this document are historical or representative examples only.
- They are included for documentation and interview discussion.
- They should not be re-run as-is.
- When the exact command line used during the deployment is not preserved, the example is explicitly labeled as representative.

## Manual Deployment Steps

### 1. Create the Resource Group

Objective: create a single lifecycle boundary for all development resources.

Historical command example:

```bash
az group create --name rg-azure-mlops-platform-dev --location francecentral
```

Why it mattered:

- Centralized all deployment assets under one deletion boundary.
- Simplified cost control and end-of-exercise cleanup.

### 2. Create Azure Container Registry

Objective: store the private Docker image used by the API deployment.

Historical command example:

```bash
az acr create \
  --resource-group rg-azure-mlops-platform-dev \
  --name acrazuremlopsplatform \
  --sku Basic
```

Why it mattered:

- Provided a private registry managed within Azure.
- Allowed the runtime platform to pull the exact validated application image.

### 3. Build the Docker Image Locally

Objective: package the FastAPI application and trained model into a deployable container.

Historical command example:

```bash
docker build -t azure-mlops-platform-api:v1 .
```

Why it mattered:

- The Dockerfile copies `src/`, `scripts/`, `README.md`, and `models/` into the image.
- Including `models/iris_model.joblib` was necessary for `/model-info` and `/predict` to work in Azure.

### 4. Tag the Image for ACR

Objective: attach the registry-qualified tag required for pushing the image to Azure Container Registry.

Historical command example:

```bash
docker tag azure-mlops-platform-api:v1 acrazuremlopsplatform.azurecr.io/azure-mlops-platform-api:v1
```

### 5. Push the Image to ACR

Objective: publish the validated application image to the private registry.

Historical command example:

```bash
docker push acrazuremlopsplatform.azurecr.io/azure-mlops-platform-api:v1
```

### 6. Create the Managed Identity

Objective: create a user-assigned identity for secure registry access from Azure Container Apps.

Representative example command:

```bash
az identity create \
  --resource-group rg-azure-mlops-platform-dev \
  --name id-azure-mlops-api-dev \
  --location francecentral
```

Why it mattered:

- Removed the need to store ACR admin credentials in deployment commands.
- Aligned the deployment with enterprise authentication practices.

### 7. Assign the `AcrPull` Role

Objective: allow the Managed Identity to pull images from the private ACR instance.

Representative example command:

```bash
az role assignment create \
  --assignee <managed-identity-principal-id> \
  --role AcrPull \
  --scope <acr-resource-id>
```

Why it mattered:

- Granted minimum required access for image pull operations.
- Avoided over-privileging the application runtime.

### 8. Create the Container Apps Environment

Objective: provision the managed environment that hosts the containerized service.

Historical command example:

```bash
az containerapp env create \
  --name cae-azure-mlops-platform-dev \
  --resource-group rg-azure-mlops-platform-dev \
  --location francecentral
```

### 9. Deploy the Container App

Objective: run the FastAPI image as a public Azure Container App.

Representative example command:

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
  --registry-identity <managed-identity-resource-id> \
  --min-replicas 0 \
  --max-replicas 1 \
  --cpu 0.25 \
  --memory 0.5Gi
```

Notes:

- The exact identity-related switches can vary by Azure CLI version.
- The deployment pattern is accurate even where the command line is shown as representative.

### 10. Test Swagger

Objective: confirm that the public application endpoint and API contract were reachable through the Container App ingress.

Validation method:

- Open the Container App public FQDN in a browser.
- Browse to `/docs` for Swagger UI.

The exact generated URL was not retained in project documentation and is intentionally not fabricated here.

### 11. Test `GET /health`

Validated result:

- HTTP status: `200`

Representative test command:

```bash
curl https://<container-app-fqdn>/health
```

### 12. Test `GET /model-info`

Validated result:

- `model_exists: true`

Representative test command:

```bash
curl https://<container-app-fqdn>/model-info
```

### 13. Test `POST /predict`

Validated result:

- Prediction label returned: `setosa`

Representative test command:

```bash
curl -X POST https://<container-app-fqdn>/predict \
  -H "Content-Type: application/json" \
  -d '{
    "sepal_length": 5.1,
    "sepal_width": 3.5,
    "petal_length": 1.4,
    "petal_width": 0.2
  }'
```

## API Validation Summary

The Azure deployment was validated successfully through the following checks:

| Endpoint | Expected Behavior | Validated Outcome |
| --- | --- | --- |
| `GET /health` | Service readiness | Returned `200` |
| `GET /model-info` | Model metadata and artifact presence | Returned `model_exists: true` |
| `POST /predict` | Inference execution | Returned prediction `setosa` |

These checks confirmed that:

- Ingress was working.
- The application started correctly inside Azure Container Apps.
- The model artifact was available in the running container.
- End-to-end inference was functional.

## Errors and Fixes

No incident log was retained, but the following deployment issues and corrective decisions are part of the validated operating record.

### Registry Authentication Hardening

Issue:

- Registry username/password authentication is operationally weaker and creates secret-handling overhead.

Applied solution:

- A user-assigned Managed Identity was created.
- The identity received the `AcrPull` role on the ACR resource.
- The Container App used that identity to pull the private image.

Outcome:

- The final deployment aligned with enterprise identity-based access patterns.

### Region Standardization

Issue:

- Earlier helper material in the repository referenced `westeurope`, but the final validated deployment was completed in `francecentral`.

Applied solution:

- Documentation was normalized to the actual validated region: `francecentral`.

Outcome:

- The deployment record now reflects the real Azure footprint that was tested successfully.

### Model Artifact Availability in the Runtime Image

Issue:

- A FastAPI inference service cannot serve predictions if the trained model artifact is missing from the running container.

Applied solution:

- The Docker image included `models/` during build.

Outcome:

- `/model-info` reported `model_exists: true`, and `/predict` returned a valid prediction.

## Why Managed Identity and `AcrPull` Are Better Than Registry Credentials

Using Managed Identity plus `AcrPull` is the preferred enterprise pattern for this deployment because it improves both security and operations:

- No registry username/password needs to be embedded in scripts or deployment commands.
- Secret rotation becomes less of an operational burden.
- Access can be restricted to the minimum required role.
- Azure-native identity and access control is easier to audit.
- The runtime identity remains decoupled from human operator credentials.

By contrast, enabling ACR admin credentials is convenient for early experimentation, but it is not the stronger long-term pattern for a production-oriented MLOps deployment.

## Cleanup

After validation, the full Azure environment was deleted by removing the Resource Group.

Historical cleanup command:

```bash
az group delete --name rg-azure-mlops-platform-dev --yes --no-wait
```

Historical verification command:

```bash
az group exists --name rg-azure-mlops-platform-dev
```

Validated result:

```text
false
```

Because all deployment resources were created inside the same Resource Group, deleting that group removed:

- Azure Container Registry
- Managed Identity
- Container Apps Environment
- Container App
- Any dependent configuration under that resource scope

## Lessons Learned

- A small local MLOps project can be promoted to Azure cleanly when the model artifact is already reproducible and containerized.
- Container Apps is a practical service for exposing a lightweight inference API without managing Kubernetes infrastructure.
- Identity-based registry access is materially better than credential-based access, even for development environments.
- Resource Group scoping is the simplest and safest cost-control mechanism for temporary Azure exercises.
- Validation should cover service health, artifact availability, and a real inference call, not only successful deployment status.

## Interview Talking Points

- The project started as a local end-to-end MLOps workflow: ingestion, validation, preprocessing, training, MLflow tracking, API serving, Docker packaging, and tests.
- The Azure validation focused on operationalizing the inference layer first, using Azure Container Registry and Azure Container Apps.
- The deployment used a user-assigned Managed Identity with `AcrPull` instead of registry secrets, which is the stronger enterprise design.
- The API was verified with both health and business-level checks, including a real prediction response.
- The environment was intentionally temporary and cost-controlled through Resource Group deletion after testing.
- A natural next step is to replace the manual sequence with CI/CD and infrastructure as code.
