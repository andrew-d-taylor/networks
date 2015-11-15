__author__ = 'andrew'

from game_domain import *
import random

class PlayerService():

    def __init__(self):
        random.seed()
        self.playerRegistry = PlayerRegistry()

    def register(self, playerId):
        player = self.playerRegistry.load(playerId)
        if player is None:
            player = self.__randomizeNewState(playerId)
        return player

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
        players = {}

    def load(self, playerId):
        try:
            return self.players[playerId]
        except KeyError:
            return None

    def save(self, player):
        self.players[player.playerId] = player
