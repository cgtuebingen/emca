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

#ifndef INCLUDE_EMCA_EMCADATA_H_
#define INCLUDE_EMCA_EMCADATA_H_

#include "platform.h"
#include "datatypes.h"
#include "stream.h"
#include "messages.h"

EMCA_NAMESPACE_BEGIN

struct Camera
{
    float nearClip;
    float farClip;
    float focusDist;
    float fov;
    Vec3f up;
    Vec3f dir;
    Point3f origin;

    Camera() = default;
    Camera(float _nearClip, float _farClip, float _focusDist, float _fov,
           Vec3f _up, Vec3f _dir, Point3f _origin)
        : nearClip(_nearClip), farClip(_farClip), focusDist(_focusDist),
          fov(_fov), up(_up), dir(_dir), origin(_origin) {}

    void serialize(Stream *stream) const
    {
        stream->writeFloat(nearClip);
        stream->writeFloat(farClip);
        stream->writeFloat(focusDist);
        stream->writeFloat(fov);
        up.serialize(stream);
        dir.serialize(stream);
        origin.serialize(stream);
    }
};

struct Mesh
{
    std::vector<Point3f> vertices;
    std::vector<Vec3i> triangles;
    std::vector<Point3f> faceColors; // optional, leave empty if not used, otherwise provide one value per face
    Color3f diffuseColor;
    Color3f specularColor;

    void serialize(Stream *stream) const
    {
        if (faceColors.size() && faceColors.size() != triangles.size())
            throw std::logic_error("the number of face colors does not match the number of faces");

        stream->writeShort(ShapeType::TriangleMesh);
        stream->writeUInt(vertices.size());
        stream->writeArray(reinterpret_cast<const float *>(vertices.data()), vertices.size() * 3);
        stream->writeUInt(triangles.size());
        stream->writeArray(reinterpret_cast<const int *>(triangles.data()), triangles.size() * 3);
        stream->writeUInt(faceColors.size());
        stream->writeArray(reinterpret_cast<const int *>(faceColors.data()), faceColors.size() * 3);
        diffuseColor.serialize(stream);
        specularColor.serialize(stream);
    }
};

struct Sphere
{
    Point3f center;
    float radius;
    Color3f diffuse;
    Color3f specular;

    Sphere() = default;
    Sphere(Point3f _center, float _radius) : center(_center), radius(_radius) {}

    void serialize(Stream *stream) const
    {
        stream->writeShort(ShapeType::SphereMesh);
        stream->writeFloat(radius);
        center.serialize(stream);
        diffuse.serialize(stream);
        specular.serialize(stream);
    }
};

EMCA_NAMESPACE_END

#endif // INCLUDE_EMCA_EMCADATA_H_
