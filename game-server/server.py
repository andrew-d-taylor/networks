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

        GameServer.instance().requestQueue = requestQueue

        updater = ServerUpdater()
        receiver = RequestReader()
        cookieMover = CookieMover()

        updateThread = threading.Thread(target=updater.run)
        updateThread.daemon = True

        receiverThread = threading.Thread(target=receiver.run, args=(requestQueue,))
        receiverThread.daemon = True

        moverThread = threading.Thread(target=cookieMover.run)
        moverThread.daemon = True

        updateThread.start()
        receiverThread.start()
        moverThread.start()

        try:
            print('Server started listening')
            while True:
                clientSocket, clientAddress = self.loginSocket.accept()
                print('Connection made with front server')
                self.loginQueue.put(clientSocket)
        except (KeyboardInterrupt, SystemExit, socket.error):
            self.loginSocket.shutdown(socket.SHUT_RDWR)
            self.loginSocket.close()
            sys.exit()

#Spin off login(player) threads
def loginWorker(loginQueue):
    while True:
        clientSocket = loginQueue.get()
        loginResponder(clientSocket)

def loginResponder(clientSocket):
        request, b, c, d = clientSocket.recvmsg(4096)
        request = request.decode('UTF-8')
        clientRequest = ClientRequest(request, clientSocket, request.split()[1])
        if not clientRequest.command.isLogin():
            clientSocket.sendall(bytes(badCommand("Player must log in before playing. Goodbye.")))
            print('User tried to play without logging in')
            clientSocket.close()
        else:
            playGame(clientRequest.playerId, clientSocket)