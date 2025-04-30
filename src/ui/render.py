import pygame
import time
import random

# Instead of importing Python Gomoku, import the C++-bound class:
# from src.game._gomoku import Gomoku
# from src.algo.algo import GomokuAI
from cpp_gomoku import Gomoku, GomokuAI
from src.game.playerTokens import PlayerToken


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
HOVER_COLOR = (255, 69, 0)
COLOR_ON = (0, 200, 0)
COLOR_OFF = (200, 0, 0)
# Temps pour chaque joueur
player_times = {
    PlayerToken.BLACK.value: {"total_time": 0, "last_time": 0},
    PlayerToken.WHITE.value: {"total_time": 0, "last_time": 0}
}


class GomokuUi:
    def __init__(self):
        # Initialize Pygame
        pygame.init()

        # We can ask for the board size from the C++ Gomoku if you want dynamic sizing.
        # Or just keep it as 19 if your C++ also defaults to 19.
        self.board_size = 19
        self.ai_suggestion = None
        self.depth_value = 3
        self.ai_process_time = 0
        self.hint_used = False
        self.message_start_time = None
        self.turn_start_time = None
        self.exit_game = False
        self.pause_after_game = False

        self.cell_size = 40  # Size of the board cells
        self.screen_size = self.board_size * self.cell_size
        self.border_size = self.cell_size  # Border set to the size of one cell
        self.score_panel_width = 350  # Width of the score panel
        self.total_screen_width = self.screen_size + 2 * self.border_size + self.score_panel_width
        self.total_screen_height = self.screen_size + 2 * self.border_size
        self.screen = pygame.display.set_mode((self.total_screen_width, self.total_screen_height), pygame.RESIZABLE)
        pygame.display.set_caption("Gomoku")
        # Stone size (based on cell_size)
        self.pion_radius = self.cell_size // 2.5  # Adjusted size for larger stones
        # Timing settings for displaying messages
        self.message_duration = 5  # Duration in seconds

 
    def draw_forbidden_message(self, message):
        """
        Dessine le message de mouvement interdit dans le panneau latéral,
        en découpant le texte si nécessaire pour éviter qu'il dépasse les limites.
        """
        if not message:
            return
        if isinstance(message, tuple):
            message = " ".join([str(m) for m in message if m])
        font = pygame.font.Font(None, 32)
        max_width = self.score_panel_width - 20  # Largeur maximale pour le texte (ajustée pour laisser une marge)
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
        message_x = self.screen_size + 2 * self.border_size  # Position dans le panneau latéral
        message_y = 350  # Position de départ pour le message
        line_spacing = 35  # Espacement entre les lignes

        for line in lines:
            text_surface = font.render(line, True, WINNER_COLOR)
            self.screen.blit(text_surface, (message_x, message_y))
            message_y += line_spacing

    def draw_toggle_pause_button(self) -> pygame.Rect:
        """Draw the ON/OFF button for a pause after the game,
        so you can see the state of the game before quitting.."""
        toggle_font = pygame.font.Font(None, 30)
        toggle_width = 240
        toggle_height = 40
        padding = 30

        toggle_x = padding
        toggle_y = self.total_screen_height - toggle_height - padding
        toggle_rect = pygame.Rect(toggle_x, toggle_y, toggle_width, toggle_height)

        label = "Pause: ON" if self.pause_after_game else "Pause: OFF"
        color = (0, 200, 0) if self.pause_after_game else (200, 0, 0)

        pygame.draw.rect(self.screen, color, toggle_rect)
        text_surface = toggle_font.render(label, True, WHITE)

        text_x = toggle_rect.centerx - text_surface.get_width() // 2
        text_y = toggle_rect.centery - text_surface.get_height() // 2
        self.screen.blit(text_surface, (text_x, text_y))

        return toggle_rect

    def draw_button(self, button_rect, text, font, mouse_pos, button_color, hover_color, text_color, outline_color=None):
        """Draw a button with hover effect, text, and optional outline."""
        if button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, hover_color, button_rect)  # Change color on hover
            if outline_color:  # Optional outline effect
                pygame.draw.rect(self.screen, outline_color, button_rect, 3)  # Draw outline with thickness 3
        else:
            pygame.draw.rect(self.screen, button_color, button_rect)  # Default color
        text_surface = font.render(text, True, text_color)
        self.screen.blit(
            text_surface, 
            (button_rect.centerx - text_surface.get_width() // 2,
            button_rect.centery - text_surface.get_height() // 2)
        )

    def draw_quit_button(self, quit_center, radius, font, mouse_pos, text_color, button_color, hover_color):
        """Draw the round 'Quitter' button with hover effect."""
        if (mouse_pos[0] - quit_center[0]) ** 2 + (mouse_pos[1] - quit_center[1]) ** 2 <= radius ** 2:
            pygame.draw.circle(self.screen, hover_color, quit_center, radius)
        else:
            pygame.draw.circle(self.screen, button_color, quit_center, radius)
        quit_text = font.render("Quitter", True, text_color)
        self.screen.blit(quit_text, (quit_center[0] - quit_text.get_width() // 2,
                                quit_center[1] - quit_text.get_height() // 2))

    def draw_generic_game_button(self, button_rect, font, mouse_pos, text, color, hover_color, text_color=WHITE):
        """
        Draws a generic button in the game interface with a hover effect.
        """
        if button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, hover_color, button_rect)
        else:
            pygame.draw.rect(self.screen, color, button_rect)

        text_surface = font.render(text, True, text_color)
        text_x = button_rect.centerx - text_surface.get_width() // 2
        text_y = button_rect.centery - text_surface.get_height() // 2
        self.screen.blit(text_surface, (text_x, text_y))

    def draw_slider(self, x, y, width, min_val, max_val, current_val, font):
        """Draw a horizontal slider and return the new value if moved."""
        slider_rect = pygame.Rect(x, y, width, 8)
        pygame.draw.rect(self.screen, GRAY, slider_rect)

        # Position du curseur
        knob_radius = 10
        knob_x = x + int((current_val - min_val) / (max_val - min_val) * width)
        knob_y = y + 4
        pygame.draw.circle(self.screen, WHITE, (knob_x, knob_y), knob_radius)

        # Texte
        text = font.render(f"AI Depth/Difficulté: {current_val}", True, WHITE)
        self.screen.blit(text, (x, y - 30))

        return slider_rect, knob_x, knob_radius

    @staticmethod
    def handle_quit_button(mouse_pos, quit_center, radius):
        """Check if the 'Quitter' button is clicked and quit the game if it is."""
        if (mouse_pos[0] - quit_center[0]) ** 2 + (mouse_pos[1] - quit_center[1]) ** 2 <= radius ** 2:
            pygame.quit()
            quit()

    def draw_animated_stone(self, row, col, final_color, duration=0.3):
        """Animate the placement of a stone starting from gray to the final color."""
        steps = 10
        max_radius = self.pion_radius
        for step in range(steps):
            radius = int(max_radius * (step + 1) / steps)
            intermediate_color = (
                GRAY
            )
            pygame.draw.circle(self.screen, intermediate_color, (
                self.border_size + self.cell_size // 2 + col * self.cell_size,
                self.border_size + self.cell_size // 2 + row * self.cell_size
            ), radius)
            pygame.display.flip()
            time.sleep(duration / steps)

    @staticmethod
    def get_ai_suggestion(gomoku, ia):
        """Recovers the best AI suggestion for the current player."""
        _, best_move = ia.minmax(3, True, True)
        return best_move if best_move else None

    def handle_depth_slider(self, slider_x: int, slider_y: int, slider_width: int, mouse_pos, font) -> tuple:
        """
        Displays and manages the AI depth slider.
        Returns the rect of the slider (for collisions) and the updated state of depth_value.
        """
        slider_rect, knob_x, knob_radius = self.draw_slider(
            slider_x,
            slider_y,
            slider_width,
            1, 11,
            self.depth_value,
            font
        )

        if pygame.mouse.get_pressed()[0] and slider_rect.collidepoint(mouse_pos):
            relative_x = mouse_pos[0] - slider_rect.x
            ratio = relative_x / slider_rect.width
            new_depth = max(1, min(11, int(round(ratio * (11 - 1) + 1))))
            self.depth_value = new_depth

        return slider_rect

    def main_menu(self):
        """Display the main menu and handle user interaction."""
        font = pygame.font.Font(None, 60)
        small_font = pygame.font.Font(None, 40)
        quit_font = pygame.font.Font(None, 30)
        
        quit_button_radius = 40
        quit_button_center = (self.total_screen_width - quit_button_radius - 30, self.total_screen_height - quit_button_radius - 30)

        while True:
            self.screen.fill(BORDER_COLOR)
            
            # Title text
            title_text = font.render("Gomoku", True, WHITE)
            self.screen.blit(title_text, (self.total_screen_width // 2 - title_text.get_width() // 2, 100))
            
            # Define button rectangles for "Partie normale", "Partie spéciale", and "Duo"
            normal_button = pygame.Rect(self.total_screen_width // 2 - 100, 300, 200, 50)
            special_button = pygame.Rect(self.total_screen_width // 2 - 100, 400, 200, 50)
            duo_button = pygame.Rect(self.total_screen_width // 2 - 100, 500, 200, 50)  # New "Duo" button
            
            mouse_pos = pygame.mouse.get_pos()
            
            # Draw buttons using the draw_button function
            self.draw_button(normal_button, "Partie normale", small_font, mouse_pos,
                        BUTTON_COLOR, BUTTON_HOVER_COLOR, WHITE, outline_color=GRAY)
            self.draw_button(special_button, "Partie renju", small_font, mouse_pos,
                        BUTTON_COLOR, BUTTON_HOVER_COLOR, WHITE, outline_color=GRAY)
            self.draw_button(duo_button, "Duo", small_font, mouse_pos,
                        BUTTON_COLOR, BUTTON_HOVER_COLOR, WHITE, outline_color=GRAY)
            
            # Draw the "Quitter" button using draw_quit_button
            self.draw_quit_button(quit_button_center, quit_button_radius, quit_font, mouse_pos, WHITE, QUIT_BUTTON_COLOR, HOVER_COLOR)
            
            # Draw the slider
            slider_font = pygame.font.Font(None, 30)
            slider_x = self.total_screen_width // 2 - 100
            slider_y = 600
            slider_width = 200
            slider_rect = self.handle_depth_slider(slider_x, slider_y, slider_width, mouse_pos, slider_font)

            toggle_rect = self.draw_toggle_pause_button()

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
                    elif toggle_rect.collidepoint(mouse_pos):
                        self.pause_after_game = not self.pause_after_game
                    GomokuUi.handle_quit_button(mouse_pos, quit_button_center, quit_button_radius)

            pygame.display.flip()
            if self.exit_game:
                pygame.quit()
                quit()

    def end_game_menu(self, winner):
        """Display the end game menu with options to replay, return to menu, or quit."""
        # draw_background()
        font = pygame.font.Font(None, 60)
        small_font = pygame.font.Font(None, 40)
        quit_font = pygame.font.Font(None, 30)
        
        quit_button_radius = 40
        quit_button_center = (self.total_screen_width - quit_button_radius - 30, self.total_screen_height - quit_button_radius - 30)
        
        while True:
            self.screen.fill(BORDER_COLOR)
            
            # Display the winner text
            winner_text = font.render(f"Le Joueur {winner} a gagné !", True, WINNER_COLOR)
            self.screen.blit(winner_text, (self.total_screen_width // 2 - winner_text.get_width() // 2, 100))
            
            # Define button rectangles for "Rejouer" and "Retour au menu"
            replay_button = pygame.Rect(self.total_screen_width // 2 - 100, 300, 200, 50)
            menu_button = pygame.Rect(self.total_screen_width // 2 - 110, 400, 220, 50)
            
            mouse_pos = pygame.mouse.get_pos()
            
            # Draw buttons using the draw_button function
            self.draw_button(replay_button, "Rejouer", small_font, mouse_pos,
                        BUTTON_COLOR, BUTTON_HOVER_COLOR, WHITE, outline_color=GRAY)
            self.draw_button(menu_button, "Retour au menu", small_font, mouse_pos,
                        BUTTON_COLOR, BUTTON_HOVER_COLOR, WHITE, outline_color=GRAY)
            
            # Draw the "Quitter" button using draw_quit_button
            self.draw_quit_button(quit_button_center, quit_button_radius, quit_font, mouse_pos, WHITE, QUIT_BUTTON_COLOR, HOVER_COLOR)
            
            # Draw the slider
            slider_font = pygame.font.Font(None, 30)
            slider_x = self.total_screen_width // 2 - 100
            slider_y = 580
            slider_width = 200
            slider_rect = self.handle_depth_slider(slider_x, slider_y, slider_width, mouse_pos, slider_font)

            toggle_rect = self.draw_toggle_pause_button()

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
                    elif toggle_rect.collidepoint(mouse_pos):
                        self.pause_after_game = not self.pause_after_game
                    GomokuUi.handle_quit_button(mouse_pos, quit_button_center, quit_button_radius)

            pygame.display.flip()
            if self.exit_game:
                pygame.quit()
                quit()

    def draw_board(self, gomoku, game_mode, winner=None, forbidden_message=None):
        """Draw the Gomoku board and display game information."""
        # draw_background()
        self.screen.fill(BORDER_COLOR)
        pygame.draw.rect(self.screen, BOARD_COLOR, (self.border_size, self.border_size, self.screen_size, self.screen_size))

        grid_start = self.border_size + self.cell_size // 2
        grid_end = self.border_size + self.screen_size - self.cell_size // 2

        # Draw the grid lines
        for x in range(self.board_size):
            x_pos = grid_start + x * self.cell_size
            pygame.draw.line(self.screen, GRID_COLOR, (x_pos, grid_start), (x_pos, grid_end))
        for y in range(self.board_size):
            y_pos = grid_start + y * self.cell_size
            pygame.draw.line(self.screen, GRID_COLOR, (grid_start, y_pos), (grid_end, y_pos))

        # Draw the stones
        for row in range(self.board_size):
            for col in range(self.board_size):
                value = gomoku.getBoardValue(row, col)
                if value == PlayerToken.WHITE.value:
                    pygame.draw.circle(self.screen, WHITE, (grid_start + col * self.cell_size, grid_start + row * self.cell_size), int(self.pion_radius))
                elif value == PlayerToken.BLACK.value:
                    pygame.draw.circle(self.screen, BLACK, (grid_start + col * self.cell_size, grid_start + row * self.cell_size), int(self.pion_radius))

        # Afficher les scores et le prochain joueur
        font = pygame.font.Font(None, 32)
        current_player = gomoku.getCurrentPlayer()
        next_player = "Noir" if current_player == PlayerToken.BLACK.value else "Blanc"
        # next_player = "Noir" if gomoku.current_player == PlayerToken.BLACK.value else "Blanc"
        if game_mode != "special":
            black_score_text = font.render(f"Pions pris par Noir : {gomoku.getBlackPlayerPebblesTaken()}", True, TEXT_COLOR)
            white_score_text = font.render(f"Pions pris par Blanc : {gomoku.getWhitePlayerPebblesTaken()}", True, TEXT_COLOR)
        next_player_text = font.render(f"Prochain joueur : {next_player}", True, BLACK if current_player == PlayerToken.BLACK.value else WHITE)

        text_x = self.screen_size + 2 * self.border_size
        if game_mode != "special":
            self.screen.blit(black_score_text, (text_x, 50))
            self.screen.blit(white_score_text, (text_x, 100))
        self.screen.blit(next_player_text, (text_x, 150))

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

        self.screen.blit(black_time_text, (text_x, time_start_y))
        self.screen.blit(white_time_text, (text_x, time_start_y + line_spacing))

        if self.ai_process_time > 0:
            ia_time_text = font.render(
                f"Process IA : {self.ai_process_time:.3f}s", 
                True, TEXT_COLOR
            )
            self.screen.blit(ia_time_text, (text_x, time_start_y + 2 * line_spacing))

        # Afficher un message d'erreur, si nécessaire
        if forbidden_message:
            self.draw_forbidden_message(forbidden_message)

        if winner:
            winner_text = font.render(f"Le Joueur {winner} a gagné !", True, WINNER_COLOR)
            text_rect = winner_text.get_rect(center=(self.border_size + self.screen_size // 2, self.border_size + self.screen_size // 2))
            self.screen.blit(winner_text, text_rect)

        surrender_button_x = self.screen_size + 2 * self.border_size
        surrender_button_y = self.total_screen_height - 160
        surrender_button_rect = pygame.Rect(surrender_button_x, surrender_button_y, 200, 50)
        surrender_font = pygame.font.Font(None, 36)
        self.draw_generic_game_button(surrender_button_rect, surrender_font, pygame.mouse.get_pos(), 
            text="Surrender",
            color=(178, 34, 34),
            hover_color=HOVER_COLOR
        )

        return surrender_button_rect

    def update_opponent_time(self, player_times: dict, current_player: int) -> float:
        if self.turn_start_time:
            # the player and modify before in process_move so we want the player from before
            opponent_player = -current_player
            turn_duration = time.time() - self.turn_start_time
            player_times[opponent_player]["total_time"] += turn_duration
            player_times[opponent_player]["last_time"] = turn_duration
            self.turn_start_time = None
        

    @staticmethod
    def reset_player_times(player_times: dict) -> None:
        for player in player_times.keys():
            player_times[player]["total_time"] = 0
            player_times[player]["last_time"] = 0

    def initialize_game(self, game_mode: str) -> tuple:
        self.board_size = 15 if game_mode == "special" else 19
        gomoku = Gomoku(self.board_size, game_mode)
        self.screen_size = self.board_size * self.cell_size
        ia_player = None
        running = True
        game_over = False
        winner = None

        if game_mode == "special":
            ia_player = random.choice([PlayerToken.BLACK.value, PlayerToken.WHITE.value])
        elif game_mode == "normal":
            ia_player = PlayerToken.WHITE.value
        return gomoku, ia_player, running, game_over, winner


    def draw_hint_feature(self, game_mode):
        """Displays IA index button and temporary suggested point in duo mode."""
        if game_mode == "duo":
            hint_button_x = self.screen_size + 2 * self.border_size  
            hint_button_y = self.total_screen_height - 100
            hint_button_rect = pygame.Rect(hint_button_x, hint_button_y, 200, 50)
            small_font = pygame.font.Font(None, 40)

            self.draw_generic_game_button(hint_button_rect, small_font, pygame.mouse.get_pos(),
                text="IA Hint",
                color=BUTTON_COLOR,
                hover_color=BUTTON_HOVER_COLOR
            )

            # Displays a temporary red dot if a suggestion has been made
            if self.ai_suggestion:
                pygame.draw.circle(
                    self.screen, WINNER_COLOR, 
                    (self.border_size + self.cell_size // 2 + self.ai_suggestion[1] * self.cell_size, 
                    self.border_size + self.cell_size // 2 + self.ai_suggestion[0] * self.cell_size), 
                    int(self.pion_radius / 2)
                )

        return hint_button_rect if game_mode == "duo" else None

    def reset_forbidden_message(self, forbidden_message):
        """Reset the forbidden message if its duration has passed."""
        if forbidden_message and self.message_start_time is not None and time.time() - self.message_start_time >= self.message_duration:
            return None, None
        return forbidden_message

    def handle_ai_turn(self, gomoku, ia_player, ai, player_times):
        """Handle the AI's turn."""
        time_ai_start = time.time()
        score, best_move = ai.minmax(self.depth_value, True, True)
        time_ai_end = time.time()
        self.ai_process_time = time_ai_end - time_ai_start
        if best_move:
            row, col = best_move
            is_valid, forbidden_message, score = gomoku.processMove(row, col)
            if not is_valid:
                self.message_start_time = time.time()
                return forbidden_message, False, is_valid, col, row
            print(f"movement play: ({row}, {col})")

        return None, gomoku.getGameStatus(), is_valid, col, row

    def handle_player_turn(self, event, gomoku, color, player_times):
        """Handle the player's turn."""
        x, y = event.pos
        grid_start = self.border_size + self.cell_size // 2
        grid_end = self.border_size + self.screen_size - self.cell_size // 2

        is_valid = False
        col, row = None, None
        if grid_start <= x <= grid_end and grid_start <= y <= grid_end:
            col = int(round((x - grid_start) / self.cell_size))
            row = int(round((y - grid_start) / self.cell_size))

            if 0 <= row < self.board_size and 0 <= col < self.board_size:
                if gomoku.getBoardValue(row, col) == PlayerToken.EMPTY.value:
                    is_valid, forbidden_message, score = gomoku.processMove(row, col)
                    if not is_valid:
                        self.message_start_time = time.time()
                        return forbidden_message, False, is_valid, col, row
                    print(f"movement play: ({row}, {col})")
                    self.ai_suggestion = None
                    self.hint_used = False   
        
        return None, gomoku.getGameStatus(), is_valid, col, row

    def render_game_ui(self):
        """Main UI rendering loop for the game."""

        forbidden_message = None

        while not self.exit_game:
            game_mode = self.main_menu()

            if game_mode in ["normal", "duo", "special"]:
                gomoku, ia_player, running, game_over, winner = self.initialize_game(game_mode)

                while running:
                    surrender_button_rect = self.draw_board(gomoku, game_mode, winner, forbidden_message)
                    if game_mode == "duo":
                        hint_button_rect = self.draw_hint_feature(game_mode)
                    else:
                        hint_button_rect = None
                    forbidden_message = self.reset_forbidden_message(forbidden_message)
                    pygame.display.flip()

                    color = WHITE if gomoku.getCurrentPlayer() == PlayerToken.WHITE.value else BLACK

                    if game_mode in ["normal", "special"] and gomoku.getCurrentPlayer() == ia_player:
                        ai = GomokuAI(gomoku=gomoku)
                        if not self.turn_start_time:
                            self.turn_start_time = time.time()
                        forbidden_message, game_over, is_valid, col, row = self.handle_ai_turn(
                            gomoku, ia_player, ai, player_times
                        )
                        if self.turn_start_time and is_valid:
                            self.update_opponent_time(player_times, gomoku.getCurrentPlayer())
                        if is_valid:
                            self.draw_animated_stone(row, col, color)
                    else:
                        if not self.turn_start_time:
                            self.turn_start_time = time.time()
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                running = False
                                self.exit_game = True
                            elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                                if game_mode == "duo" and not self.hint_used and event.type == pygame.MOUSEBUTTONDOWN:
                                    if hint_button_rect.collidepoint(event.pos):
                                        self.ai_suggestion = GomokuUi.get_ai_suggestion(gomoku, GomokuAI(gomoku))
                                        self.hint_used = True
                                if surrender_button_rect.collidepoint(event.pos):
                                    game_over = True
                                    winner = "Noir" if gomoku.getCurrentPlayer() == PlayerToken.WHITE.value else "Blanc"
                                    break
                                forbidden_message, game_over, is_valid, col, row = self.handle_player_turn(
                                    event, gomoku, color, player_times
                                )
                                if self.turn_start_time and is_valid:
                                    self.update_opponent_time(player_times, gomoku.getCurrentPlayer())
                                if is_valid:
                                    self.draw_animated_stone(row, col, color)
                    if gomoku.getGameStatus():
                        game_over = True
                        winner = "Noir" if gomoku.getCurrentPlayer() == PlayerToken.BLACK.value else "Blanc"            
                    if game_over:
                        if self.pause_after_game:
                            font = pygame.font.Font(None, 40)
                            text = font.render("Press SPACE to continue...", True, WHITE)
                            self.screen.blit(text, (self.border_size + self.screen_size // 2 - text.get_width() // 2, self.total_screen_height - 80))
                            pygame.display.flip()
                            waiting = True
                            while waiting:
                                for event in pygame.event.get():
                                    if event.type == pygame.QUIT:
                                        pygame.quit()
                                        sys.exit()
                                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                                        waiting = False
                        GomokuUi.reset_player_times(player_times)
                        self.ai_process_time = 0
                        action = self.end_game_menu(winner)
                        if action == "replay":
                            self.board_size = 15 if game_mode == "special" else 19
                            gomoku = Gomoku(self.board_size, game_mode)
                            if game_mode in ["normal", "special"]:
                                ai = GomokuAI(gomoku=gomoku)
                            game_over = False
                            winner = None
                            if game_mode in ["special"]:
                                ia_player = random.choice([PlayerToken.BLACK.value, PlayerToken.WHITE.value])
                        elif action == "menu":
                            break

            if self.exit_game:
                pygame.quit()
                quit()