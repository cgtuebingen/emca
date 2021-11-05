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

#include "dataapi.h"
#include "messages.h"

#include <fstream>
#include <algorithm>

EMCA_NAMESPACE_BEGIN

void DataApi::setPathIdx(uint32_t sampleIdx) {
    if (!m_isCollecting)
        return;
	m_currentSampleIdx = sampleIdx;
    m_currentDepthIdx = -1U;
    if (sampleIdx >= m_paths.size())
        m_paths.resize(sampleIdx+1);
    m_paths.at(sampleIdx).m_sampleIdx = sampleIdx; // enable path
}

void DataApi::setDepthIdx(uint32_t depthIdx) {
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
    if (!m_isCollecting || m_currentDepthIdx == -1U)
        return;
    m_paths.at(m_currentSampleIdx).setNextEventEstimationPos(m_currentDepthIdx, pos, visible);
}

void DataApi::setIntersectionEstimate(const Color4f& estimate) {
    if (!m_isCollecting || m_currentDepthIdx == -1U)
        return;
    m_paths.at(m_currentSampleIdx).setIntersectionEstimate(m_currentDepthIdx, estimate);
}

void DataApi::setIntersectionEmission(const Color4f& emission) {
    if (!m_isCollecting || m_currentDepthIdx == -1U)
        return;
    m_paths.at(m_currentSampleIdx).setIntersectionEmission(m_currentDepthIdx, emission);
}

void DataApi::setFinalEstimate(const Color4f& estimate) {
    if (!m_isCollecting)
        return;
    m_paths.at(m_currentSampleIdx).setFinalEstimate(estimate);
}

void DataApi::serialize(Stream *stream) const {
    uint32_t num_paths = std::count_if(m_paths.begin(), m_paths.end(), [](const auto& path) -> bool { return path.m_sampleIdx >= 0; });
    stream->writeUInt(num_paths);
	/* serialize path data */
    for (auto& path : m_paths) {
        if (path.m_sampleIdx != -1U) // only send enabled paths
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

void DataApi::HeatmapApi::initialize(const std::vector<Mesh>& meshes, uint32_t subdivision_budget) {
    heatmap_data.clear();
    finalized = false;

    heatmap_data.reserve(meshes.size());

    if (subdivision_budget > 0) {
        float totalSurfaceArea = std::accumulate(meshes.begin(), meshes.end(), 0.0f, [](float sum, const Mesh& mesh) -> float { return sum+mesh.surfaceArea; });
        for (const auto& mesh : meshes)
            heatmap_data.emplace_back(&mesh, mesh.surfaceArea/totalSurfaceArea*subdivision_budget);
    }
    else {
        for (const auto& mesh : meshes)
            heatmap_data.emplace_back(&mesh);
    }
}

void DataApi::HeatmapApi::reset()
{
    std::vector<HeatmapData> new_data;

    finalized = false;

    new_data.reserve(heatmap_data.size());
    for (const auto& heatmap : heatmap_data)
        new_data.emplace_back(heatmap.tessellation.getBaseMesh(), (heatmap.tessellation.getMaxNumFaces()-heatmap.tessellation.getBaseMesh()->triangles.size())/4);

    heatmap_data.swap(new_data);
}

void DataApi::HeatmapApi::addSample(uint32_t mesh_id, const Point3f& p, uint32_t face_id, const Color4f& value, float weight)
{
    if (!is_collecting)
        return;
    heatmap_data.at(mesh_id).addSample(p, face_id, value.r(), value.g(), value.b(), weight);
}

void DataApi::HeatmapApi::finalize() {
    is_collecting = false;

    if (heatmap_data.empty())
        return;

    if (!finalized)
        for (auto& heatmap : heatmap_data)
            heatmap.finalizeData(density_mode);

    finalized = true;

    if constexpr (/* disabled */ (false)) {
        // export heatmap data after rendering
        for (size_t i=0; i<heatmap_data.size(); ++i)
            exportPLY(std::string("heatmap")+std::to_string(i)+std::string(".ply"), i);
    }
}

void DataApi::HeatmapApi::exportPLY(const std::string &filename, uint32_t shape_id, bool ascii_mode) const
{
    const auto vertices = heatmap_data.at(shape_id).tessellation.computeTessellatedVertices();
    const auto faces = heatmap_data.at(shape_id).tessellation.computeTessellatedFaces();
    const auto values = heatmap_data.at(shape_id).computeVertexData();

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

