#!/usr/bin/python3
import socket
import getopt
import sys
import os
import hashlib
import base64
import time
from threading import Thread
from Crypto import Random
from Crypto.Cipher import AES

LISTEN = True
SERVER_HOST = ''
SERVER_PORT = 0
PW = ''

def start():

  # server <PORT> [KEY]
  global SERVER_PORT
  global SERVER_HOST
  global PW
  SERVER_PORT = int(sys.argv[1])
  SERVER_HOST = 'localhost' # server host
  if(len(sys.argv) == 3):
    PW = str(sys.argv[2])
  start_file_server()

def start_file_server():
  server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
  server_sock.bind((SERVER_HOST,SERVER_PORT))
  server_sock.listen(1)
  print("Waiting for client(s) to connect at: "+SERVER_HOST+":"+str(SERVER_PORT))

  while True:
    clientSock, addr = server_sock.accept()
    client_ip = str(addr[0])
    client_port = str(addr[1])
    client_ip,client_port = str(addr[0]),str(addr[1])
    print(client_ip + ':' + client_port + ' has connected')
    Thread(target=client_connect, args=(clientSock,client_ip,client_port)).start()


def client_connect(clientSock,client_ip,client_port):
  IVnonce = b""
  cipher = ''

  while True:
    
    #Get the Cipher type from the client
    first_message = clientSock.recv(1024)   
    if len(first_message) > 0:
      first_message_array = first_message.split(b"\n")
      cipher = (first_message_array[0]).decode('UTF-8')
      IV = clientSock.recv(16)
#      IV =  (first_message_array[1])
      print(len(IV))
      print("cipher: "+cipher)
      print("IV: " +str(IV))

    #No Encryption (1024 byte blocks--default)
    if cipher == "none":
      segment_size = 1024
      noEncryptionMode(segment_size, clientSock,client_ip)

    #AES 128 (16 byte blocks)
    elif cipher == "aes128":
      segment_size = 16
      aes128EncryptionMode(IV, segment_size, clientSock,client_ip)
 
    #AES 256 (16 byte blocks)
    elif cipher == "aes256":
      segment_size = 16
      aes256EncryptionMode(IV, segment_size, clientSock,client_ip)


def noEncryptionMode(segment_size, clientSock, client_ip):

  client_request = clientSock.recv(segment_size)
  if len(client_request) > 0:

    header_array = client_request.split(b"\n")
    command = (header_array[0]).decode(encoding='UTF-8')
    file_name = (header_array[1]).decode(encoding='UTF-8')
    print("Client command: " + command)  # DEBUGGING
    print("Filename: " + file_name)      # DEBUGGING
      
    if command == "write":
      
      print("Attempting to upload file: "+file_name+" to server from: " + client_ip)
      getFileNoEncryption(file_name,segment_size,clientSock)
      
    elif command == "read":

      print("client is in read mode")
      sendFileNoEncryption(file_name,cipher,clientSock)
   
    else:
      print( "command: "+command+ " not a valid command" )

def getFileNoEncryption(file_name,segment_size,clientSock):
  
  buffSize = segment_size
  #get file size header from client, delmited with ". ."
  file_header = clientSock.recv(segment_size)
  header_array = file_header.split(b". .")

  file_size = int(header_array[0]) ##extract the file size from header
  bytes_written = 0
  
  #CREATE THE FILE ON THE SERVER, WILL OVERWRITE IF EXISTS
  with open(file_name,"wb+") as f:
    while(bytes_written < file_size):
      data = clientSock.recv(buffSize)
      if not data:
        break
      if len(data) + bytes_written > file_size:
        data = data[:file_size-bytes_written]
      ##append
      f.write(data)
      bytes_written += len(data)
  f.close()
  print("file: "+file_name+" successfully uploaded to server") 
  
 
def sendFileNoEncryption(file_name,cipher,clientSock):

  print("server is in getFile mode")
  print(file_name)

  buffSize = 1024
  with open(file_name,'rb') as infile:
    
    file_size = len(infile.read())
    clientSock.send( bytes(str(file_size)+'. .','UTF-8')) 
    infile.seek(0)
    print(str(file_size))
    #send header (only sending size right now, will need more in header later for encryption)
    data = infile.read(1024)
    while data:
      clientSock.send(data)
      data = infile.read(1024)
    print("file sent")
    #clientSock.close() 
  infile.close()


