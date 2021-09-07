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

from filter.filter_settings import FilterSettings
from PySide2.QtCore import Slot
from core.messages import StateMsg
import logging


class ControllerFilter(object):

    """
        ControllerFilter
        Handles the core logic of the filter mechanism.
        Filters RenderData by user input.
    """

    def __init__(self, parent, model, view):

        self._controller_main = parent
        self._model = model
        self._view = view

    def handle_state_msg(self, tpl):
        """
        Handle current state, messages mostly received from thread,
        which listens on the socket pipeline for incoming messages
        :param tpl: (StateMsg, None or Datatype)
        :return:
        """
        msg = tpl[0]
        if msg is StateMsg.DATA_RENDER:
            # if filter is enabled filter RenderData and send update to MainController.
            if self._view.view_filter.is_active():
                render_data = self._model.render_data
                xs = self._model.filter.apply_filters(render_data)
                self._controller_main.update_path(xs, False)

    @Slot(bool, name='add_filter')
    def add_filter(self, clicked):
        """
        Adds a new filter to the current render data
        :param clicked:
        :return:
        """
        idx = self._view.view_filter.stackedWidget.currentIndex()
        if not self._view.view_filter.is_line_edit_empty(idx):
            fs = FilterSettings(self._view.view_filter)
            self._view.view_filter.add_filter_to_view(fs)
            render_data = self._model.render_data
            xs = self._model.filter.filter(fs, render_data)
            if xs is None:
                logging.error("Issue with filter ...")
                return
            self._controller_main.update_path(xs, False)

    @Slot(bool, name='apply_filters')
    def apply_filters(self, clicked):
        """
        Applies all current active filters to the current render data
        :param clicked: boolean
        :return:
        """
        if self._view.view_filter.filterList.count() > 0:
            render_data = self._model.render_data
            xs = self._model.filter.apply_filters(render_data)
            self._controller_main.update_path(xs, False)
        else:
            pass

    @Slot(bool, name='clear_filter')
    def clear_filter(self, clicked):
        """
        Informs the controller to clear all filters
        :param clicked: boolean
        :return:
        """
        self._model.filter.clear_all()
        self._view.view_filter.filterList.clear()

    @Slot(bool, name='delete_filter')
    def delete_filter(self, clicked):
        """
        Deletes the marked filter and updates the filtered render data.
        Paths which were deleted by the selected filter will be displayed again
        :param clicked: boolean
        :return:
        """
        if self._view.view_filter.filterList.count() > 0:
            item = self._view.view_filter.filterList.currentItem()
            if item:
                w = self._view.view_filter.filterList.itemWidget(item)
                row = self._view.view_filter.filterList.row(item)
                i = self._view.view_filter.filterList.takeItem(row)
                xs = self._model.filter.delete_filter(w.get_idx())
                self._controller_main.update_path(xs, False)
                del i
