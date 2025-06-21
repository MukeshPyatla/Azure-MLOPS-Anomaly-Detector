# src/models/score.py
import json
import numpy as np
import os
import joblib
import pandas as pd # Make sure pandas is installed in your scoring environment
from azureml.core.model import Model

# --- Global variables for model and features ---
model = None
feature_names = ['amount', 'transaction_hour'] # Must match features used during training

def init():
    """
    This function is called when the container is initialized.
    You can deserialize the model here to make it ready for inference.
    """
    global model
    # Azure ML automatically downloads the registered model to the 'AZUREML_MODEL_DIR' env var
    model_path = Model.get_model_path('anomaly-detection-model') # Name used during registration in train.py
    model = joblib.load(model_path)
    print(f"Model loaded from: {model_path}")

def run(raw_data):
    """
    This function is called for every real-time inference request.
    Args:
        raw_data: A JSON string representing the input data.
                  Expected format: [{"amount": 123.45, "transaction_hour": 14}] or [{"timestamp": "...", "amount": 123.45}]
                  The `run` function in `score.py` will expect the *pre-processed* features.
                  The Azure Function will perform the transformation to this format.
    Returns:
        A JSON object containing prediction results.
    """
    try:
        # The raw_data input to this run function *should* be the pre-processed features
        # sent by the Azure Function. So, we expect a list of dicts.
        data_list = json.loads(raw_data) # Expecting a list like [{"amount": ..., "transaction_hour": ...}]

        df_input = pd.DataFrame(data_list)

        # Ensure input has the correct features in the correct order
        if not all(feature in df_input.columns for feature in feature_names):
            raise ValueError(f"Input data missing required features. Expected: {feature_names}, Got: {df_input.columns.tolist()}")

        # Select and order features correctly
        X_inference = df_input[feature_names]

        # Predict anomaly scores (Isolation Forest outputs scores)
        # Lower score indicates higher anomaly likelihood
        anomaly_scores = model.decision_function(X_inference).tolist()

        # Optional: Classify as anomaly based on a threshold (e.g., score < 0 indicates anomaly by default IF)
        # Adjust threshold based on your model's performance requirements
        predictions = (np.array(anomaly_scores) < 0).astype(int).tolist() # IsolationForest scores <0 usually anomalies

        # You can enrich the output with original data or more details
        results = []
        for i in range(len(data_list)):
            result = data_list[i] # Use the already parsed and transformed input
            result['anomaly_score'] = anomaly_scores[i]
            result['is_anomaly_predicted'] = bool(predictions[i])
            results.append(result)

        return json.dumps(results)
    except Exception as e:
        error = str(e)
        print(f"Error during inference: {error}")
        return json.dumps({"error": error})

# Example usage for local testing (not run in actual Azure ML deployment)
if __name__ == '__main__':
    # This block is for local testing or debugging outside of Azure ML's deployment environment
    # In Azure ML, init() and run() are called by the service.
    init() # Manually call init for local testing

    # Sample pre-processed data that the Azure Function would send
    sample_data_good = '[{"amount": 100.0, "transaction_hour": 10}]'
    sample_data_anomaly = '[{"amount": 10000.0, "transaction_hour": 15}]'

    print(f"Good data prediction: {run(sample_data_good)}")
    print(f"Anomaly data prediction: {run(sample_data_anomaly)}")