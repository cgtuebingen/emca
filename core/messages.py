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

from enum import Enum

class StateMsg(Enum):
    DISCONNECT          = 0
    CONNECT             = 1
    SERVER_ERROR        = 2
    DATA_IMAGE          = 3
    DATA_PIXEL          = 4
    DATA_CAMERA         = 5
    DATA_SCENE_INFO     = 6
    DATA_MESH           = 7
    DATA_INFO           = 8
    DATA_NOT_VALID      = 9
    DATA_3D_PATHS       = 10
    DATA_DETECTOR       = 11
    UPDATE_PLUGIN       = 12
    SUPPORTED_PLUGINS   = 13
    QUIT                = 14


class ServerMsg(Enum):
    # connection management (0x000x)
    EMCA_HELLO                 = 0x0001
    EMCA_SUPPORTED_PLUGINS     = 0x0002
    EMCA_DISCONNECT            = 0x000E
    EMCA_QUIT                  = 0x000F

    # requests from the client (0x001x)
    EMCA_REQUEST_RENDER_INFO   = 0x0011
    EMCA_REQUEST_RENDER_IMAGE  = 0x0012
    EMCA_REQUEST_RENDER_PIXEL  = 0x0013
    EMCA_REQUEST_CAMERA        = 0x0014
    EMCA_REQUEST_SCENE         = 0x0015

    # responses to the client (0x002x)
    EMCA_RESPONSE_RENDER_INFO  = 0x0021
    EMCA_RESPONSE_RENDER_IMAGE = 0x0022
    EMCA_RESPONSE_RENDER_PIXEL = 0x0023
    EMCA_RESPONSE_CAMERA       = 0x0024
    EMCA_RESPONSE_SCENE        = 0x0025

    @staticmethod
    def get_server_msg(flag):
        return {
            # connection management (0x000x)
            0x0001: ServerMsg.EMCA_HELLO,
            0x0002: ServerMsg.EMCA_SUPPORTED_PLUGINS,
            0x000E: ServerMsg.EMCA_DISCONNECT,
            0x000F: ServerMsg.EMCA_QUIT,

            # requests from the client (0x001x)
            0x0011: ServerMsg.EMCA_REQUEST_RENDER_INFO,
            0x0012: ServerMsg.EMCA_REQUEST_RENDER_IMAGE,
            0x0013: ServerMsg.EMCA_REQUEST_RENDER_PIXEL,
            0x0014: ServerMsg.EMCA_REQUEST_CAMERA,
            0x0015: ServerMsg.EMCA_REQUEST_SCENE,

            # responses to the client (0x002x)
            0x0021: ServerMsg.EMCA_RESPONSE_RENDER_INFO,
            0x0022: ServerMsg.EMCA_RESPONSE_RENDER_IMAGE,
            0x0023: ServerMsg.EMCA_RESPONSE_RENDER_PIXEL,
            0x0024: ServerMsg.EMCA_RESPONSE_CAMERA,
            0x0025: ServerMsg.EMCA_RESPONSE_SCENE
        }.get(flag, None)


class ShapeType(Enum):
    TriangleMesh    = 0
    SphereMesh      = 1
