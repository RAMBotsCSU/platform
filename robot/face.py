import serial, time, asyncio
from serial.tools import list_ports

class Face:
    OVAL = 'OVAL'
    X = 'X'
    WALK = 'WALK'
    HAPPY = 'HAPPY'
    SCROLL = 'SCROLL'
    OFF = 'OFF'

    BAUD_RATE   = 115200

    def __init__(self):
        self.ser = serial.Serial(self._find_serial_dev(), self.BAUD_RATE, timeout=1)
        time.sleep(2)  # wait for ESP32 to reboot after serial connect

    def _find_serial_dev(self):
        for port in list_ports.comports():
            if port.manufacturer == 'Espressif':
                return port.device

        raise Exception("Could not connect to face controller")


    def send_command(self, cmd):
        self.ser.write((cmd + '\n').encode())
        response = self.ser.readline().decode().strip()
        print(f"Sent: {cmd} | Response: {response}")

    def close(self):
        self.ser.close()