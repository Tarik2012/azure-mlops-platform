output "tfstate_resource_group_name" {
  description = "Name of the Azure Resource Group that hosts the Terraform state backend."
  value       = azurerm_resource_group.this.name
}

output "storage_account_name" {
  description = "Name of the Azure Storage Account used for Terraform state."
  value       = azurerm_storage_account.this.name
}

output "container_name" {
  description = "Name of the Blob container used for Terraform state."
  value       = azurerm_storage_container.this.name
}
