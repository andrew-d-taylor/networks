Andrew Taylor
Assignment#1 : Guessing Game
COS 540

Language: Python 3

Run (requires Python 3):
$ python server.py <port#>

Synopsis:

I learned quite a few things about both sockets and Python during the course of completing this assignment.
I have very little experience with Python, and am hoping that these assignments will be a good vessel for
learning and becoming comfortable in that language.

An interesting quirk of Python that I encountered: Magically, to convert a string into its byte representation,
you can simply prepend the character b to a string literal. This came in handy when writing string responses from
the server to the client via the connection socket.

Python made interacting with the sockets interface relatively easy. I'm curious to see how a socket server capable of
multithreading could be implemented. The call to listen on the socket accepted a parameter, ranged 0 to 5, of maximum
connections it should queue. I'm curious as to how to maintain the connection queueing while spinning off threads
as needed.