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
from PySide2.QtCore import Qt
from PySide2.QtCore import Slot
from PySide2.QtWidgets import QButtonGroup, QWidget
from PySide2.QtWidgets import QApplication
import os
import logging


class ViewOptions(QWidget):

    """
        ViewOptions
        Handles options of EMCA
    """

    def __init__(self, parent=None):
        QWidget.__init__(self, parent=None)
        ui_filepath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ui', 'options.ui'))
        loadUi(ui_filepath, self)

        self._controller = None

        # center widget depending on screen size
        desktop_widget = QApplication.desktop()
        screen_rect = desktop_widget.availableGeometry(self)
        self.move(screen_rect.center() - self.rect().center())

        self._theme_buttons = QButtonGroup()
        self._theme_buttons.addButton(self.cbDarkTheme)
        self._theme_buttons.addButton(self.cbLightTheme)

        self.btnSave.clicked.connect(self.btn_save)
        self.btnClose.clicked.connect(self.btn_close)

    def set_controller(self, controller):
        """
        Set the connection to the controller
        :param controller: Controller
        :return:
        """
        self._controller = controller

    def enable_dark_theme(self, enabled):
        self.cbDarkTheme.setChecked(enabled)

    def enable_light_theme(self, enabled):
        self.cbLightTheme.setChecked(enabled)

    def get_theme(self):
        theme = 'dark'
        if self.cbDarkTheme.isChecked():
            theme = 'dark'
        elif self.cbLightTheme.isChecked():
            theme = 'light'
        return theme

    def get_auto_connect(self):
        return self.cbAutoConnect.isChecked()

    def get_auto_scene_load(self):
        return self.cbAutoSceneLoad.isChecked()

    def get_auto_image_load(self):
        return self.cbAutoLoadImage.isChecked()

    def set_auto_connect(self, enabled):
        self.cbAutoConnect.setChecked(enabled)

    def set_auto_scene_load(self, enabled):
        self.cbAutoSceneLoad.setChecked(enabled)

    def set_auto_image_load(self, enabled):
        self.cbAutoLoadImage.setChecked(enabled)

    @Slot(bool, name='btn_save')
    def btn_save(self, clicked):
        options_dict = {'theme': self.get_theme(),
                        'auto_connect': self.get_auto_connect(),
                        'auto_scene_load': self.get_auto_scene_load(),
                        'auto_rendered_image_load': self.get_auto_image_load()}
        self._controller.options.save_options(options_dict)

    @Slot(bool, name='btn_close')
    def btn_close(self, clicked):
        self.close()
