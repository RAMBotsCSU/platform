from robot.sparky import Sparky

from .manual import ManualMode

# filler since I implemented all buttons in ManualMode
class DanceMode(ManualMode):
    MODE_ID = 5


async def setup(robot: Sparky):
    return DanceMode(robot)
