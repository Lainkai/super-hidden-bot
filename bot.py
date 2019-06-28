import asyncio

import logging
import os

import re

import discord
from discord.ext import commands
from discord.ext.commands import Bot

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

gLogger = logging.getLogger()
gLogger.setLevel(logging.DEBUG)

class GaiaBot(Bot):

    class ActiveGameWorker():
        
        def __init__(self, bot):
            self.bot = bot
            self.enabled = True
            self.bot.loop.create_task(self.monitor())

        def disable(self):
            self.enabled = False
        
        def enable(self):
            self.enabled = True
        
        async def monitor(self):
            await self.bot.wait_until_ready()
            while self.bot.active:
                if self.enabled:
                    ended_games = []
                    for g in self.bot.active_games:
                        if self.bot.active_games[g].ended:
                            ended_games.append(g)
                    for g in ended_games:
                        self.bot.active_games.pop(g)
                await asyncio.sleep(0.125)

    def __init__(self):
        Bot.__init__(self,'G#',description="Ree")
        self.active_games = {}
        self.active = True
        self.game_worker = self.ActiveGameWorker(self)

    async def end_all_games(self):

        self.game_worker.disable()

        await self.change_presence(status=discord.Status.dnd)

        for g in self.active_games:
            await self.active_games[g].end_game()
        
        self.game_worker.enable()


gaiaBot = GaiaBot()

def get_game(module_name, ctx):
    parts = ("games.{0}.{0}".format(module_name)).split('.')
    module = ".".join(parts[:-1])
    m = __import__( module )
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m(gaiaBot,ctx)

async def bot_owner(ctx):
    return ctx.author.id == 352258945995243525

async def end_game_worthy(ctx):
    try:
        game_starter = gaiaBot.active_games[ctx.channel].ctx.message.author
        if ctx.message.author == game_starter:
            return True
        elif ctx.message.author.top_role() > game_starter.top_role():
            return True
        else:
            return False
    except KeyError:
        return True
    if isinstance(ctx.channel, discord.DMChannel) or isinstance(ctx.channel, discord.GroupChannel):
        return True
    else:
        return False

async def show_library(ctx):
    selection = discord.Embed(title="Game Selection", description="Please choose one of the following games.", color=0xfe4a49)
    game_count = 1
    for g in os.listdir('games'):
        try:
            if not g.split('.',1)[1] == "py":
                continue
        except IndexError:
            continue
        g = g.split('.',1)[0]
        if g == 'game':
            continue
        try:
            game = get_game(g,ctx)
            if not game.enabled:
                continue
            gLogger.info("Getting {0}".format(game.name))
            selection.add_field(name="{0}. {1}".format(game_count,game.name), value=game.desc,inline=False)
            game_count+=1
        except ModuleNotFoundError:
            pass

    await ctx.channel.send(content=ctx.author.mention,embed=selection)


@gaiaBot.event
async def on_ready():
    print("Ready!")
    await gaiaBot.change_presence(status=discord.Status.idle,activity=discord.Activity(name="for when you get a life.",type=discord.ActivityType.watching))

@gaiaBot.command(name='exit')
@commands.check(bot_owner)
async def exit(ctx):
    await ctx.channel.send("Bye-Bye :wave::wave:")
    await gaiaBot.end_all_games()
    await gaiaBot.logout()

@gaiaBot.command(name="play")
async def playGame(ctx, *gameid):
    """
        Starts a game given the correct id. If no correct id is found, a library of the games will be sent.
    """
    game_id = ""

    for idx, s in enumerate(gameid):
        if idx == 0:
            game_id = s
        else:
            game_id += " {0}".format(s)

    if(game_id):
        if ctx.channel in gaiaBot.active_games:
            await ctx.channel.send("{0} Oops! I am already playing a game with someone else right now. :confused: Please try again later.".format(ctx.message.author.mention), delete_after=10)
            try:
                await ctx.message.delete(delay=10)
            except discord.Forbidden:
                gLogger.warning("No permission to do stuff")
            return None
        try:
            matches = re.findall("[a-z]", game_id.lower())
            game_file = ""
            for m in matches:
                game_file+=m
            
            if game_file == "":
                    matches = re.findall("[0-9]", game_id)
                    for m in matches:
                        game_file+=m

                    num = 1
                    for g in os.listdir('games'):
                        try:
                            if not g.split('.',1)[1] == "py":
                                continue
                        except IndexError:
                            continue
                        if g == 'game.py':
                            continue
                        if num == int(game_file):
                            game_file = g.split('.',1)[0]
                            game = get_game(game_file,ctx)
                            if not game.enabled:
                                game_file = ""
                                for m in matches:
                                    game_file+=m
                                continue
                            break
                        num+=1
            else:
                game = get_game(game_file,ctx)

            gLogger.debug(game_file)
            if not game.enabled:
                raise ModuleNotFoundError

            if gaiaBot.game_worker.enabled:
                gaiaBot.active_games[ctx.channel] = game

                gLogger.debug("Loading Game #{0}, {1}".format(game_id,game.name))
                await ctx.channel.send("Loading {0}".format(game.name))

                loadTask = gaiaBot.loop.create_task(game.ready())
                await game.addPlayer(ctx.message.author)

            else:
                await ctx.channel.send("I am sorry, but I am in the process of shutting down.")

        except ModuleNotFoundError:
            gLogger.warning("Game not found: {0}".format(game_id))
            await ctx.channel.send("Sorry, but I am not familiar with the game {0}. Ask the developer if the game has been disabled".format(game_id))
            await show_library(ctx)

    else:
        await show_library(ctx)

@gaiaBot.command(name="start")
@commands.check(end_game_worthy)
async def start_game(ctx):
    try:
        await gaiaBot.active_games[ctx.channel].start_game()
    except KeyError:
        await ctx.channel.send("Start what game?")

@gaiaBot.command(name="end-game")
@commands.check(end_game_worthy)
async def endGame(ctx):
    try:
        await gaiaBot.active_games[ctx.channel].end_game()
        await ctx.channel.send("Game SUCCessfully ended.")
    except KeyError:
        await ctx.channel.send("No game to be seen.")

@gaiaBot.command(name="join")
async def addPlayer(ctx):
    try:
        await gaiaBot.active_games[ctx.channel].addPlayer(ctx.author)
    except KeyError:
        await ctx.channel.send("No game to add you to!")

@gaiaBot.command(name="do")
async def playGame(ctx, *argv):
    try:
        args = list(argv)
        comm = args.pop(0)
        args = tuple(args)
        await gaiaBot.active_games[ctx.channel].game_action(args,command=comm,sender=ctx.author)
    except KeyError:
        await ctx.channel.send("Do what lol.")
        

gaiaBot.run(open("token.txt").read())
