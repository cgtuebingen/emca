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
from matplotlib.ticker import AutoLocator
from matplotlib.ticker import FixedLocator
from matplotlib.ticker import ScalarFormatter
from matplotlib.ticker import FixedFormatter
import numpy as np
from core.plot_figure_base import FigureBase
from core.highlighter_base import HighlighterBase


class ScatterPlot2D(FigureBase):

    def __init__(self, callback=None, title=None):
        figure, axes = plt.subplots(figsize=(5, 5), nrows=1, ncols=2,
                                    gridspec_kw={"width_ratios":(9, 1), "hspace":0.05, "wspace":0.05, "left":0.1, "right":0.95, "top":0.92, "bottom":0.08},
                                    sharey=True, constrained_layout=True)
        FigureBase.__init__(self, figure, axes)
        self.highlighter = HighlighterBase(figure, axes, callback)

        self.line = None
        self.hist = None

        for ax in self.axes.flatten():
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

        self.axes[1].set_axis_off()
        self.axes[1].add_artist(self.axes[1].patch)
        self.axes[1].patch.set_zorder(-1)
        self.axes[0].xaxis.set_ticks_position('bottom')
        self.axes[0].yaxis.set_ticks_position('left')

        self.axes[0].set_title(title, color=self.color_title)

        self.plot_2d([], [])

        self.highlighter.add_rectangle_selector(self.axes[0], self.select)
        self.highlighter.enable_rectangle_selector(False)

    def clear(self):
        if self.line is not None:
            self.line.remove()
            self.line = None
        if self.hist is not None:
            self.hist.remove()
            self.hist = None

        for ax in self.figure.axes:
            ax.relim()

    def plot_2d(self, x, y):
        self.clear()

        if isinstance(y, np.ndarray):
            if y.dtype.type is np.str_:
                unique_values = np.unique(y)
                self.axes[0].yaxis.set_major_locator(FixedLocator(range(len(unique_values))))
                self.axes[0].yaxis.set_major_formatter(FixedFormatter(unique_values))
            else:
                self.axes[0].yaxis.set_major_locator(AutoLocator())
                self.axes[0].yaxis.set_major_formatter(ScalarFormatter())

        self.line = self.axes[0].scatter(x, y, color=self.color_dots, picker=True, pickradius=5, alpha=self.alpha_dots)
        _, _, self.hist = self.axes[1].hist(y, bins=10, color=self.color_dots, orientation='horizontal')


        self.redraw()

    def set_title(self, title):
        if title != self.axes[0].get_title():
            self.axes[0].set_title(title, color=self.color_title)

            self.redraw()

    # point selection
    def select(self, mousedown, mouseup):
        mask = self.highlighter.inside(mousedown, mouseup, self.line.get_offsets()[:,0], self.line.get_offsets()[:,1])
        self.highlighter.callback_send_update_path(np.int32(self.line.get_offsets()[mask,0]), False)

    # point highlighting
    def highlight(self, indices):
        """
        Highlight the given indices
        :param indices: numpy array containing path indices
        :return:
        """
        if self.line is not None:
            mask = np.isin(np.int32(self.line.get_offsets()[:,0]), indices)
            self.line.set_color(np.where(mask, 'yellow', self.color_dots))

            self.redraw()

