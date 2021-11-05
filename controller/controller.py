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

from PySide2.QtCore import QObject
from PySide2.QtCore import Slot
from core.messages import StateMsg
from controller.controller_stream import ControllerSocketStream
from controller.controller_detector import ControllerDetector
from controller.controller_filter import ControllerFilter
from controller.controller_scene import ControllerRenderScene
from controller.controller_options import ControllerOptions
import numpy as np
import logging
import time
from model.model import Model
from model.pixel_data import PixelData
from renderer.scene_renderer import SceneRenderer

from view.view_main.main_view import MainView


class Controller(QObject):

    """
        Handles the core functionality of the Brushing and Linking concept.
        Contains Sub-Controllers handling specific sub logic.
    """

    def __init__(self, model : Model, view : MainView, parent=None):
        QObject.__init__(self, parent=parent)

        self._model = model
        self._view = view

        # init sub controllers
        self._controller_detector = ControllerDetector(self, model, view)
        self._controller_filter = ControllerFilter(self, model, view)
        self._controller_stream = ControllerSocketStream(self, model, view)
        self._controller_scene = ControllerRenderScene(self, model, view)
        self._controller_options = ControllerOptions(self, model, view)

        # set connection between views and controller
        self._view.set_controller(self)

        # set connection between model and controller
        self._model.set_controller(self)
        self._model.set_callback(self.handle_state_msg)

        # initialize plugin buttons
        self._view.view_emca.add_plugins(self._model.plugins_handler.plugins)

    @property
    def detector(self) -> ControllerDetector:
        """
        Returns the sub-controller which handles the detector logic
        """
        return self._controller_detector

    @property
    def filter(self) -> ControllerFilter:
        """
        Returns the sub-controller which handles the filter logic
        """
        return self._controller_filter

    @property
    def stream(self) -> ControllerSocketStream:
        """
        Returns the sub-controller which handles the socket stream logic
        """
        return self._controller_stream

    @property
    def scene(self) -> ControllerRenderScene:
        """
        Returns the sub-controller which handles the 3d scene logic
        """
        return self._controller_scene

    @property
    def options(self) -> ControllerOptions:
        """
        Returns the sub-controller which handles the option logic
        """
        return self._controller_options

    def init_scene_renderer(self, scene_renderer : SceneRenderer):
        self._view.view_render_scene.init_scene_renderer(scene_renderer)
        # set scene renderer to plugins
        self._model.plugins_handler.set_scene_renderer(self._view.view_render_scene.scene_renderer)
        scene_renderer.set_controller(self)

    @Slot(tuple, name='handle_state_msg')
    def handle_state_msg(self, tpl : typing.Tuple[StateMsg, typing.Any]):
        """
        Handle current state, messages mostly received from thread,
        which listens on the socket pipeline for incoming messages
        :param tpl: (StateMsg, None or Datatype)
        :return:
        """
        msg = tpl[0]
        #logging.info('State: {}'.format(msg))
        if msg is StateMsg.DATA_INFO:
            self._view.view_render_info.update_render_info(tpl[1])
        elif msg is StateMsg.DATA_IMAGE:
            try:
                rendered_image_filepath = tpl[1]
                success = self._view.view_render_image.load_hdr_image(rendered_image_filepath)
                if success:
                    self._view.view_render_image.enable_view(True)
                    self._controller_options.save_options({'rendered_image_filepath': rendered_image_filepath})
            except Exception as e:
                self._view.view_popup.error_no_output_filepath(str(e))
        elif msg is StateMsg.DATA_PIXEL:
            start = time.time()
            pixel_data : PixelData = tpl[1]
            if len(pixel_data.dict_paths) == 0:
                self._view.view_popup.error_no_sample_idx_set("")
                return None
            self._view.view_render_scene.load_traced_paths(pixel_data)
            self._view.view_filter.init_data(pixel_data)
            self._view.enable_filter(True)
            self._view.view_pixel_data.enable_view(True)
            self._model.plugins_handler.init_data(pixel_data)
            if self._model.final_estimate_data.update_pixel_data(self._model.pixel_data):
                self._view.view_rgb_plot.plot_final_estimate(self._model.final_estimate_data)
                self._view.view_lum_plot.plot_final_estimate(self._model.final_estimate_data)
                self._view.view_depth_plot.plot_final_estimate(self._model.final_estimate_data)
            logging.info("process pixel data runtime: {}s".format(time.time() - start))
        elif msg is StateMsg.DATA_NOT_VALID:
            logging.error("Data is not valid!")
            # todo handle
        elif msg is StateMsg.SUPPORTED_PLUGINS:
            plugin_keys = tpl[1]
            for plugin_id in plugin_keys:
                if not self._model.plugins_handler.get_plugin_by_id(plugin_id):
                    logging.error('Plugin = {} is not supported by client'.format(plugin_id))
                else:
                    self._model.plugins_handler.enable_plugin_by_id(plugin_id, True)
        elif msg is StateMsg.UPDATE_PLUGIN:
            plugin = self._model.plugins_handler.get_plugin_by_id(tpl[1])
            if plugin:
                plugin.update_view()

        self._controller_scene.handle_state_msg(tpl)
        self._controller_stream.handle_state_msg(tpl)
        self._controller_filter.handle_state_msg(tpl)
        self._controller_detector.handle_state_msg(tpl)

    @Slot(bool, name='display_view_render_scene_options')
    def display_view_render_scene_options(self, clicked):
        if self._view.view_render_scene_options.isVisible():
            self._view.view_render_scene_options.activateWindow()
        else:
            self._view.view_render_scene_options.show()

    @Slot(bool, name='show_all_traced_paths')
    def show_all_traced_paths(self, enabled : bool):
        """
        Informs the renderer to show all traced paths
        """
        indices = np.array([])
        if enabled:
            indices = self._model.pixel_data.get_indices()
        self.update_path(indices, False)

    def update_render_info_sample_count(self, sample_count : int):
        """
        Updates the sample count value of render info
        """
        self._model.render_info.sample_count = sample_count

    def prepare_new_data(self):
        """
        Prepare view and model for new incoming pixel render data
        (In most cases clear views and data for new incoming render data)
        """
        self._view.view_render_scene.clear_traced_paths()
        self._view.view_pixel_data.clear()
        self._view.view_filter.clear()
        self._model.prepare_new_data()

    def update_path(self, indices : np.ndarray, add_item : bool):
        """
        Brushing and linking function,
        handles selected path indices,
        add_item informs if the next incoming index should be added to the current list or not
        """

        if add_item:
            # add item to current indices array and update
            new_indices = np.unique(np.append(self._model.current_path_indices, indices))
        else:
            # just replace the whole indices array
            new_indices = indices

        # mark scatter plot
        self._view.view_rgb_plot.update_path_indices(new_indices)
        self._view.view_lum_plot.update_path_indices(new_indices)
        self._view.view_depth_plot.update_path_indices(new_indices)
        # draw 3d paths
        self._view.view_render_scene.update_path_indices(new_indices)
        # update all plugins
        self._model.plugins_handler.update_path_indices(new_indices)
        # update render data view
        self._view.view_pixel_data.show_path_data(new_indices, self._model.pixel_data)
        # deselect path if no longer contained in the indices
        if self._model._current_path_index is not None and self._model._current_path_index not in new_indices:
            self.select_path(None)
        # select path if only one item
        if len(new_indices) == 1:
            self.select_path(new_indices[0])
        self._model.current_path_indices = new_indices

    def select_path(self, path_index : typing.Optional[int]):
        """
        Send path index update to all views
        """

        # reset intersection index when selecting a new path
        if self._model.current_path_index != path_index:
            self._model.current_intersection_index = None

        # this index must be an element of indices
        self._view.view_render_scene.select_path(path_index)
        # select path in render data view
        self._view.view_pixel_data.select_path(path_index)
        # send path index, update plugins
        self._model.plugins_handler.select_path(path_index)
        # save current path_index
        self._model.current_path_index = path_index

    def select_intersection(self, path_idx : typing.Optional[int], its_idx : typing.Optional[int]):
        """
        Send intersection index update to all views
        """

        # first select the path if a different path was chosen
        if self._model.current_path_index != path_idx:
            self.select_path(path_idx)

        # select intersection in 3D scene
        self._view.view_render_scene.select_intersection(path_idx, its_idx)
        # select intersection in render data view
        self._view.view_pixel_data.select_intersection(path_idx, its_idx)
        # send intersection index, update plugins
        self._model.plugins_handler.select_intersection(path_idx, its_idx)
        # save current intersection index
        self._model.current_intersection_index = its_idx

    def display_view(self):
        """
        Opens and shows the EMCA view
        """
        self._view.show()
        self._controller_options.load_pre_options()

    def close_app(self):
        """
        Closes all views and disconnected the client from the server (hard shut down)
        """
        # close all views and close connection
        self._controller_stream.close()
        self._model.plugins_handler.close()
        self._view.view_render_info.close()
        self._view.view_detector.close()
        self._view.view_connect.close()
        self._view.view_render_scene.close()
        self._view.view_render_scene_options.close()
        self._view.view_filter.close()
        self._view.close()
