#include "algo.hpp"
#include "gomoku.hpp" // Include your existing Gomoku header or the header where Gomoku is declared

#include <iostream>
#include <algorithm>    // std::max, std::min
#include <limits>       // std::numeric_limits
#include <cstdlib>      // std::rand, std::srand
#include <ctime>        // std::time
#include <vector>
#include <utility>
#include <iostream>
#include <thread>
#include <future>
#include <random>
#include <shared_mutex> // Include for shared_mutex

std::unordered_map<std::string, double> transposition_table;
std::shared_mutex transposition_mutex; // Use shared mutex

GomokuAI::GomokuAI(const Gomoku& gomoku)
    : m_gomoku(gomoku.clone())
{
    // Seed random generator (if you haven't done so elsewhere)
    std::srand(static_cast<unsigned>(std::time(nullptr)));
}

std::pair<int,int> GomokuAI::random_move()
{
    // In your Python code, random_move picks from either get_all_possible_moves(player)
    // But in your C++ code, Gomoku's get_all_possible_moves() always returns empties
    // for the *current* player. We'll just call get_all_possible_moves().
    auto moves = m_gomoku.getAllPossibleMoves();
    if (moves.empty()) {
        return std::make_pair(-1, -1);
    }
    // Pick a random index
    int idx = std::rand() % moves.size();
    return moves[idx];
}

double GomokuAI::get_score_for_position()
{
    // "score = (number_of_threat_white - number_of_threat_black)/3 * 10"
    // plus difference in pebbles_taken * 10
    // In Python, you used: 
    //   WHITE is the AI (positive)
    //   BLACK is the opponent (negative)
    //
    // Let's replicate that logic. We'll define:
    int num_threat_white = m_gomoku.getNumberOfThreats(WHITE);
    int num_threat_black = m_gomoku.getNumberOfThreats(BLACK);

    // The Gomoku class tracks captures in: white_player_pebbles_taken, black_player_pebbles_taken
    // But these are private.  If needed, you can add getters in Gomoku:
    //    int getWhiteCaptures() const { return white_player_pebbles_taken; }
    //    int getBlackCaptures() const { return black_player_pebbles_taken; }
    // For now, let's assume we have those getters. If not, you can inline directly
    // as needed (this requires modifying Gomoku to make them public or friend).
    // We'll pretend we have:
    int white_captures = m_gomoku.getWhitePlayerPebblesTaken(); // you must implement
    int black_captures = m_gomoku.getBlackPlayerPebblesTaken(); // you must implement

    double score = 0.0;
    score += (num_threat_white - num_threat_black) / 3.0 * 10.0;
    score += (white_captures - black_captures) * 10.0;

    return score;
}

ScoredMove GomokuAI::minmax(int depth, bool is_maximizing, bool is_first)
{
    if (m_gomoku.isBoardEmpty()) {
        auto move = random_move();
        return std::make_pair(0.0, move);
    }

    std::vector<std::pair<int, int>> possible_moves;

    if (!m_gomoku.getForcedMoves().empty()) {
        possible_moves = m_gomoku.getForcedMoves();
    } else {
        possible_moves = m_gomoku.getAllCloseMoves();
    }

    if (possible_moves.empty()) {
        std::cout << "No possible moves\n";
        return std::make_pair(0.0, std::make_pair(-1, -1));
    }

    double best_score = is_maximizing ? minus_infinity() : plus_infinity();
    std::vector<std::pair<int, int>> best_moves;

    // If first pass, use multi-threading
    if (is_first) {
        std::vector<std::future<std::pair<double, std::pair<int, int>>>> futures;

        for (auto& mv : possible_moves) {
            futures.emplace_back(std::async(std::launch::async, [this, mv, depth, is_maximizing]() {
                return evaluate_move(mv.first, mv.second, depth, is_maximizing);
            }));
        }

        for (auto& fut : futures) {
            auto [score, move] = fut.get();

            if (is_maximizing) {
                if (score > best_score) {
                    best_score = score;
                    best_moves.clear();
                    best_moves.push_back(move);
                } else if (score == best_score) {
                    best_moves.push_back(move);
                }
            } else {
                if (score < best_score) {
                    best_score = score;
                    best_moves.clear();
                    best_moves.push_back(move);
                } else if (score == best_score) {
                    best_moves.push_back(move);
                }
            }
        }
    } else { // Normal sequential evaluation
        for (auto& mv : possible_moves) {
            auto [score, move] = evaluate_move(mv.first, mv.second, depth, is_maximizing);

            if (is_maximizing) {
                if (score > best_score) {
                    best_score = score;
                    best_moves.clear();
                    best_moves.push_back(move);
                } else if (score == best_score) {
                    best_moves.push_back(move);
                }
            } else {
                if (score < best_score) {
                    best_score = score;
                    best_moves.clear();
                    best_moves.push_back(move);
                } else if (score == best_score) {
                    best_moves.push_back(move);
                }
            }
        }
    }

    if (!best_moves.empty()) {
        static std::random_device rd;
        static std::mt19937 gen(rd());
        std::uniform_int_distribution<> distr(0, best_moves.size() - 1);
        return std::make_pair(best_score, best_moves[distr(gen)]);
    } else {
		// // Clean the transposition table
		// {
		// 	std::unique_lock<std::shared_mutex> lock(transposition_mutex);
		// 	transposition_table.clear();
		// }
        return std::make_pair(best_score, std::make_pair(-1, -1));
    }


    // Pick randomly among the best moves
    if (!best_moves.empty()) {
        int idx = std::rand() % best_moves.size();
        return std::make_pair(best_score, best_moves[idx]);
    } else {
        // Fallback if somehow no best_moves
        return std::make_pair(best_score, std::make_pair(-1, -1));
    }
}

ScoredMove GomokuAI::evaluate_move(int row, int col, int depth, bool is_maximizing)
{
    // We'll create a temporary clone of the Gomoku state to simulate
    Gomoku cloned_state = m_gomoku.clone();
    // Attempt to place the move
    auto [valid_move, reason] = cloned_state.processMove(row, col);

    // If it's invalid, return +∞ or -∞ so the minmax can discard it
	if (!valid_move) {
		double bad_score = (is_maximizing ? -1000000.0 - depth: 1000000.0 + depth);
		return std::make_pair(bad_score, std::make_pair(row, col));
	}

	if (cloned_state.getGameStatus()) {
		double terminal_score = (is_maximizing ? 1000000.0 + depth : -1000000.0 - depth);
		return std::make_pair(terminal_score, std::make_pair(row, col));
	}

    // Not at terminal => either compute heuristic (if depth == 1) or do recursive minmax
    if (depth <= 1) {
        // Evaluate the position heuristically
		std::string key = cloned_state.computeStateHash();

		//  Check if the state is in the transposition table
		{
			std::shared_lock<std::shared_mutex> lock(transposition_mutex);
			auto it = transposition_table.find
				(key);
			if (it != transposition_table.end()) {
				return std::make_pair(it->second, std::make_pair(row, col));
			}
		}

        double score = get_score_for_position();

		// Add the state to the transposition table
		{
			std::unique_lock<std::shared_mutex> lock(transposition_mutex);
			transposition_table[key] = score;
		}

        return std::make_pair(score, std::make_pair(row, col));
    } else {
        // Recurse
        GomokuAI temp_ai(cloned_state);
        auto [child_score, child_move] = temp_ai.minmax(depth - 1, !is_maximizing, false);
        return std::make_pair(child_score, std::make_pair(row, col));
    }
}
