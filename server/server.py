#!/usr/bin/python3
import socket
import getopt
import sys
import os
from threading import Thread

LISTEN = True
SERVER_HOST = ''
SERVER_PORT = 0

def start():

  # server <PORT> [KEY]
  global SERVER_PORT
  global SERVER_HOST
  SERVER_PORT = int(sys.argv[1])
  SERVER_HOST = 'localhost' # server host
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
  
  while True:
    
    client_request = clientSock.recv(1024)
    if len(client_request) > 0:
       
      #Split incoming header on delimiter ("\n"), creates an array of values
      header_array = client_request.split(b"\n")
      print(header_array)
      #Extract those values into appropriate variables		
      command = (header_array[0]).decode(encoding='UTF-8')
      file_name = (header_array[1]).decode(encoding='UTF-8')
      cipher = (header_array[2]).decode(encoding='UTF-8')     
      
      # DEBUGGING
      print(command)
      print(file_name)
      print(cipher) 
      
      if command == "write":
        recieveFileMode(file_name,cipher,clientSock)
        print(file_name+" uploaded to server from: " + client_ip)
        message = "uploading file to server: " + file_name
      
      # client wants to download a specified file
      elif command == "read":

        sendFileMode(file_name,cipher,clientSock)
   
      else:
        print( "command: "+command+ " not a valid command" )

    # No more data to recieve, close the client socket
    if not len(client_request):
      clientSock.close()
      break

def recieveFileMode(file_name,cipher,clientSock):

  segment_size = 1024

  if cipher == "none":
    getFile(file_name,segment_size,clientSock)
  if cipher == "aes-128":
    print("aes-128 not implemented")
  if cipher == "aes-256":
    print("aes-256 not implemented")

  

def getFile(file_name,segment_size,clientSock):
  
  buffSize = segment_size  # default 1024
  #get file size header from client, delmited with ". ."
  file_header = clientSock.recv(segment_size)
  print("getting here")
  header_array = file_header.split(b". .")

  ##print(header_array[0]) TEST
  file_size = int(header_array[0]) ##extract the file size from header
  ##print(file_size) TEST
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
  print("file: "+file_name+" saved to server") 
  
 
def sendFileMode(file_name,cipher,clientSock):

  print("server is in download mode")
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

if __name__ == "__main__":
  start()





