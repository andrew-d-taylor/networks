__author__ = 'andrew'

from game_domain import *
from game import Singleton
import random

class PlayerService(metaclass=Singleton):

    def __init__(self):
        random.seed()
        self.playerRegistry = PlayerRegistry()

    def getPlayers(self):
        return self.playerRegistry.players.items()

    def get(self, playerId):
        return self.playerRegistry.load(playerId)

    def save(self, player):
        self.playerRegistry.save(player)

    def register(self, playerId):
        player = self.playerRegistry.load(playerId)
        if player is None:
            player = self.__randomizeNewState(playerId)
        player.loggedIn = True
        return player

    def logOut(self, player):
        player.logOut()
        self.playerRegistry.remove(player)

    #TODO verify that random state is a traversible tile
    def __randomizeNewState(self, playerid):
        player = Player(playerid=playerid, cookies=starting_cookie_count, position=None)
        return player

class PlayerRegistry():

    def __init__(self):
        self.players = self.__loadState()

    #Could read from a persistence file here
    def __loadState(self):
        return {}

    def load(self, playerId):
        try:
            return self.players[playerId]
        except KeyError:
            return None

    def remove(self, player):
        self.players.pop(player.playerId)

    def save(self, player):
        self.players[player.playerId] = player

class GameService(metaclass=Singleton):

    def __init__(self):
        self.gameMap = self.__randomizeNewState()
        self.playerService = PlayerService()

    def movePlayer(self, player, direction):
        self.gameMap.travel(player, direction)
        self.playerService.save(player)

    def __randomizeNewState(self):
        newGrid = PlayerGrid(default_col_count, default_row_count)
        newGrid.generateDefaultLayout()
        return GameMap(newGrid)

    def getRandomNavigableTile(self):
        return self.gameMap.getRandomStartingSpace()

    def getCookies(self):
        return self.gameMap.inFlightCookies.items()

    def hasCookiesInFlight(self):
        return len(self.gameMap.inFlightCookies) > 0

    def getMapGrid(self):
        return self.gameMap.playerGrid

    def moveCookies(self):
        self.gameMap.moveInFlightCookies()

    def tossCookie(self, player, cookie, direction):
        cookie.direction = direction
        self.gameMap.putCookieInFlight(cookie, player.position, direction)