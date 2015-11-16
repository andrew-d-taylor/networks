__author__ = 'andrew'

import socket
from multiprocessing.dummy import Queue as ThreadQue
from queue import Queue
from protocol import *
import threading
import services
import time

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
        self.test = "Test"
        self.playerService = services.PlayerService()
        self.gameService = services.GameService()
        self.playerReceivers = {}
        self.playerSenders = {}
        self.requestQueue = None

    #Called only by the RequestReader thread
    def considerPlayerRequest(self, request):
        return None

    #Called only by the ServerUpdater thread
    def getGameState(self):
        players = self.playerService.getLoggedInPlayers()
        cookies = self.gameService.getCookies()
        gameMap = self.gameService.getMap()
        return self.playerSenders, GameState(gameMap, cookies, players)

    #Called only by the main/log-in thread
    def addPlayerToGame(self, playerId, clientSocket):
        player = self.playerService.register(playerId)
        playerReceiver = PlayerReceiver(player, clientSocket, self.requestQueue)
        playerReceiver.listen()
        playerSender = PlayerSender(player, clientSocket)
        self.playerReceivers[player.playerId] = playerReceiver
        self.playerSenders[player.playerId] = playerSender

class GameState():

    def __init__(self, gameMap, cookies, players):
        self.gameMap = gameMap
        self.cookies = cookies
        self.players = players

    def toMessages(self):
        messages = []
        mapMessages = self.__convertMap()
        cookieMessages = self.__convertCookies()
        playerMessages = self.__convertPlayers()
        messages.append(mapMessages)
        messages.append(cookieMessages)
        messages.append(playerMessages)
        return messages

    def __convertMap(self):
        return None

    def __convertCookies(self):
        return None

    def __convertPlayers(self):
        return None

class ServerUpdater():

    def run(self):
        while True:
            senders, gameState = GameServer.instance().getGameState()
            messages = gameState.toMessages()
            [sender.sendMessages(messages) for sender in senders]
            time.sleep(0)

class RequestReader():

    def run(self, requestQueue):
        while True:
            msg = requestQueue.get()
            GameServer.instance().considerPlayerRequest(ClientRequest(msg))
            time.sleep(0)

class PlayerReceiver():

    def __init__(self, player, playerSocket, requestQueue):
        self.player = player
        self.playerSocket = playerSocket
        self.requestQueue = requestQueue

    def listen(self):
        while self.player.loggedIn:
            msg = self.playerSocket.recvmsg(4096)
            self.requestQueue.put(msg)
            time.sleep(0)
        self.playerSocket.close()

class PlayerSender():

    def __init__(self, player, clientSocket):
        self.player = player
        self.clientSocket = clientSocket

    def respondToPlayer(self, message):
        raw = bytes(message)
        self.clientSocket.sendall(raw)

    def sendMessages(self, messages):
        for msg in messages:
            self.respondToPlayer(msg)

class OtherSingleton(ThreadSafeSingleton):
    pass

    def foo(self):
        print("Food")