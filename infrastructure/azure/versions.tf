# infrastructure/azure/versions.tf
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0" # Use a compatible Azure provider version
    }
  }
  required_version = ">= 1.0.0" # Minimum Terraform CLI version
}

provider "azurerm" {
  features {} # Required for the AzureRM provider
  # client_id       = var.azure_client_id # If using service principal direct authentication
  # client_secret   = var.azure_client_secret
  # tenant_id       = var.azure_tenant_id
  # subscription_id = var.azure_subscription_id
}