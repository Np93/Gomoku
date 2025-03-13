import pygame
import time
import random

# Instead of importing Python Gomoku, import the C++-bound class:
# from src.game._gomoku import Gomoku
# from src.algo.algo import GomokuAI
from cpp_gomoku import Gomoku, GomokuAI

from src.game.playerTokens import PlayerToken


# Initialize Pygame
pygame.init()

# We can ask for the board size from the C++ Gomoku if you want dynamic sizing.
# Or just keep it as 19 if your C++ also defaults to 19.
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
GRAY = (169, 169, 169)
TEXT_COLOR = (0, 0, 0)        # Color for the text
WINNER_COLOR = (255, 0, 0)
BUTTON_COLOR = (70, 130, 180) # Color for buttons in the menu
BUTTON_HOVER_COLOR = (100, 149, 237) # Hover color for buttons
QUIT_BUTTON_COLOR = (220, 20, 60)    # Color for the quit button
QUIT_BUTTON_HOVER_COLOR = (255, 69, 0)

# Stone size (based on cell_size)
pion_radius = cell_size // 2.5  # Adjusted size for larger stones

# Timing settings for displaying messages
message_start_time = None
message_duration = 5  # Duration in seconds

# Global variable to control game exit
exit_game = False

# Temps pour chaque joueur
player_times = {
    PlayerToken.BLACK.value: {"total_time": 0, "last_time": 0},
    PlayerToken.WHITE.value: {"total_time": 0, "last_time": 0}
}
turn_start_time = None

ai_process_time = 0

def draw_forbidden_message(message):
    """
    Dessine le message de mouvement interdit dans le panneau latéral,
    en découpant le texte si nécessaire pour éviter qu'il dépasse les limites.
    """
    font = pygame.font.Font(None, 32)
    max_width = score_panel_width - 20  # Largeur maximale pour le texte (ajustée pour laisser une marge)
    words = message.split()  # Découpe le texte en mots
    lines = []
    current_line = ""

    # Découpe le texte en lignes en fonction de la largeur maximale
    for word in words:
        test_line = f"{current_line} {word}".strip()
        text_width, _ = font.size(test_line)
        if text_width <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)

    # Dessine chaque ligne
    message_x = screen_size + 2 * border_size  # Position dans le panneau latéral
    message_y = 350  # Position de départ pour le message
    line_spacing = 35  # Espacement entre les lignes

    for line in lines:
        text_surface = font.render(line, True, WINNER_COLOR)
        screen.blit(text_surface, (message_x, message_y))
        message_y += line_spacing

