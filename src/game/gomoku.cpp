#include "gomoku.hpp"

#include <iostream>
#include <algorithm>
#include <cstring>
#include <set>

// Definition of the global debug flag
bool DEBUG = false;

void debugCall(const std::function<void()>& func)
{
    if (DEBUG) {
        func();
    }
}

Gomoku::Gomoku(int boardSize, const std::string& gameType)
    : boardSize(boardSize), gameType(gameType) {
    board.resize(boardSize, std::vector<int>(boardSize, EMPTY));
    currentPlayer = BLACK;
    whitePlayerPebblesTaken = 0;
    blackPlayerPebblesTaken = 0;
    gameOver = false;
}

Gomoku Gomoku::clone() const
{
    Gomoku newCopy;
    newCopy.boardSize = boardSize;
    newCopy.gameType = gameType;
    newCopy.board = board;
    newCopy.currentPlayer = currentPlayer;
    newCopy.whitePlayerPebblesTaken = whitePlayerPebblesTaken;
    newCopy.blackPlayerPebblesTaken = blackPlayerPebblesTaken;
    newCopy.forcedMoves = forcedMoves;  // copy
    newCopy.gameOver = gameOver;
	newCopy.score = score;
	newCopy.lastMoves = lastMoves; // copy last moves
    return newCopy;
}

void Gomoku::addTiles(const std::vector<std::pair<int,int>> &tiles, const int player)
{
	for (auto &tile : tiles)
	{
		int r = tile.first;
		int c = tile.second;
		if (isWithinBounds(r, c)) {
			board[r][c] = player;
		}
	}
}

void Gomoku::drawBoard() const
{
    // Print column indices (header)
    std::cout << "   ";
    for (int i = 0; i < boardSize; i++)
        std::cout << i << ((i < 10) ? "  " : " ");

    std::cout << std::endl;

    // Print each row
    for (int i = 0; i < boardSize; i++)
    {
        // Row index
        std::cout << i << ((i < 10) ? "  " : " ");
        for (int j = 0; j < boardSize; j++)
        {
            if (board[i][j] == BLACK) {
                std::cout << "B  ";
            }
            else if (board[i][j] == WHITE) {
                std::cout << "W  ";
            }
            else {
                std::cout << ".  ";
            }
        }
        std::cout << std::endl;
    }
}

std::vector<std::pair<int,int>> Gomoku::getAllPossibleMoves() const
{
    std::vector<std::pair<int,int>> possibleMoves;
    for (int r = 0; r < boardSize; r++)
    {
        for (int c = 0; c < boardSize; c++)
        {
            if (board[r][c] == EMPTY) {
                possibleMoves.push_back(std::make_pair(r, c));
            }
        }
    }
    return possibleMoves;
}

std::vector<std::pair<int,int>> Gomoku::getMovesAroundLastMoves() const
{
	std::vector<std::pair<int, int>> possibleMoves;
	std::set<std::pair<int, int>> uniqueMoves;

	if (!lastMoves.firstMove.first && !lastMoves.firstMove.second)
	{
		std::cout << "No last moves available, returning all close moves." << std::endl;
		return getAllCloseMoves();
	}

	std::vector<std::pair<int, int>> directions = {
		{0, 1}, {1, 0}, {1, 1}, {1, -1}, {0, -1}, {-1, 0}, {-1, -1}, {-1, 1}
	};

	// Loop over the last three moves
	for (const auto& move : {lastMoves.firstMove, lastMoves.secondMove, lastMoves.thirdMove}) {
		if (move.first == -1 && move.second == -1) continue;

		// Expand window around the move (±5 range)
		for (int dr = -5; dr <= 5; ++dr) {
			for (int dc = -5; dc <= 5; ++dc) {
				int r = move.first + dr;
				int c = move.second + dc;

				if (!isWithinBounds(r, c)) continue;
				if (board[r][c] != EMPTY) continue;

				// Check for at least one non-empty neighbor
				bool hasNeighbor = false;
				for (const auto& dir : directions) {
					int adjRF = r + dir.first;
					int adjCF = c + dir.second;
					int adjRB = r - dir.first;
					int adjCB = c - dir.second;

					if ((isWithinBounds(adjRF, adjCF) && board[adjRF][adjCF] != EMPTY) ||
						(isWithinBounds(adjRB, adjCB) && board[adjRB][adjCB] != EMPTY)) {
						hasNeighbor = true;
						break;
					}
				}

				if (hasNeighbor) {
					uniqueMoves.emplace(r, c);
				}
			}
		}
	}

	possibleMoves.assign(uniqueMoves.begin(), uniqueMoves.end());
	return possibleMoves;
}

