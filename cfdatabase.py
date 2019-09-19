import sqlite3
from pathlib import Path

#TODO: Check for possible reuse of cursor
class CFDatabase():
    connection = None

    def __init__(self, path):
        self.connection = self.connect(path)
    
    def connect(self, db):
        dbFile = Path(db)
        if not dbFile.is_file():
            return self.create(db)
        conn = sqlite3.connect(db)
        return conn

    def create(self, db):
        conn = sqlite3.connect(db)
        fixDataTable = """CREATE TABLE IF NOT EXISTS fix_data (
            id integer PRIMARY KEY AUTOINCREMENT,
            bugged_code text NOT NULL,
            fixed_code text NOT NULL,
            checker text NOT NULL,
            message text NOT NULL,
            line integer NOT NULL);"""
        globalsTable = """
            CREATE TABLE IF NOT EXISTS globals (
            id integer PRIMARY KEY AUTOINCREMENT,
            name text NOT NULL,
            value text NOT NULL);"""
        c = conn.cursor()
        try:
            c.execute(fixDataTable)
            c.close()
            del c
            c = conn.cursor()
            c.execute(globalsTable)
            c.close()
            del c
            self.createParameter(conn, 'lastCommit', '')
        except Error as e:
            raise ValueError
        return conn
    
    def __del__(self):
        if self.connection != None:
            self.connection.close()

    #TODO: Extract common methods to base class
    def createParameter(self, conn, name, defaultValue):
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, value FROM globals WHERE name=?', (name,))
        isPresent = cursor.fetchone()
        cursor.close()
        if not isPresent or len(isPresent) != 3:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO globals (name, value) VALUES (?, ?)",(name, defaultValue,))
            conn.commit()
            cursor.close()

    def executeAndFetchOne(self, query, params):
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()

    def executeAndFetchAll(self, query, params = ()):
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

    def getLastCommit(self):
        name = 'lastCommit'
        data = self.executeAndFetchOne('SELECT id, name, value FROM globals WHERE name=?', (name,))
        return data[2]

    def storeLastCommit(self, value):
        name = 'lastCommit'
        cursor = self.connection.cursor()
        cursor.execute("UPDATE globals SET value=? WHERE name=?", (value, name,))
        self.connection.commit()
        cursor.close()
    
    def getAllFixData(self):
        return self.executeAndFetchAll("SELECT id, bugged_code, fixed_code, checker, message, line FROM fix_data")
        
    
    def getFixDataForChecker(self, checker):
        return self.executeAndFetchAll("SELECT id, bugged_code, fixed_code, checker, message, line FROM fix_data WHERE checker=?", (checker,))
    
    def clean(self):
        cursor = self.connection.cursor()
        cursor.execute('DELETE FROM fix_data')
    
    def store(self, bugCode, fixCode, checker, message, line):
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO fix_data (bugged_code, fixed_code, checker, message, line) VALUES (?, ?, ?, ?, ?)",(bugCode, fixCode, checker, message, line,))
        self.connection.commit()
        cursor.close()
