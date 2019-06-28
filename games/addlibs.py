from games.game import Game
import discord
import asyncio

import logging
import os
from random import randint
import re

gLogger = logging.getLogger()
gLogger.setLevel(logging.DEBUG)

class addlibs(Game):

        def __init__(self, client:discord.Client, ctx):
            rules = {
                "You are assigned by your name next to the part of speech":"For example, \{1-Bak3dChips\}",
                "1s are Nouns":"Wherever you are assigned a \{1\}, make it a noun, like person.",
                "2s are Adjectives":"Wherever you are assigned a \{2\}, make it an adjective, like red.",
                "3s are Verbs":"Wherever you are assigned a \{3\}, make it an verb, like run, ran, running, etc.",
                "4s are Pronouns":"Wherever you are assigned a \{4\}, make it an pronoun, like he/she.",
                "5s are Numbers":"Wherever you are assigned a \{5\}, make it a number, like one or 1."
            }
            Game.__init__(self, client, ctx, "Add-Libs", "Add your own text to a story!",rules, 1, 4, True)

        async def start_game(self):
            start = await super().start_game()
            if start == 1:
                return
            games = os.listdir(os.getcwd()+"/games/addlibs/")
            game = games[randint(0,len(games)-1)]
            game = open(os.getcwd()+"/games/addlibs/"+game).read()

            def assign_roles(input):
                assign_locs = re.findall('(?<=-)(.*?)(?=})', input)
                """ Bak3dchips:[]"""
                user_id = 0
                for x in range(1,len(assign_locs)+1):
                    if user_id == len(self.players):
                        user_id = 0
                    player = self.players[user_id].display_name
                    input = re.sub('(?<=-)'+str(x)+'(?=})',player,input,1)
                    user_id+=1
                
                return input

            assigned_game=assign_roles(game)
            await self.ctx.channel.send("`"+assigned_game+"`")

            self.game = assigned_game

        async def help(self, args, kwargs):
            await self.ctx.channel.send("Use `do fill ` and then your responses.")
            
        async def fill(self, args, kwargs):
            user = kwargs["sender"]
            if user in self.players:
                for arg in args:
                    self.game = re.sub("{.{2}"+user.display_name+"}", "***"+arg+"***", self.game,1 )
            await self.ctx.channel.send(self.game)
            if re.search("{", self.game) == None:
                await self.ctx.channel.send("Hooray! You have completed the puzzle!")
                await self.end_game()
            

                
        async def repeat(self, args, kwargs):
            message = ""
            for arg in args:
                message = message+arg+" "
            await self.ctx.channel.send(message)
            