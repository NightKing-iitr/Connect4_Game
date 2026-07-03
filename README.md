# Connect Four Game

A small Python Connect Four implementation with a CLI game and a minimax bot.

## Project Structure

- `connect_four.py` - core board, game, player, and rule logic.
- `bot_engine.py` - minimax bot and heuristic evaluation.
- `game_loop.py` - command-line interface for playing against the bot.
- `test_game.py` - game rule and state tests.
- `test_bot_engine.py` - bot search and move selection tests.
- `benchmarks/benchmark_bot.py` - performance benchmark script.
- `perfect_plays.txt` - reference perfect-play sequences.

## Run the game

From the repository root:

```bash
python3 game_loop.py --name Alex --depth 3
```

Options:
- `--name` - human player name (default: `Alex`)
- `--depth` - bot search depth between `1` and `8` (default: `3`)

## Run tests

```bash
python3 test_game.py
pytest test_bot_engine.py
```

## Notes

The bot uses alpha-beta minimax with center-weighted heuristic scoring.
