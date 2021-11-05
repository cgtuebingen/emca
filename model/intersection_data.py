"""
    MIT License

    Copyright (c) 2020 Christoph Kreisl
    Copyright (c) 2021 Lukas Ruppert

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

from core.point import Point3f
from core.color import Color4f
from stream.stream import Stream
from model.user_data import UserData

import typing


class IntersectionData(UserData):

    """
        IntersectionData
        Represents one intersection point of a traced path through the scene.
        Holds information about the intersection, more precisely the intersection position, the intersection index,
        if a next event estimation was set, if a intersection position was set and current estimate information at this point.
    """

    def __init__(self, stream : Stream):
        super().__init__(stream)

        self._depth_idx = stream.read_uint()

        # position
        self._pos = None
        if stream.read_bool():
            self._pos = stream.read_point3f()

        # next event estimation position
        self._pos_ne = None
        self._visible_ne = None
        if stream.read_bool():
            self._pos_ne = stream.read_point3f()
            self._visible_ne = stream.read_bool()

        # the incident radiance estimate of the entire path evaluated up to this point
        self._li = None
        if stream.read_bool():
            self._li = stream.read_color4f()

        # emission
        self._le = None
        if stream.read_bool():
            self._le = stream.read_color4f()

    @property
    def depth_idx(self) -> typing.Optional[int]:
        """
        Returns the current depth index (intersection index)
        """
        return self._depth_idx

    @property
    def is_ne_visible(self) -> typing.Optional[bool]:
        """
        Returns if the next estimation is occluded
        """
        return self._visible_ne

    @property
    def pos(self) -> typing.Optional[Point3f]:
        """
        Returns the intersection position
        """
        return self._pos

    @property
    def pos_ne(self) -> typing.Optional[Point3f]:
        """
        Returns the position of the next event estimation
        """
        return self._pos_ne

    @property
    def li(self) -> typing.Optional[Color4f]:
        """
        Returns the current estimate at this intersection / path position
        """
        return self._li

    @property
    def le(self) -> typing.Optional[Color4f]:
        """
        Returns the emission at this intersection / path position
        """
        return self._le

