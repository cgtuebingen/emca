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

#ifndef INCLUDE_EMCA_HEATMAPDATA_H_
#define INCLUDE_EMCA_HEATMAPDATA_H_

#include "platform.h"
#include "datatypes.h"
#include "stream.h"
#include "messages.h"
#include "scenedata.h"

#include <vector>
#include <unordered_map>
#include <mutex>
#include <atomic>

EMCA_NAMESPACE_BEGIN

/**
 * @brief The HeatmapData class provides a low-memory data collection facility for gathering heatmap data on triangle meshes
 *
 * Data collection works as follows:
 * 1. sample mean is computd per face
 * 2. once sufficiently many samples per face are collected, it is subdivided internally while the renderer continues working with the coarse mesh
 *
 * 3. once data collection is finished, faces without any samples compute a weighted average of their neighbors value for a few iterations
 */
class HeatmapData {
public:

    class DynamicTessellation {
    public:
        DynamicTessellation(const Mesh* base, uint32_t num_subdivision_faces);
        DynamicTessellation(DynamicTessellation&& other) noexcept;

        /**
         * @brief subdivideFace applies a simple loop subdivision to the specified face (4 triangles are created by connecting the midpoints of each edge)
         * parallel calls are serialized by the subdivision mutex
         * @param face
         * @return base id of the 4 new subdivided faces or 0 on failure (due to capacity limit)
         */
        uint32_t subdivideFace(uint32_t face);

        bool isSubdivided(uint32_t face_id) const {
            return subdivisions.at(face_id) != 0;
        }

        uint32_t getSubdivisionId(uint32_t face_id) const {
            return subdivisions.at(face_id);
        }

        Vec3u getFace(uint32_t id) const {
            if (id < base_mesh->triangles.size())
                return base_mesh->triangles.at(id);
            return faces.at(id-base_mesh->triangles.size());
        }

        Point3f getVertex(uint32_t id) const {
            if (id < base_mesh->vertices.size())
                return base_mesh->vertices.at(id);
            return vertices.at(id-base_mesh->vertices.size());
        }

        uint32_t getMaxNumVertices() const {
            return base_mesh->vertices.size()+vertices.size();
        }

        uint32_t getMaxNumFaces() const {
            return base_mesh->triangles.size()+faces.size();
        }

        uint32_t getNumVertices() const {
            return base_mesh->vertices.size()+num_tess_vertices;
        }

        uint32_t getNumFaces() const { // includes replaced faces
            return base_mesh->triangles.size()+num_tess_faces;
        }

        /**
         * @brief getTessellatedFace
         * @param p
         * @param face
         * @return face id in the potentially tessellated mesh
         */
        uint32_t getTessellatedFace(const Point3f& p, uint32_t face) const;

        std::vector<Point3f> computeTessellatedVertices() const;
        std::vector<Vec3u> computeTessellatedFaces() const;

        const Mesh* getBaseMesh() const { return base_mesh; }


    private:
        const Mesh* base_mesh;

        // new vertices that need to be added to the base mesh for tessellation
        std::vector<Point3f> vertices;
        // new faces that need to be added to the base mesh for tessellation (including those that are replaced by further subdivisions)
        std::vector<Vec3u> faces;
        // base index of replacement faces per face (0 if not subdivided, subdivided into faces a (+0), b (+1), c (+2), and mid (+3))
        // TODO: this should be std::atomic<uint32_t>, but int reads and writes should be atomic either way and atomic<...> disables default move operations, making this much uglier to do.
        std::vector<uint32_t> subdivisions;

        // cache of midpoints created for tessellation (low vertex id) -> (high vertex id, midpoint vertex id)
        // allows to re-use midpoints on adjacent faces
        // only access this when the mutex is locked
        std::unordered_multimap<uint32_t, std::pair<uint32_t, uint32_t>> midpoint_cache;

        // number of additional vertices and faces
        // only modify these when the mutex is locked
        uint32_t num_tess_vertices {0};
        uint32_t num_tess_faces {0};

        std::mutex subdivision_mutex;

