__author__ = 'andrew'


def respond(clientConnection):
    print('Respond method hit')
    clientConnection.send(b'HellO! Send 1 to close the connection.\n')
    sentinel = 1
    response = 0

    while response is not sentinel:
        clientConnection.send(b'Nope\n')
        response = int((clientConnection.recv(4096)))

    clientConnection.close()