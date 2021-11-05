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

import numpy as np
from PySide2.QtWidgets import QWidget
from PySide2.QtWidgets import QPushButton
from PySide2.QtWidgets import QVBoxLayout
from PySide2.QtWidgets import QHBoxLayout
from PySide2.QtWidgets import QFrame
from PySide2.QtCore import Slot
import logging
import typing
from core.plugin import Plugin

from model.pixel_data import PixelData

from typing import TYPE_CHECKING

from renderer.scene_renderer import SceneRenderer
from stream.stream import Stream
if TYPE_CHECKING:
    from controller.controller import Controller
else:
    from typing import Any as Controller


class PluginsViewContainer(QWidget):

    """
        PluginsViewContainer
        QtWidget that inserts the plugin widget.
        Represents a container with Request and Close button to request plugin data or close the window
        Besides holds the Plugin button which is used to open the Plugin view.
    """

    def __init__(self, plugin : Plugin):
        QWidget.__init__(self)

        self.setWindowTitle("Plugin {}".format(plugin.name))

        self._controller = None
        self._plugin = plugin
        self._plugin.send_select_path = self.send_select_path
        self._plugin.send_select_intersection = self.send_select_intersection
        self._plugin.send_update_path_indices = self.send_update_path_indices
        self._btn = QPushButton(plugin.name)
        self._btn.setEnabled(False)
        self._btn.clicked.connect(self.display_plugin)

        self._btn_request = QPushButton("Request")
        self._btn_request.setEnabled(False)
        self._btn_request.clicked.connect(self.request_plugin)

        self._btn_close = QPushButton("Close")
        self._btn_close.clicked.connect(self.close)

        layout = QVBoxLayout(self)
        layout.addWidget(self._plugin)

        hline = QFrame()
        hline.setFrameShape(QFrame.HLine)
        hline.setFrameShadow(QFrame.Sunken)
        layout.addWidget(hline)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self._btn_request)
        btn_layout.addWidget(self._btn_close)
        layout.addLayout(btn_layout)

    @property
    def plugin(self) -> Plugin:
        """
        Returns the Plugin
        """
        return self._plugin

    def send_update_path_indices(self, path_indices : np.ndarray, add_item : bool):
        """
        Calls the controller update_path function.
        Update the path indices of all views
        """
        self._controller.update_path(path_indices, add_item)

    def send_select_path(self, path_idx : typing.Optional[int]):
        """
        Calls the controller select_path function.
        Updates the current selected path
        """
        self._controller.select_path(path_idx)

    def send_select_intersection(self, path_idx : typing.Optional[int], its_idx : typing.Optional[int]):
        """
        Calls the controller select_intersection function.
        Updates the current selected intersection
        """
        self._controller.select_intersection(path_idx, its_idx)

    def select_path(self, path_idx : typing.Optional[int]):
        """
        Calls the Plugin select_path function
        Informs the Plugin about the current selected path
        """
        self._plugin.select_path(path_idx)

    def select_intersection(self, path_idx : typing.Optional[int], its_idx : typing.Optional[int]):
        """
        Calls the Plugin select_intersection function.
        Informs the Plugin about the current selected intersection
        """
        self._plugin.select_intersection(path_idx, its_idx)
        # automatically request new data for the selected intersection if the tool is visible
        if self.isVisible():
            self._controller.stream.request_plugin(self._plugin.flag)

    def serialize(self, stream : Stream):
        """
        Calls the Plugin serialize function.
        Data from the Plugin will be send to the server.
        """
        self._plugin.serialize(stream)

    def get_plugin_btn(self) -> QPushButton:
        """
        Returns the Plugin QButton
        Used to visualize Plugin button with name within view
        """
        return self._btn

    def enable_plugin_btn(self, enable : bool):
        """
        Enables or disables the Plugin button
        """
        self._btn.setEnabled(enable)
        self._btn_request.setEnabled(enable)

    def set_controller(self, controller : Controller):
        """
        Set the controller
        """
        self._controller = controller

    def set_scene_renderer(self, scene_renderer : SceneRenderer):
        """
        Set the renderer
        """
        self._plugin.scene_renderer = scene_renderer

    def init_pixel_data(self, pixel_data : PixelData):
        """
        Calls the Plugin init_pixel_data function.
        Render data will be set within Plugins,
        to provide them with the current render data set from the selected pixel
        """
        self._plugin.init_pixel_data(pixel_data)

    def prepare_new_data(self):
        """
        Calls the Plugin prepare_new_data function.
        Is called if a new pixel is selected in order to gather new pixel information
        :return:
        """
        self._plugin.prepare_new_data()

    def update_path_indices(self, indices : np.ndarray):
        """
        Calls the Plugin update_path_indices function.
        Informs the Plugin about all selected paths
        :param indices: np.array[(path_index),...]
        :return:
        """
        self._plugin.update_path_indices(indices)

    def update_view(self):
        """
        Calls the Plugin update_view function.
        This function is called after the deserialize function of the Plugin is finished
        """
        self._plugin.update_view()

    @Slot(bool, name='request_plugin')
    def request_plugin(self, clicked : bool):
        """
        Calls the controller request_tool function.
        If the Request button within the tool view is clicked,
        a request with the tool_id will be send to the server.
        """
        self._controller.stream.request_plugin(self._plugin.flag)

    @Slot(bool, name='display_tool')
    def display_plugin(self, clicked : bool):
        """
        Opens and displays the tool window,
        if the view is already opened but in not active in the background,
        this functions sets the tool window back active and brings it to the foreground.
        """
        if self.isVisible():
            self.activateWindow()
        else:
            self.show()
            self._controller.stream.request_plugin(self._plugin.flag)
