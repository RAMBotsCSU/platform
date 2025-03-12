import unittest
from unittest.mock import patch, MagicMock
import asyncio
from robot.motion import Motion
from robot.motion import Sparky 

class TestMotion(unittest.TestCase):

    @patch("motion.aioserial.AioSerial")
    @patch("motion.list_ports.comports")
    def setUp(self, mock_comports, mock_aioserial):
        
        # Sparky mock 
        self.mock_robot = MagicMock(spec=Sparky)
        
        # Mock the serial port list to return a mocked port
        self.mock_serial_port = MagicMock()
        self.mock_serial_port.manufacturer = "Teensyduino"
        mock_comports.return_value = [self.mock_serial_port]
        
        # Mock the AioSerial instance
        self.mock_serial = MagicMock()
        mock_aioserial.return_value = self.mock_serial
        
        # Initialize the Motion object
        self.motion = Motion(self.mock_robot)

    @patch("motion.aioserial.AioSerial.write_async", new_callable=MagicMock)
    @patch("motion.aioserial.AioSerial.read_until_async", new_callable=MagicMock)
    def test_run(self, mock_read, mock_write):
        # Simulate the serial read response
        mock_read.return_value = b"some_response"

        # Call the run method which should interact with serial
        loop = asyncio.get_event_loop()
        task = loop.create_task(self.motion.run())

        # Allow the run method to execute for a lttle
        loop.run_until_complete(asyncio.sleep(0.1))

        # Assert that the serial write and read functions were called
        mock_write.assert_called_once()
        mock_read.assert_called_once()

        task.cancel()  # Make sure we cancel the task after the test
        loop.run_until_complete(task)  # Await the cancellation

    def test_move(self):
        # Test the move method, ensuring internal state is updated
        self.motion.move(1, 2, 3, 4, 5, 6)
        
        # Check if internal state has changed as expected
        self.assertEqual(self.motion.rfb, 1)
        self.assertEqual(self.motion.rlr, 2)
        self.assertEqual(self.motion.lfb, 3)
        self.assertEqual(self.motion.llr, 4)
        self.assertEqual(self.motion.rt, 5)
        self.assertEqual(self.motion.lt, 6)
        self.assertTrue(self.motion.toggle_top)

    def test_stop(self):
        # Test the stop method
        self.motion.stop()

        # Check if internal state is reset to stop values
        self.assertEqual(self.motion.rfb, 0)
        self.assertEqual(self.motion.rlr, 0)
        self.assertEqual(self.motion.lfb, 0)
        self.assertEqual(self.motion.llr, 0)
        self.assertEqual(self.motion.rt, 0)
        self.assertEqual(self.motion.lt, 0)
        self.assertFalse(self.motion.toggle_top)

    @patch("motion.aioserial.AioSerial.read_until_async", side_effect=aioserial.SerialException)
    @patch("motion.Motion.reconnect", new_callable=MagicMock)
    def test_reconnect_on_serial_exception(self, mock_reconnect, mock_read):
        # Simulate a serial exception during the read
        mock_read.side_effect = aioserial.SerialException
        
        # Run reconnect logic (this will continuously try to reconnect)
        loop = asyncio.get_event_loop()
        task = loop.create_task(self.motion.run())
        
        # Allow a short wait to check that the reconnect logic works
        loop.run_until_complete(asyncio.sleep(0.1))
        
        # Assert that the reconnect method is called when serial exception occurs
        mock_reconnect.assert_called_once()

        task.cancel()  # Cancel the task after the test
        loop.run_until_complete(task)

if __name__ == "__main__":
    unittest.main()
