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

import typing
import OpenEXR
import Imath
from PIL import Image
from PIL.ImageQt import ImageQt as PilImageQt
from PySide2.QtCore import QPoint
from PySide2.QtGui import QColor, QPixmap
from enum import Enum
import array
import numpy as np
import matplotlib.pyplot as plt
import logging


class SaveType(Enum):
    EXR     = 0
    PNG     = 1


class HDRImage(object):

    """
        HDRImage
        Class representing a HDR (exr) image
    """

    def __init__(self):
        self._filepath = None
        self._extension = None
        self._exr = None
        self._exr_ref = None
        self._pixmap = None
        self._exposure = 0.0
        self._falsecolor = False
        self._plusminus = False
        self._show_ref = False

    @property
    def filepath(self):
        return self._filepath

    def load_exr(self, filepath_or_bytestream : typing.Union[str, bytes], reference : bool = False) -> bool:
        """
        Loads an exr file with OpenEXR
        """
        logging.info("Loading EXR ...")
        try:
            if self._pixmap:
                del self._pixmap
                self._pixmap = None
            self._filepath = filepath_or_bytestream
            if reference:
                if self._exr:
                    del self._exr_ref
                    self._exr_ref = None
                self._exr_ref = OpenEXR.InputFile(filepath_or_bytestream)
            else:
                if self._exr:
                    del self._exr
                    self._exr = None
                self._exr = OpenEXR.InputFile(filepath_or_bytestream)

            return True
        except Exception as e:
            logging.error(e)
            return False

    def is_pixmap_set(self) -> bool:
        return self._pixmap is not None

    @property
    def exr_image(self):
        """
        Returns the exr image
        :return: OpenEXR
        """
        return self._exr

    @property
    def pixmap(self) -> QPixmap:
        """
        Returns the render image as pixmap
        """
        if self._pixmap is None:
            #update pixmap if needed
            try:
                pt = Imath.PixelType(Imath.PixelType.FLOAT)

                if not self._show_ref or self._plusminus:
                    if self._exr is None:
                        return None

                    r_str = self._exr.channel('R', pt)
                    g_str = self._exr.channel('G', pt)
                    b_str = self._exr.channel('B', pt)

                    r = np.frombuffer(r_str, dtype=np.float32)
                    g = np.frombuffer(g_str, dtype=np.float32)
                    b = np.frombuffer(b_str, dtype=np.float32)

                if self._show_ref or self._plusminus:
                    if self._exr_ref is None:
                        return None

                    r_str = self._exr_ref.channel('R', pt)
                    g_str = self._exr_ref.channel('G', pt)
                    b_str = self._exr_ref.channel('B', pt)

                    r_ref = np.frombuffer(r_str, dtype=np.float32)
                    g_ref = np.frombuffer(g_str, dtype=np.float32)
                    b_ref = np.frombuffer(b_str, dtype=np.float32)

                if self._plusminus:
                    r = r-r_ref
                    g = g-g_ref
                    b = b-b_ref
                elif self._show_ref:
                    r = r_ref
                    g = g_ref
                    b = b_ref

                # apply exposure
                if self._exposure == 0:
                    r_exp = r
                    g_exp = g
                    b_exp = b
                else:
                    exposure_factor = np.power(2.0, self._exposure)

                    r_exp = r*exposure_factor
                    g_exp = g*exposure_factor
                    b_exp = b*exposure_factor

                if self._plusminus:
                    self._pixmap = self.create_pixmap_pm(r_exp, g_exp, b_exp)
                elif self._falsecolor:
                    self._pixmap = self.create_pixmap_fc(r_exp, g_exp, b_exp)
                else:
                    self._pixmap = self.create_pixmap_srgb(r_exp, g_exp, b_exp)
            except Exception as e:
                logging.error("Error " + str(e))

        return self._pixmap

    @property
    def exposure(self) -> float:
        return self._exposure

    @exposure.setter
    def exposure(self, exposure : float):
        if self._exposure != exposure:
            self._pixmap = None
        self._exposure = exposure

    @property
    def falsecolor(self) -> bool:
        return self._falsecolor

    @falsecolor.setter
    def falsecolor(self, falsecolor : bool):
        if self._falsecolor != falsecolor:
            self._pixmap = None
        self._falsecolor = falsecolor

    @property
    def plusminus(self) -> bool:
        return self._plusminus

    @plusminus.setter
    def plusminus(self, plusminus : bool):
        if self._plusminus != plusminus:
            self._pixmap = None
        self._plusminus = plusminus

    @property
    def show_ref(self) -> bool:
        return self._show_ref

    @show_ref.setter
    def show_ref(self, show_ref : bool):
        if self._show_ref != show_ref and not self._plusminus:
            self._pixmap = None
        self._show_ref = show_ref

    def create_pixmap_srgb(self, r_exp : np.ndarray, g_exp : np.ndarray, b_exp : np.ndarray) -> QPixmap:
        """
        Converts an srgb image to a pixmap
        """

        #even though this is 2.4, this corresponds to a gamma value of 2.2
        invSRGBGamma = 1.0/2.4

        r_gamma = np.where(r_exp > 0.0031308, ((255.0 * 1.055) * np.power(r_exp, invSRGBGamma) - 0.055), r_exp * (12.92 * 255.0))
        g_gamma = np.where(g_exp > 0.0031308, ((255.0 * 1.055) * np.power(g_exp, invSRGBGamma) - 0.055), g_exp * (12.92 * 255.0))
        b_gamma = np.where(b_exp > 0.0031308, ((255.0 * 1.055) * np.power(b_exp, invSRGBGamma) - 0.055), b_exp * (12.92 * 255.0))

        dw = self._exr.header()['dataWindow']
        size = (dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1)

        srgb = np.uint8([np.uint8(np.clip(r_gamma, 0.0, 255.0)),
                         np.uint8(np.clip(g_gamma, 0.0, 255.0)),
                         np.uint8(np.clip(b_gamma, 0.0, 255.0))]).transpose().reshape([size[1], size[0], 3])

        q_img = PilImageQt(Image.fromarray(srgb, 'RGB'))
        return QPixmap.fromImage(q_img).copy()

    def create_pixmap_fc(self, r_exp : np.ndarray, g_exp : np.ndarray, b_exp : np.ndarray) -> QPixmap:

        #max_intensity = np.max([r_exp,g_exp,b_exp], axis=0)
        avg_intensity = (r_exp+g_exp+b_exp)*(1.0/3.0)
        log_intensity = np.where(avg_intensity > 0.0, np.log2(avg_intensity, where=avg_intensity > 0.0)*0.1+0.5, -float('inf'))

        cmap = plt.get_cmap('viridis')

        dw = self._exr.header()['dataWindow']
        size = (dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1)

        srgb = np.uint8(np.array(cmap(log_intensity))[:,:3]*255.0).reshape([size[1], size[0], 3])
        q_img = PilImageQt(Image.fromarray(srgb, 'RGB'))
        return QPixmap.fromImage(q_img).copy()

    def create_pixmap_pm(self, r_exp : np.ndarray, g_exp : np.ndarray, b_exp : np.ndarray) -> QPixmap:
        pos = np.minimum(255.0, (np.maximum(0.0, r_exp)+np.maximum(0.0, g_exp)+np.maximum(0.0, b_exp))*( 255.0*2.0/3.0))
        neg = np.minimum(255.0, (np.minimum(0.0, r_exp)+np.minimum(0.0, g_exp)+np.minimum(0.0, b_exp))*(-255.0*2.0/3.0))

        dw = self._exr.header()['dataWindow']
        size = (dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1)

        srgb = np.uint8([neg, pos, np.zeros(np.shape(pos))]).transpose().reshape([size[1], size[0], 3])
        q_img = PilImageQt(Image.fromarray(srgb, 'RGB'))
        return QPixmap.fromImage(q_img).copy()

    def save_as_exr(self, filename : str) -> bool:
        """
        Saves the current exr image under the given filename
        """
        try:
            dw = self._exr.header()['dataWindow']
            size = (dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1)

            # Read the three color channels as 32-bit floats
            FLOAT = Imath.PixelType(Imath.PixelType.FLOAT)
            (R, G, B) = [array.array('f', self._exr.channel(Chan, FLOAT)).tolist() for Chan in ("R", "G", "B")]

            """
            # Normalize so that brightest sample is 1
            brightest = max(R + G + B)
            R = [i / brightest for i in R]
            G = [i / brightest for i in G]
            B = [i / brightest for i in B]
            """

            (Rs, Gs, Bs) = [array.array('f', Chan).tostring() for Chan in (R, G, B)]

            out = OpenEXR.OutputFile(filename, OpenEXR.Header(size[0], size[1]))
            out.writePixels({'R': Rs, 'G': Gs, 'B': Bs})
            return True
        except Exception as e:
            logging.error(e)
            return False

    def save_as_png(self, filename : str) -> bool:
        if self._exr is None:
            return False
        return self.pixmap.save(filename, "png")

    def save(self, filename : str, save_type=SaveType.EXR) -> bool:
        if save_type is SaveType.EXR:
            return self.save_as_exr(filename)
        elif save_type is SaveType.PNG:
            return self.save_as_png(filename)
        else:
            logging.info("Wrong SaveType: {}. Image will be saved as EXR".format(save_type))
            return self.save_as_exr(filename)

    def get_pixel_color(self, pixel : QPoint) -> QColor:
        pt = Imath.PixelType(Imath.PixelType.FLOAT)
        r_str = self._exr.channel('R', pt, pixel.y(), pixel.y())
        g_str = self._exr.channel('G', pt, pixel.y(), pixel.y())
        b_str = self._exr.channel('B', pt, pixel.y(), pixel.y())

        r = np.frombuffer(r_str, dtype=np.float32, count=1, offset=4*pixel.x())
        g = np.frombuffer(g_str, dtype=np.float32, count=1, offset=4*pixel.x())
        b = np.frombuffer(b_str, dtype=np.float32, count=1, offset=4*pixel.x())

        #even though this is 2.4, this corresponds to a gamma value of 2.2
        invSRGBGamma = 1.0/2.4

        r_gamma = np.where(r > 0.0031308, ((255.0 * 1.055) * np.power(r, invSRGBGamma) - 0.055), r * (12.92 * 255.0))
        g_gamma = np.where(g > 0.0031308, ((255.0 * 1.055) * np.power(g, invSRGBGamma) - 0.055), g * (12.92 * 255.0))
        b_gamma = np.where(b > 0.0031308, ((255.0 * 1.055) * np.power(b, invSRGBGamma) - 0.055), b * (12.92 * 255.0))

        logging.info(r_gamma)
        logging.info(g_gamma)
        logging.info(b_gamma)

        srgb = np.uint8([np.uint8(np.clip(r_gamma, 0.0, 255.0)),
                         np.uint8(np.clip(g_gamma, 0.0, 255.0)),
                         np.uint8(np.clip(b_gamma, 0.0, 255.0))]).flatten()

        return QColor(srgb[0], srgb[1], srgb[2])
