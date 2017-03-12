#!/usr/bin/python3
import base64
import hashlib
import sys
import time
import socket
import os
import struct
from Crypto import Random
from Crypto.Cipher import AES

COMMAND = ''
FILENAME = ''
DEST = ''
CIPHER = ''
KEY = ''
PW = ''
IV = ''

def main():
  global COMMAND
  global FILENAME
  global DEST
  global CIPHER
  global KEY 
  global PW
  global IV
#  print(hashlib.sha256(str_to_bytes("test")).hexdigest())  # This gives a 32-byte key value
#  print(hashlib.md5("test".encode()).hexdigest()) # This gives a 16-byte key value
#  rand = os.urandom(32)
#  print(hashlib.md5(rand).hexdigest()) # Randomly generate 16-byte key
#  print(os.urandom(32)) # Randomly generate 32-byte key 
#  print(Random.new().read(AES.block_size))

  IV = Random.new().read(AES.block_size)  # This generates a random IV

  if (len(sys.argv) < 4):
    print("Use this application with the following:")
    print("python3 client.py [read/write] filename hostname:port [none|aes128|aes256] key")
    print("You must use at least four of the above arguments, in the specified order")
    sys.exit("Incorrect user input")

  if (sys.argv[4]=='none'):
    COMMAND = str(sys.argv[1])
    FILENAME = str(sys.argv[2])
    DEST = str(sys.argv[3])
    CIPHER = 'none'

  else:
    if(len(sys.argv)==6):
      COMMAND = str(sys.argv[1])
      FILENAME = str(sys.argv[2])
      DEST = str(sys.argv[3])
      CIPHER = str(sys.argv[4])
      PW = str(sys.argv[5])
      print("Password: " + PW)

    elif(len(sys.argv)==4):
      COMMAND = str(sys.argv[1])
      FILENAME = str(sys.argv[2])
      DEST = str(argv[3])
      CIPHER = 'none'
  print("test2")
  # The following code block is used to parse the user input and execute the appropriate functions
  if(COMMAND=="read"):
    if(CIPHER=="none"):
       startClientNone()
    elif(CIPHER=="aes128") or (CIPHER=="aes256"):
       print("not yet implemented")
    else:
      sys.exit("Unsupported Cryptography Cipher")
  elif(COMMAND=="write"):
    if(CIPHER=="none"):
       startClientNone()
    elif(CIPHER=="aes128") or (CIPHER=="aes256"):
      separator = DEST.find(":")
      ipDEST = DEST[0:separator]
      sockDEST = DEST[separator+1:]
      clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      clientSocket.connect((ipDEST,int(sockDEST)))

      sendFileEncryption(COMMAND, FILENAME, CIPHER, PW, 16, clientSocket)
    else:
      sys.exit("Unsupported Cryptography Cipher")


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

  if(COMMAND=="read"):

    ### THIS IS BROKEN HEERE, NEED TO UPDATE THE CODE TO BE SIMILAR TO
    ### WRITE MODE!
    ## NEED TO SEND WELCOME MESSAGE TO SEVER IN PROPER FORMAT LIKE WRITE MODE

    segment_size = 1024 
    header = sendHeaderNoEncrypt(COMMAND,FILENAME,clientSocket)

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
    
    print("Client is in write mode")
    ##Move data into temp_data file (incase of large files)
    payload_file = "temp_data"
    with open(payload_file,'wb+') as f:
    
      while True: 
        data = sys.stdin.buffer.read(1)
        if not data:
          break
        f.write(data) 
    f.close()

    # Send first communication to server ( first message = CIPHER + IV (nonce) + padding)
    # first communication is always 1024 bytes transmission (NO ENCRYPTION HERE)
    iv = "randomNonce"
    first_message = CIPHER + "\n" + iv + "\n"
    first_message_length = len(first_message)
    padding = 1024 - first_message_length
    padding_arg1 = str(padding)+"B"
    # i.e. input_chunk + struct.pack('50B',*([0]*50)) --> appends 50 bytes of 0 padding
    padded_message = bytes(first_message,'UTF-8') + struct.pack(padding_arg1,*([0]*padding))
    clientSocket.send(padded_message)
    print("Hi server --> sending cipher + IV(nonce) + padding: "+ str(len(padded_message))+" bytes")

    if CIPHER == "none":
      
      #Now send the header + payload in the clear
      segment_size = 1024 
      sendFileNoEncryption(payload_file,segment_size,clientSocket)

    elif CIPHER == "aes128":
      segment_size = 16

    elif CIPHER == "aes256":
      segment_size = 16
    
  else:
    print("I don't know how to " + COMMAND)
      
