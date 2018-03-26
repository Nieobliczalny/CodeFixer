import sqlite3
from pathlib import Path

#TODO: Convert to a class
def connect(db):
    dbFile = Path(db)
    if not dbFile.is_file():
        return create(db)
    conn = sqlite3.connect(db)
    return conn

def create(db):
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