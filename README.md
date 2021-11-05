# EMCA — Explorer of Monte Carlo based Algorithms

EMCA is a framework for the visualization of Monte Carlo based algorithms.
More precisely, it is designed to visualize and analyze unidirectional path tracing algorithms.
The framework consists of two parts, a server part which serves as an interface to arbitrary rendering systems and a client which takes over the visualization.
The client is written in Python and can be easily extended.

EMCA works on a per-pixel basis which means that instead of pre-computing and saving all the necessary data of the whole rendered image during the render process,
everything is calculated directly at run-time. The data is collected and generated according to the pixel selected by the user.

EMCA was published at [VMV 2021](https://diglib.eg.org/handle/10.2312/vmv20211377). You can cite it as follows:

```
@inproceedings {ruppert2021emca,
  booktitle = {Vision, Modeling, and Visualization},
  editor = {Andres, Bjoern and Campen, Marcel and Sedlmair, Michael},
  title = {{EMCA: Explorer of Monte Carlo based Algorithms}},
  author = {Ruppert, Lukas and Kreisl, Christoph and Blank, Nils and Herholz, Sebastian and Lensch, Hendrik P. A.},
  year = {2021},
  publisher = {The Eurographics Association},
  ISBN = {978-3-03868-161-8},
  DOI = {10.2312/vmv.20211377}
}
```

The primary goal of this framework is to support other developers and especially universities researching on rendering algorithms based on Monte Carlo integration.
Furthermore, it should give the impulse to implement further ideas and improvements to provide an ongoing development of EMCA.

The current version of EMCA was mainly developed on Ubuntu 20.04, but should work on all recent Linux systems (and potentially other systems as well).


## Table of contents
* [EMCA Client](#emca_client)
  * [Overview](#overview)
  * [Features](#features)
  * [Demo Video](#demo_video)
* [Server Interface](#server_interface)
  * [Compile Server Library](#server_library)
  * [Server Setup Mitsuba](#server_setup_mitsuba)
 * [Development History](#history)
 * [License](#license)

<a name="emca_client"></a>

## EMCA Client
EMCA is based on **Python 3.7**.
To install and load all necessary dependencies, use the requirements.txt file.

```
pip3 install -r requirements.txt
```

The Python package of OpenEXR requires that the OpenEXR development libraries are already installed on the system.
If an error pops up, install the required libraries via your system's package manager. E.g.,

```
sudo apt-get install libopenexr-dev
```

The same applies to the vtk version 9.x package.
In case it can't be installed via `pip`, download the latest wheel file for your Python version from https://vtk.org/download/ or try your system's package manager.

For an overview of EMCA and its capabilities, have a look at the paper.

![View One](https://github.com/ckreisl/emca/blob/readme/images/emca_render_sample_view.png)

<a name="overview"></a>

### Overview
EMCA's main GUI is separated into the two halves:
On the left, you can look at the rendered image, a reference image, the difference between the two and the 3D scene.
You can inspect the paths involved in computing a pixel's value by selecting it in the 2D image.

On the right, you can then see plots displaying the invididual paths:
Either the contribution of the paths in RGB, the luminance, the path depth
or a detailed tree-view of all properties of each path and intersection.

Selecting a path or intersection will focus the camera in the 3D scene on the selected intersection points.

After clicking in the 3D scene or a plot, you can toggle rectangular selection with the `R` key.
Clicking and dragging will then allow you to select pahts or intersections in the 3D scene and the plots.
In the plots, you can use `Shift` to select additional paths without deselecting the previously selected paths.

In the path data tree-view, you can select multiple paths with `Ctrl` and click on *Inspect* to show only the selected paths.

A better overview of the data per intersection within a path can be seen in the *Intersection Data* window, that you can open with the button on the bottom left.
Again, you can select intersection points in the plots to quickly find the intersection in the 3D scene or in the path data view.

<a name="features"></a>

### Features

#### High Variance Sample Detector
In Monte Carlo integration, paths should be sampled proportional to their unknown eventual contribution. To reduce the variance in the rendered image, importance sampling schemes such as the throughput-oriented BSDF-sampling are applied. However, low-probability paths encountering strong emitters will result in extreme contribution estimates manifesting in firefly artifacts. Investigating these paths provides crucial insights into remaining sources of high variance that developers of efficient path tracers aim to eliminate. Clamping and denoising can be used to remove remaining fireflies. However, such methods are unsatisfactory as they require an additional post-processing step and bias the outcome.

Often, only a single path out of hundreds of paths is responsible for producing a firefly. To ease the debugging of fireflies, a firefly detector is provided which automatically selects paths with extreme contributions upon pixel selection. Paths whose contribution differs from the mean by more than two times the standard deviation are classified as outliers. As a more sophisticated approach, we also provide a second outlier detector based on the Generalized ESD for Outliers by Rosner which is more robust.

#### Filter
The ability to filter data by specific criteria offers more flexibility regarding the analysis of traced paths and their collected path data.
Therefore, we provide a filter algorithm which allows for applying multiple filters with various filter criteria based on the path data. Users can apply one or more filter constraints which are applied in combination.

### Plugins
New path tracing approaches might make use of arbitrary auxiliary data such as spherical radiance caches which might be too complex
to be suitably displayed in the existing 2D and 3D intersection data plots or the textual render data view.
To address the individual needs of novel path tracing algorithms,
a simple plugin interface allows for the construction of additional views with access to all the available path and intersection data for the current pixel.
Following the brushing and linking concept, the tool will be notified of the currently selected path and intersection such that it can update its contents accordingly.
Should the data collected during path tracing not suffice to satisfy the custom tool's needs,
a matching custom server module can be created from which the custom tool can easily request arbitrary additional data at any moment.

#### Spherical View Plugin (Custom Plugin - Mitsuba)
The spherical view tool is an example of a custom tool requiring more data than initially collected during path tracing. It displays the incident radiance from all directions at the active intersection position.
Computing an estimate of the incident radiance can take a considerable amount of time, depending on the selected resolution, sample count and the used integrator.
Therefore, it does not make sense to precompute it during the path tracing step. Instead, the incident radiance is requested and rendered on-the-fly as each intersection is selected while the tool is active.

#### How-To: Add a new Plugin
All individually created plugins should be placed within the **Plugins** folder. To load your plugin add it in the `__init__.py` file as shown below:

```
from plugins.plugin_intersection_data.plugin_intersection_data_plots import IntersectionData
from plugins.plugin_spherical_view.plugin_spherical_view import SphericalView

# In order to initialize your plugin, import your plugin here and add it to __all__ list.

__all__ = [
    'IntersectionData',
    'SphericalView',
]
```

Afterwards, EMCA will automatically load and initialize your plugin. A button with the name of your plugin will become visible in the bottom of the EMCA main view.

New Plugins must inherit from the `Plugin` base class. For code examples check the already implemented plugins within the 'Plugins' folder.


<a name="demo_video"></a>
### Video Demo (old version)
[Click Me - Vimeo](https://vimeo.com/397632936)


<a name="server_interface"></a>

## Server Interface
During the development of EMCA, [Mitsuba](https://github.com/mitsuba-renderer/mitsuba) was used as the rendering framework.
A generic server interface for arbitrary rendering frameworks can be found in the `server` folder.
It can be built into a shared library which then only requires a small custom wrapper to interface with the specific rendering framework.
An example implementation for Mitsuba can be found here: [Mitsuba-EMCA](https://github.com/cgtuebingen/mitsuba-emca).

<a name="server_library"></a>

### Compiling the Server Library
Within the `server` folder we provide a CMake file for compiling the server library.

```
mkdir build
cd build
cmake ..
make -j4
sudo make install
```

<a name="server_setup_mitsuba"></a>

### Starting the EMCA Server Utility for Mitsuba
If you never worked with Mitsuba before please download and read the [documentation](https://www.mitsuba-renderer.org/releases/current/documentation.pdf) first.
The following steps assume that [Mitsuba-EMCA](https://github.com/cgtuebingen/mitsuba-emca) is already setup.

Depending on where you installed the EMCA server library, you may need to adjust the build configuration in *build/config-linux-gcc.py*.

```
EMCAINCLUDE   = ['/usr/local/include/emca']
EMCALIBDIR    = ['/usr/local/lib']
EMCALIB       = ['emca']
```

To use EMCA, you need to adjust the path integrator that is used in your `scene.xml` to supply the visualization data.
As an example, you can use the `pathemca` integrator, which is a copy of the default `path` integrator with added instrumentation.

Set the `LD_LIBRARY_PATH` environment variable by running `source setpath.sh` in the Mitsuba folder.

Start the EMCA server with the following command: `dist/mtsutil emca <path_to_scene.xml>`

We're currently working on a official version for the [Nori](https://github.com/wjakob/nori/) rendering framework. Others may follow.
Feel free to open an issue to request adaptation of your favorite rendering framework.
Or, even better, write your own EMCA interface and we will happily link to your implementation.

### EMCA DataApi
The required data for visualization primarily includes the path's vertices from its origin at the camera until its last intersection, which might be the scene's bounding sphere in case the path terminates in an environment map.
This data is collected using the `setPathOrigin`, `setIntersectionPos` and `setIntersectionPosEnvmap` functions.
To keep track of the current path and intersection, each gets assigned an unique identifier where each path is identified by its per-pixel sample count and each intersection is identified by its depth within the path.
These indices are set using the `setPathIndex` and `setDepthIndex` functions.
To allow for the selection of paths by their incident radiance estimate, the `setFinalEstimate` function can be used to set the necessary data for the sample contribution view.
Similarly, intermediate estimates can be added with `setIntersectionEstimate`.
Additionally, arbitrary data can be added to annotate each path and intersection using the `addPathData` and `addIntersectionData` functions.

If you want to use your own DataApi with your own functions and types you can check the `DataApiMitsuba` class in `include/libcore/dataapimitsuba.h` in [Mitsuba-EMCA](https://github.com/cgtuebingen/mitsuba-emca) as an example.

<a name="history"></a>
## Development History
This framework was initially developed by Christoph Kreisl as Master thesis 03/2019 at the University of Tübingen (Germany).
Special thanks goes to Prof. Hendrik Lensch, Sebastian Herholz (supervisor), Tobias Rittig and Lukas Ruppert who made this work possible.

In 2021, the work was extended by Lukas Ruppert, especially for the display of three-dimensional data (on mesh surfaces).
An initial prototype for collecting 3D data was developed in 2020 by Nils Blank as his Bachelor's Thesis at University of Tübingen.
For VMV 2021, the collection of three-dimensional data has been re-implemented from scratch
and allows the collection of not only scalar heat maps, but fully RGB-colored data on the entire 3D scene geometry.
Also, many small detail improvements have been made such as the display of path contribution estimates in the path data view.

<a name="license"></a>
## License
The software comes with the MIT license a LICENSE file can be found within the code and every source file.
Be aware of 3rd party software:

* PySide2 (LGPL)
* vtk (BSD3)
* matplotlib (BSD)
* numpy (BSD)
* scipy (BSD)
* OpenEXR (BSD)
* Pillow (HPND)
* Imath (MIT)

(c) Christoph Kreisl, Lukas Ruppert