def sendFileNoEncryption(payload_file,segment_size,clientSocket):
  global COMMAND
  global DEST
  global FILENAME
 
  #Send header before payload
  sendHeaderNoEncrypt(COMMAND,FILENAME,clientSocket)
    
  with open(payload_file,'rb') as f:
    
    # Get payload size, and send to server so it knows how much data to recieve
    payload_size = len(f.read())
    print("Client sending file of size: " + str(payload_size) + " bytes")  ## TEST
    clientSocket.send( bytes(str(payload_size)+'. .','UTF-8'))

    #reset read pointer on payload file, and send file 1024 bytes at a time
    f.seek(0) 
    data = f.read(segment_size)
    while data:
      clientSocket.send(data)
      data = f.read(segment_size)
    f.close()

def sendHeaderNoEncrypt(COMMAND,FILENAME,clientSocket):

  header = bytes(COMMAND+"\n"+FILENAME+"\n","UTF-8")
  clientSocket.send( header )

def sendFileEncryption(COMMAND, FILENAME, CIPHER, PW, segment_s, clientSocket):
  global IV
  pad = lambda s: s + (segment_s - len(s) % segment_s) * str_to_bytes(chr(segment_s - len(s) % segment_s)) # This defines a pad function that can be called with pad(string)
  header = bytes(CIPHER + "\n" + IV + "\n","UTF-8")
  padding = 1024 - len(header)
  padded_header = bytes(header,'UTF-8') + struct.pack(str(padding)+"B",*([0]*padding))
#  padded_header = pad(header)
  clientSocket.send(padded_header) # Send crypto header, containing crypto mode and IV
# The following code counts the size of the file it is about to send
  fileize = 0
  tempFile = "temp_dat"
  print("test")
  with open(tempFile,'wb+') as f:
    while(True):
      chunk = sys.stdin.buffer.read(1)
      if not chunk:
        break
      f.write(chunk)
      filesize += 1
    f.close()
    
#  unpad = lambda s : s[0:-ord(s[-1])] # This defines an unpad function that can be called with unpad(decryptedString)
  
  if(CIPHER=="aes128"): # This block reads from stdin in 16 byte segments, encrypts and sends them as they are read
    key = hashlib.md5(PW.encode()).hexdigest() # Generates a 16-byte key from the given password
    encryptor = AES.new(key,AES.MODE_CBC,IV) # The encyptor keeps track of the IV as it changes form chunk to chunk

#    c_checker = "HELLO"
#    pad(c_checker)
#    crypto_checker = 
         
    c_header = COMMAND + "\n" + FILENAME + "\n" + fileSize + ". ."  # The crypto header needs to be filled with the command, filename, and filesize 
    crypt_header = pad(c_header)
    cryto_header = encryptor.encrypt(bytes(crypt_header,"UTF-8"))
    
    with open(tempFile,'rb') as inload:
      while(True):
        chunk = inload.read(segment_s)
        if(len(chunk)==0):
          break
        elif(len(chunk) % 16 != 0):
          chunk += bytes(' ' * (16 - len(chunk) % 16))
        encrypted = encryptor.encrypt(chunk)
        clientSocket.send(encrypted)

  elif(CIPHER=="aes256"): # This block reads from stdin in 16 byte segments, encrypts and sends them as they are read
    key = hashlib.sha256(PW.encode()).hexdigest() # Generates a 32-byte key from the given password
    encryptor = AES.new(key,AES.MODE_CBC,IV) # The encyptor keeps track of the IV as it changes form chunk to chunk
    with open(tempFile,'rb') as inload:
      while(True):
        chunk = inload.read(segment_s)
        if(len(chunk)==0):
          break
        elif(len(chunk) % 16 != 0):
          chunk += bytes(' ' * (16 - len(chunk) % 16))
        encrypted = encryptor.encrypt(chunk)
        clientSocket.send(encrypted)
    
#def recvFileEncryption(COMMAND, FILENAME, CIPHER, PW, segment_s, clientSocket):

if __name__ == '__main__':
#  print(str(hashlib.sha256(str_to_bytes("test")).digest()))
#  print(str(Random.new().read(AES.block_size)))
  main()
#  startClientNone()
