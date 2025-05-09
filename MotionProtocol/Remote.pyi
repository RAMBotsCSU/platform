from __future__ import annotations

import flatbuffers
import numpy as np

import flatbuffers
import typing

uoffset: typing.TypeAlias = flatbuffers.number_types.UOffsetTFlags.py_type

class Remote(object):
  @classmethod
  def GetRootAs(cls, buf: bytes, offset: int) -> Remote: ...
  @classmethod
  def GetRootAsRemote(cls, buf: bytes, offset: int) -> Remote: ...
  def Init(self, buf: bytes, pos: int) -> None: ...
  def Enabled(self) -> bool: ...
  def Mode(self) -> int: ...
  def Rlr(self) -> int: ...
  def Rfb(self) -> int: ...
  def Rt(self) -> int: ...
  def Llr(self) -> int: ...
  def Lfb(self) -> int: ...
  def Lt(self) -> int: ...
  def DpadU(self) -> bool: ...
  def DpadD(self) -> bool: ...
  def DpadL(self) -> bool: ...
  def DpadR(self) -> bool: ...
  def Triangle(self) -> bool: ...
  def Cross(self) -> bool: ...
  def Square(self) -> bool: ...
  def Circle(self) -> bool: ...
def RemoteStart(builder: flatbuffers.Builder) -> None: ...
def Start(builder: flatbuffers.Builder) -> None: ...
def RemoteAddEnabled(builder: flatbuffers.Builder, enabled: bool) -> None: ...
def RemoteAddMode(builder: flatbuffers.Builder, mode: int) -> None: ...
def RemoteAddRlr(builder: flatbuffers.Builder, rlr: int) -> None: ...
def RemoteAddRfb(builder: flatbuffers.Builder, rfb: int) -> None: ...
def RemoteAddRt(builder: flatbuffers.Builder, rt: int) -> None: ...
def RemoteAddLlr(builder: flatbuffers.Builder, llr: int) -> None: ...
def RemoteAddLfb(builder: flatbuffers.Builder, lfb: int) -> None: ...
def RemoteAddLt(builder: flatbuffers.Builder, lt: int) -> None: ...
def RemoteAddDpadU(builder: flatbuffers.Builder, dpadU: bool) -> None: ...
def RemoteAddDpadD(builder: flatbuffers.Builder, dpadD: bool) -> None: ...
def RemoteAddDpadL(builder: flatbuffers.Builder, dpadL: bool) -> None: ...
def RemoteAddDpadR(builder: flatbuffers.Builder, dpadR: bool) -> None: ...
def RemoteAddTriangle(builder: flatbuffers.Builder, triangle: bool) -> None: ...
def RemoteAddCross(builder: flatbuffers.Builder, cross: bool) -> None: ...
def RemoteAddSquare(builder: flatbuffers.Builder, square: bool) -> None: ...
def RemoteAddCircle(builder: flatbuffers.Builder, circle: bool) -> None: ...
def RemoteEnd(builder: flatbuffers.Builder) -> uoffset: ...
def End(builder: flatbuffers.Builder) -> uoffset: ...

