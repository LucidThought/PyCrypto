

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

  if (len(sys.argv) < 4):
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

    #send just the header, requesting a file from the server
    segment_size = 1024 
    header = sendHeader(COMMAND,FILENAME,CIPHER,segment_size,clientSocket)

    ## get file header from server (file size delmited with ". ." on the end)
    temp_data = clientSocket.recv(1024)
    array = temp_data.split(b". .") 
    ##print(array[0])
    file_size = int(array[0]) ## extract the files size from header.
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
      outFile.close()
 
  elif(COMMAND=='write'):
    
    payload_file = "temp_data"
    payload = b""
    with open(payload_file,'wb+') as f:
    
      while True: 
        data = sys.stdin.buffer.read(1)
        if not data:
          break
        payload += data
        f.write(data) 
    f.close()
    
    #First communication to the server should be the Cipher + IV for CBC
    # example 
    # iv = createIV()
    # initalizationHeader = iv + ". ." + cipher
    # clientSock.send( initalization vector )

    ## this entire header needs to be encrypted
    segment_size = 1024  #bytes 
    
    #Create and send header
    sendHeader(COMMAND,FILENAME,CIPHER,segment_size,clientSocket)
    #Send payload (the actual file)
    sendFileMode(payload_file,segment_size,clientSocket)
        # ^ We will likely have to add the section below as part of the above loop. after we read an x-byte segment, we send it and continue reading
    # ^ The server will have to write out each piece (decrypted when necessary) and check each piece for the EOF signal, not add the EOF signal to the file, and close the file
    
  else:
    print("I don't know how to " + COMMAND)
      
def sendFileMode(payload_file,segment_size,clientSocket):
    
    print(payload_file)
    buffSize = segment_size #default 1024

    with open(payload_file,'rb') as f:
      payload_size = len(f.read())
      print(payload_size)
      clientSocket.send( bytes(str(payload_size)+'. .','UTF-8')) 
      f.seek(0) #reset read pointer
      data = f.read(buffSize)
      while data:
        clientSocket.send(data)
        data = f.read(buffSize)
    f.close()

def sendHeader(COMMAND,CIPHER,FILENAME,segment_size,clientSocket):

  buffSize = segment_size
  header = bytes(COMMAND+"\n"+CIPHER+"\n"+FILENAME,"UTF-8")
  clientSocket.send( header )

if __name__ == '__main__':
#  print(str(hashlib.sha256(str_to_bytes("test")).digest()))
#  print(str(Random.new().read(AES.block_size)))
  main()
  startClientNone()
