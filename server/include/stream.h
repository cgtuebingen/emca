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

#ifndef INCLUDE_EMCA_STREAM_H
#define INCLUDE_EMCA_STREAM_H

#include "platform.h"
#include <cinttypes>
#include <type_traits>

EMCA_NAMESPACE_BEGIN

class Stream {
public:
    // generic read/write functions for fundamental data types
    template<typename T, std::enable_if_t<std::is_fundamental_v<T>, int> = 0>
    T read() {
        T result;
        read(&result, sizeof(T));
        return result;
    }

    template<typename T, std::enable_if_t<std::is_fundamental_v<T>, int> = 0>
    void write(T value) {
        write(&value, sizeof(T));
    }

    // general write functions for arrays of fundamental data types
    template <typename T, std::enable_if_t<std::is_fundamental_v<T>, int> = 0>
    void writeArray(const T *array, size_t count) {
        write(array, sizeof(T)*count);
    }
    template <typename T, size_t N, std::enable_if_t<std::is_fundamental_v<T>, int> = 0>
    inline void writeArray(const T (&arr)[N]) {
        writeArray(&arr[0], N);
    }

    // convenience read/write functions for fundamental data types
    void writeBool(bool value)           {write(char(value));}
    void writeShort(int16_t value)       {write(value);}
    void writeUShort(uint16_t value)     {write(value);}
    void writeInt(int32_t value)         {write(value);}
    void writeUInt(uint32_t value)       {write(value);}
    void writeLong(int64_t value)        {write(value);}
    void writeULong(uint64_t value)      {write(value);}
    void writeChar(char value)           {write(value);}
    void writeUChar(unsigned char value) {write(value);}
    void writeFloat(float value)         {write(value);}
    void writeDouble(double value)       {write(value);}

    bool          readBool()   {return bool(read<char>());}
    int16_t       readShort()  {return read<int16_t>();}
    uint16_t      readUShort() {return read<uint16_t>();}
    int32_t       readInt()    {return read<int32_t>();}
    uint32_t      readUInt()   {return read<uint32_t>();}
    int64_t       readLong()   {return read<int64_t>();}
    uint64_t      readULong()  {return read<uint64_t>();}
    char          readChar()   {return read<char>();}
    unsigned char readUChar()  {return read<unsigned char>();}
    float         readFloat()  {return read<float>();}
    double        readDouble() {return read<double>();}

    // read string prefixed by length
    std::string readString() {
        size_t length = readULong();
        std::string buffer(length, '\0');
        read(buffer.data(), length);
        return buffer;
    }

    // write string prefixed by length
    void writeString(const std::string& value) {
        writeULong(value.length());
        write(value.c_str(), sizeof(char) * value.length());
    }

protected:
    virtual ~Stream() = default;

private:
    // abstract base - these need to be implemented by the specific implementation
    virtual void read(void *ptr, size_t size) = 0;
    virtual void write(const void *ptr, size_t size) = 0;
};

EMCA_NAMESPACE_END

#endif /* INCLUDE_EMCA_STREAM_H */
