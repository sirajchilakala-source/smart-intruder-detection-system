#pip uninstall opencv-python opencv-contrib-python -y
#pip install opencv-contrib-python==4.5.5.64

import cv2
import os
import numpy as np

# Create directories to store registered faces
face_dir = 'faces'
if not os.path.exists(face_dir):
    os.makedirs(face_dir)

# Initialize face detector and recognizer
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
recognizer = cv2.face.LBPHFaceRecognizer_create()

# User names mapped to their IDs
user_names = {
    1: "siraj",
    2: "sohith",
    3: ""
}

# Function to detect face and save images for registration
def register_face(face_id):
    cam = cv2.VideoCapture(0)
    count = 0
    print("Capturing face images for face ID:", face_id)
    
    while True:
        ret, frame = cam.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        for (x, y, w, h) in faces:
            count += 1
            face_img = gray[y:y+h, x:x+w]
            # Save the captured face in the dataset folder
            cv2.imwrite(f"{face_dir}/user.{face_id}.{count}.jpg", face_img)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        
        cv2.imshow('Registering Face', frame)
        
        # Stop after 30 images are captured
        if count >= 100:
            break
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cam.release()
    cv2.destroyAllWindows()
    print("Face registration completed.")

# Function to train the recognizer with registered faces
def train_recognizer():
    face_samples = []
    ids = []
    image_paths = [os.path.join(face_dir, f) for f in os.listdir(face_dir) if f.endswith('.jpg')]
    
    for image_path in image_paths:
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        face_id = int(os.path.split(image_path)[-1].split('.')[1])
        face_samples.append(img)
        ids.append(face_id)
    
    recognizer.train(face_samples, np.array(ids))
    recognizer.save('trainer.yml')
    print("Training completed.")

# Function to recognize face in live video feed
def recognize_face():
    recognizer.read('trainer.yml')
    cam = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cam.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        for (x, y, w, h) in faces:
            face_img = gray[y:y+h, x:x+w]
            face_id, confidence = recognizer.predict(face_img)
            
            if confidence < 40:
                name = user_names.get(face_id, "Unknown")
                confidence_text = f"{100 - confidence:.2f}%"
                print(f"Recognized: {name} (ID: {face_id}) with confidence {confidence_text}")
            else:
                name = "Unknown"
                confidence_text = f"{100 - confidence:.2f}%"
                print("Recognized: Unknown")
            
            cv2.putText(frame, name, (x+5, y-5), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            cv2.putText(frame, confidence_text, (x+5, y+h-5), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        
        cv2.imshow('Face Recognition', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cam.release()
    cv2.destroyAllWindows()
    
while True:
    # Main program
    print("1: Register Face")
    print("2: Train Recognizer")
    print("3: Recognize Face")
    choice = input("Enter your choice: ")

    if choice == '1':
        face_id = input("Enter face ID (1 for Alice, 2 for Bob, etc.): ")
        register_face(face_id)
    elif choice == '2':
        train_recognizer()
    elif choice == '3':
        recognize_face()
    else:
        print("Invalid choice!")
