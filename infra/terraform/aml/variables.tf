variable "location" {
  description = "Azure region for Azure ML resources."
  type        = string
  default     = "francecentral"
}

variable "environment" {
  description = "Environment label used for naming and tags."
  type        = string
  default     = "dev"
}

variable "resource_group_name" {
  description = "Name of the Resource Group for Azure ML."
  type        = string
  default     = "rg-azure-mlops-aml-dev"
}

variable "workspace_name" {
  description = "Name of the Azure ML Workspace."
  type        = string
  default     = "mlw-azure-mlops-dev"
}

variable "storage_account_name" {
  description = "Globally unique Storage Account name used by Azure ML."
  type        = string
  default     = "stazuremlopsamldev"

  validation {
    condition     = can(regex("^[a-z0-9]{3,24}$", var.storage_account_name))
    error_message = "Storage Account names must contain 3-24 lowercase letters or numbers."
  }
}

variable "key_vault_name" {
  description = "Globally unique Key Vault name used by Azure ML."
  type        = string
  default     = "kv-azure-mlops-aml-dev"
}

variable "application_insights_name" {
  description = "Name of the Application Insights resource used by Azure ML."
  type        = string
  default     = "appi-azure-mlops-aml-dev"
}

variable "container_registry_name" {
  description = "Globally unique Azure Container Registry name used by Azure ML."
  type        = string
  default     = "acrazuremlopsamldev"

  validation {
    condition     = can(regex("^[a-zA-Z0-9]{5,50}$", var.container_registry_name))
    error_message = "Container Registry names must contain 5-50 alphanumeric characters."
  }
}

variable "compute_cluster_name" {
  description = "Name of the Azure ML compute cluster."
  type        = string
  default     = "cpu-cluster"
}

variable "compute_vm_size" {
  description = "VM SKU used by compute-cluster nodes."
  type        = string
  default     = "Standard_DS3_v2"
}

variable "compute_min_nodes" {
  description = "Minimum compute nodes; zero prevents idle compute allocation."
  type        = number
  default     = 0
}

variable "compute_max_nodes" {
  description = "Maximum compute nodes available to the cluster."
  type        = number
  default     = 2
}
