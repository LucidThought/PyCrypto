

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
#  print(hashlib.sha256(str_to_bytes("test")).hexdigest())  # This gives a 32-byte key value
#  print(hashlib.md5("test".encode()).hexdigest()) # This gives a 16-byte key value
#  rand = os.urandom(32)
#  print(hashlib.md5(rand).hexdigest()) # Randomly generate 16-byte key
#  print(os.urandom(32)) # Randomly generate 32-byte key 
#  print(Random.new().read(AES.block_size))

  if (len(sys.argv) < 4)
    print("Use this application with the following:")
    print("python3 client.py [read/write] hostname:port [none|aes128|aes256] key")
    print("You must use at least four of the above arguments, in the specified order")
    sys.exit("Incorrect user input")

  if (sys.argv[4]=='none'):
    COMMAND = str(sys.argv[1])
    FILENAME = str(sys.argv[2])
    DEST = str(sys.argv[3])
    CIPHER = 'none'

  else:
    if(len(sys.argv)==5):
      COMMAND = str(sys.argv[1])
      FILENAME = str(sys.argv[2])
      DEST = str(argv[3])
      CIPHER = str(argv[4])
      PW = str(argv[5])
      print("Password: " + PW)
      KEY = hashlib.sha256(str_to_bytes(PW)).hexdigest()

    elif(len(sys.argv)==4):
      COMMAND = str(sys.argv[1])
      FILENAME = str(sys.argv[2])
      DEST = str(argv[3])
      CIPHER = 'none'

    
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

    #send just the header 
    header = createHeader(COMMAND,FILENAME,CIPHER)
    clientSocket.send( header )
    temp_data = clientSocket.recv(1024)
    array = temp_data.split(b". .") 
    ##print(array[0])
    file_size = int(array[0])
    ##print(file_size)
    
    bytes_written = 0
    buffSize = 1024
    ## this writing to a file is here purely for testing. the > operator now works.
    with open('test.jpg','wb+') as outFile:

      while(bytes_written < file_size):
        data = clientSocket.recv(buffSize)
        if not data:
          break

        if len(data) + bytes_written > file_size:
          data = data[:file_size-bytes_written]

        sys.stdout.buffer.write(data)
        outFile.write(data)
        bytes_written += len(data)
 
  elif(COMMAND=='write'):
    
    payload = b""
    with open('temp_dat','wb+') as tempFile:
    
      while True: 
        data = sys.stdin.buffer.read(1)
        if not data:
          break
        payload += data
        tempFile.write(data) 
    tempFile.close()
   
    # I still have to re work this code.
    # WE NEED TO SEND HEADER AHEAD OF TIME IN SEPRATE TRANSMISSION, AND INSTEAD OF SENDING DATA IN ONE SHOT
    # NEED TO SEND 1024 AT A TIME. FILES LARGER THEN RAM WILL BUFFER OVERFLOW OTHERWISE
    # ASSIGNMENT SPECS SAY NOT TO DO THIS
    header = createHeader(COMMAND,FILENAME,CIPHER)
    clientSocket.send( header + payload)

  else:
    print("I don't know how to " + COMMAND)

def createHeader(COMMAND,CIPHER,FILENAME):

  delimiter = ". ."
  header = bytes(COMMAND+"\n"+CIPHER+"\n"+FILENAME+delimiter,"UTF-8")
  return header

if __name__ == '__main__':
#  print(str(hashlib.sha256(str_to_bytes("test")).digest()))
#  print(str(Random.new().read(AES.block_size)))
  main()
  startClientNone()
