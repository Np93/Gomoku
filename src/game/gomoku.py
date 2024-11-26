
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

	def is_move_forbidden(self, move_pos):
		"""Check if the move is forbidden based on Gomoku rules."""
		row, col = move_pos['row'], move_pos['col']

		# Check for the double-three rule
		if self.count_double_three(move_pos):
			self.board[row][col] = 0  # Remove the temporary stone
			return True, "règle du double-trois"  # The move is forbidden due to double-three

		if self.check_forbidden_pattern(move_pos):
			self.board[row][col] = 0
			return True, "capture automatique"

		return False, "Mouvement autorisé"  # The move is legal if no captures and not double-three

	def check_forbidden_pattern(self, move_pos):
		"""
		Vérifie si le mouvement proposé crée une configuration interdite 
		(adversaire, joueur, vide, adversaire).

		Args:
			move_pos (dict): Position du mouvement proposé sous la forme {'row': int, 'col': int}.

		Returns:
			bool: True si le mouvement crée une configuration interdite, False sinon.
		"""
		row, col = move_pos['row'], move_pos['col']
		opponent = -self.current_player  # Token de l'adversaire
		player = self.current_player  # Token du joueur actuel
		
		# Directions : horizontale, verticale et diagonales
		directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

		for dr, dc in directions:
			for sign in [1, -1]:  # Vérifie dans les deux sens
				# Crée le motif (adversaire, joueur, vide, adversaire)
				pattern_positions = [
					(row + sign * dr * i, col + sign * dc * i) for i in range(-2, 2)
				]

				# Vérifie que toutes les positions sont dans les limites
				if all(self.is_within_bounds(pos) for pos in pattern_positions):
					stones = [
						self.board[pattern_positions[i][0], pattern_positions[i][1]]
						for i in range(4)
					]

					# Vérifie si le motif interdit est détecté
					if (
						stones[0] == opponent and
						stones[1] == player and
						stones[2] == player and  # Case vide où le joueur veut jouer
						stones[3] == opponent
					):
						return True

		return False

	def count_double_three(self, move_pos):
		"""Check if the move creates a double-three configuration."""
		row, col = move_pos['row'], move_pos['col']
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
				# capture_on_five = self.check_possible_capture()
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

	def can_opponent_capture(self, line, opponent, player):
		"""Check if the opponent can capture stones around any stone in the line."""
		board_size = self.board_size
		board = self.board
		directions = [(0, 1), (1, 0), (1, 1), (-1, 1)]  # horizontal, vertical, diagonal right, diagonal left

		forced_moves = []


		for stone in line:
			row, col = stone

			for dr, dc in directions:
				backward_stone = (row - dr, col - dc)
				forward_stone = (row + 1 * dr, col + 1 * dc)
				forward_stone2 = (row + 2 * dr, col + 2 * dc)
	
				op_forward_stone = (row + dr, col + dc)
				op_backward_stone = (row - 1 * dr, col - 1 * dc)
				op_backward_stone2 = (row - 2 * dr, col - 2 * dc)
	
				#check for pattern 0xx0
				if self.is_within_bounds(forward_stone) and self.is_within_bounds(forward_stone2) and self.is_within_bounds(backward_stone) and self.is_within_bounds(op_backward_stone):
					if board[backward_stone] == opponent and board[row, col] == player and board[forward_stone] == player and board[forward_stone2] == PlayerToken.EMPTY.value:
						forced_moves.append(forward_stone2)
					if board[backward_stone] == PlayerToken.EMPTY.value and board[row, col] == player and board[forward_stone] == player and board[forward_stone2] == opponent:
						forced_moves.append(backward_stone)
					if board[op_backward_stone] == opponent and board[row, col] == player and board[forward_stone] == player and board[forward_stone2] == PlayerToken.EMPTY.value:
						forced_moves.append(forward_stone2)
					if board[op_backward_stone] == PlayerToken.EMPTY.value and board[row, col] == player and board[forward_stone] == player and board[forward_stone2] == opponent:
						forced_moves.append(op_backward_stone)

		if len(forced_moves) > 0:
			#remove duplicates
			forced_moves = list(set(forced_moves))
			self.forced_moves = forced_moves
			print(self.forced_moves)
			return True

		return False

	def is_within_bounds(self, pos):
		"""Check if a position is within the board bounds."""
		return 0 <= pos[0] < self.board_size and 0 <= pos[1] < self.board_size

	def check_capture_and_update(self, move_pos):
		"""Check for captures and update the board."""
		directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
		is_captures = False
		row, col = move_pos["row"], move_pos["col"]
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
							if all(self.is_within_bounds(pos) for pos in pattern):
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
							if all(self.is_within_bounds(pos) for pos in pattern):
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
		return False, None