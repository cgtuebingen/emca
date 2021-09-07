

# EMCA - Server Library

<a name="about"></a>

## About
EMCA comes with a server and client part. All files within this folder represents the server part which must be connected to the specific render system. The server files are compiled as shared library which can be then easily included into your project.

## Table of contents
* [About](#about)
* [Build](#build)
* [License](#license)

<a name="build"></a>

## Build
For compiling the shared library we provide a CMakeLists.txt file.

```
mkdir build
cd build
cmake ..
make -j4
sudo make install
```

Make sure that the path to the emca shared library is defined in **LD_LIBRARY_PATH**.

<a name="license"></a>

## License
The shared library comes with the Apache License 2.0.

(c) Christoph Kreisl



