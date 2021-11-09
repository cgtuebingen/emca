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

#ifndef INCLUDE_EMCA_EMCASERVER_H_
#define INCLUDE_EMCA_EMCASERVER_H_

#include <memory>

#include "platform.h"
#include "stream.h"
#include "renderinterface.h"
#include "dataapi.h"
#include "plugin.h"
#include "stream.h"

#include <memory>

EMCA_NAMESPACE_BEGIN

class EMCAServer {
public:
    EMCAServer(RenderInterface* renderer, DataApi* dataApi);
    ~EMCAServer() { stop(); }

    /// runs the main TCP server that communicates with the client.
    /// does not return until the server is shut down.
    void run(uint16_t port=50013);

    /// disconnect the current client
    void disconnect();
    /// stop the TCP server
    void stop();

private:
    // implementation of the binary protocol between server and client
    // changes made here require similar changes on the client side
    // these functions call into the renderer where necessary to provide the requested data
    void respondSupportedPlugins();
    void respondRenderInfo();
    void respondRenderImage();
    void respondCameraData();
    void respondSceneData();
    void respondRenderPixel();
    bool respondPluginRequest(short id);

    RenderInterface* m_renderer {nullptr};
    DataApi* m_dataApi {nullptr};

    typedef int socket_t;

    class SocketStream final : public Stream {
    public:
        SocketStream(socket_t client_socket) : m_clientSocket(client_socket) {}

    private:
        void write(const void *ptr, size_t size);
        void read(void *ptr, size_t size);

        socket_t m_clientSocket; // not owned - will not be closed on destruction
    };

    socket_t m_clientSocket {-1};
    socket_t m_serverSocket {-1};
    std::unique_ptr<SocketStream> m_stream;

    std::vector<Mesh> m_mesh_data;
};

EMCA_NAMESPACE_END

#endif /* INCLUDE_EMCA_EMCASERVER_H_ */
