__author__ = 'andrew'

from game_domain import *
import random

class PlayerService(metaclass=Singleton):

    def __init__(self):
        random.seed()
        self.playerRegistry = PlayerRegistry()

    def getLoggedInPlayers(self):
        return None

    def register(self, playerId):
        player = self.playerRegistry.load(playerId)
        if player is None:
            player = self.__randomizeNewState(playerId)
        player.loggedIn = True
        return player

    #TODO verify that random state is a traversible tile
    def __randomizeNewState(self, playerid):
        player = Player(playerid=playerid)
        player.cookies = starting_cookie_count
        player.position = Position()
        player.position.x = random.randint(0, default_col_count)
        player.position.y = random.randint(0, default_row_count)
        return player

class PlayerRegistry():

    def __init__(self):
        self.players = self.__loadState()

    def __loadState(self):
        return None

    def load(self, playerId):
        try:
            return self.players[playerId]
        except KeyError:
            return None

    def save(self, player):
        self.players[player.playerId] = player

class GameService():

    def __init__(self):
        self.gameMap = self.__randomizeNewState()

    def __randomizeNewState(self):
        return None

    def getCookies(self):
        return None

    def getMap(self):
        return None