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

#include "heatmapdata.h"

#include <atomic>
#include <algorithm>

EMCA_NAMESPACE_BEGIN


HeatmapData::DynamicTessellation::DynamicTessellation(const Mesh *base, uint32_t num_subdivision_faces) : base_mesh{base},
    vertices(3*num_subdivision_faces),
    faces(4*num_subdivision_faces),
    subdivisions(base_mesh->triangles.size()+4*num_subdivision_faces) {
    midpoint_cache.reserve(3*num_subdivision_faces);
}

HeatmapData::DynamicTessellation::DynamicTessellation(HeatmapData::DynamicTessellation&& other) noexcept
    : base_mesh{other.base_mesh}, vertices{std::move(other.vertices)}, faces{std::move(other.faces)}, subdivisions{std::move(other.subdivisions)},
      midpoint_cache{std::move(other.midpoint_cache)}, num_tess_vertices{other.num_tess_vertices}, num_tess_faces{other.num_tess_faces}
{

}

uint32_t HeatmapData::DynamicTessellation::subdivideFace(uint32_t face) {
    std::lock_guard lock(subdivision_mutex);

    // return if some other thread performed the same subdivision
    uint32_t sub = subdivisions.at(face);
    if (sub != 0)
        return sub;

    // index of new subdivision faces
    sub = num_tess_faces;

    // return if out of capacity
    if (sub+4 >= faces.size() || num_tess_vertices+3 >= vertices.size())
        return 0;

    Vec3u vertex_ids = getFace(face);

    // lookup or create midpoints
    // midpoints are opposite to the original face's vertices
    uint32_t mid_a = createMidpoint(vertex_ids.y(), vertex_ids.z());
    uint32_t mid_b = createMidpoint(vertex_ids.z(), vertex_ids.x());
    uint32_t mid_c = createMidpoint(vertex_ids.x(), vertex_ids.y());

    // create subdivision faces
    // all faces are winding counter clockwise (to preserve up-vector)
    // face order is important for efficient lookup of the subdivided face
    faces.at(sub+0) = Vec3u(vertex_ids.x(), mid_c, mid_b);
    faces.at(sub+1) = Vec3u(vertex_ids.y(), mid_a, mid_c);
    faces.at(sub+2) = Vec3u(vertex_ids.z(), mid_b, mid_a);
    faces.at(sub+3) = Vec3u(mid_a, mid_b, mid_c);

    num_tess_faces += 4;

    sub += base_mesh->triangles.size();

    subdivisions.at(face) = sub;

    return sub;
}

uint32_t HeatmapData::DynamicTessellation::getTessellatedFace(const Point3f &p, uint32_t face) const {
    while (true) {
        const uint32_t sub = subdivisions.at(face);
        if (sub == 0) // not subdivided -- done
            return face;

        // get vertices of middle face
        const Vec3u vertex_ids = getFace(sub+3);
        const Point3f a = getVertex(vertex_ids.x());
        const Point3f b = getVertex(vertex_ids.y());
        const Point3f c = getVertex(vertex_ids.z());
        // compute edge vectors and up vector
        const Vec3f ab = b-a;
        const Vec3f ac = c-a;
        const Vec3f up = cross(ab, ac);
        const Vec3f ap = p-a;

        const Vec3f cross_b = cross(ap, ac);
        const Vec3f cross_c = cross(ab, ap);

        // we are outside near b if ap is left of ac
        if (up.dot(cross_b) < 0.0f)
            face = sub+1;
        // we are outside near c if ap is right of ab
        else if (up.dot(cross_c) < 0.0f)
            face = sub+2;
        // we are outside near a if the other two barycentric triangles are larger than the entire triangle - we already know that the point could only be outside near a
        else if (cross_b.norm()+cross_c.norm() > up.norm())
            face = sub+0;
        // we must be inside the center triangle
        else
            face = sub+3;
    }
}

std::vector<Point3f> HeatmapData::DynamicTessellation::computeTessellatedVertices() const {
    if (subdivisions.empty())
        return base_mesh->vertices;

    std::vector<Point3f> combinded_vertices;
    combinded_vertices.reserve(combinded_vertices.size()+num_tess_vertices);
    combinded_vertices.insert(combinded_vertices.end(), base_mesh->vertices.begin(), base_mesh->vertices.end());
    combinded_vertices.insert(combinded_vertices.end(), vertices.begin(), vertices.begin()+num_tess_vertices);
    return combinded_vertices;
}

