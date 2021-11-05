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
from stream.stream import Stream
from core.plugin import PluginType
from plugins.plugins_view_container import PluginsViewContainer
import plugins


class PluginsHandler(object):

    """
        PluginsHandler
        Initialises and handles all custom plugins.
        Plugins will be loaded if there are imported and added in Plugins/__init__.py (__add__)
    """

    def __init__(self):

        # plugins dict { unique_tool_id : plugin, ... }
        self._plugins_view_container = {}

        # loads and initialises all tools
        for plugin in [(name, cls()) for name, cls in plugins.__dict__.items() if isinstance(cls, type)]:
            self._plugins_view_container[plugin[1].flag] = PluginsViewContainer(plugin[1])

    def set_controller(self, controller):
        """
        Sets the controller to all loaded plugins
        :param controller:
        :return:
        """
        for _, value in self._plugins_view_container.items():
            value.set_controller(controller)

    def set_scene_renderer(self, renderer : SceneRenderer):
        """
        Sets the renderer reference to all registered plugins
        """
        for _, value in self._plugins_view_container.items():
            value.set_scene_renderer(renderer)

    def apply_theme(self, theme):
        for _, value in self._plugins_view_container.items():
            value.plugin.apply_theme(theme)

    def enable_plugins(self, enable : bool):
        """
        Calls the tool container enable_tool_btn function.
        Enables the view Plugin button item
        """
        for _, value in self._plugins_view_container.items():
            if value.plugin.plugin_type is PluginType.CORE_PLUGIN:
                value.enable_plugin_btn(enable)

    def enable_plugin_by_id(self, plugin_id : int, enable : bool):
        """
        Enables the plugin btn based on the plugin id
        """
        plugin_container_item = self._plugins_view_container.get(plugin_id, None)
        if plugin_container_item:
            plugin_container_item.enable_plugin_btn(enable)

    def request_plugin(self, plugin_id : int, stream : Stream):
        """
        Calls the Tool Container
        """
        plugins_view_container = self._plugins_view_container.get(plugin_id, None)
        if plugins_view_container:
            plugins_view_container.serialize(stream)

    def init_data(self, pixel_data : PixelData):
        """
        Calls Tool Container init_pixel_data function.
        All plugins will be informed about a new render data package
        """
        for _, value in self._plugins_view_container.items():
            value.init_pixel_data(pixel_data)

    def prepare_new_data(self):
        """
        Calls the Tool Container prepare_new_data function.
        Informs all plugins that a new render data package is requested
        """
        for _, value in self._plugins_view_container.items():
            value.prepare_new_data()

    def update_path_indices(self, indices : np.ndarray):
        """
        Calls the Tool Container update_path_indices function.
        Informs all plugins about selected path index/indices
        :param indices: np.array[path_index,...]
        """
        for _, value in self._plugins_view_container.items():
            value.update_path_indices(indices)

    def select_path(self, path_index : typing.Optional[int]):
        """
        Calls the Tool Container select_path function.
        Updates all tool views with the current selected path
        """
        for _, value in self._plugins_view_container.items():
            value.select_path(path_index)

    def select_intersection(self, path_idx : typing.Optional[int], its_idx : typing.Optional[int]):
        """
        Calls the Plugin Container select_intersection function.
        Updates all tool views with the current selected intersection
        """
        for _, value in self._plugins_view_container.items():
            value.select_intersection(path_idx, its_idx)

    def get_plugin_by_id(self, plugin_id : int):
        """
        Returns the corresponding tool given the flag (unique_tool_id),
        if no tool was found None is returned
        :param flag: unique_tool_id
        :return: tool or None
        """
        plugins_view_container = self._plugins_view_container.get(plugin_id, None)
        if plugins_view_container:
            return plugins_view_container.plugin
        return None

    def close(self):
        """
        Closes all Tool windows
        :return:
        """
        for _, plugin in self._plugins_view_container.items():
            plugin.close()

    @property
    def plugins(self) -> typing.Dict[int, PluginsViewContainer]:
        """
        Returns the Plugins View Container dictionary {unique_tool_id : PluginsViewContainer, ...}
        :return:
        """
        return self._plugins_view_container



