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
from PySide2.QtWidgets import QWidget
from PySide2.QtWidgets import QApplication
import os
import logging


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

        try:
            self._hostname = self.leHostname.text()
            self._port = int(self.lePort.text())
        except ValueError as e:
            logging.error(e)
            raise ValueError(e)

        self.btnConnect.clicked.connect(self.btn_connect)

    def set_controller(self, controller):
        """
        Set the connection to the controller
        :param controller: Controller
        :return:
        """
        self._controller = controller

    def set_hostname(self, hostname):
        """
        Set the hostname
        :param hostname: str
        """
        self._hostname = hostname
        self.leHostname.setText(hostname)

    def get_hostname(self):
        """
        Returns the current set hostname
        :return: str
        """
        return self.leHostname.text()

    def set_port(self, port):
        """
        Set the port
        :param port: str|int
        """
        self._port = port
        self.lePort.setText(str(port))

    def get_port(self):
        """
        Returns the current set port
        :return: str
        """
        return self.lePort.text()

    def set_hostname_and_port(self, hostname, port):
        """
        Sets hostname and port
        :param hostname: str
        :param port: str|int
        """
        self.set_hostname(hostname)
        self.set_port(port)

    def keyPressEvent(self, event):
        """
        Handles key press event. If the enter button is clicked the connect button is triggered
        :param event:
        :return:
        """
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.btn_connect(True)

    @Slot(bool, name='connect')
    def btn_connect(self, clicked):
        """
        Informs the controller to connect to the given hostname and port.
        Closes the view afterwards.
        :param clicked: boolean
        :return:
        """
        logging.info('Clicked connect btn, show connect view')
        try:
            self._hostname = self.leHostname.text()
            self._port = int(self.lePort.text())
        except ValueError as e:
            logging.error(e)
            return None

        if self._controller.stream.connect_socket_stream(self._hostname, self._port):
            self.close()

