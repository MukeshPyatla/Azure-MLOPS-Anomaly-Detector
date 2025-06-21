# infrastructure/azure/variables.tf
variable "location" {
  description = "The Azure region to deploy resources."
  type        = string
  default     = "eastus" # You can change this to your preferred Azure region (e.g., "westus2", "westeurope")
}

variable "project_name_prefix" {
  description = "A unique prefix for all resources to avoid naming conflicts."
  type        = string
  default     = "mlopsanomaly" # Azure naming rules are stricter, use lowercase, alphanumeric only.
}