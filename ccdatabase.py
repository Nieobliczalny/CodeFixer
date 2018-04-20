import sqlite3
from pathlib import Path
from entities import BugData

class CCDatabase():
    connection = None

    def __init__(self, path):
        self.connection = self.connect(path)
    
    def connect(self, db):
        dbFile = Path(db)
        if not dbFile.is_file():
            raise FileNotFoundError
        conn = sqlite3.connect(db)
        return conn
    
    def __del__(self):
        if self.connection != None:
            self.connection.close()

    def executeAndFetchOne(self, query, params):
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()

    def executeAndFetchAll(self, query):
        cursor = self.connection.cursor()
        cursor.execute(query)
        return cursor.fetchall()

    def getAllBugs(self):
        #TODO: Ignore bugs marked as false-positive or intentional
        return self.executeAndFetchAll("SELECT id,detection_status FROM reports WHERE detection_status IN ('new', 'unresolved', 'reopened')")
    
    def getAllReports(self):
        return self.executeAndFetchAll("SELECT id FROM reports")

    def getBugData(self, bugId):
        #TODO: Ignore bugs marked as false-positive or intentional
        params = (bugId,)
        bugData = self.executeAndFetchOne("SELECT bpe.line_begin, bpe.col_begin, bpe.line_end, bpe.col_end, f.filepath FROM bug_path_events bpe JOIN files f ON bpe.file_id=f.id WHERE bpe.report_id=? ORDER BY bpe.`order` DESC LIMIT 1", params)
        checkerData = self.executeAndFetchOne("SELECT checker_id FROM reports WHERE id=? LIMIT 1", params)
        allBugData = BugData(bugData[0], bugData[2], bugData[4], checkerData[0])
        return allBugData