std::vector<std::pair<int,int>> Gomoku::getAllCloseMoves() const
{
    std::vector<std::pair<int,int>> possibleMoves;
    // Directions: horizontal, vertical, diagonals
    std::vector<std::pair<int,int>> directions = {
        {0,1}, {1,0}, {1,1}, {1,-1}
    };

    for (int r = 0; r < boardSize; r++)
    {
        for (int c = 0; c < boardSize; c++)
        {
            if (board[r][c] == EMPTY)
            {
                bool hasNeighbor = false;
                for (auto &dir : directions)
                {
                    int dr = dir.first;
                    int dc = dir.second;

                    // Forward neighbor
                    int adjRF = r + dr;
                    int adjCF = c + dc;
                    if (isWithinBounds(adjRF, adjCF)) {
                        if (board[adjRF][adjCF] != EMPTY) {
                            hasNeighbor = true;
                            break;
                        }
                    }

                    // Backward neighbor
                    int adjRB = r - dr;
                    int adjCB = c - dc;
                    if (isWithinBounds(adjRB, adjCB)) {
                        if (board[adjRB][adjCB] != EMPTY) {
                            hasNeighbor = true;
                            break;
                        }
                    }
                }
                if (hasNeighbor) {
                    possibleMoves.push_back(std::make_pair(r, c));
                }
            }
        }
    }
    return possibleMoves;
}

std::tuple<bool, std::string, int> Gomoku::processMove(int placedRow, int placedCol)
{
    // Early exit if the game is already over.
    if (gameOver)
        return std::make_tuple(false, "game_over", 0);

    // Enforce forced moves: if forcedMoves is nonempty and the chosen move is not forced, reject it.
    if (processForcedMove(placedRow, placedCol))
        return std::make_tuple(false, "forced_move", 0);

    // Commit the move on the board.
    board[placedRow][placedCol] = currentPlayer;

    int capturedCount = 0; // Declare capturedCount at the beginning of the function

    if (gameType == "duo" || gameType == "normal") {
        
        debugCall([&](){
            auto possibleCaptures = getCapturePoints(currentPlayer);
            for (auto& pos : possibleCaptures) {
                std::cout << "Capture possible by playing on : (" << pos.first << ", " << pos.second << ")\n";
            }
        });

        // Process captures
        capturedCount = processCapture(placedRow, placedCol);
    
        // Check double-three: if it is a double-three, revert and return false
		if (capturedCount == 0 && isDoubleThree(placedRow, placedCol))
		{
            debugCall([&](){
                std::cout << "Mouvement interdit (" 
                        << placedRow << ", " << placedCol 
                        << ") : Double-three detecte" << std::endl;
            });
            undoMove(placedRow, placedCol);
            return std::make_tuple(false, "double_three", 0);
        }

        // Check if current player has captured 10 pebbles -> immediate win
        if (process10Pebbles()) {
            return std::make_tuple(true, "win_score", 1000);
        }
    }
    
    if (gameType == "special") {
		// capturedCount = processCapture(placedRow, placedCol);
        capturedCount = 0;

        if (isDoubleThree(placedRow, placedCol)) {
            debugCall([&](){
                std::cout << "Mouvement interdit (" 
                        << placedRow << ", " << placedCol 
                        << ") : Double-three détecté" << std::endl;
            });
            undoMove(placedRow, placedCol);
            return std::make_tuple(false, "double_three", 0);
        }

        if (hasMoreThan5PebblesAligned(placedRow, placedCol)) {
			debugCall([&](){
				std::cout << "Mouvement interdit (" 
				<< placedRow << ", " << placedCol 
				<< ") : line over 5 détecté" << std::endl;
            });
            undoMove(placedRow, placedCol);
            return std::make_tuple(false, "line_over_5", 0);
        }
    }

    int captureScore  = capturedCount * 10;
	
    // Evaluate additional tactical factors.
	int playerPebblesTaken = (currentPlayer == BLACK) ? blackPlayerPebblesTaken : whitePlayerPebblesTaken;
    int threatScore   = getNumberOfThreatsMove(currentPlayer, placedRow, placedCol) * 5;
	auto [open4, blocked4] = getNumberOf4AlignedMove(currentPlayer, placedRow, placedCol);

	int aligned4Score = (open4 * 40) + (blocked4 * 10);
	int moveScore     = captureScore + threatScore + aligned4Score;
	if (playerPebblesTaken >= 8) {
		moveScore += 10;
	}

	// NOTE those line are mainly for the correction of the subject
	if (currentPlayer == BLACK) {
		backPlayeraligned4Stone += open4;
	} else {
		whitePlayeraligned4Stone += open4;
	}
	
	if (whitePlayeraligned4Stone > 10 && whitePlayerPebblesTaken <= 4)
	{
		std::cout << "White player has more than 10 aligned 4 stones and less than 4 pebbles taken" << std::endl;
		moveScore += aligned4Score * 0.25;
	}

    if (gameType != "special") {
	    // Check win conditions.
        if (process10Pebbles())
		{
			updateLastMoves(placedRow, placedCol);
            return std::make_tuple(true, "win_score", 1000);
		}
    }

    if (process5Pebbles(placedRow, placedCol))
	{
		updateLastMoves(placedRow, placedCol);
        return std::make_tuple(true, "win_alignments", 1000);
	}

    // Change turn only if the game is not over.
    changePlayer();
	updateLastMoves(placedRow, placedCol);
    return std::make_tuple(true, "valid_move", moveScore);
}

