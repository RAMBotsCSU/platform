from robot.sparky import Sparky

from .manual import ManualMode
# filler since I implemented all buttons in ManualMode
class LegTestingMode(ManualMode):
    MODE_ID = 3 

async def setup(robot: Sparky):
    return LegTestingMode(robot)