output "resource_group_name" {
  description = "Name of the Azure ML Resource Group."
  value       = azurerm_resource_group.this.name
}

output "workspace_name" {
  description = "Name of the Azure ML Workspace."
  value       = azurerm_machine_learning_workspace.this.name
}

output "workspace_id" {
  description = "Resource ID of the Azure ML Workspace."
  value       = azurerm_machine_learning_workspace.this.id
}

output "storage_account_name" {
  description = "Name of the Azure ML Storage Account."
  value       = azurerm_storage_account.this.name
}

output "key_vault_name" {
  description = "Name of the Azure ML Key Vault."
  value       = azurerm_key_vault.this.name
}

output "application_insights_name" {
  description = "Name of the Azure ML Application Insights resource."
  value       = azurerm_application_insights.this.name
}

output "container_registry_name" {
  description = "Name of the Azure ML Container Registry."
  value       = azurerm_container_registry.this.name
}

output "compute_cluster_name" {
  description = "Name of the Azure ML compute cluster."
  value       = azurerm_machine_learning_compute_cluster.this.name
}
