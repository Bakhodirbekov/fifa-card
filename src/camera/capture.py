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

        print("🎥 Starting camera initialization...")
        
        # Try different backends in order of preference for Windows
        backends = [
            (cv2.CAP_DSHOW, "DirectShow"),
            (cv2.CAP_MSMF, "Media Foundation"),
            (None, "Default")
        ]
        
        # Try multiple camera indices
        for i in range(3):  # Try indices 0, 1, 2
            for backend, backend_name in backends:
                print(f"🔄 Trying Camera {i} with {backend_name}...")
                try:
                    # Attempt to create VideoCapture with backend
                    if backend is not None:
                        cam = cv2.VideoCapture(i, backend)
                    else:
                        cam = cv2.VideoCapture(i)
                    
                    if cam.isOpened():
                        # Set resolution
                        cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                        cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                        cam.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                        
                        # Wait for camera to stabilize
                        time.sleep(0.5)
                        
                        # Try to read frames
                        success = False
                        for attempt in range(10):
                            ret, frame = cam.read()
                            if ret and frame is not None and frame.size > 0:
                                avg_brightness = np.mean(frame)
                                if avg_brightness > 5:
                                    success = True
                                    self.camera = cam
                                    print(f"✅ Camera {i} initialized successfully with {backend_name}!")
                                    return True
                            time.sleep(0.1)
                        
                        if not success:
                            print(f"⚠️ Camera {i} ({backend_name}) returned invalid frames")
                            cam.release()
                    
                except Exception as e:
                    print(f"❌ Error with camera {i} ({backend_name}): {str(e)[:100]}")
        
        print("=" * 60)
        print("❌ NO CAMERA FOUND!")
        print("=" * 60)
        print("💡 Troubleshooting steps:")
        print("  1. Check Windows Camera permissions:")
        print("     Settings > Privacy & Security > Camera")
        print("  2. Close apps using camera (Teams, Zoom, Skype)")
        print("  3. Try plugging in a USB webcam")
        print("  4. Restart the application")
        print("=" * 60)
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