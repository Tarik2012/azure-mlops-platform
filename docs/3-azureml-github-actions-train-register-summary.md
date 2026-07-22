# 3. Azure ML GitHub Actions Train/Register Summary

## Project context

This module documents the automated Azure ML training and model registration workflow created for the `azure-mlops-platform` project.

The previous module validated the Azure ML flow manually:

```text
Azure ML Training Job
→ MLflow metrics
→ Azure ML Model Registry
→ Managed Online Endpoint
→ Online prediction
→ Endpoint cleanup
```

This module converts the training and model-registration part into a GitHub Actions workflow.

The endpoint deployment is intentionally not included in this workflow because online endpoints can consume cloud resources while running.

---

## Goal of this module

The goal is to automate the safe MLOps pipeline:

```text
GitHub Actions
→ Azure login with OIDC
→ Terraform Azure ML infrastructure
→ Azure ML environment creation
→ Azure ML training job
→ MLflow tracking
→ Azure ML Model Registry
```

This workflow proves that model training and registration can be executed from CI/CD instead of manually from a local terminal.

---

## Workflow created

Workflow file:

```text
.github/workflows/train-register-azureml.yml
```

Workflow name:

```text
Train and Register Azure ML Model
```

Execution mode:

```yaml
on:
  workflow_dispatch:
```

This means the workflow is launched manually from GitHub Actions.

It was kept manual on purpose because it uses real Azure resources and can trigger training compute. In a company, training workflows are often controlled manually, scheduled, or triggered only when ML-related files change.

---

## Why manual execution was used

The workflow is not automatically executed on every push because training jobs can consume cloud resources.

Professional rule:

```text
Cheap and safe checks → automatic
Cloud-changing or cost-generating operations → controlled/manual/approved
```

Recommended strategy:

```text
CI tests and validation: automatic on pull requests
Terraform apply: controlled after merge or with approval
Training jobs: manual, scheduled, or triggered only by ML code/data changes
Endpoint production deployment: manual with approval
```

---

## Main GitHub Actions stages

The workflow performs these stages:

```text
1. Checkout repository
2. Set up Python
3. Install dependencies
4. Run tests
5. Authenticate to Azure with OIDC
6. Prepare Terraform backend
7. Terraform init/validate/apply for Azure ML infrastructure
8. Create Azure ML environment
9. Submit Azure ML training job
10. Wait for the job to complete
11. Register the trained model
```

No online endpoint is created in this workflow.

---

## Azure authentication with OIDC

GitHub Actions authenticates to Azure using OIDC instead of storing an Azure password.

Required GitHub environment:

```text
azure-dev
```

Required GitHub variables/secrets:

```text
AZURE_CLIENT_ID
AZURE_TENANT_ID
AZURE_SUBSCRIPTION_ID
TFSTATE_RESOURCE_GROUP_NAME
TFSTATE_STORAGE_ACCOUNT_NAME
TFSTATE_CONTAINER_NAME
```

The Azure App Registration / Service Principal used by GitHub Actions must have permissions to:

```text
- manage Azure resources required by Terraform
- access the Terraform remote state Storage Account
- create/update Azure ML resources
- submit Azure ML jobs
- register Azure ML models
```

---

## Azure resources involved

Main Azure ML resource group:

```text
rg-azure-mlops-tarik2012-dev
```

Terraform state resource group:

```text
rg-azure-mlops-tfstate-dev
```

Azure ML workspace:

```text
mlw-azure-mlops-tarik2012-dev
```

Azure ML compute cluster:

```text
cpu-amlops-tarik2012-dev
```

Terraform state Storage Account:

```text
sttarik2012mlopstfdev
```

Terraform state container:

```text
tfstate
```

Azure ML model name:

```text
iris-classifier
```

---

## Terraform in the workflow

Terraform is used to ensure the Azure ML infrastructure exists before launching the training job.

Terraform stack:

```text
infra/terraform/aml
```

Terraform backend key:

```text
aml.tfstate
```

The workflow runs Terraform against the remote backend so GitHub Actions uses the same infrastructure state as local development.

This is important because infrastructure should not be manually recreated in different places.

Principle:

```text
Terraform is the source of truth for infrastructure.
GitHub Actions executes Terraform.
Azure is the target platform.
```

---

## Azure ML environment

The workflow creates or updates the Azure ML environment from:

```text
azureml/environments/sklearn-mlflow.yml
```

Validated environment version:

```text
sklearn-mlflow:2
```

Important package included:

```text
azureml-inference-server-http
```

This package was required for Azure ML managed online inference containers. Even though this workflow does not deploy endpoints, keeping the environment correct avoids future inference problems.

---

## Azure ML training job

Training job YAML:

```text
azureml/jobs/train_iris.yml
```

Training script:

```text
src/training/train_azureml.py
```

The training script:

```text
- loads the Iris dataset
- trains a scikit-learn model
- logs parameters with MLflow
- logs metrics with MLflow
- saves model.joblib to the model output folder
```

Metrics logged:

