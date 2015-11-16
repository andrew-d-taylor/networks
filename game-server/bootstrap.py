__author__ = 'andrew'

from server import FrontServer

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
    print('Error reading from server.config file. Starting server with default port 9999')
    configMap['port'] = 9999

if not configMap['port'] or notInteger(configMap['port']):
    print('Error reading port number from server.config file. Defaulting to port 9999')
    configMap['port'] = 9999

frontServer = FrontServer(int(configMap['port']))
frontServer.start()