std::vector<Vec3u> HeatmapData::DynamicTessellation::computeTessellatedFaces() const {
    if (subdivisions.empty())
        return base_mesh->triangles;

    uint32_t num_base_faces = static_cast<uint32_t>(base_mesh->triangles.size());

    std::vector<Vec3u> combined_faces;
    combined_faces.reserve(num_base_faces+3*subdivisions.size());
    uint32_t pos = 0;

    std::vector<uint32_t> subdivided_faces;
    subdivided_faces.reserve(faces.size()/4);
    for (uint32_t i=0; i<subdivisions.size(); ++i)
        if (subdivisions.at(i) != 0)
            subdivided_faces.push_back(i);

    for (uint32_t removed : subdivided_faces) {
        if (removed < num_base_faces) { // copy all remaining faces from the base mesh
            combined_faces.insert(combined_faces.end(), base_mesh->triangles.begin()+pos, base_mesh->triangles.begin()+removed);
        }
        else { // the next removed vertex is from the tessellated mesh
            if (pos < num_base_faces) { // when switching, copy the remaining base faces
                combined_faces.insert(combined_faces.end(), base_mesh->triangles.begin()+pos, base_mesh->triangles.end());
                pos = num_base_faces;
            }
            // same as with base faces, just with an offset
            combined_faces.insert(combined_faces.end(), faces.begin()+pos-num_base_faces, faces.begin()+removed-num_base_faces);
        }
        pos = removed+1;
    }
    // potentially add remaining base faces if not recusively subdivided
    if (pos < num_base_faces) {
        combined_faces.insert(combined_faces.end(), base_mesh->triangles.begin()+pos, base_mesh->triangles.end());
        pos = num_base_faces;
    }
    // add remaining subdivided faces
    combined_faces.insert(combined_faces.end(), faces.begin()+pos-num_base_faces, faces.begin()+num_tess_faces);

    if (combined_faces.size() != num_base_faces+3*subdivided_faces.size())
        throw std::logic_error("error during computation of tessellated faces");

    return combined_faces;
}

uint32_t HeatmapData::DynamicTessellation::createMidpoint(uint32_t vertex_a, uint32_t vertex_b) {
    if (vertex_b < vertex_a)
        std::swap(vertex_a, vertex_b);

    auto candidates = midpoint_cache.equal_range(vertex_a);
    for (auto it = candidates.first; it != candidates.second; ++it) {
        // if midpoint already exists, return its id
        if (it->second.first == vertex_b)
            return it->second.second;
    }

    Point3f a = getVertex(vertex_a);
    Point3f b = getVertex(vertex_b);

    // create the midpoint and return its id
    uint32_t mid_index = num_tess_vertices;
    vertices.at(mid_index) = Point3f((a.x()+b.x())*0.5f, (a.y()+b.y())*0.5f, (a.z()+b.z())*0.5f);

    ++num_tess_vertices;

    mid_index += base_mesh->vertices.size();

    midpoint_cache.insert(std::make_pair(vertex_a, std::make_pair(vertex_b, mid_index)));

    return mid_index;
}

void HeatmapData::addSample(const Point3f &position, uint32_t face, float value_r, float value_g, float value_b, float weight) {
    face = tessellation.getTessellatedFace(position, face);

    IncrementalMean face_data = faceData.at(face).load();

    if (face_data.weight > max_samples_per_face) {
        const uint32_t subdivision = tessellation.subdivideFace(face);

        // subdivision may fail if capacity limit is reached (returns 0)
        // or may have already been performed by another thread (returns subdivision id)
        if (subdivision > 0) {
            // update face based on new subdivision
            face = tessellation.getTessellatedFace(position, face);
        }
    }

    // atomic update
    while (!faceData.at(face).compare_exchange_weak(face_data, face_data+IncrementalMean{value_r, value_g, value_b, weight}));
}

