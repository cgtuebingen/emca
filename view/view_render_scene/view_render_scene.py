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

import typing
from renderer.scene_renderer import SceneRenderer
from PySide2.QtWidgets import QWidget
from core.pyside2_uic import loadUi
import os
import logging


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
        self._scene_loaded = False

    def set_controller(self, controller):
        """
        Sets the connection to the controller
        :param controller: Controller
        :return:
        """
        self._controller = controller
        self.btnSceneOptions.clicked.connect(controller.display_view_render_scene_options)
        self.btnLoadScene.clicked.connect(controller.stream.request_scene_data)
        self.btnReset.clicked.connect(controller.scene.reset_camera_position)

    def init_scene_renderer(self, scene_renderer : SceneRenderer):
        """
        Initializes the scene renderer in this view render scene and view render scene options
        :param scene_renderer: SceneRenderer
        :return:
        """
        self._scene_renderer = scene_renderer
        self.sceneLayout.addWidget(scene_renderer.renderer.widget)

    @property
    def scene_renderer(self):
        """
        Returns the SceneRender object
        :return: SceneRenderer
        """
        return self._scene_renderer

    @property
    def scene_loaded(self):
        """
        Returns true if 3d scene was loaded
        :return: boolean
        """
        return self._scene_loaded

    @scene_loaded.setter
    def scene_loaded(self, is_loaded):
        """
        Sets the scene loaded value
        :param is_loaded: boolean
        """
        self._scene_loaded = is_loaded

    def enable_view(self, enabled : bool):
        """
        Enables the view elements
        """
        self.btnLoadScene.setEnabled(enabled)
        if enabled: # do not disable these once enabled
            self.btnReset.setEnabled(enabled)
            self.btnSceneOptions.setEnabled(enabled)

    def prepare_new_data(self):
        """
        Prepare new incoming data, informs the renderer that new data is coming
        :return:
        """
        self._scene_renderer.prepare_new_data()

    def clear_scene_objects(self):
        """
        Informs the renderer to clear all objects within the scene
        :return:
        """
        self._scene_renderer.clear_scene_objects()
        self._scene_loaded = False

    def load_camera(self, camera_data):
        """
        Informs the renderer about the camera data,
        loads the camera data and enables the camera settings
        :param camera_data:
        :return:
        """
        self._scene_renderer.load_camera(camera_data)

    def load_mesh(self, mesh_data):
        """
        Informs the renderer to load a mesh,
        enables the mesh settings
        :param mesh_data: MeshData
        :return:
        """
        self._scene_renderer.load_mesh(mesh_data)

    def process_scene_info(self, scene_info : typing.Dict[str, typing.Any]):
        self._scene_renderer.process_scene_info(scene_info)

    def load_traced_paths(self, render_data):
        """
        Informs the renderer to
        :param render_data:
        :return:
        """
        self._scene_renderer.load_traced_paths(render_data)

    def clear_traced_paths(self):
        """
        Informs the renderer to clear all visualizes traced paths
        :return:
        """
        self._scene_renderer.clear_traced_paths()

    def update_path_indices(self, indices):
        """
        Updates the view with given path indices keys from controller
        """
        self._scene_renderer.update_path_indices(indices)

    def select_path(self, index):
        """
        Informs the renderer to visualize the path with index: index
        :param index: integer
        :return:
        """
        self._scene_renderer.select_path(index)

    def select_intersection(self, path_idx, its_idx):
        """
        Informs the renderer to select / highlight the intersection with tuple tpl
        """
        self._scene_renderer.select_intersection(path_idx, its_idx)
