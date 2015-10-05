__author__ = 'andrew'
import sys
import socket as s
import os.path
from respond import respond
from multiprocessing.dummy import Queue as ThreadQue
import threading

class Server():

    def __init__(self, host, port, basedir):
        self.host = host
        self.port = port
        self.basedir = self.__formatBaseDir(basedir)
        self.socket = s.socket(s.AF_INET, s.SOCK_STREAM)
        self.q = ThreadQue()

    def start(self):

        for x in range(100):
            thread = threading.Thread(target=responder, args=(self.q,))
            thread.daemon = True
            thread.start()
        try:
            self.socket.bind((self.host, self.port))
            self.socket.listen(500)

            print('Server starting on port '+str(self.port)+' from base directory '+self.basedir)
            while True:
                clientSocket, clientAddress = self.socket.accept()
                self.q.put((clientSocket, self.basedir))
        except (KeyboardInterrupt, s.error):
            try:
                self.socket.shutdown(s.SHUT_RDWR)
                self.socket.close()
                print('Server socket closed')
                sys.exit()
            except s.error:
                print('Server port busy. Try another port.')
                sys.exit()

    def __formatBaseDir(self, basedir):
        #Trim trailing slash for convenience
        if basedir[len(basedir) - 1] is os.path.sep:
            basedir = basedir[:-1]
        return basedir

def responder(q):
        while True:
            connectionSocket, basedir = q.get()
            respond(connectionSocket, basedir)