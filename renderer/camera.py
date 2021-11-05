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

import vtk
import logging
from core.point import Point3f
from core.vector import Vec3f

from model.camera_data import CameraData


class Camera(vtk.vtkCamera):

    """
        Camera
        Represents a modified vtkCamera class for the 3D viewer
    """

    def __init__(self):
        super().__init__()
        self._motion_speed = 0.1 # always between 0 and 1
        self._scene_size   = 1.0 # estimate of scene size based on near and far clip

        self._camera_data = None

    def load_settings(self, camera_data : CameraData):
        # save parameters for camera reset
        self._camera_data = camera_data
        self._scene_size = (self._camera_data.far_clip-self._camera_data.near_clip)*0.05;

        self.reset()

    def reset(self):
        """
        Resets the camera to its default position
        :return:
        """
        if self._camera_data is not None:
            self.SetViewAngle(self._camera_data.fov)
            # clipping range will be overwritten later to improve z-Buffering
            self.SetClippingRange(self._camera_data.near_clip, self._camera_data.far_clip)
            self.SetViewUp(self._camera_data.up[0:3])
            self.SetPosition(self._camera_data.position[0:3])
            self.SetFocalPoint(self._camera_data.position+self._camera_data.direction*(self._camera_data.near_clip+self._scene_size))
        else:
            raise Exception("Camera data not set!")

    @property
    def motion_speed(self) -> float:
        """
        Returns the camera motion speed
        """
        return self._motion_speed

    @motion_speed.setter
    def motion_speed(self, speed : float):
        """
        Setter function, sets the camera motion speed
        """
        self._motion_speed = speed

    def set_focal_point(self, focal_p : Point3f):
        """
        Sets the focal point of the camera
        """
        self.SetFocalPoint(focal_p[0], focal_p[1], focal_p[2])

    def reset_motion_speed(self):
        """
        Resets the camera motion speed to 0.5
        """
        self._motion_speed = 0.5

    def pan_left(self):
        """
        Pan camera to the left
        """
        self.Yaw(self._motion_speed)

    def pan_right(self):
        """
        Pan camera to the right
        """
        self.Yaw(-self._motion_speed)

    def move_up(self):
        """
        Move camera up
        """
        self._motion_along_vector(self.GetViewUp(), -self._scene_size*self._motion_speed)

    def move_down(self):
        """
        Move camera down
        """
        self._motion_along_vector(self.GetViewUp(), self._scene_size*self._motion_speed)

    def move_right(self):
        """
        Move camera right
        """
        self._motion_along_vector(self._get_rl_vector(), -self._scene_size*self._motion_speed)

    def move_left(self):
        """
        Move camera left
        """
        self._motion_along_vector(self._get_rl_vector(), self._scene_size*self._motion_speed)

    def move_forward(self):
        """
        Move camera forward
        """
        self._motion_along_vector(self.GetDirectionOfProjection(), -self._scene_size*self._motion_speed)

    def move_backward(self):
        """
        Move camera backward
        """
        self._motion_along_vector(self.GetDirectionOfProjection(), self._scene_size*self._motion_speed)

    def _get_rl_vector(self):
        """
        Returns the right-left vector of the camera
        """
        vtm = self.GetViewTransformMatrix()
        x = vtm.GetElement(0, 0)
        y = vtm.GetElement(0, 1)
        z = vtm.GetElement(0, 2)
        return [x, y, z]

    def _motion_along_vector(self, vec : Vec3f, speed : float):
        """
        Applies a motion along a vector with given speed
        :param vec:
        :param speed:
        :return:
        """
        old_pos = self.GetPosition()
        focal_point = self.GetFocalPoint()
        self.SetPosition(
            old_pos[0] - speed * vec[0],
            old_pos[1] - speed * vec[1],
            old_pos[2] - speed * vec[2])
        self.SetFocalPoint(
            focal_point[0] - speed * vec[0],
            focal_point[1] - speed * vec[1],
            focal_point[2] - speed * vec[2])
