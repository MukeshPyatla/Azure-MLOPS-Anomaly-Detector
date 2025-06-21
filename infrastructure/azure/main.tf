# infrastructure/azure/main.tf

# --- Resource Group ---
resource "azurerm_resource_group" "rg" {
  name     = "${var.project_name_prefix}-rg"
  location = var.location
}

# --- Storage Account for Raw Data Lake (Blob Storage) ---
resource "azurerm_storage_account" "raw_data_lake_sa" {
  name                     = "${var.project_name_prefix}rawdatalake" # Storage account names must be globally unique, all lowercase, 3-24 chars
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "GRS" # Geo-Redundant Storage for durability
  public_network_access_enabled = true # For initial testing, can restrict later

  tags = {
    Environment = "Dev"
    Project     = var.project_name_prefix
    ManagedBy   = "Terraform"
  }
}

# Blob Container inside the Storage Account for raw data
resource "azurerm_storage_container" "raw_data_blob_container" {
  name                  = "raw-transactions"
  storage_account_name  = azurerm_storage_account.raw_data_lake_sa.name
  container_access_type = "private" # Restrict public access

  tags = {
    Environment = "Dev"
    Project     = var.project_name_prefix
    ManagedBy   = "Terraform"
  }
}

# --- Azure Event Hubs Namespace ---
# A container for Event Hubs
resource "azurerm_eventhub_namespace" "eh_namespace" {
  name                = "${var.project_name_prefix}-eh-namespace"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = "Standard" # Basic is cheaper, Standard has more features
  capacity            = 1 # Throughput units

  tags = {
    Environment = "Dev"
    Project     = var.project_name_prefix
    ManagedBy   = "Terraform"
  }
}

# --- Azure Event Hub (the stream itself) ---
resource "azurerm_eventhub" "transaction_eventhub" {
  name                = "${var.project_name_prefix}-transactions-eh"
  namespace_name      = azurerm_eventhub_namespace.eh_namespace.name
  resource_group_name = azurerm_resource_group.rg.name
  partition_count     = 1 # Start with 1, scale up if needed
  message_retention_in_days = 1 # Data retention

  # Enable Capture Feature to automatically write to Blob Storage
  capture_description {
    enabled             = true
    encoding            = "Avro" # Or "AvroDeflate"
    interval_in_seconds = 300 # Capture every 5 minutes
    size_limit_in_bytes = 10485760 # Capture when 10MB or 5 mins reached (10MB)
    destination {
      name                = "EventHubCapture" # Must be "EventHubCapture"
      archive_name_format = "{Namespace}/{EventHub}/{PartitionId}/{Year}/{Month}/{Day}/{Hour}/{Minute}/{Second}"
      blob_container_name = azurerm_storage_container.raw_data_blob_container.name
      storage_account_id  = azurerm_storage_account.raw_data_lake_sa.id
    }
  }

  tags = {
    Environment = "Dev"
    Project     = var.project_name_prefix
    ManagedBy   = "Terraform"
  }
}

# --- Authorization Rule for Event Hub (for data producer) ---
# Grants send permissions for your data generator script
resource "azurerm_eventhub_namespace_authorization_rule" "send_rule" {
  name                = "SendPolicy"
  namespace_name      = azurerm_eventhub_namespace.eh_namespace.name
  resource_group_name = azurerm_resource_group.rg.name
  listen              = false
  send                = true
  manage              = false
}

# OR, if you want a rule for the specific Event Hub:
resource "azurerm_eventhub_authorization_rule" "eventhub_send_rule" {
  name                = "SendPolicy"
  namespace_name      = azurerm_eventhub_namespace.eh_namespace.name
  eventhub_name       = azurerm_eventhub.transaction_eventhub.name
  resource_group_name = azurerm_resource_group.rg.name
  listen              = false
  send                = true
  manage              = false
}


# --- Storage Account for Processed Data Lake / Feature Store ---
resource "azurerm_storage_account" "processed_data_lake_sa" {
  name                     = "${var.project_name_prefix}processedlake" # Globally unique, all lowercase, 3-24 chars
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "GRS"

  tags = {
    Environment = "Dev"
    Project     = var.project_name_prefix
    ManagedBy   = "Terraform"
  }
}

resource "azurerm_storage_container" "processed_data_blob_container" {
  name                  = "processed-transactions"
  storage_account_name  = azurerm_storage_account.processed_data_lake_sa.name
  container_access_type = "private"

  tags = {
    Environment = "Dev"
    Project     = var.project_name_prefix
    ManagedBy   = "Terraform"
  }
}

