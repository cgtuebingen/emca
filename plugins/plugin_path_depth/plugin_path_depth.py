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

from core.plugin import Plugin
from core.plot_2d import ScatterPlot2D
from PySide2.QtWidgets import QVBoxLayout


class PathDepth(Plugin):

    def __init__(self):
        Plugin.__init__(
            self,
            name='PathDepth',
            flag=28)

        self.plot_path_depth = ScatterPlot2D(self.send_update_path_indices_callback)
        self.plot_path_depth.set_title('Depth')

        layout = QVBoxLayout(self)
        layout.addWidget(self.plot_path_depth)
        layout.addWidget(self.plot_path_depth.create_navigation_toolbar(self))

    def send_update_path_indices_callback(self, indices, add_item):
        self.send_update_path_indices(indices, add_item)

    def apply_theme(self, theme):
        self.plot_path_depth.apply_theme(theme)

    def init_render_data(self, render_data):
        x_list = []
        y_list = []
        for path_key, path in render_data.dict_paths.items():
            x_list.append(path_key)
            y_list.append(path.path_depth)

        self.plot_path_depth.plot_2d(x_list, y_list)
        self.plot_path_depth.set_title('Depth')

    def prepare_new_data(self):
        self.plot_path_depth.clear()

    def update_path_indices(self, indices):
        self.plot_path_depth.highlight(indices)

    def select_path(self, index):
        self.plot_path_depth.highlight([index])

    def select_intersection(self, path_idx, its_idx):
        # nothing to-do here
        pass

    def serialize(self, stream):
        # nothing to-do here since we work directly on render data
        pass

    def update_view(self):
        # nothing to-do here since we work directly on render data
        pass

    def deserialize(self, stream):
        # nothing to-do here since we work directly on render data
        pass
