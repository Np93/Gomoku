import pygame
from src.game.gomoku import Gomoku
from src.game.playerTokens import PlayerToken
import time

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
BUTTON_COLOR = (70, 130, 180) # Color for buttons in the menu
BUTTON_HOVER_COLOR = (100, 149, 237) # Hover color for buttons
QUIT_BUTTON_COLOR = (220, 20, 60)    # Color for the quit button

# Stone size (based on cell_size)
pion_radius = cell_size // 2.5  # Adjusted size for larger stones

# Timing settings for displaying messages
message_start_time = None
message_duration = 5  # Duration in seconds

# Global variable to control game exit
exit_game = False

def draw_forbidden_message(message):
    """Draw the forbidden move message in the side panel."""
    font = pygame.font.Font(None, 32)
    text_surface = font.render(message, True, WINNER_COLOR)
    message_x = screen_size + 2 * border_size  # Position in the side panel
    message_y = 200  # Position below the next player text
    screen.blit(text_surface, (message_x, message_y))

def main_menu():
    """Display the main menu and handle user interaction."""
    font = pygame.font.Font(None, 60)
    small_font = pygame.font.Font(None, 40)
    
    # Position and size for the round "Quitter" button
    quit_button_radius = 40
    quit_button_center = (total_screen_width - quit_button_radius - 30, total_screen_height - quit_button_radius - 30)
    
    while True:
        screen.fill(BORDER_COLOR)
        
        # Title text
        title_text = font.render("Gomoku", True, WHITE)
        screen.blit(title_text, (total_screen_width // 2 - title_text.get_width() // 2, 100))
        
        # Define button rectangles for "Partie normale" and "Partie spéciale"
        normal_button = pygame.Rect(total_screen_width // 2 - 100, 300, 200, 50)
        special_button = pygame.Rect(total_screen_width // 2 - 100, 400, 200, 50)
        
        # Button text
        normal_text = small_font.render("Partie normale", True, WHITE)
        special_text = small_font.render("Partie spéciale", True, WHITE)
        
        # Draw buttons and detect hover
        mouse_pos = pygame.mouse.get_pos()
        
        # Draw the "Partie normale" button
        if normal_button.collidepoint(mouse_pos):
            pygame.draw.rect(screen, BUTTON_HOVER_COLOR, normal_button)
        else:
            pygame.draw.rect(screen, BUTTON_COLOR, normal_button)
        screen.blit(normal_text, (normal_button.centerx - normal_text.get_width() // 2, normal_button.centery - normal_text.get_height() // 2))
        
        # Draw the "Partie spéciale" button
        if special_button.collidepoint(mouse_pos):
            pygame.draw.rect(screen, BUTTON_HOVER_COLOR, special_button)
        else:
            pygame.draw.rect(screen, BUTTON_COLOR, special_button)
        screen.blit(special_text, (special_button.centerx - special_text.get_width() // 2, special_button.centery - special_text.get_height() // 2))
        
        # Draw the round "Quitter" button
        pygame.draw.circle(screen, QUIT_BUTTON_COLOR, quit_button_center, quit_button_radius)
        
        # Text for "Quitter" inside the round button
        quit_text = pygame.font.Font(None, 30).render("Quitter", True, WHITE)
        screen.blit(quit_text, (quit_button_center[0] - quit_text.get_width() // 2, quit_button_center[1] - quit_text.get_height() // 2))
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if normal_button.collidepoint(mouse_pos):
                    return "normal"
                elif special_button.collidepoint(mouse_pos):
                    return "special"
                elif (mouse_pos[0] - quit_button_center[0]) ** 2 + (mouse_pos[1] - quit_button_center[1]) ** 2 <= quit_button_radius ** 2:
                    pygame.quit()
                    quit()

        pygame.display.flip()
        if exit_game:
            pygame.quit()
            quit()

def end_game_menu(winner):
    """Display the end game menu with options to replay, return to menu, or quit."""
    font = pygame.font.Font(None, 60)
    small_font = pygame.font.Font(None, 40)
    
    # Position and size for the round "Quitter" button in the end game menu
    quit_button_radius = 40
    quit_button_center = (total_screen_width - quit_button_radius - 30, total_screen_height - quit_button_radius - 30)
    
    while True:
        screen.fill(BORDER_COLOR)
        
        # Display the winner text
        winner_text = font.render(f"Le Joueur {winner} a gagné !", True, WINNER_COLOR)
        screen.blit(winner_text, (total_screen_width // 2 - winner_text.get_width() // 2, 100))
        
        # Define button rectangles for "Rejouer" and "Retour au menu"
        replay_button = pygame.Rect(total_screen_width // 2 - 100, 300, 200, 50)
        menu_button = pygame.Rect(total_screen_width // 2 - 110, 400, 220, 50)  # Widened button
        
        # Button text
        replay_text = small_font.render("Rejouer", True, WHITE)
        menu_text = small_font.render("Retour au menu", True, WHITE)
        
        # Draw buttons and detect hover
        mouse_pos = pygame.mouse.get_pos()
        
        # Draw the "Rejouer" button
        if replay_button.collidepoint(mouse_pos):
            pygame.draw.rect(screen, BUTTON_HOVER_COLOR, replay_button)
        else:
            pygame.draw.rect(screen, BUTTON_COLOR, replay_button)
        screen.blit(replay_text, (replay_button.centerx - replay_text.get_width() // 2, replay_button.centery - replay_text.get_height() // 2))
        
        # Draw the "Retour au menu" button
        if menu_button.collidepoint(mouse_pos):
            pygame.draw.rect(screen, BUTTON_HOVER_COLOR, menu_button)
        else:
            pygame.draw.rect(screen, BUTTON_COLOR, menu_button)
        screen.blit(menu_text, (menu_button.centerx - menu_text.get_width() // 2, menu_button.centery - menu_text.get_height() // 2))
        
        # Draw the round "Quitter" button
        pygame.draw.circle(screen, QUIT_BUTTON_COLOR, quit_button_center, quit_button_radius)
        
        # Text for "Quitter" inside the round button
        quit_text = pygame.font.Font(None, 30).render("Quitter", True, WHITE)
        screen.blit(quit_text, (quit_button_center[0] - quit_text.get_width() // 2, quit_button_center[1] - quit_text.get_height() // 2))
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if replay_button.collidepoint(mouse_pos):
                    return "replay"
                elif menu_button.collidepoint(mouse_pos):
                    return "menu"
                elif (mouse_pos[0] - quit_button_center[0]) ** 2 + (mouse_pos[1] - quit_button_center[1]) ** 2 <= quit_button_radius ** 2:
                    pygame.quit()
                    quit()

        pygame.display.flip()
        if exit_game:
            pygame.quit()
            quit()

def draw_board(gomoku, winner=None, forbidden_message=None):
    """Draw the Gomoku board and display game information."""
    screen.fill(BORDER_COLOR)
    pygame.draw.rect(screen, BOARD_COLOR, (border_size, border_size, screen_size, screen_size))

    grid_start = border_size + cell_size // 2
    grid_end = border_size + screen_size - cell_size // 2

    for x in range(board_size):
        x_pos = grid_start + x * cell_size
        pygame.draw.line(screen, GRID_COLOR, (x_pos, grid_start), (x_pos, grid_end))
    for y in range(board_size):
        y_pos = grid_start + y * cell_size
        pygame.draw.line(screen, GRID_COLOR, (grid_start, y_pos), (grid_end, y_pos))

    for row in range(board_size):
        for col in range(board_size):
            if gomoku.board[row, col] == PlayerToken.WHITE.value:
                pygame.draw.circle(screen, WHITE, (grid_start + col * cell_size, grid_start + row * cell_size), int(pion_radius))
            elif gomoku.board[row, col] == PlayerToken.BLACK.value:
                pygame.draw.circle(screen, BLACK, (grid_start + col * cell_size, grid_start + row * cell_size), int(pion_radius))

    font = pygame.font.Font(None, 32)
    next_player = "Noir" if gomoku.current_player == PlayerToken.BLACK.value else "Blanc"
    black_score_text = font.render(f"Pions pris par Noir : {gomoku.black_player_pebbles_taken}", True, TEXT_COLOR)
    white_score_text = font.render(f"Pions pris par Blanc : {gomoku.white_player_pebbles_taken}", True, TEXT_COLOR)
    next_player_text = font.render(f"Prochain joueur : {next_player}", True, BLACK if gomoku.current_player == PlayerToken.BLACK.value else WHITE)

    text_x = screen_size + 2 * border_size
    screen.blit(black_score_text, (text_x, 50))
    screen.blit(white_score_text, (text_x, 100))
    screen.blit(next_player_text, (text_x, 150))

    # Display the forbidden message if it exists
    if forbidden_message:
        draw_forbidden_message(forbidden_message)

    if winner:
        winner_text = font.render(f"Le Joueur {winner} a gagné !", True, WINNER_COLOR)
        text_rect = winner_text.get_rect(center=(border_size + screen_size // 2, border_size + screen_size // 2))
        screen.blit(winner_text, text_rect)

def render_game_ui():
    global message_start_time, exit_game
    forbidden_message = None

    while not exit_game:
        game_mode = main_menu()
        
        if game_mode == "normal" and not exit_game:
            gomoku = Gomoku()
            running = True
            game_over = False
            winner = None

            while running and not exit_game:
                draw_board(gomoku, winner, forbidden_message)
                
                if forbidden_message and time.time() - message_start_time < message_duration:
                    draw_forbidden_message(forbidden_message)
                elif forbidden_message and time.time() - message_start_time >= message_duration:
                    forbidden_message = None
                
                pygame.display.flip()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        exit_game = True
                    elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                        x, y = event.pos
                        grid_start = border_size + cell_size // 2
                        grid_end = border_size + screen_size - cell_size // 2

                        if grid_start <= x <= grid_end and grid_start <= y <= grid_end:
                            col = int(round((x - grid_start) / cell_size))
                            row = int(round((y - grid_start) / cell_size))

                            if 0 <= row < board_size and 0 <= col < board_size:
                                if gomoku.board[row, col] == PlayerToken.EMPTY.value:
                                    gomoku.board[row, col] = gomoku.current_player
                                    if not gomoku.check_capture_and_update({"row": row, "col": col}):
                                        forbidden = gomoku.is_move_forbidden({"row": row, "col": col})
                                        if forbidden:
                                            forbidden_message = f"Mouvement interdit : ({col}, {row})"
                                            message_start_time = time.time()
                                            gomoku.board[row, col] = PlayerToken.EMPTY.value
                                            continue

                                    if gomoku.is_win({"row": row, "col": col}):
                                        winner = "Noir" if gomoku.current_player == PlayerToken.BLACK.value else "Blanc"
                                        game_over = True

                                    if not game_over:
                                        gomoku.current_player = -gomoku.current_player

                if game_over and not exit_game:
                    action = end_game_menu(winner)
                    if action == "replay":
                        gomoku = Gomoku()
                        game_over = False
                        winner = None
                    elif action == "menu":
                        break

        if exit_game:
            pygame.quit()
            quit()