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

from core.pyside2_uic import loadUi
from PySide2.QtCore import Slot
from PySide2.QtWidgets import QWidget
from PySide2.QtWidgets import QApplication
import os
import logging
import matplotlib.pyplot as plt

class ViewRenderSceneOptions(QWidget):

    """
        ViewRenderSceneOptions
        Handles the view render scene options view and all user inputs.
        Informs the render interface about view changes
    """

    def __init__(self, parent):
        QWidget.__init__(self, parent=None)
        ui_filepath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ui', 'render_scene_options.ui'))
        loadUi(ui_filepath, self)

        self._controller = None

        # center widget depending on screen size
        desktop_widget = QApplication.desktop()
        screen_rect = desktop_widget.availableGeometry(self)
        self.move(screen_rect.center() - self.rect().center())

        # handle close btn
        self.pbClose.clicked.connect(self.close)

        # globally enables or disables the propagation of received signals from the gui
        # without this, we would have to enable and disable lots of gui signals
        self._propagate_signals = False

        cmaps = plt.colormaps()
        self.cbColormap.addItems(cmaps)

    def set_controller(self, controller):
        self._controller = controller

        # path options
        self.cbActiveNEEs.toggled.connect(self.cb_active_nees_toggled)
        self.cbNEEs.toggled.connect(self.cb_nees_toggled)
        self.dsbActiveLineWidth.valueChanged.connect(self.dsb_active_line_width_changed)
        self.dsbLineWidth.valueChanged.connect(self.dsb_line_width_changed)
        self.sliderActivePathOpacity.valueChanged.connect(self.slider_active_path_opacity_changed)
        self.sliderPathOpacity.valueChanged.connect(self.slider_path_opacity_changed)

        self.pbResetPathOptions.pressed.connect(self.pb_reset_path_options_pressed)

        # scene options
        self.sliderSceneOpacity.valueChanged.connect(self.slider_scene_opacity_changed)
        self.sliderCameraSpeed.valueChanged.connect(self.slider_camera_speed_changed)
        self.cbCameraFocusIntersection.toggled.connect(self.cb_camera_focus_intersection_toggled)

        self.pbResetSceneOptions.pressed.connect(self.pb_reset_scene_options_pressed)

        # 3d data options
        self.cbColormap.currentIndexChanged.connect(self.cb_colormap_index_changed)
        self.leCmapLabel.textChanged.connect(self.le_cmap_label_changed)
        self.dsbCmapMin.valueChanged.connect(self.dsb_cmap_min_changed)
        self.dsbCmapMax.valueChanged.connect(self.dsb_cmap_max_changed)
        self.cbShow3DData.toggled.connect(self.cb_show_3d_data_toggled)
        self.cbShowColorbar.toggled.connect(self.cb_show_colorbar_toggled)

        self.pbReset3DDataOptions.pressed.connect(self.pb_reset_3d_data_options_pressed)

        self._propagate_signals = True


    ## Path options
    @Slot(bool)
    def cb_active_nees_toggled(self, checked : bool):
        if self._propagate_signals:
            self._propagate_signals = False
            self._controller.scene.update_path_options({'show_active_nee': checked})
            self._propagate_signals = True

    @Slot(bool)
    def cb_nees_toggled(self, checked : bool):
        if self._propagate_signals:
            self._propagate_signals = False
            self._controller.scene.update_path_options({'show_all_nee': checked})
            self._propagate_signals = True

    @Slot(float)
    def dsb_active_line_width_changed(self, value : float):
        if self._propagate_signals:
            self._propagate_signals = False
            self._controller.scene.update_path_options({'active_line_width': value})
            self._propagate_signals = True
    
    @Slot(float)
    def dsb_line_width_changed(self, value : float):
        if self._propagate_signals:
            self._propagate_signals = False
            self._controller.scene.update_path_options({'other_line_width': value})
            self._propagate_signals = True
    
    @Slot(int)
    def slider_active_path_opacity_changed(self, value : int):
        if self._propagate_signals:
            value = float(value) / self.sliderActivePathOpacity.maximum()
            self._propagate_signals = False
            self._controller.scene.update_path_options({'active_opacity': value})
            self._propagate_signals = True
    
    @Slot(int)
    def slider_path_opacity_changed(self, value : int):
        if self._propagate_signals:
            value = float(value) / self.sliderPathOpacity.maximum()
            self._propagate_signals = False
            self._controller.scene.update_path_options({'other_opacity': value})
            self._propagate_signals = True

    @Slot()
    def pb_reset_path_options_pressed(self):
        self._controller.scene.reset_path_options()
    
    ## Scene options
    @Slot(int)
    def slider_scene_opacity_changed(self, value : int):
        if self._propagate_signals:
            value = float(value) / self.sliderSceneOpacity.maximum()
            self._propagate_signals = False
            self._controller.scene.update_scene_options({'opacity': value})
            self._propagate_signals = True
    
    @Slot(int)
    def slider_camera_speed_changed(self, value : int):
        if self._propagate_signals:
            value = float(value) / self.sliderCameraSpeed.maximum()
            self._propagate_signals = False
            self._controller.scene.update_scene_options({'camera_speed': value})
            self._propagate_signals = True
    
    @Slot(bool)
    def cb_camera_focus_intersection_toggled(self, checked : bool):
        if self._propagate_signals:
            self._propagate_signals = False
            self._controller.scene.update_scene_options({'focus_intersections': checked})
            self._propagate_signals = True

    @Slot()
    def pb_reset_scene_options_pressed(self):
        self._controller.scene.reset_scene_options()
    
    ## 3D Data options
    @Slot(int)
    def cb_colormap_index_changed(self, value : int):
        if self._propagate_signals:
            self._propagate_signals = False
            self._controller.scene.update_heatmap_options({'cmap': self.cbColormap.currentText()})
            self._propagate_signals = True
    
    @Slot(str)
    def le_cmap_label_changed(self, value : str):
        if self._propagate_signals:
            self._propagate_signals = False
            self._controller.scene.update_heatmap_options({'label': value})
            self._propagate_signals = True

    @Slot(float)
    def dsb_cmap_min_changed(self, value : float):
        if self._propagate_signals:
            self._propagate_signals = False
            self._controller.scene.update_heatmap_options({'min': value})
            self._propagate_signals = True
    
    @Slot(float)
    def dsb_cmap_max_changed(self, value : float):
        if self._propagate_signals:
            self._propagate_signals = False
            self._controller.scene.update_heatmap_options({'max': value})
            self._propagate_signals = True
    
    @Slot(bool)
    def cb_show_3d_data_toggled(self, checked : bool):
        if self._propagate_signals:
            self._propagate_signals = False
            self._controller.scene.update_heatmap_options({'enabled': checked})
            self._propagate_signals = True

    @Slot(bool)
    def cb_show_colorbar_toggled(self, checked : bool):
        if self._propagate_signals:
            self._propagate_signals = False
            self._controller.scene.update_heatmap_options({'colorbar': checked})
            self._propagate_signals = True

    @Slot()
    def pb_reset_3d_data_options_pressed(self):
        self._controller.scene.reset_heatmap_options()
    
    def load_path_options(self, path_options : dict):
        if self._propagate_signals:
            self._propagate_signals = False

            self.cbActiveNEEs.setChecked(path_options.get('show_active_nee', False))
            self.cbNEEs.setChecked(path_options.get('show_all_nee', False))
            self.dsbActiveLineWidth.setValue(path_options.get('active_line_width', 1.0))
            self.dsbLineWidth.setValue(path_options.get('other_line_width', 1.0))
            max = self.sliderActivePathOpacity.maximum()
            self.sliderActivePathOpacity.setValue(int(path_options.get('active_opacity', 1.0)*max))
            max = self.sliderPathOpacity.maximum()
            self.sliderPathOpacity.setValue(int(path_options.get('other_opacity', 0.25)*max))

            self._propagate_signals = True

    def load_scene_options(self, scene_options : dict):
        if self._propagate_signals:
            self._propagate_signals = False

            max = self.sliderSceneOpacity.maximum()
            self.sliderSceneOpacity.setValue(scene_options.get('opacity', 0.25)*max)
            max = self.sliderCameraSpeed.maximum()
            self.sliderCameraSpeed.setValue(scene_options.get('camera_speed', 0.5)*max)
            self.cbCameraFocusIntersection.setChecked(scene_options.get('focus_intersection', True))

            self._propagate_signals = True

    def load_heatmap_options(self, heatmap_options : dict):
        if self._propagate_signals:
            self._propagate_signals = False

            self.cbColormap.setCurrentIndex(self.cbColormap.findText(heatmap_options.get('cmap', 'plasma')))
            self.leCmapLabel.setText(heatmap_options.get('label', 'unknown'))
            self.dsbCmapMin.setValue(heatmap_options.get('min', 0.0))
            self.dsbCmapMax.setValue(heatmap_options.get('max', 1.0))
            self.cbShow3DData.setChecked(heatmap_options.get('enabled', True))
            self.cbShowColorbar.setChecked(heatmap_options.get('colorbar', True))

            self._propagate_signals = True
