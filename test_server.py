# supports 'SYST' command

import socket
import string
import ssl
import platform
import os
from database import Users



PATH = 0
ORIGINAL_DIR = os.getcwd()

USERNAME = 0
PASSWORD = 1
USER = 0
PASS = 1

COMMAND = 0
ARGS = 1
DATA = 1024



def syst_command(socket, args):
    ok_code = '215'
    socket.send(ok_code + " " + platform.system() + "\r\n")


def send_error(error_code):
    return error_code + ' \r\n'


def user_check(client ,args):
    request_password = '331 Please specify password\r\n'
    username = args[USERNAME].replace('\r\n', '')

    client.send(request_password)
    response = client.recv(DATA)
    if 'PASS' in response:
        password = response.split()[PASSWORD].replace('\r\n', '')
        return pass_check(client, password ,username)
    else:
        return send_error('503')
    


def pass_check(client, password, username):
    succesful_login = '230 Login succesful, all clear\r\n'
    wrong_password = '430 Wrong password\r\n'

    print username, password
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

def test(client, args):
    #### test
    client.send('200 \r\n')


KNOWN_COMMANDS = {'USER': user_check, 'FEAT': get_features, 'SYST': syst_command, 'CWD': cwd, 'PWD': pwd, 'DELE': delete, 'TYPE': test}


def main_loop(client):
    done = False
    request = client.recv(DATA)
    while not done:
        # get command and args
        if len(request.split()) > 1:
            command = request.split()[COMMAND]
            args = request.split()[ARGS::]
        # if command doesn't have arguments
        else:
            command = request.replace('\r\n', '')
            args = []
        # if in known commands, run it
        try:
            KNOWN_COMMANDS[command](client, args)
        # else send unknown command
        except Exception as e:
            print 'CommandERROR: ' + str(e)
            client.send(send_error('500'))

        # continue loop
        request = client.recv(DATA)


def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    p = int(raw_input("-->"))
    s.bind(("127.0.0.1", p))
    s.listen(1)
    client, address = s.accept()
    client.send('220 welcome\r\n')
    main_loop(client)


if __name__ == '__main__':
    main()