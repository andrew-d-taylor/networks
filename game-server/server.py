__author__ = 'andrew'

import socket
from multiprocessing.dummy import Queue as ThreadQue
import threading
import sys
from protocol import ClientRequest
from services import *
from game_domain import *
from game import *


class FrontServer():

    def __init__(self, port):
        self.loginSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port = port
        self.loginQueue = ThreadQue()

    def start(self):
        self.loginSocket.bind(('localhost',self.port))
        self.loginSocket.listen(200)

        for x in range(10):
            thread = threading.Thread(target=loginWorker, args=(self.loginQueue,))
            thread.daemon = True
            thread.start()

        requestQueue = Queue()
        responseQueue = Queue()

        GameServer.instance().requestQueue = requestQueue

        updater = ServerUpdater()
        receiver = RequestReader()

        updateThread = threading.Thread(target=updater.run)
        receiverThread = threading.Thread(target=receiver.run, args=(requestQueue,))

        updateThread.start()
        receiverThread.start()

        while True:
            clientSocket, clientAddress = self.loginSocket.accept()
            self.loginQueue.put(clientSocket)


#Spin off login(player) threads
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