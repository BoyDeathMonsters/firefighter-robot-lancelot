from flask import Flask, render_template, jsonify, request
from mpu6050 import mpu6050
import time
import math
import json
import threading
import subprocess

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
@app.route('/update_ultrasons', methods=['POST'])
def update_ultrasons():
    global ultrason_data
    data = request.get_json()
    ultrason_data['avant'] = data.get("avant", 0)
    ultrason_data['arriere'] = data.get("arriere", 0)
    return {"status": "ok"}        


def launch_servo_distance_program():
    subprocess.Popen(['python3', 'servo_distance.py'])    
    
@app.route('/')
def index():
    launch_servo_distance_program()
    return render_template('index13.html')  # Remplace 'index.html' par le nom de ton fichier HTML
        
    
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

# Appel au démarrage du serveur
calibrate_sensor()


@app.route('/get_yaw')
def get_yaw():
    global yaw, last_time, velocity_x, velocity_z, position_x, position_z, stationary_start
    accel = sensor.get_accel_data()
    gyro = sensor.get_gyro_data()

    accel_x = accel['x']
    accel_z = accel['z']

    # Appliquer un seuil pour éviter d'intégrer du bruit
    threshold = 2 # tu peux ajuster cette valeur

    current_time = time.time()
    dt = current_time - last_time
    last_time = current_time

    # Intégration de la vitesse angulaire pour obtenir le yaw
    yaw += math.radians(gyro['z']) * dt

    # Déplacement basé sur l’orientation gyroscopique
    move_x = 0
    move_z = 0
    real_accel_x = accel['x'] - offset_x
    real_accel_z = accel['z'] - offset_z

    if abs(real_accel_x) > threshold:
        move_x = 1 if real_accel_x > 0 else -1

    if abs(real_accel_z) > threshold:
        move_z = 1 if real_accel_z > 0 else -1

    return jsonify({
        'yaw': yaw,
        'move_x': move_x,
        'move_z': move_z
    })



    
@app.route('/get_scan')
def get_murs():
    try:
        with open("/home/cantos/robot_orientation/murs.json", "r") as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/recalibrate', methods=['POST'])
def recalibrate():
    calibrate_sensor()
    return jsonify({"status": "success", "message": "Calibration relancée "})


def get_orientation_actuelle():
    global last_time, yaw
    gyro = sensor.get_gyro_data()
    current_time = time.time()
    dt = current_time - last_time
    last_time = current_time

    # Intégration de la vitesse angulaire pour obtenir le yaw
    yaw += math.radians(gyro['z']) * dt
    return ({
        'yaw': yaw
        })

def placer_murs_autour_robot(donnees, orientation_deg):
    murs = {}
    orientation_deg = orientation_deg.get("yaw", 0)
    orientation_rad = math.radians(orientation_deg)

    for point in donnees:
        angle_local = math.radians(point["angle"])  # angle relatif au robot
        distance_cm = point["distance"]

        if distance_cm <= 0 or distance_cm > 400:
            continue

        # Angle absolu = orientation du robot + angle local
        angle_absolu = orientation_rad + angle_local

        x = (distance_cm / 10) * math.cos(angle_absolu)  # en décimètres
        z = (distance_cm / 10) * math.sin(angle_absolu)

        # On stocke avec les coordonnées globales autour du robot
        # Ici tu pourrais aussi ajouter la position (x_robot, z_robot) si le robot avance
        murs[(round(x, 2), round(z, 2))] = {
            "x": round(x, 2),
            "z": round(z, 2),
            "angle": point["angle"],
            "distance": point["distance"]
        }

    return murs

def supprimer_anciens_murs(nouveaux_points, memoire):
    angles_nouveaux = set()
    for point in nouveaux_points:
        angle = point["angle"]
        angles_nouveaux.add(angle)

    # Création de la liste des clés à supprimer
    cles_a_supprimer = []
    for (angle, distance) in memoire.keys():
        if angle in angles_nouveaux:
            cles_a_supprimer.append((angle, distance))

    # Suppression des murs dans la zone de scan
    for cle in cles_a_supprimer:
        del memoire[cle]

# Dictionnaire global qui contient les murs (clé: (angle, distance), valeur: coordonnées)
mur_memoire = {}

def mise_a_jour_murs():
    while True:
        subprocess.run(["python3", "servo_distance.py"])
        with open('murs.json', 'r') as f:
                donnees = json.load(f)

        orientation = get_orientation_actuelle()  # Ton yaw actuel
        murs_actuels = placer_murs_autour_robot(donnees, orientation)
        supprimer_anciens_murs(donnees, mur_memoire)
        for cle in murs_actuels:
            mur_memoire[cle] = murs_actuels[cle]

        # Optionnel : nettoyage intelligent
        # supprimer_anciens_murs(donnees, mur_memoire)

        time.sleep(5)

# Lancer la tâche en arrière-plan
thread = threading.Thread(target=mise_a_jour_murs)
thread.daemon = True
thread.start()    

@app.route('/api/murs')
def api_murs():
    murs_donnees = [
            {"angle": angle, "distance": mur['distance']} 
            for angle, mur in mur_memoire.items()
        ]
    return jsonify(murs_donnees)    
    

if __name__ == '__main__':
    calibration_thread = threading.Thread(target=auto_calibrate, daemon=True)
    calibration_thread.start()
    app.run(host='0.0.0.0', port=5000, debug=True)

