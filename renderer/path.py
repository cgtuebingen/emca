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

from renderer.shape import Shape
from model.path_data import PathData

import vtk


class Path(Shape):

    """
        Path
        Visualizes one path in the vtkRenderer (3D viewer)
    """

    def __init__(self,
                 idx : int,
                 path_data : PathData):
        self._path_idx = idx
        self._path_data = path_data

        self._visible = False
        self._visible_ne = False

        self._selected_its = None

        # start with an empty mesh - the path is updated afterwards
        super().__init__(vtk.vtkPolyData())

        self.redraw()

    @property
    def path_idx(self) -> int:
        """
        Returns the path index
        """
        return self._path_idx

    @property
    def path_data(self) -> PathData:
        """
        Returns the path data
        """
        return self._path_data

    @property
    def opacity(self) -> float:
        """
        Returns the current path opacity
        :return: float[0,1]
        """
        return self.GetProperty().GetOpacity()

    @opacity.setter
    def opacity(self, value : float):
        self.GetProperty().SetOpacity(value)

    @property
    def line_width(self) -> float:
        """
        Returns the current path size
        :return: float[0,1]
        """
        return self.GetProperty().GetLineWidth()

    @line_width.setter
    def line_width(self, value : float):
        self.GetProperty().SetLineWidth(value)

    @property
    def visible(self) -> bool:
        """
        Returns if the path is visible
        :return: boolean
        """
        return self._visible

    @visible.setter
    def visible(self, visible : bool):
        """
        Sets the visibility of the path object
        """
        changed = self._visible != visible
        self._visible = visible
        if changed:
            self.redraw()

    @property
    def show_ne(self) -> bool:
        """
        Returns if the next event estimations are visible of the path
        """
        return self._visible_ne

    @show_ne.setter
    def show_ne(self, visible : bool):
        """
        Sets the visibility of the next event estimations of the path
        """
        changed = self._visible_ne != visible
        self._visible_ne = visible
        if changed:
            self.redraw()

    def select_intersection(self, its_idx):
        """
        Set the given intersection as selected
        Deselects previously selected intersection in this path (if any)
        """
        self._selected_its = its_idx
        self.redraw()

    def redraw(self):
        #TODO: could probably be a bit more efficient, but it is fast enough...

        # represent the entire path as a single mesh
        points = vtk.vtkPoints()
        line_segments = vtk.vtkCellArray()
        line_segment_colors = vtk.vtkFloatArray()
        line_segment_colors.SetNumberOfComponents(3)

        if self._visible:
            last_key = None
            last_point_index = points.InsertNextPoint(self._path_data.path_origin.x,
                                                      self._path_data.path_origin.y,
                                                      self._path_data.path_origin.z)

            # create lines from intersection points
            for key, its in self._path_data.intersections.items():
                if last_key is not None and last_key+1 != key:
                    # no connection if there is a gap in the key indices
                    last_point_index = None

                point_index = None
                nee_point_index = None

                if its.pos is not None:
                    point_index = points.InsertNextPoint(its.pos.x, its.pos.y, its.pos.z)

                    if last_point_index is not None:
                        line = vtk.vtkLine()
                        line.GetPointIds().SetId(0, last_point_index)
                        line.GetPointIds().SetId(1, point_index)
                        line_segments.InsertNextCell(line)
                        if its.depth_idx == self._selected_its:
                            line_segment_colors.InsertNextTuple3(0.0, 1.0, 0.0)
                        elif its.le is not None:
                            line_segment_colors.InsertNextTuple3(1.0, 1.0, 0.0)
                        else:
                            line_segment_colors.InsertNextTuple3(1.0, 1.0, 1.0)

                    if self._visible_ne and its.pos_ne is not None:
                        nee_point_index = points.InsertNextPoint(its.pos_ne.x, its.pos_ne.y, its.pos_ne.z)
                        line = vtk.vtkLine()
                        line.GetPointIds().SetId(0, point_index)
                        line.GetPointIds().SetId(1, nee_point_index)
                        line_segments.InsertNextCell(line)
                        if its.is_ne_visible:
                            line_segment_colors.InsertNextTuple3(0.0, 0.0, 1.0)
                        else:
                            line_segment_colors.InsertNextTuple3(1.0, 0.0, 0.0)

                last_point_index = point_index
                last_key = key

        self.poly_data.SetPoints(points)
        self.poly_data.SetLines(line_segments)

        cell_data = self.poly_data.GetCellData()
        cell_data.SetAttribute(line_segment_colors, vtk.vtkDataSetAttributes.SCALARS)

        self.mapper.SetScalarModeToUseCellData()
        self.mapper.SetColorModeToDirectScalars()
