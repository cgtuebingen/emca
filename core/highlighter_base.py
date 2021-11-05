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

from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.widgets import RectangleSelector
import numpy as np
import logging


rectprops = dict(
    facecolor='white',
    edgecolor='white',
    alpha=0.2,
    fill=True)


class HighlighterBase(object):

    def __init__(self, figure : Figure, axes : Axes, callback):
        self.fig = figure
        self.axes = axes
        self.canvas = self.fig.canvas

        self._cid_toggle = self.fig.canvas.mpl_connect('key_press_event', self.key_press_event)
        self._cid_release = self.fig.canvas.mpl_connect('key_release_event', self.key_release_event)
        self._cid_pick = self.fig.canvas.mpl_connect('pick_event', self.pick_event)

        self._rs = []
        self._active = False
        self._hold_shift = False
        self.callback_send_update_path = callback

    def add_rectangle_selector(self, axes : Axes, select_func):
        rs = RectangleSelector(axes, select_func, useblit=True, rectprops=rectprops)
        self._rs.append(rs)

    def clear_rectangle_selectors(self):
        self._rs.clear()

    def delete_highlighter(self):
        del self.highlighters
        self.highlighters = None

    def pick_event(self, event):
        if self.callback_send_update_path is None:
            return
        ind = event.ind
        if self._hold_shift:
            self.callback_send_update_path(np.array([ind[0]]), True)
        else:
            self.callback_send_update_path(np.array([ind[0]]), False)

    def key_press_event(self, event):
        if event.key in ['R', 'r']:
            logging.info("Pressed key R")
            self._active = not self._active
            self.enable_rectangle_selector(self._active)
            self.enable_pick_event_selector(not self._active)
        if event.key == 'shift':
            logging.info("Shift press")
            self._hold_shift = True

    def key_release_event(self, event):
        if event.key == 'shift':
            logging.info("Shift release")
            self._hold_shift = False

    def enable_rectangle_selector(self, enable : bool):
        for rs in self._rs:
            rs.set_active(enable)

    def enable_pick_event_selector(self, enable : bool):
        if enable:
            logging.info("connect pick event")
            self._cid_pick = self.fig.canvas.mpl_connect('pick_event', self.pick_event)
        else:
            logging.info("disconnect pick event")
            self.fig.canvas.mpl_disconnect(self._cid_pick)

    def enable_multi_selection(self, enabled : bool):
        if enabled:
            self._cid_toggle = self.fig.canvas.mpl_connect('key_press_event', self.key_press_event)
            self._cid_release = self.fig.canvas.mpl_connect('key_release_event', self.key_release_event)
        else:
            self.fig.canvas.mpl_disconnect(self._cid_toggle)
            self.fig.canvas.mpl_disconnect(self._cid_release)

    def overwrite_pick_event(self, func_callback):
        self._cid_pick = self.fig.canvas.mpl_connect('pick_event', func_callback)

    def inside(self, event1, event2, x, y):
        x0, x1 = sorted([event1.xdata, event2.xdata])
        y0, y1 = sorted([event1.ydata, event2.ydata])
        return (x > x0) & (x < x1) & (y > y0) & (y < y1)
