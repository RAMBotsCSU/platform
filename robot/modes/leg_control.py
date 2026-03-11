from robot.sparky import Sparky

from .manual import ManualMode

# filler since I implemented all buttons in ManualMode
class LEGCONTROL(ManualMode):
    MODE_ID = 2


async def setup(robot: Sparky):
    return LEGCONTROL(robot)