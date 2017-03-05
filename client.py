#!/usr/bin/python

import base64
import hashlib
import sys
import time

from Crypto import Random
from Crypto.Cipher import AES

COMMAND = ''
FILENAME = ''
DEST = ''
CIPHER = ''
KEY = ''
PW = ''


# The following command read stdin as a bytestream:
# inBytes = sys.stdin.buffer.read()
# print(inBytes)
# outFile = open("pic.jpg","wb")
# outFile.write(inBytes)
# outFile.close()

def start(self)
  global COMMAND = ''
  global FILENAME = ''
  global DEST = ''
  global CIPHER = ''
  global KEY = ''

  if(sys.argv[4]=='none'):
    COMMAND = str(sys.argv[1])
    FILENAME = str(sys.argv[2])
    DEST = str(argv[3])
    CIPHER = 'none'
  else:
    if(len(sys.argv)==5):
    COMMAND = str(sys.argv[1])
    FILENAME = str(sys.argv[2])
    DEST = str(argv[3])
    CIPHER = str(argv[4])
    PW = str(argv[5])
    print("Password: " + PW)
    KEY = hashlib.sha256(str_to_bytes(PW)).digest()
  elif(len(sys.argv)==4)
    COMMAND = str(sys.argv[1])
    FILENAME = str(sys.argv[2])
    DEST = str(argv[3])
    CIPHER = 'none'


if __name__ == '__main__':
    start()
