__author__ = 'andrew'

from game import Singleton
import random

default_col_count = 10
default_row_count = 10
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
        for cookie in self.cookies:
            cookie.position = newPosition

    def removeCookie(self, cookie):
        self.cookies.remove(cookie)

    def getHitByCookie(self, cookie):
        cookie.playerId = self.playerId
        cookie.position = self.position
        self.cookies.append(cookie)

    def logOut(self):
        self.loggedIn = False

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

class GameMap(metaclass=Singleton):

    def __init__(self, playerGrid):
        self.playerGrid = playerGrid
        self.inFlightCookies = {}

    def objectCanTravel(self, position, direction):
        nextPosition = self.playerGrid.getNextPosition(position, direction)
        return self.playerGrid.isTraversible(nextPosition)

    def getRandomStartingSpace(self):
        notFound = True
        random.seed()
        while notFound:
            x, y = random.randint(0, self.playerGrid.columns - 1), random.randint(0, self.playerGrid.rows - 1)
            space = self.playerGrid.getMapSpace(Position(x, y))
            if space.isTraversible():
                notFound = False
        return space

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
            if type(positioned_object) is Cookie:
                self.playerGrid.changeCookiePosition(positioned_object, nextPosition)
            else:
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
        except KeyError:
            raise UnmovableDirection

    def isTraversible(self, position):
        mapSpace = self.getMapSpace(position)
        return mapSpace.isTraversible()

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




