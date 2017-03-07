#!/usr/bin/python3
import socket
import getopt
import sys
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
  #python3 client.py <read> <filename> host:port none
  #cat file1.txt | ./client write f1.txt localhost:9999 none

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
  
  print("welcome to the worlds most reliable file server (99.99% up time)")

  while True:

    client_request = get_data(clientSock)

    if len(client_request) > 0:

        print("data recieved")
        # extract the header by splitting on delimiter
        array = client_request.split(b". .")
        header_bytes = array[0]
        array1 = header_bytes.split(b"\n")
        print(array1[0])
        file_bytes = array[1]
        print(str(header_bytes,'utf-8'))
        print(len(array))
        #print(file_bytes)
        file_name = "gotpic.jpg"
        outFile = open(file_name,"wb")
        outFile.write(file_bytes)
        outFile.close()
        
            
    if not len(client_request):
      clientSock.close()
      break

def get_data(socket):

    buff_size = 4096
    time_out = 5
    ####### BUG found out here, need to convert the data to a 
    ####### byte string by putting b before it.
    ####### convert this later to regular string if need be.
    data_buffer = b''
    socket.settimeout(5)
    try:
        while True:
            data = socket.recv(4096)
            if not data:
                break
            data_buffer += data
    except:
        pass
    return data_buffer

if __name__ == "__main__":
  start()





