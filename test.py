from connect_four import *

print("Test module started...", "\n")

# Create players
p1 = Player("Alex", DiscColor.RED)

p2 = Player("John", DiscColor.BLUE)

# Validate player name
try: 
    player = Player("    ", DiscColor.BLUE)
except ValueError:
    print("Player 'empty name' rejected successfully.", "\n")

# Validate players creation: p1, p2
try:
    game = Game(p1, p1)
except ValueError:
    print("Same players rejected by the Game successfully.")

try: 
    game = Game(p1, Player("p3", DiscColor.RED))
except ValueError:
    print("Same colors chosen by both players rejected successfully.", "\n")

# Game start
game = Game(p1, p2)

assert game.state == GameState.IN_PROGRESS # Game in progress 
assert game.currentPlayer == p1 # Player1 to first move

# Validate wrong turn
try:
    game.makeMove(p2, 1)
except ValueError:
    print("Wrong turn rejected successfuly.", "\n")

game.makeMove(p1, 2)

assert game.board.getCell(5, 2) == DiscColor.RED # Cell updated
assert game.currentPlayer == p2 # Game turn switched to Player2 

game.makeMove(p2, 2)

assert game.board.getCell(4, 2) == DiscColor.BLUE # Place disk working

game.makeMove(p1, 2)
game.makeMove(p2, 2)
game.makeMove(p1, 2)
game.makeMove(p2, 2)

# Validate can't place in full column 
assert game.board._canPlace(2) == False
assert game.makeMove(p1, 2) == False
assert game.currentPlayer == p1


game.makeMove(p1, 3)
game.makeMove(p2, 3)
game.makeMove(p1, 4)
game.makeMove(p2, 4)
game.makeMove(p1, 5)

# Validate GameState 'WIN'
assert game.state == GameState.WON
assert game.winner == p1
assert game.makeMove(p2, 5) == False # No valid moves post game ends 

print("Win state validated successfully.")
game.board.display_grid() # Display game board 
print()



# Validate GameState 'DRAW'
draw_game = Game(Player("DrawPlayer1", DiscColor.RED), Player("DrawPlayer2", DiscColor.BLUE))
draw_moves = [
    0, 0, 0, 0, 0, 0,
    1, 1, 1, 1, 1, 1, 
    2, 2, 2, 2, 2, 2, 
    4, 3, 3, 3, 3, 3, 
    3, 4, 4, 4, 4, 4, 
    5, 5, 5, 5, 5, 5, 
    6, 6, 6, 6, 6, 6
]

for col in draw_moves:
    assert draw_game.makeMove(draw_game.currentPlayer, col) == True

assert draw_game.state == GameState.DRAW
assert draw_game.winner is None
assert draw_game.board.isFull() == True
assert draw_game.makeMove(draw_game.currentPlayer, 0) == False

print("Draw state validated successfully.")
draw_game.board.display_grid()
print()