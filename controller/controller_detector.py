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

from core.messages import StateMsg
import logging
import typing

from model.model import Model
from view.view_main.main_view import MainView

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from controller.controller import Controller
else:
    from typing import Any as Controller

class ControllerDetector(object):

    """
        ControllerDetector
        Handles the core logic of the detector which is used to determine high variance sample contributions.
        Two methods are currently used.
        1.) based on standard deviation
        2.) ESD by Rosner
    """

    def __init__(self, parent : Controller, model : Model, view : MainView):
        self._controller_main = parent
        self._model = model
        self._view = view
        # init detector view with values from detector class
        self._view.view_detector.init_values(model.detector)

    def handle_state_msg(self, tpl : typing.Tuple[StateMsg, typing.Any]):
        """
        Handle current state, messages mostly received from thread,
        which listens on the socket pipeline for incoming messages
        """
        msg = tpl[0]
        if msg is StateMsg.DATA_PIXEL:
            # check if detector is enabled and run outlier detection
            if self._model.detector.is_active:
                self.run_detector()

    def update_and_run_detector(self, m, alpha, k, pre_filter, is_default, is_active):
        """
        Saves all user changes of the detector
        :param m:
        :param alpha:
        :param k:
        :param pre_filter:
        :param is_default:
        :param is_active:
        :return:
        """
        self._model.detector.update_values(m, alpha, k, pre_filter, is_default, is_active)
        # run detector if sample contribution data is available
        if self._model.final_estimate_data.data_loaded:
            self.run_detector()
        else:
            self._view.view_popup.error_no_final_estimate_data("")

    def run_detector(self):
        """
        Only runs the detector if the checkbox for the detector is active,
        moreover the final estimate data is needed in order to detector outliers
        :return:
        """
        detector = self._model.detector
        if detector.is_active:
            data = self._model.final_estimate_data.mean
            path_outliers_indices = detector.run_outlier_detection(data=data)
            if len(path_outliers_indices) > 0:
                self._controller_main.update_path(path_outliers_indices, False)
            else:
                self._view.view_popup.error_outlier_detector_no_outliers_detected("")
        else:
            self._view.view_popup.error_detector_not_enabled("")

