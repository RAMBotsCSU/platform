import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import asyncio

from robot.mode import Mode
from robot.sparky import Sparky

class TestMode(unittest.TestCase):
    @patch('robot.mode.asyncio.new_event_loop')
    @patch('robot.mode.asyncio.set_event_loop')
    @patch('robot.mode.asyncio.all_tasks')
    def test_run(self, mock_all_tasks, mock_set_event_loop, mock_new_event_loop):
        
        # Creating mock Sparky
        mock_robot = MagicMock() 
        mock_mode = Mode(mock_robot)
        mock_loop = MagicMock()
        
        # Mocking event loop creation and set_event_loop to use our mock loop
        mock_new_event_loop.return_value = mock_loop
        mock_set_event_loop.return_value = None
        
        # Run
        mock_mode.run()

        # Assert
        mock_new_event_loop.assert_called_once()  # Ensure a new event loop is created
        mock_set_event_loop.assert_called_once_with(mock_loop)  # Ensure set_event_loop was called with the mock loop
        mock_mode.loop.run_forever.assert_called_once()  # Ensure the loop was run

    @patch('robot.mode.asyncio.all_tasks')
    @patch('robot.mode.asyncio.CancelledError')
    @patch('robot.mode.Mode.start', new_callable=AsyncMock)
    def test_stop(self, mock_start, mock_CancelledError, mock_all_tasks):
        # Arrange
        mock_robot = MagicMock()  # Mock Sparky
        mock_mode = Mode(mock_robot)
        mock_task = MagicMock()  # Create a mock task
        mock_mode.loop = MagicMock()  # Mock the loop

        # Mock the task to be returned by all_tasks
        mock_all_tasks.return_value = [mock_task]

        # Act
        mock_mode.stop()

        # Assert
        mock_all_tasks.assert_called_once_with(mock_mode.loop)  # Ensure all tasks are retrieved from the loop
        mock_task.cancel.assert_called_once()  # Ensure the cancel method was called on the task
        mock_mode.loop.stop.assert_called_once()  # Ensure the event loop was stopped

    @patch('robot.mode.Mode.start', new_callable=AsyncMock)
    def test_start(self, mock_start):
        # Arrange
        mock_robot = MagicMock()  # Mock Sparky 
        mock_mode = Mode(mock_robot)

        # Act
        asyncio.run(mock_mode.start())

        # Assert
        mock_start.assert_awaited_once()  # Ensure the start method was awaited

    @patch('robot.mode.asyncio.CancelledError')
    def test_run_with_cancel(self, mock_CancelledError):
        # Arrange
        mock_robot = MagicMock()  # Mock Sparky robot
        mock_mode = Mode(mock_robot)
        mock_mode.start = AsyncMock()
        
        # Simulate the cancellation of the task
        mock_mode.start.side_effect = asyncio.CancelledError

        # Act & Assert
        with self.assertRaises(asyncio.CancelledError):
            asyncio.run(mock_mode._run())  # Test the _run() method which should handle cancellation
            mock_mode.start.assert_awaited_once()  # Ensure start was called
            mock_mode.start.side_effect = mock_CancelledError  # Handle cancellation properly
        

if __name__ == '__main__':
    unittest.main()
