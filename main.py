import pygame
from src.game.gomoku import Gomoku
from src.game.playerTokens import PlayerToken

# Initialize Pygame
pygame.init()

# Display settings
board_size = 19
cell_size = 40  # Size of the board cells
screen_size = board_size * cell_size
border_size = 20
score_panel_width = 300  # Width of the score panel
total_screen_width = screen_size + 2 * border_size + score_panel_width
total_screen_height = screen_size + 2 * border_size

screen = pygame.display.set_mode((total_screen_width, total_screen_height))
pygame.display.set_caption("Gomoku")

# Colors
BROWN_LIGHT = (205, 133, 63)
BROWN_DARK = (139, 69, 19)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
WINNER_COLOR = (255, 0, 0)

# Stone size (based on cell_size)
pion_radius = cell_size // 2.5  # Increased for larger stones

def draw_board(gomoku, winner=None):
    # Screen background
    screen.fill(BROWN_DARK)  # Dark brown border

    # Light brown game board
    pygame.draw.rect(screen, BROWN_LIGHT, (border_size, border_size, screen_size, screen_size))

    # Draw black grid
    for x in range(board_size):
        pygame.draw.line(screen, BLACK, (border_size + x * cell_size, border_size), 
                         (border_size + x * cell_size, border_size + screen_size))
        pygame.draw.line(screen, BLACK, (border_size, border_size + x * cell_size), 
                         (border_size + screen_size, border_size + x * cell_size))

    # Place stones on the intersections of the lines
    for row in range(board_size):
        for col in range(board_size):
            if gomoku.board[row, col] == PlayerToken.WHITE.value:
                pygame.draw.circle(screen, WHITE, (border_size + col * cell_size, border_size + row * cell_size), pion_radius)
            elif gomoku.board[row, col] == PlayerToken.BLACK.value:
                pygame.draw.circle(screen, BLACK, (border_size + col * cell_size, border_size + row * cell_size), pion_radius)

    # Display scores and next player
    font = pygame.font.Font(None, 36)
    next_player = "Black" if gomoku.current_player == PlayerToken.BLACK.value else "White"
    black_score_text = font.render(f"Black player stones taken: {gomoku.black_player_pebbles_taken}", True, BLACK)
    white_score_text = font.render(f"White player stones taken: {gomoku.white_player_pebbles_taken}", True, BLACK)
    next_player_text = font.render(f"Next player: {next_player}", True, BLACK if gomoku.current_player == PlayerToken.BLACK.value else WHITE)
    
    # Display text on the score panel
    screen.blit(black_score_text, (screen_size + 2 * border_size, 50))
    screen.blit(white_score_text, (screen_size + 2 * border_size, 100))
    screen.blit(next_player_text, (screen_size + 2 * border_size, 150))

    # If a player has won, display the victory message
    if winner:
        winner_text = font.render(f"The player{winner} has won!", True, WINNER_COLOR)
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

                # Check if the click is within the board
                if border_size <= x < border_size + screen_size and border_size <= y < border_size + screen_size:
                    # Convert click coordinates to row and column indices
                    col = round((x - border_size) / cell_size)
                    row = round((y - border_size) / cell_size)

                    # Check if the spot is available
                    if gomoku.board[row, col] == PlayerToken.EMPTY.value:
                        # Apply game logic with rules
                        gomoku.board[row, col] = gomoku.current_player
                        if not gomoku.check_capture_and_update({"row": row, "col": col}):
                            if gomoku.is_move_forbidden({"row": row, "col": col}):
                                print("Forbidden move: double three")
                                gomoku.board[row, col] = PlayerToken.EMPTY.value  # Undo the move
                                continue
                        
                        # Check if the move results in a win
                        if gomoku.is_win({"row": row, "col": col}):
                            winner = "Black" if gomoku.current_player == PlayerToken.BLACK.value else "White"
                            print(f"{winner} has won!")
                            game_over = True
                        
                        # Switch player if the game is not over
                        if not game_over:
                            gomoku.current_player = -gomoku.current_player

    pygame.quit()

if __name__ == "__main__":
    main()