// GETTERS
int Gomoku::getBoardSize() const
{
    return boardSize;
}

std::string Gomoku::getGameType() const
{
    return gameType;
}

int Gomoku::getBoardValue(int row, int col) const
{
	if (isWithinBounds(row, col)) {
		return board[row][col];
	} else {
		throw std::out_of_range("Board position out of bounds");
	}
}

int Gomoku::getCurrentPlayer() const
{
	return currentPlayer;
}

int Gomoku::getWhitePlayerPebblesTaken() const
{
	return whitePlayerPebblesTaken;
}

int Gomoku::getBlackPlayerPebblesTaken() const
{
	return blackPlayerPebblesTaken;
}

bool Gomoku::getGameStatus() const
{
	return gameOver;
}

std::vector<std::pair<int,int>> Gomoku::getForcedMoves() const
{
	return forcedMoves;
}

//  SETTERS 
void Gomoku::setCurrentPlayer(int player)
{
	currentPlayer = player;
}

void Gomoku::setBlackPlayerPebblesTaken(int pebbles)
{
	blackPlayerPebblesTaken = pebbles;
}

void Gomoku::setWhitePlayerPebblesTaken(int pebbles)
{
	whitePlayerPebblesTaken = pebbles;
}

// PRIVATE METHODS

std::string Gomoku::computeStateHash() const
{
	std::string hash;
	hash.reserve(boardSize * boardSize + 2 * sizeof(int)); // Reserve space for efficiency

	for (const auto& row : board)
	{
		for (int cell : row)
		{
			hash += std::to_string(cell);
		}
	}

	hash += std::to_string(whitePlayerPebblesTaken);
	hash += std::to_string(blackPlayerPebblesTaken);

	return hash;
}

void Gomoku::changePlayer()
{
    currentPlayer = -currentPlayer; // black = 1, white = -1
}

void Gomoku::undoMove(int row, int col)
{
    board[row][col] = EMPTY;
}

bool Gomoku::isWithinBounds(int r, int c) const
{
    return (r >= 0 && r < boardSize && c >= 0 && c < boardSize);
}

/**
 * Return a vector of all positions of a given player's stones.
 */
std::vector<std::pair<int,int>> Gomoku::getAllPebblesOfPlayer(int player) const
{
    std::vector<std::pair<int,int>> pebbles;
    for (int r = 0; r < boardSize; r++)
    {
        for (int c = 0; c < boardSize; c++)
        {
            if (board[r][c] == player) {
                pebbles.push_back(std::make_pair(r, c));
            }
        }
    }
    return pebbles;
}

