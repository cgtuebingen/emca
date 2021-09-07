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


class RubberBandInteractor(vtk.vtkInteractorStyleRubberBandPick):

    """
        RubberBandInteractor
        Allows a rubber band selector by clicking the 'r' key within the 3D renderer scene view.
        The selected vertex and its corresponding path will be automatically be visualized within all other views.
    """

    def __init__(self, parent=None):
        super().__init__()

        self.AddObserver("KeyPressEvent", self.key_press_event)

    def key_press_event(self, obj, event):
        """
        Handles key input for the 3D scene viewer.
        Moves the camera within the scene
        :param obj:
        :param event:
        :return:
        """
        key = self.GetInteractor().GetKeySym()
        camera = self.GetDefaultRenderer().GetActiveCamera()

        if key == 'Up':
            camera.move_forward()
        elif key == 'Left':
            camera.move_left()
        elif key == 'Right':
            camera.move_right()
        elif key == 'Down':
            camera.move_backward()
        elif key == '8':
            camera.move_up()
        elif key == '4':
            camera.pan_left()
        elif key == '6':
            camera.pan_right()
        elif key == '2':
            camera.move_down()

        self.GetDefaultRenderer().ResetCameraClippingRange()
        self.GetInteractor().Render()
