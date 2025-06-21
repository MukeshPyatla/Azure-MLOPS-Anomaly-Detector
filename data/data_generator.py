# src/data/data_generator.py
import json
import time
import random
import datetime
from azure.eventhub import EventHubProducerClient, EventData

# --- Azure Event Hubs Configuration ---
EVENTHUB_FULLY_QUALIFIED_NAMESPACE = "YOUR_EVENTHUB_NAMESPACE_NAME.servicebus.windows.net" # e.g., "mlopsanomaly-eh-namespace.servicebus.windows.net"
EVENTHUB_NAME = "YOUR_EVENTHUB_NAME" # e.g., "mlopsanomaly-transactions-eh"
EVENTHUB_SEND_POLICY_PRIMARY_KEY = "YOUR_EVENTHUB_SEND_PRIMARY_KEY" # Get this from 'terraform output eventhub_send_primary_key'

# Connection string using Shared Access Key
# Format: Endpoint=sb://<NAMESPACE NAME>.servicebus.windows.net/;SharedAccessKeyName=<POLICY_NAME>;SharedAccessKey=<KEY>
CONNECTION_STR = f"Endpoint=sb://{EVENTHUB_FULLY_QUALIFIED_NAMESPACE}/;SharedAccessKeyName=SendPolicy;SharedAccessKey={EVENTHUB_SEND_POLICY_PRIMARY_KEY}"

producer = EventHubProducerClient.from_connection_string(
    conn_str=CONNECTION_STR,
    eventhub_name=EVENTHUB_NAME
)
# --- End Azure Event Hubs Configuration ---

def generate_transaction_data():
    transaction_id = str(random.randint(100000, 999999))
    user_id = str(random.randint(1000, 5000))
    amount = round(random.uniform(10.0, 1000.0), 2)
    timestamp = datetime.datetime.now().isoformat()
    is_fraud = False # Most transactions are not fraud

    # Introduce some anomalies for testing (e.g., very high amount for a specific user, or unusual time)
    if random.random() < 0.01: # 1% chance of fraud
        is_fraud = True
        amount = round(random.uniform(5000.0, 20000.0), 2) # High amount fraud

    return {
        "transaction_id": transaction_id,
        "user_id": user_id,
        "amount": amount,
        "timestamp": timestamp,
        "is_fraud": is_fraud,
        "ip_address": f"{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}",
        "device_type": random.choice(["mobile", "desktop", "tablet"]),
        "merchant_id": str(random.randint(1, 100))
    }

async def send_to_eventhub(record):
    event_data_batch = await producer.create_batch()
    event_data_batch.add(EventData(json.dumps(record)))
    try:
        await producer.send_batch(event_data_batch)
        print(f"Sent record: {record['transaction_id']} to Event Hub.")
    except Exception as e:
        print(f"Error sending record to Event Hub: {e}")

# Note: Event Hubs SDK uses async. Need an async runner.
import asyncio
async def main():
    while True:
        data = generate_transaction_data()
        await send_to_eventhub(data)
        await asyncio.sleep(random.uniform(0.1, 0.5)) # Send data every 0.1 to 0.5 seconds

if __name__ == "__main__":
    print(f"Starting data generation to Azure Event Hub: {EVENTHUB_NAME}")
    asyncio.run(main())