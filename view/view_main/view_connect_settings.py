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
from core.pyside2_uic import loadUi
from PySide2.QtCore import Qt
from PySide2.QtCore import Slot
from PySide2.QtWidgets import QWidget
from PySide2.QtWidgets import QApplication
import os
import logging

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from controller.controller import Controller
else:
    from typing import Any as Controller


class ViewConnectSettings(QWidget):

    """
        ViewConnectSettings
        Handles the connect settings view
    """

    def __init__(self, parent=None):
        QWidget.__init__(self, parent=None)
        ui_filepath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ui', 'connect.ui'))
        loadUi(ui_filepath, self)

        self._controller = None

        # center widget depending on screen size
        desktop_widget = QApplication.desktop()
        screen_rect = desktop_widget.availableGeometry(self)
        self.move(screen_rect.center() - self.rect().center())

        self.btnConnect.clicked.connect(self.btn_connect)

    def set_controller(self, controller : Controller):
        """
        Set the connection to the controller
        """
        self._controller = controller

    @property
    def hostname(self) -> str:
        """
        Returns the current set hostname
        """
        return self.leHostname.text()

    @hostname.setter
    def hostname(self, hostname : str):
        """
        Set the hostname
        """
        self.leHostname.setText(hostname)

    @property
    def port(self) -> int:
        """
        Returns the current set port
        """
        return int(self.lePort.text())

    @port.setter
    def port(self, port : int):
        """
        Set the port
        """
        self.lePort.setText(str(port))

    def keyPressEvent(self, event : QKeyEvent):
        """
        Handles key press event. If the enter button is clicked the connect button is triggered
        """
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.btn_connect(True)

    @Slot(bool, name='connect')
    def btn_connect(self, clicked : bool):
        """
        Informs the controller to connect to the given hostname and port.
        Closes the view afterwards.
        """
        logging.info('Clicked connect btn')

        if self._controller.stream.connect_socket_stream(self.hostname, self.port):
            self.close()

