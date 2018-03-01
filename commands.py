# -*- coding: utf-8 -*-
import socket
import platform
import os
from database import Users
from random import randint
import time


FILE_DIR = 'Files'
PATH = 0
ORIGINAL_DIR = os.getcwd() + '\\%s' % FILE_DIR
# user access
USERNAME = 0
PASSWORD = 1
USER = 0
PASS = 1
# request parsing
COMMAND = 0
ARGS = 1
DATA = 1024
# port selecting
PORT_RANGE_MAX = 254
PORT_RANGE_MIN = 192

BYTES_TO_READ = 8

#USERS = Users().get_users_pass()

#IP = socket.gethostbyname(socket.gethostname()) doesn't work because of local network, gives wrong ip address
#IP = '192.168.3.46'
IP = 'localhost'


def rename(client, args):
    """
    """
    #args[0] = file name to change from
    wait = "waiting on file new name ('args[0] + ')\r\n"
    if os.path.isfile(args[0]):
        print wait
        client.send('350' + wait)
        name = client.recv(1024)
        if name.split()[0] == 'RNTO':
            new_name = name.split()[1]
            os.rename(args[0], new_name)
        else:
            client.send(send_error('500 Not recieved file\'s new name'))
            print 'Error recieving new name'
            return
    else:
        client.send(send_error('500 Not a file'))
        print 'No such file exists'
        return


def help_command(client, args):
    """
    HELP FTP command:
    """
    global KNOWN_COMMANDS
    a = "supported commands: \n"
    for i in KNOWN_COMMANDS.keys():
        a += i + '\n'
    client.send('211' + a + '\r\n')


def syst_command(client, args):
    """
    SYST FTP command:
    send to client system name
    """
    ok_code = '215'
    client.send(ok_code + " " + platform.system() + "\r\n")


def send_error(error_code):
    return error_code + ' \r\n'


def user_check(client, args):
    """
    USER FTP command:
    Get username and password of client to check
    in pass.
    """
    request_password = '331 Please specify password\r\n'
    username = args[USERNAME]

    client.send(request_password)
    response = client.recv(DATA)
    if 'PASS' in response:
        password = response.split()[PASSWORD]
        return pass_check(client, password, username)
    else:
        return send_error('503')


def pass_check(client, password, username):
    """
    PASS FTP command:
    Check username and password of client
    """
    succesful_login = '230 Login succesful, all clear\r\n'
    wrong_password = '430 Wrong password\r\n'

    users = Users(ORIGINAL_DIR.replace('\\%s' % FILE_DIR, ''))
    user_data = users.get_users_pass()
    if (username, password) in user_data:
        client.send(succesful_login)
        print 'Client logged in with user: %s pass: %s' % (username, password)
    else:
        client.send(wrong_password)


def delete(client, args):
    """
    DELE FTP command:
    Delete file on server
    """
    path_to_file = ' '.join(args[0::])
    if os.path.isfile(path_to_file):
        os.remove(path_to_file)
        client.send('250 Requested file has been deleted\r\n')
    else:
        client.send(send_error('550'))  # file not found


def pwd(client, args):
    """
    PWD FTP command:
    Send to client the path
    of the working directory
    """
    succesful = '257 "%s" is working directory\r\n'
    current_dir = os.getcwd()
    if FILE_DIR not in current_dir:
        client.send(succesful % ORIGINAL_DIR)
    else:
        client.send(succesful % (os.getcwd()))


def cwd(client, args):
    """
    CWD FTP command:
    Change working directory.
    """
    succesful_change = '250 Succesfully changed directory\r\n'
    full_args = ' '.join(args[PATH:])
    # get path from args
    if len(args) > 0:
        if ORIGINAL_DIR not in full_args:
            path = ORIGINAL_DIR + '\\' + ' '.join(args[PATH:])
        else:
            path = full_args
    else:
        path = '\\'.join(os.getcwd().split('\\')[:-1])

    # change directory
    if os.path.exists(path) and FILE_DIR in path:
        os.chdir(path)
        client.send(succesful_change)
    else:
        client.send(send_error('550'))


def get_features(client, args):
    """
    FEAT FTP command
    send to client list of
    extra features of the server
    """
    client.send('211-Features:\r\n')
    feat_list = ['feat']  # 'rest' command to remember
    for feature in feat_list:
        client.send(feature + '\r\n')
    client.send('211 End\r\n')


def set_binary_flag(client, args):
    """
    TYPE FTP command:
    issue which type of data to transfer.
    Binary or non binary.
    """
    global binary_flag
    binary_flag = str(args[0])
    if binary_flag == 'I':
        binary_flag = 'b'
    else:
        binary_flag = ''

    client.send('200 flag changed\r\n')


