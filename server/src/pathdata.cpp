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

#include <emca/pathdata.h>

#include <algorithm>

EMCA_NAMESPACE_BEGIN

void UserData::serialize(Stream *stream) const
{
    // write number of elements
    stream->writeUInt(static_cast<uint32_t>(m_data.size()));
    for (const auto& d: m_data) {
        stream->writeString(d.first);

        // write type identifier (https://docs.python.org/3/library/struct.html#format-characters) and data
        // TODO: convert endianness?
        switch (d.second.index()) {
        case 0: // bool
            stream->writeChar('?');
            stream->writeBool(std::get<bool>(d.second));
            break;
        case 1: // float
            stream->writeChar('f');
            stream->writeFloat(std::get<float>(d.second));
            break;
        case 2: // double
            stream->writeChar('d');
            stream->writeDouble(std::get<double>(d.second));
            break;
        case 3: // int
            stream->writeChar('i');
            stream->writeInt(std::get<int>(d.second));
            break;
        case 4: // std::pair<int, int>
            stream->writeChar('2');
            stream->writeChar('i');
            stream->writeInt(std::get<std::pair<int, int>>(d.second).first);
            stream->writeInt(std::get<std::pair<int, int>>(d.second).second);
            break;
        case 5: // std::pair<float, float>
            stream->writeChar('2');
            stream->writeChar('f');
            stream->writeFloat(std::get<std::pair<float, float>>(d.second).first);
            stream->writeFloat(std::get<std::pair<float, float>>(d.second).second);
            break;
        case 6: // std::tuple<int, int, int>
            stream->writeChar('3');
            stream->writeChar('i');
            stream->writeInt(std::get<0>(std::get<std::tuple<int, int, int>>(d.second)));
            stream->writeInt(std::get<1>(std::get<std::tuple<int, int, int>>(d.second)));
            stream->writeInt(std::get<2>(std::get<std::tuple<int, int, int>>(d.second)));
            break;
        case 7: // std::tuple<float, float, float>
            stream->writeChar('3');
            stream->writeChar('f');
            stream->writeFloat(std::get<0>(std::get<std::tuple<float, float, float>>(d.second)));
            stream->writeFloat(std::get<1>(std::get<std::tuple<float, float, float>>(d.second)));
            stream->writeFloat(std::get<2>(std::get<std::tuple<float, float, float>>(d.second)));
            break;
        case 8: // std::tuple<float, float, float, float>
            stream->writeChar('4');
            stream->writeChar('f');
            stream->writeFloat(std::get<0>(std::get<std::tuple<float, float, float, float>>(d.second)));
            stream->writeFloat(std::get<1>(std::get<std::tuple<float, float, float, float>>(d.second)));
            stream->writeFloat(std::get<2>(std::get<std::tuple<float, float, float, float>>(d.second)));
            stream->writeFloat(std::get<3>(std::get<std::tuple<float, float, float, float>>(d.second)));
            break;
        case 9: // std::string
            stream->writeChar('s');
            stream->writeString(std::get<std::string>(d.second));
            break;
        default:
            throw std::logic_error("Unhandled case");
        }
    }
}

void IntersectionData::setIntersectionPos(Point3f pos)
{
    m_hasPos = true;
    m_pos = pos;
}

void IntersectionData::setNextEventEstimationPos(Point3f pos, bool visible)
{
    m_hasNE = true;
    m_posNE = pos;
    m_visibleNE = visible;
}

void IntersectionData::setIntersectionEstimate(Color4f li)
{
    m_hasEstimate = true;
    m_estimate = li;
}

void IntersectionData::setIntersectionEmission(Color4f le)
{
    m_hasEmission = true;
    m_emission = le;
}

void IntersectionData::serialize(Stream *stream) const
{
    UserData::serialize(stream);

    stream->writeUInt(m_depthIdx);

    stream->writeBool(m_hasPos);
    if (m_hasPos)
        m_pos.serialize(stream);

    stream->writeBool(m_hasNE);
    if (m_hasNE)
    {
        m_posNE.serialize(stream);
        stream->writeBool(m_visibleNE);
    }

    stream->writeBool(m_hasEstimate);
    if (m_hasEstimate)
        m_estimate.serialize(stream);

    stream->writeBool(m_hasEmission);
    if (m_hasEmission)
        m_emission.serialize(stream);
}

void PathData::setDepthIdx(uint32_t depthIdx)
{
    if (depthIdx >= m_intersections.size()) {
        m_intersections.resize(depthIdx+1);
        m_pathDepth = depthIdx;
    }
    m_intersections.at(depthIdx).m_depthIdx = depthIdx;
}

void PathData::setIntersectionPos(uint32_t depthIdx, Point3f pos)
{
    m_intersections.at(depthIdx).setIntersectionPos(pos);
}

void PathData::setNextEventEstimationPos(uint32_t depthIdx, Point3f pos, bool occluded)
{
    m_intersections.at(depthIdx).setNextEventEstimationPos(pos, occluded);
}

void PathData::setIntersectionEstimate(uint32_t depthIdx, Color4f li)
{
    m_intersections.at(depthIdx).setIntersectionEstimate(li);
}

void PathData::setIntersectionEmission(uint32_t depthIdx, Color4f le)
{
    m_intersections.at(depthIdx).setIntersectionEmission(le);
}

void PathData::setPathOrigin(Point3f origin)
{
    m_pathOrigin = origin;
}

void PathData::setFinalEstimate(Color4f li)
{
    m_hasFinalEstimate = true;
    m_finalEstimate = li;
}

void PathData::serialize(Stream *stream) const
{
    UserData::serialize(stream);

    stream->writeUInt(m_sampleIdx);
    stream->writeUInt(m_pathDepth);

    m_pathOrigin.serialize(stream);

    stream->writeBool(m_hasFinalEstimate);
    if (m_hasFinalEstimate)
        m_finalEstimate.serialize(stream);

    uint32_t num_intersections = static_cast<uint32_t>(std::count_if(m_intersections.begin(), m_intersections.end(), [](const IntersectionData& segment) -> bool { return segment.m_depthIdx != -1U; }));
    stream->writeUInt(num_intersections);
    for (const auto& intersections : m_intersections)
    {
        if (intersections.m_depthIdx != -1U)
            intersections.serialize(stream);
    }
}

EMCA_NAMESPACE_END
