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

from core.point2 import Point2i
from core.color3 import Color3f
from PySide2.QtGui import QPixmap
from PySide2.QtGui import QColor
from PySide2.QtGui import QIcon
from PySide2.QtCore import QPoint


class PixelIcon(object):

    """
        PixelIcon
        Represents and holds information about a selected pixel
        Pixel color, the position. Is used to display the selected pixel as icon in the view
    """

    def __init__(self):
        self._pixel_icon = QIcon()
        self._pixel_pos = QPoint()
        self._color = QColor()
        self._pixmap = QPixmap(16, 16)

    @property
    def icon(self):
        """
        Returns the pixel icon
        :return: QIcon
        """
        return self._pixel_icon

    @property
    def pixel_pos(self):
        """
        Returns the pixel position
        :return: QPoint
        """
        return self._pixel_pos

    @property
    def pixel_pos_point2i(self):
        """
        Transforms the QPoint pixel position into a Point2i and returns the data type
        :return: Point2i
        """
        return Point2i(self._pixel_pos.x(), self._pixel_pos.y())

    @property
    def pixel_color_color3f(self):
        """
        Transform a QColor into a Color3f object with the pixel color information
        :return: Color3f
        """
        return Color3f(self._color.red(), self._color.green(), self._color.blue(), self._color.alpha())

    def set_pixel(self, pixmap, pixel):
        """
        Sets the pixel position and the icon with the pixmap
        :param pixmap: QPixmap
        :param pixel: QPoint
        :return:
        """
        self._pixel_pos = pixel
        q_image = pixmap.toImage()
        self._color = q_image.pixelColor(pixel)
        self._pixmap.fill(self._color)
        self._pixel_icon.addPixmap(self._pixmap)

    def get_pixel_str(self):
        """
        Returns a string with class information
        :return: str
        """
        return '({},{})'.format(self._pixel_pos.x(),
                                self._pixel_pos.y())


