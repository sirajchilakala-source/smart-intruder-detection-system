import RPi.GPIO as GPIO
import time
import threading
import cv2
import os
import numpy as np
import datetime
from ultralytics import YOLO

import smtplib 
from email.mime.text import MIMEText 
from email.mime.multipart import MIMEMultipart 
from email.mime.image import MIMEImage 
from datetime import datetime

# Email credentials 
sender_email = "embedded44@gmail.com" 
receiver_emails = ["paneu7120@gmail.com"] 
sender_password = "alqplnjlmgbyoxst" 
smtp_server = "smtp.gmail.com" 
smtp_port = 587

def capture_photo(frame): 
    print("Capturing image from the current frame...") 
 
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") 
    filename = f"photo_{timestamp}.jpg" 
    cv2.imwrite(filename, frame)  # Save the current frame as the image 
    print(f"Photo saved as {filename}") 
     
    return filename 

# Function to send email with the person's name in the subject and body 
def send_mail(person_name, attachment=None): 
    print(f"Sending mail for {person_name}") 
    time.sleep(2) 
 
    msg = MIMEMultipart() 
    msg['From'] = sender_email 
    msg['To'] = ", ".join(receiver_emails) 
    msg['Subject'] = f"{person_name} detected" 
 
    body_text = f"{person_name} detected at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.\n\nPlease find the attached photo." 
    msg.attach(MIMEText(body_text, 'plain')) 
 
    if attachment: 
        with open(attachment, 'rb') as fp: 
            img_data = MIMEImage(fp.read()) 
            msg.attach(img_data) 
 
    with smtplib.SMTP(smtp_server, smtp_port) as server: 
        server.starttls() 
        server.login(sender_email, sender_password) 
        server.sendmail(sender_email, receiver_emails, msg.as_string()) 
 
    print("Mail sent") 
    time.sleep(2) 
# ================= GPIO INITIALIZATION =================
GPIO.setwarnings(False)
GPIO.cleanup()
GPIO.setmode(GPIO.BCM)

TRIG = 17
ECHO = 27
PIR = 23
SOUND = 22

RED_LED = 12
GREEN_LED = 20
BUZZER = 21

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.setup(PIR, GPIO.IN)
GPIO.setup(SOUND, GPIO.IN)

GPIO.setup(RED_LED, GPIO.OUT)
GPIO.setup(GREEN_LED, GPIO.OUT)
GPIO.setup(BUZZER, GPIO.OUT)

GPIO.output(TRIG, GPIO.LOW)
GPIO.output(BUZZER, GPIO.HIGH)
GPIO.output(GREEN_LED, GPIO.HIGH)
GPIO.output(RED_LED, GPIO.HIGH)
time.sleep(2)
GPIO.output(GREEN_LED, GPIO.LOW)
GPIO.output(RED_LED, GPIO.LOW)
GPIO.output(BUZZER, GPIO.LOW)
# ================= GLOBAL VARIABLES =================
distance_value = 100
pir_value = 0
sound_value = 0
lock = threading.Lock()

last_capture_time = 0
capture_cooldown = 10

# ================= FACE SETUP =================
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("trainer.yml")

user_names = {1: "PR", 2: "Nikitha"}

# ================= YOLO SETUP =================
model = YOLO("yolov8n.pt")
animal_classes = ["dog", "cat", "cow", "horse", "sheep", "elephant", "bear"]

# Create folders
base_path = "captures"
person_folder = os.path.join(base_path, "person")
animal_folder = os.path.join(base_path, "animal")
unknown_folder = os.path.join(base_path, "unknown")

for folder in [person_folder, animal_folder, unknown_folder]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# ================= ULTRASONIC THREAD =================
def ultrasonic_thread():
    global distance_value
    while True:
        GPIO.output(TRIG, True)
        time.sleep(0.00001)
        GPIO.output(TRIG, False)

        pulse_start = time.time()
        pulse_end = time.time()
        timeout = time.time() + 0.04

        while GPIO.input(ECHO) == 0:
            pulse_start = time.time()
            if time.time() > timeout:
                break

        while GPIO.input(ECHO) == 1:
            pulse_end = time.time()
            if time.time() > timeout:
                break

        distance = (pulse_end - pulse_start) * 17150
        distance = round(distance, 2)

        with lock:
            distance_value = distance

        time.sleep(0.3)

