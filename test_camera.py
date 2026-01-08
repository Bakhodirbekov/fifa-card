"""
Test script to check camera availability
"""
import cv2
import numpy as np

print("=" * 50)
print("🎥 CAMERA TEST SCRIPT")
print("=" * 50)

# Test 1: Check OpenCV version
print(f"\n✓ OpenCV Version: {cv2.__version__}")

# Test 2: Try to find available cameras
print("\n🔍 Searching for cameras...")
available_cameras = []

for i in range(5):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            print(f"  ✅ Camera {i} found and working!")
            available_cameras.append(i)
        else:
            print(f"  ⚠️ Camera {i} opened but can't read frames")
        cap.release()
    else:
        print(f"  ❌ Camera {i} not available")

print(f"\n📊 Total cameras found: {len(available_cameras)}")

if len(available_cameras) > 0:
    print("\n🎬 Testing first available camera...")
    camera_index = available_cameras[0]
    
    cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    print("📸 Press 'q' to quit, 's' to save test image...")
    
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if ret:
            frame_count += 1
            cv2.putText(frame, f"Frame: {frame_count}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow('Camera Test', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                cv2.imwrite('test_frame.jpg', frame)
                print("✅ Test image saved as 'test_frame.jpg'")
        else:
            print("❌ Failed to read frame")
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print("\n✅ Camera test completed successfully!")
else:
    print("\n❌ NO CAMERAS FOUND!")
    print("\n💡 Possible solutions:")
    print("  1. Check if camera is connected properly")
    print("  2. Check Windows Camera permissions (Settings > Privacy > Camera)")
    print("  3. Close other apps using camera (Skype, Teams, etc.)")
    print("  4. Try plugging in an external USB camera")

print("\n" + "=" * 50)
