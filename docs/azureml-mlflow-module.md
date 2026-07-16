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

A selected artifact can become a versioned model asset. Registration separates
evaluated training output from a model approved for deployment and preserves
lineage back to its training run. Phase 2 uses the registered
`iris-classifier:1` model.

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
az ml environment create --file azureml/environments/sklearn-mlflow.yml --resource-group rg-azure-mlops-tarik2012-dev --workspace-name mlw-azure-mlops-tarik2012-dev
az ml job create --file azureml/jobs/train_iris.yml --resource-group rg-azure-mlops-tarik2012-dev --workspace-name mlw-azure-mlops-tarik2012-dev --stream
```

## Phase 2: managed online endpoint

An Azure ML Managed Online Endpoint is a managed HTTPS interface for real-time
model inference. Azure ML operates the serving infrastructure, authentication,
routing, and monitoring behind the endpoint. The endpoint is the stable client
address; it does not itself select a model implementation.

A deployment is the runnable implementation behind an endpoint. It binds a
registered model, scoring code, runtime environment, VM SKU, and replica count.
An endpoint can contain multiple deployments so a new model can be introduced
without changing the endpoint URI.

`blue` is the conventional name of the initial deployment slot. It has no
special Azure behavior by itself. A later `green` deployment could be added and
traffic shifted gradually or switched after validation. The `--all-traffic`
option below routes 100 percent of endpoint traffic to `blue` after deployment
creation succeeds.

The endpoint and deployment YAML files are Azure ML lifecycle assets. They do
not replace or modify the Terraform-managed Resource Group, Workspace, Storage
Account, Key Vault, Application Insights, Container Registry, or compute
cluster. The existing FastAPI and Container Apps serving path also remains
independent.

### Scoring flow

Azure ML calls `init()` once when an inference container starts. The scoring
script reads `AZUREML_MODEL_DIR`, loads `model.joblib`, and retains the loaded
model for subsequent requests. Azure ML then calls `run(raw_data)` for each
request.

The scoring script accepts a batch-style payload:

```json
{"data": [[5.1, 3.5, 1.4, 0.2]]}
```

It also accepts one record with named Iris features:

```json
{
  "sepal_length": 5.1,
  "sepal_width": 3.5,
  "petal_length": 1.4,
  "petal_width": 0.2
}
```

A successful response has JSON-serializable predictions:

```json
{"predictions": [0]}
```

Malformed JSON, missing features, invalid record shapes, a missing model
artifact, and prediction failures produce explicit errors rather than silently
returning an invalid result.

### Manual creation commands

These commands create billable Azure resources. Run them manually only after
reviewing the YAML files, confirming the registered model and environment, and
authenticating to the intended subscription. They are documented here but are
not executed as part of local validation.

```powershell
az ml online-endpoint create --file azureml/endpoints/iris_endpoint.yml --resource-group rg-azure-mlops-tarik2012-dev --workspace-name mlw-azure-mlops-tarik2012-dev

az ml online-deployment create --file azureml/endpoints/iris_deployment.yml --resource-group rg-azure-mlops-tarik2012-dev --workspace-name mlw-azure-mlops-tarik2012-dev --all-traffic
```
