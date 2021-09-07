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

#ifndef INCLUDE_EMCA_DATATYPES_H_
#define INCLUDE_EMCA_DATATYPES_H_

#include "platform.h"
#include "stream.h"

#include <array>
#include <cmath>
#include <cstdint>

EMCA_NAMESPACE_BEGIN

template <typename T> struct TVec3;

template <typename T> struct TPoint2 {
    const static int dim = 2;
    std::array<T, dim> p = {0, 0};

    TPoint2() = default;
    TPoint2(T x, T y) : p{x, y} {}

    T x() const { return p[0]; }
    T y() const { return p[1]; }

    void serialize(Stream *stream) const {
        stream->writeArray(p, dim);
    }

};

template <typename T> struct TPoint3 {
    const static int dim = 3;
    std::array<T, dim> p = {0, 0, 0};

    TPoint3() = default;
    TPoint3(T x, T y, T z) : p{x, y, z} {}

    T x() const { return p[0]; }
    T y() const { return p[1]; }
    T z() const { return p[2]; }

    TVec3<T> operator-(const TPoint3& other) const {
        return TVec3<T>{x()-other.x(), y()-other.y(), z()-other.z()};
    }
    TPoint3<T> operator+(const TVec3<T>& other) const {
        return TPoint3<T>{x()+other.x(), y()+other.y(), z()+other.z()};
    }

    void serialize(Stream *stream) const {
        stream->writeArray(p.data(), dim);
    }
};

template <typename T> struct TVec2 {
    const static int dim = 2;
    std::array<T, dim> p = {0, 0};

    TVec2() = default;
    TVec2(T x, T y) : p{x, y} {}

    T x() const { return p[0]; }
    T y() const { return p[1]; }

    void serialize(Stream *stream) const {
        stream->writeArray(p.data(), dim);
    }

};

template <typename T> struct TVec3 {
    const static int dim = 3;
    std::array<T, dim> p = {0, 0, 0};

    TVec3() = default;
    TVec3(T x, T y, T z) : p{x, y, z} {}

    T x() const { return p[0]; }
    T y() const { return p[1]; }
    T z() const { return p[2]; }

    T norm() const { return std::sqrt(x()*x()+y()*y()+z()*z()); }
    void operator*=(T scale) { p[0]*=scale; p[1]*=scale; p[2]*=scale; }
    TVec3 operator*(T scale) { TVec3 copy{*this}; copy*=scale; return copy; }
    T normalize() { float norm = this->norm(); *this *= 1.0f/norm; return norm; }
    T dot(const TVec3<T>& other) const { return x()*other.x()+y()*other.y()+z()*other.z(); }

    void serialize(Stream *stream) const {
        stream->writeArray(p.data(), dim);
    }
};

template <typename T>
TVec3<T> cross(TVec3<T> a, TVec3<T> b) {
    return {a.y()*b.z()-a.z()*b.y(), a.z()*b.x()-a.x()*b.z(), a.x()*b.y()-a.y()*b.x()};
}

template <typename T> struct TColor3 {
    const static int dim = 3;
    std::array<T, dim> c = {0, 0, 0};

    TColor3() = default;
    TColor3(T r, T g, T b) : c{r, g, b} {}

    T r() const { return c[0]; }
    T g() const { return c[1]; }
    T b() const { return c[2]; }

    void serialize(Stream *stream) const {
        stream->writeArray(c.data(), dim);
        //FIXME: colors are transferred with 4 components
        stream->write(T(0));
    }
};

typedef TPoint2<float>   Point2f;
typedef TPoint2<int32_t> Point2i;
typedef TPoint3<float>   Point3f;
typedef TPoint3<int32_t> Point3i;
typedef TVec2<float>     Vec2f;
typedef TVec2<int32_t>   Vec2i;
typedef TVec3<float>     Vec3f;
typedef TVec3<int32_t>   Vec3i;
typedef TColor3<float>   Color3f;

EMCA_NAMESPACE_END

#endif /* INCLUDE_EMCA_DATATYPES_H_ */
