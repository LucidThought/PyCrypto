#!/usr/bin/python3
import socket
import getopt
import sys
import os
import hashlib
import base64
import time
import logging
import random
import string
import struct
from threading import Thread
from Crypto import Random
from Crypto.Cipher import AES

LISTEN = True
SERVER_HOST = ''
SERVER_PORT = 0
PW = ''
logging.basicConfig(level=logging.INFO, format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s', filename='server_log.txt', filemode='a')
logging.info("Crypto File Transfer Server Log")
logger = logging.getLogger("serverLog")


def start():

  # server <PORT> [KEY]
  global SERVER_PORT
  global SERVER_HOST
  global PW
  global module_logger
  SERVER_PORT = int(sys.argv[1])
  SERVER_HOST = 'localhost' # server host
  if(len(sys.argv) == 3):
    PW = str(sys.argv[2])
  if(len(sys.argv) == 2):
    PW = randomString(10)
  print("Using secret key: " + PW)
  start_file_server()

def randomString(length):
  return ''.join([random.choice(string.ascii_lowercase + string.digits) for n in range(16)])

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
    logStr = client_ip + ':' + client_port + ' has connected'
    print(logStr)
    logging.info(logStr)
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
      logging.info(client_ip + " has entered AES-128 mode")
 
    #AES 256 (16 byte blocks)
    elif cipher == "aes256":
      segment_size = 16
      aes256EncryptionMode(IV, segment_size, clientSock,client_ip)
      logging.info(client_ip + " has entered AES-256 mode")


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
      logging.info(client_ip + " is uploading a file without encryption")
      getFileNoEncryption(file_name,segment_size,clientSock)
    elif command == "read":
      logging.info(client_ip + " is requesting a file without encryption")
      sendFileNoEncryption(file_name,clientSock)
    else:
      print( "command: "+command+ " not a valid command" )

def getFileNoEncryption(file_name,segment_size,clientSock):

  buffSize = segment_size
  file_header = clientSock.recv(segment_size)
  header_array = file_header.split(b". .")
  file_size = int(header_array[0])
  bytes_written = 0
  print(file_size)
  
  #CREATE THE FILE ON THE SERVER, WILL OVERWRITE IF EXISTS
  with open(file_name,"wb+") as f:
    while(True):
      data = clientSock.recv(buffSize)
      if not data:
        break
      bytes_written += len(data)
      if(bytes_written > file_size):
        data = data[:file_size % segment_size]
      f.write(data)
  f.close()
  print("file: "+file_name+" successfully uploaded to server") 
  logging.info(file_name + " has been uploaded to the server")
  
 
def sendFileNoEncryption(file_name,clientSock):

  buffSize = 1024
  try:
    payload_size = os.path.getsize(file_name)
  except:
    print("Requested file does not exist")
    logging.info("Requested file does not exist")

  print("debug-->Server sending file of size:"+str(payload_size))
  filesize_message = str(payload_size) + ". ."
  message_size = len(filesize_message)
  padding = 1024 - message_size
  padding_arg1 = str(padding)+"B"
  padded_filesize_message = bytes(filesize_message,'UTF-8') + struct.pack(padding_arg1,*([0]*padding))
  clientSock.send( padded_filesize_message)

  print(buffSize)
  with open(file_name,'rb') as infile:
    chunk = infile.read(1024)
    while(chunk):
      if(len(chunk) % buffSize !=0):
        dchunk = b'\x00' * (buffSize - len(chunk) % buffSize)
        chunk = b"".join([chunk,dchunk])
      clientSock.send(chunk)
      chunk = infile.read(buffSize)
  logging.info(file_name + " has been sent from the server")
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
      decryptHeader = decryptHeader + decryptedString
      if (decryptHeader.find(". .") != -1):
        logging.info("Received encrypted header from " + client_ip + " in AES-128 mode")
        index = decryptHeader.find(". .") 
        decryptHeader = decryptHeader[:index]
        break
  
  #Header has been fully recieved, decrypted, + final padding removed
  header_array = decryptHeader.split("\n")
  print(header_array)    #DEBUG STATMENT
  COMMAND = (header_array[0])
  FILENAME = (header_array[1])

  if COMMAND == "write":
    logging.info("Receiving file " + FILENAME + " from " + client_ip + " in AES-128 mode")
    fileSize = int(header_array[2])
    bytes_written = 0
    with open(FILENAME,"wb+") as f:
      while(True):
        data = clientSock.recv(segment_size)
        if not data:
          break
        decryptedDataString = decryptor.decrypt(data)
        bytes_written += len(data)
        if(bytes_written > fileSize):
          decryptedDataString = decryptedDataString[:fileSize % segment_size]
        f.write(decryptedDataString)
    f.close() 
  elif COMMAND == "read":
    sendFileAes128(key, IV, segment_size, FILENAME, clientSock, client_ip)

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
      decryptHeader = decryptHeader + decryptedString
      if (decryptHeader.find(". .") != -1):
        logging.info("Received encrypted header from " + client_ip + " in AES-256 mode")
        index = decryptHeader.find(". .") 
        decryptHeader = decryptHeader[:index]
        break
  
  #Header has been fully recieved, decrypted, + final padding removed
  header_array = decryptHeader.split("\n")
  print(header_array)    #DEBUG STATMENT
  COMMAND = (header_array[0])
  FILENAME = (header_array[1])

  if COMMAND == "write":
    logging.info("Receiving file " + FILENAME + " from " + client_ip + " in AES-256 mode")
    fileSize = int(header_array[2])
    bytes_written = 0
    with open(FILENAME,"wb+") as f:
      while(True):
        data = clientSock.recv(segment_size)
        if not data:
          break
        decryptedDataString = decryptor.decrypt(data)
        bytes_written += len(data)
        if(bytes_written > fileSize):
          decryptedDataString = decryptedDataString[:fileSize % segment_size]
        f.write(decryptedDataString)
    f.close() 
  elif COMMAND == "read":
    sendFileAes256(key, IV, segment_size, FILENAME,clientSock, client_ip) 

def sendFileAes128(key, IV, segment_size, FILENAME, clientSock, ip):
  global PW
  pad = lambda s: s + (segment_size - len(s) % segment_size) * chr(segment_size - len(s) % segment_size) # This defines a pad function that can be called with pad(string)
  encryptor = AES.new(key,AES.MODE_CBC,IV)
  decryptor = AES.new(key,AES.MODE_CBC,IV)
  verify = "True"
  try:
    file_size = os.path.getsize(FILENAME)
  except:
    print("Requested file does not exist")
    logging.info("Requested file does not exist")
    verify = "False"
  c_header = verify + "\n"  + str(file_size) + ". ."  # The crypto header needs to be filled with the command, filename, and filesize 
  crypt_header = pad(c_header)
  crypto_header = encryptor.encrypt(crypt_header.encode("UTF-8"))
  clientSock.send(crypto_header)

  with open(FILENAME,'rb') as rfile:
    logging.info("Sending file " + FILENAME + " to " + ip + " in AES-128 mode")
    chunk = rfile.read(segment_size)
    while(chunk):
      if(len(chunk) % segment_size != 0):
        dchunk = b'\x00' * (segment_size - len(chunk) % segment_size)
        chunk = b"".join([chunk,dchunk])
      oChunk = encryptor.encrypt(chunk)
      clientSock.send(oChunk)
      chunk = rfile.read(segment_size)
  rfile.close()

def sendFileAes256(key, IV, segment_size, FILENAME, clientSock, ip):
  global PW
  pad = lambda s: s + (segment_size - len(s) % segment_size) * chr(segment_size - len(s) % segment_size) # This defines a pad function that can be called with pad(string)
  encryptor = AES.new(key,AES.MODE_CBC,IV)
  decryptor = AES.new(key,AES.MODE_CBC,IV)
  verify = "True"
  try:
    file_size = os.path.getsize(FILENAME)
  except:
    print("Requested file does not exist")
    logging.info("Requested file does not exist")
    verify = "False"
  c_header = verify + "\n"  + str(file_size) + ". ."  # The crypto header needs to be filled with the command, filename, and filesize 
  crypt_header = pad(c_header)
  crypto_header = encryptor.encrypt(crypt_header.encode("UTF-8"))
  clientSock.send(crypto_header)

  with open(FILENAME,'rb') as rfile:
    logging.info("Sending file " + FILENAME + " to " + ip + " in AES-256 mode")
    chunk = rfile.read(segment_size)
    while(chunk):
      if(len(chunk) % segment_size != 0):
        dchunk = b'\x00' * (segment_size - len(chunk) % segment_size)
        chunk = b"".join([chunk,dchunk])
      oChunk = encryptor.encrypt(chunk)
      clientSock.send(oChunk)
      chunk = rfile.read(segment_size)
  rfile.close()

if __name__ == "__main__":
  start()





