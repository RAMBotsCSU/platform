import unittest
from unittest.mock import MagicMock, patch

from robot.face import Face


class TestFace(unittest.TestCase):
    @patch("robot.face.time.sleep")
    def test_send_command_writes_line_and_returns_response(self, mock_sleep):
        mock_serial = MagicMock()
        mock_serial.readline.return_value = b"ok\n"

        face = Face(
            port="/dev/ttyUSB0",
            serial_factory=lambda *args, **kwargs: mock_serial,
            warmup_seconds=0,
        )

        response = face.send_command("OVAL")

        mock_serial.write.assert_called_once_with(b"OVAL\n")
        self.assertEqual(response, "ok")

    @patch("robot.face.list_ports.comports")
    def test_find_serial_dev_prefers_espressif(self, mock_comports):
        port = MagicMock()
        port.manufacturer = "Espressif"
        port.device = "COM7"
        mock_comports.return_value = [port]

        face = Face.__new__(Face)

        self.assertEqual(face._find_serial_dev(), "COM7")


if __name__ == "__main__":
    unittest.main()