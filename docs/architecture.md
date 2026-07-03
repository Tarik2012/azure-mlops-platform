# Architecture

## Overview

This project combines a local MLOps workflow with a manually validated Azure inference deployment. Locally, the repository supports data ingestion, profiling, validation, preprocessing, model training, MLflow tracking, Docker packaging, and API testing. In Azure, the validated scope focused on serving the trained model through Azure Container Apps.

## Local Architecture

The local architecture is an end-to-end machine learning workflow that produces a model artifact consumed by the API layer.

### Local Components

- `scripts/run_local_pipeline.py` orchestrates the pipeline stages.
- `src.data.ingest` loads raw Iris data.
- `src.data.profile` performs dataset profiling.
- `src.data.validate` checks schema and data quality.
- `src.data.preprocess` prepares the processed dataset.
- `src.training.train` trains the model and logs to local MLflow.
- `models/iris_model.joblib` stores the trained artifact.
- `src.api.main` and `src.api.routes` expose inference endpoints.
- `Dockerfile` packages the API and model for deployment.

### Local ASCII Diagram

```text
Raw Data
   |
   v
Ingestion -> Profiling -> Validation -> Preprocessing -> Training -> iris_model.joblib
                                                                  |
                                                                  v
                                                         FastAPI Inference API
                                                                  |
                                                                  v
                                                               Docker Image
```

## Azure Deployment Architecture

The Azure deployment operationalized the inference API, not the full training workflow. Training remained local for this stage, and the trained model artifact was baked into the container image before deployment.

### Azure Components

| Component | Role |
| --- | --- |
| Resource Group | Lifecycle and cost boundary |
| Azure Container Registry | Private image storage |
| Managed Identity | Secure Azure-native runtime identity |
| `AcrPull` role | Registry pull authorization |
| Container Apps Environment | Managed runtime environment |
| Container App | Public HTTPS application endpoint |

### Azure ASCII Diagram

```text
Developer Workstation
   |
   | docker build
   v
Local Docker Image
   |
   | docker push
   v
Azure Container Registry
   ^
   | AcrPull via Managed Identity
   |
Azure Container App  --->  Public HTTPS Endpoint
   |
   v
FastAPI Application
   |
   v
iris_model.joblib
```

## Request Flow

The runtime request path for inference is:

```text
Client -> Azure Container App -> FastAPI -> Model -> Prediction Response
```

Expanded view:

```text
Client Request
   |
   v
Container App Ingress
   |
   v
FastAPI Route (/health, /model-info, /predict)
   |
   v
Model Loader / Prediction Logic
   |
   v
HTTP Response
```

## Image Flow

The application image followed this path:

```text
Local Docker Build -> Azure Container Registry -> Container App Pulls Image
```

Expanded view:

```text
Repository Source + models/iris_model.joblib
   |
   v
docker build
   |
   v
azure-mlops-platform-api:v1
   |
   v
docker tag
   |
   v
acrazuremlopsplatform.azurecr.io/azure-mlops-platform-api:v1
   |
   v
docker push
   |
   v
Azure Container Registry
   |
   v
Azure Container App startup pull
```

## Identity Flow

The registry access flow used Azure-native identity:

```text
Container App uses Managed Identity -> AcrPull -> ACR
```

Expanded view:

```text
Azure Container App
   |
   v
User-Assigned Managed Identity
   |
   v
Azure RBAC: AcrPull
   |
   v
Azure Container Registry
```

This pattern is preferable to registry username/password authentication because it reduces secret handling and limits access through RBAC.

## Current Architecture

The current validated architecture can be summarized as follows:

- Data preparation and model training run locally.
- MLflow tracking is local.
- The trained model artifact is stored in `models/iris_model.joblib`.
- The FastAPI service is containerized with Docker.
- The container image is stored in Azure Container Registry.
- Azure Container Apps hosts the public inference API.
- Managed Identity plus `AcrPull` protects private image access.
- The temporary Azure environment was deleted after successful validation.

## Future Architecture: CI/CD and Terraform

The natural next step is to move from manual deployment to automated delivery and reproducible infrastructure.

### Target Future State

- GitHub Actions runs tests, builds the image, and pushes to ACR.
- Terraform provisions Azure resources consistently across environments.
- Environment-specific configuration is managed explicitly for dev, test, and prod.
- Deployment becomes repeatable, reviewable, and easier to audit.

### Future ASCII Diagram

```text
GitHub Push
   |
   v
GitHub Actions CI
   |
   +--> Run Tests
   |
   +--> Build Docker Image
   |
   +--> Push Image to ACR
   |
   +--> Trigger Deployment
   |
   v
Terraform / IaC Provisioning
   |
   v
Azure Resource Group
   |
   +--> ACR
   +--> Managed Identity
   +--> Container Apps Environment
   +--> Container App
```

## Architecture Notes for Interviews

- The project separates model training concerns from serving concerns.
- The Azure deployment validates the serving layer first, which is a practical incremental MLOps strategy.
- Container Apps provides a lightweight managed runtime for API hosting.
- ACR stores the immutable image artifact that is promoted into the runtime.
- Managed Identity with `AcrPull` demonstrates secure, production-oriented access design.
- The next maturity step is automating both infrastructure and deployment flow.
