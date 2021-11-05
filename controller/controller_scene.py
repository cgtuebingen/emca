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
from PySide2.QtCore import Slot
from core.messages import StateMsg
from model.model import Model
from view.view_main.main_view import MainView

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from controller.controller import Controller
else:
    from typing import Any as Controller

class ControllerRenderScene(object):

    """
        ControllerRenderScene
        Handles the interaction and logic with the RenderScene and RenderSceneOptions View.
    """

    def __init__(self, parent : Controller, model : Model, view : MainView):
        self._controller_main = parent
        self._model = model
        self._view = view

    def handle_state_msg(self, tpl : typing.Tuple[StateMsg, typing.Any]):
        """
        Handle current state, messages mostly received from thread,
        which listens on the socket pipeline for incoming messages
        """
        msg = tpl[0]
        if msg is StateMsg.DATA_INFO:
            self._controller_main.stream.request_camera_data()
            # automatically request scene data once render info is available
            if self._model.options_data.auto_scene_load:
                self._controller_main.stream.request_scene_data()
        elif msg is StateMsg.DATA_CAMERA:
            self._view.view_render_scene.scene_renderer.load_camera(tpl[1])
        elif msg is StateMsg.DATA_MESH:
            self._view.view_render_scene.scene_renderer.load_mesh(tpl[1])
        elif msg is StateMsg.DATA_SCENE_INFO:
            self._view.view_render_scene.scene_renderer.process_scene_info(tpl[1])

    @Slot(bool)
    def reset_camera_position(self, clicked : bool):
        """
        Reset the camera position to its default origin position
        """
        self._view.view_render_scene.scene_renderer.reset_camera_position()

    def reset_path_options(self):
        self._view.view_render_scene.scene_renderer.reset_path_options()

    def reset_scene_options(self):
        self._view.view_render_scene.scene_renderer.reset_scene_options()

    def reset_heatmap_options(self):
        self._view.view_render_scene.scene_renderer.reset_heatmap_options()

    def update_path_options(self, path_options : typing.Dict[str, typing.Any]):
        self._view.view_render_scene.scene_renderer.path_options = path_options
        self._view.view_render_scene_options.load_path_options(path_options)

    def update_scene_options(self, scene_options : typing.Dict[str, typing.Any]):
        self._view.view_render_scene.scene_renderer.scene_options = scene_options
        self._view.view_render_scene_options.load_scene_options(scene_options)

    def update_heatmap_options(self, heatmap_options : typing.Dict[str, typing.Any]):
        self._view.view_render_scene.scene_renderer.heatmap_options = heatmap_options
        self._view.view_render_scene_options.load_heatmap_options(heatmap_options)
