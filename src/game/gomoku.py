
import numpy as np

from src.game.playerTokens import PlayerToken


class Gomoku:
	"""Gomoku game class."""

	def __init__(self, board_size=19, player = PlayerToken.BLACK.value):
		"""Initialize Gomoku game."""
		super().__init__()
		self.board_size = board_size
		self.board = np.zeros((board_size, board_size), dtype='int8')
		self.current_player = player
		self.white_player_pebbles_taken = 0
		self.black_player_pebbles_taken = 0
		self.forced_moves = []
		self.game_over = False

	### RULES AND GAME LOGIC ###

	def copy(self):
		"""Create a copy of the current game state."""
		copy = Gomoku(self.board_size)
		copy.board = np.copy(self.board)
		copy.current_player = self.current_player
		copy.white_player_pebbles_taken = self.white_player_pebbles_taken
		copy.black_player_pebbles_taken = self.black_player_pebbles_taken
		copy.forced_moves = self.forced_moves
		copy.game_over = self.game_over
		return copy

	def process_move(self, row: int, col: int, code: int) -> bool:
		"""
		Processes a move by the current player at the specified row and column.
		"""

		# Update the board with the current player's move
		self.board[row, col] = self.current_player

		# Check for captures and update the board
		if code == 2:
			if not self._check_capture_and_update(row, col): #TODO pass _check_capture_and_update as a private method
				# if self.is_double_three(row, col): #TODO pass is_double_three as a private method
				if not self.is_move_forbidden(row, col):
					print(f"Mouvement interdit ({row}, {col}) : Double-trois détecté")
					self._undo_move(row, col)
					return False, None, "règle du double-trois"
			return True, None, None

		#TODO Check for win condition
		if code == 1:
			mode, line, message = self.is_win(row, col)
			return mode, line, message
		# Switch to the next player
		# print(f"Joueur actuel : {self.current_player}")
		# self.current_player = -self.current_player
		# print(f"Joueur suivant : {self.current_player}")

		return True, None, None

	def _undo_move(self, row: int, col: int) -> None:
		"""Undo a move on the board."""
		self.board[row, col] = PlayerToken.EMPTY.value

	def is_move_forbidden(self, row: int, col: int):
		"""Check if the move is forbidden based on Gomoku rules."""
		# row, col = move_pos['row'], move_pos['col']

		# Check for the double-three rule
		if self.count_double_three(row=row, col=col):
			self.board[row][col] = 0  # Remove the temporary stone
			return False  # The move is forbidden due to double-three

		return True  # The move is legal if no captures and not double-three

	def count_double_three(self, row: int, col: int):
		"""Check if the move creates a double-three configuration."""
		# row, col = move_pos['row'], move_pos['col']
		threats = 0
		player = self.current_player
		opponent = -player
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
			if self.analyze_sequence_for_threats(color_sequence, player, i_pos):
				print("Threat detected")
				threats += 1

			# Early exit if more than one threat is found (double-three condition)
			if threats >= 2:
				print("Double-three detected")
				return True
		
		return False

	def analyze_sequence_for_threats(self, sequence, player, middle_index):
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

	def is_win(self, row: int, col: int):
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

		# row, col = move_pos["row"], move_pos["col"]
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
					capture_possible, empty_pos = self._check_possible_capture()
					self.current_player = -self.current_player  # Rétablit le joueur actuel

					# Si une capture est possible, retourne une indication pour le coup spécial
					if capture_possible:
						return False, line, "play_special"

				# Si l'adversaire a moins de 8 pierres, vérifie si une capture est possible sur la ligne de 5
				self.current_player = -self.current_player
				capture_on_five, empty_pos = self._check_capture_on_five(line)
				# capture_on_five = self._check_possible_capture()
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

	def is_within_bounds(self, pos):
		"""Check if a position is within the board bounds."""
		return 0 <= pos[0] < self.board_size and 0 <= pos[1] < self.board_size

	def _check_capture_and_update(self, row, col):
		"""Check for captures and update the board."""
		directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
		is_captures = False
		# row, col = move_pos["row"], move_pos["col"]
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

	def _find_captures(self, condition_callback, line=None):
		"""
		Recherche des captures possibles sur le plateau en fonction d'une condition personnalisée.

		Args:
			condition_callback (function): Une fonction qui valide les motifs trouvés.
			line (list, optional): Une ligne de positions pour vérifier les intersections. Defaults à None.

		Returns:
			tuple: (bool, object) Indique si une capture est possible et retourne des informations associées.
		"""
		directions = [(0, 1), (1, 0), (1, 1), (1, -1)]  # Horizontal, vertical, diagonales
		opponent = -self.current_player
		player = self.current_player
		capture_patterns = []

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
							if all(self.is_within_bounds(pos) for pos in pattern):
								stones = [
									self.board[pattern[i][0], pattern[i][1]] for i in range(4)
								]
								# Appelle le callback pour valider le motif
								if condition_callback(stones, pattern):
									capture_patterns.append(pattern)

		if line:
			# Si une ligne est fournie, vérifie les intersections avec la ligne
			for pattern in capture_patterns:
				if pattern[1] in line or pattern[2] in line:
					return True, pattern[3]  # Retourne la position vide pour compléter la capture
			return False, None

		# Si aucune ligne n'est fournie, retourne le premier motif valide trouvé
		if capture_patterns:
			return True, capture_patterns[0][3]

		return False, None

	def _check_possible_capture(self):
		"""
		Vérifie si le joueur actuel peut potentiellement capturer une pierre sur tout le plateau.
		"""
		def validate_pattern(stones, pattern):
			return (
				stones[0] == self.current_player and
				stones[1] == -self.current_player and
				stones[2] == -self.current_player and
				stones[3] == PlayerToken.EMPTY.value
			)

		return self._find_captures(validate_pattern)

	def _check_capture_on_five(self, line):
		"""
		Vérifie si une capture est possible pour le joueur actuel et si elle intersecte une ligne de 5 pierres.
		"""
		def validate_pattern(stones, pattern):
			return (
				stones[0] == self.current_player and
				stones[1] == -self.current_player and
				stones[2] == -self.current_player and
				stones[3] == PlayerToken.EMPTY.value
			)

		return self._find_captures(validate_pattern, line=line)