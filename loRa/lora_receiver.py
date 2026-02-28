from lora_driver.sx127x import SX127x

lora = SX127x(cs_pin=8, reset_pin=22, dio0_pin=25)

print("Réception LoRa en cours...")
while True:
    data = lora.receive_payload()
    if data:
        try:
            print("Reçu :", bytes(data).decode())
        except:
            print("Reçu (brut) :", data)

