Andrew Taylor
Assignment #2: Simple Http Server
COS 540

Language: Python
To start the server:
	- Configure the desired port number and base directory in server.config
	- Run the bootstrap file:
		$ python bootstrap.py

This assignment was a lot of fun!

In the course of writing the server, I learned quite a few things about
the expectations of web browsers. Initially, I mistakenly thought that
a connection established by the client must be persisted throughout possibly
multiple requests - that all requests were essentially over a Keep-Alive
connection. And while browsers will accept this if offered, it's not necessary,
which simplified my thinking of the server.

As naive as it sounds, I was amazed that sending over binary data produced intelligible
results so consistently. I have not worked with image or multimedia files often, so reading
those files as binary and sending them across the wire was surprisingly easy. In essence, I
was enlightened by the wisdom and power of mime types.

I tried a few multithreading designs based off of Python's multiprocessing.dummy
API, and, while having some frustrating false starts, settled on a simple Queueing
model that just works.