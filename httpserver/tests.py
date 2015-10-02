__author__ = 'andrew'

from respond import getMimeMap

mimeMap = getMimeMap()

def testMimeTypeReading(extension):
    print(mimeMap[extension])

testMimeTypeReading('.js')