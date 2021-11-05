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

from plugins.plugin_spherical_view.spherical_graphics_view import SphericalGraphicsView
from PySide2.QtWidgets import QWidget
from PySide2.QtCore import Qt
from PySide2.QtCore import Slot
from core.pyside2_uic import loadUi
import os
import logging


class ViewSphericalViewImage(QWidget):

    """
        ViewSphericalViewImage
    """

    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        ui_filepath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'ui', 'spherical_view_image.ui'))
        loadUi(ui_filepath, self)

        self._pos = None
        self._dirW_i = None
        self._dirW_o = None
        self._falsecolor = False
        self._exposure = 0.0

        self._controller = None
        self._is_btn_enabled = False
        # HDR graphics view handles .exr images
        self._graphics_view = SphericalGraphicsView(self)

        # add graphics view
        self.hdrImage.addWidget(self._graphics_view)

        # connect signals
        self.btnSave.clicked.connect(self.save_image)
        self.btnReset.clicked.connect(self.fit_view)
        self.falsecolorCb.toggled.connect(self.falsecolor_cb)
        self.exposureSlider.valueChanged.connect(self.exposure_slider)

    @Slot(bool, name='save_image')
    def save_image(self, clicked):
        self._graphics_view.save_image()

    @Slot(bool, name='fit_view')
    def fit_view(self, clicked):
        self._graphics_view.reset()

    @Slot(bool, name='falsecolor_cb')
    def falsecolor_cb(self, checked):
        self.falsecolor = checked

    @Slot(int, name='exposure_slider')
    def exposure_slider(self, value):
        self.exposure = float(value)/100.0

    def load_hdr_image(self, filepath):
        return self._graphics_view.load_hdr_image(filepath)

    def set_highlight(self, name, direction=None, color=None):
        self._graphics_view.set_highlight(name, direction, color)

    def update_hightlights(self):
        self._graphics_view.update_highlights()

    @property
    def is_btn_enabled(self):
        return self._is_btn_enabled

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, pos):
        self._pos = pos

    @property
    def dirW_i(self):
        return self._dirW_i

    @dirW_i.setter
    def dirW_i(self, dirW_i):
        self._dirW_i = dirW_i
        self._graphics_view.set_highlight('incident direction', self._dirW_i, [0, 255, 0])

    @property
    def dirW_o(self):
        return self._dirW_o

    @dirW_o.setter
    def dirW_o(self, dirW_o):
        self._dirW_o = dirW_o
        self._graphics_view.set_highlight('outgoing direction', self._dirW_o, [255, 255, 255])

    @property
    def falsecolor(self):
        return self._falsecolor

    @falsecolor.setter
    def falsecolor(self, falsecolor):
        self._falsecolor = falsecolor
        if falsecolor:
            self.falsecolorCb.setCheckState(Qt.Checked)
        else:
            self.falsecolorCb.setCheckState(Qt.Unchecked)

        self._graphics_view.set_falsecolor(falsecolor)

    @property
    def exposure(self):
        return self._exposure

    @exposure.setter
    def exposure(self, exposure):
        self._exposure = exposure
        self.exposureSlider.setSliderPosition(int(exposure*100))

        self._graphics_view.update_exposure(exposure)

    def clear(self):
        self._graphics_view.clear()
        self.pos = None
        self.dirW_i = None
        self.dirW_o = None

    def enable_buttons(self, enable):
        self._is_btn_enabled = enable
        self.btnSave.setEnabled(enable)
        self.btnReset.setEnabled(enable)

    def select_intersection(self, dict_paths, path_idx, its_idx):
        path = dict_paths.get(path_idx, None)
        if path:
            intersections = path.intersections
            vert = intersections.get(its_idx, None)
            if vert and vert.pos is not None:
                self.pos = vert.pos

                self.set_highlight('NEE', vert.pos.dir_to(vert.pos_ne), [0, 0, 255] if vert.is_ne_visible else [255, 0, 0])

                prev_vert = next_vert = intersections.get(its_idx-1, None)
                if prev_vert and prev_vert.pos is not None:
                    self.dirW_i = vert.pos.dir_to(prev_vert.pos)
                # FIXME: 1 is not necessarily the first index
                elif its_idx == 1 and path and path.path_origin is not None:
                    self.dirW_i = vert.pos.dir_to(path.path_origin)
                else:
                    self.dirW_i = None

                next_vert = intersections.get(its_idx+1, None)
                if next_vert and next_vert.pos is not None:
                    self.dirW_o = vert.pos.dir_to(next_vert.pos)
                else:
                    self.dirW_o = None

