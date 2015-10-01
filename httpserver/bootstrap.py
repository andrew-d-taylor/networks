__author__ = 'andrew'

from server import Server
import sys

server = Server('localhost', int(sys.argv[1]))
server.start()