void HeatmapData::finalizeData(bool replace_with_density) {
    // normalize data by the areas of the tesselated triangles
    for (uint32_t i=0; i<tessellation.getNumFaces(); ++i) {
        auto face_data = faceData.at(i).load();

        // handle subdivided faces
        {
            const uint32_t subdivision_id = tessellation.getSubdivisionId(i);
            if (subdivision_id) {
                auto subface_data_a   = faceData.at(subdivision_id+0).load();
                auto subface_data_b   = faceData.at(subdivision_id+1).load();
                auto subface_data_c   = faceData.at(subdivision_id+2).load();
                auto subface_data_mid = faceData.at(subdivision_id+3).load();

                // try to distribute sample data proportional to density in nested faces
                // if number of samples in nested faces is low, tend towards equal distribution
                // each subdivided face will naturally contain around max_samples_per_face samples (unless given additional samples from previous subdivisions redistributed with this code)
                // also, this code ignores nested subdivisions when computing the weights
                const float sub_weight_sum = subface_data_a.weight+subface_data_b.weight+subface_data_c.weight+subface_data_mid.weight;

                if (sub_weight_sum > max_samples_per_face) {
                    // distribute data proportionally
                    const float weight_factor = face_data.weight/sub_weight_sum;
                    face_data.weight = subface_data_a.weight*weight_factor;
                    faceData.at(subdivision_id+0).store(subface_data_a  +face_data);
                    face_data.weight = subface_data_b.weight*weight_factor;
                    faceData.at(subdivision_id+1).store(subface_data_b  +face_data);
                    face_data.weight = subface_data_c.weight*weight_factor;
                    faceData.at(subdivision_id+2).store(subface_data_c  +face_data);
                    face_data.weight = subface_data_mid.weight*weight_factor;
                    faceData.at(subdivision_id+3).store(subface_data_mid+face_data);
                }
                else {
                    // distribute data uniformly
                    face_data.weight *= 0.25f;
                    faceData.at(subdivision_id+0).store(subface_data_a  +face_data);
                    faceData.at(subdivision_id+1).store(subface_data_b  +face_data);
                    faceData.at(subdivision_id+2).store(subface_data_c  +face_data);
                    faceData.at(subdivision_id+3).store(subface_data_mid+face_data);
                }


                //faceData.at(i).store(IncrementalMean{0.0f, 0.0f, 0.0f, 0.0f});

                continue;
            }
        }

        if (replace_with_density) {
            if (face_data.weight > 0.0f) {
                const Vec3u face = tessellation.getFace(i);
                Point3f a = tessellation.getVertex(face.x());
                Point3f b = tessellation.getVertex(face.y());
                Point3f c = tessellation.getVertex(face.z());

                const float triangle_area = cross(b-a, c-a).norm()*0.5f;

                face_data.mean_r = face_data.mean_g = face_data.mean_b = face_data.weight/triangle_area;
            }
            else
                face_data.mean_r = face_data.mean_g = face_data.mean_b = 0.0f;

            face_data.weight = 1.0f;

            faceData.at(i).store(face_data);
        }
    }
}

