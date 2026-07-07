locals {
  common_tags = {
    environment = var.environment
    project     = "azure-mlops-platform"
    managed_by  = "terraform"
  }
}

data "azurerm_resource_group" "platform" {
  name = var.resource_group_name
}

data "azurerm_container_registry" "platform" {
  name                = var.acr_name
  resource_group_name = data.azurerm_resource_group.platform.name
}

data "azurerm_user_assigned_identity" "platform" {
  name                = var.managed_identity_name
  resource_group_name = data.azurerm_resource_group.platform.name
}

data "azurerm_container_app_environment" "platform" {
  name                = var.container_app_environment_name
  resource_group_name = data.azurerm_resource_group.platform.name
}

resource "azurerm_container_app" "this" {
  name                         = var.container_app_name
  resource_group_name          = data.azurerm_resource_group.platform.name
  container_app_environment_id = data.azurerm_container_app_environment.platform.id
  revision_mode                = "Single"

  identity {
    type         = "UserAssigned"
    identity_ids = [data.azurerm_user_assigned_identity.platform.id]
  }

  registry {
    server   = data.azurerm_container_registry.platform.login_server
    identity = data.azurerm_user_assigned_identity.platform.id
  }

  template {
    min_replicas = var.min_replicas
    max_replicas = var.max_replicas

    container {
      name   = "api"
      image  = var.container_image
      cpu    = var.container_cpu
      memory = var.container_memory
    }
  }

  ingress {
    external_enabled = true
    target_port      = var.target_port

    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }

  tags = local.common_tags
}
