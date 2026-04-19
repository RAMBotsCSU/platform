import unittest
import os
from unittest.mock import MagicMock, patch

from robot.face import Face


class TestFace(unittest.TestCase):
    def _make_face(self):
        face = Face.__new__(Face)
        mock_serial = MagicMock()
        mock_serial.readline.return_value = b"ok\n"
        face.ser = mock_serial
        return face, mock_serial

    def _assert_expression_command(self, expression):
        face, mock_serial = self._make_face()
        face.send_command(expression)
        mock_serial.write.assert_called_once_with(f"{expression}\n".encode())
        mock_serial.readline.assert_called_once()

    def test_send_face_expression_oval(self):
        self._assert_expression_command(Face.OVAL)

    def test_send_face_expression_x(self):
        self._assert_expression_command(Face.X)

    def test_send_face_expression_walk(self):
        self._assert_expression_command(Face.WALK)

    def test_send_face_expression_happy(self):
        self._assert_expression_command(Face.HAPPY)

    def test_send_face_expression_scroll(self):
        self._assert_expression_command(Face.SCROLL)

    def test_send_face_expression_off(self):
        self._assert_expression_command(Face.OFF)

    @patch("robot.face.time.sleep")
    def test_test_all_expressions_calls_each_expression(self, mock_sleep):
        face = Face.__new__(Face)
        face.send_command = MagicMock(return_value="ok")

        results = face.test_all_expressions(delay_s=0)

        self.assertEqual(
            [call.args[0] for call in face.send_command.call_args_list],
            Face.EXPRESSIONS,
        )
        self.assertEqual(results, {expression: "ok" for expression in Face.EXPRESSIONS})
        self.assertEqual(mock_sleep.call_count, len(Face.EXPRESSIONS))

    @unittest.skipUnless(
        os.getenv("RUN_FACE_HARDWARE_TEST") == "1",
        "Set RUN_FACE_HARDWARE_TEST=1 to run hardware communication smoke test",
    )
    def test_hardware_smoke_communicates_with_face_controller(self):
        face = None
        try:
            face = Face()
            delay_s = float(os.getenv("FACE_HARDWARE_DELAY_S", "2.0"))
            face.test_all_expressions(delay_s=delay_s)
        finally:
            if face is not None:
                face.close()


if __name__ == "__main__":
    unittest.main()