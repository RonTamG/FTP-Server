import sqlite3 as sql


USERSNAME = 0
PASSWORD = 1

def execute_command(command, database, cursor):
    try:
        cursor.execute(command)
    except sql.OperationalError as e:
        return e
    database.commit()
    

class Users(object):
    def __init__(self, **kwargs):
        self.database = sql.connect('users.db')
        self.cursor = self.database.cursor()
        
        # Create table
        sql_command = """CREATE TABLE User (ID integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                                            name char,
                                            password char);
        """
        execute_command(sql_command, self.database, self.cursor)

    def get_users_pass(self):
        sql_command = 'select name, password from user'
        results = self.cursor.execute(sql_command)
        results = results.fetchall()
        return results

    def add_user(self, username, password):
    	sql_command = "INSERT INTO User (name, password) VALUES ('%s', '%s')" % (username, password)
    	print execute_command(sql_command, self.database, self.cursor)