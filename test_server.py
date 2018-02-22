# supports 'SYST' command

import socket
import string
import ssl
import platform
import os
from database import Users
from random import randint
import time

from list_check import list_command


PATH = 0
ORIGINAL_DIR = os.getcwd()

USERNAME = 0
PASSWORD = 1
USER = 0
PASS = 1

COMMAND = 0
ARGS = 1
DATA = 1024

PORT_RANGE_MAX = 254
PORT_RANGE_MIN = 192



def syst_command(socket, args):
    ok_code = '215'
    socket.send(ok_code + " " + platform.system() + "\r\n")


def send_error(error_code):
    return error_code + ' \r\n'


def user_check(client ,args):
    request_password = '331 Please specify password\r\n'
    username = args[USERNAME]

    client.send(request_password)
    response = client.recv(DATA)
    if 'PASS' in response:
        password = response.split()[PASSWORD]
        return pass_check(client, password ,username)
    else:
        return send_error('503')
    


def pass_check(client, password, username):
    succesful_login = '230 Login succesful, all clear\r\n'
    wrong_password = '430 Wrong password\r\n'

    users = Users()
    if (username, password) in users.get_users_pass():
        client.send(succesful_login)
    else:
        client.send(wrong_password)


def delete(client ,path_to_file):
    if os.path.isfile(path_to_file):
        os.remove(path_to_file)
        client.send('250 Requested file has been deleted\r\n')
    else:
        client.send(send_error('550'))  # file not found


def pwd(client, args):
    succesful = '257 "%s" is working directory\r\n'
    client.send(succesful % os.getcwd())
    print 'hola'


def cwd(client, args):
    succesful_change = '250 Succesfully changed directory\r\n'

    if len(args) > 0:
        path = ORIGINAL_DIR + args[PATH]
        if ORIGINAL_DIR in path and os.path.exists(path):
            os.chdir(path)
            client.send(succesful_change)
        else:
            client.send(send_error('550'))


def get_features(client, args):
    client.send('211-Features:\r\n')
    feat_list = ['feat'] # 'rest' command to remember
    for feature in feat_list:
        client.send(feature + '\r\n')
    client.send('211 End\r\n')


def set_binary_flag(client, args):
    """
    used by TYPE command to issue which type of data to transfer.
    Binary or non binary.
    """
    global binary_flag
    binary_flag = str(args[0])
    print 'Binary flag now set to: ' + binary_flag

    client.send('200 flag changed to %s\r\n' % str(args[0]))


def passive_port():
	p1 = randint(PORT_RANGE_MIN, PORT_RANGE_MAX)
	p2 = randint(PORT_RANGE_MIN, PORT_RANGE_MAX)

	port = p1 * 256 + p2

	return str(p1), str(p2), port

def passive_connection(client, args):
    """
    Passive connection type: server sends client on which port to send data.
    """
    print 'passive'

    global ip
    ip = '127.0.0.1'
    ip_to_send = ','.join(ip.split('.'))
#    port = randint(2024, 50000)
    global port
    port = passive_port()
    port_to_send = ','.join(port[:2])
    port = port[2]
    try:
        to_send = '227 Entering passive mode (%s,%s)\r\n' % (ip_to_send, port_to_send)
        client.send(to_send)
        return
        

    except socket.error as e:
        print e
        to_send = '421 Falied to enter passive mode\r\n'


    client.send(to_send)


def active_connection(client, args):
	global ip
	global port

	connection = args[0]
	connection = connection.split(',')
	ip = '.'.join(connection[:4])
	print 'ip: ' + ip
	try:
		print connection[4], connection[5]
		port = int(connection[4]) * 256 + int(connection[5])
	except ValueError as e:
		print e
		client.send_error('501')

	client.send('200 Connected\r\n')


# for list
def dir_files(dir):
    currected_files = ''
    files = os.listdir(dir)
    for i in files:
        if '.' in i:
            i = i.split('.')
            currected_files += i[0] + '{.' + i[1] + ' file}\n'
        else:
            currected_files += i + '\n'
    return currected_files


def file_detail(file):
    return_string = ""
    info = ['last accessed: ' + time.asctime(time.localtime(os.path.getatime(file))),
            'last metadata change: ' + time.asctime(time.localtime(os.path.getctime(file))),
            'last modified: ' + time.asctime(time.localtime(os.path.getmtime(file))),
            'file size: ' + time.asctime(time.localtime(os.path.getsize(file)))]
    for i in info:
        return_string += i + '\n'
    return return_string


def get_list(args):
    if os.path.isdir(args):
        d =  dir_files(args)
        print [d]
        return d
    if os.path.isfile(args):
        d = file_detail(args)
        print d
        return d
# end of for list


def list_command(client, args):
    file_list = 'FTP Data (%s' % get_list(os.getcwd())
#    file_list = 'FTP Data (-rw-r--r--    1 0        0        1073741824000 Feb 19  2016 1000GB.zip\r\n-rw-r--r--    1 0        0        107374182400 Feb 19  2016 100GB.zip\r\n-rw-r--r--    1 0        0          102400 Feb 19  2016 100KB.zip\r\n-rw-r--r--  '
    global ip
    global port
    print str(ip)+ ', '+ str(port)
    transfer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transfer_socket.bind((ip, port))
    transfer_socket.listen(1)
    print 'check 2'
    transfer_client, transfer_address = transfer_socket.accept()
    print 'check 3'

    client.send('150 here comes directory listing\r\n')
    print file_list
    transfer_client.send(file_list)
    transfer_client.close()

    print 'check 1'
    client.send('226 Directory send OK.\r\n')

KNOWN_COMMANDS = {'USER': user_check, 'FEAT': get_features, 'SYST': syst_command, 'CWD': cwd, 'PWD': pwd, 'DELE': delete, 'TYPE': set_binary_flag
                ,'PASV': passive_connection, 'LIST': list_command, 'PORT': active_connection}


def main_loop(client):
    done = False
    request = client.recv(DATA).replace('\r\n', '')
    while not done:
        print 'request = ' + request
        # get command and args
        if len(request.split()) > 1:
            command = request.split()[COMMAND]
            args = request.split()[ARGS::]
        # if command doesn't have arguments
        else:
            command = request
            args = []
        # if in known commands, run it
        try:
            KNOWN_COMMANDS[command](client, args)
        # else send unknown command
        except Exception as e:
            print 'CommandERROR: ' + str(e)
            client.send(send_error('500'))

        # continue loop
        request = client.recv(DATA).replace('\r\n', '')

def main_loop_Test(client):
    done = False
    request = client.recv(DATA).replace('\r\n', '')
    while not done:
        print 'request = ' + request
        # get command and args
        if len(request.split()) > 1:
            command = request.split()[COMMAND]
            args = request.split()[ARGS::]
        # if command doesn't have arguments
        else:
            command = request
            args = []
        # if in known commands, run it
        if command != 'AUTH':
        	KNOWN_COMMANDS[command](client, args)
    	else:
    	# else send unknown command
        	client.send(send_error('500'))
    	# continue loop
    	request = client.recv(DATA).replace('\r\n', '')

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    p = int(raw_input("-->"))
    s.bind(("127.0.0.1", p))
    s.listen(1)
    client, address = s.accept()
    client.send('220 welcome\r\n')
    main_loop_Test(client)
    s.close()



if __name__ == '__main__':
    main()