```text
accuracy
f1_macro
```

Manual run metric example:

```text
accuracy: 0.9000
f1_macro: 0.8997
```

---

## MLflow tracking

When the training job runs inside Azure ML, MLflow metrics and artifacts are stored in the Azure ML Workspace.

Concept:

```text
Azure ML Workspace acts as the managed MLflow tracking backend.
```

So calls such as:

```python
mlflow.log_metric("accuracy", accuracy)
mlflow.log_metric("f1_macro", f1_macro)
```

are visible in Azure ML Studio under:

```text
Jobs
→ Experiment
→ Run
→ Metrics
```

---

## Model registration

After the training job completes successfully, the workflow registers the model from the job output.

Model name:

```text
iris-classifier
```

Model type:

```text
custom_model
```

Model path pattern:

```text
azureml://jobs/<AZUREML_JOB_NAME>/outputs/model_output
```

After the successful GitHub Actions run, a new model version was registered:

```text
iris-classifier version 2
```

Manual validation showed:

```text
iris-classifier version 1 → created manually
iris-classifier version 2 → created by GitHub Actions
```

---

## Final validation

The workflow completed successfully in GitHub Actions:

```text
Status: Success
Duration: approximately 8m 40s
Branch: main
```

Model Registry validation:

```powershell
az ml model list `
  --name iris-classifier `
  --resource-group rg-azure-mlops-tarik2012-dev `
  --workspace-name mlw-azure-mlops-tarik2012-dev `
  -o table
```

Observed result:

```text
iris-classifier version 2
iris-classifier version 1
```

This confirms that the CI/CD workflow registered a new model version automatically.

---

## Error 1: GitHub Actions could not access Terraform remote state

### Symptom

Terraform init failed inside GitHub Actions:

```text
403 AuthorizationPermissionMismatch
This request is not authorized to perform this operation
```

### Cause

GitHub Actions authenticated to Azure successfully, but the Service Principal did not have data-plane permission to read/write blobs in the Terraform state Storage Account.

The local user had already been granted the required permission, but the GitHub Actions identity had not.

### Affected resource

```text
Storage Account: sttarik2012mlopstfdev
Container: tfstate
State file: aml.tfstate
```

### Fix

Grant the GitHub Actions Service Principal this role:

```text
Storage Blob Data Contributor
```

Scope:

```text
/subscriptions/<subscription-id>/resourceGroups/rg-azure-mlops-tfstate-dev/providers/Microsoft.Storage/storageAccounts/sttarik2012mlopstfdev
```

PowerShell command used:

```powershell
$SUBSCRIPTION_ID = "4cfcc350-8157-4c53-a3c4-5937dbc63be0"
$TFSTATE_RG = "rg-azure-mlops-tfstate-dev"
$TFSTATE_STORAGE = "sttarik2012mlopstfdev"
$APP_CLIENT_ID = "972622c0-e61c-447b-83e4-66534dc97ad7"

$SP_OBJECT_ID = az ad sp show `
  --id $APP_CLIENT_ID `
  --query id `
  -o tsv

az role assignment create `
  --assignee-object-id $SP_OBJECT_ID `
  --assignee-principal-type ServicePrincipal `
  --role "Storage Blob Data Contributor" `
  --scope "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$TFSTATE_RG/providers/Microsoft.Storage/storageAccounts/$TFSTATE_STORAGE"
```

### Lesson learned

Azure role assignments can be split between:

```text
management-plane permissions
data-plane permissions
```

Contributor can manage many Azure resources, but it does not automatically allow reading and writing blob data in a Storage Account.

For Terraform remote state stored in Azure Blob Storage, the identity running Terraform needs blob data access.

---

## Error 2: Workflow expected both job name and job ID

### Symptom

The workflow failed after submitting the Azure ML job:

```text
Azure ML did not return both a job name and job ID.
```

Azure ML CLI also printed warnings such as:

```text
Class AutoDeleteSettingSchema: This is an experimental class...
Class IntellectualPropertySchema: This is an experimental class...
```

### Cause

The warnings were not the real problem.

The real issue was the workflow parsing logic.

The first workflow version tried to extract both:

```text
JOB_NAME
JOB_ID
```

from Azure ML CLI output using TSV parsing.

The Azure ML CLI output did not match the expected format.

### Fix

The workflow was changed to:

```text
1. Save the full az ml job create response to azureml-job.json
2. Extract only the job name using Python
3. Export the job name as AZUREML_JOB_NAME
4. Use AZUREML_JOB_NAME in later steps
```

This is enough because model registration only needs the job name:

```text
azureml://jobs/$AZUREML_JOB_NAME/outputs/model_output
```

### Lesson learned

Do not rely on fragile TSV parsing for cloud CLI outputs when JSON is available.

Better approach:

```text
Save JSON
Parse specific field
Validate the extracted value
Print debug information
```

---

## Error 3: Rerun vs new workflow run

### Issue

After changing the workflow YAML, rerunning an old failed job can sometimes execute the workflow definition from the old commit.

### Safer approach

After pushing a workflow fix to `main`, start a new workflow run from:

```text
GitHub
→ Actions
→ Train and Register Azure ML Model
→ Run workflow
→ Branch: main
```

### Lesson learned

When fixing GitHub Actions YAML, prefer launching a fresh run from the latest commit instead of rerunning an old failed job.

---

## Difference between workflow and CI/CD

A workflow is the concrete YAML file that GitHub Actions executes.

CI/CD is the engineering practice or strategy.

```text
CI/CD = methodology
GitHub Actions workflow = implementation
```

In this project:

```text
CI:
- install dependencies
- run tests
- validate configuration

