# supports 'SYST' command

import socket
import threading

from commands import KNOWN_COMMANDS

COMMAND = 0
ARGS = 1
DATA = 1024


def get_command_args(request):
    """
    Sort command and args from client request
    """
    if len(request.split()) > 1:
        command = request.split()[COMMAND].upper()
        args = request.split()[ARGS::]
    else:
        command = request.upper()
        args = []

    return command, args


def main_loop(client):
    global connections

    request = client.recv(DATA).replace('\r\n', '')
    while True:
        print 'request = ' + request

        if not request:
            connections.remove(client)
            client.close()
            print 'client disconnected'
            break

        command, args = get_command_args(request)
        try:
            KNOWN_COMMANDS[command](client, args)
        except KeyError as e:
            print e
            client.send('500 command unknown\r\n')

        request = client.recv(DATA).replace('\r\n', '')


def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    p = int(raw_input("port-->"))
    s.bind(("0.0.0.0", p))
    s.listen(1)
    global connections
    connections = []
    while True:
        client, address = s.accept()
        client.send('220 welcome\r\n')
        current_thread = threading.Thread(target=main_loop, args=(client,))
        current_thread.daemon = True
        current_thread.start()
        connections.append(client)


if __name__ == '__main__':
    main()