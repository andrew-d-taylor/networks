__author__ = 'andrew'
import socket as s

def createMimeTypeMap():

    mimeMap = {}
    lines = [line.rstrip('\n') for line in open('mimetypes.cfg')]
    for line in lines:
        key = line[:line.find(':')]
        value = line[line.rfind(':') + 1:]
        mimeMap[key] = value
    return mimeMap

mimeMap = createMimeTypeMap()

def getMimeMap():
    return mimeMap

def respond(clientConnection):

    try:
        print('waiting for recv')
        request = clientConnection.recv(4096)
        print('request: '+request)
        header = request[:request.find("\n")]
        print(header)
        response = Response(header)
        clientConnection.close()
    except KeyboardInterrupt:
        clientConnection.shutdown(s.SHUT_RDWR)
        clientConnection.close()
        raise KeyboardInterrupt
    except s.error:
        clientConnection.shutdown(s.SHUT_RDWR)
        clientConnection.close()
        raise s.error

class Response():

    def __init__(self, requestString):
        self.fileName = self.__parseFileName(requestString)
        self.mimeType = mimeMap[self.fileName[self.fileName.rfind("."):]]
        self.file = self.__fetchFile(self.fileName)
        self.responseCode = self.__createResponseCode(self.file)


    def __parseFileName(self, requestString):
        stringAfterGet = requestString[requestString.find(' '):]
        filename = stringAfterGet[:stringAfterGet.rfind(' ')]
        return filename.strip()

    def __fetchMimeType(self, extension):
        try:
            type = mimeMap[extension]
            return type
        except KeyError:
            return None

    def __fetchFile(self, filename):
        try:
            file = open(filename)
        except OSError:
            file = None
        finally:
            return file

    def __createResponseCode(self, file):
        if file is None:
            return 404
        else:
            return 200
