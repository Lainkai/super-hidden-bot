import discord

class Game():
    min_players = 1
    def __init__(self,name:str="Game",desc:str="Template",min_players:int=1, max_players:int=None):
        self.name = name
        self.desc = desc
        self.min_players = min_players
        if max_players!=None:
            max_players = 127
        print("Game Instance Created")

    def start_game(self,channel:discord.TextChannel):
        print("Game: {0} Started".format(self.name))
    
    def end_game(self):
        print("Game: {0} Ended".format(self.name))