/**
 * Check if the current player must place a forced move,
 * and if the chosen move is not in forcedMoves, reject it.
 */
bool Gomoku::processForcedMove(int placedRow, int placedCol)
{
    if (!forcedMoves.empty())
    {
        // If the chosen move is not in forcedMoves, it's invalid
        auto it = std::find(forcedMoves.begin(), forcedMoves.end(),
                            std::make_pair(placedRow, placedCol));
        if (it == forcedMoves.end())
        {
            std::cout << "Invalid move (" << placedRow << ", "
                      << placedCol << "): Forced move required\n";
            std::cout << "Forced moves: ";
            for (auto &fm : forcedMoves) {
                std::cout << "(" << fm.first << "," << fm.second << ") ";
            }
            std::cout << std::endl;
            return true;
        }
    }
    // If we pass the check, reset forcedMoves
    forcedMoves.clear();
    return false;
}

/**
* Check if placing a stone at (placedRow, placedCol) captures opponent stones.
* A capture pattern is: CurrentPlayer - Opponent(s) - CurrentPlayer
* where the Opponent(s) can be 2 or 3 in a row.
*/
int Gomoku::processCapture(int placedRow, int placedCol)
{
	// Fixed directions: horizontal, vertical, and the two diagonals.
	static const std::vector<std::pair<int,int>> directions = {
		{0,1}, {1,0}, {1,1}, {1,-1}
	};

	int totalCaptured = 0;
	int opponentToken = -currentPlayer;

	// Loop over each direction.
	for (const auto &dir : directions)
	{
		int dRow = dir.first;
		int dCol = dir.second;
		
		// Check both forward (sign = 1) and backward (sign = -1) directions.
		for (int sign : {1, -1})
		{
			// Compute positions for the two opponent stones and the cell after them.
			int r1 = placedRow + sign * dRow;
			int c1 = placedCol + sign * dCol;
			int r2 = placedRow + sign * dRow * 2;
			int c2 = placedCol + sign * dCol * 2;
			int r3 = placedRow + sign * dRow * 3;
			int c3 = placedCol + sign * dCol * 3;

			// Check that positions are within bounds and match the capture pattern:
			// Two opponent stones followed by a stone of the current player.
			if (isWithinBounds(r2, c2) && isWithinBounds(r3, c3) &&
				board[r1][c1] == opponentToken && board[r2][c2] == opponentToken &&
				board[r3][c3] == currentPlayer)
			{
				// Remove the two captured opponent stones.
				board[r1][c1] = EMPTY;
				board[r2][c2] = EMPTY;
				totalCaptured += 2;
				if (currentPlayer == BLACK)
					blackPlayerPebblesTaken += 2;
				else
					whitePlayerPebblesTaken += 2;
			}
		}
	}
	return totalCaptured;
}
 

/**
 * Check if the move at (row, col) creates a double-three configuration.
 */
bool Gomoku::isDoubleThree(int row, int col)
{
    int threats = 0;
    // Directions: horizontal, vertical, diagonals
    std::vector<std::pair<int,int>> directions = {
        {0,1}, {1,0}, {1,1}, {1,-1}
    };

    for (auto &dir : directions)
    {
        // Gather up to 4 stones in each direction from (row, col).
        std::vector<int> colorSequence;
        colorSequence.push_back(board[row][col]);

        int dr = dir.first;
        int dc = dir.second;

        // forward direction
        for (int i = 1; i <= 4; i++)
        {
            int r = row + i * dr;
            int c = col + i * dc;
            if (isWithinBounds(r, c)) {
                colorSequence.push_back(board[r][c]);
            } else {
                break;
            }
        }

        // backward direction: insert at the front
        int iPos = 0;
        for (int i = 1; i <= 4; i++)
        {
            int r = row - i * dr;
            int c = col - i * dc;
            if (isWithinBounds(r, c)) {
                iPos++;
                colorSequence.insert(colorSequence.begin(), board[r][c]);
            } else {
                break;
            }
        }

		// If this direction creates a "three threat", increment threats
		if (checkPattern(row, col, dr, dc, {0, currentPlayer, currentPlayer, currentPlayer, 0}) ||
			checkPattern(row, col, dr, dc, {0, currentPlayer, currentPlayer, 0, currentPlayer, 0}) ||
			checkPattern(row, col, dr, dc, {0, currentPlayer, 0, currentPlayer, currentPlayer, 0})) {
			threats++;
		}

		if (threats >= 2) {
            return true; // double-three
        }
    }

    return false;
}

