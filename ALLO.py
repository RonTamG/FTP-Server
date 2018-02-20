# -*- coding: utf-8 -*-
import psutil

def ALLO_func(client, args):
    # args[0] is the path
    ok_code = '200'
    client.send(ok_code + psutil.disk_usage(args[0]).free + "Bytes of free space \r\n")

def main():


if __name__ == '__main__':
    main()