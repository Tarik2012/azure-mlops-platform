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
  default     = "rg-azure-mlops-tarik2012-dev"
}

variable "workspace_name" {
  description = "Name of the Azure ML Workspace."
  type        = string
  default     = "mlw-azure-mlops-tarik2012-dev"
}

variable "storage_account_name" {
  description = "Globally unique Storage Account name used by Azure ML."
  type        = string
  default     = "sttarik2012azuremlopsdev"

  validation {
    condition     = can(regex("^[a-z0-9]{3,24}$", var.storage_account_name))
    error_message = "Storage Account names must contain 3-24 lowercase letters or numbers."
  }
}

variable "key_vault_name" {
  description = "Globally unique Key Vault name used by Azure ML."
  type        = string
  default     = "kv-amlops-tarik2012-dev"

  validation {
    condition     = can(regex("^[a-zA-Z][a-zA-Z0-9-]{1,22}[a-zA-Z0-9]$", var.key_vault_name)) && !strcontains(var.key_vault_name, "--")
    error_message = "Key Vault names must contain 3-24 alphanumeric characters or single hyphens, start with a letter, and end with an alphanumeric character."
  }
}

variable "application_insights_name" {
  description = "Name of the Application Insights resource used by Azure ML."
  type        = string
  default     = "appi-azure-mlops-tarik2012-dev"
}

variable "container_registry_name" {
  description = "Globally unique Azure Container Registry name used by Azure ML."
  type        = string
  default     = "acrtarik2012azuremlopsdev"

  validation {
    condition     = can(regex("^[a-zA-Z0-9]{5,50}$", var.container_registry_name))
    error_message = "Container Registry names must contain 5-50 alphanumeric characters."
  }
}

variable "compute_cluster_name" {
  description = "Name of the Azure ML compute cluster."
  type        = string
  default     = "cpu-amlops-tarik2012-dev"
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
