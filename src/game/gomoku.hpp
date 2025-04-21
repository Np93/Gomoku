#ifndef GOMOKU_HPP
#define GOMOKU_HPP

#pragma once

#include <vector>
#include <utility>
#include <string>
#include <functional>
#include <iostream>

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
    explicit Gomoku(int boardSize = 19, const std::string& gameType = "normal");
    Gomoku clone() const;

	void addTiles(const std::vector<std::pair<int,int>> &tiles, const int player);

    void drawBoard() const;

    std::vector<std::pair<int,int>> getAllPossibleMoves() const;
    std::vector<std::pair<int,int>> getAllCloseMoves() const;
	std::vector<std::pair<int,int>> getMovesAroundLastMoves() const;


    std::tuple<bool, std::string, int> processMove(int placedRow, int placedCol);
    bool process5Pebbles(int placedRow, int placedCol);
    
	int getBoardSize() const;
    
	bool isDoubleThree(int row, int col);
	int getNumberOfThreats(int player);
	int getNumberOfThreatsMove(int player, int placedRow, int placedCol);
	int getNumberOf4Aligned(int player) const;
	std::pair<int, int> getNumberOf4AlignedMove(int player, int placedRow, int placedCol) const;
    bool isBoardEmpty() const;

	// GETTERS
	int getBoardValue(int row, int col) const;
	int getCurrentPlayer() const;
	int getWhitePlayerPebblesTaken() const;
	int getBlackPlayerPebblesTaken() const;
	bool getGameStatus() const;
    std::string getGameType() const;
	std::vector<std::pair<int,int>> getForcedMoves() const;
	double getScore() const { return score; }

	// SETTERS
	void setCurrentPlayer(int player);
	void setBlackPlayerPebblesTaken(int pebbles);
	void setWhitePlayerPebblesTaken(int pebbles);
	void setScore(double score) { this->score = score; }

	std::string computeStateHash() const;
	struct LastMoves
	{
		std::pair<int, int> firstMove;
		std::pair<int, int> secondMove;
		std::pair<int, int> thirdMove;
	};

private:
    int boardSize;
    std::string gameType;
    std::vector<std::vector<int>> board;
    int currentPlayer;
    int whitePlayerPebblesTaken;
    int blackPlayerPebblesTaken;
	int backPlayeraligned4Stone = 0;
	int whitePlayeraligned4Stone = 0;
    std::vector<std::pair<int,int>> forcedMoves;
    bool gameOver;

	LastMoves lastMoves;
	double score;

    void changePlayer();
    void undoMove(int row, int col);
    bool isWithinBounds(int r, int c) const;

	bool checkPattern(int startRow, int startCol, int dr, int dc, const std::vector<int> &pattern);

    std::vector<std::pair<int,int>> getAllPebblesOfPlayer(int player) const;

    bool processForcedMove(int placedRow, int placedCol);
    int processCapture(int placedRow, int placedCol);

    bool has10Pebbles() const;
    bool process10Pebbles();
    bool has5PebblesAligned(int placedRow, int placedCol) const;
    bool hasMoreThan5PebblesAligned(int placedRow, int placedCol) const;
    bool is5PebblesAlignedBreakable(int placedRow, int placedCol);
    std::vector<std::pair<int, int>> getCapturePoints(int player); // debug
	void updateLastMoves(int row, int col)
	{
		lastMoves.thirdMove = lastMoves.secondMove;
		lastMoves.secondMove = lastMoves.firstMove;
		lastMoves.firstMove = {row, col};
	}
};

#endif // GOMOKU_HPP