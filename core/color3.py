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

from core.color import Color
import numpy as np


class Color3f(Color):

    """
        Color3f
        Represents a red, green, blue color class
    """

    def __new__(subtype, r=0, g=0, b=0):
        obj = super(Color3f, subtype).__new__(Color3f, (3,), np.float32)
        obj[0] = r
        obj[1] = g
        obj[2] = b

        return obj


    @property
    def red(self):
        return self[0]

    @red.setter
    def red(self, new_red):
        self[0] = new_red

    @property
    def green(self):
        return self[1]

    @green.setter
    def green(self, new_green):
        self[1] = new_green

    @property
    def blue(self):
        return self[2]

    @blue.setter
    def blue(self, new_blue):
        self[2] = new_blue

    @property
    def mean(self):
        return (self.red + self.green + self.blue) / 3.0

    def to_list_rgb(self):
        return [self.red, self.green, self.blue]

    def to_list_srgb(self):
        srgb = [np.uint8(np.clip(np.where(x > 0.0031308, ((255.0 * 1.055) * np.power(x, 1.0/2.4) - 0.055), x * (12.92 * 255.0)), 0.0, 255.0)) for x in self]

        return srgb

    def to_string(self):
        return '[{}, {}, {}]'.format(self[0],
                                     self[1],
                                     self[2])

    def __str__(self):
        return '[{1:.{0}f}, {2:.{0}f}, {3:.{0}f}]'.format(self.decimals,
                                                          self[0],
                                                          self[1],
                                                          self[2])
