import RPi.GPIO as GPIO
import time
import threading

# GPIO Mode
GPIO.setmode(GPIO.BCM)

# ---------------- PIN DEFINITIONS ----------------
TRIG = 17
ECHO = 27
SOUND = 22
PIR = 23

RED_LED = 20
GREEN_LED = 16
BUZZER = 21

# ---------------- SETUP ----------------
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.setup(SOUND, GPIO.IN)
GPIO.setup(PIR, GPIO.IN)

GPIO.setup(RED_LED, GPIO.OUT)
GPIO.setup(GREEN_LED, GPIO.OUT)
GPIO.setup(BUZZER, GPIO.OUT)

GPIO.output(TRIG, False)

print("Waiting for sensors to settle...")
time.sleep(5)

# Shared Variables
distance_value = 0
sound_value = 0
pir_value = 0

lock = threading.Lock()

# ---------------- ULTRASONIC THREAD ----------------
def ultrasonic_thread():
    global distance_value
    while True:
        GPIO.output(TRIG, True)
        time.sleep(0.00001)
        GPIO.output(TRIG, False)

        pulse_start = time.time()
        pulse_end = time.time()

        while GPIO.input(ECHO) == 0:
            pulse_start = time.time()

        while GPIO.input(ECHO) == 1:
            pulse_end = time.time()

        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150
        distance = round(distance, 2)

        with lock:
            distance_value = distance

        time.sleep(0.3)

# ---------------- SOUND THREAD ----------------
def sound_thread():
    global sound_value
    while True:
        with lock:
            sound_value = GPIO.input(SOUND)
        time.sleep(0.1)

# ---------------- PIR THREAD ----------------
def pir_thread():
    global pir_value
    while True:
        with lock:
            pir_value = GPIO.input(PIR)
        time.sleep(0.1)

# Start Threads
threading.Thread(target=ultrasonic_thread, daemon=True).start()
threading.Thread(target=sound_thread, daemon=True).start()
threading.Thread(target=pir_thread, daemon=True).start()

# ---------------- MAIN LOOP ----------------
try:
    while True:
        with lock:
            d = distance_value
            s = sound_value
            p = pir_value

        print(f"Distance: {d} cm | Sound: {s} | PIR: {p}")

        # ----- Define Abnormal Condition -----
        abnormal = False

        if d < 10:   # Object very close
            abnormal = True

        if s == 1:   # Sound detected
            abnormal = True

        if p == 1:   # Motion detected
            abnormal = True

        # ----- LED + Buzzer Logic -----
        if abnormal:
            GPIO.output(GREEN_LED, GPIO.LOW)
            GPIO.output(RED_LED, GPIO.HIGH)
            GPIO.output(BUZZER, GPIO.HIGH)
            print("⚠️ ABNORMAL CONDITION!")
            time.sleep(1)
            GPIO.output(BUZZER, GPIO.LOW)
        else:
            GPIO.output(RED_LED, GPIO.LOW)
            GPIO.output(GREEN_LED, GPIO.HIGH)

        print("---------------------------")
        time.sleep(1)

except KeyboardInterrupt:
    print("Program stopped")

finally:
    GPIO.cleanup()
