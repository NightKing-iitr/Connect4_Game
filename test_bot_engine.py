from typing import Optional

import pytest

from bot_engine import BotEngine
from connect_four import Board, DiscColor, Game, GameState, Player


def _build_game(moves: list[int]) -> Game:
    game = Game(Player("Red", DiscColor.RED), Player("Blue", DiscColor.BLUE))
    for column in moves:
        assert game.makeMove(game.currentPlayer, column) is True
    return game


def _build_board(moves: list[int]) -> Board:
    return _build_game(moves).board


def _snapshot_board(board: Board) -> tuple[tuple[Optional[DiscColor], ...], ...]:
    return tuple(
        tuple(board.getCell(row, column) for column in range(board.cols))
        for row in range(board.rows)
    )


def _placement_state(board: Board) -> tuple[bool, ...]:
    return tuple(board._canPlace(column) for column in range(board.cols))


def _play_scripted_first_player_game(
    depth: int, scripted_moves: list[int]
) -> tuple[GameState, Optional[str], int]:
    human = Player("ScriptedHuman", DiscColor.RED)
    bot_player = Player("Bot", DiscColor.BLUE)
    game = Game(human, bot_player)
    bot = BotEngine(bot_color=bot_player.color, opponent_color=human.color, max_depth=depth)

    used_moves = 0
    while game.state == GameState.IN_PROGRESS:
        current = game.currentPlayer
        if current == human:
            assert used_moves < len(scripted_moves), f"script exhausted at move {used_moves + 1}"
            column = scripted_moves[used_moves]
            used_moves += 1
            assert game.board._canPlace(column), f"illegal scripted move {column} at move {used_moves}"
        else:
            column = bot.choseMove(game.board)

        assert game.makeMove(current, column) is True

    winner_name = game.winner.name if game.winner is not None else None
    return game.state, winner_name, used_moves


@pytest.fixture
def red_bot() -> BotEngine:
    return BotEngine(bot_color=DiscColor.RED, opponent_color=DiscColor.BLUE, max_depth=4)


@pytest.fixture
def blue_bot() -> BotEngine:
    return BotEngine(bot_color=DiscColor.BLUE, opponent_color=DiscColor.RED, max_depth=4)


@pytest.mark.parametrize(
    ("moves", "expected_column"),
    [
        ([0, 0, 1, 1, 2], 3),
    ],
)
def test_bot_takes_immediate_winning_move(
    red_bot: BotEngine, moves: list[int], expected_column: int
) -> None:
    game = _build_game(moves)

    assert red_bot.choseMove(game.board) == expected_column


@pytest.mark.parametrize(
    ("moves", "expected_column"),
    [
        ([0, 0, 1, 1, 2], 3),
    ],
)
def test_bot_blocks_opponent_immediate_winning_move(
    blue_bot: BotEngine, moves: list[int], expected_column: int
) -> None:
    game = _build_game(moves)

    assert blue_bot.choseMove(game.board) == expected_column


def test_bot_prefers_center_on_empty_board(blue_bot: BotEngine) -> None:
    assert blue_bot.choseMove(Board()) == 3


def test_chose_move_does_not_mutate_board_state(red_bot: BotEngine) -> None:
    board = _build_board([3, 2, 3, 2, 4, 1])
    before_cells = _snapshot_board(board)
    before_placements = _placement_state(board)

    move = red_bot.choseMove(board)

    assert move in range(board.cols)
    assert _snapshot_board(board) == before_cells
    assert _placement_state(board) == before_placements


@pytest.mark.parametrize(
    "moves",
    [
        [],
        [3],
        [3, 2, 3, 2, 4, 1],
        [0, 0, 1, 1, 2],
        [0, 1, 0, 1, 0, 2],
        [0, 1, 1, 2, 2, 5, 2, 3],
    ],
)
def test_incremental_score_matches_full_recomputation_on_fixed_boards(
    red_bot: BotEngine, moves: list[int]
) -> None:
    board = _build_board(moves)
    score_before = red_bot._evaluate_board_full_reference(board)

    for color in (red_bot.bot_color, red_bot.opponent_color):
        for column in range(board.cols):
            row = board.placeDisc(column, color)
            if row == -1:
                continue

            delta = red_bot._score_delta_for_move(board, row, column, color)
            assert score_before + delta == red_bot._evaluate_board_full_reference(board)
            assert red_bot._evaluate_board(board) == red_bot._evaluate_board_full_reference(board)
            assert board.clearCell(row, column) is True
            assert red_bot._evaluate_board_full_reference(board) == score_before


def test_undo_restores_exact_original_score(red_bot: BotEngine) -> None:
    board = _build_board([3, 2, 3, 2, 4, 1])
    original_score = red_bot._evaluate_board_full_reference(board)
    original_cells = _snapshot_board(board)

    row = board.placeDisc(3, red_bot.bot_color)
    assert row != -1

    delta = red_bot._score_delta_for_move(board, row, 3, red_bot.bot_color)
    assert original_score + delta == red_bot._evaluate_board_full_reference(board)

    assert board.clearCell(row, 3) is True
    assert _snapshot_board(board) == original_cells
    assert red_bot._evaluate_board_full_reference(board) == original_score


@pytest.mark.parametrize(
    "moves",
    [
        [],
        [3, 2, 3, 2, 4, 1],
        [0, 1, 0, 1, 0, 2],
        [0, 1, 1, 2, 2, 5, 2, 3],
    ],
)
def test_incremental_and_reference_bot_choose_same_move_on_fixed_positions(
    red_bot: BotEngine, moves: list[int]
) -> None:
    board_incremental = _build_board(moves)
    board_reference = _build_board(moves)

    assert red_bot.choseMove(board_incremental) == red_bot._choose_move_reference(board_reference)


@pytest.mark.parametrize(
    ("depth", "expected_state", "expected_winner", "scripted_moves"),
    [
        (1, GameState.WON, "ScriptedHuman", [3, 3, 3, 3, 4, 2, 4, 1, 4, 0, 0, 0, 0]),
        (2, GameState.WON, "ScriptedHuman", [3, 3, 3, 3, 4, 2, 4, 0, 0, 0, 6, 5]),
        (3, GameState.WON, "ScriptedHuman", [3, 4, 3, 2, 3, 1, 4, 5, 1, 5, 4, 4, 6, 6]),
        (5, GameState.WON, "ScriptedHuman", [3, 5, 2, 2, 2, 4, 1, 3, 0, 0, 5, 6, 2, 0, 6, 6, 6, 4]),
        (8, GameState.WON, "ScriptedHuman", [3, 0, 3, 0, 3, 2, 4, 2, 3, 4, 5, 2, 0, 0, 0, 5, 1]),
        (8, GameState.DRAW, None, [3, 4, 3, 5, 6, 4, 6, 2, 1, 3, 0, 2, 1, 2, 4, 1, 6, 5, 6, 0, 0]),
    ],
)
def test_perfect_play_regressions_as_first_player(
    depth: int,
    expected_state: GameState,
    expected_winner: Optional[str],
    scripted_moves: list[int],
) -> None:
    state, winner_name, used_moves = _play_scripted_first_player_game(depth, scripted_moves)

    assert used_moves == len(scripted_moves)
    assert state == expected_state
    assert winner_name == expected_winner
