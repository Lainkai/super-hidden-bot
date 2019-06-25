import asyncio

import discord
from discord.ext import commands
from discord.ext.commands import Bot

class GaiaBot(Bot):

    games = {
        '1':"adlibs",
        '2':'noods'
    }

    async def end_all_games(self):
        print("REE")

gaiaBot = GaiaBot('#',description="Ree")

def get_game(module_name):
    parts = ("games.{0}.{0}".format(gaiaBot.games[module_name])).split('.')
    module = ".".join(parts[:-1])
    m = __import__( module )
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m()

async def bot_owner(ctx):
    return ctx.author.id == 352258945995243525

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

@gaiaBot.command(name="start")
async def startGame(ctx, game_id:str = None, level_id:str= None):
    """
        Starts a game given the correct id. If no correct id is found, a library of the games will be sent.
    """
    if(game_id):
        try:
            game = get_game(game_id)
            await ctx.channel.send("here is {0}".format(game.name))
        except ModuleNotFoundError:
            await ctx.channel.send("the fucc is {0}".format(gaiaBot.games[game_id]))
    else:
        selection = discord.Embed(title="Game Selection", description="Please choose one of the following games.", colour=0xfe4a49)
        for g in gaiaBot.games:
            try:
                game = get_game(g)
                print(game.name)
                selection.add_field(name=g+". "+game.name, value=game.desc)
            except ModuleNotFoundError:
                pass

        await ctx.channel.send(content=ctx.author.mention,embed=selection)

@gaiaBot.command(name="play")
async def playGame(ctx, *argv):
    for i in argv:
        print(i)
        

gaiaBot.run(open("token.txt").read())
