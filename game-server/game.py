__author__ = 'andrew'

from protocol import *
from game_domain import *
from communication import *
import services
from utilities import ThreadSafeSingleton

COOKIE_SPEED = 3

def playGame(playerId, clientSocket):
    print('Player '+playerId+' is about to play the game')
    Game.instance().addPlayerToGame(playerId, clientSocket)

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

    def __considerPlayerMove(self, request):
        try:
            player = self.playerService.get(request.originId)
            print('Player '+player.playerId+' requested a move '+str(request.direction))
            self.gameService.movePlayer(player, request.direction)
            self.cleanState = False
        except UnmovableDirection:
            raise PlayerGameError(badCommand("Can't move in that direction"))

    def __considerPlayerThrow(self, request):
        try:
            player = self.playerService.get(request.originId)
            cookie = player.cookies[0]
            self.gameService.tossCookie(player, cookie, request.direction)
            self.cleanState = False
        except IndexError:
            raise PlayerGameError(badCommand("You don't have any more cookies to throw"))

    def __considerPlayerLogin(self, request):
        if self.playerService.get(request.playerId) is None:
            playGame(request.playerId, request.origin)
            self.cleanState = False
        else:
            raise PlayerGameError(badCommand("Player already logged in"))

    def __considerPlayerMessage(self, request):
        try:
            other = self.playerSenders[request.playerId]
            other.respondToPlayer(request.message)
        except KeyError:
            raise PlayerGameError(badCommand("Recipient is not logged in"))

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
        self.gameService.assignStartingPosition(player)
        self.playerService.assignStartingCookies(player)
        playerReceiver = PlayerReceiver(playerId, clientSocket, self.requestQueue)
        playerSender = PlayerSender(player.playerId, clientSocket)
        self.playerReceivers[player.playerId] = playerReceiver
        self.playerSenders[player.playerId] = playerSender
        mapX = self.gameService.getMapGrid().columns
        mapY = self.gameService.getMapGrid().rows
        playerSender.respondToPlayer(loginSuccess(mapX, mapY))
        initialState = self.getInitialGameState()
        playerSender.sendMessages(initialState.toMessages())
        print('Player '+playerId+' was added to the game')
        playerReceiver.listen()

    def hasCookiesInFlight(self):
        return self.gameService.hasCookiesInFlight()

    def moveCookies(self):
        if self.gameService.hasCookiesInFlight():
            self.gameService.moveCookies()
            self.cleanState = False

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
                mapMessages.append(mapSubsection(0, rowIndex, self.mapGrid.columns, rowIndex, tiles))
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