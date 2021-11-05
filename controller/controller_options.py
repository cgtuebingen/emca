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

from PySide2.QtWidgets import QFileDialog
import logging
import os
import sys
from core.messages import StateMsg

from model.model import Model
from view.view_main.main_view import MainView

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from controller.controller import Controller
else:
    from typing import Any as Controller

class ControllerOptions(object):

    """
        ControllerOptions
        Handles pre-loaded options, the theme and image dialogs.
    """

    def __init__(self, parent : Controller, model : Model, view : MainView):
        self._controller_main = parent
        self._view = view
        self._model = model

    def get_theme(self):
        return self._model.options_data.theme

    def set_theme(self, theme):
        self._view.view_rgb_plot.apply_theme(theme)
        self._view.view_lum_plot.apply_theme(theme)
        self._view.view_depth_plot.apply_theme(theme)
        self._model.plugins_handler.apply_theme(theme)

    def load_image_dialog(self, triggered):
        """
        Opens a view for loading an image.
        Loads an HDR (.exr) image into the view render image view
        :param triggered:
        :return:
        """
        dialog = QFileDialog()
        dialog.setNameFilters(['*.exr'])
        dialog.setDefaultSuffix('.exr')

        if dialog.exec() == QFileDialog.Accepted:
            filepath = dialog.selectedFiles()[0]
            if self._view.view_render_image.load_hdr_image(filepath):
                self._view.view_render_image.enable_view(True)
                self.save_options({'rendered_image_filepath': filepath})

    def load_reference_dialog(self, triggered):
        """
        Opens a view for loading an image.
        Loads an HDR (.exr) image into the view render image view
        :param triggered:
        :return:
        """
        dialog = QFileDialog()
        dialog.setNameFilters(['*.exr'])
        dialog.setDefaultSuffix('.exr')

        if dialog.exec() == QFileDialog.Accepted:
            filepath = dialog.selectedFiles()[0]
            if self._view.view_render_image.load_hdr_image(filepath, True):
                self._view.view_render_image.enable_view(True)
                self.save_options({'reference_image_filepath': filepath})

    def load_pre_options(self):
        options = self._model.options_data
        # handle auto connect
        last_hostname = options.last_hostname
        last_port = options.last_port
        # update connect view about last settings
        self._view.view_connect.hostname = last_hostname
        self._view.view_connect.port = last_port
        if options.auto_connect:
            self._controller_main.stream.connect_socket_stream(last_hostname, last_port)
        if options.auto_image_load:
            success = False
            try:
                success = self._view.view_render_image.load_hdr_image(options.last_rendered_image_filepath)
                if success and options.last_reference_image_filepath is not None:
                    self._view.view_render_image.load_hdr_image(options.last_reference_image_filepath, True)
            except Exception as e:
                logging.error(e)
                self._view.view_popup.error_on_loading_pre_saved_image(str(e))
            if success:
                self._view.view_render_image.enable_view(True)
                self._view.view_render_image.reset(True)

    def open_options(self, clicked):
        options = self._model.options_data
        # default dark otherwise light
        if options.theme == 'light':
            self._view.view_options.enable_light_theme(True)
        else:
            self._view.view_options.enable_dark_theme(True)

        self._view.view_options.set_auto_connect(options.auto_connect)
        self._view.view_options.set_auto_scene_load(options.auto_scene_load)
        self._view.view_options.set_auto_image_load(options.auto_image_load)
        self._view.view_options.show()

    def save_options(self, options_dict : dict):
        try:
            theme_changed = False
            options = self._model.options_data
            if 'theme' in options_dict:
                if options.theme != options_dict['theme']:
                    options.theme = options_dict['theme']
                    theme_changed = True
            if 'auto_connect' in options_dict:
                options.auto_connect = options_dict['auto_connect']
            if 'auto_scene_load' in options_dict:
                options.auto_scene_load = options_dict['auto_scene_load']
            if 'rendered_image_filepath' in options_dict:
                options.last_rendered_image_filepath = options_dict['rendered_image_filepath']
            if 'reference_image_filepath' in options_dict:
                options.last_reference_image_filepath = options_dict['reference_image_filepath']
            if 'auto_rendered_image_load' in options_dict:
                options.auto_image_load = options_dict['auto_rendered_image_load']
            options.save()
            # restart application if user user presses ok
            if theme_changed:
                from PySide2.QtWidgets import QMessageBox
                retval = self._view.view_popup.restart_application_info("")
                if retval == QMessageBox.Ok:
                    self._controller_main.stream.disconnect_socket_stream(True)
                    os.execl(sys.executable, sys.executable, *sys.argv)
        except Exception as e:
            logging.error(e)
            self._view.view_popup.error_saving_options(str(e))
            return
        if self._view.view_options.isVisible():
            self._view.view_options.close()
