"""
* Problem statement: Build the object-oriented design for a two-player Connect Four game. Player take turns dropping discs into a 7-column,
        6-row board. The first to align four of their discs vertically, horizontally, or diagonally wins.
        
* Requirements:
    1. Two player take turns dropping disc into 7 col and 6 row board.
    2. Disc falls into the lowest available row in chosen column.
    3. Game ends:
        - Win: When a player gets 4 in a row, column or diagonal.
        - Draw: Board gets full i.e. no more legal move available.
    4. Invalid moves should be rejected (Error handling): 
        - Players not allowed to place disc in already full column
        - Players not allowed to move out of turn
        - Players not allowed to move after game ends
"""

from enum import Enum
from typing import Optional

LINE_DIRECTIONS = (
    (0, 1),   # Horizontal
    (1, 0),   # Vertical
    (1, 1),   # Diagonal
    (1, -1),  # Anti-diagonal
)


class DiscColor(Enum):
    RED = "Red" # Player1 color
    BLUE = "Blue" # Player2 color


class GameState(Enum):
    IN_PROGRESS = "In Progress"
    WON = "Won"
    DRAW = "Draw"


class Player:
    def __init__(self, name: str, color: DiscColor) -> None:
        self.color = color
        self.name = name

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, player_name: str) -> None:
        if not player_name or not player_name.strip():
            raise ValueError("Player name cannot be empty.")
        self.__name = player_name.strip()


class Game:
    def __init__(self, player1: Player, player2: Player) -> None:
        self._validate_players(player1, player2)
        
        self.__player1 = player1
        self.__player2 = player2

        self.__currentPlayer = player1 # Player1 makes the first move

        self.__board = Board()

        self.__state = GameState.IN_PROGRESS

        self.__winner: Optional[Player] = None # Player is null in case of draw or in_progress
    
    @staticmethod
    def _validate_players(player1: Player, player2: Player):
        if player1 is player2:
            raise ValueError("Players must be different.")
        
        if player1.color == player2.color:
            raise ValueError("Players must choose different colors.")

    @property
    def player1(self):
        return self.__player1
    
    @property
    def player2(self):
        return self.__player2

    @property
    def winner(self):
        return self.__winner
    
    @property
    def currentPlayer(self):
        return self.__currentPlayer
    
    @property
    def state(self):
        return self.__state
    
    @property
    def board(self):
        return self.__board
    
    
    def makeMove(self, player: Player, column: int) -> bool:
        """
        Core logic:
            - place Disc
            - check win 
            - if not, check for draw
            - switch turn
        Edge case:
            - Game is already over (win or draw)
            - Wrong player turn
        """

        if self.state != GameState.IN_PROGRESS:
            return False
        
        if self.currentPlayer != player:
            # Caller needs to try/catch the error, otherwise the game would break with an invalid move
            raise ValueError(f"Invalid turn for player: {player.name}, {player.color.value}")
        
        row = self.board.placeDisc(column, player.color)
        if row == -1:
            return False

        if self.board.checkWin(row, column, player.color):
            self.__state = GameState.WON
            self.__winner = player
            return True

        if self.board.isFull():
            self.__state = GameState.DRAW
            return True
        
        # Switch turn
        if self.currentPlayer == self.player1:
            self.__currentPlayer = self.player2
        else: 
            self.__currentPlayer = self.player1
        
        return True

class Board:
    def __init__(self, rows: int = 6, cols: int = 7) -> None:
        self.__rows = rows
        self.__cols = cols
        self.__grid: list[list[Optional[DiscColor]]] = [
            [None] * cols for _ in range(rows)
        ]
    
    @ property
    def rows(self):
        return self.__rows
    
    @property
    def cols(self):
        return self.__cols

    def copy(self) -> 'Board':
        """Return an independent deep copy of this board."""
        clone = Board(self.__rows, self.__cols)
        for r in range(self.__rows):
            for c in range(self.__cols):
                clone.__grid[r][c] = self.__grid[r][c]
        return clone

    def _in_bounds(self, r, c):
        if (
            r < 0 or r >= self.rows or 
            c < 0 or c >= self.cols
        ):
            return False
        return True

    def getCell(self, row, column):
        return self.__grid[row][column]

    def isFull(self) -> bool:
        return all(cell is not None for row in self.__grid for cell in row)
    
    # check only the top cell of that column
    def _canPlace(self, column: int) -> bool:
        if column < 0 or column >= self.cols:
            return False
        return self.__grid[0][column] is None

    def placeDisc(self, column: int, color: DiscColor) -> int:
        # Out of bound column index
        if column < 0 or column >= self.cols:
            return -1
        
        # Column is full 
        if not self._canPlace(column):
            return -1

        for row in range(self.rows - 1, -1, -1):
            if self.__grid[row][column] is None:
                self.__grid[row][column] = color
                return row
        return -1 

    def clearCell(self, row: int, column: int) -> bool:
        if not self._in_bounds(row, column):
            return False
        self.__grid[row][column] = None
        return True
    
    def checkWin(self, row: int, column: int, color: DiscColor) -> bool:
        """
        Core logic:
        - check for 4 in a row in all 4 directions (horizontal, vertical, diagonal, anti-diagonal)
        Edge Case:
        - row, column out of bounds
        - cell (row, column) not match the given disc color
        """

        if not self._in_bounds(row, column):
            return False 
        
        if self.getCell(row, column) != color:
            return False 
        
        for dr, dc in LINE_DIRECTIONS:
            count = 1
            count += self._countInDirection(row, column, dr, dc, color) 
            count += self._countInDirection(row, column, -dr, -dc, color) # Count in opposite direction

            if count >= 4: 
                return True
            
        return False
    
    def _countInDirection(self, row, column, dr, dc, color):
        count = 0
        r = row + dr
        c = column + dc

        while (
            self._in_bounds(r, c) and 
            self.getCell(r, c) == color
        ):
            count += 1
            r += dr
            c += dc 
        return count
