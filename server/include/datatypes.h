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

#ifndef INCLUDE_EMCA_DATATYPES_H_
#define INCLUDE_EMCA_DATATYPES_H_

#include "platform.h"
#include "stream.h"

#include <array>
#include <cmath>
#include <cstdint>
#include <numeric>

EMCA_NAMESPACE_BEGIN

template <typename T, size_t N> struct TArray {
    static constexpr size_t dim = N;
    std::array<T, dim> p {};

    std::enable_if_t<(dim > 0), T> x() const { return p[0]; }
    std::enable_if_t<(dim > 1), T> y() const { return p[1]; }
    std::enable_if_t<(dim > 2), T> z() const { return p[2]; }

    std::enable_if_t<(dim > 0), T> norm() const { return std::sqrt(std::accumulate(p.begin(), p.end(), T(0), [](T sum, T element) -> T { return sum+element*element; })); }
    std::enable_if_t<(dim == 3), T> dot(const TArray<T,3>& other) const { return x()*other.x()+y()*other.y()+z()*other.z(); }

    void serialize(Stream *stream) const {
        stream->writeArray(p.data(), dim);
    }
};

template <typename T> struct TPoint2 : public TArray<T,2> {
    using TArray<T,2>::dim;
    using TArray<T,2>::p;

    TPoint2() = default;
    TPoint2(T x, T y) {
        p[0] = x;
        p[y] = y;
    }
};

template <typename T> struct TVec3 : public TArray<T,3> {
    using TArray<T,3>::dim;
    using TArray<T,3>::p;

    TVec3() = default;
    TVec3(T x, T y, T z) {
        p[0] = x;
        p[1] = y;
        p[2] = z;
    }

    TVec3& operator*=(T scale) { p[0]*=scale; p[1]*=scale; p[2]*=scale; return *this; }
    T normalize() { const float norm = this->norm(); *this *= 1.0f/norm; return norm; }
    TVec3 operator*(T scale) { TVec3 copy{*this}; copy*=scale; return copy; }
};

template <typename T>
TVec3<T> cross(const TVec3<T>& a, const TVec3<T>& b) {
    return {a.y()*b.z()-a.z()*b.y(), a.z()*b.x()-a.x()*b.z(), a.x()*b.y()-a.y()*b.x()};
}

template <typename T> struct TPoint3 : public TArray<T,3> {
    using TArray<T,3>::dim;
    using TArray<T,3>::p;
    using TArray<T,3>::x;
    using TArray<T,3>::y;
    using TArray<T,3>::z;

    TPoint3() = default;
    TPoint3(T x, T y, T z) {
        p[0] = x;
        p[1] = y;
        p[2] = z;
    }

    TVec3<T> operator-(const TPoint3& other) const {
        return TVec3<T>{x()-other.x(), y()-other.y(), z()-other.z()};
    }
    TPoint3<T> operator+(const TVec3<T>& other) const {
        return TPoint3<T>{x()+other.x(), y()+other.y(), z()+other.z()};
    }
};

template <typename T> struct TColor4 {
    static constexpr int dim = 4;
    std::array<T, dim> c {};

    TColor4() = default;
    TColor4(T r, T g, T b, T a=1) : c{r, g, b, a} {}

    T r() const { return c[0]; }
    T g() const { return c[1]; }
    T b() const { return c[2]; }
    T a() const { return c[3]; }

    void serialize(Stream *stream) const {
        stream->writeArray(c.data(), dim);
    }
};

typedef TPoint2<int32_t> Point2i;
typedef TPoint2<float>   Point2f;
typedef TPoint3<int32_t> Point3i;
typedef TPoint3<float>   Point3f;
typedef TVec3<uint32_t>  Vec3u;
typedef TVec3<float>     Vec3f;
typedef TColor4<float>   Color4f;

EMCA_NAMESPACE_END

#endif /* INCLUDE_EMCA_DATATYPES_H_ */
