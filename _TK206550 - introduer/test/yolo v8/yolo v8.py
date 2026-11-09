import cv2
import torch
from ultralytics import YOLO

# Load the YOLOv8 model (using the small 'n' version for speed)
model = YOLO("yolov8n.pt")  # Make sure the model file is in the same directory

# Initialize webcam
cap = cv2.VideoCapture(0)

# List of animal classes to detect
#animal_classes = ["person"]
#animal_classes = ["dog", "cat", "cow", "horse", "sheep", "elephant", "bear", "zebra", "giraffe", "bird"]
animal_classes = ["elephant", "bear"]

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break  # Exit loop if no frame is captured

    # Run YOLOv8 inference on the frame
    results = model(frame)
    #results = model(frame, verbose=False)  # Suppressing speed metrics output

    # Draw bounding boxes on the frame
    for result in results:
        for box in result.boxes:
            cls_id = int(box.cls[0])  # Class ID
            label = model.names[cls_id]  # Class name
            confidence = float(box.conf[0])  # Confidence score
            
            # Get bounding box coordinates
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            # Draw bounding box and label
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"{label} {confidence:.2f}", (x1, y1 - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            # Check if the detected object is an animal and confidence is > 0.7
            if label in animal_classes and confidence > 0.7:
                
                #print(f"Detected: {label} with confidence {confidence:.2f}")
                # Get bounding box coordinates
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                # Draw bounding box and label
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{label} {confidence:.2f}", (x1, y1 - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Show the live detection feed
    cv2.imshow("YOLOv8 Live Detection", frame)

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Release the camera and close OpenCV windows
cap.release()
cv2.destroyAllWindows()
