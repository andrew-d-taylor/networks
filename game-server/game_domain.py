__author__ = 'andrew'

from utilities import Singleton
import random
from math import floor
from services import PlayerService
import settings

class Player():

    def __init__(self, playerid, position, cookies):
        self.position = position
        self.cookies = cookies
        self.playerId = playerid

    def dropCookie(self):
        return self.cookies.pop()

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
        self.playerGrid.placeCookie(cookie, currentPosition)
        self.inFlightCookies[cookie.cookieId] = cookie

    def moveInFlightCookies(self):

        cookiesToRemove = []
        hitOccurences = []

        for key in self.inFlightCookies:
            cookie = self.inFlightCookies[key]

            #move to next space
            nextPosition = self.playerGrid.getNextPosition(cookie.position, cookie.direction)
            nextMapSpace = self.playerGrid.getMapSpace(nextPosition)

            #if the cookie hit a wall
            if nextMapSpace is None or not nextMapSpace.isTraversible():
                cookie, player = self.__hitWall(cookie)
                cookiesToRemove.append(cookie)
                hitOccurences.append((cookie, nextPosition, "-1"))
            #If the cookie has hit someone
            elif len(nextMapSpace.players) > 0:
                cookie, player = self.__hitPlayer(cookie, nextMapSpace)
                cookiesToRemove.append(cookie)
                hitOccurences.append((cookie, nextPosition, player))
            else:
            #cookie keeps travelling
                self.travel(cookie, cookie.direction)

        for cookie in cookiesToRemove:
            self.inFlightCookies.pop(cookie.cookieId)

        return hitOccurences

    def __hitWall(self, cookie):
        service = PlayerService()
        player = service.get(cookie.playerId)
        previousSpace = self.playerGrid.getMapSpace(cookie.position)
        previousSpace.cookies.remove(cookie)
        player.getHitByCookie(cookie)
        service.save(player)
        return (cookie, player)

    def __hitPlayer(self, cookie, nextMapSpace):
        service = PlayerService()
        previousPlayer = service.get(cookie.playerId)
        previousSpace = self.playerGrid.getMapSpace(cookie.position)
        previousSpace.cookies.remove(cookie)
        hitPlayer = nextMapSpace.players[0]
        hitPlayer.getHitByCookie(cookie)
        service.save(hitPlayer)
        if len(previousPlayer.cookies) == 0:
            raise WinnerFound(previousPlayer.playerId)
        return (cookie, hitPlayer)

    def travel(self, positioned_object, direction):
        if not self.objectCanTravel(positioned_object.position, direction):
            raise UnmovableDirection
        else:
            nextPosition = self.playerGrid.getNextPosition(positioned_object.position, direction)
            if type(positioned_object) is Cookie:
                self.playerGrid.changeCookiePosition(positioned_object, nextPosition)
            else:
                self.playerGrid.changePlayerPosition(positioned_object, nextPosition)

class PlayerGrid():

    def __init__(self, columns, rows):
        self.columns = columns
        self.rows = rows
        self.grid = [[MapSpace() for y in range(rows)] for x in range(columns)]

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
        rowEntries = []
        for index in range(self.rows):
            rowEntry = []
            for mapSpace in self.grid[:][index]:
                rowEntry.append(mapSpace)
            rowEntries.append(rowEntry.copy())
        return rowEntries

    #Creates a col x row grid with wrap-around holes in the middle of the x and y axis,
    #But otherwise bordered by unnavigable tiles
    def generateDefaultLayout(self):
        for y in range(self.rows):
            for x in range(self.columns):
                if settings.walls == 1 and y == 0 or y == self.rows - 1 or x == 0 or x == self.columns - 1:
                    if settings.wallGaps == 1 and x == floor(self.columns / 2) or y == floor(self.rows / 2):
                        space = self.grid[y][x]
                        space.tile = settings.tile_navigable
                    else:
                        space = self.grid[y][x]
                        space.tile = settings.tile_unnavigable
                else:
                    space = self.grid[y][x]
                    space.tile = settings.tile_navigable
            print(self.grid[:][y])

    def changeCookiePosition(self, cookie, position):
        previous_space = self.getMapSpace(cookie.position)
        previous_space.removeCookie(cookie)

        mapSpace = self.getMapSpace(position)
        mapSpace.addCookie(cookie)
        cookie.position = position

    def placeCookie(self, cookie, position):
        cookie.position = position
        space = self.getMapSpace(position)
        space.addCookie(cookie)

    def changePlayerPosition(self, player, position):
        previous_space = self.getMapSpace(player.position)
        previous_space.removePlayer(player)

        mapSpace = self.getMapSpace(position)
        mapSpace.addPlayer(player)
        player.position = position

    def getMapSpace(self, position):
        try:
            mapSpace = self.grid[position.y][position.x]
            return mapSpace
        except IndexError:
            return None

    def isTraversible(self, position):
        mapSpace = self.getMapSpace(position)
        if mapSpace is None:
            return False
        return mapSpace.isTraversible()

    def __getNextUpPosition(self, position):
        if (position.y + 1) == self.rows:
            return Position(position.x, 0)
        else:
            return Position(position.x, position.y + 1)

    def __getNextDownPosition(self, position):
        if (position.y - 1) < 0:
            return Position(position.x, self.rows - 1)
        else:
            return Position(position.x, position.y - 1)

    def __getNextRightPosition(self, position):
        if (position.x + 1) == self.columns:
            return Position(0, position.y)
        else:
            return Position(position.x + 1, position.y)

    def __getNextLeftPosition(self, position):
        if (position.x - 1) < 0:
            return Position(self.columns - 1, position.y)
        else:
            return Position(position.x - 1, position.y)

class MapSpace():

    def __init__(self):
        self.players = []
        self.cookies = []
        self.tile = settings.tile_navigable

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return ''+str(self.tile)

    def addPlayer(self, player):
        self.players.append(player)

    def removePlayer(self, player):
        self.players.remove(player)

    def addCookie(self, cookie):
        self.cookies.append(cookie)

    def removeCookie(self, cookie):
        self.cookies.remove(cookie)

    def isTraversible(self):
        return self.tile is settings.tile_navigable

class UnmovableDirection(Exception):
    pass


class WinnerFound(Exception):
    def __init__(self, playerId):
        self.playerId = playerId



