/*
	EMCA - Explorer Monte-Carlo based Alorithm (Shared Server Library)
	comes with an Apache License 2.0
	(c) Christoph Kreisl 2020

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

#include "dataapi.h"
#include "messages.h"

#include <fstream>
#include <algorithm>

EMCA_NAMESPACE_BEGIN

void DataApi::setPathIdx(int32_t sampleIdx) {
    if (!m_isCollecting)
        return;
	m_currentSampleIdx = sampleIdx;
    m_currentDepthIdx = -1;
    if (sampleIdx >= static_cast<int32_t>(m_paths.size()))
        m_paths.resize(sampleIdx+1);
    m_paths.at(sampleIdx).m_sampleIdx = sampleIdx; // enable path
}

void DataApi::setDepthIdx(int32_t depthIdx) {
    if (!m_isCollecting)
        return;
	m_currentDepthIdx = depthIdx;
    m_paths.at(m_currentSampleIdx).setDepthIdx(depthIdx);
}

void DataApi::setPathOrigin(const Point3f& origin) {
    if (!m_isCollecting)
        return;
    m_paths.at(m_currentSampleIdx).setPathOrigin(origin);
}

void DataApi::setIntersectionPos(const Point3f& pos) {
    if (!m_isCollecting)
        return;
    m_paths.at(m_currentSampleIdx).setIntersectionPos(m_currentDepthIdx, pos);
}

void DataApi::setNextEventEstimationPos(const Point3f& pos, bool visible) {
    if (!m_isCollecting || m_currentDepthIdx == -1)
        return;
    m_paths.at(m_currentSampleIdx).setNextEventEstimationPos(m_currentDepthIdx, pos, visible);
}

void DataApi::setIntersectionEstimate(const Color3f& estimate) {
    if (!m_isCollecting || m_currentDepthIdx == -1)
        return;
    m_paths.at(m_currentSampleIdx).setIntersectionEstimate(m_currentDepthIdx, estimate);
}

void DataApi::setIntersectionEmission(const Color3f& emission) {
    if (!m_isCollecting || m_currentDepthIdx == -1)
        return;
    m_paths.at(m_currentSampleIdx).setIntersectionEmission(m_currentDepthIdx, emission);
}

void DataApi::setFinalEstimate(const Color3f& estimate) {
    if (!m_isCollecting)
        return;
    m_paths.at(m_currentSampleIdx).setFinalEstimate(estimate);
}

void DataApi::serialize(Stream *stream) const {
    uint32_t num_paths = std::count_if(m_paths.begin(), m_paths.end(), [](const auto& path) -> bool { return path.m_sampleIdx >= 0; });
    stream->writeUInt(num_paths);
	/* serialize path data */
    for (auto& path : m_paths) {
        if (path.m_sampleIdx >= 0) // only send enabled paths
            path.serialize(stream);
	}
}

void DataApi::PluginApi::addPlugin(std::unique_ptr<Plugin>&& plugin) {
    if (getPluginById(plugin->getId())) {
        throw std::logic_error("Plugin ID is already occupied");
    } else {
        m_plugins.insert(std::make_pair(plugin->getId(), std::move(plugin)));
    }
}

Plugin* DataApi::PluginApi::getPluginByName(std::string name) {
    for (auto& [id, plugin] : m_plugins) {
        if (plugin->getName() == name)
            return plugin.get();
    }
    return nullptr;
}

Plugin* DataApi::PluginApi::getPluginById(short id) {
    auto it = m_plugins.find(id);
    return it == m_plugins.end() ? nullptr : it->second.get();
}

std::vector<short> DataApi::PluginApi::getPluginIds()
{
    std::vector<short> ret;
    for (const auto& [id, plugin] : m_plugins)
        ret.push_back(id);

    return ret;
}

void DataApi::PluginApi::printPlugins() const {
    for (const auto& [id, plugin] : m_plugins)
        std::cout << "PluginName: " << plugin->getName() << " PluginID: " << id << std::endl;
}

void DataApi::HeatmapApi::initialize(const std::vector<Mesh>& meshes, const std::vector<uint32_t>& subdivision_budgets) {
    m_data.clear();
    finalized = false;

    m_data.reserve(meshes.size());

    if (subdivision_budgets.empty()) {
        for (const auto& mesh : meshes)
            m_data.emplace_back(&mesh);
    }
    else {
        if (meshes.size() != subdivision_budgets.size())
            throw std::logic_error("one subdivision budget is required per mesh");

        for (size_t i=0; i<meshes.size(); ++i) {
            m_data.emplace_back(&meshes.at(i), subdivision_budgets.at(i));
        }
    }
}

void DataApi::HeatmapApi::addSample(uint32_t mesh_id, const Point3f& p, uint32_t face_id, const Color3f& value, float weight)
{
    if (!is_collecting)
        return;
    m_data.at(mesh_id).addSample(p, face_id, value.r(), value.g(), value.b(), weight);
}

void DataApi::HeatmapApi::finalize() {
    if (m_data.empty())
        return;

    if (!finalized)
        for (auto& heatmap : m_data)
            heatmap.finalizeData(density_mode);

    finalized = true;

    if constexpr (/* disabled */ (false)) {
        // export heatmap data after rendering
        for (size_t i=0; i<m_data.size(); ++i)
            exportPLY(std::string("heatmap")+std::to_string(i)+std::string(".ply"), i);
    }
}

void DataApi::HeatmapApi::exportPLY(const std::string &filename, uint32_t shape_id, bool ascii_mode) const
{
    const auto vertices = m_data.at(shape_id).tessellation.computeTessellatedVertices();
    const auto faces = m_data.at(shape_id).tessellation.computeTessellatedFaces();
    const auto values = m_data.at(shape_id).computeVertexData();

    std::ofstream file(filename, std::ios_base::out);
    file << "ply\n";
    if (ascii_mode)
        file << "format ascii 1.0\n";
    else
        file << "format binary_little_endian 1.0\n";
    file << "element vertex " << vertices.size() << '\n'
         << "property float x\n"
         << "property float y\n"
         << "property float z\n"
         << "property float red\n"
         << "property float green\n"
         << "property float blue\n"
         << "element face " << faces.size() << '\n'
         << "property list uchar uint32 vertex_indices\n"
         << "end_header\n";
    for (uint32_t i=0; i<vertices.size(); ++i) {
        if (ascii_mode)
            file << vertices[i].x() << ' ' << vertices[i].y() << ' '  << vertices[i].z() << ' '
                 << values[i].mean_r << ' ' << values[i].mean_g << ' '  << values[i].mean_b << '\n';
        else { // binary mode
            file.write(reinterpret_cast<const char*>(vertices[i].p.data()), 3*sizeof(float));
            float vertex_color[3];
            vertex_color[0] = values[i].mean_r;
            vertex_color[1] = values[i].mean_g;
            vertex_color[2] = values[i].mean_b;
            file.write(reinterpret_cast<const char*>(vertex_color), 3*sizeof(float));
        }
    }
    for (const auto& face : faces) {
        if (ascii_mode)
            file << 3 << ' ' << face.x() << ' ' << face.y() << ' ' << face.z() << '\n';
        else { // binary mode
            const uint8_t num_vertices = 3;
            file.write(reinterpret_cast<const char*>(&num_vertices), sizeof(uint8_t));
            file.write(reinterpret_cast<const char*>(face.p.data()), sizeof(uint32_t)*3);
        }
    }
    file.close();
}

EMCA_NAMESPACE_END

