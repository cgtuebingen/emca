cmake_minimum_required(VERSION 3.10.2)
project(emca
    DESCRIPTION "Explorer of Monte Carlo based Algorithms (Server)"
    LANGUAGES CXX)

# Set a default build configuration (Release)
if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
  message(STATUS "Setting build type to 'Release' as none was specified.")
  set(CMAKE_BUILD_TYPE Release CACHE STRING "Choose the type of build." FORCE)
  set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS "Debug" "Release"
    "MinSizeRel" "RelWithDebInfo")
endif()

include(GNUInstallDirs)

set(CMAKE_CXX_STANDARD 17)

option(EMCA_BUILD_SHARED "Build EMCA as a shared library?" ON)

# Set library type
if (EMCA_BUILD_SHARED)
  set(EMCA_LIBRARY_TYPE "SHARED")
else()
  set(EMCA_LIBRARY_TYPE "STATIC")
endif()

add_library(${PROJECT_NAME} ${EMCA_LIBRARY_TYPE}
    src/emcaserver.cpp
    src/dataapi.cpp
    src/pathdata.cpp
    src/heatmapdata.cpp)

# atomic library needed for 16 byte atomic read/write
target_link_libraries(${PROJECT_NAME} PUBLIC atomic)

target_include_directories(${PROJECT_NAME} PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
    PRIVATE src)

set_target_properties(${PROJECT_NAME} PROPERTIES
    VERSION "1.0.0"
    SOVERSION 1)

install(TARGETS ${PROJECT_NAME} EXPORT EMCAConfig
    ARCHIVE  DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY  DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME  DESTINATION ${CMAKE_INSTALL_BINDIR})

install(DIRECTORY include/${PROJECT_NAME} DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
install(EXPORT EMCAConfig DESTINATION share/EMCALib/cmake)

export(TARGETS ${PROJECT_NAME} FILE EMCAConfig.cmake)
