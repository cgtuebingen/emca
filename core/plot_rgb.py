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

import matplotlib.pyplot as plt
import numpy as np

from core.plot_figure_base import FigureBase
from core.highlighter_base import HighlighterBase
import logging


class RGBScatterPlot(FigureBase):

    def __init__(self, callback):
        figure, axes = plt.subplots(figsize=(5, 5), nrows=3, ncols=2,
                                    gridspec_kw={"width_ratios":(9, 1), "hspace":0.05, "wspace":0.05, "left":0.1, "right":0.95, "top":0.92, "bottom":0.08},
                                    sharey=True, constrained_layout=True)
        FigureBase.__init__(self, figure, axes)
        self.highlighter = HighlighterBase(figure, axes, callback)
        self.r_line = None
        self.g_line = None
        self.b_line = None

        self.r_hist = None
        self.g_hist = None
        self.b_hist = None

        for ax in self.figure.axes:
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

        self.init_figure_layout()

        self.plot_rgb([], [], [], [])

        self.highlighter.add_rectangle_selector(self.axes[0, 0], self.select_r)
        self.highlighter.add_rectangle_selector(self.axes[1, 0], self.select_g)
        self.highlighter.add_rectangle_selector(self.axes[2, 0], self.select_b)

        self.highlighter.enable_rectangle_selector(False)

    def init_figure_layout(self):
        self.axes[0, 0].set_title("Red", color=self.color_title)
        self.axes[1, 0].set_title("Green", color=self.color_title)
        self.axes[2, 0].set_title("Blue", color=self.color_title)

        for i in range(3):
            self.axes[i, 1].set_axis_off()
            self.axes[i, 1].add_artist(self.axes[i, 1].patch)
            self.axes[i, 1].patch.set_zorder(-1)
            self.axes[i, 0].xaxis.set_ticks_position('bottom')
            self.axes[i, 0].yaxis.set_ticks_position('left')

    def clear(self):
        if self.r_line is not None and self.b_line is not None and self.g_line is not None:
            self.r_line.remove()
            self.g_line.remove()
            self.b_line.remove()
            self.r_line = None
            self.g_line = None
            self.b_line = None
        if self.r_hist is not None and self.b_hist is not None and self.g_hist is not None:
            self.r_hist.remove()
            self.g_hist.remove()
            self.b_hist.remove()
            self.r_hist = None
            self.g_hist = None
            self.b_hist = None

        for ax in self.figure.axes:
            ax.relim()

    def plot_rgb(self, x, r, g, b):
        self.clear()

        # draw red data
        self.r_line = self.axes[0, 0].scatter(x, r, color='red', picker=True, pickradius=5, alpha=self.alpha_dots)
        _, _, self.r_hist = self.axes[0, 1].hist(r, bins=10, color='red', orientation='horizontal')
        # draw green data
        self.g_line = self.axes[1, 0].scatter(x, g, color='green', picker=True, pickradius=5, alpha=self.alpha_dots)
        _, _, self.g_hist = self.axes[1, 1].hist(g, bins=10, color='green', orientation='horizontal')
        # draw blue data
        self.b_line = self.axes[2, 0].scatter(x, b, color='blue', picker=True, pickradius=5, alpha=self.alpha_dots)
        _, _, self.b_hist = self.axes[2, 1].hist(b, bins=10, color='blue', orientation='horizontal')

        self.redraw()

    # point selection
    def select_r(self, mousedown, mouseup):
        mask = self.highlighter.inside(mousedown, mouseup, self.r_line.get_offsets()[:,0], self.r_line.get_offsets()[:,1])
        self.highlighter.callback_send_update_path(np.int32(self.r_line.get_offsets()[mask,0]), False)

    def select_g(self, mousedown, mouseup):
        mask = self.highlighter.inside(mousedown, mouseup, self.g_line.get_offsets()[:,0], self.g_line.get_offsets()[:,1])
        self.highlighter.callback_send_update_path(np.int32(self.g_line.get_offsets()[mask,0]), False)

    def select_b(self, mousedown, mouseup):
        mask = self.highlighter.inside(mousedown, mouseup, self.b_line.get_offsets()[:,0], self.b_line.get_offsets()[:,1])
        self.highlighter.callback_send_update_path(np.int32(self.b_line.get_offsets()[mask,0]), False)

    # point highlighting
    def highlight(self, indices):
        """
        Highlight the given indices
        :param indices: numpy array containing path indices
        :return:
        """
        mask = np.isin(np.int32(self.r_line.get_offsets()[:,0]), indices)
        self.r_line.set_color(np.where(mask, 'yellow', 'red'))
        self.g_line.set_color(np.where(mask, 'yellow', 'green'))
        self.b_line.set_color(np.where(mask, 'yellow', 'blue'))

        self.redraw()

