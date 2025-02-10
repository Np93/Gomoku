import pytest
from cpp_gomoku import Gomoku
from src.game.playerTokens import PlayerToken

class TestCaptureMechanism:

	@pytest.fixture # This decorator is used to set up the game instance before each test
	def setup_game(self):
		"""Set up a basic Gomoku game instance."""
		return Gomoku()

	def test_capture_horizontal(self, setup_game):
		game = setup_game
		game.addTiles([(4, 3), (4, 4)], PlayerToken.WHITE.value)  # White pieces
		game.addTiles([(4, 5)], PlayerToken.BLACK.value)  # Black pieces

		game.setCurrentPlayer(PlayerToken.BLACK.value)
		game.processMove(4, 2)[0]
		
		assert game.getBoardValue(4, 3) == 0
		assert game.getBoardValue(4, 4) == 0
		assert game.getBlackPlayerPebblesTaken() == 2

	def test_no_capture_vertical(self, setup_game):
		game = setup_game
		game.addTiles([(3, 4), (4, 4)], PlayerToken.WHITE.value)  # White pieces
		game.addTiles([(6, 4)], PlayerToken.BLACK.value)  # Black piece

		game.setCurrentPlayer(PlayerToken.BLACK.value)
		game.processMove(5, 4)[0]

		assert game.getBoardValue(3, 4) == PlayerToken.WHITE.value
		assert game.getBoardValue(4, 4) == PlayerToken.WHITE.value
		assert game.getBlackPlayerPebblesTaken() == 0

	def test_capture_diagonal(self, setup_game):
		game = setup_game
		game.addTiles([(3, 3), (4, 4)], PlayerToken.WHITE.value)  # White pieces
		game.addTiles([(5, 5)], PlayerToken.BLACK.value)  # Black piece

		game.setCurrentPlayer(PlayerToken.BLACK.value)
		game.processMove(2, 2)[0]

		assert game.getBoardValue(3, 3) == 0
		assert game.getBoardValue(4, 4) == 0
		assert game.getBlackPlayerPebblesTaken() == 2

	def test_edge_case_out_of_bounds(self, setup_game):
		game = setup_game
		game.addTiles([(0, 1), (0, 2)], PlayerToken.WHITE.value)  # White pieces
		game.addTiles([(0, 3)], PlayerToken.BLACK.value)  # Black piece

		game.setCurrentPlayer(PlayerToken.BLACK.value)
		game.processMove(0, 0)[0]

		assert game.getBoardValue(0, 1) == 0
		assert game.getBoardValue(0, 2) == 0
		assert game.getBlackPlayerPebblesTaken() == 2

	def test_no_false_positive(self, setup_game):
		game = setup_game
		game.addTiles([(4, 3)], PlayerToken.WHITE.value)  # White piece
		game.addTiles([(4, 4)], PlayerToken.BLACK.value)  # Black piece
		game.addTiles([(4, 5)], PlayerToken.WHITE.value)  # White piece

		game.setCurrentPlayer(PlayerToken.BLACK.value)
		game.processMove(4, 2)[0]

		assert game.getBoardValue(4, 3) == PlayerToken.WHITE.value
		assert game.getBoardValue(4, 4) == PlayerToken.BLACK.value
		assert game.getBoardValue(4, 5) == PlayerToken.WHITE.value
		assert game.getBlackPlayerPebblesTaken() == 0

