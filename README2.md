# 🚒 Firefighter Intervention Robot – LANCELOT

A multidisciplinary engineering project developed for the French Fire Department (SDIS de l’Aude), designed to operate in hazardous environments including toxic gas zones, chemical risks, structural collapse areas and confined spaces.

---

## 🎯 Project Objective

Design and build a mobile robotic platform capable of:

- Navigating complex terrain (stairs, debris, uneven surfaces)
- Detecting hazardous gases
- Providing real-time video feedback
- Transmitting sensor data remotely
- Operating safely in unstable environments

---

## 🛠 System Architecture

### 🔹 Mobility System
- Tracked locomotion system
- High-torque DC motors
- Gear reduction transmission
- Stair-climbing capability
- Linear actuators for track articulation

### 🔹 Embedded Control
- ESP32 microcontroller
- Raspberry Pi for high-level processing
- Motor drivers (Roboclaw / Cytron)
- Gyroscope stabilization

### 🔹 Sensors
- Gas sensors (CO, NH3, NO2)
- Distance sensors
- Temperature monitoring
- Gyroscopic orientation feedback

### 🔹 Communication
- LoRa long-range data transmission
- Secure remote server
- Real-time data visualization
- HTML/CSS/JS monitoring interface

### 🔹 Video System
- 1080p onboard camera
- Low latency video transmission
- HDMI output for field operators

---

## 📡 Data Flow

Sensors → ESP32 → Raspberry Pi → LoRa / Server → Remote Interface  
Camera → Video Module → Receiver → Operator Interface  

---

## 📂 Repository Content

- Embedded control code (ESP32 / Raspberry Pi)
- Sensor integration scripts
- Communication protocols
- Server-side interface code
- Control logic implementation

---

## 🧠 Engineering Methods Applied

- Requirements engineering
- Risk matrix analysis
- Gantt planning
- Systems architecture validation
- Mechanical simulations (SolidWorks)
- Iterative prototyping

---

## 👨‍🚒 Real-World Impact

This project was developed in collaboration with professional firefighters to improve intervention safety in high-risk environments.

---

## 📌 Author

Florent Bajard  
Engineering Student – Robotics & Mechanical Systems
