__author__ = 'andrew'
import socket as s
import mimetypes
import os
import datetime

def respond(clientConnection):

    try:
        request, b, c, d = clientConnection.recvmsg(4096)
        request = request.decode('UTF-8')
        print('New Request:\n\n'+request+'\n\n')

        header = request[:request.find("\n")]
        response = Response(header)
        print("File: "+response.fileName)
        print("Code: "+str(response.responseCode))
        print("MimeType: "+response.mimeType)
        writeResponse(clientConnection, response)
        clientConnection.shutdown(s.SHUT_RDWR)
        clientConnection.close()
    except KeyboardInterrupt:
        clientConnection.shutdown(s.SHUT_RDWR)
        clientConnection.close()
        raise KeyboardInterrupt
    except s.error:
        clientConnection.shutdown(s.SHUT_RDWR)
        clientConnection.close()
        raise s.error

def writeResponse(client, response):
    header = generateResponseHeader(response.responseCode, response.responseDescriptor)
    date = bytes('Date: '+str(datetime.datetime.now())+'\n', 'UTF-8')
    server = b'Andrews HTTP Server \n'
    type = bytes('Content-Type: '+response.mimeType+'\n', 'UTF-8')
    if response.file is None:
        content = generate404Response(response.fileName)
    else:
        content = response.file.read()
    length = bytes('Content-Length: '+str(len(content))+'\n\n', 'UTF-8')
    response = header+date+server+type+length+content
    client.sendall(response)

def generate404Response(filename):
    return bytes('The requested file '+filename+' does not exist\n', 'UTF-8')

def generateResponseHeader(code, descriptor):
    return bytes('HTTP/1.1 '+str(code)+' '+descriptor+'\n', 'UTF-8')

class Response():

    def __init__(self, requestString):
        self.fileName = self.__parseFileName(requestString)
        (self.mimeType, self.encoding) = self.__fetchMimeType(self.fileName)
        self.file = self.__fetchFile(self.fileName)
        self.responseCode, self.responseDescriptor = self.__createResponseCode(self.file)

    def __parseFileName(self, requestString):
        stringAfterMethod = requestString[requestString.find(' '):]
        filename = stringAfterMethod[:stringAfterMethod.rfind(' ')]
        filename = filename.strip()

        # Strip leading / unless the request is for base directory
        print('Filename: '+str(filename))
        if filename[0] is '/' and len(filename) is not 1:
            filename = filename[1:]

        return filename

    def __fetchMimeType(self, fileName):
        try:
            (mimeType, encoding) = mimetypes.guess_type(fileName)
        except KeyError:
            mimeType, encoding = None
        finally:
            if mimeType is None:
                if fileName is '/' or os.path.isdir(fileName):
                    mimeType = 'text/html'
                else:
                    mimeType = 'application/unknown'
            if encoding is None:
                encoding = 'UTF-8'

        return mimeType, encoding

    def __fetchDirectory(self, directoryName):
        list = os.listdir(directoryName)
        return generateDirectoryHtml(list)

    def __fetchFile(self, filename):
        try:
            if filename is '/':
                file = self.__fetchDirectory('.')
            elif os.path.isdir(filename):
                file = self.__fetchDirectory(filename)
            else:
                file = open(filename, 'rb')
        except OSError:
            file = None
        finally:
            return file

    def __createResponseCode(self, file):
        if file is None:
            return 404, 'NOT FOUND'
        else:
            return 200, 'OK'

def generateDirectoryHtml(list):
    directoryResponseFile = open('directory.html', 'w+')
    headBlock = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <title>Directory</title>
    </head>
    <body>
    <ul>

    '''
    entries = ''
    for item in list:
        li = createListItem(item)
        entries += li

    footBlock = '''
    </body>
    </html>
    '''

    directoryResponseFile.write(headBlock+entries+footBlock)
    directoryResponseFile.close()
    return open('directory.html', 'rb')

def createListItem(item):
    return '<li href='+item+'>'+item+'</li>'
