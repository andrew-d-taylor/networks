__author__ = 'andrew'

from game import Singleton

default_col_count = 128
default_row_count = 128
starting_cookie_count = 3

tile_navigable = 0
tile_unnavigable = -1

class Player():

    def __init__(self, playerid, position, cookies):
        self.position = position
        self.cookies = cookies
        self.playerId = playerid
        self.loggedIn = True

    def movePosition(self, newPosition):
        self.position = newPosition

    def throwCookie(self):
        self.cookies -= 1

    def getHitByCookie(self):
        self.cookies += 1

    def logOut(self):
        self.loggedIn = False

class Position():

    def __init__(self, x, y):
        self.x = x
        self.y = y

class GameMap(metaclass=Singleton):

    def __init__(self, playerGrid):
        self.playerGrid = playerGrid
        if playerGrid is None:
            self.playerGrid = PlayerGrid()

    def playerCanTravel(self, player, direction):
        nextPosition = self.playerGrid.getNextPosition(player.position, direction)
        return self.playerGrid.isTraversible(nextPosition)


class PlayerGrid():

    def __init__(self, previousState):
        if (previousState is not None):
            self.__fromPreviousState(previousState)
        else:
            self.grid = [[None for x in range(default_row_count)] for x in range(default_col_count)]

    def getNextPosition(self, currentPosition, direction):
        if direction.isUp():
            return self.__getNextUpPosition(currentPosition)
        elif direction.isDown():
            return self.__getNextDownPosition(currentPosition)
        elif direction.isLeft():
            return self.__getNextLeftPosition(currentPosition)
        else:
            return self.__getNextRightPosition(currentPosition)

    def getMapSpace(self, position):
        mapSpace = self.grid[position.x][position.y]
        if mapSpace is None:
            mapSpace = MapSpace()
        return mapSpace

    def isTraversible(self, position):
        mapSpace = self.getMapSpace(position)
        return mapSpace.isTraversible()


    def __fromPreviousState(self, previousState):
        return None

    def __getNextUpPosition(self, position):
        if (position.y + 1) > default_row_count:
            position.y = 0
            return position
        else:
            position.y += 1
            return position

    def __getNextDownPosition(self, position):
        if (position.y - 1) < 0:
            position.y = default_row_count
            return position
        else:
            position.y += 1
            return position

    def __getNextRightPosition(self, position):
        if (position.x + 1) > default_col_count:
            position.x = 0
            return position
        else:
            position.x += 1
            return position

    def __getNextLeftPosition(self, position):
        if (position.x - 1) < 0:
            position.x = default_col_count
            return position
        else:
            position.x += 1
            return position

class MapSpace():

    def __init__(self):
        self.players = []
        self.tile = tile_navigable

    def addPlayer(self, player):
        self.players.append(player)

    def removePlayer(self, player):
        self.players.remove(player)

    def isTraversible(self):
        return self.tile is tile_navigable




