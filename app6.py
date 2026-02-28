from flask import Flask, render_template, jsonify, request
from mpu6050 import mpu6050
import time
import math
import json
import threading
import subprocess
import os
import requests

app = Flask(__name__)

sensor = mpu6050(0x68)  # Adresse I2C par défaut

ultrason_data = {"avant": 0, "arriere": 0}

pitch_prev, roll_prev, yaw_prev = 0.0, 0.0, 0.0
yaw = 0.0
offset_x = 0.0
offset_y = 0.0
offset_z = 9.8
last_time = time.time()

# Recevoir les données des capteurs ultrasons 
def launch_servo_distance_program():
    while True:
        try:
            response = requests.get("http://172.20.10.14:5002/start-scan")
            print(f"Réponse de la Pi : {response.text}")
        except Exception as e:
            print(f"Erreur lors de l'appel à la Pi : {e}")
        time.sleep(10)   
        
        
#ROTATION ROBOT

@app.route('/get_orientation')
def get_orientation():
    # Récupère les données du capteur
    accel = sensor.get_accel_data()
    gyro = sensor.get_gyro_data()
    print("Données capteur:", accel)

    # Calcul des angles
    accel_x = accel['x']
    accel_y = accel['y']
    accel_z = accel['z']
    
    # Calcul du Pitch et du Roll
    pitch = math.atan2(accel_y, math.sqrt(accel_x**2 + accel_z**2))
    roll = math.atan2(-accel_x, math.sqrt(accel_y**2 + accel_z**2))
    
    # Conversion en degrés
    pitch_deg = math.degrees(pitch)
    roll_deg = math.degrees(roll)

    # Retourne les données sous forme de JSON
    return jsonify({'pitch': pitch_deg, 'roll': roll_deg})
    

#CALIBRATION

def calibrate_sensor(duration=0.2):
    global offset_x, offset_y, offset_z
    print("Calibration... Ne pas toucher le capteur.")
    samples = []
    start_time = time.time()

    while time.time() - start_time < duration:
        accel = sensor.get_accel_data()
        samples.append((accel['x'], accel['y'], accel['z']))
        time.sleep(0.05)  # 20 Hz

    count = len(samples)
    offset_x = sum(s[0] for s in samples) / count
    offset_y = sum(s[1] for s in samples) / count
    offset_z = sum(s[2] for s in samples) / count
    print(f"Calibration terminée : offset_x={offset_x:.2f}, offset_y={offset_y:.2f}, offset_z={offset_z:.2f}")
# Appel au démarrage du serveur
calibrate_sensor()

def get_pitch_roll(accel):
    accel_x = accel['x'] - offset_x
    accel_y = accel['y'] - offset_y
    accel_z = accel['z'] - offset_z
    pitch = math.atan2(accel_y, math.sqrt(accel_x**2 + accel_z**2))
    roll = math.atan2(-accel_x, math.sqrt(accel_y**2 + accel_z**2))
    return math.degrees(pitch), math.degrees(roll)
    
    
def auto_calibrate(interval=0.2, threshold=3.0):
    global pitch_prev, roll_prev, yaw_prev
    while True:
        accel = sensor.get_accel_data()
        gyro = sensor.get_gyro_data()
        pitch, roll = get_pitch_roll(accel)

        # Calcul yaw par intégration du gyro
        global yaw, last_time
        current_time = time.time()
        dt = current_time - last_time
        last_time = current_time
        yaw += math.radians(gyro['z']) * dt
        yaw_deg = math.degrees(yaw)

        # Recalibrer si l’un des angles a trop changé
        if (abs(pitch - pitch_prev) > threshold or
            abs(roll - roll_prev) > threshold or
            abs(yaw_deg - yaw_prev) > threshold):
            print("Variation détectée, recalibrage...")
            calibrate_sensor()

        pitch_prev, roll_prev, yaw_prev = pitch, roll, yaw_deg
        time.sleep(interval)
        
@app.route('/recalibrate', methods=['POST'])
def recalibrate():
    calibrate_sensor()
    return jsonify({"status": "success", "message": "Calibration relancée "})        


#DEPLACEMENT ROBOT

@app.route('/get_yaw')
def get_yaw():
    global yaw, last_time, velocity_x, velocity_y, position_x, position_y, stationary_start
    accel = sensor.get_accel_data()
    gyro = sensor.get_gyro_data()

    accel_x = accel['x']
    accel_y = accel['y']

    # Appliquer un seuil pour éviter d'intégrer du bruit
    threshold = 2 # tu peux ajuster cette valeur
    cost = 1
    
    current_time = time.time()
    dt = current_time - last_time
    last_time = current_time

    # Intégration de la vitesse angulaire pour obtenir le yaw
    if cost < gyro['z'] < cost:
        yaw = 0
    else:
        yaw += math.radians(gyro['z']) * dt

    # Déplacement basé sur l’orientation gyroscopique
    move_x = 0
    move_y = 0
    real_accel_x = accel['x'] - offset_x
    real_accel_y = accel['y'] - offset_y

    if abs(real_accel_x) > threshold:
        move_x = 1 if real_accel_x > 0 else -1

    if abs(real_accel_y) > threshold:
        move_y = 1 if real_accel_y > 0 else -1

    return jsonify({
        'yaw': yaw,
        'move_x': move_x,
        'move_z': move_y
    })
    


#MURS


    
@app.route('/')
def index():
    return render_template('index13.html')  # Remplace 'index.html' par le nom de ton fichier HTML
        
 
 
 
@app.route('/get_scan')
def get_murs():
    try:
        with open("/home/cantos/robot_orientation/murs.json", "r") as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)})
        
    

if __name__ == '__main__':
    calibration_thread = threading.Thread(target=auto_calibrate, daemon=True)
    calibration_thread.start()
    scan_thread = threading.Thread(target=launch_servo_distance_program, daemon=True)
    scan_thread.start()
    app.run(host='0.0.0.0', port=5001, debug=True)

