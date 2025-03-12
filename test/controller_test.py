import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path
from evdev import InputEvent, ecodes
from robot.controller import Controller, ControllerLED  # Assuming your file is named controller.py


class TestControllerLED(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.base_path = MagicMock(spec=Path)
        self.base_path.exists.return_value = True
        self.base_path.glob.side_effect = lambda pattern: [self.base_path / "dummy"]

        self.led = ControllerLED(self.base_path)

    @patch("aiofiles.open", new_callable=AsyncMock)
    async def test_set_color(self, mock_open):
        await self.led.set_color((255, 128, 64))
        
        self.assertEqual(mock_open.call_count, 3)
        mock_open.assert_any_call(self.led.red, mode="w")
        mock_open.assert_any_call(self.led.green, mode="w")
        mock_open.assert_any_call(self.led.blue, mode="w")


class TestController(unittest.TestCase):
    @patch("controller.list_devices", return_value=["/dev/input/event0"])
    @patch("controller.InputDevice")
    def setUp(self, mock_input_device, mock_list_devices):
        self.mock_device = MagicMock()
        self.mock_device.name = "Sony PlayStation Controller"
        self.mock_device.path = "/dev/input/event0"
        self.mock_device.capabilities.return_value = {ecodes.EV_ABS: [(ecodes.ABS_X, MagicMock(value=100))]}

        mock_input_device.return_value = self.mock_device
        self.robot_mock = MagicMock()
        self.controller = Controller(self.robot_mock)

    def test_find_controller_dev(self):
        self.assertEqual(self.controller.dev, self.mock_device)

    def test_update_event_key(self):
        event = InputEvent(0, 0, ecodes.EV_KEY, ecodes.BTN_SOUTH, 1)
        self.controller.update_event(event)
        self.assertEqual(self.controller.cross, 1)

    def test_update_event_abs(self):
        event = InputEvent(0, 0, ecodes.EV_ABS, ecodes.ABS_X, 150)
        self.controller.update_event(event)
        self.assertEqual(self.controller.left_stick_x, 150)


if __name__ == "__main__":
    unittest.main()
