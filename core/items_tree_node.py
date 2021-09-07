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

from PySide2.QtWidgets import QTreeWidgetItem


class PathNodeItem(QTreeWidgetItem):

    """
        PathNodeItem
        Represents a Path Node within the tree view of the View Render Data
        Holds the path index if this item is selected.
        Necessary to know which path item is selected by the user.
    """

    def __init__(self, index):
        QTreeWidgetItem.__init__(self)
        self._index = index

    @property
    def index(self):
        """
        Returns the node index representing the path index
        :return:
        """
        return self._index


class IntersectionNodeItem(QTreeWidgetItem):

    """
        IntersectionNodeItem
        Represents a IntersectionNode within the tree view of the View Render Data
        Holds information about the parent index and the intersection index.
        Necessary to know which intersection and path item is selected by the user.
    """

    def __init__(self, path_index, intersection_index):
        QTreeWidgetItem.__init__(self)

        self._path_index = path_index
        self._intersection_index = intersection_index

    @property
    def path_index(self):
        """
        Returns the index of the parent, representing the path index
        :return: integer
        """
        return self._path_index

    @property
    def intersection_index(self):
        """
        Returns the intersection index
        :return: integer
        """
        return self._intersection_index
