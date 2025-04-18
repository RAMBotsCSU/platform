import asyncio

from robot.sparky import Sparky

from ..mode import Mode


# effectively just walk mode
class ManualMode(Mode):
    MODE_ID = 6

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

            dpad_u = self.robot.controller.dpad_up
            dpad_d = self.robot.controller.dpad_down
            dpad_l = self.robot.controller.dpad_left
            dpad_r = self.robot.controller.dpad_right

            triangle = self.robot.controller.triangle
            cross = self.robot.controller.cross
            square = self.robot.controller.square
            circle = self.robot.controller.circle

            await self.robot.move(rfb, rlr, lfb, llr, rt, lt, dpad_u, dpad_d, dpad_l, dpad_r, triangle, cross, square, circle)

            await asyncio.sleep(0.1)


async def setup(robot: Sparky):
    return ManualMode(robot)
