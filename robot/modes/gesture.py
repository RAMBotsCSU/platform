# robot/modes/gesture.py

import asyncio

from robot.sparky import Sparky
from ..mode import Mode
from robot.gesture_engine import GestureEngine, Gesture


class GestureMode(Mode):
    """
    A mode that ignores the PS4 controller and drives Sparky purely
    from hand gestures via the Coral/EdgeTPU.

        Gestures mapped to virtual PS face buttons:
            - fist           -> cross
            - one            -> circle
            - peace_inverted -> square
            - palm           -> triangle
            - stop           -> no button pressed
    """

    MODE_ID = 4

    def __init__(self, robot: Sparky) -> None:
        super().__init__(robot)

        self.engine = GestureEngine(
            model_path="./ML/edgetpu_mobilenet_4.tflite",
            labels_path="./ML/labels.txt",
            camera_index=0,
        )

        # Last sent command
        self._last_cmd = None

    async def start(self):
        """
        Main loop for GestureMode. This is called by Mode.run()
        and runs until stop() is called.
        """
        try:
            while True:
                gesture = self.engine.get_gesture()

                # Match PushUpMode command shape: neutral sticks/triggers/dpad
                # and only emit face-button commands.
                rfb = rlr = lfb = llr = 0
                rt = lt = 0
                dpad_u = dpad_d = dpad_l = dpad_r = 0
                triangle = cross = square = circle = 0

                if gesture is not None:
                    if gesture == Gesture.CROSS:
                        cross = 1
                    elif gesture == Gesture.CIRCLE:
                        circle = 1
                    elif gesture == Gesture.SQUARE:
                        square = 1
                    elif gesture == Gesture.TRIANGLE:
                        triangle = 1

                # Send command to motion system
                await self.robot.move(
                    rfb,
                    rlr,
                    lfb,
                    llr,
                    rt,
                    lt,
                    dpad_u,
                    dpad_d,
                    dpad_l,
                    dpad_r,
                    triangle,
                    cross,
                    square,
                    circle,
                )

                await asyncio.sleep(0.1)

        except asyncio.CancelledError:
            # Normal shutdown path when mode is stopped
            pass
        except Exception as e:
            print(f"GestureMode error: {e}")

    def stop(self):
        """
        Called by Sparky.set_enabled(False) and Sparky.stop().
        We ensure the camera is released.
        """
        try:
            self.engine.close()
        except Exception:
            pass

        # Let the base class handle cancelling the task etc.
        super().stop()


async def setup(robot: Sparky):
    return GestureMode(robot)
