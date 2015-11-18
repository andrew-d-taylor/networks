__author__ = 'andrew'

import socket
from multiprocessing.dummy import Queue as ThreadQue
from queue import Queue
from protocol import *
from game_domain import *
import threading
import services
import time

COOKIE_SPEED = 3

def playGame(playerId, clientSocket):
    GameServer.instance().addPlayerToGame(playerId, clientSocket)

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class ThreadSafeSingleton(object):
    __singleton_lock = threading.Lock()
    __singleton_instance = None

    @classmethod
    def instance(cls):
        if not cls.__singleton_instance:
            with cls.__singleton_lock:
                if not cls.__singleton_instance:
                    cls.__singleton_instance = cls()
        return cls.__singleton_instance


class GameServer(ThreadSafeSingleton):
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
            self.gameService.movePlayer(player, request.direction)
            self.cleanState = False
        except UnmovableDirection:
            raise ClientRequestError(badCommand("Can't move in that direction"))

    def __considerPlayerThrow(self, request):
        try:
            player = self.playerService.get(request.originId)
            cookie = player.cookies[0]
            self.gameService.tossCookie(player, cookie, request.direction)
            self.cleanState = False
        except IndexError:
            raise ClientRequestError(badCommand("You don't have any more cookies to throw"))

    def __considerPlayerLogin(self, request):
        if self.playerService.get(request.playerId) is None:
            playGame(request.playerId, request.origin)
            self.cleanState = False
        else:
            raise ClientRequestError(badCommand("Player already logged in"))

    def __considerPlayerMessage(self, request):
        try:
            other = self.playerSenders[request.playerId]
            other.respondToPlayer(request.message)
        except KeyError:
            raise ClientRequestError(badCommand("Recipient is not logged in"))

    #Called only by the ServerUpdater thread
    def getGameState(self):
        if self.cleanState:
            return None, None
        players = self.playerService.getPlayers()
        cookies = self.gameService.getCookies()
        self.cleanState = True
        return self.playerSenders, GameState(None, cookies, players)

    def getInitialGameState(self):
        players = self.playerService.getPlayers()
        cookies = self.gameService.getCookies()
        mapGrid = self.gameService.getMapGrid()
        return GameState(mapGrid, cookies, players)

    def addPlayerToGame(self, playerId, clientSocket):
        player = self.playerService.register(playerId)
        player.position = self.gameService.getRandomNavigableTile()
        playerReceiver = PlayerReceiver(player, clientSocket, self.requestQueue)
        playerReceiver.listen()
        playerSender = PlayerSender(player.playerId, clientSocket)
        self.playerReceivers[player.playerId] = playerReceiver
        self.playerSenders[player.playerId] = playerSender
        playerSender.respondToPlayer(loginSuccess(player.position.x, player.position.y))
        initialState = self.getInitialGameState()
        playerSender.sendMessages(initialState.toMessages())
        print('Player '+playerId+' was added to the game')

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

#Ticks cookie movement and sends updates to players
class ServerUpdater():

    def run(self):
        while True:
            GameServer.instance().moveCookies()
            senders, gameState = GameServer.instance().getGameState()
            if gameState is not None:
                messages = gameState.toMessages()
                [sender.sendMessages(messages) for sender in senders]
            time.sleep(0)

#Process requests from players and gives them to the game server
class RequestReader():

    def run(self, requestQueue):
        while True:
            clientRequest = requestQueue.get()
            try:
                GameServer.instance().considerPlayerRequest(clientRequest.message)
            except ClientRequestError as e:
                clientRequest.origin.sendall(bytes(e.msg))
            time.sleep(0)

class CookieMover():

    def run(self):
        while True:
            GameServer.instance().moveCookies()
            time.sleep(COOKIE_SPEED)

class PlayerReceiver():

    def __init__(self, playerId, playerSocket, requestQueue):
        self.playerId = playerId
        self.playerSocket = playerSocket
        self.requestQueue = requestQueue

    def listen(self):
        while True:
            try:
                msg, b, c, d = self.playerSocket.recvmsg(4096)
                self.requestQueue.put(ClientRequest(msg, self.playerSocket, self.playerId))
                time.sleep(0)
            except (KeyboardInterrupt, socket.error, SystemExit) as error:
                self.playerSocket.shutdown(socket.SHUT_RDWR)
                self.playerSocket.close()

                raise error

class PlayerSender():

    def __init__(self, playerId, clientSocket):
        self.playerId = playerId
        self.clientSocket = clientSocket

    def respondToPlayer(self, message):
        raw = bytes(message)
        self.clientSocket.sendall(raw)

    def sendMessages(self, messages):
        for msg in messages:
            self.respondToPlayer(msg)

class ClientRequestError(Exception):
    def __init__(self, msg):
        self.msg = msg