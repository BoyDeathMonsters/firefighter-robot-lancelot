from flask import Flask
import subprocess

app = Flask(__name__)

@app.route('/start-scan', methods=['GET'])
def start_scan():
    try:
        subprocess.Popen(["python3", "/home/cantos/robot_orientation/map3d/servo_distance.py"])
        return "Scan lancé !", 200
    except Exception as e:
        return f"Erreur : {e}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)

