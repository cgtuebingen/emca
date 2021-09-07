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

from core.plot_2d import ScatterPlot2D
from PySide2.QtWidgets import QWidget
from PySide2.QtWidgets import QVBoxLayout
import logging


class ViewSampleLuminance(QWidget):

    """
        ViewSampleContribution
        Handles the plot view of the final estimate data per path.
        A matplotlib plot is embedded within a QWidget for visualization
    """

    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)

        self._controller = None
        # matplotlib plot embedded within a QWidget
        self._sample_contribution_plot = ScatterPlot2D(callback=self.send_update_path, title='Luminance')

        self._visible = True
        self._data = None

        # add matplotlib navigation toolbar
        layout = QVBoxLayout(self)
        layout.addWidget(self._sample_contribution_plot)
        layout.addWidget(self._sample_contribution_plot.create_navigation_toolbar(self))

    def set_controller(self, controller):
        """
        Sets the connection to the controller
        :param controller: Controller
        :return:
        """
        self._controller = controller

    def apply_theme(self, theme):
        self._sample_contribution_plot.apply_theme(theme)

    def plot_final_estimate(self, final_estimate):
        """
        Plot SampleContribution data with final estimate values from model
        :param final_estimate: FinalEstimate
        :return:
        """
        if not self._visible:
            self._data = final_estimate
            return

        if final_estimate.is_valid():
            self._sample_contribution_plot.plot_2d(final_estimate.plot_data_x,
                                                    final_estimate.luminance)

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, visible):
        self._visible = visible
        if self._visible and self._data is not None:
            self.plot_final_estimate(self._data)
            self._data = None

    def update_path_indices(self, indices):
        """
        Inform the plot to mark the given indices
        :param indices: numpy array of path indices
        :return:
        """
        self.visible = True
        self._sample_contribution_plot.highlight(indices)

    def send_update_path(self, indices, add_index):
        """
        Inform the controller about selected points from the plot highlighter,
        depending on add_index the indices are added to the current selected ones
        :param indices: numpy array of path indices
        :param add_index: boolean
        :return:
        """
        self._controller.update_path(indices, add_index)

