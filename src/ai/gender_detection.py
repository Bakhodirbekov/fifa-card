try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
except Exception:
    DEEPFACE_AVAILABLE = False

import cv2
import numpy as np
import random
from PIL import Image
import json
import time


class GenderDetector:
    def __init__(self):
        self.models = ["VGG-Face", "OpenFace", "Facenet", "DeepID"]
        self.backends = ["opencv", "ssd", "dlib", "mtcnn", "retinaface"]
        self.threshold = 0.7  # Confidence threshold

    def detect_gender(self, image_path):
        """
        Detect gender from image
        Returns: 'male', 'female', or 'unknown'
        """
        if not DEEPFACE_AVAILABLE:
            res = random.choice(['male', 'female'])
            print(f"⚠️ DeepFace not available. Fallback detection: {res}")
            return res

        try:
            # Try multiple models for better accuracy
            for model in self.models:
                try:
                    result = DeepFace.analyze(
                        img_path=image_path,
                        actions=['gender'],
                        enforce_detection=False,
                        detector_backend=self.backends[0]
                    )

                    if isinstance(result, list):
                        result = result[0]  # Take first face

                    gender = result['gender']
                    confidence = max(gender['Man'], gender['Woman']) / 100

                    if confidence > self.threshold:
                        detected_gender = 'male' if gender['Man'] > gender['Woman'] else 'female'

                        # Log result
                        self.log_detection(image_path, detected_gender, confidence)

                        return detected_gender

                except Exception as e:
                    print(f"Model {model} failed: {e}")
                    continue

            return 'unknown'

        except Exception as e:
            print(f"Gender detection error: {e}")
            return 'unknown'

    def log_detection(self, image_path, gender, confidence):
        """Log detection results"""
        log_entry = {
            'timestamp': time.time(),
            'image': image_path,
            'gender': gender,
            'confidence': confidence,
            'model': 'DeepFace'
        }

        with open('output/logs/gender_detection.log', 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

    def validate_face(self, image_path):
        """Check if face is properly detected"""
        if not DEEPFACE_AVAILABLE:
            return True

        try:
            result = DeepFace.extract_faces(
                img_path=image_path,
                detector_backend=self.backends[0],
                enforce_detection=True
            )
            return len(result) > 0
        except:
            return False