# 5. AKS Kubernetes Model Serving Summary

## Scope and cost boundary

This module adds a separate, temporary Azure Kubernetes Service (AKS) learning
environment for the existing FastAPI model-serving image. It does not change the
Azure ML Terraform or GitHub Actions.

> **Strong cost warning:** the AKS `Free` tier removes the paid control-plane SLA
> fee; it does not make the cluster free. The worker VM, managed disk, public
> IP/load-balancer networking, outbound traffic, logs, and other Azure resources
> can consume credit continuously. Create this cluster only for active practice
> and run `terraform destroy` immediately afterward. Do not leave it running
> overnight.

## What AKS is

AKS is Azure's managed Kubernetes service. Azure operates the Kubernetes control
plane, while the user chooses and pays for worker nodes where application pods
run. Kubernetes supplies a declarative API for scheduling containers, replacing
failed pods, rolling out image changes, providing service discovery, and
managing application configuration.

The `Free` AKS tier in this stack has no financially backed SLA. It is appropriate
for learning and development, not for production availability.

## AKS compared with local Kubernetes

Local Kubernetes products such as Docker Desktop, kind, or minikube run on a
developer machine. They are inexpensive, fast to reset, and useful for learning
Kubernetes objects, but they do not reproduce Azure identity, ACR authorization,
Azure networking, quotas, or cloud operations.

AKS uses real Azure resources and managed identities and is reachable through an
Azure-hosted API server. That makes it useful for learning the cloud integration,
but provisioning takes longer and incurs Azure charges. Use local Kubernetes for
most manifest iteration and AKS only for the Azure-specific exercise.

## What Terraform creates

The stack under `infra/terraform/aks` creates:

- resource group `rg-azure-mlops-aks-dev`;
- AKS cluster `aks-azure-mlops-dev` on the `Free` control-plane tier;
- one system node pool with one `Standard_B2s` VM and a 30 GiB OS disk;
- system-assigned managed identities for AKS and its kubelet;
- simple `kubenet` networking with the standard AKS load balancer for outbound
  connectivity;
- an `AcrPull` role assignment from the existing ACR to the kubelet identity.

The stack reads, but does not create or destroy, the existing registry
`acrtarik2012azuremlopsdev` in `rg-azure-mlops-tarik2012-dev`. If that registry
is in another resource group, change `acr_resource_group_name` in
`terraform.tfvars`.

`Standard_B2s` is intentionally small, but Azure SKU availability and
subscription quota differ by region. If the plan or apply reports an unavailable
SKU or quota error, choose another small AKS-supported two-vCPU SKU and review
its price before applying.

## What the Kubernetes objects do

The Namespace groups this example's objects under `azure-mlops`.

The Deployment declares one replica of the FastAPI container. Kubernetes creates
a pod, restarts it after failure, checks `/health` for readiness and liveness,
and records revisions for rollout and rollback. It uses:

```text
acrtarik2012azuremlopsdev.azurecr.io/azure-mlops-platform-api:latest
```

That image and tag must already exist in ACR. For repeatable environments,
replace `latest` with an immutable version or digest.

The Service gives the pod a stable cluster-internal name and port. It is a
`ClusterIP` Service, so it does not request a separate public Azure load
balancer. For this exercise, access it locally with `kubectl port-forward`.

## How AKS pulls from ACR

Terraform looks up the existing registry and assigns its `AcrPull` role to the
AKS kubelet managed identity. When Kubernetes schedules the pod, the kubelet
uses that Azure identity to authenticate to ACR and pull the private image. No
registry password or Kubernetes `imagePullSecret` is stored in these manifests.
Azure role assignments can take a few minutes to propagate after the first
apply.

## Prerequisites and configuration

Install and authenticate Terraform, Azure CLI, and `kubectl`. Select the intended
Azure subscription before continuing. From the repository root, create local
configuration files:

```powershell
Copy-Item infra/terraform/aks/terraform.tfvars.example infra/terraform/aks/terraform.tfvars
Copy-Item infra/terraform/aks/backend.hcl.example infra/terraform/aks/backend.hcl
```

Review both copies. The remote-state resource group, storage account, and
container must already exist. The `.gitignore` excludes the local files and
Terraform state.

## Create AKS

Initialize the separate stack:

```powershell
terraform -chdir=infra/terraform/aks init -reconfigure -backend-config=backend.hcl
```

Review the proposed resources:

```powershell
terraform -chdir=infra/terraform/aks plan -var-file=terraform.tfvars -out=aks.tfplan
```

Apply exactly the reviewed plan:

```powershell
terraform -chdir=infra/terraform/aks apply aks.tfplan
```

Merge the AKS credentials into the current kubeconfig:

```powershell
az aks get-credentials --resource-group rg-azure-mlops-aks-dev --name aks-azure-mlops-dev --overwrite-existing
```

Confirm the active context before applying anything:

```powershell
kubectl config current-context
```

## Deploy and inspect the API

Create the namespace first, then the namespaced objects:

```powershell
kubectl apply -f k8s/azure-mlops-api/namespace.yml
kubectl apply -f k8s/azure-mlops-api/deployment.yml -f k8s/azure-mlops-api/service.yml
```

List pods and inspect their readiness:

```powershell
kubectl get pods -n azure-mlops -o wide
```

Read the latest Deployment logs:

```powershell
kubectl logs -n azure-mlops deployment/azure-mlops-api --tail=100
```

Describe a failing pod and review its events:

```powershell
kubectl describe pod -n azure-mlops <pod-name>
```

Forward the internal Service to the local machine:

```powershell
kubectl port-forward -n azure-mlops service/azure-mlops-api 8000:8000
```

In another terminal, test it:

```powershell
Invoke-RestMethod http://localhost:8000/health
```

Restart the Deployment after repushing the `latest` tag:

```powershell
kubectl rollout restart deployment/azure-mlops-api -n azure-mlops
kubectl rollout status deployment/azure-mlops-api -n azure-mlops
```

Undo the most recent rollout:

```powershell
kubectl rollout undo deployment/azure-mlops-api -n azure-mlops
kubectl rollout status deployment/azure-mlops-api -n azure-mlops
```

## Guided smoke test

After creating and reviewing `backend.hcl` and `terraform.tfvars`, the helper
performs the lifecycle above:

```powershell
.\scripts\aks\aks-smoke-test.ps1
```

It shows the current Azure account and requires typing `CREATE` before apply. It
then obtains credentials, applies the manifests, lists objects, attempts a local
port-forward and `/health` request, and prints logs. At the end it requires the
exact confirmation `DESTROY` before running destruction; otherwise it prints the
manual destruction command. It never destroys without confirmation.

## Destroy immediately after practice

From the repository root:

```powershell
terraform -chdir=infra/terraform/aks plan -destroy -var-file=terraform.tfvars
terraform -chdir=infra/terraform/aks destroy -var-file=terraform.tfvars
```

Confirm with `yes` when Terraform displays the exact resources. Destruction
removes the AKS resource group, cluster, worker node, managed cluster resources
managed through AKS, and the ACR role assignment. It does not delete the existing
ACR.

Check that Terraform has no remaining managed resources:

```powershell
terraform -chdir=infra/terraform/aks show
```

If destroy fails, do not assume billing has stopped. Read the error, rerun
`terraform destroy`, and verify the AKS cluster and
`rg-azure-mlops-aks-dev` no longer exist in the Azure portal. The separately
created Terraform state storage is not removed by this stack and may have its
own small ongoing cost.
