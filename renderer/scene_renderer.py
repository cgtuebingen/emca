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

import typing
from model.render_data import RenderData
from renderer.path import Path
from typing import Union
from renderer.camera import Camera
from renderer.renderer import Renderer
from renderer.mesh import Mesh
from renderer.sphere import Sphere
from core.messages import ShapeType
from model.mesh_data import MeshData, SphereData
import numpy as np
import threading
import logging

import matplotlib.pyplot as plt
import vtk


class SceneRenderer(object):

    def __init__(self):
        self._controller = None

        self._camera = Camera()
        self._meshes = []
        self._paths = {}
        self._active_path_index = None

        self._renderer = Renderer()
        self._renderer.set_rubber_band_callback(self.rubber_band_selection)

        # Introduced to prevent multiple update calls while loading scene objects
        # Updating view is expensive
        self._widget_update_timer_running = False
        self._widget_update_timer = threading.Timer(0.1, self.widget_update_from_timer)

        self._path_options = {}
        self._scene_options = {}
        self._heatmap_options = {'label': 'unknown'}

        # global lookup table for coloring data
        self._lut = vtk.vtkLookupTable()

        self._colorbar = vtk.vtkScalarBarActor()
        self._colorbar.SetOrientationToHorizontal()
        self._colorbar.SetPosition(0.3, 0.01) # distance from bottom left
        self._colorbar.SetPosition2(0.7, 0.11) # width and height
        self._colorbar.SetTextPositionToPrecedeScalarBar()
        self._colorbar.SetLookupTable(self._lut)

    def set_controller(self, controller):
        self._controller = controller

        self.reset_path_options()
        self.reset_scene_options()
        self.reset_heatmap_options()

    def reset_path_options(self):
        self.path_options = {
            'show_active_nee': False,
            'show_all_nee': False,
            'active_line_width': 1.0,
            'other_line_width': 1.0,
            'active_opacity': 1.0,
            'other_opacity': 0.25
        }
    def reset_scene_options(self):
        opacity = 0.25
        for mesh in self._meshes:
            if mesh.face_colors is not None:
                opacity = 1.0
                break

        self.scene_options = {
            'opacity': opacity,
            'camera_speed': 0.5,
            'focus_intersections': True
        }
    def reset_heatmap_options(self):
        max_value = 0.0
        has_face_colors = False
        if len(self._meshes) > 0:
            max_value = np.ceil(np.max([mesh.max_value for mesh in self._meshes]))
            has_face_colors = np.any([mesh.face_colors is not None for mesh in self._meshes])

        self.heatmap_options = {
            'cmap': 'plasma',
            'min': 0.0,
            'max': max_value,
            'enabled': has_face_colors,
            'colorbar': has_face_colors
        }
    
    @property
    def path_options(self) -> typing.Dict[str, typing.Any]:
        return self._path_options
    
    @path_options.setter
    def path_options(self, options : typing.Dict[str, typing.Any]):
        updated = dict(self._path_options, **options)
        if updated != self._path_options:
            self._path_options = dict(self._path_options, **options)
            self.update_path_display()
            if self._controller is not None:
                self._controller.scene.update_path_options(updated)

    @property
    def scene_options(self) -> typing.Dict[str, typing.Any]:
        return self._scene_options

    @scene_options.setter
    def scene_options(self, options : typing.Dict[str, typing.Any]):
        updated = dict(self._scene_options, **options)
        if updated != self._scene_options:
            self._scene_options = updated
            self.update_scene_display()
            if self._controller is not None:
                self._controller.scene.update_scene_options(updated)
    
    @property
    def heatmap_options(self) -> typing.Dict[str, typing.Any]:
        return self._heatmap_options

    @heatmap_options.setter
    def heatmap_options(self, options : typing.Dict[str, typing.Any]):
        updated = dict(self._heatmap_options, **options)
        if updated != self._heatmap_options:
            self._heatmap_options = updated
            self.update_heatmap_display()
            if self._controller is not None:
                self._controller.scene.update_heatmap_options(updated)

    def update_path_display(self):
        for path in self._paths.values():
            if self._active_path_index is None or path.path_idx == self._active_path_index:
                path.opacity = self._path_options.get('active_opacity', 1.0)
                path.line_width = self._path_options.get('active_line_width', 1.0)
                path.show_ne = self._path_options.get('show_all_nee', False) \
                            or self._path_options.get('show_active_nee', False) and self._active_path_index is not None
            else:
                path.opacity = self._path_options.get('other_opacity', 1.0)
                path.line_width = self._path_options.get('other_line_width', 1.0)
                path.show_ne = self._path_options.get('show_all_nee', False)

        self.start_widget_update_timer()

    def update_scene_display(self):
        for mesh in self._meshes:
            mesh.opacity = self._scene_options.get('opacity', 0.25)
        
        self._camera.motion_speed = self._scene_options.get('camera_speed', 0.25)
        self.start_widget_update_timer()

    def update_heatmap_display(self):
        for mesh in self._meshes:
            mesh.mapper.SetScalarVisibility(self._heatmap_options.get('enabled', True))
        
        # fetch colormap from matplotlib and feed it into vtk
        cmap = plt.get_cmap(self._heatmap_options.get('cmap', 'plasma')) # RdBu
        self._cmap_data = np.array(cmap(np.linspace(0.0, 1.0, 256))*255.0, dtype=np.uint8)
        lut_data = vtk.vtkUnsignedCharArray()
        lut_data.SetArray(self._cmap_data, 256*4, True)
        lut_data.SetNumberOfComponents(4)
        lut_data.SetNumberOfTuples(256)
        self._lut.SetTable(lut_data)

        # set value range
        self._lut.SetRange(self._heatmap_options.get('min', 0.0), self._heatmap_options.get('max', 1.0))

        # set colorbar label
        self._colorbar.SetTitle(self._heatmap_options.get('label', 'unknown'))

        if self._heatmap_options.get('colorbar', True):
            self._renderer.AddActor(self._colorbar)
        else:
            self._renderer.RemoveActor(self._colorbar)
        
        self.start_widget_update_timer()

    @property
    def renderer(self) -> Renderer:
        """
        Returns the renderer which renders the scene in a widget
        """
        return self._renderer

    @property
    def paths(self) -> typing.Dict[int, Path]:
        """
        Returns all traced paths within the scene
        """
        return self._paths

    @property
    def active_path_index(self):
        return self._active_path_index

    def rubber_band_selection(self, path_indices, selected_point):
        self._controller.update_path(path_indices, False)

        # when only one path is selected, the intersected 3d point is given as the second parameter
        # we need to figure out which intersection it belongs to
        if selected_point is not None:
            # figure out which intersection contains this point (vtkPoint)
            #logging.info("selected point {}".format(selected_point))
            if self._paths[path_indices[0]].path_data.path_origin is not None \
                and np.allclose(self._paths[path_indices[0]].path_data.path_origin, selected_point):
                self._controller.select_intersection(path_indices[0], 1)
            else:
                for its in self._paths[path_indices[0]].path_data.intersections.values():
                    if its.pos is not None and np.allclose(its.pos, selected_point) \
                    or its.pos_ne is not None and np.allclose(its.pos_ne, selected_point):
                        self._controller.select_intersection(path_indices[0], its.depth_idx)

    def start_widget_update_timer(self):
        if not self._widget_update_timer_running:
            self._widget_update_timer_running = True
            self._widget_update_timer = threading.Timer(0.1, self.widget_update_from_timer)
            self._widget_update_timer.start()

    def widget_update_from_timer(self):
        self._renderer.widget.update()
        self._widget_update_timer_running = False

    def update_path_indices(self, indices):
        for path in self._paths.values():
            path.visible = path.path_idx in indices

        self.start_widget_update_timer()

    def select_path(self, index):
        # select no intersection (deselects previous path's intersection)
        if self._active_path_index is not None:
            self._paths[self._active_path_index].select_intersection(None)

        self._active_path_index = index
        self.update_path_display()

    def select_intersection(self, path_idx, its_idx):
        if self._active_path_index is not None:
            self._paths[self._active_path_index].select_intersection(None)
        
        self._active_path_index = path_idx

        if path_idx is not None:
            path = self._paths[path_idx]
            path.select_intersection(its_idx)

            if self._scene_options.get('focus_intersections', True):
                intersection = path.path_data.intersections[its_idx]

                if intersection is not None and intersection.pos is not None:
                    self._camera.set_focal_point(intersection.pos)
        self.start_widget_update_timer()

    def load_camera(self, camera_data):
        self._camera.load_settings(camera_data)
        self._renderer.SetActiveCamera(self._camera)
        self.start_widget_update_timer()

    def load_mesh(self, mesh_data : Union[MeshData, SphereData, None]):
        if mesh_data.shape_type is ShapeType.TriangleMesh:
            mesh = Mesh(mesh_data)
        elif mesh_data.shape_type is ShapeType.SphereMesh:
            #TODO: do we really need these? - they are represented as meshes in the 3D scene...
            mesh = Sphere(mesh_data.center, mesh_data.radius)
            #mesh.color = mesh_data.diffuse_color
            mesh.color_diffuse = mesh_data.diffuse_color
            # mesh.color_specular = mesh_data.specular_color

        #if mesh.face_colors is not None:
        #    self.scene_options = {'opacity' : 1.0}

        mesh.opacity = self._scene_options.get('opacity', 0.25)

        mesh.mapper.SetScalarVisibility(self._heatmap_options.get('enabled', False))
        mesh.mapper.SetLookupTable(self._lut)
        mesh.mapper.UseLookupTableScalarRangeOn()

        self._meshes.append(mesh)
        self._renderer.AddActor(mesh)

        # start a timer to update in a while - do not update for each mesh
        self.start_widget_update_timer()

    def process_scene_info(self, scene_info : typing.Dict[str, typing.Any]):
        if scene_info is None:
            max_value = 0.0
            if len(self._meshes) > 0:
                max_value = np.ceil(np.max([mesh.max_value for mesh in self._meshes]))
            self.heatmap_options = {'max' : max_value}
            return

        self.clear_scene_objects()
        if scene_info['has_heatmap']:
            self.scene_options = {'opacity' : 1.0}
            self.heatmap_options = {
                'cmap': scene_info['colormap'],
                'enabled': True,
                'colorbar': scene_info['show_colorbar'],
                'label': scene_info['colorbar_label']
            }

    def load_traced_paths(self, render_data : RenderData):
        self.clear_traced_paths()
        #start = time.time()
        for key, path_data in render_data.dict_paths.items():
            path = Path(key, path_data)
            self._paths[key] = path
            self._renderer.AddActor(path)
        
        #logging.info("creating traced paths runtime: {}s".format(time.time() - start))
        self.update_path_display()

    def clear_scene_objects(self):
        for mesh in self._meshes:
            self._renderer.RemoveActor(mesh)
        self._meshes.clear()
        self.start_widget_update_timer()

    def clear_traced_paths(self):
        for path in self._paths.values():
            self._renderer.RemoveActor(path)
        self._paths.clear()
        self.start_widget_update_timer()

    def reset_camera_position(self):
        self._camera.reset()
        self.start_widget_update_timer()

    def prepare_new_data(self):
        self.clear_traced_paths()
