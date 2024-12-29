import numpy as np
from src.game.playerTokens import PlayerToken

DEBUG = False

#create a decoreto that call the cunftion if debuig only
def debug(func):
	def wrapper(*args, **kwargs):
		if DEBUG:
			return func(*args, **kwargs)
	return wrapper

class Gomoku:
	"""Gomoku game class."""

	def __init__(self):
		"""Initialize Gomoku game."""
		#NOTE ALL ATTRIBUTES ARE CONSIDERED AS PRIVATE EVEN WITHOUT THE UNDERSCORE
		self.board_size: int = 19
		self.board: np.ndarray = np.zeros((self.board_size, self.board_size), dtype=int)
		self.current_player: int = PlayerToken.BLACK.value
		self.white_player_pebbles_taken: int = 0 # Number of pebbles taken by the white player
		self.black_player_pebbles_taken: int = 0
		self.forced_moves: list = []
		self.game_over: bool = False

	def copy(self) -> "Gomoku":
		"""Create a copy of the current game state."""
		new_copy = Gomoku()
		new_copy.board = np.copy(self.board)
		new_copy.current_player = self.current_player
		new_copy.white_player_pebbles_taken = self.white_player_pebbles_taken
		new_copy.black_player_pebbles_taken = self.black_player_pebbles_taken
		new_copy.forced_moves = self.forced_moves.copy()  # Ensure a separate list
		new_copy.game_over = self.game_over
		return new_copy


	### Public utils ###
	def draw_board(self) -> None:
		"""Draw the Gomoku board."""
		header = "   " + " ".join(f"{i:2}" for i in range(self.board_size))
		print(header)
		for i in range(self.board_size):
			row = f"{i:2} " + " ".join(
				"B" if self.board[i, j] == PlayerToken.BLACK.value else
				"W" if self.board[i, j] == PlayerToken.WHITE.value else
				"." for j in range(self.board_size)
			)
			print(row)

	def get_all_possible_moves(self) -> list[tuple[int, int]]:
		"""
		Get all possible moves for the given player.

		This method scans the entire board and returns a list of all empty positions
		where a move can be made. Note that this method does not check if the move 
		is legitimate according to the game rules; it only identifies empty positions.

		Returns:
			list[tuple[int, int]]: A list of tuples representing the row and column 
			indices of all possible moves.
		"""
		"""Get all possible moves for the given player. """
		possible_moves = []

		for row in range(self.board_size):
			for col in range(self.board_size):
				if self.board[row, col] == PlayerToken.EMPTY.value:
					possible_moves.append((row, col))

		return possible_moves

	def get_all_close_moves(self) -> list[tuple[int, int]]:
		"""
		Get all possible moves for the given player.

		This method scans the entire board and returns a list of all empty positions
		where a move can be made. Note that this method does not check if the move 
		is legitimate according to the game rules; it only identifies empty positions.

		Returns:
			list[tuple[int, int]]: A list of tuples representing the row and column 
			indices of all possible moves.
		"""
		"""Get all possible moves for the given player. """

		possible_moves = []
		direction = [(0, 1), (1, 0), (1, 1), (1, -1)] # Horizontal, vertical, and diagonals

		for row in range(self.board_size):
			for col in range(self.board_size):
				if self.board[row, col] == PlayerToken.EMPTY.value:
					for dr, dc in direction:
						# Forward neighbor
						adj_row_f = row + dr
						adj_col_f = col + dc
						if (0 <= adj_row_f < self.board_size) and (0 <= adj_col_f < self.board_size):
							if self.board[adj_row_f, adj_col_f] != PlayerToken.EMPTY.value:
								possible_moves.append((row, col))
								break  # Found a pebble nearby; move on to next cell

						# Backward neighbor
						adj_row_b = row - dr
						adj_col_b = col - dc
						if (0 <= adj_row_b < self.board_size) and (0 <= adj_col_b < self.board_size):
							if self.board[adj_row_b, adj_col_b] != PlayerToken.EMPTY.value:
								possible_moves.append((row, col))
								break  # Found a pebble nearby; move on to next cell

		return possible_moves

	### RULES AND GAME LOGIC ###
	#NOTE Function starting with _process check for the rule and change the game state!
	#NOTE We shoud use only this function to play the game
	def process_move(self, placed_row: int, placed_col: int) -> tuple[bool, str]:
		"""
		Processes a move by the current player at the specified row and column.
		Returns a tuple of (valid_move, reason) where:
		"""

		if self.game_over:
			return False, "game_over"

		# Si le joueur dopit faire un mouvement forcé et que ce n'est pas le cas, return false
		if self._process_forced_move(placed_row, placed_col):
			return False, "forced_move"

		# Update the board with the current player's move
		self.board[placed_row, placed_col] = self.current_player

		# Check for captures and update the board
		if not self._process_capture(placed_row, placed_col):
			if self._is_double_three(placed_row, placed_col):
				debug(lambda: print(f"Mouvement interdit ({placed_row}, {placed_col}) : Double-trois détecté"))()
				self._undo_move(placed_row, placed_col)
				return False, "double_three"

		# Verifie si le joueur possede au moins 10 pierres adverses, si oui -> fin de la partie
		if self._process_10_pebbles():
			return True, "win_score"

		# Verifie si le joueur a aligné au moins 5 pierres sans possibilité de contre, si oui -> fin de la partie
		if self._process_5_pebbles(placed_row, placed_col):
			return True, "win_alignments"

		self._change_player()

		return True, "valid_move"

	### Private utils #####
	def _change_player(self) -> None:
		"""Change the current player."""
		self.current_player = -self.current_player

	def _undo_move(self, placed_row: int, placed_col: int) -> None:
		"""Undo a move on the board."""
		self.board[placed_row, placed_col] = PlayerToken.EMPTY.value

	def _is_within_bounds(self, placed_row : int, placed_col : int) -> bool:
		"""Check if a position is within the board bounds."""
		return 0 <= placed_row < self.board_size and 0 <= placed_col < self.board_size

	### Captures ###
	def _process_capture(self, placed_row: int, placed_col: int) -> bool:
		"""
		Check if the most recent move by the current player results in captures of opponent stones.

		A capture occurs if, starting from the placed stone's position, there are exactly `n` (for n=2 or n=3) 
		consecutive opponent stones in a straight line (horizontal, vertical, or diagonal), followed by a stone 
		of the current player, forming a pattern like: CurrentPlayer - Opponent - Opponent - CurrentPlayer.

		If such a pattern is found, all the in-between opponent stones are removed from the board, and 
		the current player's capture count is increased accordingly.
		
		Parameters
		----------
		placed_row : int
			The row index of the last placed stone.
		placed_col : int
			The column index of the last placed stone.

		Returns
		-------
		bool
			True if at least one capture was made, False otherwise.
		"""

		# Directions represent vectors in the format (d_row, d_col):
		# Horizontal: (0, 1)
		# Vertical:   (1, 0)
		# Diagonals:  (1, 1) and (1, -1)
		directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
		capture_occurred = False
		opponent_token = -self.current_player

		for d_row, d_col in directions:
			# Check in both the 'forward' and 'backward' directions along this line.
			for direction_sign in [1, -1]:
				# Check for patterns of length n, where n is currently set to 2 (and could be extended if needed)
				for num_opponent_stones in range(2, 3):  
					captured_stones_positions = []

					# Verify that exactly 'num_opponent_stones' opponent stones exist in a line
					# following the placed stone.
					for offset in range(1, num_opponent_stones + 1):
						check_row = placed_row + direction_sign * d_row * offset
						check_col = placed_col + direction_sign * d_col * offset

						# Ensure we stay within board bounds
						if 0 <= check_row < self.board_size and 0 <= check_col < self.board_size:
							if self.board[check_row, check_col] == opponent_token:
								# Accumulate opponent stone positions that may be captured
								captured_stones_positions.append((check_row, check_col))
							else:
								# If we don't find an opponent stone, break early
								break
						else:
							# Out of board bounds
							break

					# If we found the exact number of consecutive opponent stones, 
					# check for a current player stone immediately after them.
					if len(captured_stones_positions) == num_opponent_stones:
						next_row = placed_row + direction_sign * d_row * (num_opponent_stones + 1)
						next_col = placed_col + direction_sign * d_col * (num_opponent_stones + 1)

						if (0 <= next_row < self.board_size and 
							0 <= next_col < self.board_size and 
							self.board[next_row, next_col] == self.current_player):

							# Confirmed capture pattern found: CurrentPlayer - Opponent(s) - CurrentPlayer
							capture_occurred = True

							# Remove the captured opponent stones from the board
							for stone_row, stone_col in captured_stones_positions:
								self.board[stone_row, stone_col] = 0

							# Update the capture count for the current player
							if self.current_player == PlayerToken.BLACK.value:
								self.black_player_pebbles_taken += len(captured_stones_positions)
							else:
								self.white_player_pebbles_taken += len(captured_stones_positions)

		return capture_occurred

	def _process_forced_move(self, placed_row: int, placed_col: int) -> bool:
		"""Check if the current player has to make a forced move.
		Returns True if the player has to make a forced move, False otherwise."""
  
		if len(self.forced_moves) > 0:
			if (placed_row, placed_col) not in self.forced_moves:
				print(f"Invalid move ({placed_row}, {placed_col}): Forced move required")
				print(f"Forced moves: {self.forced_moves}")
				return True
		
		# Reset forced moves if the player made a valid move
		self.forced_moves = []
		return False

	### Double-three detection ###
	def _is_double_three(self, row: int, col: int) -> bool:
		"""Check if the move creates a double-three configuration.
		Le mouvement a déjà été effectué, row et col sont les positions du mouvement."""
		threats = 0
		color_sequence = []
		directions = [(0, 1), (1, 0), (1, 1), (1, -1)] # Horizontal, vertical, and diagonals

		for dr, dc in directions:
			# Check one direction (e.g., left or up)
			i_pos = 0
			color_sequence = []
			color_sequence.append(self.board[row, col])
			for i in range(1, 5):
				r, c = row + i * dr, col + i * dc
				if 0 <= r < self.board_size and 0 <= c < self.board_size:
					color_sequence.append(self.board[r, c])
				else :
					break

			# Check the opposite direction (e.g., right or down)
			for i in range(1, 5):
				r, c = row - i * dr, col - i * dc
				if 0 <= r < self.board_size and 0 <= c < self.board_size:
					i_pos += 1
					#add at the beginning of the list
					color_sequence.insert(0, self.board[r, c])
				else :
					break

			if self._analyze_sequence_for_threats(color_sequence, self.current_player, i_pos):
				threats += 1

			# Early exit if more than one threat is found (double-three condition)
			if threats >= 2:
				return True
		
		return False

	def _analyze_sequence_for_threats(self, sequence, player, middle_index):
		"""Analyze a sequence to find specific open three threats ensuring the played stone is part of the pattern."""
		seq_len = len(sequence)

		# Define patterns where the middle stone is part of an "open three"
		# Patterns are checked with the middle stone as part of the three
		patterns = [
			(0, player, player, player, 0),
			(0, player, player, 0, player, 0),
			(0, player, 0, player, player, 0)
		]

		# Check patterns ensuring the middle stone is within the "three" part
		for pattern in patterns:
			start_index = middle_index - 2  # Start a bit left of the middle stone
			pattern_length = len(pattern)
			
			# Slide the window of pattern length around the middle stone
			for offset in range(-2, 3):
				if 0 <= start_index + offset < seq_len - pattern_length + 1:
					if tuple(sequence[start_index + offset:start_index + offset + pattern_length]) == pattern:
						return True

		return False

	### VICTORY CONDITIONS ###
	def _has_10_pebbles(self) -> bool:
		"""Check if a player has captured at least 10 opponent pebbles."""
		if self.current_player == PlayerToken.BLACK.value:
			return self.black_player_pebbles_taken >= 10
		else:
			return self.white_player_pebbles_taken >= 10

	def _process_10_pebbles(self) -> bool:
		"""Check if the current player has captured at least 10 opponent pebbles."""
		if self._has_10_pebbles():
			print(f"Player {self.current_player} has captured at least 10 opponent pebbles")
			self.game_over = True
			return True
		return False

	def _has_5_pebbles_aligned(self, placed_row: int, placed_col: int) -> bool:
		"""
		Check if placing a pebble at the given position results in a continuous line 
		of at least five pebbles of the current player's color. This can occur 
		horizontally, vertically, or along either diagonal.
		"""
		current_player_token = self.current_player
		directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

		for d_row, d_col in directions:
			count = 1  # Include the newly placed pebble

			# Check in the 'forward' direction
			row, col = placed_row + d_row, placed_col + d_col
			while 0 <= row < self.board_size and 0 <= col < self.board_size and self.board[row, col] == current_player_token:
				count += 1
				row += d_row
				col += d_col

			# Check in the 'backward' direction
			row, col = placed_row - d_row, placed_col - d_col
			while 0 <= row < self.board_size and 0 <= col < self.board_size and self.board[row, col] == current_player_token:
				count += 1
				row -= d_row
				col -= d_col

			if count >= 5:
				return True

		return False

	def _is_5_pebbles_aligned_breakable(self, placed_row: int, placed_col: int) -> bool:
		"""
		Check all possible ways the opponent can break a line of five pebbles
		"""

		# temp swich player
		self.current_player = -self.current_player
		moves = self.get_all_possible_moves()
		self.current_player = -self.current_player

		for row, col in moves:
			# Process the move
			Gomoku_copy = self.copy()
			Gomoku_copy.current_player = -self.current_player
			Gomoku_copy.board[row, col] = Gomoku_copy.current_player
			Gomoku_copy._process_capture(row, col)

			# Check if the original player can still win
			Gomoku_copy.current_player = self.current_player
			if not Gomoku_copy._has_5_pebbles_aligned(placed_row, placed_col):
				self.forced_moves.append((row, col))
				debug(lambda: print(f"Moves to break the line: {self.forced_moves}"))()
									
		# Return True if at least one move can break the line
		return len(self.forced_moves) > 0

	def _process_5_pebbles(self, placed_row: int, placed_col: int) -> bool:
		"""
		Process a move where the current player has aligned at least 5 pebbles.
		"""
		# Check if the opponent can break the line of 5 pebbles
		if self._has_5_pebbles_aligned(placed_row, placed_col):
			debug(lambda: print(f"Player {self.current_player} has aligned at least 5 pebbles"))()
			if self._is_5_pebbles_aligned_breakable(placed_row, placed_col):
				debug(lambda: print(f"The opponent can break the line of 5 pebbles"))()
			else:
				debug(lambda: print("The player wins"))()
				self.game_over = True
				return True
		return False