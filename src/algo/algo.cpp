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
#include <iomanip>      // Include for std::setprecision
#include <chrono>
#include <atomic>
#include <unordered_map> 

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

double GomokuAI::get_score_for_position(const std::string& gameType)
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

	int num_4_aligned_white = m_gomoku.getNumberOf4Aligned(WHITE);
	int num_4_aligned_black = m_gomoku.getNumberOf4Aligned(BLACK);

    double score = 0.0;
    score += (num_threat_white - num_threat_black) / 3.0 * 8.0;
    score += (num_4_aligned_white - num_4_aligned_black) / 4.0 * 15.0;

    if (gameType == "duo" || gameType == "normal") {
        // The Gomoku class tracks captures in: white_player_pebbles_taken, black_player_pebbles_taken
        // But these are private.  If needed, you can add getters in Gomoku:
        //    int getWhiteCaptures() const { return white_player_pebbles_taken; }
        //    int getBlackCaptures() const { return black_player_pebbles_taken; }
        // For now, let's assume we have those getters. If not, you can inline directly
        // as needed (this requires modifying Gomoku to make them public or friend).
        // We'll pretend we have:
        int white_captures = m_gomoku.getWhitePlayerPebblesTaken(); // you must implement
        int black_captures = m_gomoku.getBlackPlayerPebblesTaken(); // you must implement

        score += (white_captures - black_captures) * 10.0;
    }

    // double score = 0.0;
    // score += (num_threat_white - num_threat_black) / 3.0 * 8.0;
    // score += (white_captures - black_captures) * 10.0;
	// score += (num_4_aligned_white - num_4_aligned_black) / 4.0 * 15.0;

    return score;
}
ScoredMove GomokuAI::minmax(int depth, bool is_maximizing, bool is_first)
{
    static std::random_device rd;
    static std::mt19937 rng(rd());
    
    if (m_gomoku.isBoardEmpty()) {
        return {0.0, random_move()};
    }
    
    // Use forced moves if available; otherwise, get all close moves.
    auto forced_moves = m_gomoku.getForcedMoves();
    std::vector<std::pair<int, int>> possible_moves = 
        (!forced_moves.empty()) ? forced_moves : m_gomoku.getMovesAroundLastMoves();
    
    if (possible_moves.empty()) {
        std::cout << "No possible moves\n";
        return {0.0, {-1, -1}};
    }
    
    // Randomize move order
    std::shuffle(possible_moves.begin(), possible_moves.end(), rng);
    
    std::vector<std::pair<int, int>> best_moves;
    double best_score = is_maximizing ? minus_infinity() : plus_infinity();
    
    // Initialize alpha–beta values. Mimic alpha-beta pruning
	double alpha = -50;
	double beta  = 50;
    
    // Lambda to update the best move(s)
    auto update_best = [&](double score, const std::pair<int, int>& move) {
        if ((is_maximizing && score > best_score) || (!is_maximizing && score < best_score)) {
            best_score = score;
            best_moves.clear();
            best_moves.push_back(move);
        } else if (score == best_score) {
            best_moves.push_back(move);
        }
    };
    
    if (is_first) {
        // In the first layer we use parallel evaluation.
        // (Alpha-beta pruning is not applied here since each branch is in its own thread.)
        std::vector<std::future<ScoredMove>> futures;
        futures.reserve(possible_moves.size());
        
        for (const auto& mv : possible_moves) {
            futures.emplace_back(std::async(std::launch::async, [this, mv, depth, is_maximizing]() {
                return evaluate_move(mv.first, mv.second, depth, is_maximizing, m_gomoku.getGameType());
            }));
        }
        
        for (auto& fut : futures) {
            auto [score, move] = fut.get();
            update_best(score, move);
            // No safe way to prune here because the moves have already been launched
        }
    } else {
        // Sequential evaluation with alpha–beta pruning.
        for (const auto& mv : possible_moves) {
            auto [score, move] = evaluate_move(mv.first, mv.second, depth, is_maximizing, m_gomoku.getGameType());
            update_best(score, move);
            
            // Update alpha or beta based on the node type
            if (is_maximizing) {
                alpha = std::max(alpha, best_score);
                if (alpha >= beta) {
					std::cout << "Alpha cut-off at depth " << depth << "\n";
                    // Beta cut-off: no need to check remaining moves
                    break;
                }
            } else {
                beta = std::min(beta, best_score);
                if (beta <= alpha) {
					std::cout << "Beta cut-off at depth " << depth << "\n";
                    // Alpha cut-off: no need to check remaining moves
                    break;
                }
            }
        }
    }
    
    if (!best_moves.empty()) {
        std::uniform_int_distribution<> distr(0, best_moves.size() - 1);
        return {best_score, best_moves[distr(rng)]};
    }
    
    return {best_score, {-1, -1}};
}



ScoredMove GomokuAI::evaluate_move(int row, int col, int depth, bool is_maximizing, const std::string& gameType)
{
    Gomoku cloned_state = m_gomoku.clone();

    auto [valid_move, reason, move_score] = cloned_state.processMove(row, col);

    // Invalid move - immediately discard
    if (!valid_move) {
        double invalid_score = is_maximizing ? -1e6 - depth : 1e6 + depth;
        return {invalid_score, {row, col}};
    }

    // Terminal state detected
    if (cloned_state.getGameStatus()) {
        double terminal_score = is_maximizing ? 1e6 + depth : -1e6 - depth;
        return {terminal_score, {row, col}};
    }

    // Adjust the heuristic score based on the current player
    double adjusted_score = cloned_state.getScore();
    adjusted_score += (cloned_state.getCurrentPlayer() == BLACK ? 1 : -1) * (move_score + depth);
    cloned_state.setScore(adjusted_score);

    // Terminal depth - return heuristic score
    if (depth <= 1) {
        return {adjusted_score, {row, col}};
    }

    // Recursive min-max call
    GomokuAI temp_ai(cloned_state);
    auto [child_score, _] = temp_ai.minmax(depth - 1, !is_maximizing, false);
    return {child_score, {row, col}};
}