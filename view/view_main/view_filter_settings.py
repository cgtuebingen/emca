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

from PySide2.QtGui import QKeyEvent
from core.pyside2_uic import loadUi
from PySide2.QtCore import Slot
from PySide2.QtWidgets import QFormLayout, QLabel, QWidget
from PySide2.QtWidgets import QApplication
from PySide2.QtWidgets import QListWidgetItem
from PySide2.QtCore import Qt
from core.point import Point2f, Point2i, Point3f, Point3i
from core.color import Color4f
import os
from filter.filter_settings import FilterType

from model.pixel_data import PixelData

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from controller.controller import Controller
else:
    from typing import Any as Controller


class FilterListItem(QWidget):

    """
        FilterListItem
        Represents a filter list item holding information about the filter
    """

    def __init__(self, filter_settings):
        QWidget.__init__(self)

        self._idx = filter_settings.get_idx()

        layout = QFormLayout()
        d_type = filter_settings.get_type()
        constraint = filter_settings.get_constraint()
        text = filter_settings.get_text()

        if d_type is FilterType.SCALAR:
            layout.addRow("Scalar:", QLabel(text))
            layout.addRow("val: ", QLabel(str(constraint[0])))
        elif d_type is FilterType.POINT2:
            layout.addRow("Point2:", QLabel(""))
            layout.addRow("x: ", QLabel(str(constraint[0])))
            layout.addRow("y: ", QLabel(str(constraint[1])))
        elif d_type is FilterType.POINT3:
            layout.addRow("Point3:", QLabel(text))
            layout.addRow("x: ", QLabel(str(constraint[0])))
            layout.addRow("y: ", QLabel(str(constraint[1])))
            layout.addRow("z: ", QLabel(str(constraint[2])))
        elif d_type is FilterType.COLOR3:
            layout.addRow("Color3:", QLabel(text))
            layout.addRow("r: ", QLabel(str(constraint[0])))
            layout.addRow("g: ", QLabel(str(constraint[1])))
            layout.addRow("b: ", QLabel(str(constraint[2])))
        self.setLayout(layout)

    def get_idx(self):
        """
        Returns an index referencing the filter settings index
        :return: integer
        """
        return self._idx


