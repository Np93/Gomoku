#include "gomoku.hpp"
#include "algo.hpp"

#include <pybind11/pybind11.h>
#include <pybind11/stl.h> // for std::vector, std::pair, etc.

namespace py = pybind11;

PYBIND11_MODULE(cpp_gomoku, m) {
	m.doc() = "Pybind11 bindings for Gomoku C++ class";

	py::class_<Gomoku>(m, "Gomoku")
		.def(py::init<int, std::string>(), py::arg("boardSize") = 19, py::arg("gameType") = "normal")
		.def("clone", &Gomoku::clone)
		.def("addTiles",&Gomoku::addTiles, py::arg("tiles"), py::arg("player"))
		.def("processMove", &Gomoku::processMove)
		.def("process5Pebbles", &Gomoku::process5Pebbles, py::arg("row"), py::arg("col"))
		.def("isDoubleThree", &Gomoku::isDoubleThree, py::arg("row"), py::arg("col"))
		.def("getNumberOfThreats", &Gomoku::getNumberOfThreats, py::arg("player"))
		.def("getBoardSize", &Gomoku::getBoardSize)
		.def("getGameType", &Gomoku::getGameType)
		.def("getBoardValue", &Gomoku::getBoardValue)
		.def("getCurrentPlayer", &Gomoku::getCurrentPlayer)
		.def("getWhitePlayerPebblesTaken", &Gomoku::getWhitePlayerPebblesTaken)
		.def("getBlackPlayerPebblesTaken", &Gomoku::getBlackPlayerPebblesTaken)
		.def("getGameStatus", &Gomoku::getGameStatus)
		.def("getAllPossibleMoves", &Gomoku::getAllPossibleMoves)
		.def("getAllCloseMoves", &Gomoku::getAllCloseMoves)
		.def("setCurrentPlayer", &Gomoku::setCurrentPlayer, py::arg("player"))
		.def("setBlackPlayerPebblesTaken", &Gomoku::setBlackPlayerPebblesTaken, py::arg("pebbles"))
		.def("setWhitePlayerPebblesTaken", &Gomoku::setWhitePlayerPebblesTaken, py::arg("pebbles"));
	py::class_<GomokuAI>(m, "GomokuAI")
		.def(py::init<const Gomoku&>(), py::arg("gomoku"))
		.def("minmax", &GomokuAI::minmax, py::arg("depth"), py::arg("is_maximizing"), py::arg("is_first") = true);
}