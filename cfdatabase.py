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
            checker text NOT NULL);"""
        c = conn.cursor()
        try:
            c.execute(fixDataTable)
        except Error as e:
            raise ValueError
        return conn
    
    def __del__(self):
        if self.connection != None:
            self.connection.close()

    #TODO: Extract common methods to base class
    def executeAndFetchOne(self, query, params):
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()

    def executeAndFetchAll(self, query):
        cursor = self.connection.cursor()
        cursor.execute(query)
        return cursor.fetchall()
    
    def getAllFixData(self):
        return self.executeAndFetchAll("SELECT id, bugged_code, fixed_code, checker FROM fix_data")
    
    def clean(self):
        cursor = self.connection.cursor()
        cursor.execute('DELETE FROM fix_data')
    
    def store(self, bugCode, fixCode, checker):
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO fix_data (bugged_code, fixed_code, checker) VALUES (?, ?, ?)",(bugCode, fixCode, checker,))
        self.connection.commit()
        cursor.close()
