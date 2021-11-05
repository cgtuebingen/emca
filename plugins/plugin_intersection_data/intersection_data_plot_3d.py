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

from core.plot_2d_xy import ScatterPlot2DXY
import logging


class IntersectionDataPlot3D(ScatterPlot2DXY):

    def __init__(self, parent=None):
        ScatterPlot2DXY.__init__(self, None)
        self.parent = parent
        # overwrite pick event since we work on vertices not on paths
        self.highlighter.overwrite_pick_event(self.handle_pick)
        self.highlighter.enable_multi_selection(False)

    def handle_pick(self, event):
        ind = event.ind

        path_idx = self.parent.current_path_index()

        self.parent.send_select_intersection(path_idx, self.x[ind[0]])

    def select_intersection(self, its_idx):
        self.highlight([its_idx])

    def prepare_plot_data(self, values):
        x_list = values['its']
        points = values['value']

        y_list = points[:,0]
        z_list = points[:,1]

        return x_list, y_list, z_list

    def plot(self, name, values, xmin=None, xmax=None):
        x, y, z = self.prepare_plot_data(values)
        self.plot_2d(x, y, z)
        #if xmin is not None and xmax is not None:
            #self.axes.set_xlim(xmin, xmax)
        self.set_title(name)
        #self.axes.set_xlabel('path depth', color=self.color_title)
        #self.axes.set_ylabel('x', color=self.color_title)
        #self.axes.set_zlabel('y', color=self.color_title)
        #self.axes.set_xticks(x)
