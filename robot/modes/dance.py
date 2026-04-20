from robot.sparky import Sparky

from .manual import ManualMode

from face import Face

face = Face()

# filler since I implemented all buttons in ManualMode
class DanceMode(ManualMode, Face):
    MODE_ID = 5

async def setup(robot: Sparky):
    return DanceMode(robot)