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

import re
from enum import Enum


class FilterType(Enum):
    SCALAR = 0
    POINT2 = 1
    POINT3 = 2
    COLOR3 = 3


class FilterSettings(object):

    """
        FilterSettings
        Representing a container holding information about a filter
    """

    def __init__(self, view):
        self._idx = view.filterList.count()
        self._text = view.combItems.currentText()

        idx = view.stackedWidget.currentIndex()

        if idx == 0:
            self._type = FilterType.SCALAR
            self._constraint = (view.leExp.text(),)
        elif idx == 1:
            self._type = FilterType.POINT2
            self._constraint = (view.leExpX.text(),
                                view.leExpY.text(),
                                view.cbPoint2.isChecked())
        elif idx == 2:
            self._type = FilterType.POINT3
            self._constraint = (view.leExpX_2.text(),
                                view.leExpY_2.text(),
                                view.leExpZ.text(),
                                view.cbPoint3.isChecked())
        elif idx == 3:
            self._type = FilterType.COLOR3
            self._constraint = (view.leExpR.text(),
                                view.leExpG.text(),
                                view.leExpB.text(),
                                view.cbColor.isChecked())

    def get_idx(self):
        """
        Returns the filter index
        :return: integer
        """
        return self._idx

    def get_type(self):
        """
        Returns the filter type
        :return: FilterType
        """
        return self._type

    def get_text(self):
        """
        Returns the text
        :return: string
        """
        return self._text

    def get_constraint(self):
        """
        Returns the constraint
        :return: string
        """
        return self._constraint

    @staticmethod
    def get_expr_from_string(regex_expr, string):
        """
        Returns a expr from a string depending on the given regex expression
        :param regex_expr: regex expression
        :param string: string
        :return:
        """
        s = re.search(regex_expr, string)
        if s:
            return s.group(0)
        else:
            return ""

    def get_expr(self):
        """
        Returns the entered expression symbol
        :return:
        """
        regex_expr = '[<!=>]+'
        if self._type is FilterType.SCALAR:
            return self.get_expr_from_string(regex_expr, self._constraint[0])
        elif self._type is FilterType.POINT2:
            x = self.get_expr_from_string(regex_expr, self._constraint[0])
            if self._constraint[2]:
                return x, x
            y = self.get_expr_from_string(regex_expr, self._constraint[1])
            return x, y
        elif self._type is FilterType.POINT3 or self._type is FilterType.COLOR3:
            x = self.get_expr_from_string(regex_expr, self._constraint[0])
            if self._constraint[3]:
                return x, x, x
            y = self.get_expr_from_string(regex_expr, self._constraint[1])
            z = self.get_expr_from_string(regex_expr, self._constraint[2])
            return x, y, z

    def get_value(self):
        """
        Returns the entered value
        :return:
        """
        regex_value = '[+-]?([0-9]*[.,])?[0-9]+'
        if self._type is FilterType.SCALAR:
            expr = self.get_expr_from_string(regex_value, self._constraint[0])
            if expr != "":
                return float(expr)
            return re.sub('[<!=>]+', '', self._constraint[0])
        elif self._type is FilterType.POINT2:
            expr_x = self.get_expr_from_string(regex_value, self._constraint[0])
            expr_y = self.get_expr_from_string(regex_value, self._constraint[1])
            if expr_x != "" and expr_y != "":
                return float(expr_x), float(expr_y)
            elif expr_x != "" and expr_y == "":
                return float(expr_x), 0
            elif expr_x == "" and expr_y != "":
                return 0, float(expr_y)
            else:
                return 0, 0
        elif self._type is FilterType.POINT3 or self._type is FilterType.COLOR3:
            expr_x = self.get_expr_from_string(regex_value, self._constraint[0])
            expr_y = self.get_expr_from_string(regex_value, self._constraint[1])
            expr_z = self.get_expr_from_string(regex_value, self._constraint[2])
            if expr_x != "" and expr_y != "" and expr_z != "":
                return float(expr_x), float(expr_y), float(expr_z)
            elif expr_x != "" and expr_y != "" and expr_z == "":
                return float(expr_x), float(expr_y), 0
            elif expr_x != "" and expr_y == "" and expr_z != "":
                return float(expr_x), 0, float(expr_z)
            elif expr_x == "" and expr_y != "" and expr_z != "":
                return 0, float(expr_y), float(expr_z)
            elif expr_x == "" and expr_y == "" and expr_z != "":
                return 0, 0, float(expr_z)
            elif expr_x != "" and expr_y == "" and expr_z == "":
                return float(expr_x), 0, 0
            elif expr_x == "" and expr_y != "" and expr_z == "":
                return 0, float(expr_y), 0
            else:
                return 0, 0, 0

    def to_string(self):
        """
        Returns a string with class information
        :return:
        """
        return "FilterType: {} " \
               "Text: {}" \
               "Constraint: {}".format(self._type, self._text, self._constraint)