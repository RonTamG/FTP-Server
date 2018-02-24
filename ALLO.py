# -*- coding: utf-8 -*-
import psutil


def ALLO_func(client, args):
    # args[0] is the path
    ok_code = '200'
    free_space = psutil.disk_usage(r'C://').free
    if args[0] > free_space:
    	client.send('500 Not enough space \r\n')
    	return
    client.send(ok_code + 'There is enough space for the requested file \r\n')
    	


def main():
    


if __name__ == '__main__':
    main()