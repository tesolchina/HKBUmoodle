#!/bin/bash

# 🎓 HKBU Moodle Assistant - Streamlit GUI Launcher
# Quick prototype for testing Moodle API functions

echo "🎓 Starting HKBU Moodle Assistant..."
echo "=================================="

# Check if we're in the right directory
if [ ! -f "streamlit_app.py" ]; then
    echo "❌ Error: Please run this script from the moodle-ai-processor directory"
    echo "   Current directory: $(pwd)"
    echo "   Expected file: streamlit_app.py"
    exit 1
fi

# Check if required files exist
if [ ! -f "src/moodle_client.py" ]; then
    echo "❌ Error: moodle_client.py not found in src/ directory"
    exit 1
fi

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "⚠️  Streamlit not found. Installing dependencies..."
    pip install -r requirements_streamlit.txt
fi

# Set Python path and start Streamlit
export PYTHONPATH=".:$PYTHONPATH"

echo "🚀 Launching Streamlit app..."
echo "   Access URL: http://localhost:8501"
echo "   Press Ctrl+C to stop"
echo "=================================="

streamlit run streamlit_app.py --server.port 8501 --server.address localhost
