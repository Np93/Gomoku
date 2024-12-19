import pytest
from src.game.gomoku import Gomoku
from src.game.playerTokens import PlayerToken

class TestCaptureMechanism:

	@pytest.fixture # This decorator is used to set up the game instance before each test
	def setup_game(self):
		"""Set up a basic Gomoku game instance."""
		return Gomoku()

	def test_capture_horizontal(self, setup_game):
		game = setup_game
		game.board[4, 3] = PlayerToken.WHITE.value
		game.board[4, 4] = PlayerToken.WHITE.value
		game.board[4, 5] = PlayerToken.BLACK.value

		game.current_player = PlayerToken.BLACK.value
		assert game._process_capture(4, 2) is True
		assert game.board[4, 3] == 0
		assert game.board[4, 4] == 0
		assert game.black_player_pebbles_taken == 2

	def test_no_capture_vertical(self, setup_game):
		game = setup_game
		game.board[3, 4] = PlayerToken.WHITE.value
		game.board[4, 4] = PlayerToken.WHITE.value
		game.board[6, 4] = PlayerToken.BLACK.value

		game.current_player = PlayerToken.BLACK.value
		assert game._process_capture(5, 4) is False
		assert game.board[3, 4] == PlayerToken.WHITE.value
		assert game.board[4, 4] == PlayerToken.WHITE.value
		assert game.black_player_pebbles_taken == 0

	def test_capture_diagonal(self, setup_game):
		game = setup_game
		game.board[3, 3] = PlayerToken.WHITE.value
		game.board[4, 4] = PlayerToken.WHITE.value
		game.board[5, 5] = PlayerToken.BLACK.value

		game.current_player = PlayerToken.BLACK.value
		assert game._process_capture(2, 2) is True
		assert game.board[3, 3] == 0
		assert game.board[4, 4] == 0
		assert game.black_player_pebbles_taken == 2

	def test_edge_case_out_of_bounds(self, setup_game):
		game = setup_game
		game.board[0, 1] = PlayerToken.WHITE.value
		game.board[0, 2] = PlayerToken.WHITE.value
		game.board[0, 3] = PlayerToken.BLACK.value

		game.current_player = PlayerToken.BLACK.value
		assert game._process_capture(0, 0) is True
		assert game.board[0, 1] == 0
		assert game.board[0, 2] == 0
		assert game.black_player_pebbles_taken == 2

	def test_no_false_positive(self, setup_game):
		game = setup_game
		game.board[4, 3] = PlayerToken.WHITE.value
		game.board[4, 4] = PlayerToken.BLACK.value
		game.board[4, 5] = PlayerToken.WHITE.value

		game.current_player = PlayerToken.BLACK.value
		assert game._process_capture(4, 2) is False
		assert game.board[4, 3] == PlayerToken.WHITE.value
		assert game.board[4, 4] == PlayerToken.BLACK.value
		assert game.board[4, 5] == PlayerToken.WHITE.value
		assert game.black_player_pebbles_taken == 0

