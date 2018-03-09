# -*- coding: utf-8 -*-
def nothing_value(string1):
    x = True
    for i in string1:
        x = x and i == ' '
    return x


def store_something(self, client, args):
    stop = False
    transfer_client, transfer_socket = self.transfer_connection()
    with open(args[0], 'w' + self.binary_flag) as upload:
        x = transfer_client.recv(1024)
        while not nothing_value(x):
            upload.write(x)
            print x
            x = transfer_client.recv(1024)

    client.send('226 transfer complete\r\n')
    print 'process ended'


def main():
    """
    Add Documentation here
    """
    pass  # Replace Pass with Your Code


if __name__ == '__main__':
    main()