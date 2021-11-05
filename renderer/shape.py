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

from core.color import Color4f

import numpy as np
import vtk

class Shape(vtk.vtkActor):

    def __init__(self,
                 mesh_poly_data : vtk.vtkPolyData,
                 color_diffuse : Color4f = Color4f(1, 1, 1),
                 color_specular : Color4f = Color4f(0, 0, 0)):
        super().__init__()

        self._mapper = vtk.vtkPolyDataMapper()
        # use setter function - this sets the mapper inputs
        self.poly_data = mesh_poly_data
        self.SetMapper(self._mapper)

        # set default lighting options
        self.GetProperty().SetLighting(True)
        self.GetProperty().LightingOn()
        self.GetProperty().SetShading(True)
        self.GetProperty().ShadingOn()
        self.GetProperty().SetDiffuseColor(color_diffuse[0:3])
        self.GetProperty().SetDiffuse(1)
        if not np.allclose(color_specular, Color4f(0,0,0)):
            self.GetProperty().SetSpecularColor(color_specular[0:3])
            self.GetProperty().SetSpecular(np.mean(np.array(color_specular))/np.mean(np.array(color_specular+color_diffuse)))
        self.GetProperty().SetAmbient(0)

    @property
    def poly_data(self) -> vtk.vtkPolyData:
        return self._poly_data

    @poly_data.setter
    def poly_data(self, poly_data : vtk.vtkPolyData):
        self._poly_data = poly_data

        if isinstance(self._poly_data, vtk.vtkAlgorithmOutput):
            self._mapper.SetInputConnection(self._poly_data)
        else:
            self._mapper.SetInputData(self._poly_data)

    @property
    def mapper(self) -> vtk.vtkPolyDataMapper:
        return self._mapper

    @property
    def opacity(self) -> float:
        """
        Returns the current opacity of the object
        """
        return self.GetProperty().GetOpacity()

    @opacity.setter
    def opacity(self, value : float):
        """
        Sets the opacity of the object
        """
        self.GetProperty().SetOpacity(value)

    @property
    def color(self) -> Color4f:
        """
        Returns the actual color of the object
        :return: list
        """
        return Color4f(self.GetProperty().GetColor())

    @color.setter
    def color(self, color : Color4f):
        """
        Sets the current color of the object
        """
        self.GetProperty().SetColor(color)

    @property
    def color_diffuse(self) -> Color4f:
        """
        Returns the current diffuse color of the object
        """
        return Color4f(self.GetProperty().GetDiffuseColor())

    @color_diffuse.setter
    def color_diffuse(self, color_diffuse : Color4f):
        """
        Sets the diffuse color of the object
        """
        self.GetProperty().SetDiffuseColor(color_diffuse)

    @property
    def color_specular(self) -> Color4f:
        """
        Return the current specular color of the object
        """
        return Color4f(self.GetProperty().GetSpecularColor())

    @color_specular.setter
    def color_specular(self, color_specular : Color4f):
        """
        Sets the specular color of the object
        """
        self.GetProperty.SetSpecularColor(color_specular)
