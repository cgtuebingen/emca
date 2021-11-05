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

#include "emcaserver.h"
#include "scenedata.h"
#include "messages.h"

#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>

#include <stdexcept>
#include <cerrno>

EMCA_NAMESPACE_BEGIN

EMCAServer::EMCAServer(RenderInterface* renderer, DataApi* dataApi)
    : m_renderer{renderer}, m_dataApi{dataApi} {
    if (!renderer || !dataApi)
        throw std::logic_error("a renderer and a data api instance need to be provided");

    // FIXME: is there a better place to put this? it is a bit hidden here.
    m_mesh_data = m_renderer->getMeshData();
    m_dataApi->heatmap.initialize(m_mesh_data);
}

void EMCAServer::run(uint16_t port) {
    struct sockaddr_in server_addr, client_addr;
    memset(&server_addr, 0, sizeof(server_addr));

    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(port);

    m_serverSocket = socket(AF_INET, SOCK_STREAM, 0);
    if (m_serverSocket < 0)
        throw std::runtime_error("failed to create IP socket");

    const int option = 1;
    if (setsockopt(m_serverSocket, SOL_SOCKET, (SO_REUSEPORT | SO_REUSEADDR), &option, sizeof(option)) < 0) {
        close(m_serverSocket);
        m_serverSocket = -1;
        throw std::runtime_error("failed to set socket options");
    }

    if (bind(m_serverSocket, reinterpret_cast<struct sockaddr*>(&server_addr), sizeof(server_addr)) < 0) {
        close(m_serverSocket);
        m_serverSocket = -1;
        throw std::runtime_error("failed to bind server to port "+std::to_string(port));
    }

    int16_t lastReceivedMsg = Message::EMCA_DISCONNECT;

    while (m_serverSocket >= 0 && lastReceivedMsg == Message::EMCA_DISCONNECT) {
        disconnect();

        if (listen(m_serverSocket, 5) < 0)
            throw std::runtime_error("failed to listen on the socket");

        std::cout << "Server is listening for connections ..." << std::endl;

        try {
            socklen_t len = sizeof(client_addr);
            m_clientSocket = accept(m_serverSocket, reinterpret_cast<struct sockaddr*>(&client_addr), &len);
            if (m_clientSocket < 0)
                throw std::runtime_error("failed to accept client socket");

            m_stream = std::make_unique<SocketStream>(m_clientSocket);
            m_stream->writeShort(Message::EMCA_HELLO);
            lastReceivedMsg = m_stream->readShort();

            if (lastReceivedMsg != Message::EMCA_HELLO)
                throw std::runtime_error("Did not recieve hello message.");

            // send list of plugins
            respondSupportedPlugins();

            std::cout << "Handshake complete! Starting data transfer ..." << std::endl;

            while (m_clientSocket >= 0) {
                // read header of message
                lastReceivedMsg = m_stream->readShort();
                std::cout << "Received header msg = " << lastReceivedMsg << std::endl;

                if (respondPluginRequest(lastReceivedMsg))
                    continue;

                switch(lastReceivedMsg) {
                case Message::EMCA_REQUEST_RENDER_INFO:
                    std::cout << "Respond render info msg" << std::endl;
                    respondRenderInfo();
                    break;
                case Message::EMCA_REQUEST_CAMERA:
                    std::cout << "Respond camera data msg" << std::endl;
                    respondCameraData();
                    break;
                case Message::EMCA_REQUEST_SCENE:
                    std::cout << "Respond scene data msg" << std::endl;
                    respondSceneData();
                    break;
                case Message::EMCA_REQUEST_RENDER_IMAGE:
                    std::cout << "Render image msg" << std::endl;
                    respondRenderImage();
                    break;
                case Message::EMCA_REQUEST_RENDER_PIXEL:
                    std::cout << "Render pixel msg" << std::endl;
                    respondRenderPixel();
                    break;
                case Message::EMCA_DISCONNECT:
                    std::cout << "Disconnect msg" << std::endl;
                    disconnect();
                    break;
                case Message::EMCA_QUIT:
                    std::cout << "Quit message!" << std::endl;
                    stop();
                    break;
                default:
                    std::cout << "Unknown message received!" << std::endl;
                    break;
                }
            }
        } catch (std::exception &e) {
            std::cerr << "caught exception: " << e.what() << std::endl;
            continue;
        } catch (...) {
            std::cerr << "caught unknown exception" << std::endl;
            continue;
        }
    }

    stop();
}

void EMCAServer::disconnect() {
    if (m_clientSocket >= 0) {
        if (m_stream.get())
            m_stream->writeShort(Message::EMCA_DISCONNECT);
        m_stream.reset();
        if (close(m_clientSocket) == 0)
            std::cout << "disconnected." << std::endl;
        else
            std::cout << "disconnect failed: " << errno << std::endl;
    }
    m_clientSocket = -1;
}

void EMCAServer::stop() {
    disconnect();
    if (m_serverSocket >= 0) {
        if (close(m_serverSocket) == 0)
            std::cout << "stopped server." << std::endl;
        else
            std::cout << "stop failed: " << errno << std::endl;
    }
    m_serverSocket = -1;
}

void EMCAServer::respondSupportedPlugins() {
    try
    {
        std::cout << "Inform Client about supported Plugins" << std::endl;
        m_dataApi->plugins.printPlugins();
        std::vector<int16_t> supportedPlugins = m_dataApi->plugins.getPluginIds();
        m_stream->writeShort(Message::EMCA_SUPPORTED_PLUGINS);
        m_stream->writeUInt(static_cast<uint32_t>(supportedPlugins.size()));
        for (short &id : supportedPlugins) {
            m_stream->writeShort(id);
        }
    }
    catch (const std::exception& e)
    {
        std::cerr << e.what() << std::endl;
    }
}