def passive_port():
    """
    Return port for passive connection
    """
    p1 = randint(PORT_RANGE_MIN, PORT_RANGE_MAX)
    p2 = randint(PORT_RANGE_MIN, PORT_RANGE_MAX)

    port_to_send = p1 * 256 + p2

    return str(p1), str(p2), port_to_send


def passive_connection(client, args):
    """
    PASV FTP command:
    server sends client on
    which port to send data.
    """
    global ip
    ip = IP
    ip_to_send = ','.join(ip.split('.'))
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
    """
    PORT FTP command:
    gets data connection
    ip and port from client
    """
    global ip
    global port
    global connection_type

    connection = args[0]
    connection = connection.split(',')
    ip = '.'.join(connection[:4])
    try:
        port = int(connection[4]) * 256 + int(connection[5])
        connection_type = 'Active'
        client.send('200 Connected\r\n')
    except ValueError as e:
        print e
        client.send_error('501')


# for list
def dir_files(directory):
    """
    Return list of files in
    directory with their properties
    """
    corrected_files = ''
    tab = '		'
    space = ' '
    file_add = '-rw-r--r-- 1 owner group'
    dir_add = 'drwxr-xr-x 1 owner group'

    files = os.listdir(directory)
    for i in files:
        if os.path.isfile(directory + '\\' + i):
            full_path = directory + '\\' + i
            corrected_files += file_add + tab + str(os.path.getsize(full_path)) + space + \
                str(time.strftime('%b %d %H:%M', time.localtime(os.path.getctime(full_path)))) + space + i + '\r\n'
        if os.path.isdir(directory + '\\' + i):
            full_path = directory + '\\' + i
            corrected_files += dir_add + tab + str(os.path.getsize(full_path)) + space + \
                str(time.strftime('%b %d %H:%M', time.localtime(os.path.getctime(full_path)))) + space + i + '\r\n'
    return corrected_files


def list_command(client, args):
    """
    LIST FTP command:
    Send to client list
    of files in current directory
    """
    global ip
    global port
    global connection_type
    if FILE_DIR in os.getcwd():
        file_list = dir_files(os.getcwd())
    else:
        file_list = dir_files(os.getcwd() + '\\%s' % FILE_DIR)

    transfer_client, transfer_socket = transfer_connection()
    # else:
    #     client.send('425 Data connection failed to open\r\n')

    client.send('150 here comes directory listing\r\n')
    transfer_client.send(file_list)
    transfer_client.close()

    client.send('226 Directory send OK.\r\n')


def transfer_connection():
    """
    Return client to use according
    to connection type. Active or passive
    """
    global connection_type
    transfer_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if connection_type == 'Passive':
        transfer_server.bind((ip, port))
        transfer_server.listen(1)
        transfer_client, transfer_address = transfer_server.accept()
        return transfer_client, transfer_server
    elif connection_type == 'Active':
        transfer_server.connect((ip, port))
        return transfer_server, None


def retrieve_file(client, args, last_file_position=0):
    """
    RETR FTP command:
    send file from server to client
    """
    global ip
    global port
    global binary_flag

    path = ' '.join(args[PATH:])
    if os.path.isfile(path):
        client.send('150 opening data connection\r\n')
        transfer_client, transfer_server = transfer_connection()
        # send data
        with open(path, 'r' + binary_flag) as my_file:
            if last_file_position:
                my_file.seek(last_file_position)
            while True:
                contents = my_file.read(BYTES_TO_READ)
                if not contents:
                    break
                transfer_client.send(contents)
        # close connections
        transfer_client.close()
        try:
            transfer_server.close()
        except AttributeError:
            pass
        last_file_position = 0
        client.send('226 Transfer complete.\r\n')
    else:
        client.send('550 File does not exist\r\n')


def reset_transfer(client, args):
    try:
        last_file_pos = int(args[0])
    except ValueError:
        client.send('501 Error in arguments\r\n')
        return
    client.send('350 File pos saved\r\n')
    request = client.recv(1024)

    retrieve_file(client, request.split()[ARGS:], last_file_pos)


def return_size(client, args):
    """
    SIZE FTP command:
    send to client size of argument file
    """
    path = ' '.join(args)
    client.send('213 %s\r\n' % str(os.path.getsize(path)))


# end of for list\
KNOWN_COMMANDS = {'USER': user_check,
                  'FEAT': get_features,
                  'SYST': syst_command,
                  'CWD': cwd,
                  'PWD': pwd,
                  'DELE': delete,
                  'TYPE': set_binary_flag,
                  'PASV': passive_connection,
                  'LIST': list_command,
                  'PORT': active_connection,
                  'HELP': help_command,
                  'RETR': retrieve_file,
                  'CDUP': cwd,
                  'SIZE': return_size,
                  'REST': reset_transfer}


def main():
    """
    Add Documentation here
    """
    pass  # Replace Pass with Your Code


if __name__ == '__main__':
    main()