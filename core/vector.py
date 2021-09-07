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

import numpy as np


class Vec(np.ndarray):

    """
        Vec
        Base class for all point classes
    """

    # based on https://numpy.org/doc/stable/user/basics.subclassing.html#a-brief-python-primer-on-new-and-init
    def __new__(subtype, shape, dtype=float, buffer=None, offset=0,
                strides=None, order=None, decimals=2):
        # Create the ndarray instance of our type, given the usual
        # ndarray input arguments.  This will call the standard
        # ndarray constructor, but return an object of our type.
        # It also triggers a call to Vec.__array_finalize__
        obj = super(Vec, subtype).__new__(subtype, shape, dtype, buffer,
                                            offset, strides, order)

        obj.decimals = decimals

        # Finally, we must return the newly created object:
        return obj

    def __array_finalize__(self, obj):
        # ``self`` is a new object resulting from
        # ndarray.__new__(Vec, ...), therefore it only has
        # attributes that the ndarray.__new__ constructor gave it -
        # i.e. those of a standard ndarray.
        #
        # We could have got to the ndarray.__new__ call in 3 ways:
        # From an explicit constructor - e.g. Vec():
        #    obj is None
        #    (we're in the middle of the Vec.__new__
        #    constructor, and self.decimals will be set when we return to
        #    Vec.__new__)
        if obj is None: return
        # From view casting - e.g arr.view(Vec):
        #    obj is arr
        #    (type(obj) can be Vec)
        # From new-from-template - e.g infoarr[:3]
        #    type(obj) is Vec
        #
        # Note that it is here, rather than in the __new__ method,
        # that we set the default value for 'decimals', because this
        # method sees all creation of default objects - with the
        # Vec.__new__ constructor, but also with
        # arr.view(Vec).
        self.decimals = getattr(obj, 'decimals', 2)
        # We do not need to return anything
