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

from stream.stream import Stream
from core.messages import ServerMsg
import logging


class RenderInfo(object):

    """
        RenderInfo
        Holds general information about the rendered scene,
        such as scene name, sample count and the path where the final rendered result is saved
    """

    def __init__(self):
        self._renderer_name = None
        self._scene_name = None
        self._sample_count = None

    def deserialize(self, stream : Stream):
        """
        Deserialize a Render Info object from the socket stream
        :param stream: SocketStream
        :return:
        """
        self._renderer_name = self.is_valid_str(stream.read_string())
        self._scene_name = self.is_valid_str(stream.read_string())
        self._sample_count = stream.read_uint()

    @staticmethod
    def is_valid_str(s):
        """
        Checks if the string is valid != "not set'
        :param s: string
        :return: boolean
        """
        if s == "":
            return "not set"
        else:
            return s

    @property
    def renderer_name(self) -> str:
        """
        Returns the renderer name
        """
        return self._renderer_name

    @property
    def scene_name(self) -> str:
        """
        Returns the scene name
        """
        return self._scene_name

    @property
    def sample_count(self):
        """
        Returns the amount of used samples to render the scene
        :return: integer
        """
        if self._sample_count is not None:
            return self._sample_count
        else:
            return 0

    @sample_count.setter
    def sample_count(self, sample_count):
        """
        Setter function, sets the sample count
        :param sample_count: integer
        :return:
        """
        self._sample_count = sample_count

    def to_string(self):
        """
        Returns a string containing information about the class
        :return:
        """
        return 'renderer_name = {} \n' \
               'scene_name = {} \n' \
               'sampleCount = {}'.format(self._renderer_name,
                                         self._scene_name,
                                         self._sample_count)
