__author__ = 'andrew'

from server import Server
import sys
import os.path


def notInteger(string):
    try:
        int(string)
        return False
    except ValueError:
        return True

configFile = 'server.config'
configMap = {}

try:
    lines = [line.rstrip('\n') for line in open(configFile)]
    for line in lines:
        if line[0] is not '#':
            key = line[:line.find('=')]
            value = line[line.rfind('=')+1:]
            configMap[key.strip()] = value.strip()
except OSError:
    print('Error reading from server.config file. Starting server with default port 9999 in current directory')
    configMap['port'] = 9999
    currentDirectory = repr(__file__)
    currentDirectory = currentDirectory[:currentDirectory.rfind(os.path.sep)]
    configMap['basedir'] = currentDirectory

if not configMap['port'] or notInteger(configMap['port']):
    print('Error reading port number from server.config file. Defaulting to port 9999')
    configMap['port'] = 9999

if not configMap['basedir'] or not os.path.isdir(configMap['basedir']):
    print('Error reading basedir from server.config file. Defaulting to current working directory')
    configMap['basedir'] = os.path.dirname(os.path.abspath(__file__))

if configMap['basedir'] is '.':
    configMap['basedir'] = os.path.abspath('.')

server = Server('localhost', int(configMap['port']), configMap['basedir'])
server.start()
