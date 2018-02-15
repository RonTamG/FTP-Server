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


def list(args):
    if os.path.isdir(args):
        return dir_files(args)
    if os.path.isfile(args):
        return file_detail(args)


commands = {'LIST': list}


def main():
    while True:
        c = raw_input('$-->')
        command = c.split()
        print commands[command[0]](command[1])


if __name__ == '__main__':
    main()