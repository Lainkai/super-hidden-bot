import discord
from discord.ext.commands import Context

import asyncio

import calendar
import time

class Game():
    min_players = 1
    def __init__(self,name:str="Game",desc:str="Template", min_players:int=1, max_players:int=None):
        self.name = name
        self.desc = desc
        self.min_players = min_players
        self.egg_elapsed = 0
        self.started = False
        self.ended = False
        if max_players!=None:
            max_players = 127

    async def start_game(self):
        if not self.ready:
            return
        self.started = True
        print("Game: {0} Started".format(self.name))
    
    async def end_game(self):
        self.ended = True
        try:
            self.client.active_games.pop(self.ctx.channel)
        except KeyError:
            pass
        print("Game: {0} Ended".format(self.name))

    async def addPlayer(self, user:discord.User):
        if not self.started:
            self.players.append(user)

    async def egg_players(self):
        if time.time() - self.egg_elapsed >= 15:
            self.egg_elapsed = time.time()
            await self.ctx.channel.send("{0} out of {1} players needed!".format(self.min_players-len(self.players),self.min_players))

    async def ready_timeout(self):
        print("what")
        await asyncio.sleep(10)
        if self.ended:
            return
        if not self.started:
            self.end_game()
            await self.ctx.channel.send("I guess no one really wanted to play. . . :cry:")

    async def ready(self, client:discord.Client, ctx:Context):
        self.client = client
        self.ctx = ctx
        self.ready = False

        async with ctx.channel.typing():
            while not self.ready:
                if self.ended:
                    return
                if self.min_players <= len(self.players):
                    self.ready = True
                    continue
                await self.egg_players()
                await asyncio.sleep(1)

        prefix = await client.get_prefix(ctx.message)
        await ctx.channel.send("Ready! Type {0}start".format(prefix))

        await self.client.loop.create_task(self.ready_timeout())
