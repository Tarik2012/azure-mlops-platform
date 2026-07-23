output "resource_group_name" {
  description = "Name of the temporary AKS Resource Group."
  value       = azurerm_resource_group.this.name
}

output "aks_cluster_name" {
  description = "Name of the AKS cluster."
  value       = azurerm_kubernetes_cluster.this.name
}

output "acr_login_server" {
  description = "Login server of the existing ACR available to the AKS kubelet."
  value       = data.azurerm_container_registry.existing.login_server
}

output "kube_config_command" {
  description = "Azure CLI command that merges this cluster into the local kubeconfig."
  value       = "az aks get-credentials --resource-group ${azurerm_resource_group.this.name} --name ${azurerm_kubernetes_cluster.this.name} --overwrite-existing"
}

output "destroy_warning" {
  description = "Cost-safety reminder for this temporary learning stack."
  value       = "COST WARNING: AKS worker nodes and related Azure resources incur charges. Run terraform destroy immediately after practice."
}