class TestFivePebbleAlignment:

    @pytest.fixture
    def setup_game(self):
        """Set up a basic Gomoku game instance."""
        return Gomoku()

    def test_horizontal_five_in_row(self, setup_game):
        game = setup_game
        # Place a horizontal line of 5 pebbles
        game.addTiles([(5, 5), (5, 6), (5, 7), (5, 8)], PlayerToken.BLACK.value)
        game.setCurrentPlayer(PlayerToken.BLACK.value)

        assert game.process5Pebbles(5, 4) is True

    def test_vertical_five_in_row(self, setup_game):
        game = setup_game
        # Place a vertical line of 5 pebbles
        game.addTiles([(5, 5), (6, 5), (7, 5), (8, 5)], PlayerToken.WHITE.value)
        game.setCurrentPlayer(PlayerToken.WHITE.value)

        assert game.process5Pebbles(4, 5) is True

    def test_diagonal_five_in_row(self, setup_game):
        game = setup_game
        # Place a diagonal line of 5 pebbles (positive slope)
        game.addTiles([(5, 5), (6, 6), (7, 7), (8, 8)], PlayerToken.BLACK.value)
        game.setCurrentPlayer(PlayerToken.BLACK.value)

        assert game.process5Pebbles(4, 4) is True

    def test_anti_diagonal_five_in_row(self, setup_game):
        game = setup_game
        # Place an anti-diagonal line of 5 pebbles (negative slope)
        game.addTiles([(5, 9), (6, 8), (7, 7), (8, 6)], PlayerToken.WHITE.value)
        game.setCurrentPlayer(PlayerToken.WHITE.value)

        assert game.process5Pebbles(4, 10) is True

    def test_no_alignment(self, setup_game):
        game = setup_game
        # Place an incomplete line of 4 pebbles
        game.addTiles([(5, 5), (5, 6), (5, 7)], PlayerToken.BLACK.value)
        game.setCurrentPlayer(PlayerToken.BLACK.value)

        assert game.process5Pebbles(5, 8) is False

    def test_edge_case_board_boundary(self, setup_game):
        game = setup_game
        # Place a line near the board's edge
        game.addTiles([(0, 15), (0, 16), (0, 17), (0, 18)], PlayerToken.BLACK.value)
        game.setCurrentPlayer(PlayerToken.BLACK.value)

        assert game.process5Pebbles(0, 14) is True

    def test_overlapping_lines(self, setup_game):
        game = setup_game
        # Place overlapping horizontal and vertical lines
        game.addTiles([(5, 5), (5, 6), (5, 7), (5, 8), (5, 9)], PlayerToken.BLACK.value)
        game.addTiles([(4, 7), (6, 7), (7, 7), (8, 7)], PlayerToken.BLACK.value)
        game.setCurrentPlayer(PlayerToken.BLACK.value)

        # Should detect horizontal alignment
        assert game.process5Pebbles(5, 7) is True

    def test_mixed_tokens(self, setup_game):
        game = setup_game
        # Place mixed tokens breaking the alignment
        game.addTiles([(5, 5), (5, 6), (5, 8), (5, 9)], PlayerToken.BLACK.value)
        game.addTiles([(5, 7)], PlayerToken.WHITE.value)
        game.setCurrentPlayer(PlayerToken.BLACK.value)

        assert game.process5Pebbles(5, 4) is False

    def test_more_than_five_in_row(self, setup_game):
        game = setup_game
        # Place a horizontal line of 7 pebbles
        game.addTiles([(5, 5), (5, 6), (5, 7), (5, 8), (5, 9), (5, 10), (5, 11)], PlayerToken.BLACK.value)
        game.setCurrentPlayer(PlayerToken.BLACK.value)

        assert game.process5Pebbles(5, 7) is True


# class TestIs5PebbleAlignedBreakable:

# 	@pytest.fixture
# 	def setup_game(self):
# 		"""Set up a basic Gomoku game instance."""
# 		return Gomoku()

# 	def test_unbreakable_line(self, setup_game):
# 		# Scenario: A line of 5 Black stones formed, and White has no move to break it.
# 		game = setup_game

# 		# Place a horizontal line of 5 Black stones on row 10, columns 5-9
# 		for col in range(5, 10):
# 			game.board[10, col] = PlayerToken.BLACK.value

# 		game.current_player = PlayerToken.BLACK.value
# 		placed_row, placed_col = 10, 9  # Black just placed at (10,9)

# 		# No White stones placed strategically, so no captures or blocks are possible.
# 		# Assume get_all_possible_moves(White) returns empty or irrelevant moves that don't break the line.
# 		assert game._has_5_pebbles_aligned(placed_row, placed_col) is True
# 		assert game._is_5_pebbles_aligned_breakable(placed_row, placed_col) is False

# 	def test_breakable_by_capture_of_exact_two_stones(self, setup_game):
# 		game = setup_game

# 		game.board[10, 2] = PlayerToken.BLACK.value
# 		game.board[10, 3] = PlayerToken.BLACK.value
# 		game.board[10, 4] = PlayerToken.BLACK.value
# 		game.board[10, 5] = PlayerToken.BLACK.value
		
# 		game.board[11, 5] = PlayerToken.WHITE.value
# 		game.board[9, 5] = PlayerToken.BLACK.value
  
# 		# Black makes the final move to form 5 in a row
# 		game.current_player = PlayerToken.BLACK.value
# 		game.board[10, 6] = PlayerToken.BLACK.value
# 		placed_row, placed_col = 10, 6
  
# 		assert game._has_5_pebbles_aligned(placed_row, placed_col) is True
# 		assert game._is_5_pebbles_aligned_breakable(placed_row, placed_col) is True

# 	def test_no_break_possible(self, setup_game):
# 		# A scenario where, though Black has formed a line of 5, White has no capturing or blocking move
# 		# that would remove or disrupt the alignment.
# 		game = setup_game
# 		# Black line fully formed:
# 		for col in range(5, 10):
# 			game.board[10, col] = PlayerToken.BLACK.value
# 		# No White stones placed in threatening positions:
# 		game.current_player = PlayerToken.BLACK.value
# 		placed_row, placed_col = 10, 9

# 		assert game._has_5_pebbles_aligned(placed_row, placed_col) is True
# 		assert game._is_5_pebbles_aligned_breakable(placed_row, placed_col) is False

# class TestIs10Pebbles:

# 	@pytest.fixture
# 	def setup_game(self):
# 		"""Set up a basic Gomoku game instance."""
# 		return Gomoku()

# 	def test_black_player_has_10_pebbles(self, setup_game):
# 		game = setup_game
# 		game.black_player_pebbles_taken = 10
# 		game.current_player = PlayerToken.BLACK.value

