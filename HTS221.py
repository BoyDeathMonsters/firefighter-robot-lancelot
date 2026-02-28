import smbus
import time

ADDR = 0x5F
bus = smbus.SMBus(1)

def twos_complement(val, bits):
    if val & (1 << (bits - 1)):
        val -= (1 << bits)
    return val

def read_calibration():
    # Température
    T0_degC_x8 = bus.read_byte_data(ADDR, 0x32)
    T1_degC_x8 = bus.read_byte_data(ADDR, 0x33)
    T0_T1_msb = bus.read_byte_data(ADDR, 0x35)

    T0_degC = ((T0_T1_msb & 0x03) << 8) | T0_degC_x8
    T1_degC = ((T0_T1_msb & 0x0C) << 6) | T1_degC_x8

    T0_degC /= 8.0
    T1_degC /= 8.0

    T0_OUT = twos_complement(
        bus.read_byte_data(ADDR, 0x3C) | (bus.read_byte_data(ADDR, 0x3D) << 8), 16)
    T1_OUT = twos_complement(
        bus.read_byte_data(ADDR, 0x3E) | (bus.read_byte_data(ADDR, 0x3F) << 8), 16)

    # Humidité
    H0_rH = bus.read_byte_data(ADDR, 0x30) / 2.0
    H1_rH = bus.read_byte_data(ADDR, 0x31) / 2.0

    H0_T0_OUT = twos_complement(
        bus.read_byte_data(ADDR, 0x36) | (bus.read_byte_data(ADDR, 0x37) << 8), 16)
    H1_T0_OUT = twos_complement(
        bus.read_byte_data(ADDR, 0x3A) | (bus.read_byte_data(ADDR, 0x3B) << 8), 16)

    return {
        "T0_degC": T0_degC, "T1_degC": T1_degC,
        "T0_OUT": T0_OUT, "T1_OUT": T1_OUT,
        "H0_rH": H0_rH, "H1_rH": H1_rH,
        "H0_T0_OUT": H0_T0_OUT, "H1_T0_OUT": H1_T0_OUT
    }

def init_sensor():
    bus.write_byte_data(ADDR, 0x20, 0x85)  # CTRL_REG1: PD=1, BDU=1, ODR=1Hz
    time.sleep(0.1)

def read_temperature(calib):
    T_OUT = twos_complement(
        bus.read_byte_data(ADDR, 0x2A) | (bus.read_byte_data(ADDR, 0x2B) << 8), 16)

    T = calib["T0_degC"] + (T_OUT - calib["T0_OUT"]) * \
        (calib["T1_degC"] - calib["T0_degC"]) / (calib["T1_OUT"] - calib["T0_OUT"])
    return round(T, 2)

def read_humidity(calib):
    H_OUT = twos_complement(
        bus.read_byte_data(ADDR, 0x28) | (bus.read_byte_data(ADDR, 0x29) << 8), 16)

    H = calib["H0_rH"] + (H_OUT - calib["H0_T0_OUT"]) * \
        (calib["H1_rH"] - calib["H0_rH"]) / (calib["H1_T0_OUT"] - calib["H0_T0_OUT"])
    return round(min(max(H, 0), 100), 2)  # Clamp entre 0% et 100%

# Main
init_sensor()
calib = read_calibration()

while True:
    temp = read_temperature(calib)
    hum = read_humidity(calib)
    print(f"Température: {temp} °C, Humidité: {hum} %")
    time.sleep(1)
