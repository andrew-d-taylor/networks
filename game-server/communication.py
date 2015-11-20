__author__ = 'andrew'

import socket
import time
from protocol import ClientRequest
from protocol import RequestParsingException
from protocol import badCommand
from protocol import encoding

class PlayerReceiver():

    def __init__(self, playerId, playerSocket, requestQueue):
        self.playerId = playerId
        self.playerSocket = playerSocket
        self.requestQueue = requestQueue

    def listen(self):
        while True:
            try:
                msg, b, c, d = self.playerSocket.recvmsg(4096)
                msg = msg.decode('UTF-8')
                request = ClientRequest(msg, self.playerSocket, self.playerId)
                if request.command.isLogin():
                    self.playerSocket.sendall(bytes(badCommand('Already logged in.'), encoding))
                else:
                    self.requestQueue.put(request)
                time.sleep(0)
            except RequestParsingException:
                self.playerSocket.sendall(bytes(badCommand('Could not understand request'), encoding))
            except (KeyboardInterrupt, SystemExit):
                self.playerSocket.shutdown(socket.SHUT_RDWR)
                self.playerSocket.close()
                break
            except (socket.error, UnicodeDecodeError):
                logout = ClientRequest('logout', None, self.playerId)
                self.requestQueue.put(logout)
                break

class PlayerSender():

    def __init__(self, playerId, playerSocket):
        self.playerId = playerId
        self.playerSocket = playerSocket

    def respondToPlayer(self, message):
        raw = bytes(message, encoding)
        self.playerSocket.sendall(raw)

    def sendMessages(self, messages):
        for msg in messages:
            self.respondToPlayer(msg)