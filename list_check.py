# -*- coding: utf-8 -*-
import os


def dir_files(dir):
    return os.listdir(dir)


def file_detail(file):
    info = os.stat(file)
    return info


def list(args):
    param = args[0]
    if os.path.isdir(param):
        return dir_files(param)
    if os.path.isfile(param):
        return file_detail(param)

commands = {'LIST': list}
def main():
    """
    Add Documentation here
    """
    while True:
        c = raw_input('$-->')
        command = c.split()
        print commands[command[0]](command[1])



if __name__ == '__main__':
    main()