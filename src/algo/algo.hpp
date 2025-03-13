#ifndef GOMOKU_AI_HPP
#define GOMOKU_AI_HPP

#include <limits>
#include <random>
#include <vector>
#include <utility>
#include "gomoku.hpp" // Include your existing Gomoku header or the header where Gomoku is declared
#include <chrono>
#include <atomic>

// Simple helper to represent a move-evaluation result
//   first  = numeric score
//   second = (row, col) chosen
typedef std::pair<double, std::pair<int,int>> ScoredMove;

/**
 * GomokuAI class:
 * - Holds a copy of the Gomoku game state.
 * - Provides methods for:
 *     - random_move
 *     - minimax search
 *     - heuristic scoring
 */
class GomokuAI {
public:
    // Constructor
    GomokuAI(const Gomoku& gomoku);

    // Re-initialize the AI with a new Gomoku instance and reset depth
    void reset(const Gomoku& newGomoku);

    // Generate a random valid move among all possible moves (or close moves) for the current player.
    // Returns (-1,-1) if no moves exist.
    std::pair<int,int> random_move();

    // Evaluate the board for the perspective of the current player (WHITE=+1, BLACK=-1).
    double get_score_for_position(const std::string& gameType);

    // Minimax entry point
    // Returns (best_score, best_move)
    ScoredMove minmax(int depth, bool is_maximizing, bool is_first=true);

private:
    // Store a copy of the Gomoku board
    Gomoku m_gomoku;
    // Depth for minimax
    int m_depth;
	std::atomic<bool> time_up = false;

    // Evaluate a single move (similar to the python `evaluate_move` function).
    // Returns (score, (row,col)).
    ScoredMove evaluate_move(int row, int col, int depth, bool is_maximizing, const std::string& gameType);

    // Helper used in get_score_for_position() to mimic the python logic
    // This is a placeholder. You should fill it with logic that counts "threats" for the given player.
    int _get_number_of_threats(int player);

    // A helper to get +∞ or -∞
    inline double plus_infinity()  { return std::numeric_limits<double>::infinity(); }
    inline double minus_infinity() { return -std::numeric_limits<double>::infinity(); }
};

#endif // GOMOKU_AI_HPP
