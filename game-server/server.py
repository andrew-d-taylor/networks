__author__ = 'andrew'

import socket
from multiprocessing.dummy import Queue as ThreadQue
import threading
import sys
from protocol import ClientRequest
from services import *
from game_domain import *


class FrontServer():

    def __init__(self, port):
        self.loginSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port = port
        self.loginQueue = ThreadQue()

    def start(self):
        self.loginSocket.bind(self.port)
        self.loginSocket.listen(500)

        for x in range(100):
            thread = threading.Thread(target=loginWorker, args=(self.loginQueue,))
            thread.daemon = True
            thread.start()

        while True:
            clientSocket, clientAddress = self.loginSocket.accept()
            self.loginQueue.put(clientSocket)


def loginWorker(loginQueue):
    while True:
        clientSocket = loginQueue.get()
        loginResponder(clientSocket)

def loginResponder(clientSocket):
    try:
        request, b, c, d = clientSocket.recvmsg(4096)
        request = request.decode('UTF-8')
        clientRequest = ClientRequest(request)
        if not clientRequest.command.isLogin():
            #write back error response
            clientSocket.close()
        else:
            playGame(clientRequest.playerId, clientSocket)
    except socket.error:
        raise socket.error

def playGame(playerId, clientSocket):
    gameServer = GameServer()
    gameServer.addPlayerToGame(playerId, clientSocket)

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class GameServer(metaclass=Singleton):
    pass

    #Only called once
    def __init__(self):
        self.test = "Tes"
        self.playerService = PlayerService()

    def addPlayerToGame(self, playerId, clientSocket):
        player = self.playerService.register(playerId)
        playerSession = PlayerSession(player, clientSocket)

class PlayerSession():

    def __init__(self, player, playerSocket):
        self.player = player
        self.playerSocket = playerSocket

class OtherSingleton(metaclass=Singleton):
    pass

    def foo(self):
        print("Food")