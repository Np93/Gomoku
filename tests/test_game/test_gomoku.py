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
    move_pos = {"row": 5, "col": 5}
    # Position initiale avec une configuration double-trois
    game.board[5, 4] = game.current_player
    game.board[5, 3] = game.current_player
    game.board[4, 5] = game.current_player
    game.board[3, 5] = game.current_player
    # Double trois à 5,5 est interdit
    forbidden, message = game.is_move_forbidden(move_pos)
    print(forbidden, message)
    assert forbidden is True
    assert message == "Mouvement interdit : double-trois détecté"

def test_no_double_three():
    """Test a valid move that should not be restricted by the double-three rule."""
    game = Gomoku()
    move_pos = {"row": 5, "col": 5}
    game.board[5, 4] = game.current_player
    game.board[5, 6] = game.current_player
    game.board[4, 5] = -game.current_player
    game.board[6, 5] = -game.current_player
    # Ce mouvement ne crée pas de double-trois et devrait être permis
    forbidden, message = game.is_move_forbidden(move_pos)
    assert forbidden is False
    assert message == "Mouvement autorisé"

def test_capture_rule():
    """Test capturing opponent stones."""
    game = Gomoku()
    game.current_player = PlayerToken.BLACK.value
    game.board[5, 5] = game.current_player
    game.board[5, 6] = -game.current_player
    game.board[5, 7] = -game.current_player
    move_pos = {"row": 5, "col": 8}
    game.check_capture_and_update(move_pos)
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
    move_pos = {"row": 5, "col": 8}
    captured = game.check_capture_and_update(move_pos)
    assert captured is False
    assert game.board[5, 6] == -game.current_player
    assert game.black_player_pebbles_taken == 0