variable "location" {
  description = "Azure region where the Terraform backend resources will be created."
  type        = string
  default     = "francecentral"
}

variable "environment" {
  description = "Environment label used for naming and tagging."
  type        = string
  default     = "dev"
}

variable "resource_group_name" {
  description = "Name of the Azure Resource Group that will host the Terraform state backend."
  type        = string
  default     = "rg-azure-mlops-tfstate-dev"
}

variable "storage_account_name" {
  description = "Globally unique Azure Storage Account name for the Terraform backend."
  type        = string
  default     = "sttarik2012mlopstfdev"

  validation {
    condition     = can(regex("^[a-z0-9]{3,24}$", var.storage_account_name))
    error_message = "The storage account name must be 3-24 characters long and contain only lowercase letters and numbers."
  }
}

variable "container_name" {
  description = "Blob container name used for Terraform state files."
  type        = string
  default     = "tfstate"
}
