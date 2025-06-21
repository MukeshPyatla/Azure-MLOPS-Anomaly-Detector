# 🚀 End-to-End MLOps Pipeline for Real-time Anomaly Detection on Azure

![Project Status](https://img.shields.io/badge/Status-In%20Progress-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Cloud Provider](https://img.shields.io/badge/Cloud-Azure-0078D4?logo=azure)

---

## 📋 Table of Contents

* [1. Project Overview](#1-project-overview)
* [2. Business Problem & Impact](#2-business-problem--impact)
* [3. Architecture](#3-architecture)
* [4. Key Technologies](#4-key-technologies)
* [5. MLOps Principles & Features Demonstrated](#5-mlops-principles--features-demonstrated)
* [6. Getting Started / Local Setup](#6-getting-started--local-setup)
    * [Prerequisites](#prerequisites)
    * [Azure Authentication](#azure-authentication)
    * [Terraform Deployment](#terraform-deployment)
    * [Running the Data Generator](#running-the-data-generator)
* [7. Project Structure](#7-project-structure)
* [8. Phases of Development](#8-phases-of-development)
* [9. Results & Business Impact](#9-results--business-impact)
* [10. Future Enhancements](#10-future-enhancements)
* [11. License](#11-license)
* [12. Contact](#12-contact)

---

## 1. 🌟 Project Overview

This repository showcases a robust, end-to-end MLOps pipeline built entirely on **Microsoft Azure** for **real-time anomaly detection**. It covers every stage from data ingestion and processing to model training, deployment, monitoring, and automated retraining, all orchestrated with Infrastructure as Code (Terraform) and CI/CD principles. The project is designed to handle high-volume streaming data, making it applicable to critical use cases like fraud detection, network intrusion analysis, or IoT sensor anomaly flagging.

## 2. 📈 Business Problem & Impact

Modern enterprises contend with vast streams of data where identifying unusual patterns (anomalies) is critical but challenging. Traditional rule-based systems often fail to adapt to evolving threats or generate high false positives. This project addresses the need for:

* **Real-time Detection:** Identifying anomalies as they occur, enabling immediate action.
* **Scalability:** Handling massive data volumes without performance degradation.
* **Automation:** Minimizing manual intervention from infrastructure provisioning to model updates.
* **Reliability:** Ensuring consistent model performance and data quality in production.

**Business Impact:** By providing an automated and scalable anomaly detection system, this solution can directly lead to:
* **Reduced Financial Losses:** By quickly flagging fraudulent transactions.
* **Improved Security Posture:** By identifying unusual network access or insider threats.
* **Optimized Operations:** By detecting equipment malfunctions or operational inefficiencies proactively.
* **Cost Savings:** Through efficient resource utilization and automated workflows.

## 3. 🗺️ Architecture

The architecture diagram below illustrates the flow of data and machine learning operations within the Azure cloud environment.

![Azure MLOps Anomaly Detection Architecture Diagram](https://raw.githubusercontent.com/YOUR_USERNAME/mlops-anomaly-detector-azure/main/docs/architecture_diagram.png)

*(Consider adding a brief textual overview here similar to the one we outlined in our discussions, explaining the purpose of each major phase in the diagram.)*

## 4. 🛠️ Key Technologies

This project leverages a robust stack of Azure services and modern MLOps tools:

* **Cloud Platform:** Microsoft Azure
* **Infrastructure as Code (IaC):** Terraform
* **Streaming Ingestion:** Azure Event Hubs
* **Data Lake Storage:** Azure Data Lake Storage Gen2 (ADLS Gen2)
* **Data Transformation:** Azure Functions (for real-time ingestion to data lake), Azure Databricks / Azure Synapse Analytics / Azure Machine Learning Compute (for batch ETL / Feature Engineering)
* **Machine Learning Platform:** Azure Machine Learning (for training, model registry, endpoints)
* **Containerization:** Docker
* **Version Control:** Git, GitHub
* **CI/CD:** Azure DevOps Pipelines (or GitHub Actions)
* **Monitoring & Logging:** Azure Monitor, Azure Log Analytics
* **Programming Languages:** Python
* **ML Libraries:** Scikit-learn, Pandas, NumPy
* **MLOps Tools (Conceptual/Integration):** MLflow (for experiment tracking), DVC (for data/model versioning)

## 5. ✨ MLOps Principles & Features Demonstrated

This project showcases a holistic approach to MLOps, embodying several key principles:

* **Automated Infrastructure Provisioning:** All Azure resources defined and deployed via Terraform, ensuring consistency and reproducibility.
* **Real-time Data Ingestion:** Handling high-throughput data streams using Azure Event Hubs.
* **Scalable Data Lake:** Centralized, cost-effective storage for raw and processed data on ADLS Gen2.
* **Automated Data Processing:** Serverless functions and/or managed services for efficient data transformation.
* **Model Versioning & Registry:** Managing different versions of ML models for traceability and governance using Azure Machine Learning's Model Registry.
* **Experiment Tracking:** Ability to track model training runs, parameters, and metrics (conceptually with MLflow/Azure ML's native capabilities).
* **CI/CD for ML (CI/CD4ML):** Automating the retraining, testing, and deployment of new model versions through pipeline triggers.
* **Model Monitoring:** Continuous monitoring of model performance (e.g., prediction drift, data drift, latency) and data quality in production.
* **Alerting:** Setting up notifications for critical issues related to data quality, model performance, or infrastructure health.
* **Reproducibility:** Version control for code, infrastructure, and potentially data/models (using DVC concepts).

## 6. 🚀 Getting Started / Local Setup

Follow these steps to set up the project locally and deploy the infrastructure to your Azure subscription.

### Prerequisites

Before you begin, ensure you have the following installed:

* **Git:** [Download Git](https://git-scm.com/downloads)
* **Python 3.8+:** [Python Downloads](https://www.python.org/downloads/)
* **pip (Python package installer):** Comes with Python.
* **Terraform:** [Terraform Downloads](https://www.terraform.io/downloads.html)
* **Azure CLI:** [Install Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
* **Azure Functions Core Tools v4:** `npm install -g azure-functions-core-tools@4 --unsafe-perm true` (Requires Node.js & npm)

### Azure Authentication

You need to authenticate Terraform and your Python scripts with your Azure account.

1.  **Login via Azure CLI:**
    ```bash
    az login
    # Follow the browser prompts to authenticate.
    ```
2.  **Set your default Azure subscription (if you have multiple):**
    ```bash
    az account list --output table # Find your subscription name or ID
    az account set --subscription "Your Subscription Name or ID"
    ```

### Terraform Deployment (Phase 1 Infrastructure)

Navigate to the Terraform directory and deploy the core resources.

1.  **Navigate to the Azure Infrastructure directory:**
    ```bash
    cd infrastructure/azure
    ```
2.  **Initialize Terraform:**
    ```bash
    terraform init
    ```
3.  **Review the deployment plan:**
    ```bash
    terraform plan
    ```
    * **ACTION REQUIRED:** Carefully review the output of `terraform plan`. It shows exactly what resources will be created, modified, or destroyed. Ensure it aligns with your expectations.
4.  **Deploy the infrastructure:**
    ```bash
    terraform apply
    # Type 'yes' when prompted to confirm the deployment.
    ```
5.  **Retrieve outputs:** After successful deployment, Terraform will output key values. Copy these as you'll need them for your data generator and Azure Function.
    ```bash
    terraform output
    ```
    *(**ACTION REQUIRED:** Note down `eventhub_send_connection_string`, `eventhub_name`, `storage_account_name`, `storage_container_name`)*

### Running the Data Generator

This Python script sends simulated transaction data to your deployed Azure Event Hub.

1.  **Navigate to the data generator script directory (from project root):**
    ```bash
    cd src/data
    ```
2.  **Install Python dependencies:**
    ```bash
    pip install -r ../../requirements.txt # Installs azure-eventhub, azure-storage-blob, etc.
    ```
3.  **Set environment variables (CRITICAL for connection string!):**
    * **WARNING:** For production, use Azure Key Vault or Managed Identities. For local development, setting environment variables is acceptable.
    * **Replace `YOUR_EVENTHUB_CONNECTION_STRING` with the actual value from `terraform output eventhub_send_connection_string`.**
    * **Replace `YOUR_EVENTHUB_NAME` with the actual value from `terraform output eventhub_name`.**
    ```bash
    # For Linux/macOS:
    export EVENTHUB_CONNECTION_STR="YOUR_EVENTHUB_CONNECTION_STRING"
    export EVENTHUB_NAME="YOUR_EVENTHUB_NAME"
    # For Windows (Command Prompt):
    # set EVENTHUB_CONNECTION_STR="YOUR_EVENTHUB_CONNECTION_STRING"
    # set EVENTHUB_NAME="YOUR_EVENTHUB_NAME"
    # For Windows (PowerShell):
    # $env:EVENTHUB_CONNECTION_STR="YOUR_EVENTHUB_CONNECTION_STRING"
    # $env:EVENTHUB_NAME="YOUR_EVENTHUB_NAME"
    ```
4.  **Run the data generator:**
    ```bash
    python data_generator.py
    ```
    * You should see messages in your terminal indicating records being sent to Event Hub. Let it run for a few minutes.

## 7. 📁 Project Structure