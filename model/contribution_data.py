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
import logging
import time
import typing

from model.path_data import PathData
from model.pixel_data import PixelData


class SampleContributionData(object):

    """
        SampleContributionData
        Represents all final estimate values of n traced paths where n stands for the amount of samples.
        A final estimate value is represented by a color4f type.
    """

    def __init__(self):
        self._data_loaded = False
        self._path_indices = None
        self._red = None
        self._green = None
        self._blue = None
        self._mean = None
        self._luminance = None
        self._depth = None

    def update_pixel_data(self, pixel_data : PixelData) -> bool:
        try:
            start = time.time()

            self._path_indices = pixel_data.get_indices()

            # collect final estimates of all paths,
            # if one final estimate is not set take [-1,-1,-1, 1] as value
            estimates = []
            depths = []
            for path in pixel_data.dict_paths.values():
                depths.append(path.intersection_count)
                if path.final_estimate is None:
                    logging.info('no final estimate set on server')
                    estimates.append([-1, -1, -1, 1])
                    continue
                estimates.append(path.final_estimate)

            rgb_values = np.array(estimates)

            # get r,g,b values final estimate
            self._red   = rgb_values[:, 0]
            self._green = rgb_values[:, 1]
            self._blue  = rgb_values[:, 2]

            self._depth = np.array(depths)

            # compute the mean of all rgb values
            self._mean = np.mean(rgb_values, axis=1)
            # also compute luminance
            self._luminance = self._red * 0.212671 + self._green * 0.715160 + self._blue * 0.072169

            logging.info('generated plot data in: {}s'.format(time.time() - start))
        except Exception as e:
            logging.error("Error generation sample contribution data: {}".format(e))
            return False
        self._data_loaded = True
        return True

    @property
    def data_loaded(self) -> bool:
        """
        Returns true if a set of data is loaded
        """
        return self._data_loaded

    @property
    def indices(self) -> np.ndarray:
        """
        Returns the values of the x-axis as a numpy array
        """
        return self._path_indices

    @property
    def red(self) -> np.ndarray:
        """
        Returns the red values of all final estimate values as a numpy array
        """
        return self._red

    @property
    def green(self) -> np.ndarray:
        """
        Returns the green values of all final estimate values as a numpy array
        """
        return self._green

    @property
    def blue(self) -> np.ndarray:
        """
        Returns the blue values of all final estimate values as a numpy array
        """
        return self._blue

    @property
    def mean(self) -> np.ndarray:
        """
        Returns the mean of all final estimate values as a numpy array
        """
        return self._mean

    @property
    def luminance(self) -> np.ndarray:
        """
        Returns the luminance of all final estimate values as a numpy array
        """
        return self._luminance

    @property
    def depth(self) -> np.ndarray:
        """
        Returns the depth of all final estimate values as a numpy array
        """
        return self._depth

    def clear(self):
        """
        Clears all data sets
        """
        self._path_indices = None
        self._mean = None
        self._luminance = None
        self._depth = None
        self._red = None
        self._green = None
        self._blue = None
