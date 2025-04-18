from robot.sparky import Sparky

from .manual import ManualMode

# filler since I implemented all buttons in ManualMode
class PushUpMode(ManualMode):
    MODE_ID = 4


async def setup(robot: Sparky):
    return PushUpMode(robot)
