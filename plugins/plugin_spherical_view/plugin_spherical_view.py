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

from core.plugin import Plugin, PluginType
from model.pixel_data import PixelData
from plugins.plugin_spherical_view.view_spherical_view_image import ViewSphericalViewImage
from core.point import Point2i
from core.pyside2_uic import loadUi
import io
import os
import logging


class SphericalView(Plugin):

    """
        SphericalView Plugins (mitsuba)
        PluginType is ServerPlugin since data is generated on server side
    """

    def __init__(self):
        Plugin.__init__(self, "SphericalView", 66, PluginType.SERVER_PLUGIN)
        ui_filepath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'ui', 'spherical_view.ui'))
        loadUi(ui_filepath, self)

        self._path = None
        self._pixel_data = None
        self._render_size = Point2i(256, 128)
        self._sample_count = 16
        self._integrator = "path"

        self._spherical_view = ViewSphericalViewImage(self)
        self.hdrImage.addWidget(self._spherical_view)

    def apply_theme(self, theme):
        pass

    def prepare_new_data(self):
        self._spherical_view.clear()
        self._spherical_view.enable_buttons(False)

    def update_path_indices(self, indices):
        pass

    def select_path(self, index):
        pass

    def select_intersection(self, path_idx, its_idx):
        if self._pixel_data:
            dict_paths = self._pixel_data.dict_paths
            self._spherical_view.select_intersection(dict_paths, path_idx, its_idx)

    def serialize(self, stream):
        logging.info("Serialize in: {}".format(self.name))
        if self._spherical_view.pos is not None:
            self._render_size.x = self.sbWidth.value()
            self._render_size.y = self.sbHeight.value()
            self._sample_count = int(self.sbSampleCount.value())
            self._integrator = self.integrator.text()
            # send package id
            stream.write_short(self.flag)
            # send point / data
            stream.write_float(self._spherical_view.pos.x)
            stream.write_float(self._spherical_view.pos.y)
            stream.write_float(self._spherical_view.pos.z)
            # send amount of samples
            stream.write_int(self._sample_count)
            # send render size
            stream.write_int(self._render_size.x)
            stream.write_int(self._render_size.y)
            # send integrator
            stream.write_string(self._integrator)

    def deserialize(self, stream):
        logging.info("Deserialize in: {}".format(self.name))
        size = stream.read_int()
        if size > 0:
            self._path = io.BytesIO(stream.read(size))
        else:
            self._path = None

    def update_view(self):
        if self._path is None:
            logging.error("Path is None")
            return
        if self._spherical_view.load_hdr_image(self._path):
            if not self._spherical_view.is_btn_enabled:
                self._spherical_view.enable_buttons(True)
            self._spherical_view.update_hightlights()

    def init_pixel_data(self, pixel_data : PixelData):
        self._pixel_data = pixel_data
