__author__ = 'andrew'
import sys
import socket as s
from respond import respond
from multiprocessing.dummy import Pool as ThreadPool


class Server():

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = s.socket()
        self.threadPool = ThreadPool(20)

    def start(self):
        try:
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            print('Server starting')
            while True:
                (clientSocket, clientAddress) = self.socket.accept()
                print('Connection accepted')
                self.threadPool.map_async(respond, [clientSocket])
                print('Connection delegated to respond')
        except (KeyboardInterrupt, s.error):
            self.socket.shutdown(s.SHUT_RDWR)
            self.socket.close()
            sys.exit()
