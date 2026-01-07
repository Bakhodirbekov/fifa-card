import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QLabel, QStackedWidget, QHBoxLayout, QFrame, QLineEdit, QComboBox
)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, Slot, QSize
from PySide6.QtGui import QFont, QPixmap, QColor, QImage
from PySide6.QtMultimedia import QSoundEffect

from src.camera.capture import CameraManager
from src.card.generator import CardGenerator
from src.utils.player_selector import PlayerSelector
from src.ai.gender_detection import GenderDetector
from src.utils.printer import CardPrinter


class KioskWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.camera_manager = CameraManager()
        self.card_generator = CardGenerator()
        self.player_selector = PlayerSelector()
        self.gender_detector = GenderDetector()
        self.printer = CardPrinter()
        
        self.current_language = "uz" # Default language
        self.current_card_path = None
        self.alignment_counter = 0 # To track how long face is aligned
        
        self.setup_ui()
        self.setup_animations()
        
    def setup_ui(self):
        # Fullscreen kiosk mode
        self.setWindowState(Qt.WindowFullScreen)
        # self.setCursor(Qt.BlankCursor) # Keep cursor for now for dev

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Stacked widget for different screens
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)

        # Home Screen
        self.home_screen = self.create_home_screen()
        self.stacked_widget.addWidget(self.home_screen)

        # Camera Screen
        self.camera_screen = self.create_camera_screen()
        self.stacked_widget.addWidget(self.camera_screen)

        # Processing Screen
        self.processing_screen = self.create_processing_screen()
        self.stacked_widget.addWidget(self.processing_screen)

        # Result Screen
        self.result_screen = self.create_result_screen()
        self.stacked_widget.addWidget(self.result_screen)

    def create_home_screen(self):
        screen = QWidget()
        layout = QVBoxLayout(screen)

        # Language Toggle (Top Right)
        lang_layout = QHBoxLayout()
        lang_layout.addStretch()
        self.lang_btn = QPushButton("O'zbekcha / Русский")
        self.lang_btn.setStyleSheet("padding: 10px; font-size: 18px;")
        self.lang_btn.clicked.connect(self.toggle_language)
        lang_layout.addWidget(self.lang_btn)
        layout.addLayout(lang_layout)

        # Title
        self.title_label = QLabel("FIFA ULTIMATE CARD PHOTO BOOTH")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            font-size: 48px;
            font-weight: bold;
            color: #1a5fb4;
            padding: 40px;
        """)

        # Start Button
        self.start_btn = QPushButton("📸 SURATGA TUSHISH")
        self.start_btn.setMinimumHeight(120)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #26a269;
                color: white;
                font-size: 36px;
                font-weight: bold;
                border-radius: 20px;
                padding: 30px;
            }
            QPushButton:hover {
                background-color: #2ec27e;
            }
        """)
        self.start_btn.clicked.connect(self.start_capture)

        layout.addStretch()
        layout.addWidget(self.title_label)
        layout.addStretch()
        layout.addWidget(self.start_btn)
        layout.addStretch()

        return screen

    def create_manual_entry_screen(self):
        screen = QWidget()
        layout = QVBoxLayout(screen)
        
        self.manual_title = QLabel("ISMINGIZNI KIRITING / ВВЕДИТЕ ВАШЕ ИМЯ")
        self.manual_title.setAlignment(Qt.AlignCenter)
        self.manual_title.setStyleSheet("font-size: 32px; font-weight: bold; margin-bottom: 20px;")
        
        form_layout = QVBoxLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ism / Имя")
        self.name_input.setStyleSheet("font-size: 24px; padding: 15px;")
        
        form_layout.addWidget(self.name_input)
        
        self.continue_btn = QPushButton("DAVOM ETISH / ПРОДОЛЖИТЬ")
        self.continue_btn.setStyleSheet("background-color: #1a5fb4; color: white; font-size: 28px; padding: 20px; border-radius: 10px;")
        self.continue_btn.clicked.connect(self.goto_camera)
        
        layout.addStretch()
        layout.addWidget(self.manual_title)
        layout.addLayout(form_layout)
        layout.addStretch()
        layout.addWidget(self.continue_btn)
        layout.addStretch()
        
        return screen

    def create_camera_screen(self):
        screen = QWidget()
        layout = QVBoxLayout(screen)
        
        # Overlay message
        self.guide_label = QLabel("YUZINGIZNI DUMOLOQ ICHIGA JOYLASHTIRING\nПОМЕСТИТЕ ЛИЦО В КРУГ")
        self.guide_label.setAlignment(Qt.AlignCenter)
        self.guide_label.setStyleSheet("""
            color: white; 
            font-size: 32px; 
            font-weight: bold; 
            background-color: rgba(0, 0, 0, 150);
            padding: 20px;
        """)
        
        # Fixed size container for video to prevent jumping
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("background-color: black; border: 5px solid #1a5fb4;")
        # Set a stable size policy
        from PySide6.QtWidgets import QSizePolicy
        self.video_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.video_label.setMinimumSize(800, 600) # Ensure it doesn't start too small
        
        self.capture_btn = QPushButton("📸 SURATGA OLISH")
        self.capture_btn.setStyleSheet("background-color: #e01b24; color: white; font-size: 32px; padding: 20px;")
        self.capture_btn.clicked.connect(self.take_photo)
        
        layout.addWidget(self.guide_label)
        layout.addWidget(self.video_label, 1)
        layout.addWidget(self.capture_btn)
        
        return screen

    def create_processing_screen(self):
        screen = QWidget()
        layout = QVBoxLayout(screen)
        
        self.processing_msg = QLabel("ABRABOTKA BOLYAPTI...\nИДЕТ ОБРАБОТКА...")
        self.processing_msg.setAlignment(Qt.AlignCenter)
        self.processing_msg.setStyleSheet("font-size: 40px; font-weight: bold; color: #1a5fb4;")
        
        layout.addStretch()
        layout.addWidget(self.processing_msg)
        layout.addStretch()
        
        return screen

    def create_result_screen(self):
        screen = QWidget()
        layout = QVBoxLayout(screen)
        
        self.card_display = QLabel()
        self.card_display.setAlignment(Qt.AlignCenter)
        
        btn_layout = QHBoxLayout()
        
        self.print_btn = QPushButton("🖨️ CHOP ETISH / ПЕЧАТЬ")
        self.print_btn.setStyleSheet("background-color: #3584e4; color: white; font-size: 28px; padding: 20px;")
        self.print_btn.clicked.connect(self.print_card)
        
        self.finish_btn = QPushButton("YANA BIR BOR / ЕЩЕ РАЗ")
        self.finish_btn.setStyleSheet("background-color: #26a269; color: white; font-size: 28px; padding: 20px;")
        self.finish_btn.clicked.connect(self.reset_app)
        
        btn_layout.addWidget(self.print_btn)
        btn_layout.addWidget(self.finish_btn)
        
        layout.addWidget(self.card_display, 1)
        layout.addLayout(btn_layout)
        
        return screen

    def setup_animations(self):
        pass # Placeholder for actual animations

    def toggle_language(self):
        if self.current_language == "uz":
            self.current_language = "ru"
            self.start_btn.setText("📸 СФОТОГРАФИРОВАТЬСЯ")
            self.title_label.setText("ФОТОБУДКА FIFA ULTIMATE CARD")
            self.manual_title.setText("ВВЕДИТЕ ВАШЕ ИМЯ")
            self.processing_msg.setText("ИДЕТ ОБРАБОТКА...")
            self.print_btn.setText("🖨️ ПЕЧАТЬ")
            self.finish_btn.setText("ЕЩЕ РАЗ")
            self.guide_label.setText("ПОМЕСТИТЕ ЛИЦО В КРУГ")
        else:
            self.current_language = "uz"
            self.start_btn.setText("📸 SURATGA TUSHISH")
            self.title_label.setText("FIFA ULTIMATE CARD PHOTO BOOTH")
            self.manual_title.setText("ISMINGIZNI KIRITING")
            self.processing_msg.setText("ABRABOTKA BOLYAPTI...")
            self.print_btn.setText("🖨️ CHOP ETISH")
            self.finish_btn.setText("YANA BIR BOR")
            self.guide_label.setText("YUZINGIZNI DUMOLOQ ICHIGA JOYLASHTIRING")

    def start_capture(self):
        self.goto_camera()

    def goto_camera(self):
        self.stacked_widget.setCurrentWidget(self.camera_screen)
        if self.camera_manager.start_preview():
            # Timer to update frame
            if not hasattr(self, 'timer') or not self.timer.isActive():
                self.timer = QTimer()
                self.timer.timeout.connect(self.update_frame)
                self.timer.start(30)
        else:
            print("❌ Failed to start camera preview")
            self.guide_label.setText("XATOLIK: KAMERA TOPILMADI")
            # Go back home after 3 seconds
            QTimer.singleShot(3000, self.reset_app)

    def update_frame(self):
        frame = self.camera_manager.current_frame
        if frame is not None:
            # Create a copy to avoid modifying the original thread's frame
            import cv2
            frame = frame.copy()
            
            h, w, _ = frame.shape
            center = (w // 2, h // 2)
            radius = min(h, w) // 3
            
            # Check alignment from camera manager
            aligned = self.camera_manager.face_in_guide
            
            # Draw circular guide: Green if aligned, White if not
            color = (0, 255, 0) if aligned else (255, 255, 255)
            cv2.circle(frame, center, radius, color, 4)
            
            # Auto-capture logic
            if aligned:
                self.alignment_counter += 1
                # If aligned for ~1 second (30 frames at 30fps)
                if self.alignment_counter >= 30:
                    self.alignment_counter = 0
                    QTimer.singleShot(0, self.take_photo)
            else:
                self.alignment_counter = 0
            
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_img)
            
            # Use a fixed target width/height if label size is weird
            target_size = self.video_label.size()
            if target_size.width() < 100 or target_size.height() < 100:
                target_size = QSize(800, 600)
                
            self.video_label.setPixmap(pixmap.scaled(
                target_size, 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            ))

    def take_photo(self):
        self.timer.stop()
        photo_path = self.camera_manager.capture_photo()
        if photo_path:
            self.process_card(photo_path)

    def process_card(self, photo_path):
        self.stacked_widget.setCurrentWidget(self.processing_screen)
        QTimer.singleShot(100, lambda: self._generate_card_async(photo_path))

    def _generate_card_async(self, photo_path):
        # Detect gender automatically
        gender = self.gender_detector.detect_gender(photo_path)
        print(f"🔍 Detected gender: {gender}")
        
        if gender == 'unknown':
            gender = 'male' # Fallback
            
        # Select random base player for stats
        base_player = self.player_selector.select_player(gender)
        stats = self.player_selector.generate_stats(base_player['base_stats'])
        
        player_data = {
            'name': base_player['name'].upper(),
            'gender': gender,
            'position': base_player['position']
        }
        
        try:
            output_path = self.card_generator.generate_card(photo_path, player_data, stats)
            self.current_card_path = output_path
            self.show_result(output_path)
        except Exception as e:
            print(f"Error generating card: {e}")
            self.reset_app()

    def print_card(self):
        if self.current_card_path:
            success = self.printer.print_card(self.current_card_path)
            if success:
                print("Card sent to printer")
            else:
                print("Print failed")

    def show_result(self, output_path):
        pixmap = QPixmap(output_path)
        self.card_display.setPixmap(pixmap.scaled(self.card_display.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.stacked_widget.setCurrentWidget(self.result_screen)

    def reset_app(self):
        if hasattr(self, 'timer'):
            self.timer.stop()
        self.camera_manager.stop_camera()
        self.current_card_path = None
        self.alignment_counter = 0
        self.stacked_widget.setCurrentWidget(self.home_screen)

    def _save_new_player(self, name, gender):
        """Save new player to players.json"""
        try:
            import json
            path = 'src/data/players.json'
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            key = 'male_players' if gender == 'male' else 'female_players'
            new_id = max([p['id'] for p in data[key]]) + 1
            
            new_player = {
                "id": new_id,
                "name": name,
                "position": "ST",
                "country": "Uzbekistan",
                "club": "Custom",
                "base_stats": { "PAC": 80, "SHO": 80, "PAS": 80, "DRI": 80, "DEF": 50, "PHY": 75 },
                "image": "default.png"
            }
            
            data[key].append(new_player)
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            print(f"✅ Player {name} added to database")
        except Exception as e:
            print(f"❌ Failed to save player: {e}")


# Run application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # Load stylesheet
    with open("src/ui/styles.qss", "r") as f:
        app.setStyleSheet(f.read())

    window = KioskWindow()
    window.show()
    sys.exit(app.exec())