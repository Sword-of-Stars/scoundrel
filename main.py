import os
import sys
from scripts.game import Game
from scripts.input_validation import validate_input
import random

#random.seed(42)

game = Game()

while True:
    os.system("cls")
    game.reset()
    game.run()

    if not validate_input("Play again? (y/n) "):
        break
