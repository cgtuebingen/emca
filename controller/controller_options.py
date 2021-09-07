from PySide2.QtWidgets import QFileDialog
import logging
import os


class ControllerOptions(object):

    """
        ControllerOptions
        Handles pre-loaded options, the theme and image dialogs.
    """

    def __init__(self, parent, model, view):
        self._controller_main = parent
        self._view = view
        self._model = model

    def get_theme(self):
        return self._model.options_data.get_theme()

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
        last_hostname = 'localhost'
        last_port = 50013
        if options.is_last_hostname_set():
            last_hostname = options.get_last_hostname()
        if options.is_last_port_set():
            last_port = options.get_last_port()
        # update connect view about last settings
        self._view.view_connect.set_hostname_and_port(last_hostname, last_port)
        if options.get_option_auto_connect():
            self._controller_main.stream.connect_socket_stream(last_hostname, last_port)
        if options.get_option_auto_image_load():
            filepath = options.get_last_rendered_image_filepath()
            success = False
            try:
                success = self._view.view_render_image.load_hdr_image(filepath)
                if success and options.is_last_reference_image_filepath_set():
                    ref_file = options.get_last_reference_image_filepath()
                    self._view.view_render_image.load_hdr_image(ref_file, True)
            except Exception as e:
                logging.error(e)
                self._view.view_popup.error_on_loading_pre_saved_image(str(e))
            if success:
                self._view.view_render_image.enable_view(True)
                self._view.view_render_image.reset(True)

    def open_options(self, clicked):
        options = self._model.options_data
        theme = options.get_theme()
        # default dark otherwise light
        if theme == 'light':
            self._view.view_options.enable_light_theme(True)
        else:
            self._view.view_options.enable_dark_theme(True)

        self._view.view_options.set_auto_connect(options.get_option_auto_connect())
        self._view.view_options.set_auto_scene_load(options.get_option_auto_scene_load())
        self._view.view_options.set_auto_image_load(options.get_option_auto_image_load())
        self._view.view_options.show()

    def save_options(self, options_dict):
        try:
            theme_changed = False
            options = self._model.options_data
            if 'theme' in options_dict:
                if options.get_theme() != options_dict['theme']:
                    theme_changed = True
            if 'auto_connect' in options_dict:
                options.set_options_auto_connect(options_dict['auto_connect'])
            if 'auto_scene_load' in options_dict:
                options.set_option_auto_scene_load(options_dict['auto_scene_load'])
            if 'rendered_image_filepath' in options_dict:
                options.set_last_rendered_image_filepath(options_dict['rendered_image_filepath'])
            if 'auto_rendered_image_load' in options_dict:
                options.set_option_auto_image_load(options_dict['auto_rendered_image_load'])
            # restart application if user user presses ok
            if theme_changed:
                from PySide2.QtWidgets import QMessageBox
                retval = self._view.view_popup.restart_application_info("Theme change in progress ...")
                if retval == QMessageBox.Ok:
                    options.set_theme(options_dict['theme'])
                    options.save()
                    import sys
                    python = sys.executable
                    os.execl(python, python, *sys.argv)
            else:
                options.save()
        except Exception as e:
            logging.error(e)
            self._view.view_popup.error_saving_options(str(e))
            return
        if self._view.view_options.isVisible():
            self._view.view_options.close()
