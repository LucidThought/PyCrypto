

#!/usr/bin/python3

import base64
import hashlib
import sys
import time
import socket

from Crypto import Random
from Crypto.Cipher import AES

COMMAND = ''
FILENAME = ''
DEST = ''
CIPHER = ''
KEY = ''
PW = ''
FILE = sys.stdin.buffer.read()


# The following command read stdin as a bytestream:
# inBytes = sys.stdin.buffer.read()
# print(inBytes)
# outFile = open("pic.jpg","wb")
# outFile.write(inBytes)
# outFile.close()

def start():
  global COMMAND
  global FILENAME
  global DEST
  global CIPHER
  global KEY
  global PW
  global FILE

  print(hashlib.sha256(str_to_bytes("test")).digest())
  print(Random.new().read(AES.block_size).toString())

  if (sys.argv[4]=='none'):
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
    elif(len(sys.argv)==4):
      COMMAND = str(sys.argv[1])
      FILENAME = str(sys.argv[2])
      DEST = str(argv[3])
      CIPHER = 'none'
  
def startClient(destAddr):
  global COMMAND
  global DEST
  global FILE
  separator = DEST.find(":")
  ipDEST = DEST[0:separator]
  sockDEST = DEST[separator+1:]
  clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  clientSocket.bind(ipDEST,sockDEST)
#  if(COMMAND=='read'):
    
#  elif(COMMAND=='write'):
    
#  else:
#    print("I don't know how to " + COMMAND)


if(__name__ == "__main__"):
  print(hashlib.sha256(str_to_bytes("test")).digest())
  print(Random.new().read(AES.block_size).toString())
  start()
