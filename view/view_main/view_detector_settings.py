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

from core.pyside2_uic import loadUi
from PySide2.QtCore import Slot
from PySide2.QtWidgets import QWidget
from PySide2.QtWidgets import QApplication
import os
import logging


class ViewDetectorSettings(QWidget):

    """
        ViewDetectorSettings
        Handles the settings of the detector.
        The view will trigger the detector which will detect outliers based on the final estimate data.
    """

    def __init__(self, parent=None):
        QWidget.__init__(self, parent=None)
        ui_filepath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ui', 'detector.ui'))
        loadUi(ui_filepath, self)

        self._controller = None

        # center widget depending on screen size
        desktop_widget = QApplication.desktop()
        screen_rect = desktop_widget.availableGeometry(self)
        self.move(screen_rect.center() - self.rect().center())

        self.cb_default.clicked.connect(self.toggle_esd)
        self.cb_esd.clicked.connect(self.toggle_default)
        self.btn_apply.clicked.connect(self.apply)
        self.btn_apply_close.clicked.connect(self.apply_close)

    def set_controller(self, controller):
        """
        Sets the connection to the controller
        :param controller: Controller
        :return:
        """
        self._controller = controller

    def init_values(self, detector):
        """
        Initialise the values of the view from the detector
        :param detector:
        :return:
        """
        self.dsb_m.setValue(detector.m)
        self.dsb_alpha.setValue(detector.alpha)
        self.dsb_k.setValue(detector.k)
        self.dsb_pre_filter.setValue(detector.pre_filter)
        self.cb_default.setChecked(detector.is_default_active)

    @Slot(bool, name='toggle_esd')
    def toggle_esd(self, clicked):
        """
        Toggles the checkbox of the ESD detector, only one detector can be active
        :param clicked: boolean
        :return:
        """
        if self.cb_default.isChecked():
            self.cb_esd.setChecked(False)
        if not self.cb_default.isChecked() and not self.cb_esd.isChecked():
            self.cb_esd.setChecked(True)

    @Slot(bool, name='toggle_default')
    def toggle_default(self, clicked):
        """
        Toggles the checkbox of the default detector, only one detector can be active
        :param clicked: boolean
        :return:
        """
        if self.cb_esd.isChecked():
            self.cb_default.setChecked(False)
        if not self.cb_esd.isChecked() and not self.cb_default.isChecked():
            self.cb_default.setChecked(True)

    @Slot(bool, name='apply')
    def apply(self, clicked):
        """
        Informs the controller to apply the current detector settings
        :param clicked: boolean
        :return:
        """
        self._controller.detector.update_and_run_detector(
            self.dsb_m.value(),
            self.dsb_alpha.value(),
            self.dsb_k.value(),
            self.dsb_pre_filter.value(),
            self.cb_default.isChecked(),
            self.cb_is_active.isChecked())

    @Slot(bool, name='apply_close')
    def apply_close(self, clicked):
        """
        Applies the current detector by informing the controller and closes the view.
        :param clicked: boolean
        :return:
        """
        self.apply(clicked)
        self.close()

