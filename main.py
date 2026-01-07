"""
FIFA Ultimate Card Photo Booth
Main Application File
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PySide6.QtWidgets import QApplication
from src.ui.kiosk_window import KioskWindow
from src.utils.logger import setup_logger
from src.utils.auto_start import setup_auto_start


def main():
    """Main application function"""
    # Setup logger
    logger = setup_logger()
    logger.info("Starting FIFA Photo Booth Application")

    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("FIFA Photo Booth")
    app.setApplicationVersion("1.0.0")

    # Load stylesheet
    stylesheet_path = Path("src/ui/styles.qss")
    if stylesheet_path.exists():
        with open(stylesheet_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())

    # Create and show main window
    window = KioskWindow()
    window.show()

    # Setup auto-start for kiosk mode
    setup_auto_start()

    logger.info("Application started successfully")

    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()