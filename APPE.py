#not tested, test when uploading file

import os
import socket
ip = '127.0.0.1'
port = '3111'
def appe_command(client, args):
	global ip 
	global port
    fileName = args[0]
    filpath = r'c:\\Users\User\Desktop\FTP-Server-master\files' + fileName
    if os.path.isfile(filpath):
    	with open(filpath, 'ab') as upload_file:
    		data_socket = socket.socket()
    		data_socket.bind(ip, port)
    		data_socket.listen(1)
    		try:
    			data_client, data_address = data_socket.accept()

    		except Exeption as E:
    			client.send('500' + str(E) + '\r\n' )
    		appendex = data_client.recv(1024)
    		upload_file.write(appendex)
    else:
    	with open(filpath, 'wb') as upload_file:
    		data_socket = socket.socket()
    		data_socket.bind(ip, port)
    		data_socket.listen(1)
    		try:
    			data_client, data_address = data_socket.accept()

    		except Exeption as E:
    			client.send('500' + str(E) + '\r\n' )
    		data = data_client.recv(1024)
    		upload_file.write(data)




