import matplotlib.pyplot as plt
import numpy as np
import random
from src.game.playerTokens import PlayerToken

import copy
import multiprocessing


def evaluate_move(args):
	"""
	Worker function that will be invoked in a separate process.
	It receives all necessary information to evaluate a single move.
	"""
	(row, col), depth, is_maximizing, gomoku_state = args
	
	# NOTE: We must recreate or clone the Gomoku board from gomoku_state
	gomoku_ai = GomokuAI(copy.deepcopy(gomoku_state))
	
	# Process the move. If invalid, return a sentinel value so we can ignore it.
	is_valid = gomoku_ai.gomoku.process_move(row, col)
	if not is_valid:
		return float('inf') if is_maximizing else float('-inf'), (row, col) #TODO CHECK THIS

	# NOTE We break the loop early if the game is over, this explain why we dont evaluate the move 
	if gomoku_ai.gomoku.game_over:
		return float('inf') if is_maximizing else float('-inf'), (row, col)

	# Evaluate or recurse:
	if depth == 1:
		# If we’re at leaf depth, evaluate the move directly
		score = gomoku_ai.get_score_for_position()
	else:
		# Otherwise, call minimax recursively
		next_is_maximizing = not is_maximizing
		score, _ = gomoku_ai.minimax(depth - 1, next_is_maximizing, is_first=False)

	return score, (row, col)

class GomokuAI:
	def __init__(self, gomoku, depth=3):
		"""
		Initialise l'IA pour Gomoku.
		:param gomoku: Instance de la classe Gomoku.
		:param depth: Profondeur de recherche pour Minimax (non utilisée ici).
		"""
		self.gomoku = gomoku.copy()
		self.depth = depth

	def reset(self, gomoku):
		"""
		Réinitialise les attributs de l'IA pour un nouveau jeu.
		:param gomoku: Nouvelle instance de la classe Gomoku.
		"""
		self.gomoku = gomoku
		self.depth = 3

	def random_move(self, player) -> tuple[int, int]:
		"""Génère un mouvement aléatoire parmi les coups valides."""
		moves = self.gomoku.get_all_possible_moves(player)
		if not moves:
			return None
		return random.choice(moves)

	def get_score_for_position(self) -> int:
		""""""
		#NOTE FOR ME, WHITE HAS A POSITIVE VALUE (AI), BLACK HAS A NEGATIVE VALUE (PLAYER)
		score = 0

		number_of_threat_white = self.gomoku._get_number_of_threats(PlayerToken.WHITE.value)
		number_of_threat_black = self.gomoku._get_number_of_threats(PlayerToken.BLACK.value)
		score = (number_of_threat_white - number_of_threat_black) / 3 * 10
	
		score += (self.gomoku.white_player_pebbles_taken - self.gomoku.black_player_pebbles_taken) * 10

		return score


	def minimax(self, depth: int, is_maximizing: bool, is_first: bool = True):
			"""
			Recursive Minimax that explores all possible moves up to the given depth
			and then picks the best move for the given 'player'.

			:param depth: Current search depth.
			:param is_maximizing: Boolean indicating if it is the maximizing player's turn.
			:return: (best_score, best_move)
			"""
			possible_moves = self.gomoku.getAllCloseMoves()  # List of (row, col)
			if self.gomoku.forced_moves:
				possible_moves = self.gomoku.forced_moves

			#TODO CHECK border case later on like board full or no move
			if not possible_moves:
				return 0, None

			# Prepare the argument list for each subprocess
			# We copy the current state of the Gomoku board/engine for each parallel call
			tasks = [((row, col), depth, is_maximizing, self.gomoku)
					for (row, col) in possible_moves]

			# Use a process pool to evaluate each move in parallel
			if is_first: #NOTE this avoid process creating children which is not possible
				with multiprocessing.Pool() as pool:
					results = pool.map(evaluate_move, tasks)
			else:
				results = [evaluate_move(task) for task in tasks]

			# `results` is now a list of (score, (row, col)) from each process
			if is_maximizing:
				# Find the maximum score and collect all moves that match it
				best_score = float('-inf')
				best_moves = []
				for score, move in results:
					if score > best_score:
						best_score = score
						best_moves = [move]
					elif score == best_score:
						best_moves.append(move)
			else:
				# Minimizing player
				best_score = float('inf')
				best_moves = []
				for score, move in results:
					if score < best_score:
						best_score = score
						best_moves = [move]
					elif score == best_score:
						best_moves.append(move)

			# Pick randomly among the best moves (if multiple have the same best score)
			best_move = random.choice(best_moves) if best_moves else None

			return best_score, best_move