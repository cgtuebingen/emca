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

from core.point import Point
import numpy as np


class Point2f(Point):

    """
        Point2f
        Represents a point2 float class
    """

    def __new__(subtype, x=0, y=0):
        obj = super(Point2f, subtype).__new__(Point2f, (2,), np.float32)
        obj[0] = x
        obj[1] = y

        return obj

    @property
    def x(self):
        return self[0]

    @x.setter
    def x(self, new_x):
        self[0] = new_x

    @property
    def y(self):
        return self[1]

    @y.setter
    def y(self, new_y):
        self[1] = new_y

    def to_string(self):
        return '[{}, {}]'.format(self[0], self[1])

    def __str__(self):
        return '[{1:.{0}f}, {2:.{0}f}]'.format(self.decimals,
                                               self[0],
                                               self[1])


class Point2i(Point):
    def __new__(subtype, x=0, y=0):
        obj = super(Point2i, subtype).__new__(Point2i, (2,), np.int32)
        obj[0] = x
        obj[1] = y

        return obj

    @property
    def x(self):
        return self[0]

    @x.setter
    def x(self, new_x):
        self[0] = new_x

    @property
    def y(self):
        return self[1]

    @y.setter
    def y(self, new_y):
        self[1] = new_y

    def to_string(self):
        return '[{}, {}]'.format(self[0], self[1])

    def __str__(self):
        return '[{1:.{0}f}, {2:.{0}f}]'.format(self.decimals,
                                               self[0],
                                               self[1])