// Modified to check only the current move's surroundings
int Gomoku::getNumberOfThreatsMove(int player, int placedRow, int placedCol)
{
    int threats = 0;

    static const std::vector<std::vector<int>> patterns = {
        {0, player, player, player, 0},
        {0, player, player, 0, player, 0},
        {0, player, 0, player, player, 0}
    };

    static const std::vector<std::vector<int>> reversedPatterns = []() {
        std::vector<std::vector<int>> revPatterns;
        for (const auto &pattern : patterns) {
            std::vector<int> revPattern(pattern.rbegin(), pattern.rend());
            revPatterns.push_back(revPattern);
        }
        return revPatterns;
    }();

    static const std::vector<std::pair<int, int>> directions = {
        {0, 1}, {1, 0}, {1, 1}, {1, -1}
    };

    for (const auto &[dr, dc] : directions)
    {
        for (size_t i = 0; i < patterns.size(); i++)
        {
            // Check both the pattern and its reverse from the placed stone position.
            if (checkPattern(placedRow, placedCol, dr, dc, patterns[i]) ||
                checkPattern(placedRow, placedCol, dr, dc, reversedPatterns[i]))
            {
                threats++;
                break; // Count only one threat per direction
            }
        }
    }
    return threats;
}

// Modified to check only the current move's surroundings
std::pair<int, int> Gomoku::getNumberOf4AlignedMove(int player, int placedRow, int placedCol) const
{
	int countOpen = 0;
	int countBlocked = 0;
	std::vector<std::pair<int,int>> directions = {
		{0,1}, {1,0}, {1,1}, {1,-1}
	};

	for (auto &dir : directions)
	{
		int dr = dir.first;
		int dc = dir.second;
		int countPlayer = 1; // include the current stone

		// Check forward direction
		int rr = placedRow + dr;
		int cc = placedCol + dc;
		while (isWithinBounds(rr, cc) && board[rr][cc] == player)
		{
			countPlayer++;
			rr += dr;
			cc += dc;
		}

		// Check if the forward end is open or blocked
		bool forwardOpen = isWithinBounds(rr, cc) && board[rr][cc] == EMPTY;

		// Check backward direction
		rr = placedRow - dr;
		cc = placedCol - dc;
		while (isWithinBounds(rr, cc) && board[rr][cc] == player)
		{
			countPlayer++;
			rr -= dr;
			cc -= dc;
		}

		// Check if the backward end is open or blocked
		bool backwardOpen = isWithinBounds(rr, cc) && board[rr][cc] == EMPTY;

		// Count only exactly 4 aligned stones
		if (countPlayer == 4)
		{
			if (forwardOpen && backwardOpen)
				countOpen++;
			else if (forwardOpen || backwardOpen)
				countBlocked++;
		}
	}
	return {countOpen, countBlocked};
}

int Gomoku::getNumberOfThreats(int player)
{
    std::vector<std::pair<int, int>> pebbles = getAllPebblesOfPlayer(player);
    int threats = 0;

    static const std::vector<std::vector<int>> patterns = {
        {0, player, player, player, 0},
        {0, player, player, 0, player, 0},
        {0, player, 0, player, player, 0}
    };

    static const std::vector<std::vector<int>> reversedPatterns = []() {
        std::vector<std::vector<int>> revPatterns;
        for (const auto &pattern : patterns) {
            std::vector<int> revPattern(pattern.rbegin(), pattern.rend());
            revPatterns.push_back(revPattern);
        }
        return revPatterns;
    }();

    static const std::vector<std::pair<int, int>> directions = {
        {0, 1}, {1, 0}, {1, 1}, {1, -1}
    };

    for (auto &[row, col] : pebbles)
    {
        for (auto &[dr, dc] : directions)
        {
            for (const auto &pattern : patterns)
            {
                if (checkPattern(row, col, dr, dc, pattern) || checkPattern(row, col, dr, dc, reversedPatterns[&pattern - &patterns[0]]))
                {
                    threats++;
                    break; // Stop checking once a threat is found in this direction
                }
            }
        }
    }
    return threats;
}

