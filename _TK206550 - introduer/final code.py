import RPi.GPIO as GPIO
import time
import threading
import cv2
import os
from ultralytics import YOLO
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime

# ================= EMAIL CONFIG =================
sender_email="embedded44@gmail.com"

receiver_emails=["234g5a3210@srit.ac.in",
                 "224g1a32b9@srit.ac.in", "224g1a3292@srit.ac.in",
                 "224g1a3290@srit.ac", "rajeshbabud.cse@srit.ac.in"]

sender_password="alqplnjlmgbyoxst"
smtp_server="smtp.gmail.com"
smtp_port=587

def send_mail(detection, trigger, attachment=None):
    try:
        now=datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        msg=MIMEMultipart()
        msg['From']=sender_email
        msg['To']=", ".join(receiver_emails)
        msg['Subject']=f"Security Alert: {detection}"

        body=f"""
SMART SECURITY ALERT

Trigger    : {trigger}
Detection  : {detection}
Date & Time: {now}

Image stored locally and attached.
"""
        msg.attach(MIMEText(body,'plain'))

        if attachment:
            with open(attachment,'rb') as f:
                img=MIMEImage(f.read())
                img.add_header('Content-Disposition','attachment',
                               filename=os.path.basename(attachment))
                msg.attach(img)

        s=smtplib.SMTP(smtp_server,smtp_port,timeout=10)
        s.starttls()
        s.login(sender_email,sender_password)
        s.sendmail(sender_email,receiver_emails,msg.as_string())
        s.quit()

        print("📧 Mail Sent")

    except Exception as e:
        print("Mail error:",e)

# ================= GPIO =================
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

TRIG=17;ECHO=27;PIR=23;SOUND=22
RED=12;GREEN=20;BUZZ=21

GPIO.setup(TRIG,GPIO.OUT);GPIO.setup(ECHO,GPIO.IN)
GPIO.setup(PIR,GPIO.IN);GPIO.setup(SOUND,GPIO.IN)
GPIO.setup(RED,GPIO.OUT);GPIO.setup(GREEN,GPIO.OUT);GPIO.setup(BUZZ,GPIO.OUT)

GPIO.output(TRIG,0)
GPIO.output(RED,1);GPIO.output(GREEN,1);GPIO.output(BUZZ,1)
time.sleep(2)
GPIO.output(RED,0);GPIO.output(GREEN,0);GPIO.output(BUZZ,0)

# ================= GLOBAL =================
distance=100;pir=0;sound=0
lock=threading.Lock()

# ================= FACE =================
face_cascade=cv2.CascadeClassifier(cv2.data.haarcascades+'haarcascade_frontalface_default.xml')
recognizer=cv2.face.LBPHFaceRecognizer_create()
recognizer.read("trainer.yml")
names={1:"siraj",2:"sohith"}

# ================= YOLO =================
model=YOLO("yolov8n.pt")
animals=["dog","cat","cow","horse","sheep","elephant","bear"]

base="captures"
pf=os.path.join(base,"person")
af=os.path.join(base,"animal")
uf=os.path.join(base,"unknown")
for f in [pf,af,uf]:os.makedirs(f,exist_ok=True)

# ================= SENSOR THREADS =================
def ultrasonic():
    global distance
    while True:
        GPIO.output(TRIG,1);time.sleep(0.00001);GPIO.output(TRIG,0)
        s=time.time();e=time.time();t=time.time()+0.04
        while GPIO.input(ECHO)==0:
            s=time.time()
            if time.time()>t:break
        while GPIO.input(ECHO)==1:
            e=time.time()
            if time.time()>t:break
        with lock:distance=round((e-s)*17150,2)
        time.sleep(0.3)

def pir_t():
    global pir
    while True:
        with lock:pir=GPIO.input(PIR)
        time.sleep(0.1)

# ================= PIR WARMUP =================
def pir_warmup():
    print("pir calibrate...")
    for i in range(30,0,-1):
        time.sleep(1)
        
def sound_t():
    global sound
    while True:
        with lock:sound=GPIO.input(SOUND)
        time.sleep(0.1)

threading.Thread(target=ultrasonic,daemon=True).start()
threading.Thread(target=pir_t,daemon=True).start()
threading.Thread(target=sound_t,daemon=True).start()

# ================= CAMERA =================
cap=cv2.VideoCapture(0)
print("📷 Camera Started")
pir_warmup()

try:
    while True:
        ret,frame=cap.read()
        if not ret:break

        with lock:d,p,s=distance,pir,sound
        print(f"📏{d}cm PIR:{p} SOUND:{s}")

        # -------- Trigger Source --------
        trigger_list=[]
        if d<15: trigger_list.append("Ultrasonic")
        if p==1: trigger_list.append("PIR Motion")
        if s==1: trigger_list.append("Sound")
        trigger_text=" + ".join(trigger_list)

        if not trigger_list:
            GPIO.output(RED,0);GPIO.output(GREEN,1)

        else:
            print("⚠ ALERT")
            GPIO.output(GREEN,0);GPIO.output(RED,1)
            GPIO.output(BUZZ,1);time.sleep(1);GPIO.output(BUZZ,0)

            res=model(frame,imgsz=320,verbose=False)
            person=False;animal=False;animal_name=""

            for r in res:
                for b in r.boxes:
                    label=model.names[int(b.cls[0])]
                    conf=float(b.conf[0])
                    if label=="person" and conf>0.5:person=True
                    if label in animals and conf>0.6:
                        animal=True;animal_name=label

            # ---------- PERSON ----------
            if person:
                print("👤 Face Recognition 5s")

                name="Unknown";accuracy=0
                best=frame.copy()
                start=time.monotonic()

                while time.monotonic()-start<5:
                    cap.grab()
                    ret,f=cap.read()
                    if not ret:continue

                    gray=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY)
                    faces=face_cascade.detectMultiScale(gray,1.3,5)

                    for(x,y,w,h) in faces:
                        id,conf=recognizer.predict(gray[y:y+h,x:x+w])
                        acc=round(100-conf,2)

                        if conf<70:
                            name=names.get(id,"Unknown")
                            accuracy=acc
                            best=f.copy()

                        cv2.rectangle(f,(x,y),(x+w,y+h),(0,255,0),2)
                        cv2.putText(f,f"{name} {acc}%",(x,y-10),
                                    cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,255,0),2)

                    cv2.imshow("Smart Security System",f)
                    cv2.waitKey(1)
                    time.sleep(0.05)

                filename=f"{pf}/{name}_{accuracy}%_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                cv2.imwrite(filename,best)
                send_mail(f"Person: {name} ({accuracy}%)",trigger_text,filename)

            # ---------- ANIMAL ----------
            elif animal:
                filename=f"{af}/{animal_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                cv2.imwrite(filename,frame)
                send_mail(f"Animal: {animal_name}",trigger_text,filename)

            # ---------- UNKNOWN ----------
            else:
                filename=f"{uf}/unknown_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                cv2.imwrite(filename,frame)
                send_mail("Unknown Detection",trigger_text,filename)
            
        cv2.imshow("Smart Security System",frame)
        if cv2.waitKey(1)&0xFF==ord("q"):break

except KeyboardInterrupt:
    print("Stopped")

finally:
    cap.release()
    cv2.destroyAllWindows()
    GPIO.cleanup()
