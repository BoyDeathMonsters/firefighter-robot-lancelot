import spidev
import time

# === Initialisation SPI ===
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1350000

# === Constantes ===
Vcc = 5.0
RL = 10000

GAS_PARAMS = {
    "NH3": {"A": 50,  "B": -1.5, "R0": 10000, "M": 17.03, "channel": 0},
    "CO":  {"A": 100, "B": -1.2, "R0": 10000, "M": 28.01, "channel": 1},
    "NO2": {"A": 0.5, "B": -1.1, "R0": 10000, "M": 46.01, "channel": 2}
}

def read_channel(channel):
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    data = ((adc[1] & 3) << 8) + adc[2]
    return (data * Vcc) / 1023

def rs_from_voltage(vout):
    if vout <= 0:
        return float('inf')
    return RL * ((Vcc - vout) / vout)

def read_gas_data():
    message_parts = []
    for gas, params in GAS_PARAMS.items():
        vout = read_channel(params["channel"])
        rs = rs_from_voltage(vout)
        ratio = rs / params["R0"]
        ppm = params["A"] * (ratio ** params["B"])
        message_parts.append(f"{gas}={ppm:.1f}ppm")
    return ", ".join(message_parts)

# === Mode autonome si exécuté directement ===
if __name__ == "__main__":
    try:
        while True:
            print(read_gas_data())
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nArrêt par l'utilisateur.")
