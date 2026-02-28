from lora_driver.sx127x import SX127x
import time, os, json, subprocess, zlib, base64
from gaz_reader import read_gas_data

# Lancer le script gyroscope
gyro_proc = subprocess.Popen(["python3", "/home/victor/Capteurs/gyroscope.py"])

# Initialiser LoRa
lora = SX127x(reset_pin=22, dio0_pin=25)
print("Module LoRa initialisé.")

def compress_and_split(data_obj, prefix, max_chunk_size=95):
    try:
        data_str = json.dumps(data_obj, separators=(",", ":"))
        compressed = zlib.compress(data_str.encode())
        b64_data = base64.b64encode(compressed).decode()

        chunks = [b64_data[i:i+max_chunk_size] for i in range(0, len(b64_data), max_chunk_size)]
        total = len(chunks)
        packets = []

        for i, chunk in enumerate(chunks):
            part_header = f"[{prefix}]{i+1}/{total}:{chunk}"
            packets.append(part_header.encode())

        return packets

    except Exception as e:
        print(f"Erreur de compression {prefix}: {e}")
        return []

def read_json(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return {}

def read_last_line():
    try:
        with open("temp.txt", "r") as file:
            last_line = file.readlines()[-1].strip()
            temperature, humidity = map(float, last_line.split(','))
            return temperature, humidity
    except:
        return None, None

def simplify_murs(murs):
    return [{"a": m["angle"], "d": round(m["distance"], 1)} for m in murs]

last_mur_send = 0
last_mur_scan = 0

try:
    while True:
        now = time.time()

        # Relancer un scan murs toutes les 10 s
        if now - last_mur_scan > 10:
            subprocess.Popen(["python3", "/home/victor/Capteurs/servo_distance.py"])
            last_mur_scan = now

        # Lire les données
        gyro_data = read_json("/home/victor/Capteurs/gyro.json")
        murs_data_raw = read_json("/home/victor/Capteurs/murs.json")
        murs_data = simplify_murs(murs_data_raw)
        temperature, humidity = read_last_line()
        gas_data = read_gas_data()

        # Envoi G (gyroscope)
        for packet in compress_and_split(gyro_data, "G"):
            print(f"📤 Envoi Gyro : {len(packet)} octets")
            lora.send_payload(packet)
            time.sleep(0.3)

        # Envoi T (Température, humidité, gaz)
        data_T = {"t": temperature, "h": humidity, "gaz": gas_data}
        t_packet = compress_and_split(data_T, "T")
        if t_packet:
            print(f"📤 Envoi T : {len(t_packet[0])} octets")
            lora.send_payload(t_packet[0])

        # Envoi M (murs)
        if now - last_mur_send > 10:
            for packet in compress_and_split(murs_data, "M"):
                print(f"📤 Envoi Murs : {len(packet)} octets")
                lora.send_payload(packet)
                time.sleep(0.3)
            last_mur_send = now

        time.sleep(0.5)

except KeyboardInterrupt:
    print("Arrêt par l'utilisateur.")
    gyro_proc.terminate()
