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

import typing
from stream.stream import Stream
from model.path_data import PathData
import numpy as np
import logging


class RenderData(object):

    """
        RenderData
        Represents information about one pixel.
        The data is computed on the server side in the pixel re-rendering step.
        Containing all information about all traced paths through this pixel with all user added information.
    """

    def __init__(self):
        # amount of used samples per pixel
        self._sample_count = -1
        # {sample_index / path_index : PathData}
        self._dict_paths = {}

    def deserialize(self, stream : Stream):
        """
        Deserialize a DataView object from the socket stream
        :param stream:
        :return:
        """
        self._sample_count = stream.read_uint()
        self._dict_paths.clear()
        logging.info("SampleCount: {}".format(self._sample_count))
        # deserialize the amount of paths which were traced through the selected pixel
        for sample in range(0, self._sample_count):
            path_data = PathData()
            path_data.deserialize(stream)
            # append deserialized path to dict
            self._dict_paths[path_data.sample_idx] = path_data

    @property
    def dict_paths(self) -> typing.Dict[int, PathData]:
        """
        Returns a dict containing all traced paths through the pixel
        :return: dict{path_idx : PathData, ...}
        """
        return self._dict_paths

    @property
    def sample_count(self):
        """
        Returns the sample count
        :return: integer
        """
        return self._sample_count

    def valid_sample_count(self):
        """
        Checks if the sample count is valid > 0
        :return:
        """
        return self._sample_count > 0

    def get_indices(self):
        """
        Returns all path indices as numpy array
        :return: numpy array
        """
        return np.array(list(self._dict_paths.keys()))

    def to_string(self):
        """
        Returns a string with class information
        :return: string
        """
        return 'sampleCount = {} \n' \
               'dictPathsSize = {}'.format(self._sample_count, len(self._dict_paths))

    def clear(self):
        """
        Clears the data
        :return:
        """
        self._sample_count = -1
        self._dict_paths.clear()
