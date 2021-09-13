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


class UserData(object):

    """
        UserData
        Handles general data types which can be added by the user during the path tracing algorithm,
        in order to debug the system.
        Supported data types boolean, float, double, integer, point2i, point2f, point3i, point3f, color3f and vectors
    """

    def __init__(self):
        # handle default data types
        self._data = {}

    def deserialize(self, stream : Stream):
        """
        Deserialize UserData class from a socket stream
        :param stream:
        :return:
        """
        self.clear()
        num_items = stream.read_uint()
        for i in range(num_items):
            key = stream.read_string()
            type_identifier = stream.read_char()
            if ord(type_identifier) > ord('0') and ord(type_identifier) <= ord('9'):
                type_identifier = type_identifier+stream.read_char()
            type_identifier = type_identifier.decode("utf-8")

            if type_identifier == '?':
                self._data[key] = stream.read_bool()
            elif type_identifier == 'f':
                self._data[key] = stream.read_float()
            elif type_identifier == 'd':
                self._data[key] = stream.read_double()
            elif type_identifier == 'i':
                self._data[key] = stream.read_int()
            elif type_identifier == '2i':
                self._data[key] = stream.read_point2i()
            elif type_identifier == '2f':
                self._data[key] = stream.read_point2f()
            elif type_identifier == '3i':
                self._data[key] = stream.read_point3i()
            elif type_identifier == '3f':
                self._data[key] = stream.read_point3f()
            elif type_identifier == '4f':
                self._data[key] = stream.read_color3f()
            elif type_identifier == 's':
                self._data[key] = stream.read_string()
            else:
                raise Exception('unknown type '+type_identifier)

    @property
    def data(self) -> typing.Dict[str, typing.Any]:
        """
        Returns a data dict with set information
        """
        return self._data

    def clear(self):
        """
        Clears all data
        """
        self._data.clear()