def draw_button(screen, button_rect, text, font, mouse_pos, button_color, hover_color, text_color, outline_color=None):
    """Draw a button with hover effect, text, and optional outline."""
    if button_rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, hover_color, button_rect)  # Change color on hover
        if outline_color:  # Optional outline effect
            pygame.draw.rect(screen, outline_color, button_rect, 3)  # Draw outline with thickness 3
    else:
        pygame.draw.rect(screen, button_color, button_rect)  # Default color
    text_surface = font.render(text, True, text_color)
    screen.blit(
        text_surface, 
        (button_rect.centerx - text_surface.get_width() // 2,
         button_rect.centery - text_surface.get_height() // 2)
    )

def draw_quit_button(screen, quit_center, radius, font, mouse_pos, text_color, button_color, hover_color):
    """Draw the round 'Quitter' button with hover effect."""
    if (mouse_pos[0] - quit_center[0]) ** 2 + (mouse_pos[1] - quit_center[1]) ** 2 <= radius ** 2:
        pygame.draw.circle(screen, hover_color, quit_center, radius)
    else:
        pygame.draw.circle(screen, button_color, quit_center, radius)
    quit_text = font.render("Quitter", True, text_color)
    screen.blit(quit_text, (quit_center[0] - quit_text.get_width() // 2,
                            quit_center[1] - quit_text.get_height() // 2))

def handle_quit_button(mouse_pos, quit_center, radius):
    """Check if the 'Quitter' button is clicked and quit the game if it is."""
    if (mouse_pos[0] - quit_center[0]) ** 2 + (mouse_pos[1] - quit_center[1]) ** 2 <= radius ** 2:
        pygame.quit()
        quit()

def draw_animated_stone(row, col, final_color, duration=0.3):
    """Animate the placement of a stone starting from gray to the final color."""
    steps = 10
    max_radius = pion_radius
    for step in range(steps):
        radius = int(max_radius * (step + 1) / steps)
        intermediate_color = (
            GRAY
        )
        pygame.draw.circle(screen, intermediate_color, (
            border_size + cell_size // 2 + col * cell_size,
            border_size + cell_size // 2 + row * cell_size
        ), radius)
        pygame.display.flip()
        time.sleep(duration / steps)

# def draw_background(): en test pour l'instant c'est de la merde de damier
#     """Draw a patterned background for the game."""
#     screen.fill(BORDER_COLOR)
#     for x in range(0, total_screen_width, cell_size):
#         for y in range(0, total_screen_height, cell_size):
#             rect = pygame.Rect(x, y, cell_size, cell_size)
#             color = (210, 180, 140) if (x // cell_size + y // cell_size) % 2 == 0 else (160, 82, 45)
#             pygame.draw.rect(screen, color, rect)

def main_menu():
    """Display the main menu and handle user interaction."""
    font = pygame.font.Font(None, 60)
    small_font = pygame.font.Font(None, 40)
    quit_font = pygame.font.Font(None, 30)
    
    quit_button_radius = 40
    quit_button_center = (total_screen_width - quit_button_radius - 30, total_screen_height - quit_button_radius - 30)

    while True:
        screen.fill(BORDER_COLOR)
        
        # Title text
        title_text = font.render("Gomoku", True, WHITE)
        screen.blit(title_text, (total_screen_width // 2 - title_text.get_width() // 2, 100))
        
        # Define button rectangles for "Partie normale", "Partie spéciale", and "Duo"
        normal_button = pygame.Rect(total_screen_width // 2 - 100, 300, 200, 50)
        special_button = pygame.Rect(total_screen_width // 2 - 100, 400, 200, 50)
        duo_button = pygame.Rect(total_screen_width // 2 - 100, 500, 200, 50)  # New "Duo" button
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Draw buttons using the draw_button function
        draw_button(screen, normal_button, "Partie normale", small_font, mouse_pos,
                    BUTTON_COLOR, BUTTON_HOVER_COLOR, WHITE, outline_color=GRAY)
        draw_button(screen, special_button, "Partie renju", small_font, mouse_pos,
                    BUTTON_COLOR, BUTTON_HOVER_COLOR, WHITE, outline_color=GRAY)
        draw_button(screen, duo_button, "Duo", small_font, mouse_pos,
                    BUTTON_COLOR, BUTTON_HOVER_COLOR, WHITE, outline_color=GRAY)
        
        # Draw the "Quitter" button using draw_quit_button
        draw_quit_button(screen, quit_button_center, quit_button_radius, quit_font, mouse_pos, WHITE, QUIT_BUTTON_COLOR, QUIT_BUTTON_HOVER_COLOR)
        
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
                elif duo_button.collidepoint(mouse_pos):  # Handle "Duo" button click
                    return "duo"
                handle_quit_button(mouse_pos, quit_button_center, quit_button_radius)

        pygame.display.flip()
        if exit_game:
            pygame.quit()
            quit()

def end_game_menu(winner):
    """Display the end game menu with options to replay, return to menu, or quit."""
    # draw_background()
    font = pygame.font.Font(None, 60)
    small_font = pygame.font.Font(None, 40)
    quit_font = pygame.font.Font(None, 30)
    
    quit_button_radius = 40
    quit_button_center = (total_screen_width - quit_button_radius - 30, total_screen_height - quit_button_radius - 30)
    
    while True:
        screen.fill(BORDER_COLOR)
        
        # Display the winner text
        winner_text = font.render(f"Le Joueur {winner} a gagné !", True, WINNER_COLOR)
        screen.blit(winner_text, (total_screen_width // 2 - winner_text.get_width() // 2, 100))
        
        # Define button rectangles for "Rejouer" and "Retour au menu"
        replay_button = pygame.Rect(total_screen_width // 2 - 100, 300, 200, 50)
        menu_button = pygame.Rect(total_screen_width // 2 - 110, 400, 220, 50)
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Draw buttons using the draw_button function
        draw_button(screen, replay_button, "Rejouer", small_font, mouse_pos,
                    BUTTON_COLOR, BUTTON_HOVER_COLOR, WHITE, outline_color=GRAY)
        draw_button(screen, menu_button, "Retour au menu", small_font, mouse_pos,
                    BUTTON_COLOR, BUTTON_HOVER_COLOR, WHITE, outline_color=GRAY)
        
        # Draw the "Quitter" button using draw_quit_button
        draw_quit_button(screen, quit_button_center, quit_button_radius, quit_font, mouse_pos, WHITE, QUIT_BUTTON_COLOR, QUIT_BUTTON_HOVER_COLOR)
        
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
                handle_quit_button(mouse_pos, quit_button_center, quit_button_radius)

        pygame.display.flip()
        if exit_game:
            pygame.quit()
            quit()

def draw_board(gomoku, winner=None, forbidden_message=None):
    """Draw the Gomoku board and display game information."""
    # draw_background()
    screen.fill(BORDER_COLOR)
    pygame.draw.rect(screen, BOARD_COLOR, (border_size, border_size, screen_size, screen_size))

    grid_start = border_size + cell_size // 2
    grid_end = border_size + screen_size - cell_size // 2

    # Draw the grid lines
    for x in range(board_size):
        x_pos = grid_start + x * cell_size
        pygame.draw.line(screen, GRID_COLOR, (x_pos, grid_start), (x_pos, grid_end))
    for y in range(board_size):
        y_pos = grid_start + y * cell_size
        pygame.draw.line(screen, GRID_COLOR, (grid_start, y_pos), (grid_end, y_pos))

    # Draw the stones
    for row in range(board_size):
        for col in range(board_size):
            value = gomoku.getBoardValue(row, col)
            if value == PlayerToken.WHITE.value:
                pygame.draw.circle(screen, WHITE, (grid_start + col * cell_size, grid_start + row * cell_size), int(pion_radius))
            elif value == PlayerToken.BLACK.value:
                pygame.draw.circle(screen, BLACK, (grid_start + col * cell_size, grid_start + row * cell_size), int(pion_radius))

    # Afficher les scores et le prochain joueur
    font = pygame.font.Font(None, 32)
    current_player = gomoku.getCurrentPlayer()
    next_player = "Noir" if current_player == PlayerToken.BLACK.value else "Blanc"
    # next_player = "Noir" if gomoku.current_player == PlayerToken.BLACK.value else "Blanc"
    black_score_text = font.render(f"Pions pris par Noir : {gomoku.getBlackPlayerPebblesTaken()}", True, TEXT_COLOR)
    white_score_text = font.render(f"Pions pris par Blanc : {gomoku.getWhitePlayerPebblesTaken()}", True, TEXT_COLOR)
    next_player_text = font.render(f"Prochain joueur : {next_player}", True, BLACK if current_player == PlayerToken.BLACK.value else WHITE)

    text_x = screen_size + 2 * border_size
    screen.blit(black_score_text, (text_x, 50))
    screen.blit(white_score_text, (text_x, 100))
    screen.blit(next_player_text, (text_x, 150))

    # Afficher les temps des joueurs
    time_start_y = 200  # Point de départ pour les temps
    line_spacing = 40  # Espacement vertical entre chaque ligne

    black_time_text = font.render(
        f"Noir: {player_times[PlayerToken.BLACK.value]['total_time']:.1f}s (dernier: {player_times[PlayerToken.BLACK.value]['last_time']:.1f}s)", 
        True, TEXT_COLOR
    )
    white_time_text = font.render(
        f"Blanc: {player_times[PlayerToken.WHITE.value]['total_time']:.1f}s (dernier: {player_times[PlayerToken.WHITE.value]['last_time']:.1f}s)", 
        True, TEXT_COLOR
    )

    screen.blit(black_time_text, (text_x, time_start_y))
    screen.blit(white_time_text, (text_x, time_start_y + line_spacing))

    if ai_process_time > 0:
        ia_time_text = font.render(
            f"Process IA : {ai_process_time:.3f}s", 
            True, TEXT_COLOR
        )
        screen.blit(ia_time_text, (text_x, time_start_y + 2 * line_spacing))

    # Afficher un message d'erreur, si nécessaire
    if forbidden_message:
        draw_forbidden_message(forbidden_message)

    if winner:
        winner_text = font.render(f"Le Joueur {winner} a gagné !", True, WINNER_COLOR)
        text_rect = winner_text.get_rect(center=(border_size + screen_size // 2, border_size + screen_size // 2))
        screen.blit(winner_text, text_rect)

def update_opponent_time(player_times: dict, current_player: int, turn_start_time: float) -> float:
    if turn_start_time:
        # the player and modify before in process_move so we want the player from before
        opponent_player = -current_player
        turn_duration = time.time() - turn_start_time
        player_times[opponent_player]["total_time"] += turn_duration
        player_times[opponent_player]["last_time"] = turn_duration
        return None
    return turn_start_time

def reset_player_times(player_times: dict) -> None:
    for player in player_times.keys():
        player_times[player]["total_time"] = 0
        player_times[player]["last_time"] = 0

def initialize_game(game_mode: str) -> tuple:
    global board_size, screen_size
    board_size = 15 if game_mode == "special" else 19
    gomoku = Gomoku(board_size, game_mode)
    screen_size = board_size * cell_size
    ia_player = None
    running = True
    game_over = False
    winner = None

    if game_mode == "special":
        ia_player = random.choice([PlayerToken.BLACK.value, PlayerToken.WHITE.value])
    elif game_mode == "normal":
        ia_player = PlayerToken.WHITE.value
    return gomoku, ia_player, running, game_over, winner

def render_game_ui():
    """Main UI rendering loop for the game."""

    def reset_forbidden_message(forbidden_message, message_start_time, message_duration):
        """Reset the forbidden message if its duration has passed."""
        if forbidden_message and message_start_time is not None and time.time() - message_start_time >= message_duration:
            return None, None
        return forbidden_message, message_start_time

    def handle_ai_turn(gomoku, ia_player, ai, player_times, message_start_time):
        """Handle the AI's turn."""
        global ai_process_time
        time_ai_start = time.time()
        score, best_move = ai.minmax(3, True, True)
        time_ai_end = time.time()
        ai_process_time = time_ai_end - time_ai_start
        if best_move:
            row, col = best_move
            is_valid, forbidden_message = gomoku.processMove(row, col)
            if not is_valid:
                message_start_time = time.time()
                return forbidden_message, message_start_time, False, is_valid, col, row

        return None, message_start_time, gomoku.getGameStatus(), is_valid, col, row

    def handle_player_turn(event, gomoku, color, player_times, message_start_time):
        """Handle the player's turn."""
        global board_size
        x, y = event.pos
        grid_start = border_size + cell_size // 2
        grid_end = border_size + screen_size - cell_size // 2

        is_valid = False
        col, row = None, None
        if grid_start <= x <= grid_end and grid_start <= y <= grid_end:
            col = int(round((x - grid_start) / cell_size))
            row = int(round((y - grid_start) / cell_size))

            if 0 <= row < board_size and 0 <= col < board_size:
                if gomoku.getBoardValue(row, col) == PlayerToken.EMPTY.value:
                    is_valid, forbidden_message = gomoku.processMove(row, col)
                    if not is_valid:
                        message_start_time = time.time()
                        return forbidden_message, message_start_time, False, is_valid, col, row
        
        return None, message_start_time, gomoku.getGameStatus(), is_valid, col, row

    global message_start_time, exit_game, turn_start_time, ai_process_time
    forbidden_message = None

    while not exit_game:
        game_mode = main_menu()

        if game_mode in ["normal", "duo", "special"]:
            gomoku, ia_player, running, game_over, winner = initialize_game(game_mode)

            while running:
                draw_board(gomoku, winner, forbidden_message)
                forbidden_message, message_start_time = reset_forbidden_message(forbidden_message, message_start_time, message_duration)
                pygame.display.flip()

                color = WHITE if gomoku.getCurrentPlayer() == PlayerToken.WHITE.value else BLACK

                if game_mode in ["normal", "special"] and gomoku.getCurrentPlayer() == ia_player:
                    ai = GomokuAI(gomoku=gomoku)
                    if not turn_start_time:
                        turn_start_time = time.time()
                    forbidden_message, message_start_time, game_over, is_valid, col, row = handle_ai_turn(
                        gomoku, ia_player, ai, player_times, message_start_time
                    )
                    if turn_start_time and is_valid:
                        turn_start_time = update_opponent_time(player_times, gomoku.getCurrentPlayer(), turn_start_time)
                    if is_valid:
                        draw_animated_stone(row, col, color)
                else:
                    if not turn_start_time:
                        turn_start_time = time.time()
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                            exit_game = True
                        elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                            forbidden_message, message_start_time, game_over, is_valid, col, row = handle_player_turn(
                                event, gomoku, turn_start_time, player_times, message_start_time
                            )
                            if turn_start_time and is_valid:
                                turn_start_time = update_opponent_time(player_times, gomoku.getCurrentPlayer(), turn_start_time)
                            if is_valid:
                                draw_animated_stone(row, col, color)
                if gomoku.getGameStatus():
                    game_over = True
                    winner = "Noir" if gomoku.getCurrentPlayer() == PlayerToken.BLACK.value else "Blanc"            
                if game_over:
                    reset_player_times(player_times)
                    ai_process_time = 0
                    action = end_game_menu(winner)
                    if action == "replay":
                        board_size = 15 if game_mode == "special" else 19
                        gomoku = Gomoku(board_size, game_mode)
                        if game_mode in ["normal", "special"]:
                            ai = GomokuAI(gomoku=gomoku)
                        game_over = False
                        winner = None
                        if game_mode in ["special"]:
                            ia_player = random.choice([PlayerToken.BLACK.value, PlayerToken.WHITE.value])
                    elif action == "menu":
                        break

        if exit_game:
            pygame.quit()
            quit()