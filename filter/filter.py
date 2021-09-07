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

from filter.filter_type import FilterType
import logging
import time
import numpy as np


class Filter(object):

    """
        Filter
        Filters the Render data set depending on user added data.
        (bool, float, point2i, point2f, point3i, point3f, color3f)
        All paths which satisfy the constraints will be displayed
    """

    def __init__(self):
        self._filters = {}
        self._paths = set()

    def path_indices(self):
        """
        Returns a numpy array containing all paths indices which satisfy the filter constraints
        :return:
        """
        xs = np.array(list(self._paths), dtype=np.int32)
        xs.sort()
        return xs

    def clear_all(self):
        """
        Clears the filter view
        :return:
        """
        self._filters.clear()
        self._paths.clear()

    def delete_filter(self, index):
        """
        Deletes a selected filter,
        restores paths which where filtered by the deleted filter.
        Returns a numpy array containing all path indices which satisfy the filter constraints
        :param index: row index of QListWidget
        :return: numpy array with path indices
        """
        del self._filters[index]
        self._paths.clear()
        for f_key, f in self._filters.items():
            self._paths |= f[1]
        return self.path_indices()

    def apply_filters(self, render_data):
        """
        Applies all active filters to a new Render data set.
        Returns a numpy array containing all path indices which satisfy the filter constraints
        :param render_data:
        :return: numpy array with path indices
        """
        # apply filters to new data and update sets of path ids
        self._paths.clear()
        if len(self._filters) > 0:
            for key, f in self._filters.items():
                self.filter(f[0], render_data)
        return self.path_indices()

    def filter(self, filter_settings, render_data):
        """
        Applies a filter item with filter_settings to the Render data
        Returns a numpy array containing all path indices which satisfy the filter constraints
        :param filter_settings:
        :param render_data:
        :return: numpy array with path indices
        """
        start = time.time()
        xs = set()
        search_key = filter_settings.get_text()

        if search_key == "sampleIndex":
            for path_key, path in render_data.dict_paths.items():
                if self.compare(path.sample_idx, filter_settings):
                    xs.add(path_key)
        elif search_key == "pathDepth":
            for path_key, path in render_data.dict_paths.items():
                if self.compare(path.path_depth, filter_settings):
                    xs.add(path_key)
        elif search_key == "finalEstimate":
            for path_key, path in render_data.dict_paths.items():
                if self.compare(path.final_estimate, filter_settings):
                    xs.add(path_key)
        else:
            for path_key, path in render_data.dict_paths.items():
                entry = path.data.get(search_key, None)
                if entry:
                    if self.compare(entry, filter_settings):
                        xs.add(path_key)
                for its_key, its in path.intersections.items():
                    entry = its.data.get(search_key, None)
                    if entry:
                        if self.compare(entry, filter_settings):
                            xs.add(path_key)

        # add filter and its set of keys,
        # has to be updated if new pixel data is requested
        self._filters[filter_settings.get_idx()] = (filter_settings, xs)
        if len(self._paths) > 0:
            self._paths &= xs
        else:
            self._paths |= xs
        logging.info('filtered items in: {}s'.format(time.time() - start))
        return self.path_indices()

    def compare(self, entry, filter_settings):
        """
        Compares the render data value and data type with the user entered value.
        Returns true if the render data entry value satisfy the user entered value.
        :param entry: render data value
        :param filter_settings:
        :return: true or false
        """

        f_type = filter_settings.get_type()
        expr = filter_settings.get_expr()
        value = filter_settings.get_value()
        if f_type is FilterType.SCALAR:
            if isinstance(value, str):
                return self.compare_value(entry, expr, value, True)
            return self.compare_value(entry, expr, value)
        elif f_type is FilterType.POINT2:
            return self.compare_point2(entry,
                                       expr[0], expr[1],
                                       value[0], value[1])
        elif f_type is FilterType.POINT3:
            return self.compare_point3(entry,
                                       expr[0], expr[1], expr[2],
                                       value[0], value[1], value[2])
        elif f_type is FilterType.COLOR3:
            return self.compare_color(entry,
                                      expr[0], expr[1], expr[2],
                                      value[0], value[1], value[2])

    @staticmethod
    def compare_value(val1, expr, val2, is_string=False):
        """
        Checks which compare expression is used and compares depending on the expression the values
        Returns true if val1 satisfy the entered expression
        :param val1: value left
        :param expr: expression
        :param val2: value right
        :param is_string set if value is a string
        :return: true or false
        """
        if is_string:
            if expr == "==":
                return str(val1).lower() == str(val2).lower()
            elif expr == "!=":
                return str(val1).lower() != str(val2).lower()
        else:
            if expr == '>':
                return val1 > val2
            elif expr == '<':
                return val1 < val2
            elif expr == '==':
                return val1 == val2
            elif expr == '>=':
                return val1 >= val2
            elif expr == '<=':
                return val1 <= val2
            elif expr == '!=':
                return val1 != val2
        return False

    def compare_point2(self, point2, expr_x, expr_y, x, y):
        """
        Compares a point2 with given expressions expr_x, expr_y and two values x and y.
        Returns true if the values of point2 satisfy x and y
        :param point2: point2
        :param expr_x: Expression for point.x
        :param expr_y: Expression for point.y
        :param x:
        :param y:
        :return: true or false
        """
        x_val = True
        y_val = True

        if expr_x != "":
            x_val = self.compare_value(point2.x, expr_x, x)

        if expr_y != "":
            y_val = self.compare_value(point2.y, expr_y, y)

        return x_val and y_val

    def compare_point3(self, point3, expr_x, expr_y, expr_z, x, y, z):
        """
        Compares a point3 with given expressions expr_x, expr_y, expr_z and three values x, y and z
        Returns true if the values of point3 satisfy x,y and z
        :param point3: point3
        :param expr_x: Expression for point.x
        :param expr_y: Expression for point.y
        :param expr_z: Expression for point.z
        :param x:
        :param y:
        :param z:
        :return: true or false
        """
        x_val = True
        y_val = True
        z_val = True

        if expr_x != "":
            x_val = self.compare_value(point3.x, expr_x, x)

        if expr_y != "":
            y_val = self.compare_value(point3.y, expr_y, y)

        if expr_z != "":
            y_val = self.compare_value(point3.z, expr_z, z)

        return x_val and y_val and z_val

    def compare_color(self, color, expr_r, expr_g, expr_b, r, g, b):
        """
        Compares a color class with given expressions and compare values.
        Returns true of the color type satisfy all values (r,g,b).
        :param color: colo3f
        :param expr_r:
        :param expr_g:
        :param expr_b:
        :param r: red
        :param g: green
        :param b: blue
        :return: true or false
        """
        red = True
        green = True
        blue = True

        if expr_r != "":
            red = self.compare_value(color.red, expr_r, r)

        if expr_g != "":
            green = self.compare_value(color.green, expr_g, g)

        if expr_b != "":
            blue = self.compare_value(color.blue, expr_b, b)

        return red and green and blue

    def to_string(self):
        """
        Returns a string of all filters
        :return:
        """
        return "{}".format(self._filters)
