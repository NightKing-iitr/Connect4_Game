# Repository Guidelines

## Project Structure & Module Organization
This repository uses a flat Python layout. Core game logic lives in `connect_four.py`, including `Game`, `Board`, `Player`, and enums. The bot AI and minimax evaluation logic live in `bot_engine.py`, while `game_loop.py` is the CLI entry point. Keep core game tests in `test_game.py` and BotEngine-specific coverage in `test_bot_engine.py`. Benchmark scripts and saved outputs live under `benchmarks/`.

## Build, Test, and Development Commands
Use the local virtual environment if available: `source .venv/bin/activate`.

- `python3 game_loop.py --name Alex --depth 3` runs the playable CLI game against the bot.
- `python3 test_game.py` checks the core game logic and game state consistency.
- `python3 pytest test_bot_engine.py` runs BotEngine regression and consistency against pre-defined moves.
- `python3 benchmarks/benchmark_bot.py` measures bot performance and search strength.
- `python3 benchmarks/benchmark_bot.py` runs a heavier benchmark performance test for minimax algorithm.


## Coding Style & Naming Conventions
Follow the existing Python style in the repo: 4-space indentation, type hints where helpful, and small object-oriented classes. Keep public class names in `PascalCase` (`BotEngine`, `GameState`) and methods/variables in `snake_case`. Match existing APIs when extending methods such as `makeMove`, `placeDisc`, or `checkWin`. Preserve heuristic behavior carefully: `BotEngine` shares win-detection concepts with `connect_four.py`, but its scoring directions and incremental evaluation logic should stay behaviorally identical to the full-reference evaluator.

## Testing Guidelines
Add rule, turn-order, draw, and win checks to `test_game.py`. Put bot-search, move-choice, incremental-score, undo-restore, and scripted perfect-play regressions in `test_bot_engine.py`. Prefer parametrized pytest cases for repeated board setups. For search or heuristic changes, verify `BotEngine.choseMove()` still matches `_choose_move_reference()` on fixed boards and re-run the `perfect_plays.txt` sequences across depths `1, 2, 3, 5, 8`.

## Commit & Pull Request Guidelines
Recent commits use short, imperative subjects such as `Restrict bot depth to 8` and scoped messages like `game_loop: support command-line args`. Keep commit titles concise, descriptive, and focused on one change, for example `Add BotEngine pytest regressions and benchmark fix`. Pull requests should explain the gameplay or bot behavior affected, list the validation commands you ran, and call out any benchmark or heuristic-impacting changes explicitly.