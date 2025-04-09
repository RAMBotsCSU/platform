from __future__ import annotations

import asyncio

from typing import TYPE_CHECKING, Self, Coroutine

import aioserial

from serial.tools import list_ports
# print(list())

import flatbuffers
from MotionProtocol import Message, MessageType, Remote

if TYPE_CHECKING:
    from .sparky import Sparky

class Motion:
    rfb = 0 # Right Forward-Backward
    rlr = 0 # Right Left-Right
    lfb = 0 # Left Forward-Backward
    llr = 0 # Left Left-Right

    rt = 0 # Right Trigger
    lt = 0 # Left Trigger

    toggle_bottom = False # use IMU
    toggle_top = False # Enable

    def __init__(self, robot: Sparky) -> None:
        self.robot = robot

        self._connect()


    def _connect(self):
        self.serial = aioserial.AioSerial(port=self._find_serial_dev(), baudrate=115200, timeout=1)

    async def reconnect(self):
        while True:
            try:
                self._connect()
                return

            except Exception as e:
                print(e)

            await asyncio.sleep(10)


    def _find_serial_dev(self):
        for port in list_ports.comports():
            print(vars(port))

            if port.manufacturer == 'Teensyduino':
                return port.device

        raise Exception("Could not connect to motion controller")

    def move(self, rfb, rlr, lfb, llr, rt, lt):
        # TODO: implement some sort of timeout if this isnt colled often enough

        self.rfb = rfb
        self.rlr = rlr
        self.lfb = lfb
        self.llr = llr
        self.rt = rt
        self.lt = lt

        self.toggle_top = True

    def stop(self):
        self.rfb = 0
        self.rlr = 0
        self.lfb = 0
        self.llr = 0
        self.rt = 0
        self.lt = 0

        self.toggle_top = False

    async def run(self):
        try:
            while True:
                builder = flatbuffers.Builder(1024)

                Remote.Start(builder)
                Remote.AddEnabled(builder, self.robot.enabled)
                Remote.AddMode(builder, 6)
                Remote.AddRlr(builder, self.rlr)
                Remote.AddRfb(builder, self.rfb)
                Remote.AddRt(builder, self.rt)
                Remote.AddLlr(builder, self.llr)
                Remote.AddLfb(builder, self.lfb)
                Remote.AddLt(builder, self.lt)
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

                if not ret:
                    print("Motion controller did not respond")

                await asyncio.sleep(0.1)

        except asyncio.CancelledError:
            print(f"{repr(self)} task cancelled")

        except Exception as e:
            print(f"{repr(self)} task exception {e}")

            from traceback import print_exc
            print_exc()
