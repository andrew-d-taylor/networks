__author__ = 'andrew'

from game_domain import *
import random
from utilities import Singleton
import game_domain
from settings import *

class PlayerService(metaclass=Singleton):

    def __init__(self):
        random.seed()
        self.playerRegistry = PlayerRegistry()
        self.cookieIdCount = 1

    def getPlayers(self):
        tuples = self.playerRegistry.players.items()
        return [v for (k, v) in tuples]

    def get(self, playerId):
        return self.playerRegistry.load(playerId)

    def save(self, player):
        self.playerRegistry.save(player)

    def register(self, playerId):
        player = self.playerRegistry.load(playerId)
        if player is None:
            player = self.__randomizeNewState(playerId)
            self.save(player)
        return player

    def __randomizeNewState(self, playerid):
        player = game_domain.Player(playerid=playerid, cookies=None, position=None)
        return player

    def assignStartingCookies(self, player):
        cookies = []
        for i in range(starting_cookie_count):
            cookie = game_domain.Cookie(str(self.cookieIdCount), player.playerId, player.position, direction=None)
            cookies.append(cookie)
            self.cookieIdCount += 1
        player.cookies = cookies

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
        newGrid = game_domain.PlayerGrid(default_col_count, default_row_count)
        newGrid.generateDefaultLayout()
        return game_domain.GameMap(newGrid)

    def assignStartingPosition(self, player):
        return self.gameMap.assignRandomStartingPosition(player)

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