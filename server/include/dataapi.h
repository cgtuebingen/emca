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

#ifndef INCLUDE_EMCA_DATAAPI_H_
#define INCLUDE_EMCA_DATAAPI_H_

#include "platform.h"
#include "stream.h"
#include "plugin.h"
#include "pathdata.h"
#include "scenedata.h"
#include "heatmapdata.h"

#include <string>
#include <vector>
#include <memory>
#include <unordered_map>

EMCA_NAMESPACE_BEGIN

class DataApi {
public:
    virtual ~DataApi() = default;

    void setPathIdx(int32_t sampleIdx);
    void setDepthIdx(int32_t depthIdx);

    void setPathOrigin(const Point3f& origin);
    void setIntersectionPos(const Point3f& pos);
    void setNextEventEstimationPos(const Point3f& pos, bool visible);
    void setIntersectionEstimate(const Color3f& estimate);
    void setIntersectionEmission(const Color3f& emission);
    void setFinalEstimate(const Color3f& estimate);

    template <typename T, std::enable_if_t<std::is_fundamental_v<T> || std::is_same_v<T, std::string>, int> = 0>
    void addPathData(const std::string& s, const T& val) {
        if(m_isCollecting)
            m_paths.at(m_currentSampleIdx).add(s, val);
    }

    template <typename T, std::enable_if_t<std::is_fundamental_v<T>, int> = 0>
    void addPathData(const std::string& s, const T& val1, const T& val2) {
        if(m_isCollecting)
            m_paths.at(m_currentSampleIdx).add(s, val1, val2);
    }

    template <typename T, std::enable_if_t<std::is_fundamental_v<T>, int> = 0>
    void addPathData(const std::string& s, const T& val1, const T& val2, const T& val3) {
        if(m_isCollecting)
            m_paths.at(m_currentSampleIdx).add(s, val1, val2, val3);
    }

    template <typename T, std::enable_if_t<std::is_fundamental_v<T>, int> = 0>
    void addPathData(const std::string& s, const T& val1, const T& val2, const T& val3, const T& val4) {
        if(m_isCollecting)
            m_paths.at(m_currentSampleIdx).add(s, val1, val2, val3, val4);
    }

    template <typename T, std::enable_if_t<std::is_fundamental_v<T> || std::is_same_v<T, std::string>, int> = 0>
    void addIntersectionData(const std::string& s, const T& val) {
        if (m_isCollecting && m_currentDepthIdx >= 0)
            m_paths.at(m_currentSampleIdx).intersectionAt(m_currentDepthIdx).add(s, val);
    }

    template <typename T, std::enable_if_t<std::is_fundamental_v<T>, int> = 0>
    void addIntersectionData(const std::string& s, const T& val1, const T& val2) {
        if (m_isCollecting && m_currentDepthIdx >= 0)
            m_paths.at(m_currentSampleIdx).intersectionAt(m_currentDepthIdx).add(s, val1, val2);
    }

    template <typename T, std::enable_if_t<std::is_fundamental_v<T>, int> = 0>
    void addIntersectionData(const std::string& s, const T& val1, const T& val2, const T& val3) {
        if (m_isCollecting && m_currentDepthIdx >= 0)
            m_paths.at(m_currentSampleIdx).intersectionAt(m_currentDepthIdx).add(s, val1, val2, val3);
    }

    template <typename T, std::enable_if_t<std::is_fundamental_v<T>, int> = 0>
    void addIntersectionData(const std::string& s, const T& val1, const T& val2, const T& val3, const T& val4) {
        if (m_isCollecting && m_currentDepthIdx >= 0)
            m_paths.at(m_currentSampleIdx).intersectionAt(m_currentDepthIdx).add(s, val1, val2, val3, val4);
    }

    void serialize(Stream *stream) const;

    void enable()  { m_isCollecting = true; }
    void disable() { m_isCollecting = false; }
    bool isCollecting() const { return m_isCollecting; }

    class PluginApi {
    public:
        void addPlugin(std::unique_ptr<Plugin>&& plugin);

        Plugin* getPluginByName(std::string name);
        Plugin* getPluginById(short id);

        std::vector<short> getPluginIds();
        void printPlugins() const;

    private:
        std::unordered_map<short, std::unique_ptr<Plugin>> m_plugins;
    } plugins;

    class HeatmapApi {
    public:
        void initialize(const std::vector<Mesh>& meshes, const std::vector<uint32_t>& subdivision_budgets);
        void enable() { is_collecting = !finalized && !m_data.empty(); }
        void disable() { is_collecting = false; }
        bool isCollecting() const { return is_collecting; }

        void addSample(uint32_t mesh_id, const Point3f& p, uint32_t face_id, const Color3f& value, float weight=1.0f);

        /// small preprocessing step that propagates values to children of subdivided faces
        /// also replaces RGB values by sample density if requested
        void finalize();

        bool hasData() const { return finalized; }
        const std::vector<HeatmapData>& getHeatmapData() { if (!finalized) throw std::logic_error("finalize the data first"); return m_data; }

        // display options for the visualization client
        std::string label    {"unknown"};
        std::string colormap {"plasma"};
        bool show_colorbar   {true};

        // if set, the collected data is replaced by the sample data during the finalization step
        bool density_mode    {false};

    private:
        std::vector<HeatmapData> m_data;
        bool is_collecting {false};
        bool finalized     {false};

        /// debug function which exports the heatmap of a single mesh into a ply file
        void exportPLY(const std::string& filename, uint32_t shape_id, bool ascii_mode=true) const;
    } heatmap;

    void clear() { m_paths.clear(); }

    void setMeshData(std::vector<Mesh>&& mesh_data) { m_meshes.swap(mesh_data); }
    const std::vector<Mesh>& getMeshData() const { return m_meshes; }

    void setCamera(const Camera& camera) { m_camera = camera; }
    const Camera& getCamera() const { return m_camera; }

protected:
    Camera m_camera;
    std::vector<Mesh> m_meshes;

    std::vector<PathData> m_paths;
    int32_t m_currentSampleIdx {-1};
    int32_t m_currentDepthIdx  {-1};
    bool m_isCollecting        {false};
};

EMCA_NAMESPACE_END

#endif // INCLUDE_EMCA_DATAAPI_H_
