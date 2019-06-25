from games.game import Game
import discord

class adlibs(Game):
        def __init__(self):
            Game.__init__(self, "Ad-Libs", "Add your own text to a story!", 1, 4)