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

#IP = socket.gethostbyname(socket.gethostname())  # doesn't work because of local network, gives wrong ip address
#IP = '192.168.1.17'
#IP = 'localhost'


def send_error(error_code):
    return error_code + ' \r\n'


def passive_port():
    """
    Return port for passive connection
    """
    p1 = randint(PORT_RANGE_MIN, PORT_RANGE_MAX)
    p2 = randint(PORT_RANGE_MIN, PORT_RANGE_MAX)

    port_to_send = p1 * 256 + p2

    return str(p1), str(p2), port_to_send


# for list
def dir_files(directory):
    """
    Return list of files in
    directory with their properties
    """
    corrected_files = ''
    tab = '     '
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


class Commands(object):
    """
    Handler of commands for the ftp server
    """
    def __init__(self, my_ip):
        self.binary_flag = ''
        self.connection_type = ''
        self.ip = my_ip  # ip to send to client when transferring data
        self.port = 0  # port to send
        self.last_file_position = 0
        users = Users(ORIGINAL_DIR.replace('\\%s' % FILE_DIR, ''))
        self.user_data = users.get_users_pass()
        self.command_dict = {'USER': self.user_check,
                             'FEAT': self.get_features,
                             'SYST': self.syst_command,
                             'CWD': self.cwd,
                             'PWD': self.pwd,
                             'DELE': self.delete,
                             'TYPE': self.set_binary_flag,
                             'PASV': self.passive_connection,
                             'LIST': self.list_command,
                             'PORT': self.active_connection,
                             'HELP': self.help_command,
                             'RETR': self.retrieve_file,
                             'CDUP': self.cwd,
                             'SIZE': self.return_size,
                             'REST': self.reset_transfer,
                             'STOR': self.store_something}

    @staticmethod
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

    def help_command(self, client, args):
        """
        HELP FTP command:
        """
        a = "supported commands: \n"
        for i in self.command_dict.keys():
            a += i + '\n'
        client.send('211' + a + '\r\n')

    @staticmethod
    def syst_command(client, args):
        """
        SYST FTP command:
        send to client system name
        """
        ok_code = '215'
        client.send(ok_code + " " + platform.system() + "\r\n")

    def user_check(self, client, args):  # user check
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
            return self.pass_check(client, password, username)
        else:
            return client.send('503 Commands sent in wrong order\r\n')

    def pass_check(self, client, password, username):
        """
        PASS FTP command:
        Check username and password of client
        """
        succesful_login = '230 Login succesful, all clear\r\n'
        wrong_password = '430 Wrong password\r\n'

        if (username, password) in self.user_data:
            client.send(succesful_login)
            print 'Client logged in with user: %s pass: %s' % (username, password)
        else:
            client.send(wrong_password)

    @staticmethod
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
            client.send('550 File not found\r\n')

    @staticmethod
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

    @staticmethod
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
            client.send('550 Directory does not exist\r\n')

    @staticmethod
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

    def set_binary_flag(self, client, args):
        """
        TYPE FTP command:
        issue which type of data to transfer.
        Binary or non binary.
        """
        self.binary_flag = str(args[0])
        if self.binary_flag == 'I':
            self.binary_flag = 'b'
        else:
            self.binary_flag = ''

        client.send('200 flag changed\r\n')

    def passive_connection(self, client, args):
        """
        PASV FTP command:
        server sends client on
        which port to send data.
        """
        ip_to_send = ','.join(self.ip.split('.'))
        self.port = passive_port()
        port_to_send = ','.join(self.port[:2])
        self.port = self.port[2]
        try:
            to_send = '227 Entering passive mode (%s,%s)\r\n' % (ip_to_send, port_to_send)
            client.send(to_send)
            self.connection_type = 'Passive'
            return
        except socket.error as e:
            print e
            to_send = '421 Falied to enter passive mode\r\n'

        client.send(to_send)

    def active_connection(self, client, args):
        """
        PORT FTP command:
        gets data connection
        ip and port from client
        """
        connection = args[0]
        connection = connection.split(',')
        self.ip = '.'.join(connection[:4])
        try:
            self.port = int(connection[4]) * 256 + int(connection[5])
            self.connection_type = 'Active'
            client.send('200 Connected\r\n')
        except ValueError as e:
            print e
            client.send('501 Could not establish data connection\r\n')

    def list_command(self, client, args):
        """
        LIST FTP command:
        Send to client list
  self.      of files in current directory
        """
        if FILE_DIR in os.getcwd():
            file_list = dir_files(os.getcwd())
        else:
            file_list = dir_files(os.getcwd() + '\\%s' % FILE_DIR)

        transfer_client, transfer_socket = self.transfer_connection()
        # else:
        #     client.send('425 Data connection failed to open\r\n')

        client.send('150 here comes directory listing\r\n')
        transfer_client.send(file_list)
        transfer_client.close()

        client.send('226 Directory send OK.\r\n')

    def transfer_connection(self):
        """
        Return client to use according
        to connection type. Active or passive
        """
        transfer_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.connection_type == 'Passive':
            transfer_server.bind((self.ip, self.port))
            transfer_server.listen(1)
            transfer_client, transfer_address = transfer_server.accept()
            return transfer_client, transfer_server
        elif self.connection_type == 'Active':
            transfer_server.connect((self.ip, self.port))
            return transfer_server, None

    def retrieve_file(self, client, args):
        """
        RETR FTP command:
        send file from server to client
        """
        path = ' '.join(args[PATH:])
        if os.path.isfile(path):
            client.send('150 opening data connection\r\n')
            transfer_client, transfer_server = self.transfer_connection()
            # send data
            with open(path, 'r' + self.binary_flag) as my_file:
                if self.last_file_position:
                    my_file.seek(self.last_file_position)
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
            self.last_file_position = 0
            client.send('226 Transfer complete.\r\n')

        else:
            client.send('550 File does not exist\r\n')

    def reset_transfer(self, client, args):
        try:
            self.last_file_position = int(args[0])
        except ValueError:
            client.send('501 Error in arguments\r\n')
            return
        client.send('350 File pos saved\r\n')
        request = client.recv(1024)
        if 'RETR' in request:
            self.retrieve_file(client, request.split()[ARGS:])
#        elif 'STOR' in request:
            # command for storing a file, client upload
        else:
            client.send('503 Wrong order of commands\r\n')

    @staticmethod
    def return_size(client, args):
        """
        SIZE FTP command:
        send to client size of argument file
        """
        path = ' '.join(args)
        client.send('213 %s\r\n' % str(os.path.getsize(path)))

    def store_something(self, client, args):
        stop = False
        transfer_client, transfer_socket = self.transfer_connection()
        with open(args[0], 'w'+self.binary_flag) as upload:
            while not stop:
                try:
                    upload.write(transfer_client.recv(1024))
                except socket.error:
                    client.send('226 transfer complete\r\n')
                    stop = True
        print 'process ended'


# end of for list\
# KNOWN_COMMANDS = {'USER': user_check,
#                   'FEAT': get_features,
#                   'SYST': syst_command,
#                   'CWD': cwd,
#                   'PWD': pwd,
#                   'DELE': delete,
#                   'TYPE': set_binary_flag,
#                   'PASV': passive_connection,
#                   'LIST': list_command,
#                   'PORT': active_connection,
#                   'HELP': help_command,
#                   'RETR': retrieve_file,
#                   'CDUP': cwd,
#                   'SIZE': return_size,
#                   'REST': reset_transfer}


def main():
    """
    Add Documentation here
    """
    pass  # Replace Pass with Your Code


if __name__ == '__main__':
    main()