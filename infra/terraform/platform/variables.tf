variable "location" {
  description = "Azure region where the platform resources will be created."
  type        = string
  default     = "francecentral"
}

variable "environment" {
  description = "Environment label used for naming and tagging."
  type        = string
  default     = "dev"
}

variable "resource_group_name" {
  description = "Name of the Azure Resource Group."
  type        = string
  default     = "rg-azure-mlops-platform-dev"
}

variable "acr_name" {
  description = "Name of the Azure Container Registry."
  type        = string
  default     = "acrazuremlopsplatform"
}

variable "managed_identity_name" {
  description = "Name of the user-assigned managed identity used by the Container App."
  type        = string
  default     = "id-azure-mlops-api-dev"
}

variable "log_analytics_workspace_name" {
  description = "Name of the Log Analytics workspace used by the Container Apps environment."
  type        = string
  default     = "law-ca-azure-mlops-api-dev"
}

variable "container_app_environment_name" {
  description = "Name of the Azure Container Apps Environment."
  type        = string
  default     = "cae-azure-mlops-platform-dev"
}
