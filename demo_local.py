#!/usr/bin/env python3
"""
Demo script for running the Azure MLOps Anomaly Detector locally
This script demonstrates how to test the Streamlit app functionality.
"""

import subprocess
import sys
import os
import time
import webbrowser

def check_streamlit_installed():
    """Check if Streamlit is installed"""
    try:
        import streamlit
        print("✅ Streamlit is installed")
        return True
    except ImportError:
        print("❌ Streamlit is not installed")
        print("Install with: pip install streamlit")
        return False

def run_streamlit_app():
    """Run the Streamlit app locally"""
    print("🚀 Starting Azure MLOps Anomaly Detector...")
    print("=" * 50)
    
    # Check if streamlit_app.py exists
    if not os.path.exists("streamlit_app.py"):
        print("❌ streamlit_app.py not found in current directory")
        return False
    
    print("📋 App Features:")
    print("  • Interactive anomaly detection")
    print("  • Real-time transaction analysis")
    print("  • Data visualization with Plotly")
    print("  • Batch CSV processing")
    print("  • Model performance metrics")
    print()
    
    print("🌐 The app will open in your browser at: http://localhost:8501")
    print("📊 Navigate through the tabs to explore different features")
    print("🔄 Press Ctrl+C to stop the app")
    print()
    
    try:
        # Start Streamlit app
        subprocess.run(["streamlit", "run", "streamlit_app.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 App stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running Streamlit app: {e}")
        return False
    
    return True

def show_usage_tips():
    """Show tips for using the app"""
    print("\n💡 Usage Tips:")
    print("1. **Data Analysis Tab**: Explore transaction patterns and visualizations")
    print("2. **Live Detection Tab**: Test real-time anomaly detection")
    print("3. **Model Performance Tab**: View accuracy metrics and confusion matrix")
    print("4. **About Tab**: Learn about the project and architecture")
    print()
    print("🧪 Test Cases:")
    print("• Normal transaction: Amount $100, Hour 14")
    print("• Anomalous transaction: Amount $5000, Hour 2")
    print("• Upload sample_transactions.csv for batch testing")
    print()

def main():
    """Main demo function"""
    print("🚀 Azure MLOps Anomaly Detector - Local Demo")
    print("=" * 60)
    
    # Check prerequisites
    if not check_streamlit_installed():
        sys.exit(1)
    
    # Show usage tips
    show_usage_tips()
    
    # Ask user if they want to run the app
    response = input("Do you want to start the Streamlit app? (y/n): ").lower().strip()
    
    if response in ['y', 'yes']:
        run_streamlit_app()
    else:
        print("👋 Demo cancelled. You can run the app later with:")
        print("  streamlit run streamlit_app.py")

if __name__ == "__main__":
    main() 