# ================= PIR THREAD =================
def pir_thread():
    global pir_value
    while True:
        with lock:
            pir_value = GPIO.input(PIR)
        time.sleep(0.1)

# ================= SOUND THREAD =================
def sound_thread():
    global sound_value
    while True:
        with lock:
            sound_value = GPIO.input(SOUND)
        time.sleep(0.1)

# Start threads
threading.Thread(target=ultrasonic_thread, daemon=True).start()
threading.Thread(target=pir_thread, daemon=True).start()
threading.Thread(target=sound_thread, daemon=True).start()

# ================= CAMERA START =================
cap = cv2.VideoCapture(0)
print("📷 Camera Started...")

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        with lock:
            d = distance_value
            p = pir_value
            s = sound_value

        print(f"📏 Distance: {d} cm | 🚶 PIR: {p} | 🔊 Sound: {s}")

        trigger = (d < 15 or p == 1 or s == 1)

        # ================= NORMAL STATE =================
        if not trigger:
            GPIO.output(RED_LED, GPIO.LOW)
            GPIO.output(GREEN_LED, GPIO.HIGH)

        # ================= TRIGGERED =================
        else:
            print("⚠ ALERT Triggered!")

            GPIO.output(GREEN_LED, GPIO.LOW)
            GPIO.output(RED_LED, GPIO.HIGH)
            GPIO.output(BUZZER, GPIO.HIGH)
            time.sleep(1)
            GPIO.output(BUZZER, GPIO.LOW)

            results = model(frame, imgsz=320, verbose=False)

            person_detected = False
            animal_detected = False
            detected_label = ""

            for result in results:
                for box in result.boxes:
                    cls_id = int(box.cls[0])
                    label = model.names[cls_id]
                    conf = float(box.conf[0])

                    if label == "person" and conf > 0.5:
                        person_detected = True

                    if label in animal_classes and conf > 0.6:
                        animal_detected = True
                        detected_label = label

            current_time = time.time()

            # -------- PERSON DETECTED --------
            if person_detected:
                print("👤 Person Detected → Face Recognition 5 sec")

                face_name = "Unknown"
                face_start = time.time()

                while time.time() - face_start < 5:
                    ret, face_frame = cap.read()
                    if not ret:
                        break

                    gray_face = cv2.cvtColor(face_frame, cv2.COLOR_BGR2GRAY)
                    faces = face_cascade.detectMultiScale(gray_face, 1.3, 5)

                    for (x, y, w, h) in faces:
                        face_img = gray_face[y:y+h, x:x+w]
                        face_id, confidence = recognizer.predict(face_img)
                        face_name = user_names.get(face_id, "Unknown")

                        cv2.rectangle(face_frame, (x,y),(x+w,y+h),(255,0,0),2)
                        cv2.putText(face_frame, face_name, (x,y-10),
                                    cv2.FONT_HERSHEY_SIMPLEX,0.8,(255,0,0),2)

                    cv2.imshow("Smart Security System", face_frame)

                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        break

                if current_time - last_capture_time > capture_cooldown:
                    filename = f"{person_folder}/{face_name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                    cv2.imwrite(filename, face_frame)
                    print(f"📸 Person Saved: {filename}")
                    send_mail(face_name,filename)
                    last_capture_time = current_time

                cv2.destroyAllWindows()

            # -------- ANIMAL DETECTED --------
            elif animal_detected:
                if current_time - last_capture_time > capture_cooldown:
                    filename = f"{animal_folder}/{detected_label}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                    cv2.imwrite(filename, frame)
                    print(f"🐾 Animal Saved: {filename}")
                    send_mail(face_name,filename)
                    last_capture_time = current_time

            # -------- UNKNOWN TRIGGER --------
            else:
                if current_time - last_capture_time > capture_cooldown:
                    filename = f"{unknown_folder}/unknown_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                    cv2.imwrite(filename, frame)
                    print(f"⚠ Unknown Saved: {filename}")
                    send_mail(face_name,filename)
                    last_capture_time = current_time

        cv2.imshow("Smart Security System", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

except KeyboardInterrupt:
    print("System Stopped")

finally:
    cap.release()
    cv2.destroyAllWindows()
    GPIO.cleanup()
