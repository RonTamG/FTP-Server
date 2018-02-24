import os

ORIGINAL_DIR = os.getcwd()
PATH = 0
def cwd(client, args):
    succesful_change = '250 Succesfully changed directory\r\n'

    if len(args) > 0:
        path = ORIGINAL_DIR + args[PATH]
        if ORIGINAL_DIR in path and os.path.exists(path):
            os.chdir(path)
            print succesful_change
        else:
            print '550'

cwd(1, ['Extras'])

print os.getcwd()
os.chdir('Extras')
print os.getcwd()