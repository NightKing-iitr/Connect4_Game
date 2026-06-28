from connect_four import Game, Player, DiscColor, GameState
from bot_engine import BotEngine

humanPlayer = Player("Alex", DiscColor.RED) # Player_1
botPlayer = Player("Bot", DiscColor.BLUE) # Player_2

game = Game(humanPlayer, botPlayer)

bot = BotEngine()

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
        print("Bot to move...")
        column = bot.choseMove(game.board)

    game.makeMove(current, column)
    game.board.display_grid()

    

if game.state == GameState.DRAW:
    print("Game drawn")

elif game.state == GameState.WON:
    winner = game.winner
    print(f"Winner: {winner.name}, Color: {winner.color.value}") #type: ignore
