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
from view.view_render_image.hdr_graphics_view import HDRGraphicsView
from PySide2.QtWidgets import QWidget
from PySide2.QtCore import QPoint, Slot
from PySide2.QtCore import Qt
from core.pyside2_uic import loadUi
import math
import os
import logging

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from controller.controller import Controller
else:
    from typing import Any as Controller


class ViewRenderImage(QWidget):

    """
        ViewRenderImage
        Handles the view of the rendered image and the interaction to select a specific pixel.
        The selected pixel and its corresponding position will be send to the controller,
        which will then send a request to the server.
    """

    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        ui_filepath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ui', 'render_image.ui'))
        loadUi(ui_filepath, self)

        # accept drops for drag n drop feature
        self.setAcceptDrops(True)

        self._value = 0.0
        self._controller = None
        # HDR graphics view handles .exr images
        self._graphics_view = HDRGraphicsView(self)

        # add graphics view
        self.layoutView.addWidget(self._graphics_view)

        # connect signals
        self.btnReset.clicked.connect(self.reset)
        self.hsExposure.valueChanged.connect(self.set_spin_value)
        self.dsbExposure.valueChanged.connect(self.set_slider_value)
        self.cbFalsecolor.stateChanged.connect(self.set_falsecolor_value)

    @Slot(int, name='set_falsecolor_value')
    def set_falsecolor_value(self, value : int):
        """
        Toggles falsecolor display of the image
        """
        self._graphics_view.set_falsecolor(value != int(Qt.CheckState.Unchecked))

    def set_plusminus(self, value : bool):
        """
        Toggles plusminus display of the image
        :param value: boolean
        :return:
        """
        self._graphics_view.set_plusminus(value)

    def set_show_ref(self, value : bool):
        """
        Toggles display of the reference image
        :param value: boolean
        :return:
        """
        self._graphics_view.set_show_ref(value)

    @Slot(float, name='set_slider_value')
    def set_slider_value(self, value : float):
        """
        Sets the slider value of the exposure
        """
        # code from HDRiTools qt4Image
        len_slider = self.hsExposure.maximum() - self.hsExposure.minimum()
        len_spin = self.dsbExposure.maximum() - self.dsbExposure.minimum()
        ratio = (value - self.dsbExposure.minimum()) / len_spin
        new_value = int(math.floor((ratio * len_slider) + 0.5 + self.hsExposure.minimum()))
        self.hsExposure.setValue(new_value)
        self.update_exposure(float(value))

    @Slot(int, name='set_spin_value')
    def set_spin_value(self, value : int):
        """
        Sets the spin value of the exposure
        """
        # code from HDRiTools qt4Image
        len_slider = self.hsExposure.maximum() - self.hsExposure.minimum()
        len_spin = self.dsbExposure.maximum() - self.dsbExposure.minimum()
        ratio = (value - self.hsExposure.minimum()) / len_slider
        new_value = (ratio * len_spin) + self.dsbExposure.minimum()
        self.dsbExposure.setValue(new_value)

    def update_exposure(self, value : float):
        """
        Updates the exposure of the image
        """
        if value != self._value:
            self._value = value
            self._graphics_view.update_exposure(value)

    def set_controller(self, controller : Controller):
        """
        Sets the connection to the controller
        """
        self._controller = controller
        self.btnLoadImage.clicked.connect(controller.options.load_image_dialog)
        self.btnLoadReference.clicked.connect(controller.options.load_reference_dialog)

    def enable_view(self, enable : bool):
        """
        Enables the view elements
        """
        self.btnReset.setEnabled(enable)
        self.dsbExposure.setEnabled(enable)
        self.hsExposure.setEnabled(enable)

    def request_pixel_data(self, pixel : QPoint):
        """
        Informs the controller about the selected pixel
        """
        self._controller.stream.request_render_pixel(pixel)

    def load_hdr_image(self, filepath : typing.Union[str, bytes], is_reference : bool = False):
        """
        Loads an exr image from the given filepath
        """
        return self._graphics_view.load_hdr_image(filepath, is_reference)

    def save_last_rendered_image_filepath(self):
        hdr_image = self._graphics_view.hdr_image
        if hdr_image:
            if isinstance(hdr_image.filepath, str):
                self._controller.options.save_options({'rendered_image_filepath': hdr_image.filepath})

    @Slot(bool, name='reset')
    def reset(self, clicked):
        """
        Resets the exposure settings, and fits the render image within the view
        :param clicked: boolean
        :return:
        """
        self._graphics_view.reset()
        self.hsExposure.setValue(0)
        self.cbFalsecolor.setCheckState(Qt.CheckState.Unchecked)
