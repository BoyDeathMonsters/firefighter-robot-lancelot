from gpiozero import AngularServo, DistanceSensor
from time import sleep
import json

# Calibrage SG90 : ~0.5ms (-90°) à ~2.5ms (+90°)
servo = AngularServo(
    23,  # GPIO
    min_angle=-90,
    max_angle=90,
    min_pulse_width=0.6/1000,  # 0.5 ms
    max_pulse_width=2.4/1000   # 2.5 ms
)

capteur = DistanceSensor(echo=26, trigger=27, max_distance=4)

def get_distance():
    return capteur.distance * 100  # en cm

def scan():
    murs = []
    for angle in range(-90, 91, 10):  # de -90° à +90° inclus
        servo.angle = angle
        sleep(0.4)  # laisse le temps au servo de bouger
        distance = get_distance()
        murs.append({'angle': angle, 'distance': distance})
    return murs

if __name__ == "__main__":
    murs_data = scan()
    with open("/home/victor/Capteurs/murs.json", "w") as f:
        json.dump(murs_data, f)


