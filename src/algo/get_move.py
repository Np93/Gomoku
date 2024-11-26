import matplotlib
# import tkinter
# matplotlib.use('TkAgg')  # Use the TkAgg backend to prevent segmentation fault

import matplotlib.pyplot as plt
import numpy as np
import random
from src.game.playerTokens import PlayerToken
# from src.game.gomoku import Gomoku


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






class GomokuAI:
    def __init__(self, gomoku, depth=3):
        """
        Initialise l'IA pour Gomoku.
        :param gomoku: Instance de la classe Gomoku.
        :param depth: Profondeur de recherche pour Minimax.
        """
        self.gomoku = gomoku
        self.board_size = gomoku.board_size
        self.depth = depth
        self.DIRECTIONS = [(0, 1), (1, 0), (1, 1), (1, -1)]  # Horizontal, vertical, diagonales

    def reset(self, gomoku):
        """
        Réinitialise les attributs de l'IA pour un nouveau jeu.
        :param gomoku: Nouvelle instance de la classe Gomoku.
        """
        self.gomoku = gomoku
        self.board_size = gomoku.board_size
        self.depth = 3

    @staticmethod
    def is_move_valid(gomoku, row, col):
        """Vérifie si un mouvement est valide selon les règles de Gomoku."""
        # Vérifier que la case est vide
        if gomoku.board[row, col] != 0:
            print(f"Case non vide : ({row}, {col})")
            return False

        # Créer une copie pour simuler le mouvement
        gomoku_copy = gomoku.copy()
        gomoku_copy.board[row, col] = gomoku_copy.current_player

        # Vérifier les captures et les mouvements interdits
        if not gomoku_copy.check_capture_and_update({"row": row, "col": col}):
            forbidden, message = gomoku_copy.is_move_forbidden({"row": row, "col": col})
            if forbidden:
                print(f"Mouvement interdit ({row}, {col}) : {message}")
                return False

        return True

    def generate_priority_moves(self, player):
        """Génère une liste de coups prioritaires."""
        print(f"--- Génération des coups pour le joueur {player} ---")
        opponent = -player
        priority_moves = {"four_block": [], "capture_on_five": [], "three_block": [], 
                        "protect_two": [], "capture": [], "two_block": [], "random": []}

        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.gomoku.board[row, col] != 0 or not self.is_move_valid(self.gomoku, row, col):
                    continue

                # Vérifier les alignements et priorités
                for dr, dc in self.DIRECTIONS:
                    count = 1
                    line_coordinates = [(row, col)]  # Inclure la position actuelle
                    # Vérifier dans une direction
                    for i in range(1, 5):
                        r, c = row + dr * i, col + dc * i
                        if 0 <= r < self.board_size and 0 <= c < self.board_size:
                            if self.gomoku.board[r, c] == opponent:
                                count += 1
                                line_coordinates.append((r, c))
                            else:
                                break
                    # Vérifier dans l'autre direction
                    for i in range(1, 5):
                        r, c = row - dr * i, col - dc * i
                        if 0 <= r < self.board_size and 0 <= c < self.board_size:
                            if self.gomoku.board[r, c] == opponent:
                                count += 1
                                line_coordinates.append((r, c))
                            else:
                                break

                    # Priorité 1 : Bloquer une ligne de 4 adverse
                    if count == 4:
                        print(f"Blocage d'une ligne de 4 adverse à ({row}, {col})")
                        return [(row, col)]

                    # Si une ligne de 5 est détectée, vérifier la possibilité de capture
                    if count >= 5 and len(line_coordinates) >= 5:
                        line_coordinates = line_coordinates[:5]  # Garder uniquement 5 points
                        capture_possible, capture_coords = self.gomoku.check_capture_on_five(line_coordinates)
                        if capture_possible:
                            print(f"Capture sur une ligne de 5 détectée : {line_coordinates}")
                            # Ajouter le coup de capture aux priorités
                            if capture_coords:
                                priority_moves["capture_on_five"].append(capture_coords)
                                return [capture_coords]

                    # # Priorité 5 : Bloquer une ligne de 3 adverse
                    # if count == 3:
                    #     priority_moves["three_block"].append((row, col))

                    # Priorité 3 : Protéger une ligne de 2 de l'IA
                    original_player = self.gomoku.current_player
                    self.gomoku.current_player = -self.gomoku.current_player
                    capture_possible, capture_coords = self.gomoku.check_possible_capture()  # Récupère le booléen et les coordonnées
                    self.gomoku.current_player = original_player
                    if capture_possible:
                        priority_moves["protect_two"].append(capture_coords)

                    # Priorité 4 : Capture possible
                    capture_possible, capture_coords = self.gomoku.check_possible_capture()  # Réutilisation pour une capture générique
                    if capture_possible:
                        priority_moves["capture"].append(capture_coords)

                    # Priorité 3 : Bloquer une ligne de 3 adverse
                    if count == 3:
                        priority_moves["three_block"].append((row, col))

        # Jouer autour des pions adverses
        random_move = self.generate_random_moves_around_opponent(opponent)
        if random_move:
            priority_moves["random"].extend(random_move)

        # Retourner les coups prioritaires par ordre
        for key in ["protect_two", "capture", "three_block", "random"]:
            if priority_moves[key]:
                print(f"Coups {key} : {priority_moves[key]}")
                return priority_moves[key]

        print("Aucun coup prioritaire trouvé.")
        return []

    def generate_random_moves_around_opponent(self, opponent):
        """Génère un mouvement aléatoire autour des pions adverses."""
        possible_moves = []

        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.gomoku.board[row, col] == opponent:
                    for dr, dc in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
                        nx, ny = row + dr, col + dc
                        if 0 <= nx < self.board_size and 0 <= ny < self.board_size and self.is_move_valid(self.gomoku, nx, ny):
                            possible_moves.append((nx, ny))

        if not possible_moves:
            print("Aucun mouvement possible autour des adversaires.")
            return []

        print(f"Mouvements aléatoires générés autour des adversaires : {possible_moves}")
        return [random.choice(possible_moves)]

    def minimax(self, depth, is_maximizing, alpha, beta, player):
        """Minimax avec coupure Alpha-Beta."""
        if depth == 0 or self.gomoku.game_over:
            score = self.evaluate_board(player)
            print(f"Évaluation du plateau à profondeur 0 : {score}")
            return score

        moves = self.generate_priority_moves(player)
        if is_maximizing:
            max_eval = float('-inf')
            for row, col in moves:
                gomoku_copy = self.gomoku.copy()
                gomoku_copy.board[row, col] = player
                gomoku_copy.check_capture_and_update({"row": row, "col": col})

                eval = self.minimax(depth - 1, False, alpha, beta, player)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for row, col in moves:
                gomoku_copy = self.gomoku.copy()
                gomoku_copy.board[row, col] = -player
                gomoku_copy.check_capture_and_update({"row": row, "col": col})

                eval = self.minimax(depth - 1, True, alpha, beta, player)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def find_best_move(self, player):
        """Trouve le meilleur coup pour le joueur."""
        print(f"--- Recherche du meilleur coup pour le joueur {player} ---")
        moves = self.generate_priority_moves(player)

        if len(moves) == 1:
            print(f"Coup critique joué immédiatement : {moves[0]}")
            return moves[0]

        best_score = float('-inf')
        best_move = None

        for row, col in moves:
            gomoku_copy = self.gomoku.copy()
            gomoku_copy.board[row, col] = player
            gomoku_copy.check_capture_and_update({"row": row, "col": col})

            score = self.minimax(self.depth - 1, False, float('-inf'), float('inf'), player)
            print(f"Score pour le mouvement ({row}, {col}) : {score}")

            if score > best_score:
                best_score = score
                best_move = (row, col)

        print(f"Meilleur coup trouvé : {best_move} avec un score de {best_score}")
        return best_move

    def evaluate_board(self, player):
        """Évalue le plateau pour un joueur donné en incluant l'adversaire."""
        opponent = -player

        def calculate_alignment_score(player_or_opponent):
            """Calcule le score pour un joueur spécifique basé sur ses alignements."""
            score = 0
            for row in range(self.board_size):
                for col in range(self.board_size):
                    if self.gomoku.board[row, col] == player_or_opponent:
                        for dr, dc in self.DIRECTIONS:
                            count = 1
                            for direction in [1, -1]:  # Parcourir dans les deux directions
                                for i in range(1, 5):
                                    r, c = row + direction * dr * i, col + direction * dc * i
                                    if 0 <= r < self.board_size and 0 <= c < self.board_size:
                                        if self.gomoku.board[r, c] == player_or_opponent:
                                            count += 1
                                        else:
                                            break
                                    else:
                                        break
                            # Ajouter le score en fonction de l'alignement détecté
                            if count >= 5:
                                score += 100000
                            elif count == 4:
                                score += 5000
                            elif count == 3:
                                score += 300
                            elif count == 2:
                                score += 100
            return score

        # Calcul des scores pour le joueur actuel et l'adversaire
        player_score = calculate_alignment_score(player)
        opponent_score = calculate_alignment_score(opponent)

        # Ajouter les scores liés aux captures
        player_score += (
            self.gomoku.black_player_pebbles_taken * 200 
            if player == PlayerToken.BLACK.value 
            else self.gomoku.white_player_pebbles_taken * 200
        )
        opponent_score += (
            self.gomoku.black_player_pebbles_taken * 200 
            if opponent == PlayerToken.BLACK.value 
            else self.gomoku.white_player_pebbles_taken * 200
        )

        # Retourner la différence entre les scores
        return player_score - opponent_score