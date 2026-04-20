from __future__ import annotations

import asyncio
import importlib
import importlib.util
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
	sys.path.insert(0, str(PROJECT_ROOT))


class DummyRobot:
	def __init__(self):
		self.enabled = False
		self.selected_mode_name = ""
		self.lidar = None

	async def set_enabled(self, enabled: bool):
		self.enabled = enabled

	def stop(self):
		pass


def main():
	os.chdir(PROJECT_ROOT)

	ui_path = PROJECT_ROOT / "robot" / "ui.py"
	spec = importlib.util.spec_from_file_location("ui_smoke_module", ui_path)
	if spec is None or spec.loader is None:
		raise RuntimeError(f"Could not load UI module from {ui_path}")

	ui_module = importlib.util.module_from_spec(spec)
	try:
		spec.loader.exec_module(ui_module)
	except ModuleNotFoundError as exc:
		if exc.name in {"PyQt6", "qasync"}:
			raise SystemExit(
				"PyQt6 and qasync must be installed to run the UI smoke test"
			) from exc
		raise
	MainWindow = ui_module.MainWindow

	if not os.environ.get("QT_QPA_PLATFORM") and not os.environ.get("DISPLAY"):
		os.environ["QT_QPA_PLATFORM"] = "offscreen"

	qt_widgets = importlib.import_module("PyQt6.QtWidgets")
	qt_core = importlib.import_module("PyQt6.QtCore")
	qasync = importlib.import_module("qasync")

	QApplication = qt_widgets.QApplication
	QTimer = qt_core.QTimer
	QEventLoop = qasync.QEventLoop

	app = QApplication(sys.argv)
	loop = QEventLoop(app)
	asyncio.set_event_loop(loop)

	robot = DummyRobot()
	lidar = None

	# Optional real hardware LiDAR integration for visual UI testing.
	# Enable with: UI_TEST_REAL_LIDAR=1
	if os.getenv("UI_TEST_REAL_LIDAR") == "1":
		lidar_path = PROJECT_ROOT / "robot" / "lidar.py"
		lidar_spec = importlib.util.spec_from_file_location("lidar_module", lidar_path)
		if lidar_spec is None or lidar_spec.loader is None:
			raise RuntimeError(f"Could not load LiDAR module from {lidar_path}")

		lidar_module = importlib.util.module_from_spec(lidar_spec)
		lidar_spec.loader.exec_module(lidar_module)
		LiDAR = lidar_module.LiDAR

		lidar = LiDAR(
			port=os.getenv("UI_TEST_LIDAR_PORT") or None,
			max_distance=int(os.getenv("UI_TEST_LIDAR_MAX_DISTANCE", "2000")),
			test_output=False,
			invert_rotation=os.getenv("UI_TEST_LIDAR_INVERT", "1") == "1",
		)

		if lidar.port is None:
			lidar.port = lidar.find_serial_dev()

		asyncio.run(lidar.connect())
		lidar.start(loop=None)
		robot.lidar = lidar

		def _cleanup_lidar():
			if lidar is not None:
				try:
					asyncio.run(lidar.stop())
				except Exception as exc:
					print(f"LiDAR cleanup error: {exc}")

		app.aboutToQuit.connect(_cleanup_lidar)

	window = MainWindow(robot)
	window.show()

	auto_close_s = os.getenv("UI_TEST_AUTO_CLOSE_S")
	if auto_close_s:
		QTimer.singleShot(int(float(auto_close_s) * 1000), app.quit)

	with loop:
		loop.run_forever()


if __name__ == "__main__":
	main()

