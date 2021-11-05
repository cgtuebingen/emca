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
from model.model import Model
from stream.socket_stream_client import SocketStreamClient
from core.messages import StateMsg
from PySide2.QtCore import QPoint, Slot
import logging
from view.view_main.pixel_icon import PixelIcon

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from controller.controller import Controller
else:
    from typing import Any as Controller

from view.view_main.main_view import MainView


class ControllerSocketStream(object):

    """
        ControllerSocketStream
        Handles the SocketStream with its request logic in combination with the view.
    """

    def __init__(self, parent : Controller, model : Model, view : MainView):
        self._controller_main = parent
        self._view = view
        self._model = model

        # setup socket stream client
        hostname = self._view.view_connect.hostname
        port = self._view.view_connect.port
        # init socket stream with default values hostname:port
        self._sstream_client = SocketStreamClient(hostname, port)
        self._sstream_client.set_callback(parent.handle_state_msg)
        self._sstream_client.set_model(model)

    def handle_state_msg(self, tpl : typing.Tuple[StateMsg, typing.Any]):
        """
        Handle current state, messages mostly received from thread,
        which listens on the socket pipeline for incoming messages
        """
        msg = tpl[0]
        if msg is StateMsg.CONNECT:
            self._sstream_client.request_render_info()
            self._view.view_emca.enable_view(True)
            self._view.view_render_scene.enable_view(True)
            self._model.plugins_handler.enable_plugins(True)
        elif msg is StateMsg.DISCONNECT:
            self._view.view_emca.enable_view(False)
            self._view.view_render_scene.enable_view(False)
            self._model.plugins_handler.enable_plugins(False)
            for plugin_id in self._model.server_side_supported_plugins:
                self._model.plugins_handler.enable_plugin_by_id(plugin_id, False)
        elif msg is StateMsg.QUIT:
            self._sstream_client.wait()

    @Slot(bool, name='disconnect_socket_stream')
    def disconnect_socket_stream(self, disconnected : bool):
        """
        Disconnects the client from the server
        """
        if self._sstream_client.is_connected():
            logging.info('Requesting Disconnect ...')
            self._sstream_client.request_disconnect()

    def connect_socket_stream(self, hostname : str, port : int) -> bool:
        """
        Connects the client to the given hostname:port.
        Establishes the connection and starts the Thread,
        which is listening for incoming messages (backend)
        """
        self._model.options_data.last_hostname = hostname
        self._model.options_data.last_port = port
        is_connected, error_msg = self._sstream_client.connect_socket_stream(hostname, port)
        if not is_connected and error_msg:
            self._view.view_popup.server_error(error_msg)
            return is_connected

        self._sstream_client.start()
        return is_connected

    def request_render_info(self):
        """
        Requests the render info data from the server interface
        """
        self._sstream_client.request_render_info()

    def request_render_image(self):
        """
        Requests the render image from the server (sends start render call)
        """
        sample_count = self._model.render_info.sample_count
        self._sstream_client.request_render_image(sample_count)

    def request_camera_data(self):
        """
        Requests the camera data
        """
        self._sstream_client.request_camera_data()

    def request_scene_data(self):
        """
        Requests the scene data
        """
        self._sstream_client.request_scene_data()

    def request_render_pixel(self, pixel : QPoint):
        """
        Sends the selected pixel position to the server
        and requests the render data of this pixel
        """

        # check if client is connected, if not inform user
        if not self._sstream_client.is_connected():
            self._view.view_popup.error_not_connected("")
            return None

        # is called every time if new pixel data is requested
        self._controller_main.prepare_new_data()

        hdr_image = self._view.view_render_image._graphics_view.hdr_image
        pixel_icon = PixelIcon(hdr_image.get_pixel_color(pixel), pixel)
        sample_count = self._model.render_info.sample_count
        self._view.view_emca.update_pixel_hist(pixel_icon)
        self._sstream_client.request_render_pixel(pixel, sample_count)

    def request_plugin(self, plugin_id : int):
        """
        Handles btn (request) interaction from plugin window,
        Gets the corresponding plugin and sends plugin id request to server
        """
        if self._sstream_client.is_connected():
            plugins_handler = self._model.plugins_handler
            plugins_handler.request_plugin(plugin_id, self._sstream_client.stream)

    def close(self):
        """
        Closes the connection to the server
        """
        # handle disconnect from server if socket connection is still active
        if self._sstream_client.is_connected():
            self._sstream_client.close()
