__author__ = 'andrew'

import socket as s
from response import respond
from multiprocessing.dummy import Pool as ThreadPool


class Server():

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = s.socket()
        self.threadPool = ThreadPool(20)

    def start(self):
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        print('Server starting')
        while True:
            (clientSocket, clientAddress) = self.socket.accept()
            print('Connection accepted')
            self.threadPool.map_async(respond, [clientSocket])
            print('Returned')