class TestFivePebbleAlignment:

	@pytest.fixture
	def setup_game(self):
		"""Set up a basic Gomoku game instance."""
		return Gomoku()

	def test_horizontal_five_in_row(self, setup_game):
		game = setup_game
		# Place a horizontal line of 5 pebbles
		game.board[5, 5] = PlayerToken.BLACK.value
		game.board[5, 6] = PlayerToken.BLACK.value
		game.board[5, 7] = PlayerToken.BLACK.value
		game.board[5, 8] = PlayerToken.BLACK.value
		game.current_player = PlayerToken.BLACK.value

		assert game._has_5_pebbles_aligned(5, 4) is True

	def test_vertical_five_in_row(self, setup_game):
		game = setup_game
		# Place a vertical line of 5 pebbles
		game.board[5, 5] = PlayerToken.WHITE.value
		game.board[6, 5] = PlayerToken.WHITE.value
		game.board[7, 5] = PlayerToken.WHITE.value
		game.board[8, 5] = PlayerToken.WHITE.value
		game.current_player = PlayerToken.WHITE.value

		assert game._has_5_pebbles_aligned(4, 5) is True

	def test_diagonal_five_in_row(self, setup_game):
		game = setup_game
		# Place a diagonal line of 5 pebbles (positive slope)
		game.board[5, 5] = PlayerToken.BLACK.value
		game.board[6, 6] = PlayerToken.BLACK.value
		game.board[7, 7] = PlayerToken.BLACK.value
		game.board[8, 8] = PlayerToken.BLACK.value
		game.current_player = PlayerToken.BLACK.value

		assert game._has_5_pebbles_aligned(4, 4) is True

	def test_anti_diagonal_five_in_row(self, setup_game):
		game = setup_game
		# Place an anti-diagonal line of 5 pebbles (negative slope)
		game.board[5, 9] = PlayerToken.WHITE.value
		game.board[6, 8] = PlayerToken.WHITE.value
		game.board[7, 7] = PlayerToken.WHITE.value
		game.board[8, 6] = PlayerToken.WHITE.value
		game.current_player = PlayerToken.WHITE.value

		assert game._has_5_pebbles_aligned(4, 10) is True

	def test_no_alignment(self, setup_game):
		game = setup_game
		# Place an incomplete line of 4 pebbles
		game.board[5, 5] = PlayerToken.BLACK.value
		game.board[5, 6] = PlayerToken.BLACK.value
		game.board[5, 7] = PlayerToken.BLACK.value
		game.current_player = PlayerToken.BLACK.value

		assert game._has_5_pebbles_aligned(5, 8) is False

	def test_edge_case_board_boundary(self, setup_game):
		game = setup_game
		# Place a line near the board's edge
		game.board[0, 15] = PlayerToken.BLACK.value
		game.board[0, 16] = PlayerToken.BLACK.value
		game.board[0, 17] = PlayerToken.BLACK.value
		game.board[0, 18] = PlayerToken.BLACK.value
		game.current_player = PlayerToken.BLACK.value

		assert game._has_5_pebbles_aligned(0, 14) is True

	def test_overlapping_lines(self, setup_game):
		game = setup_game
		# Place overlapping horizontal and vertical lines
		game.board[5, 5] = PlayerToken.BLACK.value
		game.board[5, 6] = PlayerToken.BLACK.value
		game.board[5, 7] = PlayerToken.BLACK.value
		game.board[5, 8] = PlayerToken.BLACK.value
		game.board[5, 9] = PlayerToken.BLACK.value

		game.board[4, 7] = PlayerToken.BLACK.value
		game.board[6, 7] = PlayerToken.BLACK.value
		game.board[7, 7] = PlayerToken.BLACK.value
		game.board[8, 7] = PlayerToken.BLACK.value

		game.current_player = PlayerToken.BLACK.value

		# Should detect horizontal alignment
		assert game._has_5_pebbles_aligned(5, 7) is True

	def test_mixed_tokens(self, setup_game):
		game = setup_game
		# Place mixed tokens breaking the alignment
		game.board[5, 5] = PlayerToken.BLACK.value
		game.board[5, 6] = PlayerToken.BLACK.value
		game.board[5, 7] = PlayerToken.WHITE.value
		game.board[5, 8] = PlayerToken.BLACK.value
		game.board[5, 9] = PlayerToken.BLACK.value
		game.current_player = PlayerToken.BLACK.value

		assert game._has_5_pebbles_aligned(5, 4) is False

	def test_more_than_five_in_row(self, setup_game):
		game = setup_game
		# Place a horizontal line of 7 pebbles
		game.board[5, 5] = PlayerToken.BLACK.value
		game.board[5, 6] = PlayerToken.BLACK.value
		game.board[5, 7] = PlayerToken.BLACK.value
		game.board[5, 8] = PlayerToken.BLACK.value
		game.board[5, 9] = PlayerToken.BLACK.value
		game.board[5, 10] = PlayerToken.BLACK.value
		game.board[5, 11] = PlayerToken.BLACK.value
		game.current_player = PlayerToken.BLACK.value

		assert game._has_5_pebbles_aligned(5, 7) is True