# --- Azure Databricks Workspace ---
resource "azurerm_databricks_workspace" "mlops_workspace" {
  name                = "${var.project_name_prefix}-databricks"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "standard" # Or "premium" for more features/security

  # Optionally, if running in a VNet:
  # managed_resource_group_name = "${azurerm_resource_group.rg.name}-managed" # Databricks creates its own RG
  # custom_virtual_network_id     = "/subscriptions/YOUR_SUB_ID/resourceGroups/YOUR_RG/providers/Microsoft.Network/virtualNetworks/YOUR_VNET"
  # public_ip_name                = "..." # Required for VNet injection

  tags = {
    Environment = "Dev"
    Project     = var.project_name_prefix
    ManagedBy   = "Terraform"
  }
}

# --- Azure Machine Learning Workspace ---
resource "azurerm_machine_learning_workspace" "ml_workspace" {
  name                          = "${var.project_name_prefix}-ml-workspace"
  location                      = azurerm_resource_group.rg.location
  resource_group_name           = azurerm_resource_group.rg.name
  application_insights_id       = azurerm_application_insights.ml_app_insights.id # For logging & monitoring
  key_vault_id                  = azurerm_key_vault.ml_key_vault.id # For secrets management
  storage_account_id            = azurerm_storage_account.processed_data_lake_sa.id # Associates default storage
  identity {
    type = "SystemAssigned" # Azure ML Workspace managed identity
  }
  sku_name                      = "Basic" # Or "Standard", "Enterprise"

  tags = {
    Environment = "Dev"
    Project     = var.project_name_prefix
    ManagedBy   = "Terraform"
  }
}

# Supporting resources for Azure ML Workspace
# Application Insights for monitoring
resource "azurerm_application_insights" "ml_app_insights" {
  name                = "${var.project_name_prefix}-ml-appinsights"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  application_type    = "web"
  retention_in_days   = 90
}

# Key Vault for secrets management
resource "azurerm_key_vault" "ml_key_vault" {
  name                        = "${var.project_name_prefix}-kv" # Key Vault names must be globally unique
  location                    = azurerm_resource_group.rg.location
  resource_group_name         = azurerm_resource_group.rg.name
  tenant_id                   = data.azurerm_client_config.current.tenant_id
  sku_name                    = "standard"
  soft_delete_retention_days  = 7 # Minimum for soft delete

  # Grant the deploying user access to Key Vault for initial setup/testing
  # For production, you'd use a service principal or managed identity
  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = data.azurerm_client_config.current.object_id # Your Azure CLI user's object ID

    key_permissions = ["Get", "List"]
    secret_permissions = ["Get", "List", "Set", "Delete"]
    certificate_permissions = ["Get", "List"]
  }
}

# Data source to get current client configuration (tenant_id, object_id)
data "azurerm_client_config" "current" {}

# Grant Azure ML Workspace's managed identity Storage Blob Data Contributor role
# This allows AML to read from/write to your data lake storage accounts
resource "azurerm_role_assignment" "ml_workspace_storage_access" {
  scope                = azurerm_storage_account.processed_data_lake_sa.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_machine_learning_workspace.ml_workspace.identity[0].principal_id
}

resource "azurerm_role_assignment" "ml_workspace_raw_storage_access" {
  scope                = azurerm_storage_account.raw_data_lake_sa.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_machine_learning_workspace.ml_workspace.identity[0].principal_id
}

# --- Azure Log Analytics Workspace ---
resource "azurerm_log_analytics_workspace" "logs" {
  name                = "${var.project_name_prefix}-log-workspace"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = "PerGB2018" # Or "Consumption"

  tags = {
    Environment = "Dev"
    Project     = var.project_name_prefix
    ManagedBy   = "Terraform"
  }
}

# --- Azure Monitor Action Group (for alerts) ---
# This defines who gets notified (e.g., email)
resource "azurerm_monitor_action_group" "mlops_alerts" {
  name                = "${var.project_name_prefix}-mlops-alerts"
  resource_group_name = azurerm_resource_group.rg.name
  short_name          = "${var.project_name_prefix}alerts"

  email_receiver {
    name          = "primary_email_receiver"
    email_address = "your.email@example.com" # REPLACE with your actual email!
  }

  tags = {
    Environment = "Dev"
    Project     = var.project_name_prefix
    ManagedBy   = "Terraform"
  }
}