        static_assert (std::atomic<uint32_t>::is_always_lock_free, "do not use an 8/16 bit CPU :)");

        /**
         * @brief createMidpoint returns the id of the vertex in the middle of vertex_a and vertex_b
         * a new vertex is created if necessary.
         * @param vertex_a
         * @param vertex_b
         * @return
         */
        uint32_t createMidpoint(uint32_t vertex_a, uint32_t vertex_b);
    };

    struct alignas(16) IncrementalMean {
        // do not make this any larger, this needs to be exchanged atomically
        float mean_r;
        float mean_g;
        float mean_b;
        float weight;

        void operator+=(const IncrementalMean& other) {
            weight += other.weight;
            const float update_rate = other.weight/weight;
            mean_r += (other.mean_r-mean_r)*update_rate;
            mean_g += (other.mean_g-mean_g)*update_rate;
            mean_b += (other.mean_b-mean_b)*update_rate;
        }
        IncrementalMean operator+(const IncrementalMean& other) const {
            IncrementalMean copy{*this};
            copy += other;
            return copy;
        }
    };

    struct AtomicIncrementalMean { // wrapper to be updated atomically (64 bit should be atomic and thus be able to avoid a mutex)
        AtomicIncrementalMean() = default;
        ~AtomicIncrementalMean() = default;
        AtomicIncrementalMean(const AtomicIncrementalMean& other) : data{other.load()} {}

        std::atomic<IncrementalMean> data {IncrementalMean{0.0f, 0.0f, 0.0f, 0.0f}};

        IncrementalMean load(std::memory_order m = std::memory_order_relaxed) const { return data.load(m); }
        void store(const IncrementalMean& data, std::memory_order m = std::memory_order_relaxed) { this->data.store(data, m); }
        bool compare_exchange_weak(IncrementalMean& expected, IncrementalMean value, std::memory_order m = std::memory_order_relaxed) { return this->data.compare_exchange_weak(expected, value, m); }

        // while the oldest AMD64 processors do not support 16 byte compare and swap, all somewhat recent ones do (there is no guarantee at compile time, though)
        // if you need to make sure that this performs well on other hardware, consider using just one mean value rather than rgb.
        //static_assert(decltype(data)::is_always_lock_free, "this will be slow...");
    };

    // create data structures to collect heatmap data on the given mesh
    // dynamic subdivision is limited to the given number of subdivision faces
    HeatmapData(const Mesh* base, uint32_t num_subdivision_faces=1<<18) : tessellation{base, num_subdivision_faces}, faceData(tessellation.getMaxNumFaces()) {}

    // triangle mesh with refinement capabilities
    DynamicTessellation tessellation;

    // accumulated samples per face, vector is not to be resized during data collection
    std::vector<AtomicIncrementalMean> faceData;

    static constexpr float max_samples_per_face = 256.0f;

    void addSample(const Point3f& position, uint32_t face, float value_r, float value_g, float value_b, float weight=1.0f);

    // do only call this once after data collection has finished!
    void finalizeData(bool replace_with_density=false);

    std::vector<IncrementalMean> computeFaceData() const;

    // only used for the debug PLY-export
    std::vector<IncrementalMean> computeVertexData() const;

    void serialize(Stream *stream) const
    {
        // behave like a regular mesh ...
        Mesh proxy_mesh;
        proxy_mesh.vertices = tessellation.computeTessellatedVertices();
        proxy_mesh.triangles = tessellation.computeTessellatedFaces();
        proxy_mesh.specularColor = tessellation.getBaseMesh()->specularColor;
        proxy_mesh.diffuseColor = tessellation.getBaseMesh()->diffuseColor;

        // ... but with face colors
        const std::vector<IncrementalMean> faceData = computeFaceData();
        proxy_mesh.faceColors.reserve(proxy_mesh.triangles.size());
        for (const auto& data : faceData)
            proxy_mesh.faceColors.emplace_back(data.mean_r, data.mean_g, data.mean_b);

        proxy_mesh.serialize(stream);
    }
};

EMCA_NAMESPACE_END

#endif // INCLUDE_EMCA_HEATMAPDATA_H_
