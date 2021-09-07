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

#ifndef INCLUDE_EMCA_PATHDATA_H_
#define INCLUDE_EMCA_PATHDATA_H_

#include "platform.h"
#include "datatypes.h"
#include "stream.h"

#if __cplusplus < 201703L
#error C++17 is required for <variant>. If you cannot use C++17, replace the variant with a tagged union.
#endif
#include <variant>
#include <vector>

EMCA_NAMESPACE_BEGIN

class UserData
{
public:
    // this is a bit wasteful for scalars, since std::string is 32 bytes (+ heap) (on this machine, with this compiler), but it makes things much easier
    // 2 or 3 floats are points, 4 floats are color values (with alpha channel, although it is discarded by the client at the moment)
    using Data = std::variant<bool, float, double, int, std::pair<int, int>, std::pair<float, float>, std::tuple<int, int, int>, std::tuple<float, float, float>, std::tuple<float, float, float, float>, std::string>;

    template <typename T, std::enable_if_t<std::is_fundamental_v<T> || std::is_same_v<T, std::string>, int> = 0>
    void add(const std::string& s, const T& value) {
        m_data.emplace_back(s, value);
    }

    template <typename T, std::enable_if_t<std::is_fundamental_v<T>, int> = 0>
    void add(const std::string& s, const T& value1, const T& value2) {
        m_data.emplace_back(s, std::make_pair(value1, value2));
    }

    template <typename T, std::enable_if_t<std::is_fundamental_v<T>, int> = 0>
    void add(const std::string& s, const T& value1, const T& value2, const T& value3) {
        m_data.emplace_back(s, std::make_tuple(value1, value2, value3));
    }

    template <typename T, std::enable_if_t<std::is_fundamental_v<T>, int> = 0>
    void add(const std::string& s, const T& value1, const T& value2, const T& value3, const T& value4) {
        m_data.emplace_back(s, std::make_tuple(value1, value2, value3, value4));
    }

    virtual void serialize(Stream *stream) const;

protected:
    virtual ~UserData() = default;
private:
    std::vector<std::pair<std::string, Data>> m_data;
};

class IntersectionData final : public UserData
{
public:
    void setIntersectionPos(Point3f pos);
    void setNextEventEstimationPos(Point3f pos, bool visible);
    void setIntersectionEstimate(Color3f li);
    void setIntersectionEmission(Color3f le);

    void serialize(Stream *stream) const override;

private:
    int m_depthIdx {-1}; /* current path depth */
    Point3f m_pos;       /* intersection point in world coordinates */
    Point3f m_posNE;     /* next event estimation point in world coordinates */
    Color3f m_estimate;  /* current computed estimate at this intersection */
    Color3f m_emission;  /* emission at current intersection point */

    bool m_hasPos      {false};
    bool m_hasNE       {false};
    bool m_visibleNE   {false};
    bool m_hasEstimate {false};
    bool m_hasEmission {false};

    friend class PathData;
};

class PathData final : public UserData
{
public:
    void setDepthIdx(int32_t depthIdx);
    void setIntersectionPos(uint32_t depthIdx, Point3f pos);
    void setNextEventEstimationPos(uint32_t depthIdx, Point3f pos, bool occluded);
    void setIntersectionEstimate(uint32_t depthIdx, Color3f li);
    void setIntersectionEmission(uint32_t depthIdx, Color3f le);

    void setPathOrigin(Point3f origin);
    void setFinalEstimate(Color3f li);

    IntersectionData& intersectionAt(int32_t depthIdx) {
        return m_intersections.at(depthIdx);
    }

    void serialize(Stream *stream) const override;

private:
    std::vector<IntersectionData> m_intersections; /* data dictionary about each intersection */
    int32_t m_sampleIdx {-1};                      /* Current sample index */
    int32_t m_pathDepth {-1};                      /* Path length, amount of Intersections */
    Point3f m_pathOrigin;                          /* Path origin */
    Color3f m_finalEstimate;                       /* final light estimation of path */
    bool m_hasFinalEstimate {false};

    friend class DataApi;
};

EMCA_NAMESPACE_END

#endif /* INCLUDE_EMCA_PATHDATA_H_ */
