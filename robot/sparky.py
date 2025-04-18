import asyncio
import traceback
import importlib.util

from traceback import print_exc
from concurrent.futures import ThreadPoolExecutor


from .ui import MainWindow
from .mode import Mode
from .motion import Motion
from .controller import Controller


class Sparky:
    enabled: bool = False
    mode: Mode = None
    selected_mode_name: str

    def __init__(self) -> None:
        self._executor = ThreadPoolExecutor(max_workers=3)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        print(exc_type, exc, tb)

    async def set_enabled(self, en: bool):
        if en:
            try:
                print(f"Starting mode '{self.selected_mode_name}'")

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

            except Exception as e:
                print_exc()

        else:
            self.motion.stop()
            self.mode.stop()
            self.mode = None
            self.enabled = en


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
        self.ui = MainWindow.start(self)
        self.loop = self.ui.loop
        asyncio.set_event_loop(self.loop)

        self.controller = Controller(self)
        self.loop.create_task(self.controller.events())
        self.loop.create_task(self.controller.polling())

        self.motion = Motion(self)
        self.loop.create_task(self.motion.run())

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

        # set controller back to blue, weird annoying way
        self._executor.submit(asyncio.run, self.controller.led.set_color((0, 0, 50)))

        self._executor.shutdown()

        print("stopped")
