import serial, time, asyncio
from serial.tools import list_ports

class Face:
    OVAL = 'OVAL'
    X = 'X'
    WALK = 'WALK'
    HAPPY = 'HAPPY'
    SCROLL = 'SCROLL'
    OFF = 'OFF'
    ser = serial.Serial()
    EXPRESSIONS = [OVAL, X, WALK, HAPPY, SCROLL, OFF]

    BAUD_RATE   = 115200

    def __init__(self):
        self.ser = serial.Serial(self._find_serial_dev(), self.BAUD_RATE, timeout=1)
        time.sleep(2)  # wait for ESP32 to reboot after serial connect

    def _find_serial_dev(self):
        for port in list_ports.comports():
            if port.manufacturer == 'Espressif Systems':
                return port.device

        raise Exception("Could not connect to face controller")


    def send_command(self, cmd):
        self.ser.write((cmd + '\n').encode())
        response = self.ser.readline().decode().strip()
        print(f"Sent: {cmd} | Response: {response}")
        return response

    def test_all_expressions(self, delay_s=1.0, expected_response=None):
        """Send each supported expression command to the face controller.

        Args:
            delay_s: Time to wait between commands so each expression is visible.
            expected_response: Optional exact response required from device.

        Returns:
            Dict of expression -> response string.

        Raises:
            ValueError: If expected_response is set and any command response differs.
        """
        results = {}
        for expression in self.EXPRESSIONS:
            response = self.send_command(expression)
            results[expression] = response

            if expected_response is not None and response != expected_response:
                raise ValueError(
                    f"Expression {expression} returned '{response}' (expected '{expected_response}')"
                )

            time.sleep(delay_s)

        return results

    def close(self):
        self.ser.close()