import sqlite3
from pathlib import Path

#TODO: Convert to a class
def connect(db):
    dbFile = Path(db)
    if not dbFile.is_file():
        raise FileNotFoundError
    conn = sqlite3.connect(db)
    return conn

def getAllBugs(connection):
    cursor = connection.cursor()
    #TODO: Include current version of file as filter
    cursor.execute("SELECT id,detection_status FROM reports WHERE detection_status IN ('new', 'unresolved', 'reopened')")
    return cursor.fetchall()

def getBugData(connection, bugId):
    cursor = connection.cursor()
    params = (bugId,)
    cursor.execute("SELECT bpe.line_begin, bpe.col_begin, bpe.line_end, bpe.col_end, f.filepath FROM bug_path_events bpe JOIN files f ON bpe.file_id=f.id WHERE bpe.report_id=? ORDER BY bpe.`order` DESC LIMIT 1", params)
    return cursor.fetchone()
