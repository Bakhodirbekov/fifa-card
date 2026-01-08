"""
Simple camera permissions test
"""
import cv2
import sys

print("🔍 Testing notebook camera...")
print(f"OpenCV version: {cv2.__version__}")

# Try with DirectShow (best for Windows laptops)
print("\n📸 Attempting to open camera with DirectShow...")
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if cap.isOpened():
    print("✅ Camera opened successfully!")
    
    # Try to read a frame
    ret, frame = cap.read()
    if ret:
        print("✅ Frame captured successfully!")
        print(f"   Frame size: {frame.shape}")
        
        # Show camera feed
        print("\n🎥 Displaying camera feed...")
        print("   Press 'q' to quit, 's' to save test image")
        
        while True:
            ret, frame = cap.read()
            if ret:
                cv2.imshow('Notebook Camera Test', frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    cv2.imwrite('notebook_test.jpg', frame)
                    print("✅ Test image saved!")
            else:
                print("❌ Failed to read frame")
                break
        
        cap.release()
        cv2.destroyAllWindows()
        print("\n✅ Camera test completed successfully!")
        sys.exit(0)
    else:
        print("❌ Could not read frame from camera")
        cap.release()
else:
    print("❌ Could not open camera")

print("\n" + "="*60)
print("❌ CAMERA ACCESS FAILED")
print("="*60)
print("\n💡 Solutions:")
print("1. Check Windows Camera permissions (Settings just opened)")
print("2. Make sure 'Desktop apps' can access camera")
print("3. Close other apps using camera (Teams, Zoom, etc.)")
print("4. Try restarting your computer")
print("5. Update camera drivers from Device Manager")
print("="*60)
sys.exit(1)
