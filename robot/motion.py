from __future__ import annotations

import asyncio

from typing import TYPE_CHECKING, Self, Coroutine

import aioserial

from serial.tools import list_ports

from odrive.enums import AxisError

import flatbuffers
from MotionProtocol import Message, MessageType, Remote, ODriveStatus

if TYPE_CHECKING:
    from .sparky import Sparky

class Motion:
    rfb = 0 # Right Forward-Backward
    rlr = 0 # Right Left-Right
    lfb = 0 # Left Forward-Backward
    llr = 0 # Left Left-Right

    rt = 0 # Right Trigger
    lt = 0 # Left Trigger

    dpad_u = False
    dpad_d = False
    dpad_l = False
    dpad_r = False

    triangle = False
    cross = False
    square = False
    circle = False

    def __init__(self, robot: Sparky) -> None:
        self.robot = robot

        self._connect()


    def _connect(self):
        self.serial = aioserial.AioSerial(port=self._find_serial_dev(), baudrate=115200, timeout=1)

    async def reconnect(self):
        while True:
            try:
                self._connect()
                print("Connected.")
                return

            except Exception as e:
                print(e)

            await asyncio.sleep(10)


    def _find_serial_dev(self):
        for port in list_ports.comports():
            if port.manufacturer == 'Teensyduino':
                return port.device

        raise Exception("Could not connect to motion controller")

    def move(self, rfb, rlr, lfb, llr, rt, lt, dpad_u, dpad_d, dpad_l, dpad_r, triangle, cross, square, circle):
        # TODO: implement some sort of timeout if this isnt called often enough

        self.rfb = rfb
        self.rlr = rlr
        self.lfb = lfb
        self.llr = llr
        self.rt = rt
        self.lt = lt

        self.dpad_u = dpad_u
        self.dpad_d = dpad_d
        self.dpad_l = dpad_l
        self.dpad_r = dpad_r

        self.triangle = triangle
        self.cross = cross
        self.square = square
        self.circle = circle

    def stop(self):
        self.rfb = 0
        self.rlr = 0
        self.lfb = 0
        self.llr = 0
        self.rt = 0
        self.lt = 0

        self.dpad_u = False
        self.dpad_d = False
        self.dpad_l = False
        self.dpad_r = False

        self.triangle = False
        self.cross = False
        self.square = False
        self.circle = False

    async def run(self):
        try:
            while True:
                builder = flatbuffers.Builder(1024)

                Remote.Start(builder)

                Remote.RemoteAddEnabled(builder, self.robot.enabled)
                Remote.RemoteAddMode(builder, self.robot.mode.MODE_ID if self.robot.mode else 0)

                Remote.RemoteAddRlr(builder, self.rlr)
                Remote.RemoteAddRfb(builder, self.rfb)
                Remote.RemoteAddRt(builder, self.rt)
                Remote.RemoteAddLlr(builder, self.llr)
                Remote.RemoteAddLfb(builder, self.lfb)
                Remote.RemoteAddLt(builder, self.lt)

                Remote.RemoteAddDpadU(builder, self.dpad_u)
                Remote.RemoteAddDpadD(builder, self.dpad_d)
                Remote.RemoteAddDpadL(builder, self.dpad_l)
                Remote.RemoteAddDpadR(builder, self.dpad_r)

                Remote.RemoteAddTriangle(builder, self.triangle)
                Remote.RemoteAddCross(builder, self.cross)
                Remote.RemoteAddSquare(builder, self.square)
                Remote.RemoteAddCircle(builder, self.circle)

                remote = Remote.End(builder)

                Message.Start(builder)
                Message.AddType(builder, MessageType.MessageType.REMOTE)
                Message.AddRemote(builder, remote)
                msg = Message.End(builder)

                builder.Finish(msg)

                buf = builder.Output()

                try:
                    await self.serial.write_async(buf)

                    ret = await self.serial.read_until_async(expected=aioserial.LF, size=None)
                except aioserial.SerialException:
                    print("Motion serial failure, trying again")
                    await self.reconnect()
                    continue

                if ret:
                    try:
                        status = ODriveStatus.ODriveStatus.GetRootAsODriveStatus(ret[:-1], 0)
                        print(f"Connected: 1: {status.Connected0()}, 2: {status.Connected1()}, 3: {status.Connected2()}, 4: {status.Connected3()}, 5: {status.Connected4()}, 6: {status.Connected5()}")
                        print(f"Errors:\n    00: {status.Error00()}, 01: {status.Error01()}\n    10: {status.Error10()}, 11: {status.Error11()}\n    20: {status.Error20()}, 21: {status.Error21()}\n    30: {status.Error30()}, 31: {status.Error31()}\n    40: {status.Error40()}, 41: {status.Error41()}\n    50: {status.Error50()}, 51: {status.Error51()}")
                    except Exception as e:
                        print(f"ugh {e}", print(ret))
                        pass
                else:
                    print("Motion controller did not respond")

                await asyncio.sleep(0.1)

        except asyncio.CancelledError:
            print(f"{repr(self)} task cancelled")

        except Exception as e:
            print(f"{repr(self)} task exception {e}")

            from traceback import print_exc
            print_exc()
