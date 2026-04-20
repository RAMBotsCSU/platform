from __future__ import annotations

import math
import queue

from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import QWidget


class LiDARRadarWidget(QWidget):
    def __init__(self, lidar=None, parent=None):
        super().__init__(parent)
        self.lidar = lidar
        self.max_distance = getattr(lidar, "max_distance", 2000)
        self.heat = {}  # (ix, iy) -> intensity
        self.grid_size = 120
        self.decay = 0.92
        self.min_intensity = 0.03
        self.hit_gain = 1.6
        self.heat_saturation = 10.0

        self.flip_x = False
        self.flip_y = False

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._poll_lidar)
        self.timer.start(33)  # ~30 FPS

    def _poll_lidar(self):
        # Decay old heat
        for cell in list(self.heat.keys()):
            v = self.heat[cell] * self.decay
            if v < self.min_intensity:
                del self.heat[cell]
            else:
                self.heat[cell] = v

        if self.lidar is not None:
            # Add new samples
            while True:
                try:
                    _, angle, distance = self.lidar.get_sample_nowait()
                except queue.Empty:
                    break
                except Exception:
                    break

                a = math.radians(angle)
                x_mm = distance * math.cos(a)
                y_mm = distance * math.sin(a)

                if self.flip_x:
                    x_mm = -x_mm
                if self.flip_y:
                    y_mm = -y_mm

                ix = int(((x_mm + self.max_distance) / (2 * self.max_distance)) * (self.grid_size - 1))
                iy = int((((-y_mm) + self.max_distance) / (2 * self.max_distance)) * (self.grid_size - 1))

                if 0 <= ix < self.grid_size and 0 <= iy < self.grid_size:
                    self.heat[(ix, iy)] = min(self.heat.get((ix, iy), 0.0) + self.hit_gain, self.heat_saturation)

        self.update()

    def _heat_color(self, t: float) -> QColor:
        t = max(0.0, min(1.0, t))
        if t < 0.25:
            u = t / 0.25
            r, g, b = 0, int(255 * u), 255
        elif t < 0.5:
            u = (t - 0.25) / 0.25
            r, g, b = 0, 255, int(255 * (1 - u))
        elif t < 0.75:
            u = (t - 0.5) / 0.25
            r, g, b = int(255 * u), 255, 0
        else:
            u = (t - 0.75) / 0.25
            r, g, b = 255, int(255 * (1 - u)), 0
        return QColor(r, g, b, int(40 + 180 * t))

    def paintEvent(self, _):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(10, 10, 10))

        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2
        radius = min(w, h) * 0.45

        # Radar grid
        painter.setPen(QPen(QColor(60, 60, 60), 1))
        for f in (0.25, 0.5, 0.75, 1.0):
            r = int(radius * f)
            painter.drawEllipse(cx - r, cy - r, 2 * r, 2 * r)
        painter.drawLine(cx - int(radius), cy, cx + int(radius), cy)
        painter.drawLine(cx, cy - int(radius), cx, cy + int(radius))

        # Heatmap cells
        cell_px = (2.0 * radius) / self.grid_size
        x0 = cx - radius
        y0 = cy - radius

        painter.setPen(QPen(QColor(0, 0, 0, 0), 0))
        for (ix, iy), intensity in self.heat.items():
            nx = ((ix + 0.5) / self.grid_size) * 2.0 - 1.0
            ny = ((iy + 0.5) / self.grid_size) * 2.0 - 1.0
            if nx * nx + ny * ny > 1.0:
                continue

            t = intensity / self.heat_saturation
            painter.fillRect(
                int(x0 + ix * cell_px),
                int(y0 + iy * cell_px),
                max(1, int(cell_px) + 1),
                max(1, int(cell_px) + 1),
                self._heat_color(t),
            )
