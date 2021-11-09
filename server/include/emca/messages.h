/*
    EMCA - Explorer of Monte Carlo based Alorithms (Shared Server Library)
    comes with an Apache License 2.0
    (c) Christoph Kreisl 2020
    (c) Lukas Ruppert 2021

    Licensed to the Apache Software Foundation (ASF) under one
    or more contributor license agreements.  See the NOTICE file
    distributed with this work for additional information
    regarding copyright ownership.  The ASF licenses this file
    to you under the Apache License, Version 2.0 (the
    "License"); you may not use this file except in compliance
    with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing,
    software distributed under the License is distributed on an
    "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
    KIND, either express or implied.  See the License for the
    specific language governing permissions and limitations
    under the License.
*/

#ifndef INCLUDE_EMCA_MESSAGES_H_
#define INCLUDE_EMCA_MESSAGES_H_

#include "platform.h"

EMCA_NAMESPACE_BEGIN

// message identifiers for the TCP protocol
enum Message {
    // connection management (0x000x)
    EMCA_HELLO                 = 0x0001,
    EMCA_SUPPORTED_PLUGINS     = 0x0002,
    EMCA_DISCONNECT            = 0x000E,
    EMCA_QUIT                  = 0x000F,

    // requests from the client (0x001x)
    EMCA_REQUEST_RENDER_INFO   = 0x0011,
    EMCA_REQUEST_RENDER_IMAGE  = 0x0012,
    EMCA_REQUEST_RENDER_PIXEL  = 0x0013,
    EMCA_REQUEST_CAMERA        = 0x0014,
    EMCA_REQUEST_SCENE         = 0x0015,

    // responses to the client (0x002x)
    EMCA_RESPONSE_RENDER_INFO  = 0x0021,
    EMCA_RESPONSE_RENDER_IMAGE = 0x0022,
    EMCA_RESPONSE_RENDER_PIXEL = 0x0023,
    EMCA_RESPONSE_CAMERA       = 0x0024,
    EMCA_RESPONSE_SCENE        = 0x0025,
};

// shape types that can be transferred to the client
enum ShapeType
{
    TriangleMesh             = 0,
    SphereMesh               = 1
};

EMCA_NAMESPACE_END

#endif /* INCLUDE_EMCA_MESSAGES_H_ */
