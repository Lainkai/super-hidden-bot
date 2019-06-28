from games.game import Game
import discord
import asyncio

import logging

gLogger = logging.getLogger()
gLogger.setLevel(logging.DEBUG)

class wumpussadventure(Game):
        
        def __init__(self, client:discord.Client, ctx):
            Game.__init__(self, client, ctx, "Wumpus's Adventure!", "Text Adventure","Follow the story of wumpus", 2, 4, True)