"""
Auto-start configuration for Windows kiosk mode
"""

import os
import sys
import winreg
from pathlib import Path


def setup_auto_start():
    """Setup application to start automatically on Windows login"""

    try:
        # Get executable path
        if getattr(sys, 'frozen', False):
            # Running as exe
            app_path = sys.executable
        else:
            # Running as script
            app_path = os.path.abspath(sys.argv[0])

        # Registry key for auto-start
        key = winreg.HKEY_CURRENT_USER
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"

        # Open or create key
        with winreg.OpenKey(key, key_path, 0, winreg.KEY_ALL_ACCESS) as reg_key:
            # Set value
            winreg.SetValueEx(
                reg_key,
                "FIFA_Photo_Booth",
                0,
                winreg.REG_SZ,
                f'"{app_path}" --kiosk'
            )

        print("✅ Auto-start configured")
        return True

    except Exception as e:
        print(f"❌ Failed to setup auto-start: {e}")
        return False


def remove_auto_start():
    """Remove auto-start configuration"""

    try:
        key = winreg.HKEY_CURRENT_USER
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"

        with winreg.OpenKey(key, key_path, 0, winreg.KEY_ALL_ACCESS) as reg_key:
            try:
                winreg.DeleteValue(reg_key, "FIFA_Photo_Booth")
                print("✅ Auto-start removed")
                return True
            except FileNotFoundError:
                print("⚠️  Auto-start entry not found")
                return True

    except Exception as e:
        print(f"❌ Failed to remove auto-start: {e}")
        return False