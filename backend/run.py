#!/usr/bin/env python3
"""
Simple script to run the Flask application
"""
import os
import sys
from app import app

if __name__ == '__main__':
    # Create uploads directory if it doesn't exist
    os.makedirs('uploads', exist_ok=True)
    
    # Run the Flask application
    print("Starting Steganography Web Application...")
    print("Backend will be available at: http://localhost:5000")
    print("Frontend should be running at: http://localhost:3000")
    print("Press Ctrl+C to stop the server")
    
    app.run(debug=True, host='0.0.0.0', port=5000)




















