import pygame
import time
import random

from src.game.gomoku import Gomoku
from src.game.playerTokens import PlayerToken
from src.algo.algo import GomokuAI

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

# Temps pour chaque joueur
player_times = {
    PlayerToken.BLACK.value: {"total_time": 0, "last_time": 0},
    PlayerToken.WHITE.value: {"total_time": 0, "last_time": 0}
}
turn_start_time = None


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
    message_y = 300  # Position de départ pour le message
    line_spacing = 35  # Espacement entre les lignes

    for line in lines:
        text_surface = font.render(line, True, WINNER_COLOR)
        screen.blit(text_surface, (message_x, message_y))
        message_y += line_spacing

def draw_button(screen, button_rect, text, font, mouse_pos, button_color, hover_color, text_color):
    """Draw a button with hover effect and text."""
    if button_rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, hover_color, button_rect)
    else:
        pygame.draw.rect(screen, button_color, button_rect)
    text_surface = font.render(text, True, text_color)
    screen.blit(text_surface, (button_rect.centerx - text_surface.get_width() // 2,
                            button_rect.centery - text_surface.get_height() // 2))

def draw_quit_button(screen, quit_center, radius, font, text_color, button_color):
    """Draw the round 'Quitter' button."""
    pygame.draw.circle(screen, button_color, quit_center, radius)
    quit_text = font.render("Quitter", True, text_color)
    screen.blit(quit_text, (quit_center[0] - quit_text.get_width() // 2,
                            quit_center[1] - quit_text.get_height() // 2))

def handle_quit_button(mouse_pos, quit_center, radius):
    """Check if the 'Quitter' button is clicked and quit the game if it is."""
    if (mouse_pos[0] - quit_center[0]) ** 2 + (mouse_pos[1] - quit_center[1]) ** 2 <= radius ** 2:
        pygame.quit()
        quit()

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
                    BUTTON_COLOR, BUTTON_HOVER_COLOR, WHITE)
        draw_button(screen, special_button, "Partie spéciale", small_font, mouse_pos,
                    BUTTON_COLOR, BUTTON_HOVER_COLOR, WHITE)
        draw_button(screen, duo_button, "Duo", small_font, mouse_pos,  # Draw the "Duo" button
                    BUTTON_COLOR, BUTTON_HOVER_COLOR, WHITE)
        
        # Draw the "Quitter" button using draw_quit_button
        draw_quit_button(screen, quit_button_center, quit_button_radius, quit_font, WHITE, QUIT_BUTTON_COLOR)
        
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
                    BUTTON_COLOR, BUTTON_HOVER_COLOR, WHITE)
        draw_button(screen, menu_button, "Retour au menu", small_font, mouse_pos,
                    BUTTON_COLOR, BUTTON_HOVER_COLOR, WHITE)
        
        # Draw the "Quitter" button using draw_quit_button
        draw_quit_button(screen, quit_button_center, quit_button_radius, quit_font, WHITE, QUIT_BUTTON_COLOR)
        
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
    screen.fill(BORDER_COLOR)
    pygame.draw.rect(screen, BOARD_COLOR, (border_size, border_size, screen_size, screen_size))

    grid_start = border_size + cell_size // 2
    grid_end = border_size + screen_size - cell_size // 2

    # Dessiner le plateau
    for x in range(board_size):
        x_pos = grid_start + x * cell_size
        pygame.draw.line(screen, GRID_COLOR, (x_pos, grid_start), (x_pos, grid_end))
    for y in range(board_size):
        y_pos = grid_start + y * cell_size
        pygame.draw.line(screen, GRID_COLOR, (grid_start, y_pos), (grid_end, y_pos))

    # Dessiner les pions
    for row in range(board_size):
        for col in range(board_size):
            if gomoku.board[row, col] == PlayerToken.WHITE.value:
                pygame.draw.circle(screen, WHITE, (grid_start + col * cell_size, grid_start + row * cell_size), int(pion_radius))
            elif gomoku.board[row, col] == PlayerToken.BLACK.value:
                pygame.draw.circle(screen, BLACK, (grid_start + col * cell_size, grid_start + row * cell_size), int(pion_radius))

    # Afficher les scores et le prochain joueur
    font = pygame.font.Font(None, 32)
    next_player = "Noir" if gomoku.current_player == PlayerToken.BLACK.value else "Blanc"
    black_score_text = font.render(f"Pions pris par Noir : {gomoku.black_player_pebbles_taken}", True, TEXT_COLOR)
    white_score_text = font.render(f"Pions pris par Blanc : {gomoku.white_player_pebbles_taken}", True, TEXT_COLOR)
    next_player_text = font.render(f"Prochain joueur : {next_player}", True, BLACK if gomoku.current_player == PlayerToken.BLACK.value else WHITE)

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

    # Afficher un message d'erreur, si nécessaire
    if forbidden_message:
        draw_forbidden_message(forbidden_message)

    if winner:
        winner_text = font.render(f"Le Joueur {winner} a gagné !", True, WINNER_COLOR)
        text_rect = winner_text.get_rect(center=(border_size + screen_size // 2, border_size + screen_size // 2))
        screen.blit(winner_text, text_rect)

def render_game_ui():
    global message_start_time, exit_game, turn_start_time
    forbidden_message = None
    coup_special = False  # Indique si un coup spécial est actif
    special_turn_owner = None  # Suivi du joueur qui a obtenu le coup spécial
    break_line_5 = None # indique si il y a une possibiliter de briser la ligne de 5
    var_win_type = None # indique si une condition de victoire est actuellement disponible

    while not exit_game:
        game_mode = main_menu()
        
        if game_mode in ["normal", "duo", "special"] and not exit_game:
            gomoku = Gomoku()
            ai = GomokuAI(gomoku=gomoku, depth=1)
            running = True
            game_over = False
            winner = None
            ia_player = PlayerToken.WHITE.value
        
            if game_mode in ["special"] and not exit_game:
                ia_player = random.choice([PlayerToken.BLACK.value, PlayerToken.WHITE.value]) # Déterminer aléatoirement qui est contrôlé par l'IA
                print(ia_player)
            while running and not exit_game:
                draw_board(gomoku, winner, forbidden_message)
                
                if forbidden_message and time.time() - message_start_time < message_duration:
                    draw_forbidden_message(forbidden_message)
                elif forbidden_message and time.time() - message_start_time >= message_duration:
                    forbidden_message = None
                
                pygame.display.flip()

                if game_mode in ["normal", "special"] and gomoku.current_player == ia_player:
                    if not turn_start_time:
                        turn_start_time = time.time()
                    best_move = ai.find_best_move(player=ia_player)
                    if best_move:
                        row, col = best_move

                        #TODO CREATE A FUINCTION MAJ time
                        # TODO MAJ the logic of changing players with time management (gomoku.current_player)  is now changed in process_move 
                        if turn_start_time:
                            turn_duration = time.time() - turn_start_time
                            player_times[gomoku.current_player]["total_time"] += turn_duration
                            player_times[gomoku.current_player]["last_time"] = turn_duration
                            turn_start_time = None

                        # is_valid, forbidden_message = process_move(gomoku, row, col)
                        is_valid = gomoku.process_move(row, col)
                        if not is_valid:
                            # gomoku.board[row, col] = PlayerToken.EMPTY.value
                            continue
                        
                        if gomoku.game_over:
                            game_over = True
                            winner = "Noir" if gomoku.current_player == PlayerToken.BLACK.value else "Blanc"

                else:
                    # time start
                    if not turn_start_time:
                        turn_start_time = time.time()
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
                                        is_valid = gomoku.process_move(row, col)
                                        if not is_valid:
                                            message_start_time = time.time()
                                            continue
                                        # MAJ time
                                        # TODO CREATE A FUNCTION MAJ TIME
                                        if turn_start_time:
                                            turn_duration = time.time() - turn_start_time
                                            player_times[gomoku.current_player]["total_time"] += turn_duration
                                            player_times[gomoku.current_player]["last_time"] = turn_duration
                                            turn_start_time = None
                                        
                                        if gomoku.game_over:
                                            game_over = True
                                            winner = "Noir" if gomoku.current_player == PlayerToken.BLACK.value else "Blanc"

                if game_over and not exit_game:
                    action = end_game_menu(winner)
                    if action == "replay":
                        gomoku = Gomoku()
                        ai.reset(gomoku)
                        ai = GomokuAI(gomoku)
                        game_over = False
                        winner = None
                        coup_special = False
                        special_turn_owner = None
                        if game_mode in ["special"] and not exit_game:
                            ia_player = random.choice([PlayerToken.BLACK.value, PlayerToken.WHITE.value])
                    elif action == "menu":
                        break

        if exit_game:
            pygame.quit()
            quit()