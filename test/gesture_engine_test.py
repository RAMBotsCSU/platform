import importlib.util
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np


MODULE_PATH = Path(__file__).resolve().parents[1] / "robot" / "gesture_engine.py"


def load_gesture_module():
    """Load gesture_engine with stubbed external dependencies."""
    fake_cv2 = types.ModuleType("cv2")
    fake_cv2.COLOR_BGR2RGB = 1
    fake_cv2.resize = lambda frame, size: np.zeros((size[1], size[0], 3), dtype=np.uint8)
    fake_cv2.cvtColor = lambda frame, code: frame
    fake_cv2.VideoCapture = lambda index: None

    fake_edgetpu = types.ModuleType("edgetpu")
    fake_common = types.ModuleType("common")
    fake_classify = types.ModuleType("classify")

    fake_interpreter = MagicMock()
    fake_interpreter.get_input_details.return_value = [
        {"quantization": (1.0, 0), "dtype": np.uint8, "index": 0}
    ]
    fake_edgetpu.make_interpreter = MagicMock(return_value=fake_interpreter)
    fake_common.input_size = MagicMock(return_value=(4, 4))
    fake_classify.get_classes = MagicMock(return_value=[])

    fake_utils = types.ModuleType("utils")
    fake_utils.edgetpu = fake_edgetpu
    fake_adapters = types.ModuleType("adapters")
    fake_adapters.common = fake_common
    fake_adapters.classify = fake_classify
    fake_pycoral = types.ModuleType("pycoral")
    fake_pycoral.utils = fake_utils
    fake_pycoral.adapters = fake_adapters

    module_name = "gesture_engine_under_test"
    if module_name in sys.modules:
        del sys.modules[module_name]

    with patch.dict(
        sys.modules,
        {
            "cv2": fake_cv2,
            "pycoral": fake_pycoral,
            "pycoral.utils": fake_utils,
            "pycoral.utils.edgetpu": fake_edgetpu,
            "pycoral.adapters": fake_adapters,
            "pycoral.adapters.common": fake_common,
            "pycoral.adapters.classify": fake_classify,
        },
    ):
        spec = importlib.util.spec_from_file_location(module_name, MODULE_PATH)
        module = importlib.util.module_from_spec(spec)
        assert spec is not None and spec.loader is not None
        spec.loader.exec_module(module)

    return module


class TestGestureEngine(unittest.TestCase):
    def setUp(self):
        self.module = load_gesture_module()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.labels_path = Path(self.temp_dir.name) / "labels.txt"
        self.labels_path.write_text(
            "0 stop\n1 fist\n2 palm\n3 peace_inverted\n4 one\n",
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def _make_engine(self, history_len=3):
        cap = MagicMock()
        cap.isOpened.return_value = True
        cap.read.return_value = (True, np.zeros((8, 8, 3), dtype=np.uint8))

        with patch.object(self.module.cv2, "VideoCapture", return_value=cap):
            engine = self.module.GestureEngine(
                model_path="dummy_model.tflite",
                labels_path=str(self.labels_path),
                history_len=history_len,
                score_threshold=0.8,
            )

        return engine, cap

    def test_init_raises_when_camera_fails(self):
        cap = MagicMock()
        cap.isOpened.return_value = False

        with patch.object(self.module.cv2, "VideoCapture", return_value=cap):
            with self.assertRaises(RuntimeError):
                self.module.GestureEngine("dummy", str(self.labels_path))

    def test_get_gesture_requires_full_history_and_change(self):
        engine, _ = self._make_engine(history_len=3)
        class_result = [types.SimpleNamespace(id=3, score=0.95)]

        with patch.object(self.module.classify, "get_classes", side_effect=[class_result] * 4):
            self.assertIsNone(engine.get_gesture())
            self.assertIsNone(engine.get_gesture())
            self.assertEqual(engine.get_gesture(), self.module.Gesture.WALK_FORWARD)
            self.assertIsNone(engine.get_gesture())

    def test_get_gesture_uses_majority_vote(self):
        engine, _ = self._make_engine(history_len=3)
        predictions = [
            [types.SimpleNamespace(id=1, score=0.91)],
            [types.SimpleNamespace(id=2, score=0.92)],
            [types.SimpleNamespace(id=2, score=0.94)],
        ]

        with patch.object(self.module.classify, "get_classes", side_effect=predictions):
            self.assertIsNone(engine.get_gesture())
            self.assertIsNone(engine.get_gesture())
            self.assertEqual(engine.get_gesture(), self.module.Gesture.SIT)

    def test_get_gesture_returns_none_for_low_confidence(self):
        engine, _ = self._make_engine(history_len=3)

        with patch.object(self.module.classify, "get_classes", return_value=[]):
            self.assertIsNone(engine.get_gesture())


if __name__ == "__main__":
    unittest.main()
