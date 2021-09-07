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

import vtk
import logging


class Camera(vtk.vtkCamera):

    """
        Camera
        Represents a modified vtkCamera class for the 3D viewer
    """

    def __init__(self):
        super().__init__()
        # boolean to check if camera should always set the viewing direction to selected intersection
        self._auto_clipping = True
        self._motion_speed = 0.1

        self._base_motion_speed = 1.0
        self._origin = None
        self._focal_point = None
        self._focus_dist = None
        self._up = None
        self._near_clip = None
        self._far_clip = None
        self._fov = None

    def load_settings(self, camera_data):
        # save parameters for camera reset
        self._origin = camera_data.origin
        self._base_motion_speed = (camera_data.far_clip-camera_data.near_clip)*0.05;
        self._focal_point = camera_data.origin+camera_data.direction
        self._up = camera_data.up
        self._near_clip = camera_data.near_clip
        self._far_clip = camera_data.far_clip
        self._focus_dist = camera_data.focus_dist
        self._fov = camera_data.fov
        self.reset()

    def reset(self):
        """
        Resets the camera to its default position
        :return:
        """
        if self._origin is not None:
            self.SetPosition(self._origin.x, self._origin.y, self._origin.z)
            self.SetFocalPoint(self._focal_point.x, self._focal_point.y, self._focal_point.z)
            self.SetViewUp(self._up.x, self._up.y, self._up.z)
            self.SetClippingRange(self._near_clip, self._far_clip)
            self.SetDistance(self._base_motion_speed)
            self.SetViewAngle(self._fov)
        else:
            raise Exception("Camera origin not set!")

    @property
    def auto_clipping(self):
        """
        Returns if auto clipping is enabled or disabled
        :return: boolean
        """
        return self._auto_clipping

    @auto_clipping.setter
    def auto_clipping(self, new_value):
        """
        Setter function, sets the auto clipping value
        :param new_value: boolean
        :return:
        """
        self._auto_clipping = new_value

    @property
    def motion_speed(self):
        """
        Returns the camera motion speed
        :return:
        """
        return self._motion_speed

    @motion_speed.setter
    def motion_speed(self, speed):
        """
        Setter function, sets the camera motion speed
        :param speed:
        :return:
        """
        self._motion_speed = speed

    def set_focal_point(self, focal_p):
        """
        Sets the focal point of the camera
        :param focal_p: list[x,y,z]
        :return:
        """
        self.SetFocalPoint(focal_p[0], focal_p[1], focal_p[2])

    def reset_motion_speed(self):
        """
        Resets the camera motion speed to 0.5
        :return:
        """
        self._motion_speed = 0.5

    def pan_left(self):
        """
        Pan camera to the left
        :return:
        """
        self.Yaw(self._base_motion_speed*self._motion_speed)

    def pan_right(self):
        """
        Pan camera to the right
        :return:
        """
        self.Yaw(-self._base_motion_speed*self._motion_speed)

    def move_up(self):
        """
        Move camera up
        :return:
        """
        self._motion_along_vector(self.GetViewUp(), -self._base_motion_speed*self._motion_speed)

    def move_down(self):
        """
        Move camera down
        :return:
        """
        self._motion_along_vector(self.GetViewUp(), self._base_motion_speed*self._motion_speed)

    def move_right(self):
        """
        Move camera right
        :return:
        """
        self._motion_along_vector(self._get_rl_vector(), -self._base_motion_speed*self._motion_speed)

    def move_left(self):
        """
        Move camera left
        :return:
        """
        self._motion_along_vector(self._get_rl_vector(), self._base_motion_speed*self._motion_speed)

    def move_forward(self):
        """
        Move camera forward
        :return:
        """
        self._motion_along_vector(self.GetDirectionOfProjection(), -self._base_motion_speed*self._motion_speed)

    def move_backward(self):
        """
        Move camera backward
        :return:
        """
        self._motion_along_vector(self.GetDirectionOfProjection(), self._base_motion_speed*self._motion_speed)

    def _get_rl_vector(self):
        """
        Returns the right-left vector of the camera
        :return:
        """
        vtm = self.GetViewTransformMatrix()
        x = vtm.GetElement(0, 0)
        y = vtm.GetElement(0, 1)
        z = vtm.GetElement(0, 2)
        return [x, y, z]

    def _motion_along_vector(self, vec, speed):
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
