# EMCA — Explorer of Monte Carlo based Algorithms

## Note - VMV 2021 version - this is just a preview
This work builds on previous work mainly done by Christoph Kreisl.
Most of the text below still describes the old version of the system and is not necessarily consistent with the updated version which has undergone major changes.
Expect further, potentially large, changes to both documentation and the code.
Until further announcement, treat this only as a preview.

Thank you for your interest in EMCA,

Lukas


<a name="about"></a>

## About
EMCA is a framework for the visualization of Monte Carlo based algorithms.
More precisely it is designed to visualize and analyze unidirectional path tracing algorithms.
The framework consists of two parts, a server part which serves as an interface for the respective rendering system and a client which takes over the visualization.
The client is written in Python and can be easily extended.
EMCA works on a per-pixel basis which means that instead of pre-computing and saving all the necessary data of the whole rendered image during the render process,
everything is calculated directly at run-time. The data is collected and generated according to the pixel selected by the user.

This framework was initially developed by Christoph Kreisl as Master thesis 03/2019 at the University of Tübingen (Germany).
Special thanks goes to Prof. Hendrik Lensch, Sebastian Herholz (supervisor), Tobias Rittig and Lukas Ruppert who made this work possible.
* Master-Thesis: https://github.com/ckreisl/emca/blob/readme/images/ckreisl_thesis.pdf

Since the release of this master thesis, some changes have been applied so that it can now be published as a more or less **alpha** version and in a quite stable state.
The primary goal of this framework is to support other developers and especially universities researching on rendering algorithms based on Monte Carlo.
Furthermore, it should give the impulse to implement further ideas and improvements to provide an ongoing development of EMCA.

Currently, this framework only runs on **Linux** systems. The new version was developed on Ubuntu 20.04, but should work on all recent systems.

In 2021, the work was extended, especially for the display of three-dimensional data (on mesh surfaces).
An initial prototype was developed in 2020 by Nils Blank as his Bachelor's Thesis at University of Tübingen.
For VMV 2021, the collection of three-dimensional data has been re-implemented from scratch
and allows the collection of not only scalar heat maps, but fully RGB-colored data on the entire 3D scene geometry.

**The final BibTex entry for the VMV 2021 version follow as soon as it is available, this is just a placeholder:**

```
@inproceedings{ruppert2021emca,
  booktitle = {Vision, Modeling \& Visualization},
  title = {{EMCA: Explorer of Monte Carlo based Algorithms}},
  author = {Ruppert, Lukas and Kreisl, Christoph and Blank, Nils and Herholz, Sebastian and Lensch, Hendrik P.A.},
  year = {2021},
  publisher = {The Eurographics Association}
}
```

