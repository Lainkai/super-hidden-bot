import discord
from discord.ext.commands import Context

import asyncio

import calendar
import time

import logging

import abc

gLogger = logging.getLogger()
gLogger.setLevel(logging.DEBUG)

class Game():
    min_players = 1
    def __init__(self,client:discord.Client, ctx, name:str="Game",desc:str="Template",rules:dict=None, min_players:int=1, max_players:int=None, enabled=False):
        self.name = name
        self.desc = desc
        self.min_players = min_players
        self.egg_elapsed = 0
        self.started = False
        self.ended = False
        self.players = []
        self.client = client
        self.ctx = ctx
        self.rules = rules
        self.enabled = enabled 
        if max_players!=None:
           self.max_players = 127
        else:
            self.max_players = max_players

    async def start_game(self):
        if not self.ready or self.started:
            return 1
        self.started = True
        print("Game: {0} Started".format(self.name))
    
    async def end_game(self):
        self.ended = True
        try:
            self.client.active_games.pop(self.ctx.channel)
        except KeyError:
            pass
        print("Game: {0} Ended".format(self.name))

    async def game_action(self, args, **kwargs):
        coro = getattr(self, kwargs.pop("command"))
        await coro(args, kwargs)

    async def addPlayer(self, user:discord.User):
        if not self.started:
            self.players.append(user)
            await self.ctx.channel.send(user.mention + " has been added!")

    async def egg_players(self):
        if time.time() - self.egg_elapsed >= 15:
            self.egg_elapsed = time.time()
            await self.ctx.channel.send("{0} out of {1} players needed!".format(self.min_players-len(self.players),self.min_players))

    async def ready_timeout(self):
        
        await asyncio.sleep(60)
        if self.ended:
            return
        if not self.started:
            await self.end_game()
            await self.ctx.channel.send("I guess no one really wanted to play. . . :cry:")

    async def send_rules(self):
        embed = discord.Embed(title="Rules", description="The rules of the game!", color=0xfe4a49)
        if self.rules is None or len(self.rules)<1 or not isinstance(self.rules,dict):
            embed.add_field(name="There are none!", value="Good luck!")
        else:
            for name, value in self.rules.items():
                embed.add_field(name=name,value=value)
        await self.ctx.channel.send(embed=embed)

    async def ready(self):
        if isinstance(self.ctx.channel,discord.DMChannel) and self.min_players > 1:
            await self.ctx.channel.send("This game is not possible, for there are not enough members.")
            await self.end_game()
        if isinstance(self.ctx.channel, discord.GroupChannel) and self.min_players > len(self.ctx.channel.recipients)-1:
            await self.ctx.channel.send("This game is not possible, for there are not enough members.")
            await self.end_game()
        if isinstance(self.ctx.channel, discord.TextChannel) and self.min_players > len(self.ctx.channel.members)-1:
            await self.ctx.channel.send("This game is not possible, for there are not enough members.")
            await self.end_game()

        if self.ended:
            return

        await self.send_rules()
        
        self.ready = False

        async def wait_for_players():
            async with self.ctx.channel.typing():
                while not self.ready:
                    if self.ended:
                        return
                    if self.min_players <= len(self.players):
                        self.ready = True
                        continue
                    await self.egg_players()
                    await asyncio.sleep(1)
        
        try:
            await asyncio.wait_for(wait_for_players(),60)
        except asyncio.TimeoutError as timout:
            await self.ctx.channel.send("Oh well. . . I guess not enough people want to play. . . :cry:")
            await self.end_game()

        prefix = await self.client.get_prefix(self.ctx.message)
        if not self.ended:
            await self.ctx.channel.send("Ready! Type {0}start".format(prefix))

        self.client.loop.create_task(self.ready_timeout())
