import argparse

from connect_four import Game, Player, DiscColor, GameState
from bot_engine import BotEngine

def main():
    parser = argparse.ArgumentParser(description="Play Connect4 against the bot")
    parser.add_argument("--depth", type=int, default= 3, help="Bot search depth") # Custom validation on depth
    parser.add_argument("--name", type=str, default="Alex", help="Human player name")

    args = parser.parse_args()

    if not 1 <= args.depth <= 10:
        parser.error("depth must be between 1 and 10")

    max_depth = args.depth
    player_name = args.name

    humanPlayer = Player(player_name, DiscColor.RED) # Player_1
    botPlayer = Player("Bot", DiscColor.BLUE) # Player_2

    game = Game(humanPlayer, botPlayer)

    bot = BotEngine(botPlayer.color, humanPlayer.color, max_depth)

    print(f"Connect4 game starts against Bot with depth: {max_depth}", "\n")

    while game.state == GameState.IN_PROGRESS:
        current = game.currentPlayer

        if current == humanPlayer:
            while True:
                try:
                    column = int(input(f"{current.name}, choose a column (0-6): "))
                except ValueError:
                    print("Please enter a valid integer.")
                    continue

                if 0 <= column <= 6 and game.board._canPlace(column):
                    break

                print("Please choose an available column between 0 and 6.")
        else:
            column = bot.choseMove(game.board)
            print(f"Bot chose column: {column}")

        game.makeMove(current, column)
        game.board.display_grid()
        print()

    if game.state == GameState.DRAW:
        print("Game drawn")

    elif game.state == GameState.WON:
        winner = game.winner
        print(f"Winner: {winner.name}, Color: {winner.color.value}") #type: ignore

if __name__ == "__main__":
    main()