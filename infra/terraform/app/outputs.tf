output "container_app_name" {
  description = "Name of the Azure Container App."
  value       = azurerm_container_app.this.name
}

output "container_app_fqdn" {
  description = "Public FQDN of the Azure Container App when ingress is available."
  value       = try(azurerm_container_app.this.latest_revision_fqdn, null)
}

output "container_app_url" {
  description = "Public HTTPS URL of the Azure Container App when ingress is available."
  value       = try(format("https://%s", azurerm_container_app.this.latest_revision_fqdn), null)
}

output "container_image" {
  description = "Container image reference deployed to the Azure Container App."
  value       = azurerm_container_app.this.template[0].container[0].image
}