# --- Azure Monitor Metric Alert: ML Endpoint Latency ---
# Alerts if the endpoint's request latency goes too high
resource "azurerm_monitor_metric_alert" "ml_endpoint_high_latency_alert" {
  name                = "${var.project_name_prefix}-ep-high-latency"
  resource_group_name = azurerm_resource_group.rg.name
  scopes              = [azurerm_machine_learning_inference_cluster.managed_endpoint.id]
  description         = "Alerts if ML Endpoint request latency is consistently high."
  severity            = 2 # 0-4 (0=Critical, 4=Verbose)
  frequency           = "PT5M" # Check every 5 minutes
  window_size         = "PT5M" # Look at data over the last 5 minutes
  enabled             = true
  action_group_id     = azurerm_monitor_action_group.mlops_alerts.id

  criteria {
    metric_namespace = "Microsoft.MachineLearningServices/workspaces/onlineEndpoints"
    metric_name      = "RequestLatency"
    aggregation      = "Average"
    operator         = "GreaterThan"
    threshold        = 1000 # Milliseconds (e.g., alert if average latency > 1 second)
    dimension {
      name     = "DeploymentName"
      operator = "Include"
      values   = [azurerm_machine_learning_online_deployment.anomaly_model_deployment.name]
    }
  }

  tags = {
    Environment = "Dev"
    Project     = var.project_name_prefix
    ManagedBy   = "Terraform"
  }
}

# --- Azure Monitor Log Alert: Function App Errors ---
# Alerts if the Function App logs a high number of errors indicating processing issues
resource "azurerm_monitor_scheduled_query_rules_alert" "function_app_errors_alert" {
  name                = "${var.project_name_prefix}-func-app-errors"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  severity            = 2
  frequency           = "PT5M"
  time_window         = "PT5M" # Look for errors in last 5 minutes
  enabled             = true
  data_source_id      = azurerm_log_analytics_workspace.logs.id # Link to Log Analytics Workspace

  # Kusto Query Language (KQL) to find errors in Function App logs
  criteria {
    type = "LogQuery"
    metric_trigger {
      metric_column = "Count"
      metric_trigger_type = "NumberOfViolations"
      operator = "GreaterThan"
      threshold = 5 # Alert if more than 5 errors in 5 minutes
    }
    query = <<QUERY
    AppTraces
    | where AppRoleName == "${azurerm_linux_function_app.anomaly_detector_function_app.name}"
    | where SeverityLevel == "2" // Error level
    | summarize Count=count() by bin(TimeGenerated, 5m)
    | project Count
    QUERY
  }
  action {
    action_group = [azurerm_monitor_action_group.mlops_alerts.id]
  }

  tags = {
    Environment = "Dev"
    Project     = var.project_name_prefix
    ManagedBy   = "Terraform"
  }
}

# Data source to associate Application Insights with Log Analytics Workspace
resource "azurerm_application_insights_workbook" "ml_app_insights_workbook_association" {
  name                = "${azurerm_application_insights.ml_app_insights.name}-workbook" # Example name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  category            = "general"
  description         = "MLOps Anomaly Detector Monitoring Dashboard"
  display_name        = "MLOps Anomaly Detector Dashboard"
  tags = {
    Environment = "Dev"
    Project     = var.project_name_prefix
    ManagedBy   = "Terraform"
  }
}

# Ensure Application Insights sends data to Log Analytics
resource "azurerm_application_insights_standard_web_test" "ml_app_insights_web_test" {
  name                = "${azurerm_application_insights.ml_app_insights.name}-web-test"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  application_insights_id = azurerm_application_insights.ml_app_insights.id
  geo_locations       = ["us-east"]
  request {
    url = azurerm_machine_learning_inference_cluster.managed_endpoint.scoring_uri # Ping the ML endpoint
  }
  tags = {
    Environment = "Dev"
    Project     = var.project_name_prefix
    ManagedBy   = "Terraform"
  }
}
# --- Azure Function App related resources ---

# Storage account for the Function App's internal use (logs, code, triggers)
resource "azurerm_storage_account" "function_app_sa" {
  name                     = "${var.project_name_prefix}functionsa" # Globally unique, all lowercase
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS" # Locally-Redundant Storage is fine for function app storage

  tags = {
    Environment = "Dev"
    Project     = var.project_name_prefix
    ManagedBy   = "Terraform"
  }
}

# App Service Plan for the Function App (defines compute resources)
resource "azurerm_app_service_plan" "function_app_plan" {
  name                = "${var.project_name_prefix}-function-plan"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  kind                = "FunctionApp"
  sku {
    tier = "Consumption" # Serverless plan (cost-effective, scales automatically)
    size = "Y1" # Required for Consumption plan
  }

  tags = {
    Environment = "Dev"
    Project     = var.project_name_prefix
    ManagedBy   = "Terraform"
  }
}

