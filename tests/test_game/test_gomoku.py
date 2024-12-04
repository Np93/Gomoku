import pytest
from src.game.gomoku import Gomoku
from src.game.playerTokens import PlayerToken

def test_initial_state():
    """Test the initial state of the Gomoku board and player attributes."""
    game = Gomoku()
    assert game.board.shape == (19, 19)
    assert game.current_player == PlayerToken.BLACK.value
    assert game.white_player_pebbles_taken == 0
    assert game.black_player_pebbles_taken == 0
    assert game.game_over is False

def test_double_three_rule():
    """Test the double-three rule to ensure forbidden move detection."""
    game = Gomoku()
    # Position initiale avec une configuration double-trois
    game.board[5, 4] = game.current_player
    game.board[5, 3] = game.current_player
    game.board[4, 5] = game.current_player
    game.board[3, 5] = game.current_player
    
    # Ajout d'une pierre qui crée un double-trois
    game.board[5, 5] = game.current_player
    forbidden = game.is_double_three(5, 5)
    assert forbidden is True

def test_no_double_three():
    """Test a valid move that should not be restricted by the double-three rule."""
    game = Gomoku()
    game.board[5, 4] = game.current_player
    game.board[5, 6] = game.current_player
    game.board[4, 5] = -game.current_player
    game.board[6, 5] = -game.current_player
    
    # Ajout d'une pierre qui ne crée pas de double-trois
    game.board[5, 5] = game.current_player
    forbidden = game.is_double_three(5, 5)
    assert forbidden is False

def test_capture_rule():
    """Test capturing opponent stones."""
    game = Gomoku()
    game.current_player = PlayerToken.BLACK.value
    game.board[5, 5] = game.current_player
    game.board[5, 6] = -game.current_player
    game.board[5, 7] = -game.current_player
    game._check_capture_and_update(5, 8)
    # Les pierres capturées sont supprimées et le joueur actuel reçoit des points
    assert game.board[5, 6] == 0
    assert game.board[5, 7] == 0
    assert game.black_player_pebbles_taken == 2

def test_no_capture():
    """Ensure no capture happens if the configuration is invalid."""
    game = Gomoku()
    game.current_player = PlayerToken.BLACK.value
    game.board[5, 5] = game.current_player
    game.board[5, 6] = -game.current_player
    game.board[5, 7] = game.current_player
    captured = game._check_capture_and_update(5, 8)
    assert captured is False
    assert game.board[5, 6] == -game.current_player
    assert game.black_player_pebbles_taken == 0