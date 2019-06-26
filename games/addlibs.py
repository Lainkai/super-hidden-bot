from games.game import Game
import discord
import asyncio

class addlibs(Game):

        def __init__(self):
            Game.__init__(self, "Add-Libs", "Add your own text to a story!", 1, 4)
            self.players=[]

        async def ready(self,client:discord.Client, ctx):
            await ctx.channel.send("The rules are as follows `blah blah `__noun__` blah`")
            try:
                await asyncio.wait_for(super(addlibs, self).ready(client,ctx),60)
            except asyncio.TimeoutError:
                await ctx.channel.send("Oh well. . . I guess not enough people want to play. . . :cry:")
                client.active_games.pop(ctx.channel)
            