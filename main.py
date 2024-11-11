import pygame
from src.game.gomoku import Gomoku
from src.game.playerTokens import PlayerToken

# Initialiser Pygame
pygame.init()

# Paramètres d'affichage
board_size = 19
cell_size = 40  # Augmenté pour avoir plus d'espace
screen_size = board_size * cell_size
border_size = 20
score_panel_width = 300
total_screen_width = screen_size + 2 * border_size + score_panel_width
total_screen_height = screen_size + 2 * border_size

screen = pygame.display.set_mode((total_screen_width, total_screen_height))
pygame.display.set_caption("Gomoku")

# Couleurs
BROWN_LIGHT = (205, 133, 63)
BROWN_DARK = (139, 69, 19)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
WINNER_COLOR = (255, 0, 0)

def draw_board(gomoku, winner=None):
    # Fond de l’écran
    screen.fill(BROWN_DARK)  # Bordure brune foncée

    # Plateau de jeu brun clair
    pygame.draw.rect(screen, BROWN_LIGHT, (border_size, border_size, screen_size, screen_size))

    # Dessiner la grille noire
    for x in range(board_size):
        pygame.draw.line(screen, BLACK, (border_size + x * cell_size, border_size), 
                         (border_size + x * cell_size, border_size + screen_size))
        pygame.draw.line(screen, BLACK, (border_size, border_size + x * cell_size), 
                         (border_size + screen_size, border_size + x * cell_size))

    # Placer les pierres aux intersections des lignes
    for row in range(board_size):
        for col in range(board_size):
            if gomoku.board[row, col] == PlayerToken.WHITE.value:
                pygame.draw.circle(screen, WHITE, (border_size + col * cell_size, border_size + row * cell_size), cell_size // 4)
            elif gomoku.board[row, col] == PlayerToken.BLACK.value:
                pygame.draw.circle(screen, BLACK, (border_size + col * cell_size, border_size + row * cell_size), cell_size // 4)

    # Affichage des scores et joueur suivant
    font = pygame.font.Font(None, 36)
    next_player = "Noir" if gomoku.current_player == PlayerToken.BLACK.value else "Blanc"
    black_score_text = font.render(f"Pions pris par Noir : {gomoku.black_player_pebbles_taken}", True, BLACK)
    white_score_text = font.render(f"Pions pris par Blanc : {gomoku.white_player_pebbles_taken}", True, BLACK)
    next_player_text = font.render(f"Prochain joueur : {next_player}", True, BLACK if gomoku.current_player == PlayerToken.BLACK.value else WHITE)
    
    # Afficher les textes sur le panneau latéral de score
    screen.blit(black_score_text, (screen_size + 2 * border_size, 50))
    screen.blit(white_score_text, (screen_size + 2 * border_size, 100))
    screen.blit(next_player_text, (screen_size + 2 * border_size, 150))

    # Si un joueur a gagné, afficher le message de victoire
    if winner:
        winner_text = font.render(f"Le joueur {winner} a gagné!", True, WINNER_COLOR)
        screen.blit(winner_text, (screen_size // 2 - 100, screen_size // 2))

def main():
    gomoku = Gomoku()
    running = True
    game_over = False
    winner = None

    while running:
        draw_board(gomoku, winner)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                x, y = event.pos

                # Vérifier que le clic est dans le plateau
                if border_size <= x < border_size + screen_size and border_size <= y < border_size + screen_size:
                    # Convertir les coordonnées du clic en indices de ligne et de colonne
                    col = round((x - border_size) / cell_size)
                    row = round((y - border_size) / cell_size)

                    # Vérifier que l'emplacement est libre
                    if gomoku.board[row, col] == PlayerToken.EMPTY.value:
                        # Appliquer la logique du jeu avec les règles
                        gomoku.board[row, col] = gomoku.current_player
                        if not gomoku.check_capture_and_update({"row": row, "col": col}):
                            if gomoku.is_move_forbidden({"row": row, "col": col}):
                                print("Coup interdit : double trois")
                                gomoku.board[row, col] = PlayerToken.EMPTY.value  # Annuler le coup
                                continue
                        
                        # Vérifier si le mouvement entraîne une victoire
                        if gomoku.is_win({"row": row, "col": col}):
                            winner = "Noir" if gomoku.current_player == PlayerToken.BLACK.value else "Blanc"
                            print(f"Le joueur {winner} a gagné!")
                            game_over = True
                        
                        # Changer de joueur si la partie n'est pas terminée
                        if not game_over:
                            gomoku.current_player = -gomoku.current_player

    pygame.quit()

if __name__ == "__main__":
    main()



# import numpy as np

# from src.game.gomoku import Gomoku
# # from src.game.playerTokens import PlayerToken

# from src.ui.render import plot_gomoku_board_interactive_with_player_info


# def main():
#     gomoku = Gomoku()

#     # Plot the interactive board with player move info
#     plot_gomoku_board_interactive_with_player_info(gomoku)


# if __name__ == "__main__":
#     main()