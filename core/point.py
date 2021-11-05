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
from core.vector import Vec3f

class Point(np.ndarray):

    """
        Point
        Base class for all point classes
    """

    # based on https://numpy.org/doc/stable/user/basics.subclassing.html#a-brief-python-primer-on-new-and-init
    def __new__(subtype, shape, dtype=float, buffer=None, offset=0,
                strides=None, order=None, decimals=2):
        # Create the ndarray instance of our type, given the usual
        # ndarray input arguments.  This will call the standard
        # ndarray constructor, but return an object of our type.
        # It also triggers a call to Point.__array_finalize__
        obj = super(Point, subtype).__new__(subtype, shape, dtype, buffer,
                                            offset, strides, order)

        obj.decimals = decimals

        # Finally, we must return the newly created object:
        return obj

    def __array_finalize__(self, obj):
        # ``self`` is a new object resulting from
        # ndarray.__new__(Point, ...), therefore it only has
        # attributes that the ndarray.__new__ constructor gave it -
        # i.e. those of a standard ndarray.
        #
        # We could have got to the ndarray.__new__ call in 3 ways:
        # From an explicit constructor - e.g. Point():
        #    obj is None
        #    (we're in the middle of the Point.__new__
        #    constructor, and self.decimals will be set when we return to
        #    Point.__new__)
        if obj is None: return
        # From view casting - e.g arr.view(Point):
        #    obj is arr
        #    (type(obj) can be Point)
        # From new-from-template - e.g infoarr[:3]
        #    type(obj) is Point
        #
        # Note that it is here, rather than in the __new__ method,
        # that we set the default value for 'decimals', because this
        # method sees all creation of default objects - with the
        # Point.__new__ constructor, but also with
        # arr.view(Point).
        self.decimals = getattr(obj, 'decimals', 2)
        # We do not need to return anything


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
        obj.decimals = 0

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


class Point3f(Point):

    """
        Point3f
        Represents a point3 float class
    """

    def __new__(subtype, x=0, y=0, z=0):
        obj = super(Point3f, subtype).__new__(Point3f, (3,), np.float32)
        obj[0] = x
        obj[1] = y
        obj[2] = z

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

    @property
    def z(self):
        return self[2]

    @z.setter
    def z(self, new_z):
        self[2] = new_z

    def dir_to(self, dest):
        if dest is None:
            return None
        dir_vec = dest-self
        dir_vec_norm = dir_vec/np.linalg.norm(dir_vec)
        return Vec3f(dir_vec_norm[0], dir_vec_norm[1], dir_vec_norm[2])

    def to_string(self):
        return '[{}, {}, {}]'.format(self[0], self[1], self[2])

    def __str__(self):
        return '[{1:.{0}f}, {2:.{0}f}, {3:.{0}f}]'.format(self.decimals,
                                                          self[0],
                                                          self[1],
                                                          self[2])


class Point3i(Point):

    """
        Point3i
        Represents point3 integer class
    """

    def __new__(subtype, x=0, y=0, z=0):
        obj = super(Point3i, subtype).__new__(Point3i, (3,), np.int32)
        obj[0] = x
        obj[1] = y
        obj[2] = z
        obj.decimals = 0

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

    @property
    def z(self):
        return self[2]

    @z.setter
    def z(self, new_z):
        self[2] = new_z

    def to_string(self):
        return '[{}, {}, {}]'.format(self[0], self[1], self[2])

    def __str__(self):
        return '[{1:.{0}f}, {2:.{0}f}, {3:.{0}f}]'.format(self.decimals,
                                                          self[0],
                                                          self[1],
                                                          self[2])
