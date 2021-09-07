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
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolBar
from PySide2.QtWidgets import QSizePolicy
from PySide2.QtCore import Qt
import numpy as np
import logging

white = 'white'
params = {'ytick.color': white,
          'xtick.color': white,
          'axes.labelcolor': white,
          'axes.edgecolor': white}
plt.rcParams.update(params)


class FigureBase(FigureCanvas):

    def __init__(self, figure, axes):
        FigureCanvas.__init__(self, figure)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.RGBA = '#31363b'
        self.plot_facecolor = '#232629'
        self.figure.patch.set_facecolor(self.RGBA)
        self.axes = axes
        self.setFocusPolicy(Qt.ClickFocus)
        self.setFocus()

        if isinstance(self.axes, np.ndarray):
            for ax in self.figure.axes:
                ax.set_facecolor(self.plot_facecolor)
        else:
            self.axes.set_facecolor(self.plot_facecolor)

        self.alpha_dots = 0.7
        self.color_dots = '#eff0f1'
        self.color_title = 'white'
        self.color_axes = 'white'

    def create_navigation_toolbar(self, parent=None):
        return NavigationToolBar(self, parent)

    def apply_theme(self, theme):
        if theme == 'light':
            self.RGBA = '#EFF0F1'
            self.plot_facecolor = '#EFF0F1'
            self.color_axes = 'black'
            self.color_title = 'black'
            self.color_dots = 'blue'
        else:
            self.RGBA = '#31363b'
            self.plot_facecolor = '#232629'
            self.color_axes = 'white'
            self.color_title = 'white'
            self.color_dots = '#eff0f1'
        self.figure.patch.set_facecolor(self.RGBA)
        if isinstance(self.axes, np.ndarray):
            for ax in self.figure.axes:
                ax.set_facecolor(self.plot_facecolor)
                ax.tick_params(axis='x', colors=self.color_axes)
                ax.tick_params(axis='y', colors=self.color_axes)
                for spine in ['left', 'right', 'bottom', 'top']:
                    ax.spines[spine].set_color(self.color_axes)
        else:
            self.axes.set_facecolor(self.plot_facecolor)
            self.axes.tick_params(axis='x', colors=self.color_axes)
            self.axes.tick_params(axis='y', colors=self.color_axes)
            for spine in ['left', 'right', 'bottom', 'top']:
                self.axes.spines[spine].set_color(self.color_axes)
        self.redraw()

    def clear(self):
        if isinstance(self.axes, np.ndarray):
            for ax in self.figure.axes:
                ax.clear()
        else:
            self.axes.clear()
        self.redraw()

    def redraw(self):
        #logging.info("redraw requested")
        self.figure.canvas.draw_idle()
