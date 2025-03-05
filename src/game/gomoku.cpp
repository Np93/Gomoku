#include "gomoku.hpp"

#include <iostream>
#include <algorithm>
#include <cstring>

// Definition of the global debug flag
bool DEBUG = false;

void debugCall(const std::function<void()>& func)
{
    if (DEBUG) {
        func();
    }
}

Gomoku::Gomoku()
{
    boardSize = 19;
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
    newCopy.board = board;
    newCopy.currentPlayer = currentPlayer;
    newCopy.whitePlayerPebblesTaken = whitePlayerPebblesTaken;
    newCopy.blackPlayerPebblesTaken = blackPlayerPebblesTaken;
    newCopy.forcedMoves = forcedMoves;  // copy
    newCopy.gameOver = gameOver;
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

std::pair<bool, std::string> Gomoku::processMove(int placedRow, int placedCol)
{
    if (gameOver) {
        return std::make_pair(false, "game_over");
    }

    // If the player must make a forced move but didn't:
    if (processForcedMove(placedRow, placedCol)) {
        return std::make_pair(false, "forced_move");
    }

    // Place the stone on the board
    board[placedRow][placedCol] = currentPlayer;

    // Process captures
    bool captured = processCapture(placedRow, placedCol);

    // Check double-three: if it is a double-three, revert and return false
    if (!captured && isDoubleThree(placedRow, placedCol))
    {
        debugCall([&](){
            std::cout << "Mouvement interdit (" 
                      << placedRow << ", " << placedCol 
                      << ") : Double-three detecte" << std::endl;
        });
        undoMove(placedRow, placedCol);
        return std::make_pair(false, "double_three");
    }

    // Check if current player has captured 10 pebbles -> immediate win
    if (process10Pebbles()) {
        return std::make_pair(true, "win_score");
    }

    // Check if current player aligned at least 5
    if (process5Pebbles(placedRow, placedCol)) {
        return std::make_pair(true, "win_alignments");
    }

    // Change turn
    changePlayer();

    return std::make_pair(true, "valid_move");
}

// GETTERS
int Gomoku::getBoardSize() const
{
    return boardSize;
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
bool Gomoku::processCapture(int placedRow, int placedCol)
{
    // Directions: horizontal, vertical, diagonals
    std::vector<std::pair<int,int>> directions = {
        {0,1}, {1,0}, {1,1}, {1,-1}
    };
    bool captureOccurred = false;
    int opponentToken = -currentPlayer;

    for (auto &dir : directions)
    {
        int dRow = dir.first;
        int dCol = dir.second;

        // Check in both forward/backward directions
        for (int directionSign : {1, -1})
        {
            // We only check for patterns of 2 or 3 consecutive opponent stones
            for (int numOpponentStones = 2; numOpponentStones == 2; numOpponentStones++)
            {
                std::vector<std::pair<int,int>> capturedStonesPositions;

                // Collect consecutive opponent stones
                for (int offset = 1; offset <= numOpponentStones; offset++)
                {
                    int checkR = placedRow + directionSign * dRow * offset;
                    int checkC = placedCol + directionSign * dCol * offset;
                    if (isWithinBounds(checkR, checkC))
                    {
                        if (board[checkR][checkC] == opponentToken) {
                            capturedStonesPositions.push_back({checkR, checkC});
                        } else {
                            break;
                        }
                    } else {
                        break;
                    }
                }

                // If we found exactly numOpponentStones, check next cell is currentPlayer
                if ((int)capturedStonesPositions.size() == numOpponentStones)
                {
                    int nextR = placedRow + directionSign * dRow * (numOpponentStones + 1);
                    int nextC = placedCol + directionSign * dCol * (numOpponentStones + 1);

                    if (isWithinBounds(nextR, nextC) &&
                        board[nextR][nextC] == currentPlayer)
                    {
                        // We have a capture pattern
                        captureOccurred = true;
                        // Remove captured stones
                        for (auto &pos : capturedStonesPositions) {
                            board[pos.first][pos.second] = EMPTY;
                        }
                        // Update player's capture count
                        if (currentPlayer == BLACK) {
                            blackPlayerPebblesTaken += (int)capturedStonesPositions.size();
                        } else {
                            whitePlayerPebblesTaken += (int)capturedStonesPositions.size();
                        }
                    }
                }
            }
        }
    }

    return captureOccurred;
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

int Gomoku::getNumberOfThreats(int player)
{
    std::vector<std::pair<int, int>> pebbles = getAllPebblesOfPlayer(player);
    int threats = 0;

    std::vector<std::vector<int>> patterns = {
        {0, player, player, player, 0},
        {0, player, player, 0, player, 0},
        {0, player, 0, player, player, 0}
    };

    std::vector<std::pair<int, int>> directions = {
        {0, 1}, {1, 0}, {1, 1}, {1, -1}
    };

    for (auto &[row, col] : pebbles)
    {
        for (auto &[dr, dc] : directions)
        {
            for (const auto &pattern : patterns)
            {
                if (checkPattern(row, col, dr, dc, pattern) || checkPattern(row, col, -dr, -dc, pattern))
                {
                    threats++;
                    break;
                }
            }
        }
    }
    return threats;
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
 * Check if there's at least one opponent's move that could break the line of 5.
 * If so, we add these moves to forcedMoves.
 */
bool Gomoku::is5PebblesAlignedBreakable(int placedRow, int placedCol)
{
    // Temporarily switch to opponent
    int originalPlayer = currentPlayer;
    int opponent = -originalPlayer;

    // Get all possible moves for the opponent
    currentPlayer = opponent;
    std::vector<std::pair<int,int>> moves = getAllPossibleMoves();
    // Switch back
    currentPlayer = originalPlayer;

    // Test each possible move by the opponent
    for (auto &m : moves)
    {
        int r = m.first;
        int c = m.second;

        // Make a temporary copy of the board
        Gomoku gCopy = clone();
        gCopy.currentPlayer = opponent;

        // Place the opponent's stone
        gCopy.board[r][c] = gCopy.currentPlayer;
        // Process possible captures from that move
        gCopy.processCapture(r, c);

        // Switch back to original player in the copy
        gCopy.currentPlayer = originalPlayer;

        // If after that move, there's no 5 in a row for original player,
        // it means the opponent broke the line -> forced move
        if (!gCopy.has5PebblesAligned(placedRow, placedCol))
        {
            forcedMoves.push_back(std::make_pair(r, c));
            debugCall([&](){
                std::cout << "Move to break line: (" << r << "," << c << ")\n";
            });
        }
    }
    return (!forcedMoves.empty());
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
        if (is5PebblesAlignedBreakable(placedRow, placedCol))
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