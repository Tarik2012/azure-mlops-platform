# Azure ML and MLflow training module

## Purpose

This module introduces managed model training without changing the existing
FastAPI, Docker, Azure Container Registry, Container Apps, Terraform, or GitHub
Actions deployment flow. The training code runs locally first and can later be
submitted to Azure ML as the same Python module.

## Core concepts

### Azure ML Workspace

An Azure Machine Learning workspace is the control plane for machine-learning
assets and activity. It provides a shared boundary for jobs, environments,
datastores, compute, metrics, models, endpoints, identity, and access control. Its
Storage Account, Key Vault, Application Insights instance, and Container Registry
support artifacts, secrets, telemetry, and custom images.

### Compute Cluster

An Azure ML compute cluster supplies managed virtual machines for jobs. It scales
between a configured minimum and maximum node count; a minimum of zero avoids idle
compute charges. A job references the cluster but does not create it.

### MLflow tracking

MLflow records parameters, metrics, run metadata, and artifacts so training runs
can be compared and reproduced. Locally, MLflow uses a local tracking store. In an
Azure ML job, Azure ML provides the tracking integration and associates the same
logging calls with the managed job run.

### Model Registry

In a later phase, a selected artifact will become a versioned model asset.
Registration separates evaluated training output from a model approved for
deployment and preserves lineage back to its training run.

## How this differs from Container Apps

The existing Container Apps module packages and serves the FastAPI inference API.
This module manages the earlier training lifecycle: reproducible compute,
experiments, metrics, and model artifacts. Training does not replace the API.

The planned lifecycle is:

```text
data -> training job -> MLflow -> model registry -> managed online endpoint
```

## Local training

```powershell
.\venv\Scripts\python.exe -m src.training.train_azureml --model-output .tmp\azureml-model
```

This requires no Azure credentials. It writes `model.joblib` to the selected
output directory and logs parameters, metrics, and the artifact with MLflow.

## Safe preparation commands

```powershell
terraform fmt -recursive infra/terraform
terraform -chdir=infra/terraform/aml init -backend=false
terraform -chdir=infra/terraform/aml validate
terraform -chdir=infra/terraform/aml plan -var-file=terraform.tfvars.example
```

Review the plan carefully. A future, explicit `terraform apply` creates billable
Azure resources and requires an authenticated Azure subscription.

After infrastructure exists, these commands register the environment and submit
the job. Both update Azure and are intentionally not part of Phase 1 validation:

```powershell
az ml environment create --file azureml/environments/sklearn-mlflow.yml --resource-group rg-azure-mlops-aml-dev --workspace-name mlw-azure-mlops-dev
az ml job create --file azureml/jobs/train_iris.yml --resource-group rg-azure-mlops-aml-dev --workspace-name mlw-azure-mlops-dev --stream
```