# The Azure Function App itself
resource "azurerm_linux_function_app" "anomaly_detector_function_app" {
  name                          = "${var.project_name_prefix}-anomaly-func" # Globally unique
  location                      = azurerm_resource_group.rg.location
  resource_group_name           = azurerm_resource_group.rg.name
  service_plan_id               = azurerm_app_service_plan.function_app_plan.id
  storage_account_name          = azurerm_storage_account.function_app_sa.name
  storage_account_access_key    = azurerm_storage_account.function_app_sa.primary_access_key
  os_type                       = "linux"
  functions_extension_version   = "~4" # Latest stable version
  app_settings = {
    # Connection string for the Event Hub trigger. Terraform accesses the output from Phase 1.
    "EventHubConnection" = azurerm_eventhub_namespace_authorization_rule.send_rule.primary_connection_string
    "FUNCTIONS_WORKER_RUNTIME" = "python"
    "AML_ENDPOINT_URL"         = azurerm_machine_learning_inference_cluster.managed_endpoint.scoring_uri # Will be created below
    "AML_ENDPOINT_KEY"         = azurerm_machine_learning_inference_cluster.managed_endpoint.primary_key # Will be created below
    "WEBSITES_ENABLE_APP_SERVICE_STORAGE" = "false" # Recommended for consumption plans
  }

  site_config {
    application_stack {
      python_version = "3.9" # Match your function's Python version, consistent with env.yml if possible
    }
  }

  tags = {
    Environment = "Dev"
    Project     = var.project_name_prefix
    ManagedBy   = "Terraform"
  }
}

# --- Azure ML Managed Online Endpoint & Deployment ---

# Managed Online Endpoint (the API Gateway for your model)
# This is where your model will be exposed as an API
resource "azurerm_machine_learning_inference_cluster" "managed_endpoint" {
  name                = "${var.project_name_prefix}-anomaly-ep" # Globally unique endpoint name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  type                = "ManagedOnline" # For real-time managed deployments

  # Default SKU (Standard_DS2_v2 is common for small deployments)
  sku_name = "Default"
  tags = {
    Environment = "Dev"
    Project     = var.project_name_prefix
    ManagedBy   = "Terraform"
  }
}

# Managed Online Deployment (deploys a specific model version to the endpoint)
# This associates your registered model, scoring code, and environment with the endpoint
resource "azurerm_machine_learning_online_deployment" "anomaly_model_deployment" {
  name                         = "default" # Name of the deployment under the endpoint (e.g., 'default', 'blue', 'green')
  endpoint_id                  = azurerm_machine_learning_inference_cluster.managed_endpoint.id
  instance_count               = 1 # Number of instances for your deployment
  instance_type                = "Standard_DS2_v2" # Choose VM size based on model size/traffic/cost

  # Reference to the registered model from Phase 3
  model_id                     = azurerm_machine_learning_model.registered_anomaly_model.id

  # Scoring script and environment definition
  container_registry_enabled   = false # Use Azure ML's environment creation, not custom registry
  code_configuration {
    code_id = azurerm_machine_learning_code_version.anomaly_model_code.id # Link to uploaded code asset
  }
  environment_id = azurerm_machine_learning_environment_version.anomaly_model_env.id # Link to uploaded env asset

  tags = {
    Environment = "Dev"
    Project     = var.project_name_prefix
    ManagedBy   = "Terraform"
  }
}

# --- Resources for AML Deployment Artifacts (Code and Environment Assets) ---
# These Terraform resources push your local 'score.py' and 'conda_env.yml' to Azure ML assets

# Azure ML Code Asset (for score.py)
resource "azurerm_machine_learning_code_version" "anomaly_model_code" {
  name                  = "${var.project_name_prefix}-anomaly-score-code"
  version               = "1" # Start with version 1, increment for updates
  resource_group_name   = azurerm_resource_group.rg.name
  workspace_name        = azurerm_machine_learning_workspace.ml_workspace.name
  # The asset_path is where the code will be stored in AML's default storage.
  # base_path is the relative path from where Terraform is run to the directory containing score.py
  base_path             = "${path.module}/../../src/models" # Relative path to src/models
  asset_path            = "src/models" # Path within Azure ML's default blob storage for this asset
}

# Azure ML Environment Asset (for conda_env.yml)
resource "azurerm_machine_learning_environment_version" "anomaly_model_env" {
  name                  = "${var.project_name_prefix}-anomaly-env"
  version               = "1" # Start with version 1, increment for updates
  resource_group_name   = azurerm_resource_group.rg.name
  workspace_name        = azurerm_machine_learning_workspace.ml_workspace.name
  conda_file_path       = "${path.module}/../../src/models/conda_env.yml" # Relative path to conda_env.yml
  image_name            = "mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04:latest" # Base Docker image for ML environment
  os_type               = "Linux"
  inference_config { # Needed for real-time inference deployments
    scoring_script = "score.py" # The name of your scoring script within the uploaded code asset
  }
}

# Data source to get the ID of the registered model from Phase 3
# This dynamically fetches the *latest* registered model with the given name
data "azurerm_machine_learning_model" "registered_anomaly_model" {
  name                  = "anomaly-detection-model" # Name used during registration in train.py
  # If you need a specific version, use 'version = "X"' instead of data lookup
  resource_group_name   = azurerm_resource_group.rg.name
  workspace_name        = azurerm_machine_learning_workspace.ml_workspace.name
}