CD / MLOps:
- authenticate to Azure
- apply Terraform
- run Azure ML training job
- register model
```

This workflow is a CI/CD MLOps workflow, but it does not deploy an online production endpoint.

---

## How this would be done in a company

A professional MLOps setup usually separates safe automatic checks from controlled cloud operations.

Typical structure:

```text
Pull Request:
  - tests
  - lint
  - docker build
  - terraform fmt
  - terraform validate
  - terraform plan

Merge to main:
  - terraform apply to dev
  - submit training job
  - log metrics
  - register candidate model

Manual approval:
  - deploy to staging
  - smoke test
  - monitor metrics

Production approval:
  - deploy to production
  - monitor latency/errors/model quality
  - rollback if needed
```

Training and deployment are often controlled because they can generate cost and affect real systems.

---

## What this module proves

This module proves that the project can:

```text
- authenticate from GitHub Actions to Azure using OIDC
- use Terraform remote state from CI/CD
- provision/validate Azure ML infrastructure automatically
- create Azure ML environments automatically
- submit Azure ML training jobs automatically
- track metrics with MLflow
- register models automatically in Azure ML Model Registry
- create new model versions from successful training runs
```

This is a real MLOps CI/CD capability.

---

## Interview explanation in English

```text
I created a GitHub Actions workflow to automate the Azure ML training and model registration process. The workflow runs tests, authenticates to Azure using OIDC, applies the Terraform Azure ML infrastructure, creates the Azure ML environment, submits a training job, tracks metrics with MLflow, waits for the job to complete, and registers the trained model in Azure ML Model Registry.

During implementation, I solved real CI/CD issues such as Terraform remote state permissions for the GitHub service principal and robust parsing of Azure ML CLI job outputs. The workflow successfully registered a new model version automatically.
```

---

## Interview explanation in Spanish

```text
Automaticé el pipeline de entrenamiento y registro de modelos con GitHub Actions. El workflow ejecuta tests, se autentica en Azure con OIDC, aplica la infraestructura de Azure ML con Terraform, crea el environment, lanza un training job en Azure ML, registra métricas con MLflow y guarda el modelo entrenado en Azure ML Model Registry.

Durante la implementación resolví problemas reales de CI/CD, como permisos sobre el Terraform remote state en Azure Storage y errores de parsing del output de Azure ML CLI. Finalmente, el workflow registró automáticamente una nueva versión del modelo.
```

---

## Current status

Completed:

```text
Manual Azure ML flow: OK
Managed Online Endpoint test: OK
Endpoint cleanup: OK
GitHub Actions train/register workflow: OK
Model version 2 registered automatically: OK
No active online endpoint: OK
Compute cluster min_instances = 0: OK
```

Remaining for next modules:

```text
1. Azure ML observability and monitoring
2. Endpoint metrics, logs, latency, errors
3. Application Insights integration
4. Model lifecycle: version promotion, rollback, blue/green
5. Kubernetes / AKS model serving
6. Databricks + Mosaic AI
```

---

## Commands used for final checks

Check active endpoints:

```powershell
az ml online-endpoint list `
  --resource-group rg-azure-mlops-tarik2012-dev `
  --workspace-name mlw-azure-mlops-tarik2012-dev `
  -o table
```

Expected result:

```text
No endpoints listed
```

Check compute cluster:

```powershell
az ml compute show `
  --name cpu-amlops-tarik2012-dev `
  --resource-group rg-azure-mlops-tarik2012-dev `
  --workspace-name mlw-azure-mlops-tarik2012-dev `
  -o table
```

Important result:

```text
Min_instances = 0
Max_instances = 2
Provisioning_state = Succeeded
```

Check model versions:

```powershell
az ml model list `
  --name iris-classifier `
  --resource-group rg-azure-mlops-tarik2012-dev `
  --workspace-name mlw-azure-mlops-tarik2012-dev `
  -o table
```

Observed result:

```text
iris-classifier version 2
iris-classifier version 1
```

---

## Final takeaway

The project now includes a working MLOps automation layer:

```text
Code repository
→ GitHub Actions
→ Azure OIDC
→ Terraform
→ Azure ML
→ MLflow
→ Model Registry
```

This is the foundation for more advanced production topics:

```text
observability
model lifecycle
endpoint automation
Kubernetes
Databricks
Mosaic AI
AI agents in production
```
