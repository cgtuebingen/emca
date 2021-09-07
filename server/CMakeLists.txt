cmake_minimum_required(VERSION 3.10.2)
project(emca
    VERSION 1.0.0
    DESCRIPTION "Explorer of Monte Carlo based Algorithms (Server)"
    LANGUAGES CXX)

include(GNUInstallDirs)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -latomic")

set(SOURCE_FILES
    src/emcaserver.cpp
    src/dataapi.cpp
    src/pathdata.cpp
    src/heatmapdata.cpp)

add_library(${PROJECT_NAME} SHARED ${SOURCE_FILES})
set_property(TARGET ${PROJECT_NAME} PROPERTY POSITION_INDEPENDENT_CODE ON)

set_target_properties(emca PROPERTIES VERSION ${PROJECT_VERSION})

target_include_directories(${PROJECT_NAME} PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
    PRIVATE src)

set_target_properties(${PROJECT_NAME} PROPERTIES
    VERSION ${PROJECT_VERSION}
    SOVERSION 1)

install(TARGETS ${PROJECT_NAME} EXPORT EMCAConfig
    ARCHIVE  DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY  DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME  DESTINATION ${CMAKE_INSTALL_BINDIR})

install(DIRECTORY include/ DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/${PROJECT_NAME})
install(EXPORT EMCAConfig DESTINATION share/EMCALib/cmake)

export(TARGETS ${PROJECT_NAME} FILE EMCAConfig.cmake)
