"""
    MIT License

    Copyright (c) 2020 Christoph Kreisl

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
"""

from core.color3 import Color3f
from core.vector3 import Vec3i
from core.vector3 import Vec3f
from core.point2 import Point2f
from core.point2 import Point2i
from core.point3 import Point3f
from core.point3 import Point3i

import abc
import struct
import numpy as np
from enum import Enum


class ByteOrder(Enum):
    NATIVE              = '@'   # native
    LITTLE_ENDIAN       = '<'   # little endian
    BIG_ENDIAN          = '>'   # big endian
    NETWORK             = '!'   # network (= big endian)


class Format(Enum):
    CHAR                = 'c'
    SIGNED_CHAR         = 'b'
    UNSIGNED_CHAR       = 'B'
    BOOL                = '?'
    SHORT               = 'h'
    UNSIGNED_SHORT      = 'H'
    INT                 = 'i'
    UNSIGNED_INT        = 'I'
    LONG                = 'q'
    UNSIGNED_LONG       = 'Q'
    FLOAT               = 'f'
    DOUBLE              = 'd'


class SizeOf(Enum):
    CHAR                = struct.calcsize(Format.CHAR.value)
    SIGNED_CHAR         = struct.calcsize(Format.UNSIGNED_CHAR.value)
    UNSIGNED_CHAR       = struct.calcsize(Format.UNSIGNED_CHAR.value)
    BOOL                = struct.calcsize(Format.BOOL.value)
    SHORT               = struct.calcsize(Format.SHORT.value)
    UNSIGNED_SHORT      = struct.calcsize(Format.UNSIGNED_SHORT.value)
    INT                 = struct.calcsize(Format.INT.value)
    UNSIGNED_INT        = struct.calcsize(Format.UNSIGNED_INT.value)
    LONG                = struct.calcsize(Format.LONG.value)
    UNSIGNED_LONG       = struct.calcsize(Format.UNSIGNED_LONG.value)
    FLOAT               = struct.calcsize(Format.FLOAT.value)
    DOUBLE              = struct.calcsize(Format.DOUBLE.value)