int Gomoku::getNumberOf4Aligned(int player) const
{
	int count = 0;
	// Directions: horizontal, vertical, diagonals
	std::vector<std::pair<int,int>> directions = {
		{0,1}, {1,0}, {1,1}, {1,-1}
	};

	std::vector<std::pair<int, int>> pebbles = getAllPebblesOfPlayer(player);

	for (auto &[r, c] : pebbles)
	{
		for (auto &dir : directions)
		{
			int dr = dir.first;
			int dc = dir.second;

			// Forward direction
			int rr = r + dr;
			int cc = c + dc;
			int countPlayer = 1; // include the current pebble

			bool is_blocked_backward = false;
			bool is_blocked_forward = false;

			while (isWithinBounds(rr, cc) && board[rr][cc] == player)
			{
				countPlayer++;
				rr += dr;
				cc += dc;
			}

			// We are looking only for 4 pebble alignments without any opponent pebble at each end
			if (!isWithinBounds(rr, cc) || board[rr][cc] != EMPTY)
				continue; // Move to the next direction

			// Backward direction
			rr = r - dr;
			cc = c - dc;
			while (isWithinBounds(rr, cc) && board[rr][cc] == player)
			{
				countPlayer++;
				rr -= dr;
				cc -= dc;
			}

			// We are looking only for 4 pebble alignments without any opponent pebble at each end
			if (!isWithinBounds(rr, cc) || board[rr][cc] != EMPTY)
				continue; // Move to the next direction

			// Check if exactly 4 aligned and no opponent pebble at each end
			if (countPlayer == 4)
			{
				count++;
			}
		}
	}
	return count;
}

bool Gomoku::checkPattern(int startRow, int startCol, int dr, int dc, const std::vector<int> &pattern)
{
    int patternLength = pattern.size();
    std::vector<std::pair<int, int>> offsets;

    for (int i = 0; i < patternLength; i++)
    {
        offsets.emplace_back(i * dr, i * dc);
    }

    for (int shift = -patternLength + 1; shift <= 0; shift++)
    {
        bool match = true;
        for (size_t idx = 0; idx < pattern.size(); idx++)
        {
            int row = startRow + offsets[idx].first + shift * dr;
            int col = startCol + offsets[idx].second + shift * dc;

            if (!isWithinBounds(row, col) || board[row][col] != pattern[idx])
            {
                match = false;
                break;
            }
        }
        if (match)
        {
            return true;
        }
    }
    return false;
}


/**
 * Check if the current player has captured at least 10 opponent pebbles.
 */
bool Gomoku::has10Pebbles() const
{
    if (currentPlayer == BLACK) {
        return (blackPlayerPebblesTaken >= 10);
    } else {
        return (whitePlayerPebblesTaken >= 10);
    }
}

/**
 * If the current player has 10 captures, the game ends.
 */
bool Gomoku::process10Pebbles()
{
    if (has10Pebbles()) {
        gameOver = true;
        return true;
    }
    return false;
}

/**
 * Check if placing a pebble at (placedRow, placedCol) results
 * in an alignment of at least 5 consecutive pebbles (horizontal, vertical, diagonal).
 */
bool Gomoku::has5PebblesAligned(int placedRow, int placedCol) const
{
    // Directions: horizontal, vertical, diagonals
    std::vector<std::pair<int,int>> directions = {
        {0,1}, {1,0}, {1,1}, {1,-1}
    };

    for (auto &dir : directions)
    {
        int count = 1; // count newly placed stone
        int dr = dir.first;
        int dc = dir.second;

        // forward direction
        int rr = placedRow + dr;
        int cc = placedCol + dc;
        while (isWithinBounds(rr, cc) && board[rr][cc] == currentPlayer)
        {
            count++;
            rr += dr;
            cc += dc;
        }

        // backward direction
        rr = placedRow - dr;
        cc = placedCol - dc;
        while (isWithinBounds(rr, cc) && board[rr][cc] == currentPlayer)
        {
            count++;
            rr -= dr;
            cc -= dc;
        }

        if (count >= 5) {
            return true;
        }
    }
    return false;
}

