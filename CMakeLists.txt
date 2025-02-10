cmake_minimum_required(VERSION 3.10)
project(gomoku_python_binding)

# Turn on position-independent code for all targets
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

find_package(pybind11 REQUIRED)
include_directories(${PYTHON_INCLUDE_DIRS} ${pybind11_INCLUDE_DIRS})

execute_process(
    COMMAND python3 -c "import pybind11; print(pybind11.get_include())"
    OUTPUT_VARIABLE PYBIND11_INCLUDE_DIR
    OUTPUT_STRIP_TRAILING_WHITESPACE
)
include_directories(${PYBIND11_INCLUDE_DIR})

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

set_target_properties(gomoku_pybind_module PROPERTIES
    PREFIX ""
    SUFFIX ".so"
    OUTPUT_NAME "cpp_gomoku"
)
