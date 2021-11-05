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

import typing
from stream.stream import Stream
from model.path_data import PathData
import numpy as np
import logging


class PixelData(object):

    """
        RenderData
        Represents information about one pixel.
        The data is computed on the server side in the pixel re-rendering step.
        Containing all information about all traced paths through this pixel with all user added information.
    """

    def __init__(self):
        # {sample_index / path_index : PathData}
        self._dict_paths = {}  # ordered dict (since Python 3.7)

    def deserialize(self, stream : Stream):
        """
        Deserialize a DataView object from the socket stream
        """
        sample_count = stream.read_uint()
        self._dict_paths.clear()
        logging.info("SampleCount: {}".format(sample_count))
        # deserialize the amount of paths which were traced through the selected pixel
        for sample in range(sample_count):
            path_data = PathData(stream)
            # append deserialized path to dict
            self._dict_paths[path_data.sample_idx] = path_data

    @property
    def dict_paths(self) -> typing.Dict[int, PathData]:
        """
        Returns a dict containing all traced paths through the pixel
        """
        return self._dict_paths

    def get_indices(self) -> np.ndarray:
        """
        Returns all path indices as numpy array
        """
        return np.array(list(self._dict_paths.keys()))

    def to_string(self) -> str:
        """
        Returns a string with class information
        """
        return 'number of paths = {}'.format(len(self._dict_paths))

    def clear(self):
        """
        Clears the data
        """
        self._dict_paths.clear()
