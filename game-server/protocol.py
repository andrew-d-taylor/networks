__author__ = 'andrew'

from settings import encoding

def loginSuccess(mapx, mapy):
    return "200 " + str(mapx) + ", " + str(mapy) + "\n"


def playerMessage(playerId, messageText):
    return "100 " + playerId + " " + messageText + "\n"


def playerWon(playerId):
    return "101 " + playerId + ", won the game!\n"


def mapSubsection(x1, y1, x2, y2, tiles):
    msg = ["102 " + str(x1) + ", " + str(y1) + ", " + str(x2) + ", " + str(y2)]
    for tile in tiles:
        msg.append(", "+str(tile))
    msg.append(" \n")
    return "".join(msg)

def cookieInFlight(cookieId, cookieX, cookieY, direction):
    return "103 " + cookieId + ", " + str(cookieX) + ", " + str(cookieY) + ", " + str(direction) + "\n"


def playerCookieUpdate(playerId, playerX, playerY, cookieCount):
    return "104 " + playerId + ", " + str(playerX) + ", " + str(playerY) + ", " + str(cookieCount) + "\n"


def badCommand(message):
    return "400 " + message + "\n"

def logOut(playerId):
    return "104 "+playerId+", -1, -1, -1"

def hitWall(cookie, position):
    return "105 "+cookie.cookieId+", "+str(position.x)+", "+str(position.y)+", -1\n"

def hitPlayer(cookie, position, player):
    return "105 "+cookie.cookieId+", "+str(position.x)+", "+str(position.y)+", "+player.playerId+"\n"

def serverError(message):
    return "500 " + message + "\n"


class ClientRequest():
    def __init__(self, requestString, originSocket, originId):
        requestSplit = requestString.split()
        if not requestSplit:
            return
        try:
            self.command = Command(requestSplit[0])
            self.origin = originSocket
            self.originId = originId
            if self.command.isLogin():
                self.playerId = requestSplit[1]
            elif self.command.isLogout():
                self.playerId = originId
            elif self.command.isMessage():
                self.playerId = requestSplit[1]
                self.message = requestSplit[2]
            else:
                self.direction = Direction(requestSplit[1])
        except IndexError:
            raise RequestParsingException


    def writeErrorResponse(self, msg):
        raw = bytes(msg, encoding)
        self.origin.sendall(raw)


class Command():
    def __init__(self, requestSubstring):
        self.__command = self.__parseCommand(requestSubstring)

    def __parseCommand(self, requestSubstring):
        requestSubstring = requestSubstring.lower()
        if requestSubstring == "login" or requestSubstring == "l":
            return "login"
        elif requestSubstring == "Q" or requestSubstring == "q":
            return "q"
        elif requestSubstring == "move" or requestSubstring == "m":
            return "move"
        elif requestSubstring == "throw" or requestSubstring == "t":
            return "throw"
        elif requestSubstring == "msg":
            return "msg"
        else:
            raise RequestParsingException

    def isLogin(self):
        return self.__command == "login"

    def isLogout(self):
        return self.__command == "q"

    def isMove(self):
        return self.__command == "move"

    def isThrow(self):
        return self.__command == "throw"

    def isMessage(self):
        return self.__command == "msg"


class Direction():

    def __init__(self, requestSubstring):
        self.__direction = self.__parseDirection(requestSubstring)

    def __str__(self):
        return self.__direction

    def __parseDirection(self, requestSubstring):
        requestSubstring = requestSubstring.lower()
        if requestSubstring == "up" or requestSubstring == "u":
            return "up"
        elif requestSubstring == "down" or requestSubstring == "d":
            return "down"
        elif requestSubstring == "left" or requestSubstring == "l":
            return "left"
        elif requestSubstring == "right" or requestSubstring == "r":
            return "right"
        else:
            raise RequestParsingException

    def isUp(self):
        return self.__direction == "up"

    def isDown(self):
        return self.__direction == "down"

    def isLeft(self):
        return self.__direction == "left"

    def isRight(self):
        return self.__direction == "right"


class RequestParsingException(Exception):
    pass
