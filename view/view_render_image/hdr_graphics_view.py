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

from core.hdr_graphics_view_base import HDRGraphicsViewBase
from PySide2.QtCore import QPoint
import logging


class HDRGraphicsView(HDRGraphicsViewBase):

    """
        HDRGraphicsView
        Custom QGraphicsView which holds the rendered image and handles interactions
    """

    def __init__(self, parent):
        HDRGraphicsViewBase.__init__(self)
        self._parent = parent
        self._old_scene_pos = QPoint()

    def mousePressEvent(self, q_mouse_event):
        """
        Handles a mouse press event, aves the current position.
        A request to the controller will only be send if the position will be the same after mouse btn release.
        :param q_mouse_event:
        :return:
        """
        global_pos = q_mouse_event.globalPos()
        self._old_scene_pos = self.transform_to_scene_pos(global_pos)
        super().mousePressEvent(q_mouse_event)

    def mouseReleaseEvent(self, q_mouse_event):
        """
        Handles a mouse button release.
        Informs the controller if the position has not changed since the click.
        Otherwise the image will be moved.
        :param q_mouse_event:
        :return:
        """
        global_pos = q_mouse_event.globalPos()
        new_pos = self.transform_to_scene_pos(global_pos)
        if self._old_scene_pos == new_pos:
            pixel = self.transform_to_image_coordinate(q_mouse_event.globalPos())
            if self.pixel_within_bounds(pixel):
                self._parent.request_render_data(pixel)
        super().mouseReleaseEvent(q_mouse_event)

    def mouseMoveEvent(self, q_mouse_event):
        """
        Handles mouse move event
        :param q_mouse_event:
        :return:
        """
        image_coord = self.transform_to_image_coordinate(q_mouse_event.globalPos())
        text = '({},{})'.format(image_coord.x(), image_coord.y())
        self._parent.labelCurrentPos.setText(text)
        super().mouseMoveEvent(q_mouse_event)

    def dropEvent(self, q_drop_event):
        try:
            super().dropEvent(q_drop_event)
            self._parent.enable_view(True)
            self._parent.save_last_rendered_image_filepath()
        except Exception as e:
            logging.error(e)

