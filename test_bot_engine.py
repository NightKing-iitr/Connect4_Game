from bot_engine import BotEngine
from connect_four import Board, DiscColor, Game, Player


def _build_game(moves: list[int]) -> Game:
    game = Game(Player("Red", DiscColor.RED), Player("Blue", DiscColor.BLUE))
    for column in moves:
        assert game.makeMove(game.currentPlayer, column) is True
    return game


def _snapshot_board(board: Board) -> tuple[tuple[DiscColor | None, ...], ...]:
    return tuple(
        tuple(board.getCell(row, column) for column in range(board.cols))
        for row in range(board.rows)
    )


def _placement_state(board: Board) -> tuple[bool, ...]:
    return tuple(board._canPlace(column) for column in range(board.cols))


def _build_board_from_moves(moves: list[int]) -> Board:
    return _build_game(moves).board


def test_bot_takes_immediate_winning_move() -> None:
    game = _build_game([0, 0, 1, 1, 2])
    bot = BotEngine(bot_color=DiscColor.RED, opponent_color=DiscColor.BLUE, max_depth=4)

    assert bot.choseMove(game.board) == 3


def test_bot_blocks_opponent_immediate_winning_move() -> None:
    game = _build_game([0, 0, 1, 1, 2])
    bot = BotEngine(bot_color=DiscColor.BLUE, opponent_color=DiscColor.RED, max_depth=4)

    assert bot.choseMove(game.board) == 3


def test_bot_prefers_center_on_empty_board() -> None:
    board = Board()
    bot = BotEngine(bot_color=DiscColor.BLUE, opponent_color=DiscColor.RED, max_depth=4)

    assert bot.choseMove(board) == 3


def test_chose_move_does_not_mutate_board_state() -> None:
    game = _build_game([3, 2, 3, 2, 4, 1])
    bot = BotEngine(bot_color=DiscColor.RED, opponent_color=DiscColor.BLUE, max_depth=4)
    before_cells = _snapshot_board(game.board)
    before_placements = _placement_state(game.board)

    move = bot.choseMove(game.board)

    assert move in range(game.board.cols)
    assert _snapshot_board(game.board) == before_cells
    assert _placement_state(game.board) == before_placements


def test_incremental_score_matches_full_recomputation_on_fixed_boards() -> None:
    bot = BotEngine(bot_color=DiscColor.RED, opponent_color=DiscColor.BLUE, max_depth=4)
    position_sets = [
        [],
        [3],
        [3, 2, 3, 2, 4, 1],
        [0, 0, 1, 1, 2],
        [0, 1, 0, 1, 0, 2],
        [0, 1, 1, 2, 2, 5, 2, 3],
    ]

    for moves in position_sets:
        board = _build_board_from_moves(moves)
        score_before = bot._evaluate_board_full_reference(board)

        for color in (bot.bot_color, bot.opponent_color):
            for column in range(board.cols):
                row = board.placeDisc(column, color)
                if row == -1:
                    continue

                delta = bot._score_delta_for_move(board, row, column, color)
                assert score_before + delta == bot._evaluate_board_full_reference(board)
                assert bot._evaluate_board_full_reference(board) == bot._evaluate_board(board)
                assert board.clearCell(row, column) is True
                assert bot._evaluate_board_full_reference(board) == score_before


def test_undo_restores_exact_original_score() -> None:
    board = _build_board_from_moves([3, 2, 3, 2, 4, 1])
    bot = BotEngine(bot_color=DiscColor.RED, opponent_color=DiscColor.BLUE, max_depth=4)
    original_score = bot._evaluate_board_full_reference(board)
    original_cells = _snapshot_board(board)

    row = board.placeDisc(3, bot.bot_color)
    assert row != -1
    delta = bot._score_delta_for_move(board, row, 3, bot.bot_color)
    assert original_score + delta == bot._evaluate_board_full_reference(board)

    assert board.clearCell(row, 3) is True
    assert _snapshot_board(board) == original_cells
    assert bot._evaluate_board_full_reference(board) == original_score


def test_incremental_and_reference_bot_choose_same_move_on_fixed_positions() -> None:
    bot = BotEngine(bot_color=DiscColor.RED, opponent_color=DiscColor.BLUE, max_depth=4)
    positions = [
        [],
        [3, 2, 3, 2, 4, 1],
        [0, 1, 0, 1, 0, 2],
        [0, 1, 1, 2, 2, 5, 2, 3],
    ]

    for moves in positions:
        board_incremental = _build_board_from_moves(moves)
        board_reference = _build_board_from_moves(moves)
        assert bot.choseMove(board_incremental) == bot._choose_move_reference(board_reference)
