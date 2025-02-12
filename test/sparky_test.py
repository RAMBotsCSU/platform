import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import asyncio
from robot.sparky import Sparky

class TestSparky(unittest.TestCase):

    @patch('robot.sparky.ThreadPoolExecutor')
    @patch('robot.sparky.Motion')
    @patch('robot.sparky.Controller')
    @patch('robot.sparky.MainWindow')
    @patch('robot.sparky.importlib.util.find_spec')
    @patch('robot.sparky.importlib.util.module_from_spec')
    def test_set_enabled_on(self, mock_module_from_spec, mock_find_spec, mock_MainWindow, mock_Controller, mock_Motion, mock_ThreadPoolExecutor):
        # Setup Mocks
        mock_find_spec.return_value = MagicMock()
        mock_module = MagicMock()
        mock_module_from_spec.return_value = mock_module
        mock_mode_setup = MagicMock()
        mock_module.setup = mock_mode_setup
        mock_mode_setup.return_value = MagicMock()
        
        # Mock constructor of other classes
        mock_Motion.return_value = MagicMock()
        mock_Controller.return_value = MagicMock()
        mock_MainWindow.return_value = MagicMock()
        
        sparky = Sparky()
        
        # Enable sparky
        loop = asyncio.get_event_loop()
        asyncio.set_event_loop(loop)
        sparky.set_enabled(True)
        
        # Check that the mode is set and run method is called
        mock_mode_setup.assert_called_once_with(sparky)
        sparky.mode.run.assert_called_once()

    @patch('robot.sparky.ThreadPoolExecutor')
    @patch('robot.sparky.Motion')
    @patch('robot.sparky.Controller')
    @patch('robot.sparky.MainWindow')
    def test_set_enabled_off(self, mock_MainWindow, mock_Controller, mock_Motion, mock_ThreadPoolExecutor):
        # Mock constructor of other classes
        mock_Motion.return_value = MagicMock()
        mock_Controller.return_value = MagicMock()
        mock_MainWindow.return_value = MagicMock()
        
        sparky = Sparky()

        # Mock method calls
        sparky.motion.stop = MagicMock()
        sparky.mode.stop = MagicMock()
        
        # Disable sparky
        sparky.set_enabled(False)
        
        # Check that stop was called for motion and mode
        sparky.motion.stop.assert_called_once()
        sparky.mode.stop.assert_called_once()

    @patch('robot.sparky.Controller')
    @patch('robot.sparky.Motion')
    @patch('robot.sparky.MainWindow')
    def test_run_method(self, mock_MainWindow, mock_Motion, mock_Controller):
        # Mock constructor of other classes
        mock_Motion.return_value = MagicMock()
        mock_Controller.return_value = MagicMock()
        mock_MainWindow.return_value = MagicMock()
        
        sparky = Sparky()
        
        # Create asyncio tasks
        sparky.loop = asyncio.new_event_loop()
        sparky.controller = MagicMock()
        sparky.motion = MagicMock()
        
        # Start the run method
        loop = asyncio.get_event_loop()
        asyncio.set_event_loop(loop)
        sparky.run()

        # Check that the run methods of motion and controller are called
        sparky.motion.run.assert_called_once()
        sparky.controller.events.assert_called_once()
        sparky.controller.polling.assert_called_once()

    @patch('robot.sparky.Controller')
    @patch('robot.sparky.Motion')
    def test_stop_method(self, mock_Motion, mock_Controller):
        # Mock constructor of other classes
        mock_Motion.return_value = MagicMock()
        mock_Controller.return_value = MagicMock()
        
        sparky = Sparky()
        
        # Setup mock methods for stop behavior
        sparky.motion.stop = MagicMock()
        sparky.controller.led.set_color = MagicMock()
        
        # Call stop method
        sparky.stop()
        
        # Check stop calls
        sparky.motion.stop.assert_called_once()
        sparky.controller.led.set_color.assert_called_once_with((0, 0, 50))

    @patch('robot.sparky.Controller')
    @patch('robot.sparky.Motion')
    def test_heartbeat(self, mock_Motion, mock_Controller):
        # Mock constructor of other classes
        mock_Motion.return_value = MagicMock()
        mock_Controller.return_value = MagicMock()
        
        sparky = Sparky()
        
        # Mock the controller's led object
        sparky.controller.led = MagicMock()
        
        # Run heartbeat
        heartbeat_task = asyncio.create_task(sparky.heartbeat())
        asyncio.run(heartbeat_task)  # Run it asynchronously
        
        # Test that the led color was set (not precise timing)
        sparky.controller.led.set_color.assert_called()
        heartbeat_task.cancel()  # Cancel the heartbeat task after test

if __name__ == '__main__':
    unittest.main()
