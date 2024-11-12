import pygame
from src.game.gomoku import Gomoku
from src.game.playerTokens import PlayerToken

# Initialize Pygame
pygame.init()

# Display settings
board_size = 19
cell_size = 40  # Size of the board cells
screen_size = board_size * cell_size
border_size = cell_size  # Border set to the size of one cell
score_panel_width = 350  # Width of the score panel
total_screen_width = screen_size + 2 * border_size + score_panel_width
total_screen_height = screen_size + 2 * border_size

screen = pygame.display.set_mode((total_screen_width, total_screen_height))
pygame.display.set_caption("Gomoku")

# Colors
BORDER_COLOR = (139, 69, 19)  # Darker brown for the border
BOARD_COLOR = (205, 133, 63)  # Light brown for the board
GRID_COLOR = (0, 0, 0)        # Color for the grid lines
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
TEXT_COLOR = (0, 0, 0)        # Color for the text
WINNER_COLOR = (255, 0, 0)

# Stone size (based on cell_size)
pion_radius = cell_size // 2.5  # Adjusted size for larger stones

def draw_board(gomoku, winner=None):
    # Fill the background with the border color (dark brown)
    screen.fill(BORDER_COLOR)

    # Draw the board area with a light brown color
    pygame.draw.rect(screen, BOARD_COLOR, (border_size, border_size, screen_size, screen_size))

    # Define the start and end of the grid inside the board, leaving a margin for the border
    grid_start = border_size + cell_size // 2
    grid_end = border_size + screen_size - cell_size // 2

    # Draw the 19x19 black grid within the light brown board area
    for x in range(board_size):
        x_pos = grid_start + x * cell_size
        pygame.draw.line(screen, GRID_COLOR, (x_pos, grid_start), (x_pos, grid_end))
    for y in range(board_size):
        y_pos = grid_start + y * cell_size
        pygame.draw.line(screen, GRID_COLOR, (grid_start, y_pos), (grid_end, y_pos))

    # Place stones on the intersections of the lines
    for row in range(board_size):
        for col in range(board_size):
            if gomoku.board[row, col] == PlayerToken.WHITE.value:
                pygame.draw.circle(screen, WHITE,
                                   (grid_start + col * cell_size, grid_start + row * cell_size), int(pion_radius))
            elif gomoku.board[row, col] == PlayerToken.BLACK.value:
                pygame.draw.circle(screen, BLACK,
                                   (grid_start + col * cell_size, grid_start + row * cell_size), int(pion_radius))

    # Display scores and next player
    font = pygame.font.Font(None, 32)  # Adjust font size if necessary
    next_player = "Noir" if gomoku.current_player == PlayerToken.BLACK.value else "Blanc"
    black_score_text = font.render(f"Pions pris par Noir : {gomoku.black_player_pebbles_taken}", True, TEXT_COLOR)
    white_score_text = font.render(f"Pions pris par Blanc : {gomoku.white_player_pebbles_taken}", True, TEXT_COLOR)
    next_player_text = font.render(f"Prochain joueur : {next_player}", True, BLACK if gomoku.current_player == PlayerToken.BLACK.value else WHITE)

    # Position text in the score panel
    text_x = screen_size + 2 * border_size
    screen.blit(black_score_text, (text_x, 50))
    screen.blit(white_score_text, (text_x, 100))
    screen.blit(next_player_text, (text_x, 150))

    # If a player has won, display the victory message
    if winner:
        winner_text = font.render(f"Le Joueur {winner} a gagné !", True, WINNER_COLOR)
        # Center the text on the game area
        text_rect = winner_text.get_rect(center=(border_size + screen_size // 2, border_size + screen_size // 2))
        screen.blit(winner_text, text_rect)

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

                # Check if the click is within the grid area
                grid_start = border_size + cell_size // 2
                grid_end = border_size + screen_size - cell_size // 2

                if grid_start <= x <= grid_end and grid_start <= y <= grid_end:
                    # Calculate the nearest grid intersection
                    col = int(round((x - grid_start) / cell_size))
                    row = int(round((y - grid_start) / cell_size))

                    # Ensure indices are within bounds
                    if 0 <= row < board_size and 0 <= col < board_size:
                        # Check if the spot is available
                        if gomoku.board[row, col] == PlayerToken.EMPTY.value:
                            # Apply game logic with rules
                            gomoku.board[row, col] = gomoku.current_player
                            if not gomoku.check_capture_and_update({"row": row, "col": col}):
                                if gomoku.is_move_forbidden({"row": row, "col": col}):
                                    print("Coup interdit : double trois")
                                    gomoku.board[row, col] = PlayerToken.EMPTY.value  # Undo the move
                                    continue

                            # Check if the move results in a win
                            if gomoku.is_win({"row": row, "col": col}):
                                winner = "Noir" if gomoku.current_player == PlayerToken.BLACK.value else "Blanc"
                                print(f"{winner} a gagné !")
                                game_over = True

                            # Switch player if the game is not over
                            if not game_over:
                                gomoku.current_player = -gomoku.current_player

    pygame.quit()

if __name__ == "__main__":
    main()