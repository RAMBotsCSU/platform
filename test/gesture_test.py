from __future__ import annotations

import builtins
import importlib
import importlib.util
import sys
import types
import unittest
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import mock_open, patch

import numpy as np


@dataclass
class DummyClass:
	id: int


class DummyCapture:
	def __init__(self, opened: bool = True, frame: np.ndarray | None = None) -> None:
		self._opened = opened
		self._frame = frame if frame is not None else np.zeros((2, 2, 3), dtype=np.uint8)
		self.released = False

	def isOpened(self) -> bool:
		return self._opened

	def read(self):
		return True, self._frame.copy()

	def release(self) -> None:
		self.released = True


class DummyInterpreter:
	def __init__(self, model_path: str, input_size: tuple[int, int] = (2, 2)) -> None:
		self.model_path = model_path
		self.input_size = input_size
		self.tensor = None
		self.invoked = False
		self.classifications: list[DummyClass] = []

	def allocate_tensors(self) -> None:
		pass

	def get_input_details(self):
		return [
			{
				"index": 0,
				"quantization": (0.5, 1),
				"dtype": np.int8,
			}
		]

	def set_tensor(self, index, tensor) -> None:
		self.tensor = (index, tensor)

	def invoke(self) -> None:
		self.invoked = True


def install_fake_deps(camera: DummyCapture | None = None):
	camera = camera or DummyCapture()

	cv2 = types.ModuleType("cv2")
	cv2.COLOR_BGR2RGB = 1
	cv2.VideoCapture = lambda index=0: camera
	cv2.resize = lambda frame, size: np.zeros((size[1], size[0], 3), dtype=frame.dtype)
	cv2.cvtColor = lambda frame, code: frame

	pycoral = types.ModuleType("pycoral")
	utils = types.ModuleType("pycoral.utils")
	edgetpu = types.ModuleType("pycoral.utils.edgetpu")
	adapters = types.ModuleType("pycoral.adapters")
	common = types.ModuleType("pycoral.adapters.common")
	classify = types.ModuleType("pycoral.adapters.classify")

	def make_interpreter(model_path):
		return DummyInterpreter(model_path)

	def input_size(interpreter):
		return interpreter.input_size

	def get_classes(interpreter, top_k=1, score_threshold=0.8):
		return interpreter.classifications

	edgetpu.make_interpreter = make_interpreter
	common.input_size = input_size
	classify.get_classes = get_classes

	pycoral.utils = utils
	pycoral.adapters = adapters
	utils.edgetpu = edgetpu
	adapters.common = common
	adapters.classify = classify

	modules = {
		"cv2": cv2,
		"pycoral": pycoral,
		"pycoral.utils": utils,
		"pycoral.utils.edgetpu": edgetpu,
		"pycoral.adapters": adapters,
		"pycoral.adapters.common": common,
		"pycoral.adapters.classify": classify,
	}

	return patch.dict(sys.modules, modules), camera


class TestGestureEngine(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.deps_patcher, cls.camera = install_fake_deps()
		cls.deps_patcher.start()

		module_path = Path(__file__).resolve().parents[1] / "robot" / "gesture_engine.py"
		spec = importlib.util.spec_from_file_location("gesture_engine_test_module", module_path)
		if spec is None or spec.loader is None:
			raise RuntimeError(f"Could not load gesture_engine module from {module_path}")

		cls.gesture_engine = importlib.util.module_from_spec(spec)
		spec.loader.exec_module(cls.gesture_engine)

	@classmethod
	def tearDownClass(cls):
		cls.deps_patcher.stop()

	def _make_engine(self, classifications=None):
		labels_text = "\n".join(
			[
				"0 stop",
				"1 fist",
				"2 palm",
				"3 peace_inverted",
				"4 one",
			]
		)

		with patch.object(builtins, "open", mock_open(read_data=labels_text)):
			engine = self.gesture_engine.GestureEngine(
				"model.tflite",
				"labels.txt",
				camera_index=0,
				history_len=3,
				score_threshold=0.8,
			)

		if classifications is not None:
			engine.interpreter.classifications = classifications

		return engine

	def test_init_loads_labels_and_camera(self):
		engine = self._make_engine()

		self.assertEqual(engine.interpreter.model_path, "model.tflite")
		self.assertEqual(engine.labels[0], "stop")
		self.assertEqual(engine.labels[4], "one")
		self.assertTrue(engine.cap.isOpened())
		self.assertEqual(engine.history.maxlen, 3)

	def test_init_raises_when_camera_cannot_open(self):
		labels_text = "0 stop\n"
		with patch.object(self.gesture_engine.cv2, "VideoCapture", return_value=DummyCapture(opened=False)):
			with patch.object(builtins, "open", mock_open(read_data=labels_text)):
				with self.assertRaises(RuntimeError):
					self.gesture_engine.GestureEngine("model.tflite", "labels.txt")

	def test_preprocess_resizes_and_quantizes(self):
		engine = self._make_engine()
		frame = np.zeros((2, 2, 3), dtype=np.uint8)

		result = engine._preprocess(frame)

		self.assertEqual(result.shape, (1, 2, 2, 3))
		self.assertEqual(result.dtype, np.int8)
		self.assertTrue(np.all(result == 1))

	def test_get_gesture_waits_for_history_then_returns_majority(self):
		engine = self._make_engine([DummyClass(id=0)])

		self.assertIsNone(engine.get_gesture())
		self.assertIsNone(engine.get_gesture())

		gesture = engine.get_gesture()
		self.assertEqual(gesture, self.gesture_engine.Gesture.STOP)

		self.assertIsNone(engine.get_gesture())

	def test_get_gesture_returns_none_without_confident_prediction(self):
		engine = self._make_engine([])

		self.assertIsNone(engine.get_gesture())
		self.assertIsNone(engine.get_gesture())
		self.assertIsNone(engine.get_gesture())

	def test_close_releases_camera(self):
		engine = self._make_engine()

		cap = engine.cap
		engine.close()

		self.assertIsNone(engine.cap)
		self.assertTrue(cap.released)


if __name__ == "__main__":
	unittest.main()