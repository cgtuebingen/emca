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

from core.vector3 import Vec3f
from core.point3 import Point3f


class CameraData(object):

    """
        Camera Data
        Holds information about the camera data
        Will be used by the renderer interface to initialise the camera for the 3D scene viewer
    """

    def __init__(self):
        self._near_clip = 5
        self._far_clip = 15
        self._focus_dist = 10
        self._fov = 45
        self._up = Vec3f(0, 0, 1)
        self._direction = Vec3f(1, 0, 0)
        self._origin = Point3f(0, 0, 0)

    def deserialize(self, stream):
        """
        Deserializes all camera information from the socket stream
        :param stream: SocketStream
        :return:
        """
        self._near_clip = stream.read_float()
        self._far_clip = stream.read_float()
        self._focus_dist = stream.read_float()
        self._fov = stream.read_float()
        self._up = stream.read_vec3f()
        self._direction = stream.read_vec3f()
        self._origin = stream.read_point3f()

    @property
    def near_clip(self):
        """
        Returns the camera near clip value
        :return:
        """
        return self._near_clip

    @property
    def far_clip(self):
        """
        Returns the camera far clip value
        :return:
        """
        return self._far_clip

    @property
    def focus_dist(self):
        """
        Returns the camera focus distance
        :return:
        """
        return self._focus_dist

    @property
    def fov(self):
        """
        Returns the camera the field of view angle
        :return:
        """
        return self._fov

    @property
    def up(self):
        """
        Returns the camera up vector
        :return:
        """
        return self._up

    @property
    def direction(self):
        """
        Returns the camera viewing direction
        :return:
        """
        return self._direction

    @property
    def origin(self):
        """
        Returns the camera 3D origin world point
        :return:
        """
        return self._origin

    def to_string(self):
        """
        Returns all camera information within a string
        :return:
        """
        return 'neaClip = {} \n' \
               'farClip = {} \n' \
               'focusDist = {} \n' \
               'fov = {} \n' \
               'up = {} \n' \
               'direction = {} \n' \
               'origin = {} \n'.format(self._near_clip,
                                       self._far_clip,
                                       self._focus_dist,
                                       self._fov,
                                       self._up.to_string(),
                                       self._direction.to_string(),
                                       self._origin.to_string())


