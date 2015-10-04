__author__ = 'andrew'
import sys
import socket as s
from respond import respond, Response
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing.dummy import Queue as ThreadQue
import threading



class Server():

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = s.socket(s.AF_INET, s.SOCK_STREAM)
        self.threadPool = ThreadPool(200)
        self.q = ThreadQue()

    def start(self):

        for x in range(100):
            thread = threading.Thread(target=responder, args=(self.q,))
            thread.daemon = True
            thread.start()
        try:
            self.socket.bind((self.host, self.port))
            self.socket.listen(500)

            print('Server starting')
            while True:
                clientSocket, clientAddress = self.socket.accept()
                self.q.put(clientSocket)
        except (KeyboardInterrupt, s.error):
            self.socket.shutdown(s.SHUT_RDWR)
            self.socket.close()
            sys.exit()

def responder(q):
        while True:
            connectionSocket = q.get()
            respond(connectionSocket)