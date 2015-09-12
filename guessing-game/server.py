__author__ = 'andrew'

import socket as s
import random
import sys

socket = s.socket()
host = 'localhost'
annoyingAsciiArt = '(╯°□°）╯︵ ┻━┻   ┬──┬◡ﾉ(° -°ﾉ)   (╯°□°）╯︵ ┻━┻'

if len(sys.argv) < 2:
    sys.stderr.write('User must provide a port number on server startup\n')
    sys.exit()

try:
    port = int(sys.argv[1])
except ValueError:
    sys.stderr.write('Port number must be an integer\n')
    sys.exit()

if port < 0 or port > 65535:
    sys.stderr.write('Port number must be in valid range\n')
    sys.exit()

socket.bind((host, port))
socket.listen(5)
print('\n')
print(annoyingAsciiArt)
print('Server listening on host, port -- '+str(socket.getsockname()))
print(annoyingAsciiArt)
print('\n')

def playGameWithClient(client):
    sentinel = random.randint(1, 100)
    print('Sentinel = '+str(sentinel))
    guess = sentinel - 1
    client.send(b'+ Welcome. Guess a number between 1 and 100\n')
    while guess is not sentinel:
        try:
            guess = int((client.recv(4096)))
            print('Guess = '+str(guess))
        except ValueError:
            client.send(b'! Guesses must be between 1 and 100\n')
            continue

        if guess > sentinel:
            client.send(b'< Too high! Try again\n')
        elif guess < sentinel:
            client.send(b'> Too low! Try again\n')

    client.send(b'* Nice! See you next time\n')
    client.close()
    print('Server closing connection with client\n')


try:
    while True:
        (connectionSocket, clientAddress) = socket.accept()
        print(annoyingAsciiArt)
        print('Server accepted connection from client '+str(clientAddress[0]))
        print(annoyingAsciiArt)
        print('\n')
        playGameWithClient(connectionSocket)
except KeyboardInterrupt:
    socket.close()
    sys.exit()