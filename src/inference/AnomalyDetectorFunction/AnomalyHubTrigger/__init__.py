# src/inference/AnomalyDetectorFunction/AnomalyHubTrigger/__init__.py
import logging
import azure.functions as func
import json
import os
import requests
import pandas as pd # For pd.to_datetime

# --- Azure ML Endpoint Configuration ---
# These will be set as Application Settings in the Function App via Terraform
AML_ENDPOINT_URL = os.environ.get("AML_ENDPOINT_URL")
AML_ENDPOINT_KEY = os.environ.get("AML_ENDPOINT_KEY")

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {AML_ENDPOINT_KEY}',
    # 'azureml-model-id': 'anomaly-detection-model:1' # Optional: if you want to target a specific version. Omit for latest
}

# --- End Azure ML Endpoint Configuration ---

# Suppress verbose http logging from azure.core.pipeline
logging.getLogger('azure.core.pipeline.policies.http_logging_policy').setLevel(logging.WARNING)

async def main(events: str, context: func.Context):
    logging.info(f'Python EventHub trigger function processed {len(events)} events.')

    for event in events:
        try:
            event_body = event.get_body().decode('utf-8')
            logging.info(f'Processing event: {event_body}')

            # Your data_generator.py sends raw JSON string.
            # Event Hubs Capture wraps it in Avro. However, when an Azure Function
            # triggers from an Event Hub, it typically provides the *unwrapped* event body.
            # So, we expect a raw JSON string of a single transaction.
            transaction_data = json.loads(event_body)

            # --- Feature Extraction for Inference (must match score.py expectations) ---
            # The 'score.py' expects a list of dictionaries like [{"amount": ..., "transaction_hour": ...}]
            # so we create that payload here.
            inference_payload = [{
                "amount": transaction_data.get("amount"),
                "transaction_hour": pd.to_datetime(transaction_data.get("timestamp")).hour
            }]

            # Make request to Azure ML Endpoint
            response = requests.post(AML_ENDPOINT_URL, json=inference_payload, headers=headers)
            response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)

            predictions = response.json()
            logging.info(f"Transaction ID: {transaction_data.get('transaction_id')}, Prediction Response: {predictions}")

            # --- Process Prediction Results ---
            if predictions and predictions[0].get('is_anomaly_predicted'):
                # Log anomalies to Function App logs (which go to Application Insights)
                logging.warning(f"!!! ANOMALY DETECTED !!! ID: {transaction_data.get('transaction_id')}, Amount: {transaction_data.get('amount')}, Score: {predictions[0].get('anomaly_score')}")
                # Future: Send this anomaly record to a dedicated 'alerts' Event Hub or Azure Cosmos DB
                # for further processing or dashboarding.
            else:
                logging.info(f"Transaction ID: {transaction_data.get('transaction_id')} - Normal.")

        except Exception as e:
            logging.error(f"Error processing event: {e}. Event Body: {event.get_body().decode('utf-8')}")