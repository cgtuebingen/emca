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

from renderer.shape import Shape
from model.mesh_data import MeshData
import vtk
import logging
import time

import numpy as np


class Mesh(Shape):

    """
        Mesh
        Represents a Mesh object within the 3D scene as vtkActor
    """

    def __init__(self, mesh_data : MeshData):

        #start = time.time()

        vertices = vtk.vtkPoints()
        vertex_float_array = vtk.vtkFloatArray()
        vertex_float_array.SetArray(mesh_data.vertices, mesh_data.vertex_count*3, True)
        vertex_float_array.SetNumberOfComponents(3)
        vertex_float_array.SetNumberOfTuples(mesh_data.vertex_count)
        vertices.SetData(vertex_float_array)

        triangles = vtk.vtkCellArray()
        triangle_id_array = vtk.vtkIdTypeArray()
        triangle_id_array.SetArray(mesh_data.triangles, mesh_data.triangle_count*4, True)
        triangles.SetCells(mesh_data.triangle_count, triangle_id_array)

        mesh_poly_data = vtk.vtkPolyData()
        mesh_poly_data.SetPoints(vertices)
        mesh_poly_data.SetPolys(triangles)

        self.face_colors = None
        self.max_value = 0.0

        if mesh_data.face_colors is not None:
            interpolate = False # just adds blur - not really helpful

            rgb_colors = mesh_data.face_colors.reshape([mesh_data.triangle_count, 3])
            # assume rgb mode if values differ per channel, otherwise choose scalar mdoe
            #TODO: let the server decide
            rgb_mode = not(np.allclose(rgb_colors[:,0], rgb_colors[:,1]) and np.allclose(rgb_colors[:,1], rgb_colors[:,2]))

            if rgb_mode: # color mode
                #even though this is 2.4, this corresponds to a gamma value of 2.2
                invSRGBGamma = 1.0/2.4
                srgb_face_colors = np.where(mesh_data.face_colors > 0.0031308, (1.055 * np.power(mesh_data.face_colors, invSRGBGamma) - 0.055), mesh_data.face_colors * 12.92)
                #clamp to 1.0 when using colors directly - otherwise wrong colors are displayed
                self.face_colors = np.minimum(srgb_face_colors, 1.0, dtype=np.float32)
            else:
                self.face_colors = mesh_data.face_colors
                self.max_value = np.nanquantile(self.face_colors, 0.95, interpolation='lower')

            face_color_float_array = vtk.vtkFloatArray()
            face_color_float_array.SetArray(self.face_colors, mesh_data.triangle_count*3, True)
            face_color_float_array.SetNumberOfComponents(3)
            face_color_float_array.SetNumberOfTuples(mesh_data.triangle_count)

            cell_data = mesh_poly_data.GetCellData()
            cell_data.SetAttribute(face_color_float_array, vtk.vtkDataSetAttributes.SCALARS)

            if interpolate:
                # interpolate data by converting to vertex colors
                cell_to_point = vtk.vtkCellDataToPointData()
                cell_to_point.SetInputData(mesh_poly_data)
                cell_to_point.Update()
                mesh_poly_data.ShallowCopy(cell_to_point.GetPolyDataOutput())

        super().__init__(mesh_poly_data, mesh_data.diffuse_color, mesh_data.specular_color)

        if mesh_data.face_colors is not None:
            if interpolate: # vertex colors
                self.mapper.SetScalarModeToUsePointData()
            else: # face colors
                self.mapper.SetScalarModeToUseCellData()

            if rgb_mode:
                # pass through rgb color values
                self.mapper.SetColorModeToDirectScalars()
            else:
                # apply colormap
                self.mapper.SetColorModeToMapScalars()
            
            # disable specular color if there are face colors
            self.GetProperty().SetSpecular(0)

        #logging.info('processed mesh containing {} vertices and {} triangles in: {:.3}s'
        #             .format(mesh.vertex_count, mesh.triangle_count, time.time() - start))