/**
 * returns possible capture points for the player, used for debugging
*/
std::vector<std::pair<int, int>> Gomoku::getCapturePoints(int player)
{
	std::vector<std::pair<int, int>> captureMoves;
	int opponent = -player;

	static const std::vector<std::pair<int,int>> directions = {
		{0,1}, {1,0}, {1,1}, {1,-1}
	};

	for (int row = 0; row < boardSize; ++row)
	{
		for (int col = 0; col < boardSize; ++col)
		{
			if (board[row][col] != EMPTY) continue;
			for (const auto& dir : directions)
			{
				int dRow = dir.first;
				int dCol = dir.second;

				for (int sign : {1, -1})
				{
					int r1 = row + sign * dRow;
					int c1 = col + sign * dCol;
					int r2 = row + sign * dRow * 2;
					int c2 = col + sign * dCol * 2;
					int r3 = row + sign * dRow * 3;
					int c3 = col + sign * dCol * 3;

					if (isWithinBounds(r3, c3) &&
						board[r1][c1] == opponent &&
						board[r2][c2] == opponent &&
						board[r3][c3] == player)
					{
						captureMoves.emplace_back(row, col);
					}
				}
			}
		}
	}

	return captureMoves;
}

/**
 * Check if there's at least one opponent's move that could break the line of 5.
 * If so, we add these moves to forcedMoves.
 */
#include <set> // Add this include at the top of your file

bool Gomoku::is5PebblesAlignedBreakable(int placedRow, int placedCol)
{
	int originalPlayer = currentPlayer;
	int opponent = -originalPlayer;

	// Use a set to avoid duplicate candidate moves.
	std::set<std::pair<int,int>> candidateMoves;
	std::vector<std::pair<int,int>> directions = { {0,1}, {1,0}, {1,1}, {1,-1} };
    std::vector<std::pair<int,int>> directions8 = { {0,1}, {1,0}, {1,1}, {1,-1}, {0,-1}, {-1,0}, {-1,-1}, {-1,1} };

    std::set<std::pair<int, int>> alignedStones;
	debugCall([&](){
	    std::cout << "Collecting aligned stones from (" << placedRow << ", " << placedCol << ") for player " << originalPlayer << "\n";
    });

    for (auto &[dr, dc] : directions) {
        alignedStones.insert({placedRow, placedCol});    
        // Forward
        int r = placedRow + dr, c = placedCol + dc;
        while (isWithinBounds(r, c) && board[r][c] == originalPlayer) {
            alignedStones.insert({r, c});
            r += dr;
            c += dc;
        }

        // Backward
        r = placedRow - dr;
        c = placedCol - dc;
        while (isWithinBounds(r, c) && board[r][c] == originalPlayer) {
            alignedStones.insert({r, c});
            r -= dr;
            c -= dc;
        }
    }

    debugCall([&](){
        std::cout << "\nAligned stones found around (" << placedRow << ", " << placedCol << ") for player " << originalPlayer << ":\n";
        for (const auto& [r, c] : alignedStones) {
            std::cout << "  • (" << r << ", " << c << ")\n";
        }

        std::cout << "Total aligned stones: " << alignedStones.size() << "\n";
    });

    for (auto &[r, c] : alignedStones) {
        for (auto &[dr, dc] : directions8) {
            int r2 = r + dr;
            int c2 = c + dc;

            if (!isWithinBounds(r2, c2)) continue;

            if (board[r][c] == originalPlayer && board[r2][c2] == originalPlayer) {
                int r0 = r - dr;
                int c0 = c - dc;
                if (isWithinBounds(r0, c0) && board[r0][c0] == EMPTY) {
                    candidateMoves.insert({r0, c0});
                }
                int r3 = r2 + dr;
                int c3 = c2 + dc;
                if (isWithinBounds(r3, c3) && board[r3][c3] == EMPTY) {
                    candidateMoves.insert({r3, c3});
                }
            }
        }
    }
    debugCall([&](){
        std::cout << "Final candidateMoves: ";
        for (const auto& move : candidateMoves) {
            std::cout << "(" << move.first << ", " << move.second << ") ";
        }
        std::cout << "\n";
        std::cout << "Candidate moves: ";
    });
    // Simulate each candidate move in-place.
	for (auto &move : candidateMoves) {
        debugCall([&](){
            std::cout << "(" << move.first << ", " << move.second << ")\n";
        });
        int r = move.first;
		int c = move.second;
		
		// Save original state for reversion.
		int originalCell = board[r][c];  // Should be EMPTY.
		board[r][c] = opponent;  // Simulate opponent move.

		// Capture simulation: record any stones removed.
		std::vector<std::pair<int,int>> capturedPositions;
		{
			std::vector<std::pair<int,int>> simDirs = { {0,1}, {1,0}, {1,1}, {1,-1} };
			for (auto &d : simDirs) {
				int dRow = d.first, dCol = d.second;
				for (int sign : {1, -1}) {
					std::vector<std::pair<int,int>> tempCaptured;
					// Check for exactly two stones from originalPlayer.
					for (int offset = 1; offset <= 2; offset++) {
						int checkR = r + sign * dRow * offset;
						int checkC = c + sign * dCol * offset;
						if (isWithinBounds(checkR, checkC) && board[checkR][checkC] == originalPlayer)
							tempCaptured.push_back(std::make_pair(checkR, checkC));
						else
							break;
					}
					if (tempCaptured.size() == 2) {
						int nextR = r + sign * dRow * 3;
						int nextC = c + sign * dCol * 3;
						if (isWithinBounds(nextR, nextC) && board[nextR][nextC] == opponent) {
							for (auto &pos : tempCaptured) {
								board[pos.first][pos.second] = EMPTY;
								capturedPositions.push_back(pos);
							}
						}
					}
				}
			}
		}
		
		// Check if the 5-alignment (for originalPlayer) at (placedRow, placedCol) is now broken.
		bool alignmentBroken = !has5PebblesAligned(placedRow, placedCol);
		
		// Revert the simulation.
		board[r][c] = originalCell;
		for (auto &pos : capturedPositions) {
			board[pos.first][pos.second] = originalPlayer;
		}
		
		// If the move breaks the alignment, add it to forcedMoves.
		if (alignmentBroken) {
			forcedMoves.push_back(std::make_pair(r, c));
			debugCall([&](){
				std::cout << "Move to break line: (" << r << ", " << c << ")\n";
			});
		}
	}
	
	return !forcedMoves.empty();
}