std::vector<HeatmapData::IncrementalMean> HeatmapData::computeFaceData() const
{
    const uint32_t num_faces = tessellation.getNumFaces(); // includes replaced ones
    // gathers vertex ids of unknown faces - in a second pass, neighboring faces are identified
    // vertex --> id of unknown face
    std::unordered_multimap<uint32_t, uint32_t> unknown_face_vertices;

    // copy of the face data (with gaps to be filled in)
    std::vector<IncrementalMean> filled_face_data(num_faces);

    // checks if there is any data to not search for neighboring faces with values if there are none
    bool got_any_data = false;

    for (uint32_t i=0; i<num_faces; ++i) {
        if (tessellation.isSubdivided(i))
            continue;

        auto face_data = faceData.at(i).load();
        // copy over face data -- copy needed to fill in the gaps
        filled_face_data.at(i) = face_data;

        // check for faces without data and add them to the multimap
        if (face_data.weight == 0.0f || std::isnan(face_data.weight)) {
            Vec3u vertices = tessellation.getFace(i);
            unknown_face_vertices.insert({{vertices.x(), i}, {vertices.y(), i}, {vertices.z(), i}});
            filled_face_data.at(i) = IncrementalMean{0.0f, 0.0f, 0.0f, 0.0f};
        }
        else
            got_any_data = true;
    }

    // if there is some data, distribute it to neighboring faces that lack data
    if (got_any_data && unknown_face_vertices.size() > 0) {
        // loop through the faces to find neighboring faces to fill in unkown data
        // id of unknown face --> neighboring face
        std::unordered_multimap<uint32_t, uint32_t> unknown_face_neighbors;
        unknown_face_neighbors.reserve(unknown_face_neighbors.size()*5); // expect around 5 neighboring faces per vertex

        for (uint32_t i=0; i<num_faces; ++i) {
            // skip subdivided faces
            if (tessellation.isSubdivided(i))
                continue;

            Vec3u face = tessellation.getFace(i);
            const auto it_x = unknown_face_vertices.find(face.x());
            const auto it_y = unknown_face_vertices.find(face.y());
            const auto it_z = unknown_face_vertices.find(face.z());
            if (it_x != unknown_face_vertices.end() && it_x->second != i)
                unknown_face_neighbors.emplace(it_x->second, i);
            if (it_y != unknown_face_vertices.end() && it_y->second != i)
                unknown_face_neighbors.emplace(it_y->second, i);
            if (it_z != unknown_face_vertices.end() && it_z->second != i)
                unknown_face_neighbors.emplace(it_z->second, i);
        }

        // done with those
        unknown_face_vertices.clear();

        // distribute data to neighboring faces without data
        //TODO: check what difference this actually makes -- looked like it does not do much in previous tests
        uint32_t filled_faces;
        for (uint32_t i=0; i<3; ++i) {
            filled_faces = 0;
            uint32_t num_valid = 0;
            uint32_t unknown_face_id = -1U;
            for (auto it=unknown_face_neighbors.begin(); it != unknown_face_neighbors.end(); ++it) {
                if (it->first != unknown_face_id) {
                    if (num_valid > 0) {
                        filled_face_data.at(unknown_face_id).weight /= float(num_valid*32); // divide by number of valid samples and also divide by another large factor for estimating
                        // erase face from list of unknowns
                        // erasing from unorederd_multimap only invalidates iterators pointing to the removed elements - this should be fine
                        unknown_face_neighbors.erase(unknown_face_id);
                        num_valid = 0;
                        ++filled_faces;
                    }
                    unknown_face_id = it->first;
                }
                if (filled_face_data.at(it->second).weight > 0.0f) {
                    filled_face_data.at(unknown_face_id) += filled_face_data.at(it->second);
                    ++num_valid;
                }
            }
            if (num_valid > 0) {
                filled_face_data.at(unknown_face_id).weight /= float(num_valid*32); // divide by number of valid samples and also divide by another large factor for estimating
                // erase face from list of unknowns
                // erasing from unorederd_multimap only invalidates iterators pointing to the removed elements - this should be fine
                unknown_face_neighbors.erase(unknown_face_id);
                ++filled_faces;
            }

            std::cout << "filled in the data of " << filled_faces << " faces using their neighbors." << std::endl;

            // terminate early if possible
            if (filled_faces == 0 || unknown_face_neighbors.empty())
                break;
        }
    }

    // erase subdivided faces
    //TODO: don't add them in the first place
    std::vector<IncrementalMean> filtered_face_data;
    filtered_face_data.reserve(filled_face_data.size());
    for (uint32_t i=0; i < num_faces; ++i)
        if (!tessellation.isSubdivided(i))
            filtered_face_data.push_back(filled_face_data.at(i));

    return filtered_face_data;
}

std::vector<HeatmapData::IncrementalMean> HeatmapData::computeVertexData() const
{
    const uint32_t num_faces = tessellation.getNumFaces(); // includes replaced ones
    const uint32_t num_vertices = tessellation.getNumVertices();

    // vertex colors will be accumulated here
    std::vector<IncrementalMean> vertexData(num_vertices);

    const auto face_data = computeFaceData();

    uint32_t num_subdivisions = 0;

    for (uint32_t i=0; i<num_faces; ++i) {
        // skip data from subdivided faces
        if (tessellation.isSubdivided(i)) {
            ++num_subdivisions;
            continue;
        }

        // accumulate the rest
        Vec3u vertex_ids = tessellation.getFace(i);
        IncrementalMean data = face_data.at(i-num_subdivisions);

        for (uint32_t j=0; j<3; ++j) // there may be a clever weighting scheme to apply here - this kind of works though
            vertexData.at(static_cast<size_t>(vertex_ids.p.at(j))) += data;
    }
    return vertexData;
}

EMCA_NAMESPACE_END

