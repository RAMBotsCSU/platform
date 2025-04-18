# automatically generated by the FlatBuffers compiler, do not modify

# namespace: MotionProtocol

import flatbuffers
from flatbuffers.compat import import_numpy
from typing import Any
np = import_numpy()

class Remote(object):
    __slots__ = ['_tab']

    @classmethod
    def GetRootAs(cls, buf, offset: int = 0):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = Remote()
        x.Init(buf, n + offset)
        return x

    @classmethod
    def GetRootAsRemote(cls, buf, offset=0):
        """This method is deprecated. Please switch to GetRootAs."""
        return cls.GetRootAs(buf, offset)
    # Remote
    def Init(self, buf: bytes, pos: int):
        self._tab = flatbuffers.table.Table(buf, pos)

    # Remote
    def Enabled(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return bool(self._tab.Get(flatbuffers.number_types.BoolFlags, o + self._tab.Pos))
        return False

    # Remote
    def Mode(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Int8Flags, o + self._tab.Pos)
        return 0

    # Remote
    def Rlr(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(8))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Int8Flags, o + self._tab.Pos)
        return 0

    # Remote
    def Rfb(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(10))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Int8Flags, o + self._tab.Pos)
        return 0

    # Remote
    def Rt(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(12))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Uint8Flags, o + self._tab.Pos)
        return 0

    # Remote
    def Llr(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(14))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Int8Flags, o + self._tab.Pos)
        return 0

    # Remote
    def Lfb(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(16))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Int8Flags, o + self._tab.Pos)
        return 0

    # Remote
    def Lt(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(18))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Uint8Flags, o + self._tab.Pos)
        return 0

    # Remote
    def DpadU(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(20))
        if o != 0:
            return bool(self._tab.Get(flatbuffers.number_types.BoolFlags, o + self._tab.Pos))
        return False

    # Remote
    def DpadD(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(22))
        if o != 0:
            return bool(self._tab.Get(flatbuffers.number_types.BoolFlags, o + self._tab.Pos))
        return False

    # Remote
    def DpadL(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(24))
        if o != 0:
            return bool(self._tab.Get(flatbuffers.number_types.BoolFlags, o + self._tab.Pos))
        return False

    # Remote
    def DpadR(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(26))
        if o != 0:
            return bool(self._tab.Get(flatbuffers.number_types.BoolFlags, o + self._tab.Pos))
        return False

    # Remote
    def Triangle(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(28))
        if o != 0:
            return bool(self._tab.Get(flatbuffers.number_types.BoolFlags, o + self._tab.Pos))
        return False

    # Remote
    def Cross(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(30))
        if o != 0:
            return bool(self._tab.Get(flatbuffers.number_types.BoolFlags, o + self._tab.Pos))
        return False

    # Remote
    def Square(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(32))
        if o != 0:
            return bool(self._tab.Get(flatbuffers.number_types.BoolFlags, o + self._tab.Pos))
        return False

    # Remote
    def Circle(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(34))
        if o != 0:
            return bool(self._tab.Get(flatbuffers.number_types.BoolFlags, o + self._tab.Pos))
        return False

def RemoteStart(builder: flatbuffers.Builder):
    builder.StartObject(16)

def Start(builder: flatbuffers.Builder):
    RemoteStart(builder)

def RemoteAddEnabled(builder: flatbuffers.Builder, enabled: bool):
    builder.PrependBoolSlot(0, enabled, 0)

def AddEnabled(builder: flatbuffers.Builder, enabled: bool):
    RemoteAddEnabled(builder, enabled)

def RemoteAddMode(builder: flatbuffers.Builder, mode: int):
    builder.PrependInt8Slot(1, mode, 0)

def AddMode(builder: flatbuffers.Builder, mode: int):
    RemoteAddMode(builder, mode)

def RemoteAddRlr(builder: flatbuffers.Builder, rlr: int):
    builder.PrependInt8Slot(2, rlr, 0)

def AddRlr(builder: flatbuffers.Builder, rlr: int):
    RemoteAddRlr(builder, rlr)

def RemoteAddRfb(builder: flatbuffers.Builder, rfb: int):
    builder.PrependInt8Slot(3, rfb, 0)

def AddRfb(builder: flatbuffers.Builder, rfb: int):
    RemoteAddRfb(builder, rfb)

def RemoteAddRt(builder: flatbuffers.Builder, rt: int):
    builder.PrependUint8Slot(4, rt, 0)

def AddRt(builder: flatbuffers.Builder, rt: int):
    RemoteAddRt(builder, rt)

def RemoteAddLlr(builder: flatbuffers.Builder, llr: int):
    builder.PrependInt8Slot(5, llr, 0)

def AddLlr(builder: flatbuffers.Builder, llr: int):
    RemoteAddLlr(builder, llr)

def RemoteAddLfb(builder: flatbuffers.Builder, lfb: int):
    builder.PrependInt8Slot(6, lfb, 0)

def AddLfb(builder: flatbuffers.Builder, lfb: int):
    RemoteAddLfb(builder, lfb)

def RemoteAddLt(builder: flatbuffers.Builder, lt: int):
    builder.PrependUint8Slot(7, lt, 0)

def AddLt(builder: flatbuffers.Builder, lt: int):
    RemoteAddLt(builder, lt)

def RemoteAddDpadU(builder: flatbuffers.Builder, dpadU: bool):
    builder.PrependBoolSlot(8, dpadU, 0)

def AddDpadU(builder: flatbuffers.Builder, dpadU: bool):
    RemoteAddDpadU(builder, dpadU)

def RemoteAddDpadD(builder: flatbuffers.Builder, dpadD: bool):
    builder.PrependBoolSlot(9, dpadD, 0)

def AddDpadD(builder: flatbuffers.Builder, dpadD: bool):
    RemoteAddDpadD(builder, dpadD)

def RemoteAddDpadL(builder: flatbuffers.Builder, dpadL: bool):
    builder.PrependBoolSlot(10, dpadL, 0)

def AddDpadL(builder: flatbuffers.Builder, dpadL: bool):
    RemoteAddDpadL(builder, dpadL)

def RemoteAddDpadR(builder: flatbuffers.Builder, dpadR: bool):
    builder.PrependBoolSlot(11, dpadR, 0)

def AddDpadR(builder: flatbuffers.Builder, dpadR: bool):
    RemoteAddDpadR(builder, dpadR)

def RemoteAddTriangle(builder: flatbuffers.Builder, triangle: bool):
    builder.PrependBoolSlot(12, triangle, 0)

def AddTriangle(builder: flatbuffers.Builder, triangle: bool):
    RemoteAddTriangle(builder, triangle)

def RemoteAddCross(builder: flatbuffers.Builder, cross: bool):
    builder.PrependBoolSlot(13, cross, 0)

def AddCross(builder: flatbuffers.Builder, cross: bool):
    RemoteAddCross(builder, cross)

def RemoteAddSquare(builder: flatbuffers.Builder, square: bool):
    builder.PrependBoolSlot(14, square, 0)

def AddSquare(builder: flatbuffers.Builder, square: bool):
    RemoteAddSquare(builder, square)

def RemoteAddCircle(builder: flatbuffers.Builder, circle: bool):
    builder.PrependBoolSlot(15, circle, 0)

def AddCircle(builder: flatbuffers.Builder, circle: bool):
    RemoteAddCircle(builder, circle)

def RemoteEnd(builder: flatbuffers.Builder) -> int:
    return builder.EndObject()

def End(builder: flatbuffers.Builder) -> int:
    return RemoteEnd(builder)
