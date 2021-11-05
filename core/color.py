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

import numpy as np


class Color(np.ndarray):

    """
        Color
        Base class for all point classes
    """

    # based on https://numpy.org/doc/stable/user/basics.subclassing.html#a-brief-python-primer-on-new-and-init
    def __new__(subtype, shape, dtype=float, buffer=None, offset=0,
                strides=None, order=None, decimals=2):
        # Create the ndarray instance of our type, given the usual
        # ndarray input arguments.  This will call the standard
        # ndarray constructor, but return an object of our type.
        # It also triggers a call to Color.__array_finalize__
        obj = super(Color, subtype).__new__(subtype, shape, dtype, buffer,
                                            offset, strides, order)

        obj.decimals = decimals

        # Finally, we must return the newly created object:
        return obj

    def __array_finalize__(self, obj):
        # ``self`` is a new object resulting from
        # ndarray.__new__(Color, ...), therefore it only has
        # attributes that the ndarray.__new__ constructor gave it -
        # i.e. those of a standard ndarray.
        #
        # We could have got to the ndarray.__new__ call in 3 ways:
        # From an explicit constructor - e.g. Color():
        #    obj is None
        #    (we're in the middle of the Color.__new__
        #    constructor, and self.decimals will be set when we return to
        #    Color.__new__)
        if obj is None: return
        # From view casting - e.g arr.view(Color):
        #    obj is arr
        #    (type(obj) can be Color)
        # From new-from-template - e.g infoarr[:3]
        #    type(obj) is Color
        #
        # Note that it is here, rather than in the __new__ method,
        # that we set the default value for 'decimals', because this
        # method sees all creation of default objects - with the
        # Color.__new__ constructor, but also with
        # arr.view(Color).
        self.decimals = getattr(obj, 'decimals', 2)
        # We do not need to return anything


class Color4f(Color):

    """
        Color4f
        Represents a red, green, blue color class
    """

    def __new__(subtype, r=0, g=0, b=0, a=1):
        obj = super(Color4f, subtype).__new__(Color4f, (4,), np.float32)
        obj[0] = r
        obj[1] = g
        obj[2] = b
        obj[3] = a

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
    def alpha(self):
        return self[3]

    @alpha.setter
    def alpha(self, new_alpha):
        self[3] = new_alpha

    @property
    def mean(self):
        return (self.red + self.green + self.blue) / 3.0

    def to_list_rgb(self):
        return [self.red, self.green, self.blue]

    def to_list_srgb(self):
        srgb = [np.uint8(np.clip(np.where(x > 0.0031308, ((255.0 * 1.055) * np.power(x, 1.0/2.4) - 0.055), x * (12.92 * 255.0)), 0.0, 255.0)) for x in self[0:3]]

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
