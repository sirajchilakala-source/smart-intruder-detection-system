import cv2

# Open the default camera (usually the built-in webcam)
cap = cv2.VideoCapture(0)

# Set video frame width and height (optional)
frameWidth = 640
frameHeight = 480
cap.set(3, frameWidth)
cap.set(4, frameHeight)

# Loop to capture each frame
while True:
    success, img = cap.read()  # Capture a frame
    if not success:
        break  # Break the loop if the frame is not captured

    # Show the frame in a window
    cv2.imshow("Camera Feed", img)

    # Press 'q' to exit the camera view
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()
