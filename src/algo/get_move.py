import matplotlib
# import tkinter
# matplotlib.use('TkAgg')  # Use the TkAgg backend to prevent segmentation fault

import matplotlib.pyplot as plt
import numpy as np
import random
from src.game.playerTokens import PlayerToken


def get_all_possible_moves(gomoku):
	"""
	Get all possible moves for the current player based on the current game state.

	:param gomoku: Gomoku game instance.
	:return: List of all possible moves.
	"""

	possible_moves = []
	for row in range(19):
		for col in range(19):
			if gomoku.board[row, col] == PlayerToken.EMPTY.value:
				possible_moves.append((row, col))

	return possible_moves

def is_move_valid(gomoku, row, col):
	
	#copy the class
	gomoku_copy = gomoku.copy()
	
	gomoku_copy.board[row, col] = gomoku_copy.current_player
	if not gomoku_copy.check_capture_and_update({"row": row, "col": col}):
		forbidden, message = gomoku_copy.is_move_forbidden({"row": row, "col": col})
		if forbidden:
			print(f"Mouvement interdit ({row}, {col}) : {message}")
			return False

	return True

def get_random_move(gomoku):
	"""
	Get a random valid move for the current player.

	:param gomoku: Gomoku game instance.
	:return: Tuple (row, col) representing the move.
	"""
	# Récupérer tous les mouvements possibles
	possible_moves = get_all_possible_moves(gomoku)
	random.shuffle(possible_moves)  # Mélanger pour l'aléatoire

	# Parcourir les mouvements possibles
	for row, col in possible_moves:
		print(f"Test du mouvement ({row}, {col})")
		if is_move_valid(gomoku, row, col):
			print(f"Mouvement valide trouvé : ({row}, {col})")
			return row, col

	# Aucun mouvement valide trouvé
	print("Aucun mouvement valide n'a été trouvé.")
	return None