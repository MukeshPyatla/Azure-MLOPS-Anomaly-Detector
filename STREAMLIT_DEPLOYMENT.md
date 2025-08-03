# 🚀 Streamlit Cloud Deployment Guide

This guide will help you deploy the Azure MLOps Anomaly Detector to Streamlit Cloud.

## 📋 Prerequisites

1. **GitHub Account**: You need a GitHub account to host your repository
2. **Streamlit Cloud Account**: Sign up at [share.streamlit.io](https://share.streamlit.io)
3. **Python Knowledge**: Basic understanding of Python and Streamlit

## 🚀 Quick Deployment Steps

### Step 1: Prepare Your Repository

Ensure your repository contains these files:
- `streamlit_app.py` - Main Streamlit application
- `requirements.txt` - Python dependencies
- `.streamlit/config.toml` - Streamlit configuration
- `packages.txt` - System dependencies (if needed)
- `sample_transactions.csv` - Sample data for testing

### Step 2: Deploy to Streamlit Cloud

1. **Push to GitHub**: Make sure your code is pushed to a GitHub repository
2. **Connect to Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with your GitHub account
   - Click "New app"
   - Select your repository
   - Set the path to your Streamlit app: `streamlit_app.py`
   - Click "Deploy!"

### Step 3: Configure Your App

After deployment, you can configure:
- **App URL**: Your app will be available at `https://your-app-name.streamlit.app`
- **Repository**: Link to your GitHub repository
- **Branch**: Choose which branch to deploy from

## 🔧 Configuration Files

### `streamlit_app.py`
The main application file that contains:
- Interactive anomaly detection interface
- Data visualization with Plotly
- Real-time prediction capabilities
- Batch processing functionality

### `requirements.txt`
Contains all Python dependencies:
```
streamlit>=1.28.0
plotly>=5.15.0
pandas
numpy
scikit-learn
matplotlib>=3.7.0
seaborn>=0.12.0
joblib
```

### `.streamlit/config.toml`
Streamlit configuration for optimal deployment:
```toml
[global]
developmentMode = false

[server]
headless = true
port = 8501
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false
```

## 🎯 Features Available

### 1. **Data Analysis Tab**
- Interactive visualizations of transaction data
- Anomaly detection patterns
- Data distribution analysis

### 2. **Live Detection Tab**
- Real-time anomaly detection
- Single transaction analysis
- Batch CSV file processing
- Download results functionality

### 3. **Model Performance Tab**
- Accuracy, Precision, Recall, F1-Score
- Confusion matrix visualization
- Model evaluation metrics

### 4. **About Tab**
- Project overview and architecture
- Technology stack information
- Use cases and business impact

## 🧪 Testing Your Deployment

### Test Single Transaction Detection
1. Go to the "Live Detection" tab
2. Enter transaction details:
   - Amount: $5000 (anomalous)
   - Hour: 2 (unusual hour)
   - User ID: TEST123
   - Device: desktop
3. Click "🔍 Detect Anomaly"
4. Verify the anomaly is detected

### Test Batch Processing
1. Download the `sample_transactions.csv` file
2. Go to "Batch Prediction" section
3. Upload the CSV file
4. Verify results and download processed data

## 🔍 Troubleshooting

### Common Issues

1. **Import Errors**:
   - Ensure all dependencies are in `requirements.txt`
   - Check Python version compatibility

2. **Memory Issues**:
   - Reduce the number of samples in the sidebar
   - Clear cache using the "Generate New Data" button

3. **Deployment Failures**:
   - Check that `streamlit_app.py` is in the root directory
   - Verify all required files are committed to GitHub

### Performance Optimization

1. **Caching**: The app uses `@st.cache_data` and `@st.cache_resource` for optimal performance
2. **Data Size**: Limit sample size for faster loading
3. **Visualizations**: Plotly charts are optimized for web display

## 📊 Monitoring Your App

### Streamlit Cloud Dashboard
- **App Status**: Monitor deployment status
- **Usage Analytics**: Track user interactions
- **Error Logs**: View any deployment errors

### GitHub Integration
- **Automatic Updates**: Changes to your main branch automatically redeploy
- **Version Control**: Track all changes in your repository

## 🎨 Customization

### Styling
The app includes custom CSS for better visual appeal:
- Blue color scheme matching Azure branding
- Responsive design for different screen sizes
- Clear visual indicators for anomalies

### Adding Features
You can extend the app by:
- Adding more visualization types
- Implementing additional ML models
- Creating more interactive elements
- Adding authentication

## 🔗 Useful Links

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Streamlit Cloud](https://share.streamlit.io/)
- [Plotly Documentation](https://plotly.com/python/)
- [Scikit-learn Documentation](https://scikit-learn.org/)

## 📞 Support

If you encounter issues:
1. Check the Streamlit Cloud logs
2. Review the GitHub repository for updates
3. Test locally with `streamlit run streamlit_app.py`

---

**Happy Deploying! 🚀** 