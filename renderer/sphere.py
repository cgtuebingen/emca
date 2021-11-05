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
import vtk
import logging


class Sphere(Shape):

    """
        Sphere
        Represents a vtk Sphere object within the 3D scene
    """

    def __init__(self, center, radius, theta_resolution=20, phi_resolution=20):

        self._center = center
        self._radius = radius

        sphere = vtk.vtkSphereSource()
        # center (x,y,z)
        sphere.SetCenter(list(center))
        sphere.SetRadius(radius)
        sphere.SetThetaResolution(theta_resolution)
        sphere.SetPhiResolution(phi_resolution)

        # get poly data
        mesh_poly_data = sphere.GetOutputPort()

        super().__init__(mesh_poly_data)

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, radius):
        self._radius = radius

    @property
    def center(self):
        return self._center

    @center.setter
    def center(self, center):
        self._center = center

