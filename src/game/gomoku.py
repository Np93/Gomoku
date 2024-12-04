import numpy as np
from src.game.playerTokens import PlayerToken

class Gomoku:
	"""Gomoku game class."""

	def __init__(self):
		"""Initialize Gomoku game."""
		#NOTE ALL ATTRIBUTES ARE CONSIDERED AS PRIVATE EVEN WITHOUT THE UNDERSCORE
		super().__init__()
		self.board_size: int = 19
		self.board: np.ndarray = np.zeros((self.board_size, self.board_size), dtype=int)
		self.current_player: int = PlayerToken.BLACK.value
		self.white_player_pebbles_taken: int = 0
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


	### UTILS ###
	def draw_board(self):
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

	### RULES AND GAME LOGIC ###
	#NOTE We shoud use only this function to play the game

	def process_move(self, row: int, col: int) -> bool:
		"""
		Processes a move by the current player at the specified row and column.
		"""

		# Update the board with the current player's move
		self.board[row, col] = self.current_player

		# Check for captures and update the board
		if not self._check_capture_and_update(row, col): #TODO pass check_capture_and_update as a private method
			if self.is_double_three(row, col): #TODO pass is_double_three as a private method
				print(f"Mouvement interdit ({row}, {col}) : Double-trois détecté")
				self._undo_move(row, col)
				return False

		#TODO Check for win condition

		# Switch to the next player
		print(f"Joueur actuel : {self.current_player}")
		self.current_player = -self.current_player
		print(f"Joueur suivant : {self.current_player}")

		return True
 
	def _undo_move(self, row: int, col: int) -> None:
		"""Undo a move on the board."""
		self.board[row, col] = PlayerToken.EMPTY.value

	def _is_within_bounds(self, row : int, col : int) -> bool:
		"""Check if a position is within the board bounds."""
		return 0 <= row < self.board_size and 0 <= col < self.board_size

	#NOTE This function work 
	def _check_capture_and_update(self, row : int, col : int) -> bool:
		"""Check for captures and update the board.
  		Le mouvement a déjà été effectué, row et col sont les positions du mouvement.
		Cette fonction update le board par contre en cas de capture."""
  
		directions = [(0, 1), (1, 0), (1, 1), (1, -1)] # Horizontal, vertical, and diagonals
		is_captures = False
		opponent = -self.current_player

		for dr, dc in directions:
			for sign in [1, -1]:  # Check both directions
				for n in range(2, 3):  # Checking for 2, 3, or 4 stones
					captured_stones = []
					# Check for exactly n opponent stones in the direction
					for i in range(1, n + 1):
						r, c = row + sign * dr * i, col + sign * dc * i
						if 0 <= r < self.board_size and 0 <= c < self.board_size:
							if self.board[r, c] == opponent:
								captured_stones.append((r, c))
							else:
								break
						else:
							break

					# Check if these are exactly n opponent stones followed by a current player stone
					if len(captured_stones) == n:
						r, c = row + sign * dr * (n + 1), col + sign * dc * (n + 1)
						if 0 <= r < self.board_size and 0 <= c < self.board_size and self.board[r, c] == self.current_player:
							# Capture confirmed
							is_captures = True
							for cr, cc in captured_stones:
								self.board[cr, cc] = 0  # Remove the stone from the board
							if self.current_player == PlayerToken.BLACK.value:
								self.black_player_pebbles_taken += len(captured_stones)
							else:  # White's turn
								self.white_player_pebbles_taken += len(captured_stones)
		return is_captures

	@staticmethod
	def is_move_valid(self, row: int, col: int) -> bool:
		"""Vérifie si un mouvement est valide selon les règles de Gomoku.
		Le mouvement a déjà été effectué, row et col sont les positions du mouvement."""
		# Vérifier que la case est vide
		if self.board[row, col] != 0:
			print(f"Case non vide : ({row}, {col})")
			return False

		# Créer une copie pour simuler le mouvement
		gomoku_copy = self.copy()
		gomoku_copy.board[row, col] = gomoku_copy.current_player

		# Si pas de capture, il faut vérifier le double-trois
		if not gomoku_copy._check_capture_and_update(row, col):
			if gomoku_copy.is_double_three(row, col):
				print(f"Mouvement interdit ({row}, {col}) : Double-trois détecté")
				self._undo_move(row, col)
				return False

		return True

	#TODO CHECK THIS FUNCTION
	def is_double_three(self, row: int, col: int) -> bool:
		"""Check if the move creates a double-three configuration.
		Le mouvement a déjà été effectué, row et col sont les positions du mouvement."""
		threats = 0
		player = self.current_player
		color_sequence = []
		i_pos = 0
		directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

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
			if self._analyze_sequence_for_threats(color_sequence, player, i_pos):
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
			end_index = middle_index + 3  # End a bit right of the middle stone, adjust based on pattern length
			pattern_length = len(pattern)
			
			# Slide the window of pattern length around the middle stone
			for offset in range(-2, 3):
				if 0 <= start_index + offset < seq_len - pattern_length + 1:
					if tuple(sequence[start_index + offset:start_index + offset + pattern_length]) == pattern:
						return True

		return False

	def is_win(self, move_pos):
		"""Check if there is a winning condition on the board."""

		# Vérifie si un joueur a pris au moins 10 pierres adverses
		if self.current_player == PlayerToken.BLACK.value:
			if self.black_player_pebbles_taken >= 10:
				self.game_over = True
				return True, [], "score_10"
		else:
			if self.white_player_pebbles_taken >= 10:
				self.game_over = True
				return True, [], "score_10"

		row, col = move_pos["row"], move_pos["col"]
		player = self.current_player  # Current player making the move
		opponent = -player  # Opponent player

		# Directions represent vertical, horizontal, and two diagonal checks
		directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

		for dr, dc in directions:
			count = 1  # Start counting the stone just placed
			line = [(row, col)]  # Store the position of the stones in the line

			# Check one direction (e.g., left or up)
			for i in range(1, 5):
				r, c = row + i * dr, col + i * dc
				if 0 <= r < self.board_size and 0 <= c < self.board_size and self.board[r, c] == player:
					count += 1
					line.append((r, c))
				else:
					break

			# Check the opposite direction (e.g., right or down)
			for i in range(1, 5):
				r, c = row - i * dr, col - i * dc
				if 0 <= r < self.board_size and 0 <= c < self.board_size and self.board[r, c] == player:
					count += 1
					line.append((r, c))
				else:
					break

			# Check if the count of consecutive stones has reached five or more
			if count >= 5:
				print(f"Ligne détectée : {line}")

				# Détermine les informations relatives à l'adversaire
				opponent_pebbles_taken = (
					self.white_player_pebbles_taken if self.current_player == PlayerToken.BLACK.value else self.black_player_pebbles_taken
				)
				opponent_color = "White" if self.current_player == PlayerToken.BLACK.value else "Black"

				# Affiche le nombre de pierres prises par l'adversaire
				print(f"{opponent_color} player has {opponent_pebbles_taken} pebbles")

				# Vérifie si l'adversaire a pris au moins 8 pierres
				if opponent_pebbles_taken >= 8:
					# Simule le tour de l’adversaire
					self.current_player = -self.current_player
					capture_possible, empty_pos = self.check_possible_capture()
					self.current_player = -self.current_player  # Rétablit le joueur actuel

					# Si une capture est possible, retourne une indication pour le coup spécial
					if capture_possible:
						return False, line, "play_special"

				# Si l'adversaire a moins de 8 pierres, vérifie si une capture est possible sur la ligne de 5
				self.current_player = -self.current_player
				capture_on_five, empty_pos = self.check_capture_on_five(line)
				self.current_player = -self.current_player
				if capture_on_five:
					print(f"Capture possible sur la ligne de 5 pour {opponent_color}")
					return False, line, "break_line"

				# Si aucune capture ne peut briser la ligne, victoire confirmée
				self.game_over = True
				print(f"Ligne de 5 détectée : {line}")
				return True, line, "win_five"

		# Si aucune condition de victoire n’est remplie, retourne False
		return False, [], "no_win"

	def check_possible_capture(self):
		"""Check if the current player can potentially capture a piece on the entire board."""
		directions = [(0, 1), (1, 0), (1, 1), (1, -1)]  # Horizontal, vertical, and diagonals
		opponent = -self.current_player  # Opponent's token
		player = self.current_player  # Current player's token (the next player to move)

		# print(f"Checking possible captures for player {player} (next to move)")

		# Scan the entire board
		for row in range(self.board_size):
			for col in range(self.board_size):
				if self.board[row, col] == player:  # Only check around the player's stones
					for dr, dc in directions:
						for sign in [1, -1]:  # Check both directions
							# Build the pattern (player, opponent, opponent, empty)
							pattern = [
								(row + sign * dr * i, col + sign * dc * i) for i in range(4)
							]

							# Ensure all positions in the pattern are within bounds
							if all(self._is_within_bounds(row, col) for row, col in pattern):
								stones = [
									self.board[pattern[i][0], pattern[i][1]] for i in range(4)
								]
								# print(f"Checking pattern at {pattern}: {stones}")

								if (
									stones[0] == player and
									stones[1] == opponent and
									stones[2] == opponent and
									stones[3] == PlayerToken.EMPTY.value
								):
									print("Capture possible")
									return True, pattern[3]

		# print("Capture pas possible")
		return False, None

	def check_capture_on_five(self, line):
		"""
		Check if a capture is possible for the current player and if at least one capture
		intersects with the given line of 5 stones.
		"""
		directions = [(0, 1), (1, 0), (1, 1), (1, -1)]  # Horizontal, vertical, and diagonals
		opponent = -self.current_player  # Opponent's token
		player = self.current_player  # Current player's token
		capture_patterns = []  # Stocke toutes les captures possibles sur le plateau

		print(f"Checking all possible captures for player {player} and cross-referencing with the line {line}")

		# Parcourt tout le plateau pour chercher les captures possibles
		for row in range(self.board_size):
			for col in range(self.board_size):
				if self.board[row, col] == player:  # Vérifie autour des pierres du joueur
					for dr, dc in directions:
						for sign in [1, -1]:  # Vérifie dans les deux directions
							# Construit le motif (player, opponent, opponent, empty)
							pattern = [
								(row + sign * dr * i, col + sign * dc * i) for i in range(4)
							]

							# Vérifie si toutes les positions du motif sont dans les limites
							if all(self._is_within_bounds(row , col) for row, col in pattern):
								stones = [
									self.board[pattern[i][0], pattern[i][1]] for i in range(4)
								]
								# print(f"Checking pattern at {pattern}: {stones}")

								# Vérifie le motif (player, opponent, opponent, empty)
								if (
									stones[0] == player and
									stones[1] == opponent and
									stones[2] == opponent and
									stones[3] == PlayerToken.EMPTY.value
								):
									# print(f"Capture possible via pattern {pattern}")
									capture_patterns.append(pattern)

		# Vérifie si une capture passe par la ligne de 5
		for pattern in capture_patterns:
			pos2_in_line = pattern[1] in line
			pos3_in_line = pattern[2] in line

			if pos2_in_line or pos3_in_line:  # Si pos2 ou pos3 est dans la ligne
				empty_pos = pattern[3]
				print(f"Capture sur la ligne de 5 via pattern {pattern}")
				return True, empty_pos

		print("No capture intersects with the line of 5")
		return False, None#