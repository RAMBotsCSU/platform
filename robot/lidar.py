import time
import threading
import asyncio
import queue as thread_queue
from serial.tools import list_ports
from adafruit_rplidar import RPLidar

class LiDAR:
    def __init__(
        self,
        port=None,
        max_distance=6000,
        test_output=True,
        queue_maxsize=500,
        time_offset_ms=50,
        angle_offset_deg=0.0,
        invert_rotation=False,
    ):
        """
        port: serial port of the LiDAR
        max_distance: maximum distance to accept in mm
        test_output: if True, prints some sample points to confirm
        time_offset_ms: milliseconds to backdate timestamps (compensate for processing delay)
        """
        self.port = port
        self.max_distance = max_distance
        self.lidar = None
        self._running = False
        self._thread = None
        self._loop = None
        self.queue = asyncio.Queue(maxsize=queue_maxsize)
        self.sample_queue = thread_queue.Queue(maxsize=queue_maxsize)  # thread-safe queue for GUI polling
        self.test_output = test_output
        self.time_offset_s = time_offset_ms / 1000.0
        self.angle_offset_deg = float(angle_offset_deg)
        self.invert_rotation = bool(invert_rotation)

    def find_serial_dev(self):
        for port in list_ports.comports():
            if port.manufacturer == 'Silicon Labs':
                return port.device

        raise Exception("Could not connect to LiDAR")
    
    async def connect(self):
        """Initialize LiDAR and prepare for scanning"""
        try:
            print("Connecting to LiDAR...")
            self.lidar = RPLidar(None, self.port, timeout=3)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize LiDAR: {e}")

        # Stop motor & clear input
        try:
            self.lidar.stop()
            self.lidar.stop_motor()
        except Exception:
            pass

        await asyncio.sleep(0.5)

        try:
            self.lidar.clear_input()
        except Exception:
            pass

        await asyncio.sleep(0.2)
        print("LiDAR connected and ready")

    def start(self, loop=None):
        """Start LiDAR motor and scanning thread"""
        if not self.lidar:
            raise RuntimeError("LiDAR not connected. Call connect() first.")
        self._loop = loop
        self._running = True

        # Start motor
        try:
            self.lidar.start_motor()
            print("LiDAR motor started")
        except Exception as e:
            raise RuntimeError(f"Failed to start LiDAR motor: {e}")

        time.sleep(1.0)  # let motor spin up

        # Start scanning thread
        self._thread = threading.Thread(target=self._scan_loop, daemon=True)
        self._thread.start()

    def _enqueue(self, item):
        """Runs on loop thread: drop oldest if full, then enqueue."""
        if self.queue.full():
            try:
                self.queue.get_nowait()
            except asyncio.QueueEmpty:
                pass
        try:
            self.queue.put_nowait(item)
        except asyncio.QueueFull:
            pass

    def _enqueue_threadsafe(self, item):
        """Drop oldest if full, then enqueue into thread-safe queue."""
        if self.sample_queue.full():
            try:
                self.sample_queue.get_nowait()
            except thread_queue.Empty:
                pass
        try:
            self.sample_queue.put_nowait(item)
        except thread_queue.Full:
            pass

    def get_sample_nowait(self):
        """Return (ts, angle, distance) or raise queue.Empty."""
        return self.sample_queue.get_nowait()

    @staticmethod
    def _normalize_angle(angle_deg: float) -> float:
        return angle_deg % 360.0

    def set_angle_offset(self, offset_deg: float):
        self.angle_offset_deg = float(offset_deg)

    def set_invert_rotation(self, enabled: bool):
        self.invert_rotation = bool(enabled)

    def _scan_loop(self):
        """Read measurements from LiDAR and push to asyncio queue"""
        print("LiDAR scanning thread started")
        sample_count = 0
        try:
            for new_scan, quality, angle, distance in self.lidar.iter_measurments():
                if not self._running:
                    break

                if distance <= 0 or distance > self.max_distance:
                    continue

                raw_angle = -angle if self.invert_rotation else angle
                corrected_angle = self._normalize_angle(raw_angle + self.angle_offset_deg)
                ts = time.monotonic() - self.time_offset_s
                item = (ts, corrected_angle, distance)

                self._enqueue_threadsafe(item)

                if self._loop is not None:
                    try:
                        self._loop.call_soon_threadsafe(self._enqueue, item)
                    except Exception:
                        pass

                # Print a few points to confirm
                if self.test_output and sample_count < 5:
                    print(f"LiDAR sample: angle={corrected_angle:.1f}, distance={distance:.1f} mm")
                    sample_count += 1

        except Exception as e:
            print("LiDAR thread exited:", e)
        finally:
            print("LiDAR scanning thread ended")

    async def stop(self):
        """Stop scanning and motor"""
        self._running = False
        await asyncio.sleep(0.1)  # let thread exit
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        try:
            if self.lidar:
                self.lidar.stop()
                self.lidar.stop_motor()
                self.lidar.disconnect()
                print("LiDAR stopped and disconnected")
        except Exception as e:
            print("Error stopping LiDAR:", e)