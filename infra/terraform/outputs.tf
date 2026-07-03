output "resource_group_name" {
  description = "Name of the Azure Resource Group."
  value       = azurerm_resource_group.this.name
}

output "acr_login_server" {
  description = "Login server of the Azure Container Registry."
  value       = azurerm_container_registry.this.login_server
}

output "managed_identity_id" {
  description = "Resource ID of the user-assigned managed identity."
  value       = azurerm_user_assigned_identity.this.id
}

output "container_app_name" {
  description = "Name of the Azure Container App."
  value       = azurerm_container_app.this.name
}

output "container_app_url" {
  description = "Public HTTPS URL of the Container App when ingress is available."
  value       = try(format("https://%s", azurerm_container_app.this.latest_revision_fqdn), null)
}
