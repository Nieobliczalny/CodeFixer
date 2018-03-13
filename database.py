import sqlite3
from pathlib import Path

#TODO: Convert to a class
def connect(db):
    dbFile = Path(db)
    if not dbFile.is_file():
        raise FileNotFoundError
    conn = sqlite3.connect(db)
    return conn

def executeAndFetch(connection, query, params):
    cursor = connection.cursor()
    cursor.execute(query, params)
    return cursor.fetchone()

def getAllBugs(connection):
    cursor = connection.cursor()
    #TODO: Include current version of file as filter
    cursor.execute("SELECT id,detection_status FROM reports WHERE detection_status IN ('new', 'unresolved', 'reopened')")
    return cursor.fetchall()

def getBugData(connection, bugId):
    params = (bugId,)
    bugData = executeAndFetch(connection, "SELECT bpe.line_begin, bpe.col_begin, bpe.line_end, bpe.col_end, f.filepath FROM bug_path_events bpe JOIN files f ON bpe.file_id=f.id WHERE bpe.report_id=? ORDER BY bpe.`order` DESC LIMIT 1", params)
    versionData = executeAndFetch(connection, "SELECT rh.version_tag FROM reports rp JOIN runs rn ON rp.run_id=rn.id JOIN run_histories rh ON rn.id=rh.run_id WHERE rp.id=? ORDER BY rh.time DESC LIMIT 1", params)
    allBugData = [bugData[0], bugData[1], bugData[2], bugData[3], bugData[4], versionData[0]]
    #TODO: Make bugData a class
    return allBugData
