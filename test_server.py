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
    def __init__(self, port, logger, my_ip=socket.gethostbyname(socket.gethostname())):
        super(Server, self).__init__(my_ip)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(("0.0.0.0", port))
        self.server_socket.listen(1)
        print "connected"
        self.connections = []
        # output gui
        self.logger = logger
        self.online = True

    def run(self):
        while self.online: # can also add here max number of connections
            client, address = self.server_socket.accept()
            client.send('220 welcome\r\n')

            current_thread = threading.Thread(target=self.main_loop, args=(client, address,))
            current_thread.daemon = True
            current_thread.start()

            self.connections.append(client)

    def main_loop(self, client, address):
        this_client = '%s:%d -> ' % address
        try:
            request = client.recv(DATA).replace('\r\n', '')
            while self.online:
                print 'request = ' + request

                if not request:  # or command === quit
                    self.connections.remove(client)
                    client.close()
                    self.logger.add_text('%sdisconnected' % this_client)
                    break

                command, args = get_command_args(request)
                try:
                    log = str(self.command_dict[command](client, args))
                    print log
                    self.logger.add_text(this_client + log)
                #print self.command_dict[command](client, args)
                except KeyError as e:
                    print e
                    client.send('500 command unknown\r\n')

                request = client.recv(DATA).replace('\r\n', '')
        except socket.error:
            pass
            # could remove because gui already prints the client disconnected
            #if self.connections:
            #    self.logger.add_text("Server closed client connection")

    def close_server(self):
        for connection in self.connections:
            connection.close()

        # print threading.activeCount()
        self.online = False
        self.server_socket.close()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((socket.gethostbyname(socket.gethostname()), 6000))
        #s.connect(('192.168.1.17', 6000))
        s.close()
        self.logger.add_text('Closed Server')


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
    s = Server(6000, None)
    s.run()


if __name__ == '__main__':
    main()