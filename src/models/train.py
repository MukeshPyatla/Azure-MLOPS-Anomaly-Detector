# src/models/train.py
import argparse
import os
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib # For saving the model

# Azure ML SDK imports
from azureml.core import Workspace, Dataset, Model, Run
from azureml.data.datapath import DataPath

# --- Configuration Variables (will be passed as job parameters) ---
# These will typically come from environment variables or Azure ML parameters
# For local testing, you might hardcode or use os.getenv
PROCESSED_BLOB_CONTAINER_NAME = os.environ.get("PROCESSED_BLOB_CONTAINER_NAME", "processed-transactions") # From Terraform output
PROCESSED_STORAGE_ACCOUNT_NAME = os.environ.get("PROCESSED_STORAGE_ACCOUNT_NAME", "mlopsanomalyprocessedlake") # From Terraform output
# --- End Configuration ---

# --- Anomaly Detection Threshold (example) ---
# For IsolationForest, a low score indicates an anomaly. This threshold might need tuning.
ANOMALY_SCORE_THRESHOLD = 0.05 # Lower score = higher anomaly likelihood

def get_dataset(ws, storage_account_name, container_name, path=""):
    """Gets data from the processed data lake."""
    datastore = ws.get_default_datastore()
    data_path = DataPath(datastore, os.path.join(container_name, path))
    tab_ds = Dataset.Tabular.from_parquet_files(path=data_path)
    return tab_ds.to_pandas_dataframe()

def train_model(df):
    # Features for Isolation Forest (basic set, expand as needed)
    # Assuming df has 'amount', 'transaction_hour'
    features = ['amount', 'transaction_hour']
    X = df[features]

    # Initialize and train Isolation Forest model
    # contamination: proportion of outliers in the data set (estimate)
    # A higher contamination value will result in more anomalies being detected.
    # For real fraud, this is often a very small number (e.g., 0.001)
    model = IsolationForest(contamination=0.01, random_state=42, n_estimators=100) # 1% assumed contamination
    model.fit(X)
    return model

def evaluate_model(model, df, run):
    # Predict raw anomaly scores (lower is more anomalous)
    df['anomaly_score'] = model.decision_function(df[['amount', 'transaction_hour']])

    # For evaluation, we assume 'is_fraud' provides true labels for anomalies
    # In unsupervised anomaly detection, you typically rely on clustering/profiling
    # For this project, 'is_fraud' provides a ground truth for basic evaluation.
    df['prediction'] = (df['anomaly_score'] < 0).astype(int) # IsolationForest scores <0 usually anomalies

    # Filter to where 'is_fraud' is true for more relevant metrics if dataset is imbalanced
    # Or, focus on precision/recall for the positive class (anomalies)
    y_true = df['is_fraud'].astype(int) # Convert boolean to int (True=1, False=0)
    y_pred = df['prediction']

    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, zero_division=0) # zero_division handles no positive predictions
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)

    print(f"Model Metrics:")
    print(f"  Accuracy: {accuracy:.4f}")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall: {recall:.4f}")
    print(f"  F1-Score: {f1:.4f}")

    # Log metrics to Azure ML Run
    run.log("accuracy", accuracy)
    run.log("precision", precision)
    run.log("recall", recall)
    run.log("f1_score", f1)
    run.log("anomaly_score_threshold", ANOMALY_SCORE_THRESHOLD)

if __name__ == "__main__":
    print("Starting model training script...")

    # Get current run context
    run = Run.get_context()
    ws = run.experiment.workspace

    # Get processed data from Blob Storage
    # The path should match how your Glue job writes to processed_transactions/
    # You might need to adjust the path to point to a specific hour's data or use a wildcard for all parquet files
    # For simplicity, let's assume it reads all parquet files within the container path for now.
    processed_data_path_in_datastore = os.path.join(PROCESSED_BLOB_CONTAINER_NAME, "processed_transactions/")
    df_processed = get_dataset(ws, PROCESSED_STORAGE_ACCOUNT_NAME, processed_data_path_in_datastore)

    # Drop rows with NaN if any (IsolationForest does not handle NaNs)
    df_processed = df_processed.dropna(subset=['amount', 'transaction_hour'])

    if df_processed.empty:
        raise ValueError("Processed DataFrame is empty. Cannot train model.")

    print(f"Loaded {len(df_processed)} rows for training.")

    # Train model
    print("Training IsolationForest model...")
    model = train_model(df_processed)
    print("Model training complete.")

    # Evaluate model
    print("Evaluating model...")
    evaluate_model(model, df_processed.copy(), run) # Use a copy to avoid modifying original df for evaluation

    # Save model locally
    model_filename = "anomaly_isolation_forest_model.joblib"
    joblib.dump(model, model_filename)
    print(f"Model saved locally as {model_filename}")

    # Register model in Azure ML Model Registry
    print("Registering model in Azure ML Model Registry...")
    registered_model = Model.register(
        workspace=ws,
        model_path=model_filename, # Path to the saved model file
        model_name="anomaly-detection-model",
        description="Isolation Forest model for transaction anomaly detection",
        tags={"model_type": "anomaly_detection", "algorithm": "IsolationForest"},
        properties={"accuracy": run.get_metrics().get("accuracy"), # Access metrics from the run
                    "precision": run.get_metrics().get("precision")}
    )
    print(f"Model registered with ID: {registered_model.id}, Version: {registered_model.version}")

    # Signal completion
    run.complete()