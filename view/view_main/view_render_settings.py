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

from PySide2.QtGui import QKeyEvent
from model.render_info import RenderInfo
from core.pyside2_uic import loadUi
from PySide2.QtWidgets import QWidget
from PySide2.QtWidgets import QApplication
from PySide2.QtCore import Slot
from PySide2.QtCore import Qt
import os

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from controller.controller import Controller
else:
    from typing import Any as Controller


class ViewRenderSettings(QWidget):

    """
        ViewRenderSettings
        Handles general information about the scene
    """

    def __init__(self, parent=None):
        QWidget.__init__(self, parent=None)
        ui_filepath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ui', 'render_info.ui'))
        loadUi(ui_filepath, self)

        self._controller = None

        # center widget depending on screen size
        desktop_widget = QApplication.desktop()
        screen_rect = desktop_widget.availableGeometry(self)
        self.move(screen_rect.center() - self.rect().center())

        self.btnClose.clicked.connect(self.close)

    def set_controller(self, controller : Controller):
        """
        Sets the connection to the controller
        :param controller: Controller
        :return:
        """
        self._controller = controller
        self.sbSampleCount.valueChanged.connect(self.sb_update_sample_count)

    def update_render_info(self, render_info : RenderInfo):
        """
        Updates the view info with new render information
        :param render_info: RenderInfo from model
        :return:
        """
        self.labelRendererName.setText(render_info.renderer_name)
        self.labelSceneName.setText(render_info.scene_name)
        self.sbSampleCount.setValue(render_info.sample_count)

    def keyPressEvent(self, event : QKeyEvent):
        """
        Handles key press event, if enter is pressed the submit button will be triggered
        """
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.btn_submit(True)

    @Slot(int, name='sb_update_sample_count')
    def sb_update_sample_count(self, value : int):
        """
        Informs the controller to update the sample count of render info
        """
        self._controller.update_render_info_sample_count(value)
