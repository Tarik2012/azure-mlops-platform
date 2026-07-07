# Terraform Deployment Flow

The Terraform configuration is split into three stacks:

- `infra/terraform/bootstrap`: one-time backend resources for Terraform state
- `infra/terraform/platform`: shared Azure platform resources
- `infra/terraform/app`: the Azure Container App deployment

Do not run Terraform from `infra/terraform` directly.

## Stack responsibilities

### Bootstrap

Creates only the Terraform remote state backend:

- Resource Group for state storage
- Storage Account
- Blob container

### Platform

Creates the shared Azure platform resources:

- Resource Group
- Azure Container Registry
- User Assigned Managed Identity
- `AcrPull` role assignment
- Log Analytics Workspace
- Azure Container Apps Environment

### App

Creates only the Azure Container App and reads the platform resources with data sources.

## One-time bootstrap

1. Apply the `bootstrap` stack locally to create the Terraform backend.
2. Create a Microsoft Entra application or service principal for GitHub Actions.
3. Add a federated credential for GitHub OIDC.
4. Grant the GitHub deployment identity Azure permissions.
5. Configure GitHub repository variables for Azure and Terraform backend settings.

### OIDC guidance

For a clean manual deployment flow, the repository includes a GitHub Actions environment named `azure-dev` in the deployment workflow. A practical Entra federated credential subject for that job is:

```text
repo:<github-owner>/<github-repo>:environment:azure-dev
```

Recommended Azure role assignments for the GitHub deployment identity:

- `Contributor` on the subscription that will host the platform resources
- `Storage Blob Data Contributor` on the Terraform state storage account

Repository variables required by the deployment workflow:

- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`
- `TFSTATE_RESOURCE_GROUP_NAME`
- `TFSTATE_STORAGE_ACCOUNT_NAME`
- `TFSTATE_CONTAINER_NAME`

## Remote backend configuration

Both `platform` and `app` use the AzureRM backend:

- [infra/terraform/platform/backend.hcl.example](</C:/Users/erroc/Projects/mlops-azure-fastapi-demo/infra/terraform/platform/backend.hcl.example>)
- [infra/terraform/app/backend.hcl.example](</C:/Users/erroc/Projects/mlops-azure-fastapi-demo/infra/terraform/app/backend.hcl.example>)

Use Azure AD authentication for the backend:

```hcl
use_azuread_auth = true
```

## Normal CI/CD flow

### CI workflow

`.github/workflows/ci.yml` runs on `push` and `pull_request` and performs:

- Python dependency installation
- `pytest`
- `terraform fmt -check -recursive infra/terraform`
- `terraform init -backend=false`
- `terraform validate`

Terraform validation runs for:

- `infra/terraform/bootstrap`
- `infra/terraform/platform`
- `infra/terraform/app`

### Deployment workflow

`.github/workflows/deploy-azure.yml` is manual by default through `workflow_dispatch`.

It performs:

1. Install Python dependencies
2. Run the local pipeline to generate the model artifact required by the container image
3. Run tests
4. Log in to Azure with GitHub OIDC
5. Initialize, plan, and apply the `platform` stack with remote state
6. Read platform outputs, including the ACR name and login server
7. Build the Docker image tagged with `github.sha`
8. Log in to ACR and push the image
9. Initialize, plan, and apply the `app` stack with the pushed image reference
10. Read the deployed Container App URL
11. Smoke test `/health`, `/model-info`, and `/predict`

## Destroy order

Destroy in this order:

1. `app`
2. `platform`
3. `bootstrap` only if you intentionally want to remove the Terraform backend

Do not automate destroy on push.

## Local commands

Initialize and validate all stacks locally without using the remote backend:

```powershell
terraform -chdir=infra/terraform/bootstrap init -backend=false
terraform -chdir=infra/terraform/bootstrap validate
terraform -chdir=infra/terraform/platform init -backend=false
terraform -chdir=infra/terraform/platform validate
terraform -chdir=infra/terraform/app init -backend=false
terraform -chdir=infra/terraform/app validate
```
