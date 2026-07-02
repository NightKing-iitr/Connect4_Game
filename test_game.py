from connect_four import Game, GameState, Board, DiscColor, Player

import pytest


def _build_game(game: Game, moves: list[int]) -> Game:
    for column in moves:
        assert game.makeMove(game.currentPlayer, column) is True
    return game


def _build_board(game: Game, moves: list[int]) -> Board:
    return _build_game(game, moves).board


@pytest.fixture 
def red_player() -> Player:
    return Player("Alex", DiscColor.RED)


@pytest.fixture
def blue_player() -> Player:
    return Player("John", DiscColor.BLUE)


def test_player_rejects_empty_name():
    with pytest.raises(ValueError):
        Player("  ", DiscColor.BLUE)


def test_game_rejects_duplicate_players(red_player: Player):
    with pytest.raises(ValueError):
        Game(red_player, red_player)


def test_game_rejects_player_with_same_color(red_player: Player):
    with pytest.raises(ValueError):
        Game(red_player, Player("Invalid", DiscColor.RED))


@pytest.fixture
def game(red_player, blue_player) -> Game:
    return Game(red_player, blue_player)


def test_game_starts_with_red_player(game, red_player):
    assert game.state == GameState.IN_PROGRESS
    assert game.currentPlayer == red_player


def test_game_rejects_wrong_turn(game: Game, red_player, blue_player):
    assert game.currentPlayer == red_player
    game.makeMove(red_player, 1)

    assert game.board.getCell(5, 1) == DiscColor.RED # Cell updated to red color 
    assert game.currentPlayer == blue_player # Game turn changed to blue player

    with pytest.raises(ValueError):
        game.makeMove(red_player, 2) # Invalid player


@pytest.mark.parametrize(
        "moves",
        [
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 1, 0, 0]
        ]
)
def test_board_rejects_placement_in_full_column(
    game: Game,
    moves: list[int]
):
    board = _build_board(game, moves)

    assert board._canPlace(0) == False # Column_0 is full 

    assert game.makeMove(game.currentPlayer, 0) == False
    assert board.placeDisc(0, game.currentPlayer.color) == -1

def test_board_clear_cell(game: Game):
    moves = [0, 0, 0, 0, 0, 0]
    undo_board = _build_board(game, moves) # Column_0 is full 

    assert undo_board.getCell(0, 0) == DiscColor.BLUE # Top cell of Column_0
    assert undo_board.clearCell(0, 0) == True
    assert undo_board.getCell(0, 0) == None # Cell empty

    assert undo_board.clearCell(6, 0) == False # Invalid cell: out of bounds


@pytest.mark.parametrize(
        "moves",
        [
            [0, 1, 0, 1, 0, 1, 0], # Vertical 
            [0, 0, 1, 1, 2, 2, 3], # Horizontal
            [0, 1, 1, 2, 2, 3, 2, 3, 3, 0, 3] # Diagonal
            # Add anti-diagonal winning moves for 1st player
        ]
) 
def test_winning_moves(game: Game, moves: list[int]):
    board = _build_board(game, moves)

    assert game.state == GameState.WON
    assert game.winner == game.player1 # Moves for first player to win

    # No moves after Won state
    assert game.makeMove(game.currentPlayer, 6) == False # No valid moves after game ends 


def test_draw_moves(game: Game):
    draw_moves = [
        0, 0, 0, 0, 0, 0,
        1, 1, 1, 1, 1, 1, 
        2, 2, 2, 2, 2, 2, 
        4, 3, 3, 3, 3, 3, 
        3, 4, 4, 4, 4, 4, 
        5, 5, 5, 5, 5, 5, 
        6, 6, 6, 6, 6, 6
    ]
    draw_game = _build_game(game, draw_moves)

    assert draw_game.state == GameState.DRAW
    assert draw_game.winner is None
    assert draw_game.board.isFull() == True
    assert draw_game.makeMove(draw_game.currentPlayer, 0) == False
