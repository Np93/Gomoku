#ifndef GOMOKU_HPP
#define GOMOKU_HPP

#pragma once

#include <vector>
#include <utility>
#include <string>
#include <functional>

// Global debug flag declaration (defined in gomoku.cpp)
extern bool DEBUG;

// Helper function to call a lambda only if DEBUG is true
void debugCall(const std::function<void()>& func);

// Player token definitions
constexpr int EMPTY = 0;
constexpr int BLACK = -1;
constexpr int WHITE = 1;
/**
 * Gomoku class declaration.
 */
class Gomoku
{
public:
    Gomoku();
    Gomoku clone() const;

	void addTiles(const std::vector<std::pair<int,int>> &tiles, const int player);

    void drawBoard() const;

    std::vector<std::pair<int,int>> getAllPossibleMoves() const;
    std::vector<std::pair<int,int>> getAllCloseMoves() const;

    std::pair<bool, std::string> processMove(int placedRow, int placedCol);
    bool process5Pebbles(int placedRow, int placedCol);
    
	int getBoardSize() const;
    
	bool isDoubleThree(int row, int col);
	int getNumberOfThreats(int player);

	// GETTERS
	int getBoardValue(int row, int col) const;
	int getCurrentPlayer() const;
	int getWhitePlayerPebblesTaken() const;
	int getBlackPlayerPebblesTaken() const;
	bool getGameStatus() const;
	std::vector<std::pair<int,int>> getForcedMoves() const;

	// SETTERS
	void setCurrentPlayer(int player);
	void setBlackPlayerPebblesTaken(int pebbles);
	void setWhitePlayerPebblesTaken(int pebbles);

private:
    int boardSize;
    std::vector<std::vector<int>> board;
    int currentPlayer;
    int whitePlayerPebblesTaken;
    int blackPlayerPebblesTaken;
    std::vector<std::pair<int,int>> forcedMoves;
    bool gameOver;

    void changePlayer();
    void undoMove(int row, int col);
    bool isWithinBounds(int r, int c) const;

	bool checkPattern(int startRow, int startCol, int dr, int dc, const std::vector<int> &pattern);

    std::vector<std::pair<int,int>> getAllPebblesOfPlayer(int player) const;

    bool processForcedMove(int placedRow, int placedCol);
    bool processCapture(int placedRow, int placedCol);

    bool has10Pebbles() const;
    bool process10Pebbles();
    bool has5PebblesAligned(int placedRow, int placedCol) const;
    bool is5PebblesAlignedBreakable(int placedRow, int placedCol);
};

#endif // GOMOKU_HPP