def aes128EncryptionMode(IV, segment_size,clientSock,client_ip):
  global PW
  
  key = hashlib.md5(PW.encode()).hexdigest()
  decryptor = AES.new(key,AES.MODE_CBC,IV)
  header = b''
  
  decryptHeader = ''
  while True:
    chunk = clientSock.recv(segment_size)
    if len(chunk) > 0:
      decryptedByteString = decryptor.decrypt(chunk)
      decryptedString = decryptedByteString.decode("UTF-8") #decodes the bytestring segment into a string
#      print(decryptedByteString)
      decryptHeader = decryptHeader + decryptedString
      if (decryptHeader.find(". .") == -1):
        print("No delimiter detected") #DEBUG
      else:
        print("Delimiter detected, removing padding from segment") #debug
        index = decryptHeader.find(". .") 
        decryptHeader = decryptHeader[:index]
        break
  
  #Header has been fully recieved, decrypted, + final padding removed
  header_array = decryptHeader.split("\n")
  print(header_array)    #DEBUG STATMENT
  COMMAND = (header_array[0])#.decode(encoding='UTF-8')
  FILENAME = (header_array[1])#.decode(encoding='UTF-8')

  if COMMAND == "write":
    fileSize = int(header_array[2])
    bytes_written = 0
    with open(FILENAME,"wb+") as f:
      while(True):
        data = clientSock.recv(segment_size)
        if not data:
          break
        decryptedDataString = decryptor.decrypt(data)
#        decryptedString = decryptedByteString.decode("utf-8")
        bytes_written += len(data)
        if(bytes_written > fileSize):
          decryptedDataString = decryptedDataString[:fileSize % 16]
        f.write(decryptedDataString)
    f.close() 
  elif COMMAND == "read":
    sendFileAes128(FILENAME,clientSock)

def aes256EncryptionMode(IV, segment_size,clientSock,client_ip):
  global PW
  
  key = hashlib.sha256(PW.encode()).digest()
  decryptor = AES.new(key,AES.MODE_CBC,IV)
  header = b''
  
  decryptHeader = ''
  while True:
    chunk = clientSock.recv(segment_size)
    if len(chunk) > 0:
      decryptedByteString = decryptor.decrypt(chunk)
      decryptedString = decryptedByteString.decode("UTF-8") #decodes the bytestring segment into a string
#      print(decryptedByteString)
      decryptHeader = decryptHeader + decryptedString
      if (decryptHeader.find(". .") == -1):
        print("No delimiter detected") #DEBUG
      else:
        print("Delimiter detected, removing padding from segment") #debug
        index = decryptHeader.find(". .") 
        decryptHeader = decryptHeader[:index]
        break
  
  #Header has been fully recieved, decrypted, + final padding removed
  header_array = decryptHeader.split("\n")
  print(header_array)    #DEBUG STATMENT
  COMMAND = (header_array[0])#.decode(encoding='UTF-8')
  FILENAME = (header_array[1])#.decode(encoding='UTF-8')

  if COMMAND == "write":
    fileSize = int(header_array[2])
    bytes_written = 0
    with open(FILENAME,"wb+") as f:
      while(True):
        data = clientSock.recv(segment_size)
        if not data:
          break
        decryptedDataString = decryptor.decrypt(data)
#        decryptedString = decryptedByteString.decode("utf-8")
        bytes_written += len(data)
        if(bytes_written > fileSize):
          decryptedDataString = decryptedDataString[:fileSize % 16]
        f.write(decryptedDataString)
    f.close() 
  elif COMMAND == "read":
    sendFileAes128(FILENAME,clientSock)

def getFileAes128(FILENAME,fileSize,clientSock):

  key = hashlib.sha256(PW.encode()).hexdigest()
  decryptor = AES.new(key,AES.MODE_CBC,IV)
  data = b''
  bytes_written = 0  

  with open(FILENAME,"wb+") as f:
    while(bytes_written < fileSize):
      data = clientSock.recv(segment_size)
      if not data:
        break
      if len(data) + bytes_written > fileSize:
        data = data[:fileSize-bytes_written]
        decryptedDataString = decryptor.decrypt(data)
        decryptedString = decryptedByteString.decode("utf-8")

        if ( (decryptedString.find(". .")) != -1):
          print("No delimiter detected") #DEBUG
          f.write(decryptedByteString)
          bytes_written += len(data)
        else:
          print("Delimiter detected, removing padding from segment") #debug
          f.write(decryptedString)  ## NEED TO REMOVE PADDING
          #ALSO need to remove delimiter if it's present??
          bytes_written += len(data)
  f.close() 

def sendFileAes128(FILENAME,clientSock):
  print("sendFileAes128 not implemented")



if __name__ == "__main__":
  start()





