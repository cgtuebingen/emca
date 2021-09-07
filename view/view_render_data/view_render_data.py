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

from core.items_tree_node import PathNodeItem
from core.items_tree_node import IntersectionNodeItem
from core.color3 import Color3f

from core.pyside2_uic import loadUi
from PySide2.QtWidgets import QWidget
from PySide2.QtWidgets import QTreeWidgetItem
from PySide2.QtCore import QItemSelectionModel, Slot
from PySide2.QtGui import QPixmap
from PySide2.QtGui import QColor
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QAbstractItemView
import numpy as np
import os


class ViewRenderData(QWidget):

    """
        ViewRenderData
        Handles the view of the Render data containing all information about the selected pixel and its traced paths.
        Moreover, all user added data will be visualized here as tree structure.
    """

    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        ui_filepath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ui', 'render_data.ui'))
        loadUi(ui_filepath, self)

        self.tree.setHeaderLabels(["Item", "Value"])
        self.tree.setColumnWidth(0, 200)
        self._controller = None

        self.tree.itemSelectionChanged.connect(self.select_tree_item)
        self.tree.setSelectionMode(QAbstractItemView.ExtendedSelection)

        # connect buttons
        self.btnShowAll.clicked.connect(self.show_all_traced_paths)
        self.btnInspect.clicked.connect(self.inspect_selected_paths)
        self.cbExpand.toggled.connect(self.expand_items)

    def set_controller(self, controller):
        """
        Sets the connection to the controller
        :param controller: Controller
        :return:
        """
        self._controller = controller

    def enable_view(self, enabled):
        self.btnShowAll.setEnabled(enabled)
        self.btnInspect.setEnabled(enabled)
        self.cbExpand.setEnabled(enabled)

    def show_path_data(self, indices, render_data):
        """
        Load path render data depending on indices input
        :param indices: np.array([])
        :param render_data: RenderData
        :return:
        """
        self.tree.clear()
        for i in indices:
            self.add_path_data_node(render_data.dict_paths[i])
        self.expand_items(self.cbExpand.isChecked())

    @Slot(bool, name='show_all_traced_paths')
    def show_all_traced_paths(self, clicked):
        self._controller.show_all_traced_paths(True)

    @Slot(name='select_tree_item')
    def select_tree_item(self):
        """
        Handles if a path or intersection node is selected. Informs the controller about the selected index
        :param item: QTreeWidgetItem
        :return:
        """

        if self.tree.state() == QAbstractItemView.DragSelectingState:
            return

        num_items = len(self.tree.selectedItems())

        if num_items == 0:
            self._controller.select_path(None)
            return

        if num_items > 1:
            return

        item = self.tree.selectedItems()[0]

        if isinstance(item, PathNodeItem):
            self._controller.select_path(item.index)
        elif isinstance(item, IntersectionNodeItem):
            self._controller.select_intersection(item.path_index, item.intersection_index)

    @Slot(bool, name='inspect_selected_paths')
    def inspect_selected_paths(self, clicked):
        """
        Handles the button input of inspect,
        removes all other paths except the selected one(s)
        :param clicked: boolean
        :return:
        """

        items = self.tree.selectedItems()
        indices = []

        for item in items:
            if isinstance(item, PathNodeItem):
                indices.append(item.index)
            elif isinstance(item, IntersectionNodeItem):
                indices.append(item.path_index)

        indices = np.unique(np.array(indices, dtype=np.int32))
        self._controller.update_path(indices, False)

    @Slot(bool, name='expand_items')
    def expand_items(self, state):
        """
        Depending on state, expands the tree view and shows all child items.
        :param state: boolean
        :return:
        """
        if state:
            self.tree.expandAll()
        else:
            self.tree.collapseAll()

    def select_path(self, index):
        """
        Select/Highlight a path node depending on the input index
        :param index: integer - path_index
        :return:
        """
        self.tree.blockSignals(True)
        for i in range(0, self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            if isinstance(item, PathNodeItem):
                if item.index == index:
                    self.tree.setCurrentItem(item)
                    break
        self.tree.blockSignals(False)

    def select_intersection(self, path_idx, its_idx):
        """
        Select/Highlight a intersection node depending on the input tuple tpl
        """
        self.tree.blockSignals(True)
        for i in range(0, self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            if isinstance(item, PathNodeItem):
                if item.index == path_idx:
                    for j in range(0, item.childCount()):
                        item_child = item.child(j)
                        if isinstance(item_child, IntersectionNodeItem):
                            if path_idx == item_child.path_index and its_idx == item_child.intersection_index:
                                self.tree.setCurrentItem(item_child)
                                break
                    break
        self.tree.blockSignals(False)

    def add_path_data_node(self, path_data):
        """
        Adds path data to a path node
        :param path_data:
        :return:
        """
        path = PathNodeItem(path_data.sample_idx)
        path.setText(0, "Path ({})".format(path_data.sample_idx))
        self.add_path_info_node(path, path_data)
        for its in path_data.intersections.values():
            self.add_intersection_node(path, its)
        self.tree.addTopLevelItem(path)

    def add_path_info_node(self, parent : PathNodeItem, path_data):
        """
        Adds path information data to a path node
        :param parent:
        :param path_data:
        :return:
        """
        path_info = QTreeWidgetItem()
        path_info.setText(0, "Info")
        #self.add_child_item_node(path_info, "Sample Index", str(path_data.sample_idx))
        self.add_child_item_node(path_info, "Path Depth", str(path_data.path_depth))
        # add color icon to the path
        [r, g, b] = path_data.final_estimate.to_list_srgb()
        color = QColor(r, g, b)
        icon = QIcon()
        pixmap = QPixmap(16,16)
        pixmap.fill(color)
        icon.addPixmap(pixmap)
        parent.setIcon(1, pixmap)
        parent.setText(1, str(path_data.final_estimate))
        parent.setToolTip(1, path_data.final_estimate.to_string())
        #self.add_child_item_node(path_info, "Final Estimate", str(path_data.final_estimate), color)
        self.add_child_item_node(path_info, "Origin", str(path_data.path_origin))
        self.add_user_data_to_node(path_info, path_data)
        parent.addChild(path_info)

    def add_intersection_node(self, parent : PathNodeItem, its):
        """
        Adds a intersection node and all of its information within a node
        :param parent:
        :param its: Intersection
        :return:
        """
        its_node = IntersectionNodeItem(parent.index, its.depth_idx)
        its_node.setText(0, "Intersection ({})".format(its.depth_idx))
        if its.pos is not None:
            self.add_child_item_node(its_node, "Position", str(its.pos))
        if its.pos_ne is not None:
            visible_str = " (hit)" if its.is_ne_visible else " (occluded)"
            self.add_child_item_node(its_node, "Pos. NEE"+visible_str, str(its.pos_ne))
        if its.li is not None:
            # add color to the intersection
            [r, g, b] = its.li.to_list_srgb()
            color = QColor(r, g, b)
            icon = QIcon()
            pixmap = QPixmap(16,16)
            pixmap.fill(color)
            icon.addPixmap(pixmap)
            its_node.setIcon(1, pixmap)
            its_node.setText(1, str(its.li))
            its_node.setToolTip(1, its.li.to_string())
            #self.add_child_item_node(its_node, "Estimate", str(its.li), color)
        if its.le is not None:
            # add color to the intersection
            [r, g, b] = its.le.to_list_srgb()
            color = QColor(r, g, b)
            self.add_child_item_node(its_node, "Emission", str(its.le), color)
        self.add_user_data_to_node(its_node, its)
        parent.addChild(its_node)

    def add_user_data_to_node(self, node, user_data):
        """
        Adds the user data which was added by the user as nodes
        :param node:
        :param user_data:
        :return:
        """
        # insert general data
        for key, value in user_data.data.items():
            if isinstance(value, Color3f):
                [r,g,b] = value.to_list_srgb()
                color = QColor(r, g, b)
                self.add_child_item_node(node, str(key), str(value), color)
            else:
                self.add_child_item_node(node, str(key), str(value))

    def add_child_item_node(self, parent, name, value, color=None):
        """
        Adds a child item to a node parent containing name and value
        :param parent:
        :param name:
        :param value:
        :param color: optional QColor to add to the item as an icon
        :return:
        """
        item = QTreeWidgetItem()
        item.setText(0, name)
        item.setText(1, value)
        if isinstance(color, QColor):
            icon = QIcon()
            pixmap = QPixmap(16,16)
            pixmap.fill(color)
            icon.addPixmap(pixmap)
            item.setIcon(1, icon)
        parent.addChild(item)

    def prepare_new_data(self):
        """
        Prepare new data for new incoming data, clears the tree view.
        :return:
        """
        self.tree.clear()
