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

from PySide2.QtCore import QObject
from PySide2.QtWidgets import QMessageBox


class PopupMessages(QObject):

    """
        PopupMessages
        Handles all popup messages. Used to inform the user with popups about error messages.
    """

    def __init__(self, parent=None):
        QObject.__init__(self, parent=parent)
        self._parent = parent
        self._msgBox = QMessageBox()

    def server_connection_broke(self, msg):
        """
        Popup error message if the socket connection broke
        :param msg: string
        :return:
        """
        self._msgBox.setIcon(QMessageBox.Warning)
        self._msgBox.setWindowTitle("Connection Error")
        self._msgBox.setText("Server connection broke")
        self._msgBox.setInformativeText("Restart Server and reconnect client")
        self._msgBox.setDetailedText(msg)
        self._msgBox.setStandardButtons(QMessageBox.Ok)
        self._msgBox.exec_()

    def server_error(self, msg):
        """
        Popup error message if something went wrong with the server
        :param msg: string
        :return:
        """
        self._msgBox.setIcon(QMessageBox.Information)
        self._msgBox.setWindowTitle("Connection Error")
        self._msgBox.setText("Server error")
        self._msgBox.setInformativeText("Can not connect to server. Start server or check for right port and hostname.")
        self._msgBox.setDetailedText(msg)
        self._msgBox.setStandardButtons(QMessageBox.Ok)
        self._msgBox.exec_()

    def error_not_connected(self, msg):
        """
        Popup error message if no connection is esablished
        :param msg: string
        :return:
        """
        self._msgBox.setIcon(QMessageBox.Information)
        self._msgBox.setWindowTitle("Connection Error")
        self._msgBox.setText("Diconnected")
        self._msgBox.setInformativeText("You are currently not connected to any server")
        self._msgBox.setDetailedText(msg)
        self._msgBox.setStandardButtons(QMessageBox.Ok)
        self._msgBox.exec_()

    def error_no_sample_idx_set(self, msg):
        """
        Popup error message if no sample index was set on server side
        :param msg: string
        :return:
        """
        self._msgBox.setIcon(QMessageBox.Information)
        self._msgBox.setWindowTitle("Index error")
        self._msgBox.setText("Sample index error")
        self._msgBox.setInformativeText("Sample index was not set on server side")
        self._msgBox.setDetailedText(msg)
        self._msgBox.setStandardButtons(QMessageBox.Ok)
        self._msgBox.exec_()

    def error_no_depth_idx_set(self, msg):
        """
        Popup error message if no depth index was set on server side
        :param msg:
        :return:
        """
        self._msgBox.setIcon(QMessageBox.Information)
        self._msgBox.setWindowTitle("Index error")
        self._msgBox.setText("Path depth index error")
        self._msgBox.setInformativeText("Path depth index was not set on server side")
        self._msgBox.setDetailedText(msg)
        self._msgBox.setStandardButtons(QMessageBox.Ok)
        self._msgBox.exec_()

    def error_no_final_estimate_data(self, msg):
        """
        Popup error message if no final estimate data was set on server side
        :param msg:
        :return:
        """
        self._msgBox.setIcon(QMessageBox.Information)
        self._msgBox.setWindowTitle("Missing data")
        self._msgBox.setText("Missing final estimate values")
        self._msgBox.setInformativeText("No final estimate data available to run outlier detection")
        self._msgBox.setDetailedText(msg)
        self._msgBox.setStandardButtons(QMessageBox.Ok)
        self._msgBox.exec_()

    def error_no_output_filepath(self, msg):
        self._msgBox.setIcon(QMessageBox.Information)
        self._msgBox.setWindowTitle("Missing rendered image")
        self._msgBox.setText("No render image output path is set")
        self._msgBox.setInformativeText("Please set a valid path to the rendered image in the render image message")
        self._msgBox.setDetailedText(msg)
        self._msgBox.setStandardButtons(QMessageBox.Ok)
        self._msgBox.exec_()

    def error_saving_options(self, msg):
        self._msgBox.setIcon(QMessageBox.Warning)
        self._msgBox.setWindowTitle("Error Saving EMCA Options")
        self._msgBox.setText("Saving EMCA options was not possible")
        self._msgBox.setInformativeText("Internal error check error message")
        self._msgBox.setDetailedText(msg)
        self._msgBox.setStandardButtons(QMessageBox.Ok)
        self._msgBox.exec_()

    def error_on_loading_pre_saved_image(self, msg):
        self._msgBox.setIcon(QMessageBox.Warning)
        self._msgBox.setWindowTitle("Error Loading Image")
        self._msgBox.setText("Loading pre saved image was not possible")
        self._msgBox.setInformativeText("This may happen if the filename or location of the pre-saved image has changed. Or an image was never loaded before")
        self._msgBox.setDetailedText(msg)
        self._msgBox.setStandardButtons(QMessageBox.Ok)
        self._msgBox.exec_()

    def restart_application_info(self, msg):
        self._msgBox.setIcon(QMessageBox.Information)
        self._msgBox.setWindowTitle("Theme Change")
        self._msgBox.setText("Application needs a whole restart for changing the theme")
        self._msgBox.setInformativeText("All current data will be lost due to this application restart")
        self._msgBox.setDetailedText(msg)
        self._msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        return self._msgBox.exec_()

    def error_outlier_detector_no_outliers_detected(self, msg):
        self._msgBox.setIcon(QMessageBox.Warning)
        self._msgBox.setWindowTitle("No Outliers Detected")
        self._msgBox.setText("No outliers detected. Try to adapt your outlier detector settings.")
        self._msgBox.setInformativeText("Outlier algorithm could not find any outliers in given data")
        self._msgBox.setDetailedText(msg)
        self._msgBox.setStandardButtons(QMessageBox.Ok)
        self._msgBox.exec_()

    def error_detector_not_enabled(self, msg):
        self._msgBox.setIcon(QMessageBox.Information)
        self._msgBox.setWindowTitle("Error Outlier Detector is not enabled yet")
        self._msgBox.setText("Checkbox for Outlier Detection is not checked.")
        self._msgBox.setInformativeText("Select and enable the checkbox for outlier detections.")
        self._msgBox.setDetailedText(msg)
        self._msgBox.setStandardButtons(QMessageBox.Ok)
        self._msgBox.exec_()




