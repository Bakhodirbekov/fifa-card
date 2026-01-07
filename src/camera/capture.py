import cv2
import numpy as np
from datetime import datetime
import os
from threading import Thread
import time


class CameraManager:
    def __init__(self):
        self.camera = None
        self.is_capturing = False
        self.current_frame = None
        self.capture_thread = None
        self.face_in_guide = False
        
        # Load face cascade for auto-detection
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

    def initialize_camera(self):
        """Try to find and initialize camera with multiple fallbacks"""
        # Close existing camera if any
        if self.camera:
            self.camera.release()
            self.camera = None

        # Prefer MSMF on modern Windows, then DSHOW
        backends = [cv2.CAP_MSMF, cv2.CAP_DSHOW, None]
        
        for i in range(2):  # Try indices 0 and 1
            for backend in backends:
                print(f"🔄 Trying Camera {i} with backend {backend}...")
                try:
                    if backend is not None:
                        cam = cv2.VideoCapture(i, backend)
                    else:
                        cam = cv2.VideoCapture(i)
                    
                    if cam.isOpened():
                        # Set resolution early
                        cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                        cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                        
                        # Aggressive warm up - some cameras need many frames to stabilize exposure
                        success = False
                        for _ in range(15): 
                            ret, frame = cam.read()
                            if ret and frame is not None:
                                # Check if frame is not pitch black
                                if np.mean(frame) > 10: 
                                    success = True
                                    break
                            time.sleep(0.1)
                        
                        if success:
                            self.camera = cam
                            print(f"✅ Camera {i} initialized successfully!")
                            return True
                        else:
                            print(f"⚠️ Camera {i} backend {backend} returned only black frames. Closing...")
                            cam.release()
                except Exception as e:
                    print(f"❌ Error with Camera {i} backend {backend}: {e}")
                
        print("❌ Could not find any working camera.")
        return False

    def start_preview(self):
        """Start camera preview in separate thread"""
        if not self.camera or not self.camera.isOpened():
            if not self.initialize_camera():
                return False

        self.is_capturing = True
        self.capture_thread = Thread(target=self._preview_loop)
        self.capture_thread.start()
        return True

    def _preview_loop(self):
        """Main camera loop with face alignment detection"""
        while self.is_capturing:
            ret, frame = self.camera.read()
            if ret:
                # Mirror effect
                frame = cv2.flip(frame, 1)
                
                # Detect face for guide alignment
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                # Use faster parameters for preview
                faces = self.face_cascade.detectMultiScale(gray, 1.3, 5, minSize=(100, 100))
                
                h, w, _ = frame.shape
                center_x, center_y = w // 2, h // 2
                guide_radius = min(h, w) // 3
                
                self.face_in_guide = False
                for (x, y, fw, fh) in faces:
                    face_center_x = x + fw // 2
                    face_center_y = y + fh // 2
                    
                    # Calculate distance from screen center
                    dist = ((face_center_x - center_x)**2 + (face_center_y - center_y)**2)**0.5
                    if dist < guide_radius // 3: # Face is well centered
                        self.face_in_guide = True
                        break

                # Convert to RGB for PySide
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.current_frame = rgb_frame

            time.sleep(0.03)

    def capture_photo(self):
        """Capture single photo"""
        if self.current_frame is not None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"output/captured/photo_{timestamp}.jpg"

            # Save image
            cv2.imwrite(filename, cv2.cvtColor(self.current_frame, cv2.COLOR_RGB2BGR))

            # Play capture sound
            self.play_capture_sound()

            return filename
        return None

    def play_capture_sound(self):
        """Play capture sound effect"""
        try:
            from PySide6.QtMultimedia import QSoundEffect
            from PySide6.QtCore import QUrl
            sound = QSoundEffect()
            sound.setSource(QUrl.fromLocalFile("src/assets/sounds/capture.wav"))
            sound.play()
        except:
            print("Capture sound played (silent)")

    def stop_camera(self):
        """Stop camera and release resources"""
        self.is_capturing = False
        if self.capture_thread:
            self.capture_thread.join(timeout=2)

        if self.camera:
            self.camera.release()

    def __del__(self):
        self.stop_camera()