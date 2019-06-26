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

    def __init__(self):
        Bot.__init__(self,'#',description="Ree")
        self.active_games = {}

    def end_all_games(self):
        for g in self.active_games:
            self.active_games[g].end_game()
        

gaiaBot = GaiaBot()

def get_game(module_name):
    parts = ("games.{0}.{0}".format(module_name)).split('.')
    module = ".".join(parts[:-1])
    m = __import__( module )
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m()

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


@gaiaBot.event
async def on_ready():
    print("Ready!")
    await gaiaBot.change_presence(status=discord.Status.idle,activity=discord.Activity(name="for when you get a life.",type=discord.ActivityType.watching))

@gaiaBot.command(name='exit')
@commands.check(bot_owner)
async def exit(ctx):
    await ctx.channel.send("Bye-Bye :wave::wave:")
    gaiaBot.end_all_games()
    await gaiaBot.logout()

@gaiaBot.command(name="play")
async def playGame(ctx, game_id:str = None, level_id:str= None):
    """
        Starts a game given the correct id. If no correct id is found, a library of the games will be sent.
    """
    if(game_id):
        if ctx.channel in gaiaBot.active_games:
            await ctx.channel.send("{0} Oops! I am already playing a game with someone else right now. :confused: Please try again later.".format(ctx.message.author.mention), delete_after=10)
            try:
                ctx.message.delete(delay=10)
            except discord.Forbidden:
                print("OOFed\n\n")
            return None
        try:
            matches = re.findall("[a-z]", game_id.lower())
            game_file = ""
            for m in matches:
                game_file+=m
            logging.debug(game_file)
            game = get_game(game_file)

            gaiaBot.active_games[ctx.channel] = game

            logging.debug("Loading Game #{0}, {1}".format(game_id,game.name))
            await ctx.channel.send("Loading {0}".format(game.name))

            loadTask = gaiaBot.loop.create_task(game.ready(gaiaBot,ctx))
            await game.addPlayer(ctx.message.author)

        except ModuleNotFoundError:

            logging.warning("Game not found: {0}".format(game_id))
            await ctx.channel.send("Sorry, but I am not familiar with the game {0}".format(game_id))

    else:
        selection = discord.Embed(title="Game Selection", description="Please choose one of the following games.", colour=0xfe4a49)
        game_count = 1
        for g in os.listdir('games'):
            g = g.split('.',1)[0]
            if g == 'game' or g == '__pycache__' or g == "exp":
                continue
            try:
                game = get_game(g)
                logger.info("Getting {0}".format(game.name))
                selection.add_field(name="{0}. {1}".format(game_count,game.name), value=game.desc)
                game_count+=1
            except ModuleNotFoundError:
                pass

        await ctx.channel.send(content=ctx.author.mention,embed=selection)

@gaiaBot.command(name="end-game")
@commands.check(end_game_worthy)
async def endGame(ctx):
    try:
        await gaiaBot.active_games[ctx.channel].end_game()
        await ctx.channel.send("Game SUCCessfully ended.")
    except KeyError:
        await ctx.channel.send("No game to be seen.")


@gaiaBot.command(name="do")
async def playGame(ctx, *argv):

    pass
        

gaiaBot.run(open("token.txt").read())
