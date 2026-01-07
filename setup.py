#!/usr/bin/env python3
"""
Setup script for FIFA Photo Booth
"""

import subprocess
import sys
import os
from pathlib import Path


def main():
    print("🚀 Setting up FIFA Photo Booth...")

    # Create directory structure
    base_path = Path(__file__).parent
    folders = [
        "config",
        "src/ui/components",
        "src/camera",
        "src/ai",
        "src/data/templates",
        "src/card",
        "src/utils",
        "src/assets/images",
        "src/assets/fonts",
        "src/assets/sounds",
        "output/captured",
        "output/cards",
        "output/logs",
        "tests"
    ]

    for folder in folders:
        folder_path = base_path / folder
        folder_path.mkdir(parents=True, exist_ok=True)
        print(f"📁 Created: {folder}")

    # Create __init__.py files
    init_files = [
        "src/__init__.py",
        "src/ui/__init__.py",
        "src/ui/components/__init__.py",
        "src/camera/__init__.py",
        "src/ai/__init__.py",
        "src/data/__init__.py",
        "src/card/__init__.py",
        "src/utils/__init__.py",
        "tests/__init__.py"
    ]

    for init_file in init_files:
        file_path = base_path / init_file
        file_path.touch(exist_ok=True)

    # Install requirements
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        sys.exit(1)

    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Add card templates to src/data/templates/")
    print("2. Add fonts to src/assets/fonts/")
    print("3. Run: python main.py")


if __name__ == "__main__":
    main()