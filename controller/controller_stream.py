from stream.socket_stream_client import SocketStreamClient
from core.messages import StateMsg
from PySide2.QtCore import Slot
import logging


class ControllerSocketStream(object):

    """
        ControllerSocketStream
        Handles the SocketStream with its request logic in combination with the view.
    """

    def __init__(self, parent, model, view):
        self._controller_main = parent
        self._view = view
        self._model = model

        # setup socket stream client
        port = self._view.view_connect.get_port()
        hostname = self._view.view_connect.get_hostname()
        # init socket stream with default values hostname:port
        self._sstream_client = SocketStreamClient(port, hostname)
        self._sstream_client.set_callback(parent.handle_state_msg)
        self._sstream_client.set_model(model)

    def handle_state_msg(self, tpl):
        """
        Handle current state, messages mostly received from thread,
        which listens on the socket pipeline for incoming messages
        :param tpl: (StateMsg, None or Datatype)
        :return:
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
    def disconnect_socket_stream(self, disconnected):
        """
        Disconnects the client from the server
        :param disconnected: boolean
        :return:
        """
        if self._sstream_client.is_connected():
            logging.info('Requesting Disconnect ...')
            self._sstream_client.request_disconnect()

    def connect_socket_stream(self, hostname, port):
        """
        Connects the client to the given hostname:port.
        Establishes the connection and starts the Thread,
        which is listening for incoming messages (backend)
        :param hostname:
        :param port:
        :return:
        """
        self._model.options_data.set_last_hostname_and_port(hostname, port)
        is_connected, error_msg = self._sstream_client.connect_socket_stream(hostname, port)
        if not is_connected and error_msg:
            self._view.view_popup.server_error(error_msg)
            return is_connected

        self._sstream_client.start()
        return is_connected

    def request_render_info(self):
        """
        Requests the render info data from the server interface
        :return:
        """
        self._sstream_client.request_render_info()

    def request_render_image(self):
        """
        Requests the render image from the server (sends start render call)
        :return:
        """
        sample_count = self._model.render_info.sample_count
        self._sstream_client.request_render_image(sample_count)

    def request_scene_data(self):
        """
        Requests the scene data
        :return:
        """
        self._sstream_client.request_scene_data()

    def request_render_data(self, pixel):
        """
        Sends the selected pixel position to the server
        and requests the render data of this pixel
        :param pixel: (x,y) pixel position
        :return:
        """

        # check if client is connected, if not inform user
        if not self._sstream_client.is_connected():
            self._view.view_popup.error_not_connected("")
            return None

        # is called every time if new pixel data is requested
        self._controller_main.prepare_new_data()

        pixmap = self._view.view_render_image.pixmap
        pixel_icon = self._view.pixel_icon
        pixel_icon.set_pixel(pixmap, pixel)
        sample_count = self._model.render_info.sample_count
        self._view.view_emca.update_pixel_hist(pixel_icon)
        self._sstream_client.request_render_data(pixel, sample_count)

    def request_plugin(self, flag):
        """
        Handles btn (request) interaction from plugin window,
        Gets the corresponding plugin and sends plugin id request to server
        :param flag: plugin_id
        :return:
        """
        if self._sstream_client.is_connected():
            plugins_handler = self._model.plugins_handler
            plugins_handler.request_plugin(flag, self._sstream_client.stream)

    def close(self):
        """
        Closes the connection to the server
        :return:
        """
        # handle disconnect from server if socket connection is still active
        if self._sstream_client.is_connected():
            self._sstream_client.close()