class Stream(object):

    """
    Stream interface
    """

    def __init__(self):
        pass

    @abc.abstractmethod
    def read(self, size) -> bytes:
        return

    @abc.abstractmethod
    def write(self, data : bytes, size : int):
        return

    """ Write operations """

    def write_char(self, value : bytes):
        data = struct.pack(Format.CHAR.value, value)
        self.write(data, SizeOf.CHAR.value)

    def write_schar(self, value : int):
        data = struct.pack(Format.SIGNED_CHAR.value, value)
        self.write(data, SizeOf.SIGNED_CHAR.value)

    def write_uchar(self, value : int):
        data = struct.pack(Format.UNSIGNED_CHAR.value, value)
        self.write(data, SizeOf.UNSIGNED_CHAR.value)

    def write_bool(self, value : bool):
        data = struct.pack(Format.BOOL.value, value)
        self.write(data, SizeOf.BOOL.value)

    def write_short(self, value : int):
        data = struct.pack(Format.SHORT.value, value)
        self.write(data, SizeOf.SHORT.value)

    def write_ushort(self, value : int):
        data = struct.pack(Format.UNSIGNED_SHORT.value, value)
        self.write(data, SizeOf.UNSIGNED_SHORT.value)

    def write_int(self, value : int):
        data = struct.pack(Format.INT.value, value)
        self.write(data, SizeOf.INT.value)

    def write_uint(self, value : int):
        data = struct.pack(Format.UNSIGNED_INT.value, value)
        self.write(data, SizeOf.UNSIGNED_INT.value)

    def write_long(self, value : int):
        data = struct.pack(Format.LONG.value, value)
        self.write(data, SizeOf.LONG.value)

    def write_ulong(self, value : int):
        data = struct.pack(Format.UNSIGNED_LONG.value, value)
        self.write(data, SizeOf.UNSIGNED_LONG.value)

    def write_float(self, value : float):
        data = struct.pack(Format.FLOAT.value, value)
        self.write(data, SizeOf.FLOAT.value)

    def write_double(self, value : float):
        data = struct.pack(Format.DOUBLE.value, value)
        self.write(data, SizeOf.DOUBLE.value)

    def write_string(self, value : str):
        raw_value = bytes(value, "utf-8")
        self.write_ulong(len(raw_value))
        self.write(raw_value, len(raw_value))

    """ Read operations """

    def read_char(self) -> bytes:
        data = self.read(SizeOf.CHAR.value)
        return struct.unpack(Format.CHAR.value, data)[0]

    def read_uchar(self) -> int:
        data = self.read(SizeOf.UNSIGNED_CHAR.value)
        return struct.unpack(Format.UNSIGNED_CHAR.value, data)[0]

    def read_bool(self) -> bool:
        data = self.read(SizeOf.BOOL.value)
        return struct.unpack(Format.BOOL.value, data)[0]

    def read_ushort(self) -> int:
        data = self.read(SizeOf.UNSIGNED_SHORT.value)
        return struct.unpack(Format.UNSIGNED_SHORT.value, data)[0]

    def read_short(self) -> int:
        data = self.read(SizeOf.SHORT.value)
        return struct.unpack(Format.SHORT.value, data)[0]

    def read_int(self) -> int:
        data = self.read(SizeOf.INT.value)
        return struct.unpack(Format.INT.value, data)[0]

    def read_uint(self) -> int:
        data = self.read(SizeOf.UNSIGNED_INT.value)
        return struct.unpack(Format.UNSIGNED_INT.value, data)[0]

    def read_long(self) -> int:
        data = self.read(SizeOf.LONG.value)
        return struct.unpack(Format.LONG.value, data)[0]

    def read_ulong(self) -> int:
        data = self.read(SizeOf.UNSIGNED_LONG.value)
        return struct.unpack(Format.UNSIGNED_LONG.value, data)[0]

    def read_float(self) -> float:
        data = self.read(SizeOf.FLOAT.value)
        return struct.unpack(Format.FLOAT.value, data)[0]

    def read_double(self) -> float:
        data = self.read(SizeOf.DOUBLE.value)
        return struct.unpack(Format.DOUBLE.value, data)[0]

    """ Specific read and write functions """
    def read_string(self) -> str:
        string_len = self.read_ulong()
        data = self.read(string_len)
        return data.decode("utf-8")

    def read_float_array(self, size) -> np.ndarray:
        data = self.read(size * SizeOf.FLOAT.value)
        return np.frombuffer(data, np.float32, size)

    def read_int_array(self, size) -> np.ndarray:
        data = self.read(size * SizeOf.INT.value)
        return np.frombuffer(data, np.int32, size)

    def read_point2f(self) -> Point2f:
        xs = self.read_float_array(2)
        return Point2f(xs[0], xs[1])

    def read_point2i(self) -> Point2i:
        xs = self.read_int_array(2)
        return Point2i(xs[0], xs[1])

    def read_point3f(self) -> Point3f:
        xs = self.read_float_array(3)
        return Point3f(xs[0], xs[1], xs[2])

    def read_point3i(self) -> Point3i:
        xs = self.read_int_array(3)
        return Point3i(xs[0], xs[1], xs[2])

    def read_vec3f(self) -> Vec3f:
        xs = self.read_float_array(3)
        return Vec3f(xs[0], xs[1], xs[2])

    def read_vec3i(self) -> Vec3i:
        xs = self.read_int_array(3)
        return Vec3i(xs[0], xs[1], xs[2])

    def read_color3f(self) -> Color3f:
        # FIXME: change API to transfer just 3 floats, otherwise call this color4f
        xs = self.read_float_array(4)
        return Color3f(xs[0], xs[1], xs[2])

