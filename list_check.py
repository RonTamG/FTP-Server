# -*- coding: utf-8 -*-
import os
import time


def dir_files(dir):
    print dir
    corrected_files = ''
    tab = '		'
    space = ' '
    file_add = '-rw-r--r-- 1 owner group'
    dir_add = 'rwxr-xr-x 1 owner group'

    files = os.listdir(dir)
    for i in files:
        if os.path.isfile(dir + '\\' + i):
            full_path = dir + '\\' + i
            corrected_files += file_add + tab + str(os.path.getsize(full_path)) + space + \
                str(time.strftime('%b %d %H:%M', time.localtime(os.path.getctime(full_path)))) + space + i + '\r\n'
        if os.path.isdir(dir + '\\' + i):
            full_path = dir + '\\' + i
            corrected_files += dir_add + tab + str(os.path.getsize(full_path)) + space + \
                str(time.strftime('%b %d %H:%M', time.localtime(os.path.getctime(full_path)))) + space + i + '\r\n'
    return corrected_files


def get_list(args):
    if os.path.isdir(args):
        d = dir_files(args)
        return d

commands = {'LIST': list}


def main():
    print get_list(os.getcwd() + '\\Files')



if __name__ == '__main__':
    main()