class ViewFilterSettings(QWidget):

    """
        ViewFilter
        Handles the view and all filter interactions
    """

    def __init__(self, parent=None):
        QWidget.__init__(self, parent=None)
        ui_filepath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ui', 'filter.ui'))
        loadUi(ui_filepath, self)

        self._controller = None

        # center widget depending on screen size
        desktop_widget = QApplication.desktop()
        screen_rect = desktop_widget.availableGeometry(self)
        self.move(screen_rect.center() - self.rect().center())

        self._filter_items = {}

        self.combItems.currentTextChanged.connect(self.update_stacked_widget)
        self.btnClose.clicked.connect(self.close)

        self.cbPoint2.stateChanged.connect(self.state_changed)
        self.cbPoint3.stateChanged.connect(self.state_changed)
        self.cbColor.stateChanged.connect(self.state_changed)

        self.leExpX.textChanged.connect(self.le_point_2x)
        self.leExpY.textChanged.connect(self.le_point_2y)
        self.leExpX_2.textChanged.connect(self.le_point_3x)
        self.leExpY_2.textChanged.connect(self.le_point_3y)
        self.leExpZ.textChanged.connect(self.le_point_3z)
        self.leExpR.textChanged.connect(self.le_color_r)
        self.leExpG.textChanged.connect(self.le_color_g)
        self.leExpB.textChanged.connect(self.le_color_b)

        self.filterList.setStyleSheet("QListWidget::item { border-bottom: 1px solid black; }")

    def set_controller(self, controller : Controller):
        """
        Sets the connection to the controller
        :param controller: Controller
        :return:
        """
        self._controller = controller
        self.btnClearAll.clicked.connect(controller.filter.clear_filter)
        self.btnApplyFilter.clicked.connect(controller.filter.apply_filters)
        self.btnDeleteFilter.clicked.connect(controller.filter.delete_filter)
        self.btnAddFilter.clicked.connect(controller.filter.add_filter)

    def clear(self):
        """
        Prepare view for new incoming data
        """
        # self._filter_items.clear()
        self.combItems.clear()

    def init_data(self, pixel_data : PixelData):
        """
        Initialise the view
        """
        # iterate through all paths and their vertices
        for _, path in pixel_data.dict_paths.items():

            # pathinfo stuff sample_idx, final_estimate, path_depth
            if path.sample_idx:
                if not self._filter_items.get('sampleIndex', None):
                    self._filter_items['sampleIndex'] = path.sample_idx

            if path.valid_depth:
                if not self._filter_items.get('pathDepth', None):
                    self._filter_items['pathDepth'] = path.path_depth

            if path.final_estimate is not None:
                if not self._filter_items.get('finalEstimate', None) is not None:
                    self._filter_items['finalEstimate'] = path.final_estimate

            # add path user data
            for key_user, value_user in path.data.items():
                # add item if not in list
                if self._filter_items.get(key_user, None) is not None:
                    self._filter_items[key_user] = value_user

            # iterate over intersection points
            for _, its in path.intersections.items():
                for key_user, value_user in its.data.items():
                    # add item if not in list
                    if not self._filter_items.get(key_user, None) is None:
                        self._filter_items[key_user] = value_user

        # add all values to combBox
        for key, _ in self._filter_items.items():
            self.combItems.addItem(key)

        # update expression view on current item
        if self.combItems.count() > 0:
            self.update_stacked_widget(self.combItems.currentText())

    def is_active(self):
        """
        Returns if filtering is active
        :return: boolean
        """
        return self.cbFilterEnabled.isChecked()

    def keyPressEvent(self, event : QKeyEvent):
        """
        Handles key press enter events.
        Checks if the enter key is pressed to apply the filter
        """
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self._controller.filter.add_filter(True)

    @Slot(str, name='update_stacked_widget')
    def update_stacked_widget(self, text):
        """
        Updates the stacked widget view handling the constraints inputs
        :param text: string
        :return:
        """
        item = self._filter_items.get(text, None)
        if item is not None:
            """
                Index   - Widget:
                0       - bool, float, int, string
                1       - Point2
                2       - Point3
                3       - Color3
            """
            if isinstance(item, bool) or isinstance(item, float) or isinstance(item, int) or isinstance(item, str):
                self.stackedWidget.setCurrentIndex(0)
            elif isinstance(item, Point2f) or isinstance(item, Point2i):
                self.stackedWidget.setCurrentIndex(1)
            elif isinstance(item, Point3f) or isinstance(item, Point3i):
                self.stackedWidget.setCurrentIndex(2)
            elif isinstance(item, Color4f):
                self.stackedWidget.setCurrentIndex(3)

    @Slot(str, name='le_point_2x')
    def le_point_2x(self, text):
        if self.cbPoint2.isChecked():
            self.leExpY.blockSignals(True)
            self.leExpY.setText(text)
            self.leExpY.blockSignals(False)

    @Slot(str, name='le_point_2y')
    def le_point_2y(self, text):
        if self.cbPoint2.isChecked():
            self.leExpX.blockSignals(True)
            self.leExpX.setText(text)
            self.leExpX.blockSignals(False)

    @Slot(str, name='le_point_3x')
    def le_point_3x(self, text):
        if self.cbPoint3.isChecked():
            self.leExpY_2.blockSignals(True)
            self.leExpZ.blockSignals(True)
            self.leExpY_2.setText(text)
            self.leExpZ.setText(text)
            self.leExpY_2.blockSignals(False)
            self.leExpZ.blockSignals(False)

    @Slot(str, name='le_point_3y')
    def le_point_3y(self, text):
        if self.cbPoint3.isChecked():
            self.leExpX_2.blockSignals(True)
            self.leExpZ.blockSignals(True)
            self.leExpX_2.setText(text)
            self.leExpZ.setText(text)
            self.leExpX_2.blockSignals(False)
            self.leExpZ.blockSignals(False)

    @Slot(str, name='le_point_3z')
    def le_point_3z(self, text):
        if self.cbPoint3.isChecked():
            self.leExpX_2.blockSignals(True)
            self.leExpY_2.blockSignals(True)
            self.leExpX_2.setText(text)
            self.leExpY_2.setText(text)
            self.leExpX_2.blockSignals(False)
            self.leExpY_2.blockSignals(False)

    @Slot(str, name='le_color_r')
    def le_color_r(self, text):
        if self.cbColor.isChecked():
            self.leExpG.blockSignals(True)
            self.leExpB.blockSignals(True)
            self.leExpG.setText(text)
            self.leExpB.setText(text)
            self.leExpG.blockSignals(False)
            self.leExpB.blockSignals(False)

    @Slot(str, name='le_color_g')
    def le_color_g(self, text):
        if self.cbColor.isChecked():
            self.leExpR.blockSignals(True)
            self.leExpB.blockSignals(True)
            self.leExpR.setText(text)
            self.leExpB.setText(text)
            self.leExpR.blockSignals(False)
            self.leExpB.blockSignals(False)

    @Slot(str, name='le_color_b')
    def le_color_b(self, text):
        if self.cbColor.isChecked():
            self.leExpR.blockSignals(True)
            self.leExpG.blockSignals(True)
            self.leExpR.setText(text)
            self.leExpG.setText(text)
            self.leExpR.blockSignals(False)
            self.leExpG.blockSignals(False)

    @Slot(int, name='state_changed')
    def state_changed(self, state):
        if state != Qt.Checked:
            return
        idx = self.stackedWidget.currentIndex()
        if idx == 1:
            self.leExpY.setText(self.leExpX.text())
        elif idx == 2:
            self.leExpY_2.setText(self.leExpX_2.text())
            self.leExpZ.setText(self.leExpX_2.text())
        elif idx == 3:
            self.leExpG.setText(self.leExpR.text())
            self.leExpB.setText(self.leExpR.text())

    def add_filter_to_view(self, filter_settings):
        """
        Adds a filter to the filter list
        :param filter_settings:
        :return:
        """
        fi = FilterListItem(filter_settings)
        item = QListWidgetItem()
        item.setSizeHint(fi.sizeHint())
        idx = self.stackedWidget.currentIndex()
        self.filterList.addItem(item)
        self.filterList.setItemWidget(item, fi)
        self.clear_line_edit_entries(idx)

    def is_line_edit_empty(self, index):
        """
        Checks if a input is empty
        :param index:
        :return:
        """
        if index == 0:
            return self.leExp.text() == ""
        elif index == 1:
            if self.cbPoint2.isChecked():
                return self.leExpX.text() == ""
            return self.leExpX.text() == "" and self.leExpY.text() == ""
        elif index == 2:
            if self.cbPoint3.isChecked():
                return self.leExpX_2.text() == ""
            return self.leExpX_2.text() == "" and self.leExpY_2.text() == "" and self.leExpZ.text() == ""
        elif index == 3:
            if self.cbColor.isChecked():
                return self.leExpR.text() == ""
            return self.leExpR.text() == "" and self.leExpG.text() == "" and self.leExpB.text() == ""

    def clear_line_edit_entries(self, index):
        """
        Clears all line entries of the current view
        :param index: integer
        :return:
        """
        if index == 0:
            self.leExp.clear()
        elif index == 1:
            self.leExpX.clear()
            self.leExpY.clear()
        elif index == 2:
            self.leExpX_2.clear()
            self.leExpY_2.clear()
            self.leExpZ.clear()
        elif index == 3:
            self.leExpR.clear()
            self.leExpG.clear()
            self.leExpB.clear()
