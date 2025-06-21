# infrastructure/azure/outputs.tf
output "resource_group_name" {
  description = "Name of the resource group."
  value       = azurerm_resource_group.rg.name
}

output "storage_account_name" {
  description = "Name of the raw data lake storage account."
  value       = azurerm_storage_account.raw_data_lake_sa.name
}

output "raw_data_blob_container_name" {
  description = "Name of the raw data blob container."
  value       = azurerm_storage_container.raw_data_blob_container.name
}

output "eventhub_namespace_name" {
  description = "Name of the Event Hubs Namespace."
  value       = azurerm_eventhub_namespace.eh_namespace.name
}

output "eventhub_name" {
  description = "Name of the Transaction Event Hub."
  value       = azurerm_eventhub.transaction_eventhub.name
}

output "eventhub_send_primary_key" {
  description = "Primary Shared Access Key for sending to Event Hub (use with caution, avoid exposing in code)."
  value       = azurerm_eventhub_namespace_authorization_rule.send_rule.primary_key # Or eventhub_send_rule.primary_key
  sensitive   = true # Mark as sensitive so it's not shown in plan/apply output
}

output "processed_data_lake_storage_account_name" {
  description = "Name of the storage account for processed data."
  value       = azurerm_storage_account.processed_data_lake_sa.name
}

output "processed_data_blob_container_name" {
  description = "Name of the blob container for processed data."
  value       = azurerm_storage_container.processed_data_blob_container.name
}

output "databricks_workspace_url" {
  description = "URL to access the Azure Databricks workspace."
  value       = azurerm_databricks_workspace.mlops_workspace.workspace_url
}

output "ml_workspace_url" {
  description = "URL to access the Azure Machine Learning workspace."
  value       = azurerm_machine_learning_workspace.ml_workspace.workspace_url
}

output "function_app_name" {
  description = "Name of the Azure Function App."
  value       = azurerm_linux_function_app.anomaly_detector_function_app.name
}

output "function_app_default_hostname" {
  description = "Default hostname of the Azure Function App."
  value       = azurerm_linux_function_app.anomaly_detector_function_app.default_hostname
}

output "ml_endpoint_scoring_uri" {
  description = "Scoring URI of the Azure ML Managed Online Endpoint."
  value       = azurerm_machine_learning_inference_cluster.managed_endpoint.scoring_uri
}

output "ml_endpoint_primary_key" {
  description = "Primary key for the Azure ML Managed Online Endpoint (use with caution)."
  value       = azurerm_machine_learning_inference_cluster.managed_endpoint.primary_key
  sensitive   = true # Mark as sensitive so it's not shown in plan/apply output
}