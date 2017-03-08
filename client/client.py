

#!/usr/bin/python3

import base64
import hashlib
import sys
import time
import socket
import os



#from Crypto import Random
#from Crypto.Cipher import AES

COMMAND = ''
FILENAME = ''
DEST = ''
CIPHER = ''
KEY = ''
PW = ''
FILE = b''

# The following command read stdin as a bytestream:
# inBytes = sys.stdin.buffer.read()
# print(inBytes)
# outFile = open("pic.jpg","wb")
# outFile.write(inBytes)
# outFile.close()

def main():
  global COMMAND
  global FILENAME
  global DEST
  global CIPHER
  global KEY 
  global PW
  global FILE
  print("Main")
#  print(hashlib.sha256(str_to_bytes("test")).hexdigest())  # This gives a 32-byte key value
#  print(hashlib.md5("test".encode()).hexdigest()) # This gives a 16-byte key value
#  rand = os.urandom(32)
#  print(hashlib.md5(rand).hexdigest()) # Randomly generate 16-byte key
#  print(os.urandom(32)) # Randomly generate 32-byte key 
#  print(Random.new().read(AES.block_size))

  # fixed BUG HERE --> CALLING FILE = sys.stdin.buffer.read() can't be called in global during read mode
  if (sys.argv[4]=='none'):
    COMMAND = str(sys.argv[1])
    FILENAME = str(sys.argv[2])
    DEST = str(sys.argv[3])
    CIPHER = 'none'
    if COMMAND == "write":
      FILE = sys.stdin.buffer.read()

  else:
    if(len(sys.argv)==5):
      COMMAND = str(sys.argv[1])
      FILENAME = str(sys.argv[2])
      DEST = str(argv[3])
      CIPHER = str(argv[4])
      PW = str(argv[5])
      print("Password: " + PW)
      KEY = hashlib.sha256(str_to_bytes(PW)).hexdigest()
      if COMMAND == "write":
        FILE = sys.stdin.buffer.read()

    elif(len(sys.argv)==4):
      COMMAND = str(sys.argv[1])
      FILENAME = str(sys.argv[2])
      DEST = str(argv[3])
      CIPHER = 'none'
      if COMMAND == "write":
        FILE = sys.stdin.buffer.read()
  
def str_to_bytes(data):
  utype = type(b''.decode('utf-8'))
  if isinstance(data, utype):
    return data.encode('utf-8')
  return data

def startClientNone():
  global COMMAND
  global DEST
  global FILE
  separator = DEST.find(":")
  ipDEST = DEST[0:separator]
  sockDEST = DEST[separator+1:]
  clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  clientSocket.connect((ipDEST,int(sockDEST)))
  print(COMMAND)

  if(COMMAND=="read"):
    print("READ")  
    
    header = createHeader(COMMAND,FILENAME,CIPHER)
    clientSock.send( header )    
 
  if(COMMAND=='write'):
    
    #send header + payload
    print("debugx")
    header = createHeader(COMMAND,FILENAME,CIPHER)
    clientSocket.send( header + FILE)
    print("debugxx")  

  else:
    print("I don't know how to " + COMMAND)

def createHeader(COMMAND,CIPHER,FILENAME):

  delimiter = ". ."
  header = bytes(COMMAND+"\n"+CIPHER+"\n"+FILENAME+delimiter,"UTF-8")
  return header

if __name__ == '__main__':
  print("Start")
#  print(str(hashlib.sha256(str_to_bytes("test")).digest()))
#  print(str(Random.new().read(AES.block_size)))
  main()
  print("debug1")
  startClientNone()
