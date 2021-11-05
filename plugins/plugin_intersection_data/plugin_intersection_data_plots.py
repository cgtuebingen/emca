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

import numpy as np

from core.plugin import Plugin

from core.point import Point2f
from core.color import Color4f

from model.pixel_data import PixelData

from core.pyside2_uic import loadUi
from PySide2.QtWidgets import QVBoxLayout
from PySide2.QtWidgets import QListWidgetItem
from PySide2.QtCore import Slot
from PySide2.QtCore import Qt
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolBar

from plugins.plugin_intersection_data.plot_list_item import PlotListItem
from plugins.plugin_intersection_data.intersection_data_plot_2d import IntersectionDataPlot2D
from plugins.plugin_intersection_data.intersection_data_plot_3d import IntersectionDataPlot3D
from plugins.plugin_intersection_data.intersection_data_plot_rgb import IntersectionDataPlotRGB
import os
import logging


class PathListItem(QListWidgetItem):

    def __init__(self, idx, name, layout):
        super().__init__(name, layout)
        self._idx = idx

    @property
    def idx(self):
        return self._idx


class IntersectionData(Plugin):

    def __init__(self):
        Plugin.__init__(
            self,
            name='IntersectionData',
            flag=27)
        ui_filepath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'ui', 'plugin_plots.ui'))
        loadUi(ui_filepath, self)

        self._its_data_plot_2d = IntersectionDataPlot2D(self)
        self._its_data_plot_3d = IntersectionDataPlot3D(self)
        self._its_data_plot_rgb = IntersectionDataPlotRGB(self)
        self._plots = [self._its_data_plot_2d,
                       self._its_data_plot_3d,
                       self._its_data_plot_rgb]
        self._pixel_data = None
        self._cur_its_idx = None
        self._last_plot_item = None

        layout_2d = QVBoxLayout(self.hist2D)
        layout_2d.addWidget(self._its_data_plot_2d)
        layout_2d.addWidget(self._its_data_plot_2d.create_navigation_toolbar(self.hist2D))

        layout_3d = QVBoxLayout(self.hist3D)
        layout_3d.addWidget(self._its_data_plot_3d)
        layout_3d.addWidget(NavigationToolBar(self._its_data_plot_3d, self.hist3D))

        layout_color = QVBoxLayout(self.histColor)
        layout_color.addWidget(self._its_data_plot_rgb)
        layout_color.addWidget(self._its_data_plot_rgb.create_navigation_toolbar(self.histColor))

        self.listPaths.currentItemChanged.connect(self.select_path_from_list)
        self.listPlotNames.currentRowChanged.connect(self.update_plots)

    def current_path_index(self):
        if self.listPaths.count() > 0:
            item = self.listPaths.currentItem()
            return item.idx
        return None

    def apply_theme(self, theme):
        for plot in self._plots:
            plot.apply_theme(theme)

    def init_pixel_data(self, pixel_data : PixelData):
        self._pixel_data = pixel_data

    def prepare_new_data(self):
        self._cur_its_idx = None
        self._last_plot_item = None
        self.clear_plots()
        self.listPaths.blockSignals(True)
        self.listPaths.clear()
        self.listPaths.blockSignals(False)
        self.listPlotNames.blockSignals(True)
        self.listPlotNames.clear()
        self.listPlotNames.blockSignals(False)

    def update_path_indices(self, indices):
        self.prepare_new_data()
        for i in indices:
            PathListItem(i, 'Path ({})'.format(i), self.listPaths)

    def select_path(self, index):
        self.listPlotNames.blockSignals(True)
        self.listPlotNames.clear()
        self.listPlotNames.blockSignals(False)

        if index is None:
            self.listPaths.clearSelection()
            return

        for i in range(0, self.listPaths.count()):
            item = self.listPaths.item(i)
            if item.idx == index:
                break
            item = None

        if item is None:
            return

        self.listPaths.blockSignals(True)
        self.listPaths.setCurrentItem(item)
        self.listPaths.blockSignals(False)

        paths = self._pixel_data.dict_paths
        path_data = paths.get(item.idx, None)

        if path_data:
            intersections = path_data.intersections
            plot_data_dict = {}
            for its_idx, its in intersections.items():
                for key, value in its.data.items():
                    if plot_data_dict.get(key, None) is None:

                        if isinstance(value, Point2f):
                            plot_type = '3d'
                        elif isinstance(value, Color4f):
                            plot_type = 'rgb'
                        elif np.shape(value) == () or np.shape(value) == (1,):
                            plot_type = '2d'
                        else:
                            # skip value of unknown type
                            continue
                        plot_data_dict[key] = {'its':[],'value':[],'type':plot_type}

                    plot_data_dict[key]['its'].append(its_idx)
                    plot_data_dict[key]['value'].append(value)

                # Add a plot of the intersection estimate (if available)
                if its.li is not None:
                    key = 'Estimate'
                    if plot_data_dict.get(key, None) is None:
                        plot_type = 'rgb'
                        plot_data_dict[key] = {'its':[],'value':[],'type':plot_type}
                    plot_data_dict[key]['its'].append(its_idx)
                    plot_data_dict[key]['value'].append(its.li)

                # Add a plot of the emission (if available)
                if its.le is not None:
                    key = 'Emission'
                    if plot_data_dict.get(key, None) is None:
                        plot_type = 'rgb'
                        plot_data_dict[key] = {'its':[],'value':[],'type':plot_type}
                    plot_data_dict[key]['its'].append(its_idx)
                    plot_data_dict[key]['value'].append(its.le)


            for key in plot_data_dict.keys():
                plot_data_dict[key]['its']   = np.array(plot_data_dict[key]['its'])
                plot_data_dict[key]['value'] = np.array(plot_data_dict[key]['value'])

                if plot_data_dict[key]['type'] == '2d':
                    PlotListItem(key, self.listPlotNames, plot_data_dict, 0.75, path_data.path_depth+0.25, self._its_data_plot_2d, 0)
                elif plot_data_dict[key]['type'] == '3d':
                    PlotListItem(key, self.listPlotNames, plot_data_dict, 0.75, path_data.path_depth+0.25, self._its_data_plot_3d, 1)
                elif plot_data_dict[key]['type'] == 'rgb':
                    PlotListItem(key, self.listPlotNames, plot_data_dict, 0.75, path_data.path_depth+0.25, self._its_data_plot_rgb, 2)
                else:
                    raise Exception('invalid data type'+str(plot_data_dict[key]['type']))

            if self._last_plot_item is None:
                self.listPlotNames.setCurrentRow(0)
            else:
                self.clear_plots()
                items_list = self.listPlotNames.findItems(self._last_plot_item, Qt.MatchCaseSensitive)
                if len(items_list) > 0:
                    item = items_list[0]
                    if self.stackedHists.currentIndex() != item.widget_idx:
                        self.stackedHists.setCurrentIndex(item.widget_idx)
                    item.setSelected(True)
                    item.plot_canvas.plot(item.name, item.plot_data[item.name], item.xmin, item.xmax)
                else:
                    self.listPlotNames.setCurrentRow(0)

    def select_intersection(self, path_idx, its_idx):
        if self._pixel_data:
            self._cur_its_idx = its_idx
            stacked_idx = self.stackedHists.currentIndex()
            if stacked_idx == 0:
                self._its_data_plot_2d.select_intersection(its_idx)
            elif stacked_idx == 1:
                self._its_data_plot_3d.select_intersection(its_idx)
            elif stacked_idx == 2:
                self._its_data_plot_rgb.select_intersection(its_idx)

    @Slot(QListWidgetItem, name='select_path_from_list')
    def select_path_from_list(self, item):
        self.send_select_path(item.idx)

    def update_plots(self, row_idx):
        self.clear_plots()

        item = self.listPlotNames.item(row_idx)
        if not item:
            return None

        self._last_plot_item = item.name

        if self.stackedHists.currentIndex() != item.widget_idx:
            self.stackedHists.setCurrentIndex(item.widget_idx)

        self.listPlotNames.setCurrentItem(item)
        item.plot_canvas.plot(item.name, item.plot_data[item.name], item.xmin, item.xmax)

        if self._cur_its_idx is not None:
            item.plot_canvas.select_intersection(self._cur_its_idx)

    def clear_plots(self):
        for plot in self._plots:
            plot.clear()

    @staticmethod
    def insert_plot_data(source_dict, target_dict, intersection_idx):
        for name, value in source_dict.items():
            if target_dict.get(name, None) is not None:
                target_dict[name]['its'].append(intersection_idx)
                target_dict[name]['value'].append(value)
            else:
                target_dict[name] = {'its':[intersection_idx],'value':[value]}

    def serialize(self, stream):
        # nothing to-do here since we work directly on render data
        pass

    def deserialize(self, stream):
        # nothing to-do here since we work directly on render data
        pass

    def update_view(self):
        # nothing to-do here since we work directly on render data
        pass
