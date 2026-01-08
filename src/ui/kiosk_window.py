import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QLabel, QStackedWidget, QHBoxLayout, QFrame, QLineEdit, QComboBox,
    QSizePolicy
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

        # Gender Selection Screen
        self.gender_screen = self.create_gender_selection_screen()
        self.stacked_widget.addWidget(self.gender_screen)

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
        self.lang_btn.setStyleSheet("padding: 10px; font-size: 18px; background-color: #333; border: 1px solid #555;")
        self.lang_btn.clicked.connect(self.toggle_language)
        lang_layout.addWidget(self.lang_btn)
        layout.addLayout(lang_layout)

        # Title
        self.title_label = QLabel("FIFA x COCA-COLA\nULTIMATE TEAM")
        self.title_label.setObjectName("title")
        self.title_label.setAlignment(Qt.AlignCenter)

        # Start Button
        self.start_btn = QPushButton("📸 SURATGA TUSHISH")
        self.start_btn.setMinimumHeight(120)
        self.start_btn.clicked.connect(self.start_capture)

        layout.addStretch()
        layout.addWidget(self.title_label)
        layout.addStretch()
        layout.addWidget(self.start_btn)
        layout.addStretch()

        return screen

    def create_gender_selection_screen(self):
        screen = QWidget()
        layout = QVBoxLayout(screen)
        
        title = QLabel("JINSINGIZNI TANLANG / ВЫБЕРИТЕ ПОЛ")
        title.setObjectName("title")
        title.setStyleSheet("font-size: 36px;")
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(30)
        
        # Male Button
        self.male_btn = QPushButton("ERKAK (MALE)")
        self.male_btn.setObjectName("gender_male")
        self.male_btn.setMinimumHeight(200)
        self.male_btn.setMinimumWidth(300)
        self.male_btn.clicked.connect(lambda: self.select_gender('male'))
        
        # Female Button
        self.female_btn = QPushButton("AYOL (FEMALE)")
        self.female_btn.setObjectName("gender_female")
        self.female_btn.setMinimumHeight(200)
        self.female_btn.setMinimumWidth(300)
        self.female_btn.clicked.connect(lambda: self.select_gender('female'))
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.male_btn)
        btn_layout.addWidget(self.female_btn)
        btn_layout.addStretch()
        
        layout.addStretch()
        layout.addWidget(title)
        layout.addLayout(btn_layout)
        layout.addStretch()
        
        return screen

    def create_manual_entry_screen(self):
        # Deprecated or unused in this flow, keeping basic implementation just in case
        return QWidget()

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
        
        # Video container
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setObjectName("camera_preview")
        self.video_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.video_label.setMinimumSize(800, 600)
        
        self.capture_btn = QPushButton("📸 SURATGA OLISH")
        self.capture_btn.clicked.connect(self.take_photo)
        
        layout.addWidget(self.guide_label)
        layout.addWidget(self.video_label, 1)
        layout.addWidget(self.capture_btn)
        
        return screen

    def create_processing_screen(self):
        screen = QWidget()
        layout = QVBoxLayout(screen)
        screen.setObjectName("processing_screen")
        
        self.processing_msg = QLabel("TAYYORLANMOQDA...\nИДЕТ ОБРАБОТКА...")
        self.processing_msg.setObjectName("processing_text")
        
        layout.addStretch()
        layout.addWidget(self.processing_msg)
        layout.addStretch()
        
        return screen

    def create_result_screen(self):
        screen = QWidget()
        layout = QVBoxLayout(screen)
        
        # Use Web View for animated HTML card
        try:
            from PySide6.QtWebEngineWidgets import QWebEngineView
            self.card_display = QWebEngineView()
            self.card_display.page().setBackgroundColor(Qt.transparent)
        except ImportError:
            # Fallback (Should not happen if requirements correct)
            self.card_display = QLabel("WebEngine Missing")
            self.card_display.setAlignment(Qt.AlignCenter)

        self.card_display.setObjectName("card_display")
        
        btn_layout = QHBoxLayout()
        
        self.print_btn = QPushButton("🖨️ CHOP ETISH / ПЕЧАТЬ")
        self.print_btn.setObjectName("print_button")
        self.print_btn.clicked.connect(self.print_card)
        
        self.finish_btn = QPushButton("YANA BIR BOR / ЕЩЕ РАЗ")
        self.finish_btn.setObjectName("save_button")
        self.finish_btn.clicked.connect(self.reset_app)
        
        btn_layout.addWidget(self.print_btn)
        btn_layout.addWidget(self.finish_btn)
        
        layout.addWidget(self.card_display, 1)
        layout.addLayout(btn_layout)
        
        return screen

    def setup_animations(self):
        pass 

    def toggle_language(self):
        if self.current_language == "uz":
            self.current_language = "ru"
            self.start_btn.setText("📸 СФОТОГРАФИРОВАТЬСЯ")
            self.title_label.setText("ФОТОБУДКА FIFA x COCA-COLA")
            self.processing_msg.setText("ИДЕТ ОБРАБОТКА...")
            self.print_btn.setText("🖨️ ПЕЧАТЬ")
            self.finish_btn.setText("ЕЩЕ РАЗ")
            self.guide_label.setText("ПОМЕСТИТЕ ЛИЦО В КРУГ")
            self.male_btn.setText("МУЖЧИНА (MALE)")
            self.female_btn.setText("ЖЕНЩИНА (FEMALE)")
        else:
            self.current_language = "uz"
            self.start_btn.setText("📸 SURATGA TUSHISH")
            self.title_label.setText("FIFA x COCA-COLA\nULTIMATE TEAM")
            self.processing_msg.setText("TAYYORLANMOQDA...")
            self.print_btn.setText("🖨️ CHOP ETISH")
            self.finish_btn.setText("YANA BIR BOR")
            self.guide_label.setText("YUZINGIZNI DUMOLOQ ICHIGA JOYLASHTIRING")
            self.male_btn.setText("ERKAK (MALE)")
            self.female_btn.setText("AYOL (FEMALE)")

    def start_capture(self):
        self.goto_camera()

    def goto_camera(self):
        self.stacked_widget.setCurrentWidget(self.camera_screen)
        if self.camera_manager.start_preview():
            if not hasattr(self, 'timer'):
                self.timer = QTimer()
                self.timer.timeout.connect(self.update_frame)
            if not self.timer.isActive():
                self.timer.start(30)
        else:
            print("❌ Failed to start camera preview")
            self.show_demo_mode()

    def update_frame(self):
        frame = self.camera_manager.current_frame
        if frame is not None:
            # Create a copy
            import cv2
            frame = frame.copy()
            
            h, w, _ = frame.shape
            center = (w // 2, h // 2)
            radius = min(h, w) // 3
            
            aligned = self.camera_manager.face_in_guide
            
            # Guide color: Red for Coca-Cola theme by default, Green if aligned
            color = (0, 255, 0) if aligned else (255, 255, 255)
            cv2.circle(frame, center, radius, color, 4)
            
            # Auto-capture logic
            if aligned:
                self.alignment_counter += 1
                if self.alignment_counter >= 30:
                    self.alignment_counter = 0
                    QTimer.singleShot(0, self.take_photo)
            else:
                self.alignment_counter = 0
            
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_img)
            
            target_size = self.video_label.size()
            if target_size.width() < 100 or target_size.height() < 100:
                target_size = QSize(800, 600)
                
            self.video_label.setPixmap(pixmap.scaled(
                target_size, 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            ))

    def take_photo(self):
        if hasattr(self, 'timer') and self.timer.isActive():
            self.timer.stop()
        photo_path = self.camera_manager.capture_photo()
        if photo_path:
            self.current_photo_path = photo_path # Store temporarily
            # Go to gender selection instead of processing directly
            self.stacked_widget.setCurrentWidget(self.gender_screen)

    def select_gender(self, gender):
        if hasattr(self, 'current_photo_path') and self.current_photo_path:
            self.process_card(self.current_photo_path, gender)
        else:
            print("Error: No photo path found")
            self.reset_app()

    def process_card(self, photo_path, selected_gender='male'):
        self.stacked_widget.setCurrentWidget(self.processing_screen)
        QTimer.singleShot(100, lambda: self._generate_card_async(photo_path, selected_gender))

    def _generate_card_async(self, photo_path, gender):
        print(f"👤 Selected gender: {gender}")
            
        # Select random base player based on SELECTED gender
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
        from PySide6.QtCore import QUrl
        try:
             # Load local HTML file
             local_url = QUrl.fromLocalFile(output_path)
             if hasattr(self.card_display, 'load'):
                 self.card_display.load(local_url)
             else:
                 print("WebEngine fallback: cannot show HTML in QLabel")
        except Exception as e:
            print(f"Error showing result: {e}")
            
        self.stacked_widget.setCurrentWidget(self.result_screen)

    def reset_app(self):
        if hasattr(self, 'timer') and self.timer.isActive():
            self.timer.stop()
        self.camera_manager.stop_camera()
        self.current_card_path = None
        self.alignment_counter = 0
        self.stacked_widget.setCurrentWidget(self.home_screen)

    def show_demo_mode(self):
        """Show demo mode when camera is not available"""
        from PySide6.QtWidgets import QMessageBox, QFileDialog
        
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Kamera topilmadi / Камера не найдена")
        msg.setText(
            "KAMERA TOPILMADI!\n"
            "Rasmni fayldan yuklashni xohlaysizmi?\n\n"
            "КАМЕРА НЕ НАЙДЕНА!\n"
            "Хотите загрузить фото из файла?"
        )
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.Yes)
        
        result = msg.exec()
        
        if result == QMessageBox.Yes:
            self.upload_photo()
        else:
            self.reset_app()
    
    def upload_photo(self):
        """Allow user to upload a photo from file"""
        from PySide6.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Rasm tanlang / Выберите фото",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if file_path:
            print(f"📁 Selected file: {file_path}")
            # Store path and go to gender selection
            self.current_photo_path = file_path
            self.stacked_widget.setCurrentWidget(self.gender_screen)
        else:
            self.reset_app()

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