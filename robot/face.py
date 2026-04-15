import serial
import time

SERIAL_PORT = '/dev/ttyUSB0'  # change to your port (see note below)
BAUD_RATE   = 115200

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
time.sleep(2)  # wait for ESP32 to reboot after serial connect

def send_command(cmd):
    ser.write((cmd + '\n').encode())
    response = ser.readline().decode().strip()
    print(f"Sent: {cmd} | Response: {response}")

send_command('OVAL')
time.sleep(5)
send_command('X')
time.sleep(5)
send_command('WALK')
time.sleep(5)
send_command('HAPPY')
time.sleep(5)
send_command('SCROLL')
time.sleep(5)
send_command('OFF')

ser.close()