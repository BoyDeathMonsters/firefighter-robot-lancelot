from mpu6050 import mpu6050
import time
import math

# Initialisation du capteur
sensor = mpu6050(0x68)  # Adresse I2C par défaut

import json

while True:
    accel = sensor.get_accel_data()
    gyro = sensor.get_gyro_data()

    accel_x = accel['x']
    accel_y = accel['y']
    accel_z = accel['z']

    pitch = math.atan2(accel_y, math.sqrt(accel_x**2 + accel_z**2))
    roll = math.atan2(-accel_x, math.sqrt(accel_y**2 + accel_z**2))

    pitch_deg = math.degrees(pitch)
    roll_deg = math.degrees(roll)

    data = {
        'accel': accel,
        'gyro': gyro,
        'pitch': round(pitch_deg, 2),
        'roll': round(roll_deg, 2)
    }

    with open("/home/victor/Capteurs/gyro.json", "w") as f:
        json.dump(data, f)

    time.sleep(0.1)

