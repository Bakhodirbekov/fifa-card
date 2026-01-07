import win32print
import win32ui
from PIL import Image, ImageWin
import os
import tempfile


class CardPrinter:
    def __init__(self):
        self.printer_name = None
        self.paper_size = 'A5'

    def get_available_printers(self):
        """Get list of available printers"""
        printers = []
        for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL):
            printers.append(printer[2])
        return printers

    def print_card(self, image_path, copies=1):
        """Print card to default printer"""
        try:
            # Get default printer
            printer_name = win32print.GetDefaultPrinter()

            # Open image
            image = Image.open(image_path)

            # Calculate print size (A5 = 148x210mm)
            if self.paper_size == 'A5':
                target_width = int(148 * 300 / 25.4)  # 300 DPI
                target_height = int(210 * 300 / 25.4)
            else:  # A4
                target_width = int(210 * 300 / 25.4)
                target_height = int(297 * 300 / 25.4)

            # Resize image maintaining aspect ratio
            image.thumbnail((target_width, target_height), Image.Resampling.LANCZOS)

            # Create temporary file for printing
            temp_file = tempfile.NamedTemporaryFile(suffix='.bmp', delete=False)
            image.save(temp_file.name, 'BMP')
            temp_file.close()

            # Print using Windows GDI
            hDC = win32ui.CreateDC()
            hDC.CreatePrinterDC(printer_name)
            hDC.StartDoc("FIFA Card")
            hDC.StartPage()

            # Draw image
            dib = ImageWin.Dib(image)
            dib.draw(hDC.GetHandleOutput(), (0, 0, target_width, target_height))

            hDC.EndPage()
            hDC.EndDoc()
            hDC.DeleteDC()

            # Cleanup
            os.unlink(temp_file.name)

            return True

        except Exception as e:
            print(f"Print error: {e}")
            return False

    def save_to_usb(self, image_path, usb_drive='D:'):
        """Save card to USB drive"""
        try:
            if not os.path.exists(usb_drive):
                # Try to find USB drive
                for drive in ['E:', 'F:', 'G:', 'H:']:
                    if os.path.exists(drive):
                        usb_drive = drive
                        break
                else:
                    return False

            filename = os.path.basename(image_path)
            destination = os.path.join(usb_drive, 'FIFA_Cards', filename)

            # Create directory if doesn't exist
            os.makedirs(os.path.dirname(destination), exist_ok=True)

            # Copy file
            with open(image_path, 'rb') as src, open(destination, 'wb') as dst:
                dst.write(src.read())

            return True

        except Exception as e:
            print(f"USB save error: {e}")
            return False