# 		assert game._has_10_pebbles() is True

# 	def test_black_player_has_less_than_10_pebbles(self, setup_game):
# 		game = setup_game
# 		game.black_player_pebbles_taken = 9
# 		game.current_player = PlayerToken.BLACK.value

# 		assert game._has_10_pebbles() is False

# 	def test_white_player_has_10_pebbles(self, setup_game):
# 		game = setup_game
# 		game.white_player_pebbles_taken = 10
# 		game.current_player = PlayerToken.WHITE.value

# 		assert game._has_10_pebbles() is True

# 	def test_white_player_has_less_than_10_pebbles(self, setup_game):
# 		game = setup_game
# 		game.white_player_pebbles_taken = 9
# 		game.current_player = PlayerToken.WHITE.value

# 		assert game._has_10_pebbles() is False

class TestDoubleThreeDetection:

    @pytest.fixture
    def setup_game(self):
        """Set up a basic Gomoku game instance."""
        return Gomoku()

    def test_double_three_horizontal_and_vertical(self, setup_game):
        game = setup_game
        # Horizontal three at (5,4) to (5,6)
        game.addTiles([(5, 4), (5, 5), (5, 6)], PlayerToken.BLACK.value)
        # Vertical three at (4,5) to (6,5)
        game.addTiles([(4, 5), (6, 5)], PlayerToken.BLACK.value)

        # Place pebble at (5,5) to create a double three
        game.setCurrentPlayer(PlayerToken.BLACK.value)
        assert game.isDoubleThree(5, 5) is True

    def test_no_double_three_with_interruption(self, setup_game):
        game = setup_game
        # Horizontal line interrupted by a White pebble
        game.addTiles([(5, 4), (5, 6)], PlayerToken.BLACK.value)
        game.addTiles([(5, 5)], PlayerToken.WHITE.value)
        # Vertical line interrupted by a White pebble
        game.addTiles([(4, 5), (6, 5)], PlayerToken.BLACK.value)

        # Check that (5,5) does not create a double three
        game.setCurrentPlayer(PlayerToken.BLACK.value)
        assert game.isDoubleThree(5, 5) is False

    def test_double_three_with_diagonal_and_horizontal(self, setup_game):
        game = setup_game
        # Diagonal line (positive slope)
        game.addTiles([(4, 4), (5, 5), (6, 6)], PlayerToken.BLACK.value)
        # Horizontal line
        game.addTiles([(5, 3), (5, 4)], PlayerToken.BLACK.value)

        # Place pebble at (5,5) to create a double three
        game.setCurrentPlayer(PlayerToken.BLACK.value)
        assert game.isDoubleThree(5, 5) is True

    def test_no_double_three_with_incomplete_lines(self, setup_game):
        game = setup_game
        # Incomplete horizontal line
        game.addTiles([(5, 4)], PlayerToken.BLACK.value)
        # Incomplete diagonal line
        game.addTiles([(6, 6)], PlayerToken.BLACK.value)

        # Place pebble at (5,5) should not create a double three
        game.setCurrentPlayer(PlayerToken.BLACK.value)
        assert game.isDoubleThree(5, 5) is False

    def test_double_three_detects_correct_player(self, setup_game):
        game = setup_game
        # Horizontal three for Black
        game.addTiles([(5, 4), (5, 5), (5, 6)], PlayerToken.BLACK.value)
        # Vertical three for White
        game.addTiles([(4, 6), (6, 6)], PlayerToken.WHITE.value)

        # Place pebble at (5,6) for Black should not count White's potential lines
        game.setCurrentPlayer(PlayerToken.BLACK.value)
        assert game.isDoubleThree(5, 6) is False

    def test_crochet_double_three(self, setup_game):
        game = setup_game
        game.addTiles([(5, 5), (6, 5), (7, 6), (7, 7)], PlayerToken.BLACK.value)
        
        # Place a pebble that creates a double three at (7,5)
        game.setCurrentPlayer(PlayerToken.BLACK.value)
        game.addTiles([(7, 5)], PlayerToken.BLACK.value)

        assert game.isDoubleThree(7, 5) is True

    def test_diagonal_close_double_three(self, setup_game):
        game = setup_game
        game.addTiles([(5, 5), (6, 5), (6, 6), (5, 7)], PlayerToken.BLACK.value)
        
        # Place a pebble that creates a double three at (7,5)
        game.setCurrentPlayer(PlayerToken.BLACK.value)
        game.addTiles([(7, 5)], PlayerToken.BLACK.value)

        assert game.isDoubleThree(7, 5) is True

    def test_diagonal_close_not_double_three(self, setup_game):
        game = setup_game
        game.addTiles([(5, 5), (6, 5), (6, 6), (5, 7), (8, 5)], PlayerToken.BLACK.value)
        
        # Place a pebble at (7,5), should not create a double three
        game.setCurrentPlayer(PlayerToken.BLACK.value)
        game.addTiles([(7, 5)], PlayerToken.BLACK.value)

        assert game.isDoubleThree(7, 5) is False