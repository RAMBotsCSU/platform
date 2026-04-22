import asyncio
import traceback
import importlib.util

from traceback import print_exc
from concurrent.futures import ThreadPoolExecutor


from .ui import MainWindow
from .mode import Mode
from .motion import Motion
from .controller import Controller
from .face import Face
from .audio_manager import AudioManager


class Sparky:
    enabled: bool = False
    mode: Mode = None
    selected_mode_name: str
    face: Face = None

    def __init__(self) -> None:
        self._executor = ThreadPoolExecutor(max_workers=3)
        self.lidar = None
        self.mode_to_face = {
            "manual": Face.OVAL,
            "pushup": Face.RAGE,
            "dance": Face.HAPPY,
            "leg_testing": Face.OVAL,
            "gesture": Face.OVAL,
            "leg_control": Face.OVAL,
        }
        self.audio_manager = AudioManager()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        print(exc_type, exc, tb)

    async def set_enabled(self, en: bool):
        if en:
            try:
                print(f"Starting mode '{self.selected_mode_name}'")

                mode_audio_map = {
                    "manual": 0,        # walkMode
                    "pushup": 1,        # pushUpsMode  
                    "leg_control": 2,   # legControlMode
                    "leg_testing": 3,   # gyroMode (closest match)
                    "gesture": 4,       # machineLearningMode (ML/gesture)
                    "dance": 5          # danceMode
                }

                # Play mode change sound
                mode_number = mode_audio_map.get(self.selected_mode_name, 0)
                self.audio_manager.play_mode_sounds(mode_number)
                # dynamically load the mode at runtime
                name = importlib.util.resolve_name(f"robot.modes.{self.selected_mode_name}", None)
                spec = importlib.util.find_spec(name)
                lib = importlib.util.module_from_spec(spec)

                spec.loader.exec_module(lib)
                setup = getattr(lib, 'setup')
                self.mode = await setup(self)

                # start the mode subroutine
                self._executor.submit(self.mode.run)

                self.enabled = en

                # Update face by selected mode
                if self.face:
                    cmd = self.mode_to_face.get(self.selected_mode_name, Face.OVAL)
                    self.face.send_command(cmd)

            except Exception as e:
                print_exc()

        else:
            self.audio_manager.play_sound("pause")
            self.motion.stop()
            self.mode.stop()
            self.mode = None
            self.enabled = en

            # Robot disabled expression
            if self.face:
                self.face.send_command(Face.OFF)


    async def heartbeat(self):
        next_change_in = 0
        led_on = True

        while True:
            if led_on:
                color = (0, 0, 0)
                next_change_in = 0.1

            else:
                if self.enabled:
                    color = (50, 0, 0)
                    next_change_in = 0.4

                else:
                    color = (0, 50 ,0)
                    next_change_in = 1.9

            led_on = not led_on

            await self.controller.led.set_color(color)
            await asyncio.sleep(next_change_in)


    async def move(self, *args, **kwargs):
        self.motion.move(*args, **kwargs)

    async def run(self):
        # Initialize LiDAR if available (optional hardware)
        try:
            from .lidar import LiDAR

            self.lidar = LiDAR(
                port=None,
                max_distance=2000,
                test_output=False,
                invert_rotation=True,
            )

            if self.lidar.port is None:
                self.lidar.port = self.lidar.find_serial_dev()

            await self.lidar.connect()
            self.lidar.start(loop=None)
            print("LiDAR initialized")
        except Exception as e:
            print(f"LiDAR init skipped: {e}")
            self.lidar = None

        self.ui = MainWindow.start(self)
        self.loop = self.ui.loop
        asyncio.set_event_loop(self.loop)

        # Play startup sound
        self.audio_manager.play_sound("startup1")

        self.controller = Controller(self)
        self.loop.create_task(self.controller.events())
        self.loop.create_task(self.controller.polling())

        self.motion = Motion(self)
        self.loop.create_task(self.motion.run())

        # Initialize face once
        try:
            self.face = Face()
        except Exception as e:
            print(f"Face init failed: {e}")
            self.face = None

        self.loop.create_task(self.heartbeat())
        self.ui.loop.run_forever()

    def stop(self):
        print(f"{self.__class__.__name__} stopping")

        self.motion.stop()

        if self.mode:
            self.mode.stop()

        for task in asyncio.all_tasks(self.loop):
            print(f"Cancelling Task: {task.get_coro()}")
            task.cancel()

        self.loop.stop()

        if self.lidar:
            self._executor.submit(asyncio.run, self.lidar.stop())

        # set controller back to blue, weird annoying way
        self._executor.submit(asyncio.run, self.controller.led.set_color((0, 0, 50)))

        self._executor.shutdown()

        print("stopped")
