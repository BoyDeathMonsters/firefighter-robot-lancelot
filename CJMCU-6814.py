import spidev
import time

# Initialisation SPI
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1350000

# Tension d’alimentation et résistance de charge
Vcc = 5.0
RL = 10000  # 10kΩ

# === Calibration R0 pour chaque gaz (à ajuster avec de l’air propre) ===
R0_NH3 = 10000
R0_CO  = 10000
R0_NO2 = 10000

# === Paramètres courbe Rs/R0 ➜ ppm pour chaque gaz ===
#       ppm = A * (Rs/R0)^B   (valeurs approximées)
GAS_PARAMS = {
    "NH3": {"A": 50,  "B": -1.5, "R0": R0_NH3, "M": 17.03},   # masse molaire NH3
    "CO":  {"A": 100, "B": -1.2, "R0": R0_CO,  "M": 28.01},   # masse molaire CO
    "NO2": {"A": 0.5, "B": -1.1, "R0": R0_NO2, "M": 46.01}    # masse molaire NO2
}

def read_channel(channel):
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    data = ((adc[1] & 3) << 8) + adc[2]
    return (data * Vcc) / 1023

def rs_from_voltage(vout):
    if vout <= 0:
        return float('inf')
    return RL * ((Vcc - vout) / vout)

while True:
    print("\n" * 30)
    print("Lecture des gaz :")
    for gas, config in [("NH3",  {"channel": 0}),
                        ("CO",   {"channel": 1}),
                        ("NO2",  {"channel": 2})]:

        vout = read_channel(config["channel"])
        rs = rs_from_voltage(vout)

        params = GAS_PARAMS[gas]
        r0 = params["R0"]
        ratio = rs / r0
        ppm = params["A"] * (ratio ** params["B"])
        ug_m3 = ppm * (params["M"] * 1000 / 24.45)  # µg/m³

        print(f"{gas}:")
        print(f"  {ppm:.2f} ppm ≈ {ug_m3:.0f} µg/m³")
        print("-" * 30)

    time.sleep(2)
