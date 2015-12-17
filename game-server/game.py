__author__ = 'andrew'

from protocol import *
from game_domain import *
from communication import *
import services
import sys
from utilities import ThreadSafeSingleton
from game_domain import WinnerFound

class Game(ThreadSafeSingleton):
    pass

    #Only called once
    def __init__(self):
        self.playerService = services.PlayerService()
        self.gameService = services.GameService()
        self.playerReceivers = {}
        self.playerSenders = {}
        self.requestQueue = None
        self.cleanState = True

    #Called only by the RequestReader thread
    def considerPlayerRequest(self, request):
        if request.command.isLogin():
            self.__considerPlayerLogin(request)
        elif request.command.isMessage():
            self.__considerPlayerMessage(request)
        elif request.command.isMove():
            self.__considerPlayerMove(request)
        elif request.command.isThrow():
            self.__considerPlayerThrow(request)
        elif request.command.isLogout():
            self.__considerPlayerLogout(request)

    def __considerPlayerLogout(self, request):
        self.playerSenders.pop(request.playerId)
        self.playerReceivers.pop(request.playerId)
        self.playerService.remove(request.playerId)
        self.__broadcastMessage(logOut(request.playerId))

    def __considerPlayerMove(self, request):
        try:
            player = self.playerService.get(request.originId)
            self.gameService.movePlayer(player, request.direction)
            self.cleanState = False
        except UnmovableDirection:
            raise PlayerGameError(badCommand("Can't move in that direction"))

    def __considerPlayerThrow(self, request):
        try:
            player = self.playerService.get(request.originId)
            self.gameService.tossCookie(player, request.direction)
            self.cleanState = False
        except IndexError:
            raise PlayerGameError(badCommand("You don't have any more cookies to throw"))

    def __considerPlayerLogin(self, request):
        if self.playerService.get(request.playerId) is None:
            self.addPlayerToGame(request.playerId, request.origin)
        else:
            raise PlayerGameError(badCommand("Player already logged in"))

    def __considerPlayerMessage(self, request):
        try:
            if request.playerId is 'all':
                self.__messageAllPlayers(request)
            else:
                other = self.playerSenders[request.playerId]
                other.respondToPlayer(playerMessage(request.playerId, request.message+'\n'))
        except KeyError:
            raise PlayerGameError(badCommand("Recipient is not logged in"))

    def __messageAllPlayers(self, request):
        for key in self.playerSenders:
            sender = self.playerSenders[key]
            sender.respondToPlayer(playerMessage('all', request.message+'\n'))

    def __broadcastMessage(self, message):
        for key in self.playerSenders:
            sender = self.playerSenders[key]
            sender.respondToPlayer(message+"\n")

    #Called only by the ServerUpdater thread
    def getGameState(self):
        if self.cleanState:
            return None, None
        players = self.playerService.getPlayers()
        cookies = self.gameService.getCookies()
        tuples = self.playerSenders.items()
        senders = [v for (k,v) in tuples]
        self.cleanState = True
        return senders, GameState(None, cookies, players)

    def getInitialGameState(self):
        players = self.playerService.getPlayers()
        cookies = self.gameService.getCookies()
        mapGrid = self.gameService.getMapGrid()
        return GameState(mapGrid, cookies, players)

    def addPlayerToGame(self, playerId, clientSocket):
        player = self.playerService.register(playerId)
        self.gameService.assignStartingState(player)
        playerSender, playerReceiver = self.__establishCommunication(playerId, clientSocket)
        self.__sendLoginResponse(playerSender)
        self.__sendInitialState(playerSender)
        playerReceiver.listen()

    def __establishCommunication(self, playerId, clientSocket):
        playerReceiver = PlayerReceiver(playerId, clientSocket, self.requestQueue)
        playerSender = PlayerSender(playerId, clientSocket)
        self.playerReceivers[playerId] = playerReceiver
        self.playerSenders[playerId] = playerSender
        return playerSender, playerReceiver

    def __sendLoginResponse(self, playerSender):
        mapX = self.gameService.getMapGrid().columns
        mapY = self.gameService.getMapGrid().rows
        playerSender.respondToPlayer(loginSuccess(mapX, mapY))

    def __sendInitialState(self, playerSender):
        initialState = self.getInitialGameState()
        playerSender.sendMessages(initialState.toMessages())

    def hasCookiesInFlight(self):
        return self.gameService.hasCookiesInFlight()

    def moveCookies(self):
        if self.gameService.hasCookiesInFlight():
            try:
                hitOccurences = self.gameService.moveCookies()
                if len(hitOccurences) > 0:
                    self.__handleCookieHits(hitOccurences)
                else:
                    self.cleanState = False
            except WinnerFound as winner:
                self.gameWon(winner.playerId)

    def gameWon(self, playerId):
        for key in self.playerSenders:
            sender = self.playerSenders[key]
            sender.respondToPlayer(playerWon(playerId))
            sender.playerSocket.close()
        sys.exit()

    def __handleCookieHits(self, hitOccurences):
        for cookie, position, player in hitOccurences:
            if player == "-1":
                self.__broadcastMessage(hitWall(cookie, position))
            else:
                self.__broadcastMessage(hitPlayer(cookie, position, player))

class GameState():

    def __init__(self, mapGrid, cookies, players):
        self.mapGrid = mapGrid
        self.cookies = cookies
        self.players = players

    def toMessages(self):
        messages = []
        mapMessages = self.__convertMap()
        cookieMessages = self.__convertCookies()
        playerMessages = self.__convertPlayers()
        messages.extend(mapMessages)
        if len(mapMessages) > 0:
            messages.extend(["999 Initial State Update Done\n"])
        messages.extend(cookieMessages)
        messages.extend(playerMessages)
        return messages

    def __convertMap(self):
        mapMessages = []
        if self.mapGrid is not None:
            rows = self.mapGrid.getAllRows()
            rowIndex = 0
            for row in rows:
                tiles = []
                for mapSpace in row:
                    tiles.append(mapSpace.tile)
                print(tiles)
                mapMessages.append(mapSubsection(0, rowIndex, self.mapGrid.columns - 1, rowIndex, tiles))
                rowIndex += 1
        return mapMessages

    def __convertCookies(self):
        cookieMessages = []
        if self.cookies is not None:
            for cookie in self.cookies:
                cookieMessages.append(cookieInFlight(cookie.cookieId, cookie.position.x, cookie.position.y, cookie.direction))
        return cookieMessages

    def __convertPlayers(self):
        playerMessages = []
        if self.players is not None:
            for player in self.players:
                playerMessages.append(playerCookieUpdate(player.playerId, player.position.x, player.position.y, len(player.cookies)))
        return playerMessages

class PlayerGameError(Exception):
    def __init__(self, msg):
        self.msg = msg
