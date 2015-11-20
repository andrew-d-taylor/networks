__author__ = 'andrew'

from game_domain import *
import random
from utilities import Singleton
import game_domain
import settings

class PlayerService(metaclass=Singleton):

    def __init__(self, config=None):
        if config is not None:
            self.config = config
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

    def remove(self, playerId):
        self.playerRegistry.remove(playerId)

    def register(self, playerId):
        player = self.playerRegistry.load(playerId)
        if player is None:
            player = self.__randomizeNewState(playerId)
            self.save(player)
        return player

    def __randomizeNewState(self, playerId):
        player = game_domain.Player(playerid=playerId, cookies=None, position=None)
        return player

    def assignStartingCookies(self, player):
        cookies = []
        for i in range(settings.starting_cookie_count):
            cookie = game_domain.Cookie(str(self.cookieIdCount), player.playerId, player.position, direction=None)
            cookies.append(cookie)
            self.cookieIdCount += 1
        player.cookies = cookies

class PlayerRegistry():

    def __init__(self):
        self.players = {}

    def load(self, playerId):
        try:
            return self.players[playerId]
        except KeyError:
            return None

    def remove(self, playerId):
        self.players.pop(playerId)

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
        newGrid = game_domain.PlayerGrid(settings.default_col_count, settings.default_row_count)
        newGrid.generateDefaultLayout()
        return game_domain.GameMap(newGrid)

    def assignStartingState(self, player):
        self.__assignStartingPosition(player)
        self.playerService.assignStartingCookies(player)

    def __assignStartingPosition(self, player):
        return self.gameMap.assignRandomStartingPosition(player)

    def getCookies(self):
        tuples = self.gameMap.inFlightCookies.items()
        return [cookie for (k, cookie) in tuples]

    def hasCookiesInFlight(self):
        return len(self.gameMap.inFlightCookies) > 0

    def getMapGrid(self):
        return self.gameMap.playerGrid

    def moveCookies(self):
        self.gameMap.moveInFlightCookies()

    def tossCookie(self, player, direction):
        cookie = player.dropCookie()
        self.gameMap.putCookieInFlight(cookie, player.position, direction)