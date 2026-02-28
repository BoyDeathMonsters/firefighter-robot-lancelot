from lora_driver.sx127x import SX127x
import time

lora = SX127x(reset_pin=22, dio0_pin=25)

while True:
    msg = "Hello LoRa"
    print("Envoi :", msg)
    lora.send_payload([ord(c) for c in msg])
    time.sleep(1)