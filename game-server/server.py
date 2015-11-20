__author__ = 'andrew'

import socket
from multiprocessing.dummy import Queue as ThreadQue
import threading
import sys
import protocol
from game import Game
from game import PlayerGameError
from queue import Queue
import time
import settings

class FrontServer():

    def __init__(self):
        self.loginSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port = settings.port
        self.loginQueue = ThreadQue()

    def start(self):
        self.loginSocket.bind(('localhost',self.port))
        self.loginSocket.listen(200)

        for x in range(10):
            thread = threading.Thread(target=loginWorker, args=(self.loginQueue,))
            thread.daemon = True
            thread.start()

        requestQueue = Queue()
        Game.instance().requestQueue = requestQueue

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
        clientSocket.sendall(bytes(protocol.playerMessage('', 'Welcome. Log in to play the game.'), settings.encoding))
        request, b, c, d = clientSocket.recvmsg(4096)
        request = request.decode('UTF-8')
        try:
            clientRequest = protocol.ClientRequest(request, clientSocket, request.split()[1])
            if not clientRequest.command.isLogin():
                raise protocol.RequestParsingException
            else:
                Game.instance().considerPlayerRequest(clientRequest)
        except (protocol.RequestParsingException, IndexError):
                clientSocket.sendall(bytes(protocol.badCommand("Player must log in before playing. Goodbye."), settings.encoding))
                clientSocket.close()


#Ticks cookie movement and sends updates to players
class ServerUpdater():

    def run(self):
        while True:
            senders, gameState = Game.instance().getGameState()
            if gameState is not None:
                messages = gameState.toMessages()
                for sender in senders:
                    sender.sendMessages(messages)
            time.sleep(0)

#Process requests from players and gives them to the game server
class RequestReader():

    def run(self, requestQueue):
        while True:
            clientRequest = requestQueue.get()
            try:
                Game.instance().considerPlayerRequest(clientRequest)
            except PlayerGameError as e:
                clientRequest.origin.sendall(bytes(e.msg, settings.encoding))
            time.sleep(0)

#Move in-flight cookies every so often
class CookieMover():

    def run(self):
        while True:
            Game.instance().moveCookies()
            time.sleep(settings.cookie_speed)