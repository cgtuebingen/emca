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
import numpy as np
from model.pixel_data import PixelData
from renderer.scene_renderer import SceneRenderer
from PySide2.QtWidgets import QWidget
from core.pyside2_uic import loadUi
import os
import logging

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from controller.controller import Controller
else:
    from typing import Any as Controller


class ViewRenderScene(QWidget):

    """
        ViewRenderScene
        Handles the three-dimensional visualization.
    """

    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        ui_filepath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ui', 'render_scene.ui'))
        loadUi(ui_filepath, self)

        self._controller = None
        self._scene_renderer = None

    def set_controller(self, controller : Controller):
        """
        Sets the connection to the controller
        """
        self._controller = controller
        self.btnSceneOptions.clicked.connect(controller.display_view_render_scene_options)
        self.btnLoadScene.clicked.connect(controller.stream.request_scene_data)
        self.btnReset.clicked.connect(controller.scene.reset_camera_position)

    def init_scene_renderer(self, scene_renderer : SceneRenderer):
        """
        Initializes the scene renderer in this view render scene and view render scene options
        """
        self._scene_renderer = scene_renderer
        self.sceneLayout.addWidget(scene_renderer.renderer.widget)

    @property
    def scene_renderer(self) -> SceneRenderer:
        """
        Returns the SceneRender object
        """
        return self._scene_renderer

    def enable_view(self, enabled : bool):
        """
        Enables the view elements
        """
        self.btnLoadScene.setEnabled(enabled)
        if enabled: # do not disable these once enabled
            self.btnReset.setEnabled(enabled)
            self.btnSceneOptions.setEnabled(enabled)

    def load_traced_paths(self, pixel_data : PixelData):
        """
        Informs the renderer to visualize the traced paths
        """
        self._scene_renderer.load_traced_paths(pixel_data)

    def clear_traced_paths(self):
        """
        Informs the renderer to clear all visualizes traced paths
        """
        self._scene_renderer.clear_traced_paths()

    def update_path_indices(self, indices : np.ndarray):
        """
        Updates the view with given path indices keys from controller
        """
        self._scene_renderer.update_path_indices(indices)

    def select_path(self, path_idx : typing.Optional[int]):
        """
        Informs the renderer to visualize the path with index: index
        """
        self._scene_renderer.select_path(path_idx)

    def select_intersection(self, path_idx : typing.Optional[int], its_idx : typing.Optional[int]):
        """
        Informs the renderer to select / highlight the intersection with tuple tpl
        """
        self._scene_renderer.select_intersection(path_idx, its_idx)
