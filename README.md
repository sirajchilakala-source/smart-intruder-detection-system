# Smart Intruder Detection System

## 📌 Project Overview

The **Smart Intruder Detection System** is an IoT and AI-based security system designed to detect unauthorized intruders using cameras and sensors.

The system combines **motion detection, image processing, and object detection** to identify suspicious activity. When an intruder is detected, the system can generate an alert and send the required information through the communication system.

This project was developed as a **Final Year Project** using Python, IoT technologies, computer vision, and deep learning.

---

## 🎯 Objectives

- Detect unauthorized human movement.
- Capture images or video when suspicious activity is detected.
- Use computer vision and AI-based object detection for intruder identification.
- Reduce false alarms using multiple detection methods.
- Send alerts when an intruder is detected.
- Provide a smart and automated security solution.

---

## 🛠️ Technologies Used

### Programming
- Python

### Computer Vision & AI
- OpenCV
- YOLOv5 / YOLOv8
- Image and video processing

### IoT & Hardware
- Raspberry Pi
- PIR Motion Sensor
- Camera
- Audio/Alarm components
- Thermal sensing components

### Communication
- MQTT

### Development Tools
- Jupyter Notebook
- Python
- Git
- GitHub

---

## ⚙️ System Workflow

```text
        Motion / Sensor Detection
                  │
                  ▼
          Raspberry Pi
                  │
                  ▼
              Camera
                  │
                  ▼
       Image / Video Processing
                  │
                  ▼
         YOLO Object Detection
                  │
                  ▼
       Intruder / Person Detected
                  │
                  ▼
          Alert Generation
                  │
                  ▼
        MQTT / Notification System
```

---

## 🔍 How It Works

1. The **PIR sensor** monitors the surroundings for motion.
2. When motion is detected, the camera is activated to capture the required visual information.
3. **OpenCV** is used for image and video processing.
4. The captured information is analyzed using **YOLO-based object detection**.
5. If an unauthorized person/intruder is identified, the system generates an alert.
6. **MQTT** is used for communication between the IoT components.
7. The captured data can be stored for further analysis or verification.

---

## 🚀 Key Features

- Real-time motion detection
- Camera-based monitoring
- AI-powered object detection
- Human/intruder identification
- IoT-based communication
- MQTT integration
- Automated alert mechanism
- Raspberry Pi-based implementation
- Computer vision using OpenCV

---

## 📂 Project Structure

```text
smart-intruder-detection-system/
│
├── captures/
├── test/
├── main.py
├── final code.py
└── README.md
```

> The exact files and folders may vary depending on the version of the project.

---

## 💻 Installation

### 1. Clone the repository

```bash
git clone git@github.com:sirajchilakala-source/smart-intruder-detection-system.git
```

### 2. Navigate to the project

```bash
cd smart-intruder-detection-system
```

### 3. Install required Python packages

Install the dependencies required by the project.

For example:

```bash
pip install opencv-python
```

Additional packages may be required depending on the YOLO, MQTT, and hardware configuration.

---

## ▶️ Running the Project

Run the main Python program:

```bash
python main.py
```

Depending on the project configuration, the camera, sensors, MQTT communication, and object detection modules should be configured before running the complete system.

---

## 📡 MQTT Communication

MQTT is used as the communication protocol between the IoT components.

The system can publish detection-related information through an MQTT broker, allowing connected devices or applications to receive alerts.

---

## 🔐 Security

The system is designed to improve security by providing automated monitoring and faster intruder detection.

Possible applications include:

- Homes
- Offices
- Laboratories
- Warehouses
- Restricted areas
- Small-scale industrial environments

---

## 📊 Project Outcomes

The project demonstrates how **IoT, computer vision, and AI-based object detection** can be combined to create an automated security system.

It provides a foundation for developing more advanced surveillance systems with features such as real-time notifications, cloud storage, face recognition, and centralized monitoring.

---

## 🔮 Future Enhancements

The system can be further improved by adding:

- Face recognition
- Mobile application integration
- Cloud-based image/video storage
- Real-time mobile notifications
- Multiple camera support
- Improved object detection accuracy
- Remote monitoring dashboard
- GPS/location-based alerts
- Advanced analytics and reporting

---

## 👨‍💻 Developer

**Siraj Chilakala**

B.Tech – Computer Science and Engineering (Data Science)  
Srinivasa Ramanujan Institute of Technology, Anantapur

### GitHub

**Username:** `sirajchilakala-source`

---

## 📜 License

This project was developed for academic and educational purposes as part of a Final Year Project.
