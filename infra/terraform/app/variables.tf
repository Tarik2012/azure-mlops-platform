variable "environment" {
  description = "Environment label used for naming and tagging."
  type        = string
  default     = "dev"
}

variable "resource_group_name" {
  description = "Name of the Azure Resource Group that already hosts the platform resources."
  type        = string
  default     = "rg-azure-mlops-platform-dev"
}

variable "acr_name" {
  description = "Name of the existing Azure Container Registry."
  type        = string
  default     = "acrazuremlopsplatform"
}

variable "managed_identity_name" {
  description = "Name of the existing user-assigned managed identity used by the Container App."
  type        = string
  default     = "id-azure-mlops-api-dev"
}

variable "container_app_environment_name" {
  description = "Name of the existing Azure Container Apps Environment."
  type        = string
  default     = "cae-azure-mlops-platform-dev"
}

variable "container_app_name" {
  description = "Name of the Azure Container App."
  type        = string
  default     = "ca-azure-mlops-api-dev"
}

variable "container_image" {
  description = "Container image reference that the Container App will run."
  type        = string
  default     = "acrazuremlopsplatform.azurecr.io/azure-mlops-platform-api:v1"
}

variable "target_port" {
  description = "Ingress port exposed by the Container App."
  type        = number
  default     = 8000
}

variable "container_cpu" {
  description = "vCPU allocated to the container."
  type        = number
  default     = 0.25
}

variable "container_memory" {
  description = "Memory allocated to the container."
  type        = string
  default     = "0.5Gi"
}

variable "min_replicas" {
  description = "Minimum number of replicas for the Container App."
  type        = number
  default     = 0
}

variable "max_replicas" {
  description = "Maximum number of replicas for the Container App."
  type        = number
  default     = 1
}
