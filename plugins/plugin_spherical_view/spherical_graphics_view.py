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

from core.hdr_graphics_view_base import HDRGraphicsViewBase
from PySide2.QtWidgets import QFileDialog
from PySide2.QtGui import QBrush
from PySide2.QtGui import QColor
from PySide2.QtCore import Qt
from PySide2.QtCore import QPoint
import logging

import matplotlib.pyplot as plt
import numpy as np


class SphericalGraphicsView(HDRGraphicsViewBase):

    def __init__(self, parent):
        HDRGraphicsViewBase.__init__(self)
        self._parent = parent
        self._highlights = {}

    def update_highlights(self):
        if self.pixmap_item is None:
            return

        for h_name in self._highlights.keys():
            # TODO: assign colors deterministically, based on name
            if self._highlights[h_name].get('color') is None:
                cmap = plt.get_cmap('Accent')
                color = cmap(np.random.rand())
                self._highlights[h_name]['color'] = QColor(color[0]*255, color[1]*255, color[2]*255)

            if self._highlights[h_name].get('ellipse') is None:
                self._highlights[h_name]['ellipse'] = self._scene.addEllipse(0.0, 0.0, 5.0, 5.0, self._highlights[h_name]['color'], QBrush(Qt.NoBrush))
                self._highlights[h_name]['ellipse'].setParentItem(self._pixmap_item)
                self._highlights[h_name]['ellipse'].setToolTip(h_name)

            if self._highlights[h_name].get('x') and self._highlights[h_name].get('y'):
                self._highlights[h_name]['ellipse'].setPos(QPoint(self._highlights[h_name]['x']*self.pixmap.width()-2.5, self._highlights[h_name]['y']*self.pixmap.height()-2.5))
                self._highlights[h_name]['ellipse'].show()
            else:
                self._highlights[h_name]['ellipse'].hide()

    def set_highlight(self, name, direction=None, color=None):
        if self._highlights.get(name) is None:
            self._highlights[name] = {}
        if color is not None:
            self._highlights[name]['color'] = QColor(color[0], color[1], color[2])
            if not self._highlights[name].get('ellipse') is None:
                self._highlights[name]['ellipse'].setPen(self._highlights[name]['color'])
        if direction is None:
            self._highlights[name]['x'] = None
            self._highlights[name]['y'] = None
            if not self._highlights[name].get('ellipse') is None:
                self._highlights[name]['ellipse'].hide()
        else:
            theta = np.arccos(direction[2])
            phi = np.arctan2(direction[1], direction[0])

            self._highlights[name]['x'] = (np.pi-phi)/(2.0*np.pi)
            self._highlights[name]['y'] = theta/np.pi

    def save_image(self):
        dialog = QFileDialog(self)
        dialog.setNameFilter("Images (*.png *.jpg)")
        dialog.selectNameFilter("Images (*.png *.jpg)")
        filepath = dialog.getSaveFileName(self)[0]

        logging.info('filepath: {}'.format(filepath))

        if filepath and self.pixmap:
            success = False
            if filepath.endswith('.jpg') or filepath.endswith('.jpeg'):
                success = self.pixmap.save(filepath, 'jpeg')
            elif filepath.endswith('.png'):
                success = self.pixmap.save(filepath, 'png')
            elif filepath.endswith('.exr'):
                success = self.hdr_image.save(filepath)
            if success:
                logging.info("Image saved SUCCESSFULLY")
            else:
                logging.error("ERROR in saving image")

    def clear(self):
        super().clear()
        for h_name in self._highlights.keys():
            if self._highlights[h_name].get('ellipse'):
                self._highlights[h_name]['ellipse'] = None