/**
 * Process an alignment of 5 stones: check if it is breakable by the opponent.
 * If not breakable, the current player wins immediately.
 */
bool Gomoku::process5Pebbles(int placedRow, int placedCol)
{
    if (has5PebblesAligned(placedRow, placedCol))
    {
        debugCall([&](){
            std::cout << "Player " << currentPlayer
                      << " has aligned at least 5 pebbles\n";
        });
        // Check if opponent can break it
        if ((gameType == "duo" || gameType == "normal") && is5PebblesAlignedBreakable(placedRow, placedCol))
        {
            debugCall([&](){
                std::cout << "Opponent can break the line of 5 pebbles\n";
            });
        }
        else
        {
            debugCall([&](){
                std::cout << "The player wins\n";
            });
            gameOver = true;
            return true;
        }
    }
    return false;
}

bool Gomoku::isBoardEmpty() const
{
    return !std::any_of(board.begin(), board.end(), [](const std::vector<int>& row) {
        return std::any_of(row.begin(), row.end(), [](int cell) { return cell != EMPTY; });
    });
}

/**
 * for bonuses look if a line has more than 5 Pebbles to forbid the move
 */
bool Gomoku::hasMoreThan5PebblesAligned(int placedRow, int placedCol) const
{
    std::vector<std::pair<int,int>> directions = {
        {0,1}, {1,0}, {1,1}, {1,-1}
    };

    for (auto &dir : directions)
    {
        int count = 1;
        int dr = dir.first;
        int dc = dir.second;

        int rr = placedRow + dr;
        int cc = placedCol + dc;
        while (isWithinBounds(rr, cc) && board[rr][cc] == currentPlayer)
        {
            count++;
            rr += dr;
            cc += dc;
        }

        rr = placedRow - dr;
        cc = placedCol - dc;
        while (isWithinBounds(rr, cc) && board[rr][cc] == currentPlayer)
        {
            count++;
            rr -= dr;
            cc -= dc;
        }

        if (count > 5) { 
            return true;
        }
    }
    
    return false;
}