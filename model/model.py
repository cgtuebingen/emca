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

from stream.stream import Stream
from plugins.plugins_handler import PluginsHandler
from model.options_data import OptionsConfig
from model.render_info import RenderInfo
from model.camera_data import CameraData
from model.mesh_data import ShapeData
from model.pixel_data import PixelData
from model.contribution_data import SampleContributionData
from PySide2.QtCore import Signal
from PySide2.QtCore import QObject
from core.messages import StateMsg
from filter.filter import Filter
from detector.detector import Detector
import numpy as np
import time
import logging

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from controller.controller import Controller
else:
    from typing import Any as Controller


class Model(QObject):

    """
        Dataset
        Represents the Model of the Model-View-Controller.
        Stores and handles all data files.
        Therefore deserializes the data from the socket stream.
    """

    sendStateMsgSig = Signal(tuple)

    def __init__(self):
        QObject.__init__(self, parent=None)
        self._options = OptionsConfig()
        self._plugins_handler = PluginsHandler()

        self._render_info = RenderInfo()
        self._camera_data = CameraData()
        self._mesh_data = ShapeData()
        self._pixel_data = PixelData()
        self._final_estimate_data = SampleContributionData()

        # Model also holds refs to filter and detector
        self._filter = Filter()
        self._detector = Detector()

        # model keeps track of current selected path indices
        self._current_path_indices = np.array([], dtype=np.int32)
        self._current_path_index = None
        self._current_intersection_index = None

        self._server_side_supported_plugins = []
        self._controller = None

    def set_callback(self, callback):
        """
        Set / Connect Qt signal callback to controllers msg handler
        """
        self.sendStateMsgSig.connect(callback)

    def set_controller(self, controller : Controller):
        """
        Set the connection to the controller
        """
        self._controller = controller
        self._plugins_handler.set_controller(controller)

    @property
    def filter(self) -> Filter:
        return self._filter

    @property
    def detector(self) -> Detector:
        return self._detector

    @property
    def current_path_indices(self) -> np.ndarray:
        return self._current_path_indices

    @current_path_indices.setter
    def current_path_indices(self, indices : np.ndarray):
        self._current_path_indices = indices

    @property
    def current_path_index(self) -> typing.Optional[int]:
        return self._current_path_index

    @current_path_index.setter
    def current_path_index(self, path_index : typing.Optional[int]):
        self._current_path_index = path_index

    @property
    def current_intersection_index(self) -> typing.Optional[int]:
        return self._current_intersection_index

    @current_intersection_index.setter
    def current_intersection_index(self, intersection_index : typing.Optional[int]):
        self._current_intersection_index = intersection_index

    @property
    def server_side_supported_plugins(self) -> typing.List[int]:
        return self._server_side_supported_plugins

    @property
    def plugins_handler(self) -> PluginsHandler:
        """
        Returns the Plugins Handler
        :return:
        """
        return self._plugins_handler

    @property
    def render_info(self) -> RenderInfo:
        """
        Returns the Render Info
        :return:
        """
        return self._render_info

    @property
    def camera_data(self) -> CameraData:
        """
        Returns the Camera Data
        :return:
        """
        return self._camera_data

    @property
    def mesh_data(self) -> ShapeData:
        """
        Returns the Mesh Data
        """
        return self._mesh_data

    @property
    def pixel_data(self) -> PixelData:
        """
        Returns the gathered information of one pixel
        """
        return self._pixel_data

    @property
    def final_estimate_data(self) -> SampleContributionData:
        """
        Returns the Final Estimate Plot Data
        """
        return self._final_estimate_data

    @property
    def options_data(self) -> OptionsConfig:
        """
        Returns the options loaded from .ini file
        """
        return self._options

    @render_info.setter
    def render_info(self, new_render_info : RenderInfo):
        """
        Set function for Render Info data
        """
        self._render_info = new_render_info

    @camera_data.setter
    def camera_data(self, new_camera_data : CameraData):
        """
        Set function for Camera data
        """
        self._camera_data = new_camera_data

    @mesh_data.setter
    def mesh_data(self, new_mesh_data : ShapeData):
        """
        Set function for Mesh data
        """
        self._mesh_data = new_mesh_data

    @pixel_data.setter
    def pixel_data(self, new_pixel_data : PixelData):
        """
        Set function for Render data
        """
        self._pixel_data = new_pixel_data

    def prepare_new_data(self):
        """
        Resets the current selected path|intersection|indices and
        calls the PluginsHandler prepare_new_data function.
        """
        self._plugins_handler.prepare_new_data()
        self._current_path_indices = np.array([], dtype=np.int32)
        self._current_path_index = None
        self._current_intersection_index = None

    def deserialize_supported_plugins(self, stream : Stream):
        """
        Deserialize list of supported plugin keys
        """
        #start = time.time()
        self._server_side_supported_plugins.clear()
        msg_len = stream.read_uint()
        for i in range(0, msg_len):
            self._server_side_supported_plugins.append(stream.read_short())
        logging.info('Supported Plugins = {}'.format(self._server_side_supported_plugins))
        #logging.info('serialize supported plugin keys in: {:.3}s'.format(time.time() - start))
        self.sendStateMsgSig.emit((StateMsg.SUPPORTED_PLUGINS, self._server_side_supported_plugins))

    def serialize_render_info(self, stream : Stream):
        """
        Serialize the Render Info data and informs the controller about it
        Sends data to the server
        """
        #start = time.time()
        self._render_info.serialize(stream)
        #logging.info('serialize render info in: {:.3}s'.format(time.time() - start))

    def deserialize_render_info(self, stream : Stream):
        """
        Deserialize the Render Info data and informs the controller about it
        Reads data from the socket stream
        """
        start = time.time()
        self._render_info.deserialize(stream)
        #logging.info('deserialize render info in: {:.3}s'.format(time.time() - start))
        self.sendStateMsgSig.emit((StateMsg.DATA_INFO, self._render_info))

    def deserialize_camera(self, stream : Stream):
        """
        Deserialize the Camera data and informs the controller about it
        """
        #start = time.time()
        self._camera_data.deserialize(stream)
        #logging.info('deserialize camera data in: {:.3}s'.format(time.time() - start))
        self.sendStateMsgSig.emit((StateMsg.DATA_CAMERA, self._camera_data))

    def deserialize_scene_objects(self, stream : Stream):
        """
        Deserialize Mesh data (3D Scene objects) and informs the controller about it
        """
        start = time.time()
        has_heatmap_data = stream.read_bool()

        # TODO: make scene info a proper class
        scene_info = {}
        scene_info['has_heatmap'] = has_heatmap_data

        if has_heatmap_data:
            scene_info['colormap'] = stream.read_string()
            scene_info['show_colorbar'] = stream.read_bool()
            scene_info['colorbar_label'] = stream.read_string()

        self.sendStateMsgSig.emit((StateMsg.DATA_SCENE_INFO, scene_info))

        num_meshes = stream.read_uint()
        for i in range(num_meshes):
            #start = time.time()
            self._mesh_data.deserialize(stream)
            # add the meshes to the secene as they are received - could also add all at once, but that is not quite as interactive
            self.sendStateMsgSig.emit((StateMsg.DATA_MESH, self._mesh_data.meshes[-1]))

        #FIXME: make this a bit cleaner, don't piggy-back on the scene info function
        if has_heatmap_data: # send a signal to update the max value
            self.sendStateMsgSig.emit((StateMsg.DATA_SCENE_INFO, None))

        logging.info('loaded scene with {} meshes in: {:.3}s'.format(num_meshes, time.time() - start))

    def deserialize_pixel_data(self, stream : Stream):
        """
        Deserialize Pixel data and informs the controller about it
        """
        #start = time.time()
        self._pixel_data.deserialize(stream)
        #logging.info('deserialize render data in: {:.3}s'.format(time.time() - start))
        self.sendStateMsgSig.emit((StateMsg.DATA_PIXEL, self._pixel_data))
