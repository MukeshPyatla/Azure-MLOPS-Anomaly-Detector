#!/usr/bin/env python3
"""
Test script for the Streamlit Anomaly Detection App
This script verifies that all dependencies are working correctly.
"""

import sys
import importlib

def test_imports():
    """Test that all required packages can be imported"""
    required_packages = [
        'streamlit',
        'pandas',
        'numpy',
        'plotly',
        'sklearn',
        'matplotlib',
        'seaborn',
        'joblib'
    ]
    
    print("Testing imports...")
    failed_imports = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError as e:
            print(f"❌ {package}: {e}")
            failed_imports.append(package)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {failed_imports}")
        print("Please install missing packages with: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ All imports successful!")
        return True

def test_streamlit_app():
    """Test that the Streamlit app can be imported"""
    try:
        # Import the main app functions
        from streamlit_app import generate_synthetic_data, train_anomaly_model, predict_anomaly
        
        print("Testing Streamlit app functions...")
        
        # Test data generation
        data = generate_synthetic_data(100)
        print(f"✅ Generated {len(data)} synthetic transactions")
        
        # Test model training
        model, features = train_anomaly_model(data)
        print(f"✅ Trained model with features: {features}")
        
        # Test prediction
        test_transaction = {'amount': 5000, 'transaction_hour': 2}
        prediction = predict_anomaly(model, features, test_transaction)
        print(f"✅ Made prediction: {prediction}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Streamlit app: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Azure MLOps Anomaly Detector Streamlit App")
    print("=" * 60)
    
    # Test imports
    imports_ok = test_imports()
    
    if imports_ok:
        # Test app functionality
        app_ok = test_streamlit_app()
        
        if app_ok:
            print("\n🎉 All tests passed! The app is ready to deploy.")
            print("\nTo run the app locally:")
            print("  streamlit run streamlit_app.py")
            print("\nTo deploy to Streamlit Cloud:")
            print("  1. Push to GitHub")
            print("  2. Go to share.streamlit.io")
            print("  3. Connect your repository")
            print("  4. Set app path to: streamlit_app.py")
            print("  5. Deploy!")
        else:
            print("\n❌ App functionality tests failed.")
            sys.exit(1)
    else:
        print("\n❌ Import tests failed.")
        sys.exit(1)

if __name__ == "__main__":
    main() 