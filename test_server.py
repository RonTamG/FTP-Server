import socket
import string
import ssl
import platform

USERNAME = 1
USER = 0
PASS = 1


def SYST_command(socket):
    ok_code = '215'
    socket.send(ok_code + " " + platform.system() + "\r\n")


def send_error(socket, error_code):
    error_message_code = '404'
    if error_code == 1:
        socket.send(error_message_code + ' password/username not in the system.')


def login_succesful(socket, extra_data):
    message = "Login succesful, all clear"
    print message
    login_succesful_code = '230'
    socket.send(login_succesful_code + message + '\r\n')


def send_code(socket, code):
    print code
    socket.send(code + '\r\n')


def get_user_pass():
    #extracts the usernames and passwords from the file database file
    users_pass = {}
    with open('accounts.txt', 'r') as database:
        user_list = database.readlines()
        print user_list
        for line in user_list:
            user_and_pass = line.split('~')
            print user_and_pass
            users_pass[user_and_pass[USER]] = user_and_pass[PASS].replace('\n', '')

    print users_pass
    return users_pass


def test_stuff(c_socket):
    c_socket.send("331 Please specify the password.\r\n")
    print c_socket.recv(1024)


def Authenticate(c_socket):
    # establish connecition and request USER input
    establish_coms = c_socket.recv(1024)
    while "USER" not in establish_coms:
        c_socket.send("530 Please login with USER and PASS.\r\n")
        establish_coms = c_socket.recv(1024)

    # get dictionary of users with their passwords
    users_pass = get_user_pass()

    print users_pass

    username = establish_coms.split('USER')
    username = username[USERNAME]

    if " " in username:
        username = username.replace(" ", "")
    if '\r\n' in username:
        username = username.replace('\r\n', '')

    #authenticates username for further communication
    if username in users_pass.keys():
        c_socket.send("331 Please specify the password.\r\n")
    #        login_succesful(c_socket, "welcome " + username + ". need password")

    #recieving password and authenticating it
    password = c_socket.recv(1024).replace('\r\n', '')
    if "PASS" in password:
        password = password.split('PASS')[1].replace(" ", '')
        print "pass = " + password
    print users_pass[username]
    print users_pass[username] == password
    if users_pass[username] == password:
        login_succesful(c_socket, "Access granted...")
    else:
        send_error(c_socket, 1)


def get_features():
    return '211 None\r\n'


KNOWN_COMMANDS = {'USER': Authenticate, 'PASS': None, 'FEAT': get_features, 'SYST': SYST_command}


def main_loop(c_socket):
    response = c_socket.recv(1024)
    print response
    command = response.split()[0]
    print command
    while command not in KNOWN_COMMANDS.keys():
        c_socket.send('500 Unknown coomand or invalid syntax\r\n')
        response = c_socket.recv(1024)
        command = response.split()[0]
        print response

    c_socket.send(KNOWN_COMMANDS[command](c_socket))


#	c.send("221")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
p = int(raw_input("-->"))
s.bind(("127.0.0.1", p))
s.listen(1)
try:
    c = s.accept()[0]
    c.send("220 \r\n")
    Authenticate(c)
    main_loop(c)

except Exception as e:
    print e
finally:
    s.close()