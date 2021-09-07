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

from PySide2.QtWidgets import QWidget
from PySide2.QtWidgets import QButtonGroup
from PySide2.QtWidgets import QStackedWidget
from PySide2.QtCore import Slot
from PySide2.QtCore import QPoint
from core.pyside2_uic import loadUi

from view.view_main.view_options_settings import ViewOptions
from view.view_main.view_connect_settings import ViewConnectSettings
from view.view_main.view_filter_settings import ViewFilterSettings
from view.view_main.view_detector_settings import ViewDetectorSettings
from view.view_main.view_render_settings import ViewRenderSettings

from view.view_render_data.view_render_data import ViewRenderData
from view.view_render_scene.view_render_scene import ViewRenderScene
from view.view_render_scene.view_render_scene_options import ViewRenderSceneOptions
from view.view_render_image.view_render_image import ViewRenderImage
from view.view_sample_contribution.view_sample_contribution_plot import ViewSampleContribution
from view.view_sample_contribution.view_sample_lum_plot import ViewSampleLuminance
from view.view_sample_contribution.view_sample_depth_plot import ViewSampleDepth
import os

import logging


class ViewEMCA(QWidget):

    """
        EMCA Mainview
        Holding all sub-view items.
        Handling connection between the views and informs the controller about interactions.
    """

    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        ui_filepath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ui', 'emca.ui'))
        loadUi(ui_filepath, self)

        self.setAcceptDrops(True)

        # init views
        self._controller = None
        self._view_main = parent
        self._view_options = ViewOptions(parent=parent)
        self._view_connect = ViewConnectSettings(parent=parent)
        self._view_detector = ViewDetectorSettings(parent=parent)
        self._view_filter = ViewFilterSettings(parent=parent)
        self._view_render_info = ViewRenderSettings(parent=parent)
        self._view_render_image = ViewRenderImage(parent=self)
        self._view_rgb_plot = ViewSampleContribution(parent=self)
        self._view_lum_plot = ViewSampleLuminance(parent=self)
        self._view_depth_plot = ViewSampleDepth(parent=self)
        self._view_render_data = ViewRenderData(parent=self)
        self._view_render_scene = ViewRenderScene(parent=self)
        self._view_render_scene_options = ViewRenderSceneOptions(parent=self)

        # redrawing is quite expensive, so lets only do that when necessary
        self._view_rgb_plot.visible = True
        self._view_lum_plot.visible = False
        self._view_depth_plot.visible = False

        # stacked widget
        self._stacked_widget_left = QStackedWidget()
        self._stacked_widget_left.addWidget(self._view_render_image)
        self._stacked_widget_left.addWidget(self._view_render_scene)
        self.left.addWidget(self._stacked_widget_left)

        self._stacked_widget_right = QStackedWidget()
        self._stacked_widget_right.addWidget(self._view_rgb_plot)
        self._stacked_widget_right.addWidget(self._view_lum_plot)
        self._stacked_widget_right.addWidget(self._view_depth_plot)
        self._stacked_widget_right.addWidget(self._view_render_data)
        self.right.addWidget(self._stacked_widget_right)

        # connect signals
        self.btnConnect.clicked.connect(self.open_connect_view)
        self.btnDetector.clicked.connect(self.open_detector_view)
        self.btnFilter.clicked.connect(self.open_filter_view)
        self.btnOptions.clicked.connect(self.open_render_info_view)
        self.btnRender.clicked.connect(self.request_render_image)

        self._view_right_button_group = QButtonGroup()
        self._view_right_button_group.addButton(self.btnSampleRGB, 0)
        self._view_right_button_group.addButton(self.btnSampleLum, 1)
        self._view_right_button_group.addButton(self.btnPathDepth, 2)
        self._view_right_button_group.addButton(self.btnPathData, 3)
        self._view_right_button_group.idClicked.connect(self.toggle_view_right)

        self._view_left_button_group = QButtonGroup()
        self._view_left_button_group.addButton(self.btnRenderView, 0)
        self._view_left_button_group.addButton(self.btnRefView, 1)
        self._view_left_button_group.addButton(self.btnDiffView, 2)
        self._view_left_button_group.addButton(self.btn3DView, 3)
        self._view_left_button_group.idClicked.connect(self.toggle_view_left)

        self.cbPixelHistory.currentIndexChanged.connect(self.request_history_pixel)

    def set_controller(self, controller):
        """
        Sets the connection to the controller
        :param controller: Controller
        :return:
        """
        self._controller = controller
        self._view_options.set_controller(controller)
        self._view_rgb_plot.set_controller(controller)
        self._view_lum_plot.set_controller(controller)
        self._view_depth_plot.set_controller(controller)
        self._view_render_scene.set_controller(controller)
        self._view_render_scene_options.set_controller(controller)
        self._view_render_data.set_controller(controller)
        self._view_render_image.set_controller(controller)
        self._view_render_info.set_controller(controller)
        self._view_connect.set_controller(controller)
        self._view_detector.set_controller(controller)
        self._view_filter.set_controller(controller)

    @Slot(bool, name='open_connect_view')
    def open_connect_view(self, clicked):
        """
        Opens the connect view, if the view is already open the window is set back to active
        :param clicked: boolean
        :return:
        """
        if self._view_connect.isVisible():
            self._view_connect.activateWindow()
        else:
            self._view_connect.show()

    @Slot(bool, name='open_detector_view')
    def open_detector_view(self, clicked):
        """
        Opens the detector view, if the view is already open the window is set back to active
        :param clicked: boolean
        :return:
        """
        if self._view_detector.isVisible():
            self._view_detector.activateWindow()
        else:
            self._view_detector.show()

    @Slot(bool, name='open_filter_view')
    def open_filter_view(self, clicked):
        """
        Opens the filter view, if the view is already open the window is set back to active
        :param clicked: boolean
        :return:
        """
        if self._view_filter.isVisible():
            self._view_filter.activateWindow()
        else:
            self._view_filter.show()

    @Slot(bool, name='open_render_info_view')
    def open_render_info_view(self, clicked):
        """
        Opens the render info view, if the view is already open the window is set back to active
        :param clicked:
        :return:
        """
        if self._view_render_info.isVisible():
            self._view_render_info.activateWindow()
        else:
            self._view_render_info.show()

    @Slot(bool, name='request_render_image')
    def request_render_image(self, clicked):
        """
        Informs the controller to request the render image from the server
        :param clicked: boolean
        :return:
        """
        self._controller.stream.request_render_image()

    @Slot(int, name='toggle_view_left')
    def toggle_view_left(self, id):
        """
        Toggles the contents of the left view (Render/Ref/Diff/3D)
        :param id: integer
        :return:
        """

        # set plus/minus rendering in diff mode
        self._view_render_image.set_plusminus(id == 2)
        self._view_render_image.set_show_ref(id == 1)
        # switch between 2D and 3D
        self._stacked_widget_left.setCurrentIndex(1 if id == 3 else 0)

    @Slot(bool, name='toggle_view_right')
    def toggle_view_right(self, id):
        """
        Toggles the two views on the right side final estimate plot and render data via a stacked widget
        :param id:  integer
        :return:
        """

        self._view_rgb_plot.visible   = id == 0
        self._view_lum_plot.visible   = id == 1
        self._view_depth_plot.visible = id == 2

        self._stacked_widget_right.setCurrentIndex(id)

    @property
    def controller(self):
        """
        Returns the controller
        :return: Controller
        """
        return self._controller

    @property
    def view_main(self):
        """
        Returns the QMainView
        :return: QMainView
        """
        return self._view_main

    @property
    def view_connect(self):
        """
        Returns the connect view
        :return: QWidget
        """
        return self._view_connect

    @property
    def view_detector(self):
        """
        Returns the detector view
        :return: QWidget
        """
        return self._view_detector

    @property
    def view_filter(self):
        """
        Returns the filter view
        :return: QWidget
        """
        return self._view_filter

    @property
    def view_render_info(self):
        """
        Returns the render info view
        :return: QWidget
        """
        return self._view_render_info

    @property
    def view_render_image(self):
        """
        Returns the render image view
        :return: QWidget
        """
        return self._view_render_image

    @property
    def view_render_data(self):
        """
        Returns the render data view
        :return: QWidget
        """
        return self._view_render_data

    @property
    def view_rgb_plot(self):
        """
        Returns the final estimate plot view
        :return: QWidget
        """
        return self._view_rgb_plot

    @property
    def view_lum_plot(self):
        """
        Returns the final estimate plot view
        :return: QWidget
        """
        return self._view_lum_plot

    @property
    def view_depth_plot(self):
        """
        Returns the final estimate plot view
        :return: QWidget
        """
        return self._view_depth_plot

    @property
    def view_render_scene(self):
        """
        Returns the 3D render scene view
        :return: QWidget
        """
        return self._view_render_scene

    @property
    def view_render_scene_options(self):
        """
        Returns the 3D Scene options
        :return: QWidget
        """
        return self._view_render_scene_options

    @property
    def view_options(self):
        """
        Returns the options widget
        :return: QWidget
        """
        return self._view_options

    def enable_view(self, enabled : bool):
        """
        Enables view elements depending on enabled
        """
        self.btnConnect.clicked.disconnect()
        if enabled:
            self.btnConnect.setText('Disconnect')
            self.btnConnect.clicked.connect(self._controller.stream.disconnect_socket_stream)
        else:
            self.btnConnect.setText('Connect')
            self.btnConnect.clicked.connect(self.open_connect_view)

        self.btnRender.setEnabled(enabled)
        self.btnOptions.setEnabled(enabled)
        self.labelSelectedPixel.setEnabled(enabled)
        self.cbPixelHistory.setEnabled(enabled)
        self.btnDetector.setEnabled(enabled)
        self.btnFilter.setEnabled(enabled)

    def add_plugins(self, plugins):
        """
        Adds the plugin buttons to the view
        :param plugins: dict{tool_id : PluginsViewContainer, ... }
        :return:
        """
        row = 0
        col = 0
        for flag, plugin in plugins.items():
            btn_plugin = plugin.get_plugin_btn()
            if col > 5:
                row = row + 1
            self.layoutPlugins.addWidget(btn_plugin, row, col)
            col = col + 1

    def update_pixel_hist(self, pixel_info):
        """
        Updates the pixel history
        :param pixel_info: PixelInfo
        :return:
        """
        self.cbPixelHistory.blockSignals(True)
        text = pixel_info.get_pixel_str()
        # check if item is already in list
        idx = self.cbPixelHistory.findText(text)
        if idx == -1:
            # item not found, insert new item
            self.cbPixelHistory.addItem(pixel_info.icon, text)
            idx = self.cbPixelHistory.count()-1
            self.cbPixelHistory.setCurrentIndex(idx)
        else:
            # item found, select its index
            self.cbPixelHistory.setCurrentIndex(idx)
        self.cbPixelHistory.blockSignals(False)

    @Slot(int, name='request_history_pixel')
    def request_history_pixel(self, index):
        """
        Informs the controller to request an old data set from the pixel history
        :param index: integer
        :return:
        """
        text = self.cbPixelHistory.itemText(index)
        text = text.strip('()')
        values = text.split(",")
        x, y = int(values[0]), int(values[1])
        logging.info('Request pixel=({},{})'.format(x, y))
        self._controller.stream.request_render_data(QPoint(x, y))
