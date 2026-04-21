from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont, QImage, QPainter, QPen
from PyQt6.QtWidgets import QLabel, QSizePolicy, QVBoxLayout, QWidget

if TYPE_CHECKING:
    from .sparky import Sparky


class GesturePreviewWidget(QWidget):
    def __init__(
        self,
        robot: "Sparky" | None = None,
        parent: QWidget | None = None,
        model_path: str = "./ML/edgetpu_mobilenet_4.tflite",
        labels_path: str = "./ML/labels.txt",
        camera_index: int = 0,
    ) -> None:
        super().__init__(parent)

        self.robot = robot
        self.model_path = model_path
        self.labels_path = labels_path
        self.camera_index = camera_index

        self.engine: GestureEngine | None = None
        self._gesture_enum = None
        self._frame: np.ndarray | None = None
        self._status_text = "Gesture preview inactive"
        self._last_prediction = "No prediction"
        self._running = False

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(320, 240)

        self._timer = QTimer(self)
        self._timer.setInterval(100)
        self._timer.timeout.connect(self._update_frame)

    def start(self) -> None:
        if self._running:
            return

        if self.engine is None:
            try:
                self.engine = self._create_engine()
                self._status_text = "Gesture preview running"
            except Exception as e:
                self.engine = None
                self._status_text = f"Gesture preview unavailable: {e}"
                self.update()
                return

        self._running = True
        self._timer.start()
        self._update_frame()

    def _create_engine(self):
        gesture_engine_path = Path(__file__).with_name("gesture_engine.py")
        spec = importlib.util.spec_from_file_location("gesture_engine_widget_module", gesture_engine_path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"Could not load gesture engine module from {gesture_engine_path}")

        gesture_engine_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(gesture_engine_module)
        self._gesture_enum = gesture_engine_module.Gesture

        return gesture_engine_module.GestureEngine(
            model_path=self.model_path,
            labels_path=self.labels_path,
            camera_index=self.camera_index,
        )

    def stop(self) -> None:
        self._timer.stop()
        self._running = False
        self._frame = None
        self._last_prediction = "No prediction"

        if self.engine is not None:
            try:
                self.engine.close()
            finally:
                self.engine = None

        self._status_text = "Gesture preview stopped"
        self.update()

    def _gesture_name(self, gesture: int | None) -> str:
        if gesture is None:
            return ""

        if self._gesture_enum is not None:
            names = {
                self._gesture_enum.STOP: "STOP",
                self._gesture_enum.PUSH_DOWN: "PUSH_DOWN",
                self._gesture_enum.SIT: "SIT",
                self._gesture_enum.WALK_FORWARD: "WALK_FORWARD",
                self._gesture_enum.WALK_BACKWARD: "WALK_BACKWARD",
            }
            return names.get(gesture, str(gesture))

        names = {
            0: "STOP",
            1: "PUSH_DOWN",
            2: "SIT",
            3: "WALK_FORWARD",
            4: "WALK_BACKWARD",
        }
        return names.get(gesture, str(gesture))

    def _update_frame(self) -> None:
        if self.engine is None:
            return

        frame, gesture, label = self.engine.read_frame_and_prediction()
        if frame is None:
            self._frame = None
            self._last_prediction = "Camera unavailable"
            self.update()
            return

        self._frame = frame
        gesture_name = self._gesture_name(gesture)
        if gesture_name:
            self._last_prediction = f"Prediction: {gesture_name} ({label or 'Unknown'})"
        elif label:
            self._last_prediction = f"Prediction: {label}"
        else:
            self._last_prediction = "Prediction: ..."

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(15, 15, 15))

        if self._frame is not None:
            frame = self._frame
            rgb = frame[:, :, ::-1].copy()
            height, width, channels = rgb.shape
            bytes_per_line = channels * width
            image = QImage(rgb.data, width, height, bytes_per_line, QImage.Format.Format_RGB888).copy()

            target = self.rect().adjusted(8, 8, -8, -48)
            scaled = image.scaled(target.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

            x = target.x() + (target.width() - scaled.width()) // 2
            y = target.y() + (target.height() - scaled.height()) // 2
            painter.drawImage(x, y, scaled)
        else:
            painter.setPen(QColor(220, 220, 220))
            painter.setFont(QFont("Sans Serif", 12))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self._status_text)

        painter.setPen(QPen(QColor(0, 0, 0, 180), 1))
        overlay_rect = self.rect().adjusted(0, self.height() - 36, 0, 0)
        painter.fillRect(overlay_rect, QColor(0, 0, 0, 180))
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Sans Serif", 11, QFont.Weight.Bold))
        painter.drawText(overlay_rect.adjusted(12, 0, -12, 0), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, self._last_prediction)
