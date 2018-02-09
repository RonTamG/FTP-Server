import socket
#because all of the responses are small strings. no protocol is needed


def main():
    command = ""
    PORT = 8820


    while command.lower() != "exit":
        client = socket.socket()
        try:
            client.connect(("127.0.0.1", PORT))

        except socket.error:
            print "not able to connect"
            break

        command = raw_input("what is your command? ")
        client.send(command)

        data = client.recv(1024)

        print data
    client.close()


if __name__ == '__main__':
    main()