#!/usr/bin/env python3
"""
Install missing dependencies for Finance Agent
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def main():
    """Install missing dependencies"""
    print("🔧 Installing missing dependencies...")
    
    # List of packages that might be missing
    packages = [
        "PyPDF2==3.0.1",
        "pytesseract==0.3.10",
        "opencv-python==4.8.1.78",
        "langchain-google-genai==0.0.6",
        "langchain-community==0.0.20",
        "langchain-core==0.1.20",
        "faiss-cpu==1.7.4",
        "plotly==5.19.0"
    ]
    
    success_count = 0
    total_count = len(packages)
    
    for package in packages:
        if install_package(package):
            success_count += 1
    
    print(f"\n📊 Installation Summary:")
    print(f"   Successfully installed: {success_count}/{total_count} packages")
    
    if success_count == total_count:
        print("🎉 All dependencies installed successfully!")
        print("\n🚀 You can now run:")
        print("   streamlit run streamlit_app.py")
    else:
        print("⚠️  Some packages failed to install. Please check the errors above.")
        print("   You may need to install them manually or check your internet connection.")

if __name__ == "__main__":
    main() 