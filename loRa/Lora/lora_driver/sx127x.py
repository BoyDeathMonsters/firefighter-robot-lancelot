from gpiozero import DigitalOutputDevice, DigitalInputDevice
import time
import spidev

class SX127x:
    def __init__(self, spi_bus=0, spi_device=0, reset_pin=22, dio0_pin=25):
        self.reset = DigitalOutputDevice(reset_pin)
        self.dio0 = DigitalInputDevice(dio0_pin)

        self.spi = spidev.SpiDev()
        self.spi.open(spi_bus, spi_device)
        self.spi.max_speed_hz = 2000000
        self.spi.mode = 0

        self.reset_device()
        self.configure_lora()

    def reset_device(self):
        print("[SX127x] Resetting device...")
        self.reset.on()      # HIGH
        time.sleep(0.1)
        self.reset.off()     # LOW pulse
        time.sleep(0.1)
        self.reset.on()      # HIGH de nouveau
        time.sleep(0.1)

    def write_register(self, addr, value):
        self.spi.xfer2([addr | 0x80, value])

    def read_register(self, addr):
        response = self.spi.xfer2([addr & 0x7F, 0x00])
        return response[1]

    def configure_lora(self):
        print("[SX127x] Configuring LoRa...")
        self.write_register(0x01, 0x80)  # Sleep mode with LoRa
        time.sleep(0.1)
        self.write_register(0x1D, 0x72)  # BW = 125 kHz, CR = 4/5
        self.write_register(0x1E, 0x74)  # SF = 7, CRC on
        self.write_register(0x26, 0x04)  # Low datarate optimize off
        self.write_register(0x09, 0xFF)  # Max TX Power
        self.write_register(0x0E, 0x00)  # FIFO TX base address
        self.write_register(0x0F, 0x00)  # FIFO RX base address
        self.set_frequency(433)         # Set frequency to 868 MHz
        print("[SX127x] Configuration complete.")

    def set_frequency(self, freq_mhz):
        frf = int((freq_mhz * 1000000.0) / 61.03515625)
        self.write_register(0x06, (frf >> 16) & 0xFF)
        self.write_register(0x07, (frf >> 8) & 0xFF)
        self.write_register(0x08, frf & 0xFF)
        print(f"[SX127x] Frequency set to {freq_mhz} MHz")

    def send_payload(self, data):
        if isinstance(data, str):
            data = [ord(c) for c in data]
        print("[SX127x] Sending:", data)
        self.write_register(0x0D, 0x00)  # FIFO addr ptr
        for byte in data:
            self.write_register(0x00, byte)

        self.write_register(0x22, len(data))  # payload length
        self.write_register(0x01, 0x83)       # mode: TX

        while not self.dio0.value:
            time.sleep(0.01)

        self.write_register(0x12, 0x08)
        self.write_register(0x01, 0x81)# Clear TxDone IRQ
        print("[SX127x] Sent!")

    def receive_payload(self):
        self.write_register(0x01, 0x85)  # mode: RXCONTINUOUS
        print("[SX127x] Listening...")
        self.write_register(0x12,0xFF)
        while not self.dio0.value:
            time.sleep(0.01)

        irq_flags = self.read_register(0x12)
        if irq_flags & 0x40:  # RxDone
            self.write_register(0x12, 0xFF)  # clear all IRQ flags
            current_addr = self.read_register(0x10)
            received_count = self.read_register(0x13)
            self.write_register(0x0D, current_addr)

            payload = []
            for _ in range(received_count):
                payload.append(self.read_register(0x00))
            print("[SX127x] Received:", payload)
            return bytes(payload)

        return ''

    def close(self):
        self.spi.close()

