__author__ = 'andrew'

import socket
import time
from protocol import ClientRequest
from settings import encoding

class PlayerReceiver():

    def __init__(self, playerId, playerSocket, requestQueue):
        self.playerId = playerId
        self.playerSocket = playerSocket
        self.requestQueue = requestQueue

    def listen(self):
        while True:
            try:
                print('PlayerReceiver for '+self.playerId+" is now listening")
                msg, b, c, d = self.playerSocket.recvmsg(4096)
                msg = msg.decode('UTF-8')
                print('Message received: '+msg)
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
        raw = bytes(message, encoding)
        print('Sending message to '+self.playerId)
        self.clientSocket.sendall(raw)

    def sendMessages(self, messages):
        for msg in messages:
            self.respondToPlayer(msg)