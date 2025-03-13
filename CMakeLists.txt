cmake_minimum_required(VERSION 3.10)
cmake_policy(SET CMP0148 NEW)

project(gomoku_python_binding)

# Turn on position-independent code for all targets
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# Ensure a Release build is used if not already specified
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()

# Set Release compiler flags: high optimization, link-time optimization, and target-specific tuning.
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -flto -march=native")

# Enable Interprocedural Optimization (IPO) / Link Time Optimization (LTO)
set(CMAKE_INTERPROCEDURAL_OPTIMIZATION TRUE)

# Find pybind11
find_package(pybind11 REQUIRED)
include_directories(${PYTHON_INCLUDE_DIRS} ${pybind11_INCLUDE_DIRS})

# Get pybind11 include directory from Python (optional if already set by find_package)
execute_process(
    COMMAND python3 -c "import pybind11; print(pybind11.get_include())"
    OUTPUT_VARIABLE PYBIND11_INCLUDE_DIR
    OUTPUT_STRIP_TRAILING_WHITESPACE
)
include_directories(${PYBIND11_INCLUDE_DIR})

# Build the Gomoku static library
add_library(gomoku STATIC
    src/game/gomoku.cpp
    src/game/gomoku.hpp
    src/algo/algo.cpp
    src/algo/algo.hpp
)

target_include_directories(gomoku
    PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/src/game
    ${CMAKE_CURRENT_SOURCE_DIR}/src/algo
)

# Build the pybind11 module as a shared library
add_library(gomoku_pybind_module SHARED
    gomoku_pybind.cpp
)

target_include_directories(gomoku_pybind_module
    PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/src/game
    ${CMAKE_CURRENT_SOURCE_DIR}/src/algo
)

target_link_libraries(gomoku_pybind_module
    PRIVATE
    pybind11::module
    gomoku
)

# Set properties for the pybind11 module
set_target_properties(gomoku_pybind_module PROPERTIES
    PREFIX ""
    SUFFIX ".so"
    OUTPUT_NAME "cpp_gomoku"
)

# Optional: Additional optimizations (uncomment if needed)
# For loop unrolling, you can try adding:
set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -funroll-loops")
#
# For fast-math optimizations (if acceptable for your application):
set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -ffast-math")
#
# For Profile-Guided Optimization (PGO), a two-step process is needed:
#   1. Instrumentation: -fprofile-generate
#   2. Use the generated data: -fprofile-use
