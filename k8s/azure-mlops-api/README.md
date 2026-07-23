# Azure MLOps API manifests

These manifests deploy one FastAPI replica into the `azure-mlops` namespace and
expose it inside the cluster with a `ClusterIP` Service. `ClusterIP` avoids
creating another public Azure load balancer; use port forwarding for practice:

```powershell
kubectl apply -f k8s/azure-mlops-api/namespace.yml
kubectl apply -f k8s/azure-mlops-api/deployment.yml -f k8s/azure-mlops-api/service.yml
kubectl get pods,services -n azure-mlops
kubectl port-forward -n azure-mlops service/azure-mlops-api 8000:8000
```

In another terminal:

```powershell
Invoke-RestMethod http://localhost:8000/health
```

The image must already exist at
`acrtarik2012azuremlopsdev.azurecr.io/azure-mlops-platform-api:latest`. Terraform
grants the cluster kubelet identity the `AcrPull` role on that existing ACR, so
no Kubernetes image-pull secret is required.

These files are examples for a temporary learning cluster. They do not add
production ingress, TLS, autoscaling, disruption budgets, or secret management.
