import streamlit as st
import pandas as pd
import numpy as np
import json
import datetime
import random
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib
import io
import base64

# Page configuration
st.set_page_config(
    page_title="Azure MLOps Anomaly Detector",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .anomaly-alert {
        background-color: #ffebee;
        color: #c62828;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #c62828;
    }
    .normal-alert {
        background-color: #e8f5e8;
        color: #2e7d32;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2e7d32;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def generate_synthetic_data(n_samples=1000):
    """Generate synthetic transaction data for demonstration"""
    np.random.seed(42)
    
    # Generate normal transactions
    normal_amounts = np.random.normal(100, 50, int(n_samples * 0.95))
    normal_hours = np.random.randint(0, 24, int(n_samples * 0.95))
    
    # Generate anomalous transactions
    anomaly_amounts = np.random.normal(5000, 2000, int(n_samples * 0.05))
    anomaly_hours = np.random.choice([0, 1, 2, 3, 22, 23], int(n_samples * 0.05))  # Unusual hours
    
    # Combine data
    amounts = np.concatenate([normal_amounts, anomaly_amounts])
    hours = np.concatenate([normal_hours, anomaly_hours])
    
    # Create DataFrame
    data = []
    for i in range(len(amounts)):
        transaction_id = f"TXN{str(i).zfill(6)}"
        user_id = f"USER{random.randint(1000, 5000)}"
        timestamp = datetime.datetime.now() - datetime.timedelta(hours=random.randint(0, 24*7))
        
        # Determine if this is actually an anomaly based on amount and hour
        is_anomaly = amounts[i] > 1000 or hours[i] in [0, 1, 2, 3, 22, 23]
        
        data.append({
            'transaction_id': transaction_id,
            'user_id': user_id,
            'amount': round(amounts[i], 2),
            'transaction_hour': hours[i],
            'timestamp': timestamp,
            'is_anomaly': is_anomaly,
            'ip_address': f"{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}",
            'device_type': random.choice(["mobile", "desktop", "tablet"]),
            'merchant_id': str(random.randint(1, 100))
        })
    
    return pd.DataFrame(data)

@st.cache_resource
def train_anomaly_model(data):
    """Train Isolation Forest model for anomaly detection"""
    # Prepare features
    features = ['amount', 'transaction_hour']
    X = data[features]
    
    # Train model
    model = IsolationForest(
        contamination=0.05,  # 5% contamination
        random_state=42,
        n_estimators=100
    )
    model.fit(X)
    
    return model, features

def predict_anomaly(model, features, transaction_data):
    """Predict anomaly for given transaction data"""
    # Prepare input data
    input_df = pd.DataFrame([transaction_data])
    X_input = input_df[features]
    
    # Get anomaly score (lower = more anomalous)
    anomaly_score = model.decision_function(X_input)[0]
    is_anomaly = anomaly_score < 0
    
    return {
        'anomaly_score': anomaly_score,
        'is_anomaly': is_anomaly,
        'confidence': abs(anomaly_score)
    }

def create_visualizations(data, model, features):
    """Create various visualizations for the data and model"""
    
    # 1. Amount vs Hour scatter plot
    fig_scatter = px.scatter(
        data, 
        x='transaction_hour', 
        y='amount',
        color='is_anomaly',
        title='Transaction Amount vs Hour (Anomalies Highlighted)',
        labels={'transaction_hour': 'Hour of Day', 'amount': 'Transaction Amount ($)'},
        color_discrete_map={True: '#ff4444', False: '#4444ff'}
    )
    fig_scatter.update_layout(height=400)
    
    # 2. Amount distribution
    fig_hist = px.histogram(
        data,
        x='amount',
        nbins=50,
        title='Transaction Amount Distribution',
        labels={'amount': 'Transaction Amount ($)', 'count': 'Frequency'}
    )
    fig_hist.update_layout(height=400)
    
    # 3. Hour distribution
    fig_hour = px.bar(
        data['transaction_hour'].value_counts().reset_index(),
        x='index',
        y='transaction_hour',
        title='Transaction Volume by Hour',
        labels={'index': 'Hour of Day', 'transaction_hour': 'Number of Transactions'}
    )
    fig_hour.update_layout(height=400)
    
    # 4. Model predictions visualization
    predictions = model.predict(data[features])
    data_with_predictions = data.copy()
    data_with_predictions['model_prediction'] = predictions == -1  # -1 means anomaly in Isolation Forest
    
    fig_model = px.scatter(
        data_with_predictions,
        x='transaction_hour',
        y='amount',
        color='model_prediction',
        title='Model Predictions vs Actual Anomalies',
        labels={'transaction_hour': 'Hour of Day', 'amount': 'Transaction Amount ($)'},
        color_discrete_map={True: '#ff4444', False: '#4444ff'}
    )
    fig_model.update_layout(height=400)
    
    return fig_scatter, fig_hist, fig_hour, fig_model

def main():
    # Header
    st.markdown('<h1 class="main-header">🚀 Azure MLOps Anomaly Detector</h1>', unsafe_allow_html=True)
    st.markdown("### Real-time Anomaly Detection for Financial Transactions")
    
    # Sidebar
    st.sidebar.title("Configuration")
    
    # Data generation
    st.sidebar.subheader("Data Generation")
    n_samples = st.sidebar.slider("Number of samples", 100, 5000, 1000)
    
    if st.sidebar.button("Generate New Data"):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.rerun()
    
    # Generate data
    with st.spinner("Generating synthetic transaction data..."):
        data = generate_synthetic_data(n_samples)
    
    # Train model
    with st.spinner("Training anomaly detection model..."):
        model, features = train_anomaly_model(data)
    
    # Main content
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Transactions", len(data))
    
    with col2:
        st.metric("Anomalies Detected", data['is_anomaly'].sum())
    
    with col3:
        anomaly_rate = (data['is_anomaly'].sum() / len(data)) * 100
        st.metric("Anomaly Rate", f"{anomaly_rate:.1f}%")
    
    with col4:
        avg_amount = data['amount'].mean()
        st.metric("Avg Transaction", f"${avg_amount:.2f}")
    
    # Tabs for different functionalities
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Data Analysis", "🔍 Live Detection", "📈 Model Performance", "📋 About"])
    
    with tab1:
        st.subheader("Data Analysis")
        
        # Create visualizations
        fig_scatter, fig_hist, fig_hour, fig_model = create_visualizations(data, model, features)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(fig_scatter, use_container_width=True)
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col2:
            st.plotly_chart(fig_hour, use_container_width=True)
            st.plotly_chart(fig_model, use_container_width=True)
        
        # Data table
        st.subheader("Sample Data")
        st.dataframe(data.head(10), use_container_width=True)
    
    with tab2:
        st.subheader("Live Anomaly Detection")
        st.write("Enter transaction details to detect anomalies in real-time:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            amount = st.number_input("Transaction Amount ($)", min_value=0.01, max_value=100000.0, value=100.0, step=0.01)
            hour = st.slider("Transaction Hour", 0, 23, 12)
        
        with col2:
            user_id = st.text_input("User ID", value="USER1234")
            device_type = st.selectbox("Device Type", ["mobile", "desktop", "tablet"])
        
        # Create transaction data
        transaction_data = {
            'amount': amount,
            'transaction_hour': hour,
            'user_id': user_id,
            'device_type': device_type,
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        if st.button("🔍 Detect Anomaly", type="primary"):
            # Get prediction
            prediction = predict_anomaly(model, features, transaction_data)
            
            # Display results
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Transaction Details")
                st.json(transaction_data)
            
            with col2:
                st.markdown("### Detection Results")
                
                if prediction['is_anomaly']:
                    st.markdown('<div class="anomaly-alert">🚨 ANOMALY DETECTED</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="normal-alert">✅ NORMAL TRANSACTION</div>', unsafe_allow_html=True)
                
                st.metric("Anomaly Score", f"{prediction['anomaly_score']:.4f}")
                st.metric("Confidence", f"{prediction['confidence']:.4f}")
                
                # Explanation
                if prediction['is_anomaly']:
                    st.info("This transaction was flagged as anomalous due to unusual patterns in amount, timing, or other features.")
                else:
                    st.success("This transaction appears to follow normal patterns.")
        
        # Batch prediction
        st.subheader("Batch Prediction")
        st.write("Upload a CSV file with transaction data for batch anomaly detection:")
        
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        
        if uploaded_file is not None:
            try:
                batch_data = pd.read_csv(uploaded_file)
                
                if all(feature in batch_data.columns for feature in features):
                    # Make predictions
                    X_batch = batch_data[features]
                    anomaly_scores = model.decision_function(X_batch)
                    predictions = anomaly_scores < 0
                    
                    # Add predictions to data
                    batch_data['anomaly_score'] = anomaly_scores
                    batch_data['is_anomaly'] = predictions
                    
                    st.success(f"Processed {len(batch_data)} transactions")
                    st.dataframe(batch_data, use_container_width=True)
                    
                    # Download results
                    csv = batch_data.to_csv(index=False)
                    st.download_button(
                        label="Download Results",
                        data=csv,
                        file_name="anomaly_detection_results.csv",
                        mime="text/csv"
                    )
                else:
                    st.error(f"CSV must contain columns: {features}")
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
    
    with tab3:
        st.subheader("Model Performance")
        
        # Calculate metrics
        predictions = model.predict(data[features])
        y_true = data['is_anomaly'].astype(int)
        y_pred = (predictions == -1).astype(int)  # -1 means anomaly in Isolation Forest
        
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, zero_division=0)
        recall = recall_score(y_true, y_pred, zero_division=0)
        f1 = f1_score(y_true, y_pred, zero_division=0)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Accuracy", f"{accuracy:.4f}")
        
        with col2:
            st.metric("Precision", f"{precision:.4f}")
        
        with col3:
            st.metric("Recall", f"{recall:.4f}")
        
        with col4:
            st.metric("F1-Score", f"{f1:.4f}")
        
        # Confusion matrix
        from sklearn.metrics import confusion_matrix
        import seaborn as sns
        import matplotlib.pyplot as plt
        
        cm = confusion_matrix(y_true, y_pred)
        
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax)
        ax.set_title('Confusion Matrix')
        ax.set_xlabel('Predicted')
        ax.set_ylabel('Actual')
        
        st.pyplot(fig)
    
    with tab4:
        st.subheader("About This Project")
        
        st.markdown("""
        ### 🚀 Azure MLOps Anomaly Detection
        
        This Streamlit application demonstrates the capabilities of our **End-to-End MLOps Pipeline for Real-time Anomaly Detection on Azure**.
        
        #### 🔧 Key Features:
        - **Real-time Anomaly Detection**: Using Isolation Forest algorithm
        - **Synthetic Data Generation**: Realistic transaction data simulation
        - **Interactive Visualizations**: Explore patterns and anomalies
        - **Batch Processing**: Upload CSV files for bulk analysis
        - **Model Performance Metrics**: Comprehensive evaluation
        
        #### 🏗️ Full Azure Architecture:
        The complete project includes:
        - **Azure Event Hubs**: Real-time data ingestion
        - **Azure Data Lake Storage**: Scalable data storage
        - **Azure Databricks**: Data processing and feature engineering
        - **Azure Machine Learning**: Model training and deployment
        - **Azure Functions**: Real-time inference
        - **Terraform**: Infrastructure as Code
        - **GitHub Actions**: CI/CD pipeline
        
        #### 📊 Use Cases:
        - **Fraud Detection**: Identify suspicious financial transactions
        - **Network Security**: Detect unusual network activity
        - **IoT Monitoring**: Flag sensor anomalies
        - **Quality Control**: Identify manufacturing defects
        
        #### 🛠️ Technologies:
        - **Python**: Core programming language
        - **Scikit-learn**: Machine learning algorithms
        - **Streamlit**: Web application framework
        - **Plotly**: Interactive visualizations
        - **Pandas**: Data manipulation
        - **NumPy**: Numerical computing
        
        #### 📈 Business Impact:
        - **Reduced Financial Losses**: Quick fraud detection
        - **Improved Security**: Proactive threat identification
        - **Operational Efficiency**: Automated anomaly detection
        - **Cost Savings**: Reduced manual monitoring
        
        ---
        
        **GitHub Repository**: [Azure MLOps Anomaly Detector](https://github.com/MukeshPyatla/azure-mlops-anomaly-detector)
        """)

if __name__ == "__main__":
    main() 