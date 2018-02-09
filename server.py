# -*- coding: utf-8 -*-
import socket
import string
import ssl


def send_error(socket, error_code):
    error_message_code = '404'
    if error_code == 1:
        socket.send(error_message_code + ' password/username not in the system.')


def send_all_clear(socket, extra_data):
    all_clear_code = '200'
    socket.send(all_clear_code + " " + extra_data)


def Authenticate(c_socket):
    astablish_coms = c_socket.recv(1024)
    users_pass = {}
    if "USER" in astablish_coms:
        username = astablish_coms.split('USER')
        username = username[1]
        if " " in username:
            username = username.replace(" ", "")

        #extracts the usernames and passwords from the file 'authentication resorces'
        with open(r'C:\Users\user\Desktop\school\cyber\FTP_project\authentication resorces.txt', 'r') as database:
            user_list = database.read().split("~")
            print user_list
            for i in xrange(0, len(user_list) - 1):
                print user_list[i]
                users_pass[user_list[i]] = user_list[i + 1]

        #authenticates username for further communication
        if username in users_pass.keys():
            send_all_clear(c_socket, "welcome " + username + ". need password")

        #recieving password and authenticating it
        password = c_socket.recv(1024)
        if "PASS" in password:
            password = password.split('PASS')[1]
            print password
        if users_pass[username] == password:
            send_all_clear(c_socket, "Access granted...")
        else:
            send_error(c_socket, 1)


def main():
    stop = False
    server = socket.socket()
    server.bind(('0.0.0.0', 8820))
    server.listen(1)

    while not stop:
        client_socket, client_address = server.accept()
        Authenticate(client_socket)


if __name__ == '__main__':
    main()