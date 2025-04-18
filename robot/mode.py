from __future__ import annotations

import asyncio

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .sparky import Sparky

class Mode:
    MODE_ID = -1
    loop: asyncio.AbstractEventLoop

    def __init__(self, robot: Sparky) -> None:
        self.robot = robot
        self.motion = robot.motion

    async def start(self): ...

    async def _run(self):
        try:
            await self.start()

        except asyncio.CancelledError:
            print(f"{self.__class__.__name__} cancelled")

    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        self.loop.create_task(self.start())

        self.loop.run_forever()

    def stop(self):
        for task in asyncio.all_tasks(self.loop):
            print(f"Cancelling Task: {task.get_coro()}")
            task.cancel()

        self.loop.stop()
