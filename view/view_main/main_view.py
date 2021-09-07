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

from PySide2.QtWidgets import QApplication
from PySide2.QtWidgets import QMainWindow
from PySide2.QtWidgets import QAction
from PySide2.QtCore import Slot
from view.view_main.view_emca import ViewEMCA
from view.view_main.view_about import ViewAbout
from view.view_main.popup_messages import PopupMessages
from view.view_main.pixel_icon import PixelIcon


class MainView(QMainWindow):

    """
        MainView
        Represents the MainView of EMCA
    """

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent=parent)

        # center widget depending on screen size
        desktop_widget = QApplication.desktop()
        screen_rect = desktop_widget.availableGeometry(self)
        self.move(screen_rect.center() - self.rect().center())

        # Main view of EMCA, holding all subviews
        self._view_emca = ViewEMCA(parent=self)
        # Popup view handling error messages
        self._view_popup = PopupMessages()
        # About information
        self._view_about = ViewAbout()
        # Pixel Icon of selected Pixel in MainView
        self._pixel_icon = PixelIcon()
        self.setCentralWidget(self._view_emca)
        self.setWindowTitle('Explorer of Monte Carlo based Algorithms (EMCA)')
        # Accept drops for Drag n drop events
        self.setAcceptDrops(True)
        self.add_menu_bar()
        self._controller = None

    def add_menu_bar(self):
        """
        Initialises and adds all menu items to the menu
        :return:
        """

        options = QAction('Options', self)
        options.setShortcut('Ctrl+S')
        options.setToolTip('Options')
        options.triggered.connect(self.open_options)

        load_image = QAction('Load image', self)
        load_image.setShortcut('Ctrl+O')
        load_image.setToolTip('Load .exr')
        load_image.triggered.connect(self.load_image_dialog)

        exit_action = QAction("Quit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setToolTip("Closes the Application")
        exit_action.triggered.connect(self.close)

        about_action = QAction("About", self)
        about_action.triggered.connect(self._view_about.show)

        main_menu = self.menuBar()
        main_menu.setNativeMenuBar(False)
        menu = main_menu.addMenu("&Menu")
        menu.addAction(load_image)
        menu.addAction(options)
        menu.addAction(exit_action)
        about = main_menu.addMenu("&About")
        about.addAction(about_action)

    def set_controller(self, controller):
        """
        Set the connection to the controller
        :param controller:
        :return:
        """
        self._controller = controller
        self._view_emca.set_controller(controller)

    def closeEvent(self, q_close_event):
        """
        Handle the close event. Controller will be informed
        :param q_close_event:
        :return:
        """
        self._controller.close_app()

    def enable_filter(self, enable):
        """
        Depending on enable, the filter button and its view will be enabled
        :param enable: boolean
        :return:
        """
        self._view_emca.btnFilter.setEnabled(enable)

    @Slot(bool, name='open_options')
    def open_options(self, clicked):
        """
        Opens the options window
        :param clicked: boolean
        :return:
        """
        self._controller.options.open_options(clicked)

    @Slot(bool, name='load_image_dialog')
    def load_image_dialog(self, clicked):
        """
        Opens the dialog to load a file
        :param clicked: boolean
        :return:
        """
        self._controller.options.load_image_dialog(clicked)

    @property
    def controller(self):
        """
        Returns the controller
        :return: Controller
        """
        return self._controller

    @property
    def pixel_icon(self):
        """
        Return the pixel icon object
        :return: PixelIcon
        """
        return self._pixel_icon

    @property
    def view_emca(self):
        """
        Returns the view widget of EMCA
        :return: QWidget
        """
        return self._view_emca

    @property
    def view_popup(self):
        """
        Returns the view handling the popup messages
        :return: QObject
        """
        return self._view_popup

    @property
    def view_render_info(self):
        """
        Returns the view handling the render info
        :return: QWidget
        """
        return self._view_emca.view_render_info

    @property
    def view_rgb_plot(self):
        """
        Returns the view handling the final estimate view
        :return: QWidget
        """
        return self._view_emca.view_rgb_plot

    @property
    def view_lum_plot(self):
        """
        Returns the view handling the final estimate view
        :return: QWidget
        """
        return self._view_emca.view_lum_plot

    @property
    def view_depth_plot(self):
        """
        Returns the view handling the final estimate view
        :return: QWidget
        """
        return self._view_emca.view_depth_plot

    @property
    def view_connect(self):
        """
        Returns the view handling the connect settings
        :return: QWidget
        """
        return self._view_emca.view_connect

    @property
    def view_filter(self):
        """
        Returns the view handling the filter
        :return: QWidget
        """
        return self._view_emca.view_filter

    @property
    def view_render_image(self):
        """
        Returns the view handling the rendered image
        :return: QWidget
        """
        return self._view_emca.view_render_image

    @property
    def view_render_scene(self):
        """
        Returns the view handling the 3D viewer
        :return: QWidget
        """
        return self._view_emca.view_render_scene

    @property
    def view_render_scene_options(self):
        """
        Returns the view handling the scene options
        :return: QWidget
        """
        return self._view_emca.view_render_scene_options

    @property
    def view_render_data(self):
        """
        Returns the view handling the render data
        :return: QWidget
        """
        return self._view_emca.view_render_data

    @property
    def view_detector(self):
        """
        Returns the view handling the detector
        :return: QWidget
        """
        return self._view_emca.view_detector

    @property
    def view_options(self):
        """
        Returns the view handling the options
        :return: QWidget
        """
        return self._view_emca.view_options

