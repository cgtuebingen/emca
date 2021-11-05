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

#ifndef INCLUDE_EMCA_PLUGIN_H_
#define INCLUDE_EMCA_PLUGIN_H_

#include "platform.h"
#include "stream.h"

EMCA_NAMESPACE_BEGIN

class Plugin {
public:
    Plugin(std::string name, short id) : m_name(name), m_id(id) { }
    virtual ~Plugin() = default;

    virtual void run() = 0;
    virtual void serialize(Stream *stream) const = 0;
    virtual void deserialize(Stream *stream) = 0;

    const std::string& getName() const { return m_name; }
    int16_t getId() const { return m_id; }

private:
    std::string m_name;
    int16_t m_id;
};

EMCA_NAMESPACE_END

#endif /* INCLUDE_EMCA_PLUGIN_H_ */
