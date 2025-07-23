#!/usr/bin/env python3
"""
Setup script for Finance Agent
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print("✅ Python version is compatible")

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        sys.exit(1)

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file already exists")
        return
    
    print("📝 Creating .env file...")
    env_content = """# Gmail Configuration
GMAIL_EMAIL=your_email@gmail.com
GMAIL_PASSWORD=your_app_password
GMAIL_SMTP_SERVER=smtp.gmail.com
GMAIL_SMTP_PORT=587

# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE=finance_agent

# Google AI Configuration
GOOGLE_API_KEY=your_gemini_api_key

# Application Configuration
DEBUG=True
LOG_LEVEL=INFO
"""
    
    with open(env_file, "w") as f:
        f.write(env_content)
    
    print("✅ .env file created")
    print("⚠️  Please update the .env file with your actual credentials")

def check_mongodb():
    """Check if MongoDB is available"""
    print("🔍 Checking MongoDB connection...")
    try:
        import pymongo
        client = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print("✅ MongoDB is running and accessible")
        client.close()
    except Exception as e:
        print("⚠️  MongoDB connection failed. Please ensure MongoDB is running:")
        print("   - Install MongoDB locally, or")
        print("   - Use MongoDB Atlas cloud service")
        print(f"   Error: {e}")

def check_tesseract():
    """Check if Tesseract OCR is installed"""
    print("🔍 Checking Tesseract OCR...")
    try:
        import pytesseract
        # Try to get version
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract OCR is installed (version: {version})")
    except Exception as e:
        print("⚠️  Tesseract OCR not found or not properly configured")
        print("   Please install Tesseract OCR:")
        print("   - Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
        print("   - Linux: sudo apt-get install tesseract-ocr")
        print("   - macOS: brew install tesseract")

def create_directories():
    """Create necessary directories"""
    directories = ["logs", "exports", "temp"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    print("✅ Directories created")

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing imports...")
    try:
        import langchain
        import streamlit
        import pymongo
        import google.generativeai
        import PyPDF2
        import PIL
        import cv2
        import pandas
        print("✅ All required modules imported successfully")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please run: pip install -r requirements.txt")
        sys.exit(1)

def main():
    """Main setup function"""
    print("🚀 Setting up Finance Agent...")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Install dependencies
    install_dependencies()
    
    # Test imports
    test_imports()
    
    # Create .env file
    create_env_file()
    
    # Create directories
    create_directories()
    
    # Check external dependencies
    check_mongodb()
    check_tesseract()
    
    print("=" * 50)
    print("✅ Setup completed!")
    print("\n📋 Next steps:")
    print("1. Update the .env file with your credentials")
    print("2. Start MongoDB (if running locally)")
    print("3. Run: streamlit run streamlit_app.py")
    print("4. Open http://localhost:8501 in your browser")
    print("\n📚 For more information, see README.md")

if __name__ == "__main__":
    main() 