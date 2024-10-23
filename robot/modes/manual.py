import asyncio

from robot.sparky import Sparky

from ..mode import Mode


class ManualMode(Mode):
    def __init__(self, robot: Sparky) -> None:
        super().__init__(robot)


    async def start(self):
        while True:
            print(self.robot.controller)

            rfb = self.robot.controller.right_stick_y - 128
            rlr = self.robot.controller.right_stick_x - 128

            lfb = self.robot.controller.left_stick_y - 128
            llr = self.robot.controller.left_stick_x - 128

            lt = self.robot.controller.l2_analog
            rt = self.robot.controller.r2_analog

            await self.robot.move(rfb, rlr, lfb, llr, rt, lt)

            await asyncio.sleep(0.1)

async def setup(robot: Sparky):
    return ManualMode(robot)
