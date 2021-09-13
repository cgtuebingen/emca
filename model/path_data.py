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
from core.point3 import Point3f
import typing
from stream.stream import Stream
from model.intersection_data import IntersectionData
from model.user_data import UserData

class PathData(UserData):

    """
        PathData
        Represents one traced path with added user data
    """

    def __init__(self):
        super().__init__()

        self._sample_idx = None
        self._path_depth = None
        self._path_origin = None
        self._final_estimate = None
        self._dict_intersections = {} # ordered dict (since Python 3.7)
        self._intersection_count = 0

    def deserialize(self, stream : Stream):
        """
        Deserializes one path object from the socket stream
        :param stream:
        :return:
        """
        super().deserialize(stream)
        self._sample_idx = stream.read_int()
        self._path_depth = stream.read_int()
        self._path_origin = stream.read_point3f()

        self._final_estimate = None
        if stream.read_bool():
            self._final_estimate = stream.read_color3f()

        self._dict_intersections.clear()
        self._intersection_count = stream.read_uint()
        for i in range(0, self._intersection_count):
            intersection = IntersectionData()
            intersection.deserialize(stream)
            self._dict_intersections[intersection.depth_idx] = intersection

    @property
    def final_estimate(self) -> Color3f:
        """
        Returns the Final Estimate value of this path
        """
        return self._final_estimate

    @property
    def sample_idx(self) -> int:
        """
        Returns the samples index which indicates the path index
        """
        return self._sample_idx

    @property
    def path_origin(self) -> Point3f:
        """
        Returns the path origin
        """
        return self._path_origin

    @property
    def path_depth(self) -> int:
        """
        Returns the path depth (amount of bounces and containing vertices)
        """
        return self._path_depth

    @property
    def intersections(self) -> typing.Dict[int, IntersectionData]:
        """
        Returns the a dict containing all path vertices
        :return: dict{intersection_idx, intersection object}
        """
        return self._dict_intersections

    @property
    def intersection_count(self) -> int:
        """
        Returns the amount of vertices (intersections)
        """
        return self._intersection_count

    def valid_depth(self) -> bool:
        """
        Checks if the path depth is valid
        """
        return self._path_depth is not None

    def to_string(self):
        return "SampleIdx = {}\n" \
               "PathDepth = {}\n" \
               "PathOrigin = {}\n" \
               "FinalEstimate = {}\n" \
               "ShowPath = {}\n" \
               "Intersections = {}\n" \
               "IntersectionCount = {}".format(self._sample_idx, self._path_depth, self._path_origin,
                                               self._final_estimate, self._dict_intersections,
                                               self._intersection_count)
