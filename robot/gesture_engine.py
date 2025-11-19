# robot/gesture_engine.py

import cv2
import time
import logging
from collections import deque

import numpy as np
from pycoral.utils import edgetpu
from pycoral.adapters import common, classify


class Gesture:
    STOP = 0
    PUSH_DOWN = 1
    SIT = 2
    WALK_FORWARD = 3
    WALK_BACKWARD = 4


class GestureEngine:
    """
    Coral + camera gesture recognizer.

    Usage:
        engine = GestureEngine("edgetpu_mobilenet_4.tflite", "labels.txt")
        gesture = engine.get_gesture()  # blocks for one frame/inference
    """

    def __init__(
        self,
        model_path: str,
        labels_path: str,
        camera_index: int = 0,
        history_len: int = 3,
        score_threshold: float = 0.80,
    ) -> None:
        self.logger = logging.getLogger(__name__)

        # Load model
        self.interpreter = edgetpu.make_interpreter(model_path)
        self.interpreter.allocate_tensors()

        self.input_details = self.interpreter.get_input_details()
        self.input_size = common.input_size(self.interpreter)  # (width, height)

        # Load labels
        self.labels = self._load_labels(labels_path)

        # Camera
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            raise RuntimeError("GestureEngine: camera could not be opened")

        # History for majority vote
        self.history = deque(maxlen=history_len)
        self.last_gesture = None

        self.score_threshold = score_threshold

        # Map label string -> Gesture enum
        # Adjust keys here to match your labels.txt
        self.label_to_gesture = {
            "stop": Gesture.STOP,
            "fist": Gesture.PUSH_DOWN,
            "palm": Gesture.SIT,
            "peace_inverted": Gesture.WALK_FORWARD,
            "one": Gesture.WALK_BACKWARD,
        }

        self.logger.info(
            "GestureEngine initialized (model=%s, labels=%s, history_len=%d)",
            model_path,
            labels_path,
            history_len,
        )

    def _load_labels(self, path: str) -> dict[int, str]:
        with open(path, "r") as f:
            return {
                int(line.split()[0]): line.strip().split(maxsplit=1)[1]
                for line in f.readlines()
            }

    def _preprocess(self, frame: np.ndarray) -> np.ndarray:
        # Resize to model input size, convert BGR->RGB
        w, h = self.input_size
        resized = cv2.resize(frame, (w, h))
        resized = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)

        scale, zero_point = self.input_details[0]["quantization"]
        dtype = self.input_details[0]["dtype"]

        if scale > 0:
            if dtype == np.int8:
                resized = ((resized / 255.0) / scale + zero_point).astype(np.int8)
            else:
                resized = ((resized / 255.0) / scale + zero_point).astype(np.uint8)

        return np.expand_dims(resized, axis=0)

    def _class_to_gesture(self, class_id: int) -> int | None:
        label = self.labels.get(class_id)
        if label is None:
            return None
        return self.label_to_gesture.get(label)

    def get_gesture(self) -> int | None:
        """
        Capture one frame, run inference, update 3-frame history, and
        return a gesture code (Gesture.*) or None if not stable/changed.

        This is a blocking call, but it's fine because it runs in the mode
        thread, not the UI thread.
        """
        ret, frame = self.cap.read()
        if not ret:
            self.logger.warning("GestureEngine: failed to read frame")
            return None

        input_tensor = self._preprocess(frame)
        self.interpreter.set_tensor(self.input_details[0]["index"], input_tensor)
        self.interpreter.invoke()

        classes = classify.get_classes(
            self.interpreter, top_k=1, score_threshold=self.score_threshold
        )

        if not classes:
            # No confident prediction
            return None

        c = classes[0]
        self.history.append(c.id)

        # Not enough history yet
        if len(self.history) < self.history.maxlen:
            return None

        # Majority vote
        counts: dict[int, int] = {}
        for cid in self.history:
            counts[cid] = counts.get(cid, 0) + 1

        majority_class = max(counts, key=counts.get)
        gesture = self._class_to_gesture(majority_class)

        if gesture is None:
            return None

        # Only return if changed from last gesture
        if gesture == self.last_gesture:
            return None

        self.last_gesture = gesture
        self.logger.info(
            "GestureEngine: majority gesture=%s (class_id=%d, label=%s)",
            gesture,
            majority_class,
            self.labels.get(majority_class, "Unknown"),
        )
        return gesture

    def close(self) -> None:
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            self.logger.info("GestureEngine camera released")

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass
