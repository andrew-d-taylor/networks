__author__ = 'andrew'

from utilities import Singleton
import random
from services import PlayerService
from settings import *

class Player():

    def __init__(self, playerid, position, cookies):
        self.position = position
        self.cookies = cookies
        self.playerId = playerid

    def movePosition(self, newPosition):
        self.position = newPosition
        for cookie in self.cookies:
            cookie.position = newPosition

    def removeCookie(self, cookie):
        self.cookies.remove(cookie)

    def getHitByCookie(self, cookie):
        cookie.playerId = self.playerId
        cookie.position = self.position
        self.cookies.append(cookie)

class Cookie():

    def __init__(self, cookieId, playerId, position, direction):
        self.cookieId = cookieId
        self.playerId = playerId
        self.position = position
        self.direction = direction

class Position():

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return ''+str(self.x)+', '+str(self.y)

class GameMap(metaclass=Singleton):

    def __init__(self, playerGrid):
        self.playerGrid = playerGrid
        self.inFlightCookies = {}

    def objectCanTravel(self, position, direction):
        nextPosition = self.playerGrid.getNextPosition(position, direction)
        return self.playerGrid.isTraversible(nextPosition)

    def assignRandomStartingPosition(self, player):
        notFound = True
        random.seed()
        x, y = 0,0
        space = None
        while notFound:
            x, y = random.randint(0, self.playerGrid.columns - 1), random.randint(0, self.playerGrid.rows - 1)
            space = self.playerGrid.getMapSpace(Position(x, y))
            if space.isTraversible():
                notFound = False
        player.position = Position(x, y)
        space.addPlayer(player)

    def putCookieInFlight(self, cookie, currentPosition, direction):
        cookie.position = currentPosition
        cookie.direction = direction
        self.playerGrid.changeCookiePosition(cookie, currentPosition)
        self.inFlightCookies[cookie.cookieId] = cookie

    def moveInFlightCookies(self):
        for cookie in self.inFlightCookies:
            #move to next space
            nextPosition = self.playerGrid.getNextPosition(cookie.position, cookie.direction)
            nextMapSpace = self.playerGrid.getMapSpace(nextPosition)
            #If the cookie has hit someone
            if len(nextMapSpace.players) == 0:
                self.inFlightCookies.pop(cookie.cookieId)
                service = PlayerService()
                hitPlayer = nextMapSpace.players[0]
                hitPlayer.getHitByCookie(cookie)
                previousSpace = self.playerGrid.getMapSpace(cookie.position)
                previousSpace.cookies.remove(cookie)
                service.save(hitPlayer)
            #if the cookie hit a wall
            elif not nextMapSpace.isTraversible():
                self.inFlightCookies.pop(cookie.cookieId)
                service = PlayerService()
                player = service.get(cookie.playerId)
                previousSpace = self.playerGrid.getMapSpace(cookie.position)
                previousSpace.cookies.remove(cookie)
                player.getHitByCookie(cookie)
                service.save(player)
            else:
                #cookie keeps travelling
                self.travel(cookie, nextPosition)

    def travel(self, positioned_object, direction):
        if not self.objectCanTravel(positioned_object.position, direction):
            raise UnmovableDirection
        else:
            nextPosition = self.playerGrid.getNextPosition(positioned_object.position, direction)
            print('Next position is: '+str(nextPosition))
            if type(positioned_object) is Cookie:
                self.playerGrid.changeCookiePosition(positioned_object, nextPosition)
            else:
                print('Player moving from '+str(positioned_object.position)+' to '+str(nextPosition))
                self.playerGrid.changePlayerPosition(positioned_object, nextPosition)

class PlayerGrid():

    def __init__(self, columns, rows):
        self.columns = columns
        self.rows = rows
        self.grid = [[MapSpace() for x in range(columns)] for y in range(rows)]

    def getNextPosition(self, currentPosition, direction):
        if direction.isUp():
            return self.__getNextUpPosition(currentPosition)
        elif direction.isDown():
            return self.__getNextDownPosition(currentPosition)
        elif direction.isLeft():
            return self.__getNextLeftPosition(currentPosition)
        else:
            return self.__getNextRightPosition(currentPosition)

    def getAllRows(self):
        rows = []
        for index in rows:
            rows.append(self.grid[index])
        return rows

    def generateDefaultLayout(self):
        for x in range(self.rows):
            for y in range(self.columns):
                if y == 0 or y == self.columns or x == 0 or x == self.rows:
                    space = self.grid[x][y]
                    space.tile = tile_unnavigable

    def changeCookiePosition(self, cookie, position):
        previous_space = self.getMapSpace(cookie.position)
        previous_space.removeCookie(cookie)

        mapSpace = self.getMapSpace(position)
        mapSpace.addCookie(cookie)
        cookie.position = position

    def changePlayerPosition(self, player, position):
        previous_space = self.getMapSpace(player.position)
        previous_space.removePlayer(player)

        mapSpace = self.getMapSpace(position)
        mapSpace.addPlayer(player)
        player.position = position

    def getMapSpace(self, position):
        try:
            mapSpace = self.grid[position.x][position.y]
            return mapSpace
        except IndexError:
            raise UnmovableDirection

    def isTraversible(self, position):
        try:
            mapSpace = self.getMapSpace(position)
        except IndexError:
            return False
        return mapSpace.isTraversible()

    def __getNextUpPosition(self, position):
        if (position.y + 1) > default_row_count:
            return Position(position.x, 0)
        else:
            return Position(position.x, position.y + 1)

    def __getNextDownPosition(self, position):
        if (position.y - 1) < 0:
            return Position(position.x, default_row_count)
        else:
            return Position(position.x, position.y - 1)

    def __getNextRightPosition(self, position):
        if (position.x + 1) > default_col_count:
            return Position(0, position.y)
        else:
            return Position(position.x + 1, position.y)

    def __getNextLeftPosition(self, position):
        if (position.x - 1) < 0:
            return Position(default_col_count, position.y)
        else:
            return Position(position.x - 1, position.y)

class MapSpace():

    def __init__(self):
        self.players = []
        self.cookies = []
        self.tile = tile_navigable

    def addPlayer(self, player):
        self.players.append(player)

    def removePlayer(self, player):
        self.players.remove(player)

    def addCookie(self, cookie):
        self.cookies.append(cookie)

    def removeCookie(self, cookie):
        self.cookies.remove(cookie)

    def isTraversible(self):
        return self.tile is tile_navigable

class UnmovableDirection(Exception):
    pass




