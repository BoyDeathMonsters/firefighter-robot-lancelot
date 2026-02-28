# lora_receiver.py
import time
from lora_driver.sx127x import SX127x

def main():
    print("[LoRa Receiver] Initialisation...")
    lora = SX127x()  # Assure-toi que la fréquence est identique à celle du sender

    print("[LoRa Receiver] Réception LoRa en cours...")
    while True:
        try:
            data = lora.receive_payload()
            if data:
                try:
                    message = bytes(data).decode('utf-8')
                    print("[LoRa Receiver] Reçu :", message)
                except UnicodeDecodeError:
                    print("[LoRa Receiver] Données reçues mais illisibles :", data)
            time.sleep(0.1)  # Petite pause pour ne pas saturer le CPU
        except KeyboardInterrupt:
            print("\nArrêt manuel. Fermeture.")
            break

    lora.close()

if __name__ == "__main__":
    main()