class TestIs5PebbleAlignedBreakable:

	@pytest.fixture
	def setup_game(self):
		"""Set up a basic Gomoku game instance."""
		return Gomoku()

	def test_unbreakable_line(self, setup_game):
		# Scenario: A line of 5 Black stones formed, and White has no move to break it.
		game = setup_game

		# Place a horizontal line of 5 Black stones on row 10, columns 5-9
		for col in range(5, 10):
			game.board[10, col] = PlayerToken.BLACK.value

		game.current_player = PlayerToken.BLACK.value
		placed_row, placed_col = 10, 9  # Black just placed at (10,9)

		# No White stones placed strategically, so no captures or blocks are possible.
		# Assume get_all_possible_moves(White) returns empty or irrelevant moves that don't break the line.
		assert game._has_5_pebbles_aligned(placed_row, placed_col) is True
		assert game._is_5_pebbles_aligned_breakable(placed_row, placed_col) is False

	def test_breakable_by_capture_of_exact_two_stones(self, setup_game):
		game = setup_game

		game.board[10, 2] = PlayerToken.BLACK.value
		game.board[10, 3] = PlayerToken.BLACK.value
		game.board[10, 4] = PlayerToken.BLACK.value
		game.board[10, 5] = PlayerToken.BLACK.value
		
		game.board[11, 5] = PlayerToken.WHITE.value
		game.board[9, 5] = PlayerToken.BLACK.value
  
		# Black makes the final move to form 5 in a row
		game.current_player = PlayerToken.BLACK.value
		game.board[10, 6] = PlayerToken.BLACK.value
		placed_row, placed_col = 10, 6
  
		assert game._has_5_pebbles_aligned(placed_row, placed_col) is True
		assert game._is_5_pebbles_aligned_breakable(placed_row, placed_col) is True

	def test_no_break_possible(self, setup_game):
		# A scenario where, though Black has formed a line of 5, White has no capturing or blocking move
		# that would remove or disrupt the alignment.
		game = setup_game
		# Black line fully formed:
		for col in range(5, 10):
			game.board[10, col] = PlayerToken.BLACK.value
		# No White stones placed in threatening positions:
		game.current_player = PlayerToken.BLACK.value
		placed_row, placed_col = 10, 9

		assert game._has_5_pebbles_aligned(placed_row, placed_col) is True
		assert game._is_5_pebbles_aligned_breakable(placed_row, placed_col) is False

