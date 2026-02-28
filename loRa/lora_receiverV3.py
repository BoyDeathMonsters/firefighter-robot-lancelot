from lora_driver.sx127x import SX127x
import zlib, json, base64, time, re

lora = SX127x(reset_pin=22, dio0_pin=25)
print(" Récepteur LoRa prêt.")

received_parts = {}  # Exemple: {"T": {"total": 3, "chunks": {1: "abc", 2: "def", 3: "ghi"}, "last_time": ...}}
TIMEOUT = 0.5

def save_to_file(filename, data):
    try:
        lines = []

        # Lire les lignes existantes s'il y a un fichier
        try:
            with open(filename, 'r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            pass  # Pas grave si le fichier n'existe pas encore

        # Ajouter la nouvelle ligne à la fin
        new_line = json.dumps(data) + "\n"
        lines.append(new_line)

        # Garder seulement les 50 dernières
        if len(lines) > 50:
            lines = lines[-50:]

        # Réécrire le fichier avec les lignes filtrées
        with open(filename, 'w') as f:
            f.writelines(lines)

    except Exception as e:
        print(f"Erreur écriture fichier : {e}")


def decode_and_save(prefix, full_b64_data):
    try:
        compressed = base64.b64decode(full_b64_data.encode())
        decompressed = zlib.decompress(compressed)
        data = json.loads(decompressed.decode())

        if prefix == "G":
            print("[Gyroscope]")
            print(json.dumps(data, indent=2))
            save_to_file("gyro.json", data)

        elif prefix == "M":
            print(" [Murs]")
            murs = [{"angle": m["a"], "distance": m["d"]} for m in data]
            for mur in murs:
                print(f" ↪ Angle: {mur['angle']}°, Distance: {mur['distance']} cm")
            save_to_file("murs.json", murs)

        elif prefix == "T":
            print(f" [Température/Humidité/Gaz] → Temp: {data['t']}°C, Humidité: {data['h']}%, Gaz: {data['gaz']}")
            save_to_file("temperature.json", data)

        else:
            print(f" Préfixe inconnu : {prefix}")

    except Exception as e:
        print(f" Erreur de décodage : {e}")

def process_payload(payload):
    try:
        payload_str = payload.decode()
        match = re.match(r"\[(\w)\](\d+)/(\d+):(.+)", payload_str)
        if not match:
            print(f" Format incorrect : {payload_str}")
            return

        prefix, index, total, chunk = match.groups()
        index, total = int(index), int(total)

        if prefix not in received_parts:
            received_parts[prefix] = {"chunks": {}, "total": total, "last_time": time.time()}

        received_parts[prefix]["chunks"][index] = chunk
        received_parts[prefix]["last_time"] = time.time()

        if len(received_parts[prefix]["chunks"]) == total:
            print(f" Reconstruction complète pour [{prefix}]")
            full_b64_data = ''.join(received_parts[prefix]["chunks"][i] for i in range(1, total + 1))
            print(f"Donnees ({prefix}) : {full_b64_data}")
            decode_and_save(prefix, full_b64_data)
            del received_parts[prefix]

    except Exception as e:
        print(f" Erreur traitement payload : {e}")

def check_for_timeouts():
    now = time.time()
    expired = []

    for prefix, info in received_parts.items():
        if now - info["last_time"] > TIMEOUT:
            print(f" Timeout - suppression de {prefix}")
            expired.append(prefix)

    for prefix in expired:
        del received_parts[prefix]

try:
    last_check = time.time()
    while True:
        payload = lora.receive_payload()
        if payload:
            print(f" Reçu : {payload}")
            process_payload(payload)

        if time.time() - last_check > 0.2:
            check_for_timeouts()
            last_check = time.time()

except KeyboardInterrupt:
    print(" Arrêt du programme.")

