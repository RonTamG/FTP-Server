# supports 'SYST' command

import socket
import threading

from commands import Commands

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


class Server(Commands):
    def __init__(self, my_ip=socket.gethostbyname(socket.gethostname())):
        super(Server, self).__init__(my_ip)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        p = int(raw_input("port-->"))
        self.server_socket.bind(("0.0.0.0", p))
        self.server_socket.listen(1)
        self.connections = []

    def run(self):
        while True:
            client, address = self.server_socket.accept()
            client.send('220 welcome\r\n')

            current_thread = threading.Thread(target=self.main_loop, args=(client,))
            current_thread.daemon = True
            current_thread.start()

            self.connections.append(client)

    def main_loop(self, client):
        request = client.recv(DATA).replace('\r\n', '')
        while True:
            print 'request = ' + request

            if not request:
                self.connections.remove(client)
                client.close()
                print 'client disconnected'
                break

            command, args = get_command_args(request)
            try:
                self.command_dict[command](client, args)
            except KeyError as e:
                print e
                client.send('500 command unknown\r\n')

            request = client.recv(DATA).replace('\r\n', '')


def main():
    # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # p = int(raw_input("port-->"))
    # s.bind(("0.0.0.0", p))
    # s.listen(1)
    # global connections
    # connections = []
    # while True:
    #     client, address = s.accept()
    #     client.send('220 welcome\r\n')
    #     current_thread = threading.Thread(target=main_loop, args=(client,))
    #     current_thread.daemon = True
    #     current_thread.start()
    #     connections.append(client)
    s = Server()
    s.run()


if __name__ == '__main__':
    main()