## Table of contents
* [About](#about)
* [Server Interface](#server_interface)
  * [Compile Server Library](#server_library)
  * [Server Setup Mitsuba](#server_setup_mitsuba)
* [EMCA Client](#emca_client)
  * [Brushing and Linking](#brushing_linking)
  * [Render View](#render_view)
  * [Sample Contribution View](#sample_view)
  * [3D Scene View](#scene_view)
  * [Render Data View](#data_view)
  * [Custom Plugin Interface](#custom_plugin_interface)
  * [Features](#features)
  * [Socket Package Flow](#socket_package_flow)
  * [Demo Video](#demo_video)
  * [License](#license)

<a name="server_interface"></a>

## Server Interface
During the development of EMCA [mitsuba](https://github.com/mitsuba-renderer/mitsuba) was used as render system.
For this purpose, an interface was implemented to allow data transfer between Mitsuba and the EMCA framework.
You can find the server code in the `server` folder.
For more flexibility the server code is provided as shared library.
This should make it easier to integrate it into other rendering systems.
The necessary Mitsuba modifications which have been applied can be found here:
[Mitsuba-EMCA](https://github.com/cgtuebingen/mitsuba-emca)

In general 'any' render system can be used. For this purpose the EMCA server interface must be adapted to the respective render system.
In addition, the renderer must be modified so that it can render deterministic images.
At the moment there is no **offical** documentation available to adapt the EMCA server interface to other render systems than mitsuba.

<a name="server_library"></a>

### Compile Server Library
Within the `server` folder we provide a CMake file for compiling the server library.

```
mkdir build
cd build
cmake ..
make -j4
sudo make install
```

Make sure that the path to the emca shared library is defined in **LD_LIBRARY_PATH**.

<a name="server_setup_mitsuba"></a>

### Server Setup Mitsuba
If you never worked with [mitsuba](https://github.com/mitsuba-renderer/mitsuba) before please download and read the [documentation](https://www.mitsuba-renderer.org/releases/current/documentation.pdf) first.
With the following steps I assume that the setup of Mitsuba is already done.

1. Clone or pull the changes from the mitsuba emca-lib branch.
2. Add paths to emca libraries in *config.py*.
```
EMCAINCLUDE   = ['/usr/local/include/emca']
EMCALIBDIR    = ['/usr/local/lib']
EMCALIB       = ['emca']
```
3. Compile mitsuba
4. Modify your scene.xml file. Set the integrator type to `pathemca` or your adapted integrator. For further information on how to add data check the `pathemca.cpp` file.
```
<!-- Modified Multiple Importance Sampling Path Tracing Algorithm -->
<integrator type="pathemca"/>
```
5. Start the server with the following command: `mtsutil emca <path_to_scene.xml>`

There are no official examples or adoptions of other rendering frameworks so far, but would certainly be possible.
Feel free to open an issue to request adaptation of your favorite rendering framework.
Or, even better, adapt your renderer and we will link to your implementation.

### Code Modification
The following is based on the modifications made to Mitsuba. The changes which need to be made inside the path tracing code of the rendering algorithm to be able to communicate with the server to provide the necessary data are minimally invasive.
An example for a simple uni-directional path tracer is shown in the `pathemca.cpp` file.

In `utils/emca.cpp` you can explore the interface connection which servers as the server part.

### DataApi
The required data for visualization primarily includes the path's vertices from its origin at the camera until its last intersection, which might be the scene's bounding sphere in case the path terminates in an environment map.
This data is collected using the `setPathOrigin`, `setIntersectionPos` and `setIntersectionPosEnvmap` functions.
To keep track of the current path and intersection, each gets assigned an unique identifier where each path is identified by its per-pixel sample count and each intersection is identified by its depth within the path.
These indices are set using the `setPathIndex` and `setDepthIndex` functions.
To allow for the selection of paths by their incident radiance estimate, the `setFinalEstimate` function can be used to set the necessary data for the sample contribution view.
Similarly, intermediate estimates can be added with `setIntersectionEstimate`.
Additionally, arbitrary data can be added to annotate each path and intersection using potentially fully custom data using the `addPathData` and `addIntersectionData` functions.

If you want to use your own DataApi with your own functions and types you can check the `DataApiMitsuba` class in `include/libcore/dataapimitsuba.h` (from emca-lib branch - mitsuba) as an example.

<a name="emca_client"></a>

## EMCA Client
EMCA is based on **Python 3.7**. To install and load all necessary dependencies use the requirements.txt file.
```
pip3 install -r requirements.txt
```
The Python packages OpenEXR can lead to problems during installation in case the base libraries are not installed (tested on Ubuntu 18.04). If an error pops up install the required libraries via the package manager.

```
sudo apt-get install libopenexr-dev
sudo apt-get install openexr
```

Same applies to the vtk version 9.x package. In case it can't be installed via the pip package manager download the latest wheel file for Python 3.8 from: https://vtk.org/download/ or try your system's package manager.

<a name="brushing_linking"></a>

### Brushing and Linking
The concept of brushing and linking is to connect multiple views within a GUI representing different parts of the same data.
Selecting a path or intersection in any view will automatically select the same path or intersection in all other views including the (custom) tools presented shortly. This approach allows to provide insight into multiple aspects of the data without cluttering a single view with all the available data. Especially the connection to the scene view provides valuable insight into the otherwise difficult to parse intersection points.

![View One](https://github.com/ckreisl/emca/blob/readme/images/emca_render_sample_view.png)

<a name="render_view"></a>

### Render View
Displaying the rendered image, the render view is the starting point of any visualization task.
Here, the user can select individual pixels, e.g. ones containing artifacts such as fireflies or general high-variance regions, to inspect their contributing light transport paths and look for potential errors or sources of high variance.
The image can either be loaded from file, via drag'n drop or be requested from the server to render anew.
On selection of a pixel, the server is queried for the corresponding path data, which can be quickly generated by the rendering system.
Once this data is received, it becomes available for further inspection in the following views.
A history of previously selected pixels allows to quickly switch between several pixels of interest.

<a name="sample_view"></a>

### Sample Contribution View
The sample contribution view provides interactive scatter plots of each path's estimate of incident radiance for the selected pixel per spectrum provided by the renderer.
In the scatter plots, paths can be quickly classified into non-contributing paths, regularly contributing paths and outliers which might have caused a firefly artifact.
Here, one or multiple paths can be selected for inspection.
For efficient selection of a subset of paths, a rectangular selection tool is provided.

* Rectangle selection tool can be (de-)activated by pressing the 'R' key.
* Single paths can be added by holding down the 'Shift' key while selecting elements.

![View Two](https://github.com/ckreisl/emca/blob/readme/images/emca_scene_data_view.png)

<a name="scene_view"></a>

### Scene View
The scene view allows the user to explore the selected traced paths within a semitransparent representation of the scene's geometry.
The camera is initialized to its location in the rendered image and can be moved around freely.
To allow for quick selection of paths, a rectangular selection tool can be used to select individual intersections directly in the scene view.
When selecting path intersections from other views, the camera is automatically moved to the selected intersection.
To additionally highlight the selected intersection, its preceding path segment is highlighted in green while the intersection point is colored in orange.
Regular path segments are shown in white unless they terminate in the environment map in which case they are colored in yellow.
If the rendering algorithm uses next event estimation, shadow rays can be shown in blue for successful connections to the emitter and in red in case the sampled emitter is occluded.

* Rectangle selection tool can be (de-)activated by pressing the 'R' key.

#### Depth-Buffer issues with Intel GPUs
When using the Mesa driver for Intel GPUs, scene contents aren't always ordered properly if scene opacity is at 100%.
AMD and Nvidia GPUs work fine.
This seems to be a known issue when using VTK under Qt5 with PySide2.
We'll fix this as soon as we find a solution.

<a name="data_view"></a>

### Data View
The render data view shows all the collected data for each selected path and its vertices.
Paths and their data are presented in a collapsible tree structure to the user to allow for comprehensible inspection and comparison of various paths and individual vertices.
In combination with the scene view, light transport paths can be quickly analyzed by interactively stepping through the individual intersection points by simply selecting the vertices in the data view.

<a name="custom_plugin_interface"></a>

### Custom Plugin Interface
New path tracing approaches might make use of arbitrary auxiliary data such as spherical radiance caches which might be too complex
to be suitably displayed in the existing 2D and 3D intersection data plots or the textual render data view.
To address the individual needs of novel path tracing algorithms,
a custom tool interface allows for simple construction of additional views with access to all the available path and intersection data for the current pixel.
Following the brushing and linking concept the tool will be notified of the currently selected path and intersection such that it can update its contents accordingly.
Should the data collected during path tracing not suffice to satisfy the custom tool's needs,
a matching custom server module can be created from which the custom tool can easily request arbitrary additional data at any moment.

#### Intersection Data Plots Plugin (Core Plugin)
The intersection data plots provide an aggregated view of all user-supplied data for a single traced path. The view allows for exploring fundamental quantities and their changes during ray traversal like the Russian roulette probability or PDF. Supporting multiple data types with 2D and 3D plots for one or two dimensional data at various path depths as well as spectral plots for radiance data enables visualizing the most commonly gathered data. All plots are automatically created on-the-fly after receiving the render data from the server side.

#### Path Depth Plugin (Core Plugin)
The path depth view allows for analyzing traced paths according to their reached depth. Detecting paths that end too early can be essential in order to determine convergence problems of a rendered image.
Terminating paths based only on their throughput may undersample important contributions of hard to reach light sources.
Therefore, in combination with the per-path estimate view, one can analyze various Russian roulette criteria like ADRR and their relations between path contribution and the reached depth.

#### Spherical View Plugin (Custom Plugin - Mitsuba)
The spherical view tool is an example of a custom tool requiring more data than initially collected during path tracing. It displays the incident radiance from all directions at the active intersection position.
Computing an estimate of the incident radiance can take a considerable amount of time, depending on the selected resolution, sample count and the used integrator. Therefore, it does not make sense to precompute it during the path tracing step. Instead, the incident radiance is requested and rendered on-the-fly as each intersection is selected while the tool is active.

#### How-To: Add a new Plugin
All individually created plugins should be placed within the **Plugins** folder. To load your plugin add it in the `__init__.py` file as shown below:

```
from plugins.plugin_intersection_data.plugin_intersection_data_plots import IntersectionData
from plugins.plugin_path_depth.plugin_path_depth import PathDepth
from plugins.plugin_spherical_view.plugin_spherical_view import SphericalView

# In order to initialize your plugin, import your plugin here and add it to __all__ list.

__all__ = [
    'IntersectionData',
    'PathDepth',
    'SphericalView',
]
```

Afterwards, EMCA will automatically load and initialize your plugin. A button with the name of your plugin will become visible in the bottom of the EMCA main view.

New Plugins must inherit from the `Plugin` base class. For code examples check the already implemented plugins within the 'Plugins' folder.

<a name="features"></a>

### Features

#### High Variance Sample Detector
In Monte Carlo integration, paths should be sampled proportional to their unknown eventual contribution. To reduce the variance in the rendered image, importance sampling schemes such as the throughput-oriented BSDF-sampling are applied. However, low-probability paths encountering strong emitters will result in extreme contribution estimates manifesting in firefly artifacts. Investigating these paths provides crucial insights into remaining sources of high variance that developers of efficient path tracers aim to eliminate. Clamping and denoising can be used to remove remaining fireflies. However, such methods are unsatisfactory as they require an additional post-processing step and bias the outcome.

Often, only a single path out of hundreds of paths is responsible for producing a firefly. To ease the debugging of fireflies, a firefly detector is provided which automatically selects paths with extreme contributions on pixel selection. Paths whose contribution differs from the mean by more than two times the standard deviation are classified as outliers. As a more sophisticated approach, we also provide a second outlier detector based on the Generalized ESD for Outliers by Rosner which is more robust.

#### Filter
The ability to filter data by specific criteria offers more flexibility regarding the analysis of traced paths and their collected path data.
Therefore, we provide a filter algorithm which allows for applying multiple filters with various filter criteria based on the path data. Users can apply one or more filter constraints which are applied in combination.

<a name="socket_package_flow"></a>
### Socket Package Flow Diagram (old version)
<object data="https://github.com/ckreisl/emca/blob/readme/images/emca_tcp_flow.pdf" type="application/pdf" width="700px" height="700px">
    <embed src="https://github.com/ckreisl/emca/blob/readme/images/emca_tcp_flow.pdf">
        <p>This browser does not support PDFs. Please download the PDF to view it: <a href="https://github.com/ckreisl/emca/blob/readme/images/emca_tcp_flow.pdf">Download PDF</a>.</p>
    </embed>
</object>

<a name="demo_video"></a>
### Video Demo (old version)
[Click Me - Vimeo](https://vimeo.com/397632936)

<a name="license"></a>
### License
The software comes with the MIT license a LICENSE file can be found within the code and every source file.
Be aware of 3rd party software:

* PySide2 (LGPL)
* vtk (BSD3)
* matplotlib (BSD)
* numpy (BSD)
* six (MIT)
* scipy (BSD)
* OpenEXR (BSD)
* Pillow (HPND)
* Imath (MIT)

(c) Christoph Kreisl
