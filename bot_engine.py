from typing import Optional

from connect_four import Board, DiscColor


class BotEngine:
    def __init__(
            self, 
            bot_color: DiscColor = DiscColor.BLUE, 
            opponent_color: DiscColor = DiscColor.RED, 
            max_depth: int = 5
            ) -> None:
        self.bot_color = bot_color
        self.opponent_color = opponent_color
        self.max_depth = max_depth

    def choseMove(self, game_board: Board) -> int:
        legal_columns = [column for column in range(game_board.cols) if game_board._canPlace(column)]
        if not legal_columns:
            return -1

        # Bot plays the immediate winning move  
        for column in self._ordered_columns(game_board):
            if self._would_win(game_board, column, self.bot_color):
                return column

        # Block the human player immediate winning move on next turn
        for column in self._ordered_columns(game_board):
            if self._would_win(game_board, column, self.opponent_color):
                return column

        return self._get_minimax_move(game_board)

    # Return the best possible move based on 'Minimax' algorithm
    def _get_minimax_move(self, game_board: Board) -> int:
        best_score = float("-inf")
        best_move = -1

        for column in self._ordered_columns(game_board):
            row = game_board.placeDisc(column, self.bot_color)
            if row == -1:
                continue

            score = self._minimax(game_board, self.max_depth - 1, False, float("-inf"), float("inf"))
            game_board.clearCell(row, column)
            if score > best_score:
                best_score = score
                best_move = column

        return best_move

    # Sort the possible available columns by its closeness to the center
    def _ordered_columns(self, game_board: Board) -> list[int]:
        center = game_board.cols // 2
        return sorted([column for column in range(game_board.cols) 
                       if game_board._canPlace(column)], key=lambda column: abs(column - center))

    def _would_win(self, board: Board, column: int, color: DiscColor) -> bool:
        row = board.placeDisc(column, color)
        if row == -1:
            return False
        did_win = board.checkWin(row, column, color)
        board.clearCell(row, column)
        return did_win

    def _minimax(self, board: Board, depth: int, is_maximizing: bool, alpha: float, beta: float) -> float:
        if depth == 0 or board.isFull():
            return self._evaluate_board(board)

        legal_columns = [column for column in range(board.cols) if board._canPlace(column)]
        if not legal_columns:
            return 0.0

        ordered_columns = self._ordered_columns(board)

        # Bot trying to maximize the score
        if is_maximizing:
            best_score = float("-inf")
            for column in ordered_columns:
                row = board.placeDisc(column, self.bot_color)
                if row == -1:
                    continue

                if board.checkWin(row, column, self.bot_color):
                    board.clearCell(row, column)
                    return 100000 + depth

                score = self._minimax(board, depth - 1, False, alpha, beta)
                board.clearCell(row, column)
                best_score = max(best_score, score)
                alpha = max(alpha, score) # alpha-beta pruning
                if beta <= alpha:
                    break
            return best_score

        # Human opponent trying to minimize the score 
        best_score = float("inf")
        for column in ordered_columns:
            row = board.placeDisc(column, self.opponent_color)
            if row == -1:
                continue

            if board.checkWin(row, column, self.opponent_color):
                board.clearCell(row, column)
                return -100000 - depth

            score = self._minimax(board, depth - 1, True, alpha, beta)
            board.clearCell(row, column)
            best_score = min(best_score, score)
            beta = min(beta, score) # alpha-beta pruning
            if beta <= alpha:
                break
        return best_score

    """
    Heuristic function
        - prefer positions that create winning opportunities for bot
        - penalize positions that create winning opportunities for the human
        - favour central control
    """
    def _evaluate_board(self, board: Board) -> float:
        score = 0.0

        center_column = board.cols // 2
        center_count = sum(1 for row in range(board.rows) if board.getCell(row, center_column) == self.bot_color)
        score += center_count * 4
        center_count = sum(1 for row in range(board.rows) if board.getCell(row, center_column) == self.opponent_color)
        score -= center_count * 4

        for row in range(board.rows):
            for column in range(board.cols):
                cell = board.getCell(row, column)
                if cell is None:
                    continue

                color = self.bot_color if cell == self.bot_color else self.opponent_color
                for direction in [(0, 1), (1, 0), (1, 1), (1, -1)]:
                    window = []
                    for step in range(4):
                        r = row + direction[0] * step
                        c = column + direction[1] * step
                        if 0 <= r < board.rows and 0 <= c < board.cols:
                            window.append(board.getCell(r, c))
                        else:
                            window.append(None)

                    score += self._score_window(window, color)

        return score

    def _score_window(self, window: list[Optional[DiscColor]], color: DiscColor) -> float:
        opponent = self.opponent_color if color == self.bot_color else self.bot_color
        count_color = window.count(color)
        count_opponent = window.count(opponent)
        count_empty = window.count(None)

        if count_color == 4:
            return 100000.0
        if count_opponent == 4:
            return -100000.0
        if count_color > 0 and count_opponent == 0:
            if count_color == 3 and count_empty == 1:
                return 100.0
            if count_color == 2 and count_empty == 2:
                return 10.0
            if count_color == 1 and count_empty == 3:
                return 1.0
        if count_opponent > 0 and count_color == 0:
            if count_opponent == 3 and count_empty == 1:
                return -120.0
            if count_opponent == 2 and count_empty == 2:
                return -12.0
            if count_opponent == 1 and count_empty == 3:
                return -1.0
        return 0.0
