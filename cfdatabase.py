import sqlite3
from pathlib import Path

#TODO: Check for possible reuse of cursor
class CFDatabase():
    connection = None
    cursor = None

    def __init__(self, path):
        self.connection = self.connect(path)
        self.cursor = self.connection.cursor()
    
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
            self.cursor = conn.cursor()
            self.createParameter(conn, 'lastCommit', '')
            del self.cursor
        except Error as e:
            raise ValueError
        return conn
    
    def __del__(self):
        if self.cursor != None:
            self.cursor.close()
        if self.connection != None:
            self.connection.close()

    #TODO: Extract common methods to base class
    def createParameter(self, conn, name, defaultValue):
        self.cursor.execute('SELECT id, name, value FROM globals WHERE name=?', (name,))
        isPresent = self.cursor.fetchone()
        if not isPresent or len(isPresent) != 3:
            self.cursor.execute("INSERT INTO globals (name, value) VALUES (?, ?)",(name, defaultValue,))
            conn.commit()

    def executeAndFetchOne(self, query, params):
        self.cursor.execute(query, params)
        return self.cursor.fetchone()

    def executeAndFetchAll(self, query, params = ()):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def getLastCommit(self):
        name = 'lastCommit'
        data = self.executeAndFetchOne('SELECT id, name, value FROM globals WHERE name=?', (name,))
        return data[2]

    def storeLastCommit(self, value):
        name = 'lastCommit'
        self.cursor.execute("UPDATE globals SET value=? WHERE name=?", (value, name,))
        self.commit()
    
    def getAllFixData(self):
        return self.executeAndFetchAll("SELECT id, bugged_code, fixed_code, checker, message, line FROM fix_data")
        
    
    def getFixDataForChecker(self, checker):
        return self.executeAndFetchAll("SELECT id, bugged_code, fixed_code, checker, message, line FROM fix_data WHERE checker=?", (checker,))
    
    def clean(self):
        self.cursor.execute('DELETE FROM fix_data')
    
    def store(self, bugCode, fixCode, checker, message, line):
        self.cursor.execute("INSERT INTO fix_data (bugged_code, fixed_code, checker, message, line) VALUES (?, ?, ?, ?, ?)",(bugCode, fixCode, checker, message, line,))

    def commit(self):
        self.connection.commit()