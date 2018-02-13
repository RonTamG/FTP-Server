# -*- coding: utf-8 -*-
import socket
import string
import ssl
import sqlite3


def a_tls():
    a_code = '234'
    return a_code + " TLS selected \r\n"


def a_ssl():
    a_code = '234'
    return a_code + " SSL selected \r\n"


COMMANDS = {'AUTH SSL': a_ssl, "AUTH TLS": a_tls}


def main():
    stop = False
    server = socket.socket()
    server.bind(('0.0.0.0', 8820))
    server.listen(1)
    client_socket, client_address = server.accept()
    client_socket.send('220 \r\n')
    while not stop:
        req = client_socket.recv(1024)
        req = req.replace('\r\n', '')
        client_socket = ssl.wrap_socket(client_socket, server_side=True)
        client_socket.send(COMMANDS[req]())


if __name__ == '__main__':
    main()