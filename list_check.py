# -*- coding: utf-8 -*-
import os
import time


def dir_files(dir):
    currected_files = ''
    files = os.listdir(dir)
    for i in files:
        if '.' in i:
            i = i.split('.')
            currected_files += i[0] + '{.' + i[1] + ' file}\n'
        else:
            currected_files += i + '\n'
    return currected_files


def file_detail(file):
    return_string = ""
    info = ['last accessed: ' + time.asctime(time.localtime(os.path.getatime(file))),
            'last metadata change: ' + time.asctime(time.localtime(os.path.getctime(file))),
            'last modified: ' + time.asctime(time.localtime(os.path.getmtime(file))),
            'file size: ' + time.asctime(time.localtime(os.path.getsize(file)))]
    for i in info:
        return_string += i + '\n'
    return return_string


def list_command(client, args):
    if os.path.isdir(args):
        d =  dir_files(args)
        print [d]
        return d
    if os.path.isfile(args):
        d = file_detail(args)
        print d
        return d


commands = {'LIST': list}


def main():
    list_command('S', os.getcwd())


if __name__ == '__main__':
    main()