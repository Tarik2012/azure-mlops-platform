variable "location" {
  description = "Azure region for the temporary AKS learning environment."
  type        = string
  default     = "francecentral"
}

variable "environment" {
  description = "Environment label used for tags."
  type        = string
  default     = "dev"
}

variable "resource_group_name" {
  description = "Name of the Resource Group created for AKS."
  type        = string
  default     = "rg-azure-mlops-aks-dev"
}

variable "aks_cluster_name" {
  description = "Name of the AKS cluster."
  type        = string
  default     = "aks-azure-mlops-dev"
}

variable "dns_prefix" {
  description = "DNS prefix used by the AKS API server."
  type        = string
  default     = "aks-azure-mlops-dev"
}

variable "node_count" {
  description = "Fixed number of nodes in the system pool. Keep this at one for learning."
  type        = number
  default     = 1

  validation {
    condition     = var.node_count == 1
    error_message = "This temporary learning stack intentionally supports exactly one node."
  }
}

variable "node_vm_size" {
  description = "Small VM SKU for the single system node. Availability and quota vary by region."
  type        = string
  default     = "Standard_B2s"
}

variable "acr_name" {
  description = "Name of the existing Azure Container Registry."
  type        = string
  default     = "acrtarik2012azuremlopsdev"
}

variable "acr_resource_group_name" {
  description = "Resource Group containing the existing Azure Container Registry."
  type        = string
  default     = "rg-azure-mlops-tarik2012-dev"
}