class TestIs10Pebbles:

	@pytest.fixture
	def setup_game(self):
		"""Set up a basic Gomoku game instance."""
		return Gomoku()

	def test_black_player_has_10_pebbles(self, setup_game):
		game = setup_game
		game.black_player_pebbles_taken = 10
		game.current_player = PlayerToken.BLACK.value

		assert game._has_10_pebbles() is True

	def test_black_player_has_less_than_10_pebbles(self, setup_game):
		game = setup_game
		game.black_player_pebbles_taken = 9
		game.current_player = PlayerToken.BLACK.value

		assert game._has_10_pebbles() is False

	def test_white_player_has_10_pebbles(self, setup_game):
		game = setup_game
		game.white_player_pebbles_taken = 10
		game.current_player = PlayerToken.WHITE.value

		assert game._has_10_pebbles() is True

	def test_white_player_has_less_than_10_pebbles(self, setup_game):
		game = setup_game
		game.white_player_pebbles_taken = 9
		game.current_player = PlayerToken.WHITE.value

		assert game._has_10_pebbles() is False

	class TestDoubleThreeDetection:

		@pytest.fixture
		def setup_game(self):
			"""Set up a basic Gomoku game instance."""
			return Gomoku()

		def test_double_three_horizontal_and_vertical(self, setup_game):
			game = setup_game
			# Horizontal three at (5,4) to (5,6)
			game.board[5, 4] = PlayerToken.BLACK.value
			game.board[5, 5] = PlayerToken.BLACK.value
			game.board[5, 6] = PlayerToken.BLACK.value
			# Vertical three at (4,5) to (6,5)
			game.board[4, 5] = PlayerToken.BLACK.value
			game.board[6, 5] = PlayerToken.BLACK.value

			# Place pebble at (5,5) to create a double three
			game.current_player = PlayerToken.BLACK.value
			assert game._is_double_three(5, 5) is True

		def test_no_double_three_with_interruption(self, setup_game):
			game = setup_game
			# Horizontal line interrupted by a White pebble
			game.board[5, 4] = PlayerToken.BLACK.value
			game.board[5, 6] = PlayerToken.BLACK.value
			game.board[5, 5] = PlayerToken.WHITE.value
			# Vertical line interrupted by a White pebble
			game.board[4, 5] = PlayerToken.BLACK.value
			game.board[6, 5] = PlayerToken.BLACK.value

			# Place pebble at (5,5) (which is already White) to check no double three
			game.current_player = PlayerToken.BLACK.value
			assert game._is_double_three(5, 5) is False

		def test_double_three_with_diagonal_and_horizontal(self, setup_game):
			game = setup_game
			# Diagonal line (positive slope)
			game.board[4, 4] = PlayerToken.BLACK.value
			game.board[5, 5] = PlayerToken.BLACK.value
			game.board[6, 6] = PlayerToken.BLACK.value
			# Horizontal line
			game.board[5, 3] = PlayerToken.BLACK.value
			game.board[5, 4] = PlayerToken.BLACK.value

			# Place pebble at (5,5) to create a double three
			game.current_player = PlayerToken.BLACK.value
			assert game._is_double_three(5, 5) is True

		def test_no_double_three_with_incomplete_lines(self, setup_game):
			game = setup_game
			# Incomplete horizontal line
			game.board[5, 4] = PlayerToken.BLACK.value
			# Incomplete diagonal line
			game.board[6, 6] = PlayerToken.BLACK.value

			# Place pebble at (5,5) should not create a double three
			game.current_player = PlayerToken.BLACK.value
			assert game._is_double_three(5, 5) is False

		def test_double_three_detects_correct_player(self, setup_game):
			game = setup_game
			# Horizontal three for Black
			game.board[5, 4] = PlayerToken.BLACK.value
			game.board[5, 5] = PlayerToken.BLACK.value
			game.board[5, 6] = PlayerToken.BLACK.value
			# Vertical three for White
			game.board[4, 6] = PlayerToken.WHITE.value
			game.board[6, 6] = PlayerToken.WHITE.value

			# Place pebble at (5,6) for Black should not count White's potential lines
			game.current_player = PlayerToken.BLACK.value
			assert game._is_double_three(5, 6) is False


			@pytest.fixture
			def setup_game(self):
				"""Set up a basic Gomoku game instance."""
				return Gomoku()

			def test_crochet_double_three(self, setup_game):
				game = setup_game
				game.board[5, 5] = PlayerToken.BLACK.value
				game.board[6, 5] = PlayerToken.BLACK.value
				game.board[7, 6] = PlayerToken.BLACK.value
				game.board[7, 7] = PlayerToken.BLACK.value
				
				# Place a pebble that creates a double three at (5,7)
				game.current_player = PlayerToken.BLACK.value
				game.board[7, 5] = PlayerToken.BLACK.value

				assert game._is_double_three(7, 5) is True

			def test_diagonal_close_double_three(self, setup_game):
				game = setup_game
				game.board[5, 5] = PlayerToken.BLACK.value
				game.board[6, 5] = PlayerToken.BLACK.value
				game.board[6, 6] = PlayerToken.BLACK.value
				game.board[5, 7] = PlayerToken.BLACK.value
				
				# Place a pebble that creates a double three at (4,4)
				game.current_player = PlayerToken.BLACK.value
				game.board[7, 5] = PlayerToken.BLACK.value

				assert game._is_double_three(7, 5) is True


			def test_diagonal_close_not_double_three(self, setup_game):
				game = setup_game
				game.board[5, 5] = PlayerToken.BLACK.value
				game.board[6, 5] = PlayerToken.BLACK.value
				game.board[6, 6] = PlayerToken.BLACK.value
				game.board[5, 7] = PlayerToken.BLACK.value
				game.board[8, 5] = PlayerToken.BLACK.value
				
				# Place a pebble that creates a double three at (4,4)
				game.current_player = PlayerToken.BLACK.value
				game.board[7, 5] = PlayerToken.BLACK.value

				assert game._is_double_three(7, 5) is False