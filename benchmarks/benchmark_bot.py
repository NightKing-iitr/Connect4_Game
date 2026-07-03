"""
Performance benchmark for BotEngine minimax.

Run: python3 benchmarks/benchmark_bot.py
"""

import argparse
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from connect_four import Board, DiscColor, Game, GameState, Player
from bot_engine import BotEngine


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("value must be at least 1")
    return parsed


class InstrumentedBot(BotEngine):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.nodes_visited = 0

    def reset(self):
        self.nodes_visited = 0

    def _minimax(self, board, depth, is_maximizing, alpha, beta, current_score):
        self.nodes_visited += 1
        return super()._minimax(board, depth, is_maximizing, alpha, beta, current_score)


def _time_move(bot: InstrumentedBot, board: Board, runs: int = 7) -> tuple[float, float]:
    """Return (mean_ms, stdev_ms) over `runs` calls. Resets node count each run."""
    if runs < 1:
        raise ValueError("runs must be at least 1")

    times = []
    for _ in range(runs):
        bot.reset()
        t0 = time.perf_counter()
        bot.choseMove(board)
        times.append((time.perf_counter() - t0) * 1000)
    std_ms = statistics.stdev(times) if len(times) > 1 else 0.0
    return statistics.mean(times), std_ms


def _play_game(depth_red: int, depth_blue: int) -> str:
    """Play one full game. Returns 'red', 'blue', or 'draw'."""
    p1 = Player("Red", DiscColor.RED)
    p2 = Player("Blue", DiscColor.BLUE)
    game = Game(p1, p2)
    bot_red = BotEngine(bot_color=DiscColor.RED, opponent_color=DiscColor.BLUE, max_depth=depth_red)
    bot_blue = BotEngine(bot_color=DiscColor.BLUE, opponent_color=DiscColor.RED, max_depth=depth_blue)

    while game.state == GameState.IN_PROGRESS:
        current = game.currentPlayer
        col = bot_red.choseMove(game.board) if current == p1 else bot_blue.choseMove(game.board)
        game.makeMove(current, col)

    if game.state == GameState.WON:
        return "red" if game.winner == p1 else "blue"
    return "draw"


def bench_depth_scaling(depth_max: int, runs: int):
    print(f"\n{'=' * 60}")
    print("BENCHMARK 1: Depth scaling on an empty board")
    print(f"  {runs} timed runs per depth, node counts are deterministic")
    print(f"{'=' * 60}")
    print(f"{'Depth':<7} {'Nodes':>10} {'xPrev':>7} {'Mean ms':>10} {'Std ms':>8}")
    print("-" * 46)

    prev_nodes = None
    for depth in range(1, depth_max + 1):
        bot = InstrumentedBot(max_depth=depth)
        board = Board()

        mean_ms, std_ms = _time_move(bot, board, runs)

        bot.reset()
        bot.choseMove(board)
        nodes = bot.nodes_visited

        ratio = f"{nodes / prev_nodes:.1f}x" if prev_nodes else "-"
        print(f"{depth:<7} {nodes:>10,} {ratio:>7} {mean_ms:>10.1f} {std_ms:>8.1f}")
        prev_nodes = nodes

    print()
    print("  - Nodes xPrev shows the effective branching factor after alpha-beta pruning.")
    print("  - Higher ratios usually mean pruning or move ordering can improve.")


def bench_move_distribution(depth: int):
    print(f"\n{'=' * 60}")
    print(f"BENCHMARK 2: Per-move time across a full game (depth={depth})")
    print("  Shows how move time drops as the board fills up.")
    print(f"{'=' * 60}")
    print(f"{'Move':>5} {'Player':<8} {'Col':>4} {'Nodes':>10} {'ms':>8}")
    print("-" * 40)

    p1 = Player("Red", DiscColor.RED)
    p2 = Player("Blue", DiscColor.BLUE)
    game = Game(p1, p2)
    bot_red = InstrumentedBot(bot_color=DiscColor.RED, opponent_color=DiscColor.BLUE, max_depth=depth)
    bot_blue = InstrumentedBot(bot_color=DiscColor.BLUE, opponent_color=DiscColor.RED, max_depth=depth)

    move_num = 1
    while game.state == GameState.IN_PROGRESS:
        current = game.currentPlayer
        if current == p1:
            bot_red.reset()
            t0 = time.perf_counter()
            col = bot_red.choseMove(game.board)
            ms = (time.perf_counter() - t0) * 1000
            nodes = bot_red.nodes_visited
            label = "RED"
        else:
            bot_blue.reset()
            t0 = time.perf_counter()
            col = bot_blue.choseMove(game.board)
            ms = (time.perf_counter() - t0) * 1000
            nodes = bot_blue.nodes_visited
            label = "BLUE"

        game.makeMove(current, col)
        print(f"{move_num:>5} {label:<8} {col:>4} {nodes:>10,} {ms:>8.1f}")
        move_num += 1

    print()
    print(f"Result: {game.state.value}", end="")
    if game.winner:
        print(f" - {game.winner.name} wins")
    else:
        print()


def bench_strength(games_per_matchup: int):
    print(f"\n{'=' * 60}")
    print("BENCHMARK 3: Strength test (higher depth vs lower depth)")
    print(f"  {games_per_matchup} games per matchup.")
    print("  NOTE: Connect Four has a strong first-player advantage.")
    print("  Games alternate who goes first to control for this.")
    print(f"{'=' * 60}")
    print(f"{'Matchup':<22} {'Deeper wins':>12} {'Shallower':>10} {'Draws':>7} {'First-mv wins':>14}")
    print("-" * 68)

    matchups = [(5, 1), (5, 3), (5, 4), (3, 1)]

    for deep, shallow in matchups:
        deeper_wins = shallower_wins = draws = first_mover_wins = 0

        for i in range(games_per_matchup):
            first_is_deeper = (i % 2 == 0)

            if first_is_deeper:
                result = _play_game(deep, shallow)
                if result == "red":
                    deeper_wins += 1
                    first_mover_wins += 1
                elif result == "blue":
                    shallower_wins += 1
                else:
                    draws += 1
            else:
                result = _play_game(shallow, deep)
                if result == "blue":
                    deeper_wins += 1
                elif result == "red":
                    shallower_wins += 1
                    first_mover_wins += 1
                else:
                    draws += 1

        label = f"depth-{deep} vs depth-{shallow}"
        print(f"{label:<22} {deeper_wins:>12} {shallower_wins:>10} {draws:>7} {first_mover_wins:>14}")

    print()
    print("  - If first-player wins dominate, the heuristic still trails opening advantage.")
    print("  - Depth alone is not enough if move ordering and evaluation stay weak.")


def main():
    parser = argparse.ArgumentParser(description="BotEngine minimax benchmark")
    parser.add_argument("--depth-max", type=positive_int, default=8,
                        help="Maximum depth for the scaling benchmark (default: 8)")
    parser.add_argument("--timing-runs", type=positive_int, default=7,
                        help="Timed runs per depth in benchmark 1 (default: 7)")
    parser.add_argument("--move-dist-depth", type=positive_int, default=5,
                        help="Depth for per-move time distribution benchmark (default: 5)")
    parser.add_argument("--games", type=positive_int, default=10,
                        help="Games per matchup in the strength test (default: 10)")
    args = parser.parse_args()

    bench_depth_scaling(args.depth_max, args.timing_runs)
    bench_move_distribution(args.move_dist_depth)
    bench_strength(args.games)


if __name__ == "__main__":
    main()