void EMCAServer::respondRenderInfo() {
    try {
        m_stream->writeShort(Message::EMCA_RESPONSE_RENDER_INFO);
        m_stream->writeString(m_renderer->getRendererName());
        m_stream->writeString(m_renderer->getSceneName());
        m_stream->writeUInt(m_renderer->getSampleCount());
    } catch (const std::exception& e) {
        std::cerr << "Render info error: " << e.what() << std::endl;
    }
}

void EMCAServer::respondRenderImage() {
    try {
        const uint32_t sampleCount = m_stream->readUInt();
        m_renderer->setSampleCount(sampleCount);

        // enabling the heatmap is up to the preprocessing step during rendering
        m_renderer->renderImage();
        // finalize heatmap data (if there is any)
        if (m_dataApi->heatmap.isCollecting()) {
            m_dataApi->heatmap.finalize();
        }

        m_stream->writeShort(Message::EMCA_RESPONSE_RENDER_IMAGE);
        //TODO: pass through the rendered exr image if the connection is remote
        m_stream->writeString(m_renderer->getRenderedImagePath());

        // send heatmap data, if there is any
        if (m_dataApi->heatmap.hasData())
            respondSceneData();
    } catch(const std::exception& e) {
        std::cerr << "Render image error: " << e.what() << std::endl;
    }
}

void EMCAServer::respondCameraData() {
    try {
        std::cout << "Send Camera Information ... " << std::flush;
        m_stream->writeShort(Message::EMCA_RESPONSE_CAMERA);
        m_renderer->getCameraData().serialize(m_stream.get());
        std::cout << "done" << std::endl;
    } catch (std::exception &e) {
        std::cerr << "Camera data error: " << e.what() << std::endl;
    }
}

void EMCAServer::respondSceneData() {
    try {
        m_stream->writeShort(Message::EMCA_RESPONSE_SCENE);

        const bool has_heatmap_data = m_dataApi->heatmap.hasData();
        m_stream->writeBool(has_heatmap_data);

        if (has_heatmap_data) {
            m_stream->writeString(m_dataApi->heatmap.colormap);
            m_stream->writeBool(m_dataApi->heatmap.show_colorbar);
            m_stream->writeString(m_dataApi->heatmap.label);

            const auto& heatmap_data = m_dataApi->heatmap.getHeatmapData();
            m_stream->writeUInt(static_cast<uint32_t>(heatmap_data.size()));
            std::cout << "Send Heatmap Information ... " << std::flush;
            for (const auto& heatmap : heatmap_data) {
                heatmap.serialize(m_stream.get());
            }
        }
        else {
            std::cout << "Send Mesh Information ... " << std::flush;
            m_stream->writeUInt(static_cast<uint32_t>(m_mesh_data.size()));
            for (const auto& mesh : m_mesh_data) {
                // send mesh to client
                mesh.serialize(m_stream.get());
            }
        }
        std::cout << "done" << std::endl;
    } catch (std::exception &e) {
        std::cerr << "Scene data error: " << e.what() << std::endl;
    }
}

void EMCAServer::respondRenderPixel() {
    try {
        m_dataApi->enable();
        uint32_t x = m_stream->readUInt();
        uint32_t y = m_stream->readUInt();
        uint32_t sampleCount = m_stream->readUInt();

        m_renderer->setSampleCount(sampleCount);

        std::cout << "Respond Pathdata of pixel: (" << x << ", " << y << ")" << std::endl;
        m_renderer->renderPixel(x, y);

        m_stream->writeShort(Message::EMCA_RESPONSE_RENDER_PIXEL);
        m_dataApi->serialize(m_stream.get());
        m_dataApi->disable();
        // clear the current path data - even when selecting the same pixel again, it will be recomputed
        m_dataApi->clear();
    } catch (std::exception &e) {
        std::cerr << "Render data error: " << e.what() << std::endl;
    }
}

bool EMCAServer::respondPluginRequest(short id) {
    Plugin *plugin = m_dataApi->plugins.getPluginById(id);
    if (!plugin)
        return false;
    try {
        plugin->deserialize(m_stream.get());
        plugin->run();
        plugin->serialize(m_stream.get());
        return true;
    } catch (std::exception &e) {
        std::cerr << "Plugin error: " << e.what() << std::endl;
    }

    return false;
}

void EMCAServer::SocketStream::read(void *ptr, size_t size) {
    char* data = reinterpret_cast<char*>(ptr);
    char* const end = data+size;

    while (data < end) {
        const ssize_t n = recv(m_clientSocket, data, static_cast<size_t>(std::distance(data, end)), 0);

        if (n == 0)
            throw std::runtime_error("read failed. remote has disconnected.");
        else if (n < 0)
            throw std::runtime_error("read failed. socket error: "+std::to_string(errno));

        data += n;
    }
}

void EMCAServer::SocketStream::write(const void *ptr, size_t size) {
    const char* data = reinterpret_cast<const char*>(ptr);
    const char* const end = data+size;

    while (data < end) {
        const ssize_t n = send(m_clientSocket, data, static_cast<size_t>(std::distance(data, end)), MSG_NOSIGNAL);

        if (n == EPIPE)
            throw std::runtime_error("write failed. remote has disconnected.");
        else if (n < 0)
            throw std::runtime_error("write failed. socket error: "+std::to_string(errno));

        data += n;
    }
}

EMCA_NAMESPACE_END

